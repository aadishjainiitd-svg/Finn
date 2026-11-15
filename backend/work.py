"""Leased, restart-recoverable work; one extraction flight across processes."""
import asyncio
import hashlib
import json
import time
import uuid
from . import repository
from .network import SourceError

LEASE=90
LONG=('refresh','research_pack','thesis')
# Per-browser rolling 24-hour shares of model-backed work.
OWNER_GROUP={'research':'questions','portfolio_research':'questions','thesis':'questions','research_pack':'questions','filing':'filings'}
OWNER_DAILY={**{k:15 for k,v in OWNER_GROUP.items() if v=='questions'},'filing':40}
_runner_loop=None
_wake=None


def public(row):
    if not row:return None
    return {'id':row['id'],**{k:v for k,v in json.loads(row['progress']).items() if not k.startswith('_')},
            'status':'running' if row['status'] in ('queued','running') else row['status']}


def enqueue(owner,kind,payload,once=False):
    identity=hashlib.sha256(json.dumps([kind,payload],sort_keys=True).encode()).hexdigest()
    now=time.time()
    with repository.transaction() as tx:
        # Serialize admission across web processes; same transaction protects the
        # queue capacity and duplicate request check. No private payload is global.
        tx.execute("UPDATE worker_slots SET lease_until=lease_until WHERE id='global'")
        # A once-only slot (scheduled refresh) may be retried after an error.
        statuses=" AND status<>'error'" if once else " AND status IN ('queued','running')"
        existing=tx.execute("SELECT * FROM work_jobs WHERE owner=? AND identity_key=?"+statuses+" ORDER BY created DESC LIMIT 1",(owner,identity)).fetchone()
        if existing:return public(existing)
        share=OWNER_DAILY.get(kind)
        if share and not owner.startswith('_'):
            # One visitor cannot spend the whole shared free model allowance.
            group=[k for k,v in OWNER_GROUP.items() if v==OWNER_GROUP[kind]]
            used=tx.execute("SELECT COUNT(*) AS n FROM work_jobs WHERE owner=? AND created>? AND kind IN ("+','.join('?'*len(group))+")",
                            (owner,now-86400,*group)).fetchone()['n']
            if used>=share:
                raise SourceError('owner_quota',f"This browser has used its share of today's free analysis ({share}). Saved sources and earlier answers stay readable; try again tomorrow.")
        active=tx.execute("SELECT COUNT(*) AS n FROM work_jobs WHERE status IN ('queued','running')").fetchone()['n']
        if active>=2:raise SourceError('busy','One investigation is running and one is waiting. Please retry shortly.')
        if kind in LONG:
            # Long batch work (a refresh re-queues itself between batches) may
            # hold only one of the two global slots, so anonymous sessions
            # cannot occupy both and block every question and filing read.
            placeholders=','.join('?'*len(LONG))
            long_active=tx.execute("SELECT COUNT(*) AS n FROM work_jobs WHERE status IN ('queued','running') AND kind IN ("+placeholders+")",LONG).fetchone()['n']
            if long_active>=1:raise SourceError('busy','A source refresh or research pack is already running. Questions still run; retry the refresh shortly.')
        jid=uuid.uuid4().hex
        from .sources import now as iso_now
        progress={'stage':'Queued; work survives an app restart','created_at':iso_now(),'kind':kind}
        tx.execute('INSERT INTO work_jobs(id,owner,kind,identity_key,payload,status,progress,created,updated) VALUES (?,?,?,?,?,?,?,?,?)',
            (jid,owner,kind,identity,json.dumps(payload),'queued',json.dumps(progress),now,now))
    runner,wake=_runner_loop,_wake
    if runner and wake:
        try:runner.call_soon_threadsafe(wake.set)
        except RuntimeError:pass # Shutdown; the durable command remains queued.
    return {'id':jid,'status':'running',**progress}


def get(owner,jid):
    with repository.transaction() as tx:
        return public(tx.execute('SELECT * FROM work_jobs WHERE owner=? AND id=?',(owner,jid)).fetchone())


def active(owner):
    with repository.transaction() as tx:
        rows=tx.execute("SELECT * FROM work_jobs WHERE owner=? AND status IN ('queued','running') ORDER BY created DESC",(owner,)).fetchall()
    return [{**public(row),'request':json.loads(row['payload']) if row['kind'] in ('research','portfolio_research') else {'kind':row['kind']}} for row in rows]


def claim(at=None):
    now=time.time() if at is None else at;token=uuid.uuid4().hex
    with repository.transaction() as tx:
        won=tx.execute("UPDATE worker_slots SET token=?,lease_until=? WHERE id='global' AND lease_until<=? RETURNING token",(token,now+LEASE,now)).fetchone()
        if not won:return None
        interrupted={'status':'error','stage':'Repeated interruption','error':{'code':'retry_limit',
            'message':'Processing was interrupted three times. Inspect existing sources or retry explicitly.'}}
        tx.execute("UPDATE work_jobs SET status='error',progress=?,updated=? WHERE status='running' AND lease_until<=? AND attempts>=3",
            (json.dumps(interrupted),now,now))
        row=tx.execute("SELECT * FROM work_jobs WHERE status='queued' OR (status='running' AND lease_until<=?) ORDER BY CASE WHEN kind IN ('research','portfolio_research','filing') THEN 0 ELSE 1 END,created,id LIMIT 1",(now,)).fetchone()
        if not row:
            tx.execute("UPDATE worker_slots SET lease_until=0 WHERE id='global' AND token=?",(token,));return None
        tx.execute("UPDATE work_jobs SET status='running',token=?,lease_until=?,updated=?,attempts=attempts+1 WHERE id=?",(token,now+LEASE,now,row['id']))
        return {**dict(row),'token':token,'payload':json.loads(row['payload']),'progress':json.loads(row['progress'])}


def heartbeat(job,progress):
    now=time.time()
    with repository.transaction() as tx:
        won=tx.execute("UPDATE worker_slots SET lease_until=? WHERE id='global' AND token=? AND lease_until>? RETURNING token",(now+LEASE,job['token'],now)).fetchone()
        if not won:raise SourceError('lease_lost','Processing ownership changed. This attempt has stopped.')
        tx.execute('UPDATE work_jobs SET progress=?,updated=?,lease_until=? WHERE id=? AND token=?',
                   (json.dumps(progress),now,now+LEASE,job['id'],job['token']))


def finish(job,progress):
    with repository.transaction() as tx:
        tx.execute("UPDATE work_jobs SET status=?,progress=?,updated=?,lease_until=0,attempts=CASE WHEN ?='queued' THEN 0 ELSE attempts END WHERE id=? AND token=?",
            (progress['status'],json.dumps(progress),time.time(),progress['status'],job['id'],job['token']))
        tx.execute("UPDATE worker_slots SET lease_until=0 WHERE id='global' AND token=?",(job['token'],))


async def execute(job,progress):
    from . import research,brief,portfolio,store,watches
    payload=job['payload'];owner=job['owner']
    if job['kind']=='research':
        if payload.get('filing_id'):
            snapshot=store.cached('brief-snapshot') or {'events':[]}
            brief.events_by_id.update({e['id']:e for e in snapshot['events']})
        await research.run(progress,payload['symbol'],payload['question'],payload.get('filing_id'),owner,payload.get('conversation'))
        if progress.get('result'):
            progress['result']={**progress['result'],'history_id':job['id'],'filing_id':payload.get('filing_id')}
            repository.save(owner,'history',job['id'],{'symbol':payload['symbol'],'question':payload['question'],
                'filing_id':payload.get('filing_id'),'parent_id':(payload.get('conversation') or {}).get('parent_id'),'answer':progress['result'],'created_at':progress.get('created_at')})
    elif job['kind']=='portfolio_research':
        from .portfolio_research import run
        await run(progress,owner,payload)
        if progress.get('result'):
            progress['result']={**progress['result'],'history_id':job['id'],'filing_id':payload.get('filing_id')}
            repository.save(owner,'history',job['id'],{'symbol':'BOOK','question':payload['question'],'filing_id':None,
                'scope':progress['result']['scope'],'parent_id':(payload.get('conversation') or {}).get('parent_id'),'answer':progress['result'],'created_at':progress.get('created_at')})
    elif job['kind']=='scheduled_refresh':
        from .scheduled import run
        await run(progress)
    elif job['kind']=='research_pack':
        from .research_pack import build
        await build(progress,payload['symbol'],annual_count=payload.get('annual_count',2))
    elif job['kind']=='thesis':
        from .theses import batch
        await batch(progress,owner,payload.get('symbol'),payload.get('event_id'))
    elif job['kind']=='refresh':
        if '_assessment_ids' not in progress:
            symbols=[h['symbol'] for h in portfolio.book(owner)['holdings']]
            progress['stage']='Refreshing stored filing and completed-session coverage'
            snapshot=await brief.get_brief(force=True,symbols=symbols,background=False)
            progress['_assessment_ids']=[e['id'] for e in snapshot['events'] if e['symbol'] in symbols and e['kind']=='filing' and (e['assessment']=='pending' or e.get('assessment_policy')!=brief.ASSESSMENT_POLICY)]
            progress['attachments_total']=len(progress['_assessment_ids']);progress['attachments_checked']=0;progress['attachments_failed']=0
        await assess_batch(progress)
        if progress['_assessment_ids']:
            progress.update(status='queued',stage=f"{progress['attachments_checked']} of {progress['attachments_total']} attachments checked; questions can run between batches")
            return
        snapshot=store.cached('brief-snapshot')
        if not progress.get('_watch_evaluated'):
            await asyncio.to_thread(watches.evaluate_owner,owner,snapshot)
            progress['_watch_evaluated']=True
        from .theses import batch
        try:await batch(progress,owner)
        except SourceError as exc:
            # Sources and watches already refreshed; a thesis quota/model failure
            # is a reported gap, not a failed refresh.
            progress['thesis_gap']='Thesis evidence checks did not run: '+exc.message
        if progress['status']=='queued':return
        progress.update(status='complete',stage='Sources refreshed',result={'checked_at':snapshot['checked_at'],'counts':snapshot['counts']})
    elif job['kind']=='filing':
        event=payload['event'];progress['stage']='Reading the original disclosure'
        async with research.worker:evidence=await brief.assess(event)
        await asyncio.to_thread(watches.evaluate_owner,owner,store.cached('brief-snapshot') or {'events':[],'checked_at':None})
        progress.update(status='complete',stage='Source assessed',result={'evidence':evidence})
    else:raise SourceError('unknown_job','Unknown work type.')


async def assess_batch(progress):
    from . import research,brief,store
    for _ in range(min(3,len(progress['_assessment_ids']))):
        eid=progress['_assessment_ids'][0]
        snapshot=store.cached('brief-snapshot') or {'events':[]}
        event=next((e for e in snapshot['events'] if e['id']==eid),None)
        if event:
            progress['stage']='Reading '+event['symbol']+' disclosure · '+str(progress['attachments_checked']+1)+'/'+str(progress['attachments_total'])
            try:
                async with research.worker:await brief.assess(event)
            except Exception as exc:
                # Any failure on one filing is recorded and skipped; otherwise the
                # same filing would abort every later refresh at the same point.
                message=exc.message if isinstance(exc,SourceError) else 'Could not read this filing.'
                if not isinstance(exc,SourceError):print('assess_error='+type(exc).__name__,flush=True)
                failure={'version':None,'text':None,'evidence':[],'error':message,'source_signature':event['source_signature']}
                store.put('assessed-'+eid,failure)
                latest=store.cached('brief-snapshot') or snapshot
                for item in latest['events']:
                    if item['id']==eid and item.get('source_signature')==event['source_signature']:
                        item.update(assessment='pending',assessment_error=message,tier=min(item.get('tier',1),1),reason='Could not read this filing; kept visible for review.')
                latest.setdefault('counts',{})['pending']=sum(e['assessment']=='pending' for e in latest['events'])
                store.put('brief-snapshot',latest)
                progress['attachments_failed']+=1
        progress['attachments_checked']+=1
        progress['_assessment_ids'].pop(0)


async def run_one(job):
    progress={**job['progress'],'id':job['id'],'status':'running'}
    async def pulse():
        renewed=time.time()
        while True:
            await asyncio.sleep(15)
            try:
                await asyncio.to_thread(heartbeat,job,progress.copy());renewed=time.time()
            except SourceError as exc:
                # A lost lease stops at once. A transient storage failure is retried
                # while the last renewed lease still has a safe margin left.
                if exc.code=='lease_lost' or time.time()-renewed>LEASE-20:raise
    task=asyncio.create_task(execute(job,progress));beat=asyncio.create_task(pulse())
    try:
        done,_=await asyncio.wait([task,beat],return_when=asyncio.FIRST_COMPLETED)
        if beat in done:
            await beat
        await task
    except asyncio.CancelledError:
        # Leave leased work recoverable. Never turn a shutdown into completion.
        raise
    except Exception as exc:
        progress.update(status='error',stage='Could not complete',error={
            'code':exc.code if isinstance(exc,SourceError) else 'processing_error',
            'message':exc.message if isinstance(exc,SourceError) else 'Processing stopped. Retry; stored evidence is unchanged.'})
    finally:
        task.cancel();beat.cancel();await asyncio.gather(task,beat,return_exceptions=True)
    await asyncio.to_thread(finish,job,progress)


async def loop():
    global _runner_loop,_wake
    _runner_loop=asyncio.get_running_loop();_wake=asyncio.Event()
    try:
        while True:
            _wake.clear()
            try:
                job=await asyncio.to_thread(claim)
                if job:
                    await run_one(job)
                    continue
            except asyncio.CancelledError:raise
            except Exception as exc:print('work_loop_error='+type(exc).__name__,flush=True)
            # Same-process commands wake immediately. Other workers/restarts
            # are checked at a bounded interval without continuously polling.
            try:await asyncio.wait_for(_wake.wait(),timeout=30)
            except TimeoutError:pass
    finally:_runner_loop=None;_wake=None
