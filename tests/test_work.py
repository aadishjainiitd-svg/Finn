import json
from concurrent.futures import ThreadPoolExecutor
import pytest
from backend import repository,store,work
from backend.network import SourceError


@pytest.fixture(autouse=True)
def isolated(tmp_path,monkeypatch):
    monkeypatch.setenv('FINN_DATABASE_URL','')
    monkeypatch.setattr(repository,'DATA',tmp_path)
    monkeypatch.setattr(store,'DATA',tmp_path)
    repository.init();store.init()


def test_one_lease_across_eight_workers_and_owner_isolation():
    job=work.enqueue('alice','refresh',{})
    assert work.enqueue('alice','refresh',{})['id']==job['id']
    with ThreadPoolExecutor(max_workers=8) as pool:
        claims=[j for j in pool.map(lambda _:work.claim(),range(8)) if j]
    assert len(claims)==1
    assert work.get('bob',job['id']) is None
    work.finish(claims[0],{'status':'complete','result':{'checked_at':'fixture'}})
    repository.init()
    assert work.get('alice',job['id'])['status']=='complete'


def test_expired_lease_recovered_and_stale_writer_cannot_finish(monkeypatch):
    job=work.enqueue('alice','refresh',{})
    first=work.claim(at=100)
    assert work.claim(at=189) is None
    second=work.claim(at=191)
    assert second['id']==job['id'] and second['token']!=first['token']
    monkeypatch.setattr(work.time,'time',lambda:192)
    with pytest.raises(SourceError):work.heartbeat(first,{'stage':'obsolete'})
    work.finish(first,{'status':'complete','result':{'obsolete':True}})
    assert work.get('alice',job['id'])['status']=='running'
    work.finish(second,{'status':'complete','result':{'recovered':True}})
    assert work.get('alice',job['id'])['result']=={'recovered':True}


def test_queue_capacity_and_dedup_are_atomic():
    def submit(i):
        try:return work.enqueue(str(i),'research',{'symbol':'TCS','question':'q'+str(i)})
        except SourceError:return None
    with ThreadPoolExecutor(max_workers=8) as pool:assert len([j for j in pool.map(submit,range(8)) if j])==2


# Regression: adversarial review F1 (2026-11-15). Two anonymous sessions could
# hold both global slots with self-requeueing refreshes and block every question.
def test_long_batch_work_can_hold_only_one_global_slot():
    def submit(i):
        try:return work.enqueue('anon'+str(i),'refresh',{})
        except SourceError:return None
    with ThreadPoolExecutor(max_workers=8) as pool:assert len([j for j in pool.map(submit,range(8)) if j])==1
    with pytest.raises(SourceError):work.enqueue('other','research_pack',{'symbol':'TCS'})
    assert work.enqueue('bob','research',{'symbol':'TCS','question':'What happened?'})['status']=='running'


# Regression: adversarial review F4. A non-SourceError on one filing must be
# recorded and skipped, not abort the batch at the same filing on every refresh.
def test_unexpected_filing_error_is_recorded_and_batch_continues(monkeypatch):
    import asyncio
    from backend import brief
    events=[{'id':str(i),'symbol':'TCS','kind':'filing','assessment':'pending','tier':1,'source_signature':'s'+str(i)} for i in range(2)]
    store.put('brief-snapshot',{'events':events,'counts':{'pending':2}})
    seen=[]
    async def assess(event):
        seen.append(event['id'])
        if event['id']=='0':raise KeyError('unexpected parser shape')
    monkeypatch.setattr(brief,'assess',assess)
    progress={'_assessment_ids':['0','1'],'attachments_checked':0,'attachments_total':2,'attachments_failed':0}
    asyncio.run(work.assess_batch(progress))
    assert seen==['0','1'] and progress['attachments_failed']==1 and progress['_assessment_ids']==[]
    failed=store.cached('brief-snapshot')['events'][0]
    assert failed['assessment']=='pending' and failed['assessment_error']=='Could not read this filing.'


def test_rehydrate_restores_exact_search_pages_and_public_cache_does_not_share_questions(monkeypatch):
    meta={'version':'v1','hash':'h1','symbol':'TCS','kind':'annual'}
    repository.retain_document(meta,[{'id':'v1-p7','page':7,'text':'Durable original evidence.'}])
    # Uses the local repository adapter while exercising the hosted-cache path.
    monkeypatch.setattr(repository,'configured',lambda:True)
    original=repository.transaction
    from contextlib import contextmanager
    @contextmanager
    def local():
        monkeypatch.setattr(repository,'configured',lambda:False)
        try:
            with original() as tx:yield tx
        finally:monkeypatch.setattr(repository,'configured',lambda:True)
    monkeypatch.setattr(repository,'transaction',local)
    assert store.rehydrate('v1')
    with store.db() as c:
        assert c.execute("SELECT text FROM search WHERE search MATCH 'Durable'").fetchone()['text']=='Durable original evidence.'
    store.put('brief-snapshot',{'checked_at':'old receipt'})
    store.put('answer-private',{'question':'Private'})
    with store.db() as c:c.execute('DELETE FROM cache')
    assert store.cached('brief-snapshot')=={'checked_at':'old receipt'}
    assert repository.get('_public','source_cache','answer-private') is None
    assert not store.durable_key('question-TCS-private')


def test_watch_firings_are_owner_scoped_idempotent_and_never_backdated(monkeypatch):
    from backend import watches
    from tests.test_watches import bars
    rule=watches.draft('TCS volume is at least 2x usual')
    store.put('price-TCS',{'chart':bars(),'checked_at':'2026-02-24T12:00:00+00:00'})
    repository.save('alice','rules','r1',{'rule':rule,'sentence':'Volume rule','active_since':0})
    snapshot={'events':[],'checked_at':'2026-02-24T12:00:00+00:00'}
    assert watches.evaluate_owner('alice',snapshot)==1
    assert watches.evaluate_owner('alice',snapshot)==0
    assert len(repository.listing('alice','firings'))==1
    assert repository.listing('bob','firings')==[]
    repository.save('bob','rules','r2',{'rule':rule,'sentence':'Volume rule','active_since':2000000000})
    assert watches.evaluate_owner('bob',snapshot)==0


def test_refresh_assesses_in_recoverable_batches_and_questions_take_priority(monkeypatch):
    import asyncio
    from backend import brief,portfolio,watches
    events=[{'id':str(i),'symbol':'TCS','kind':'filing','assessment':'pending','tier':0 if i==0 else 1,'source_signature':'s'+str(i)} for i in range(4)]
    snapshot={'events':events,'checked_at':'fixture','counts':{'pending':4}}
    fetched=[];assessed=[]
    async def fetch(**kwargs):fetched.append(True);store.put('brief-snapshot',snapshot);return snapshot
    async def assess(event):
        assessed.append(event['id'])
        if event['id']=='0':raise SourceError('unreadable','Could not read attachment')
        current=store.cached('brief-snapshot')
        for e in current['events']:
            if e['id']==event['id']:e['assessment']='assessed'
        store.put('brief-snapshot',current)
    monkeypatch.setattr(brief,'get_brief',fetch);monkeypatch.setattr(brief,'assess',assess)
    monkeypatch.setattr(portfolio,'book',lambda owner:{'holdings':[{'symbol':'TCS'}]})
    monkeypatch.setattr(watches,'evaluate_owner',lambda *args:0)
    refresh=work.enqueue('alice','refresh',{});asyncio.run(work.run_one(work.claim()))
    assert work.get('alice',refresh['id'])['status']=='running' and len(assessed)==3
    assert not any(k.startswith('_') for k in work.get('alice',refresh['id']))
    question=work.enqueue('bob','research',{'symbol':'TCS','question':'What happened?'})
    claimed=work.claim();assert claimed['id']==question['id']
    work.finish(claimed,{'status':'complete'})
    # Fresh repository initialisation represents a process boundary. Cursor
    # resumes the fourth disclosure without fetching sources again.
    repository.init();asyncio.run(work.run_one(work.claim()))
    final=work.get('alice',refresh['id'])
    assert final['status']=='complete' and final['attachments_failed']==1
    assert len(fetched)==1 and assessed==['0','1','2','3']
    failed=store.cached('brief-snapshot')['events'][0]
    assert failed['assessment']=='pending' and failed['tier']==0


def test_slow_remote_filing_cache_reads_do_not_starve_the_lease_heartbeat(monkeypatch):
    import asyncio,time
    from backend import brief
    pulse=[];original=brief.make_filing
    async def filings():return {'rows':[{'symbol':'TCS','seq_id':'1','desc':'Update','attchmntFile':'https://issuer.example/filing.pdf','an_dt':'13-Nov-2026 10:00:00'}],'checked_at':'2026-11-15T00:00:00+00:00'}
    async def price(symbol):raise SourceError('offline','Controlled unavailable price')
    def delayed(row,checked):
        time.sleep(.12) # Synchronous remote-cache delay, not network fixture latency.
        assert pulse,'Filing preparation blocked the async heartbeat'
        return original(row,checked)
    monkeypatch.setattr(brief,'filings',filings);monkeypatch.setattr(brief,'price',price);monkeypatch.setattr(brief,'make_filing',delayed)
    async def run():
        async def heartbeat():await asyncio.sleep(.02);pulse.append(True)
        beat=asyncio.create_task(heartbeat())
        result=await brief.get_brief(force=True,symbols=['TCS'],background=False)
        await beat
        return result
    assert asyncio.run(run())['counts']['distinct_filings']==1


# Regression: adversarial review F7. One transient storage failure during a
# heartbeat must not abort a job whose lease is still valid; a lost lease must.
def test_transient_heartbeat_failure_is_retried_but_lost_lease_stops(monkeypatch):
    import asyncio
    real_sleep=asyncio.sleep
    async def fast(seconds):await real_sleep(0)
    monkeypatch.setattr(work.asyncio,'sleep',fast)
    calls=[]
    def flaky(job,progress):
        calls.append(1)
        if len(calls)==1:raise SourceError('storage_unavailable','blip')
    monkeypatch.setattr(work,'heartbeat',flaky)
    async def slow(job,progress):
        while len(calls)<3:await real_sleep(0)
        progress.update(status='complete',stage='done')
    monkeypatch.setattr(work,'execute',slow)
    job=work.enqueue('alice','research',{'symbol':'TCS','question':'q'});asyncio.run(work.run_one(work.claim()))
    assert work.get('alice',job['id'])['status']=='complete' and len(calls)>=3
    def lost(job,progress):raise SourceError('lease_lost','gone')
    monkeypatch.setattr(work,'heartbeat',lost)
    async def forever(job,progress):
        while True:await real_sleep(0)
    monkeypatch.setattr(work,'execute',forever)
    job=work.enqueue('bob','research',{'symbol':'TCS','question':'q2'});asyncio.run(work.run_one(work.claim()))
    assert work.get('bob',job['id'])['status']=='error'


def test_one_browser_cannot_spend_the_shared_model_allowance(monkeypatch):
    monkeypatch.setitem(work.OWNER_DAILY,'research',2)
    monkeypatch.setitem(work.OWNER_DAILY,'thesis',2)
    with repository.transaction() as tx:
        for i in range(2):
            tx.execute('INSERT INTO work_jobs(id,owner,kind,identity_key,payload,status,progress,created,updated) VALUES (?,?,?,?,?,?,?,?,?)',
                       ('old'+str(i),'alice','research','k'+str(i),'{}','complete','{}',__import__('time').time()-60,0))
    with pytest.raises(SourceError) as exc:work.enqueue('alice','thesis',{'symbol':'TCS'})
    assert exc.value.code=='owner_quota'
    # Another browser and system work are unaffected; old jobs age out after 24h.
    assert work.enqueue('bob','research',{'symbol':'TCS','question':'q'})['status']=='running'
    with repository.transaction() as tx:tx.execute("UPDATE work_jobs SET created=created-90000 WHERE owner='alice'")
    assert work.enqueue('alice','thesis',{'symbol':'TCS'})['status']=='running'


def test_errored_once_only_slot_can_be_retried():
    first=work.enqueue('_scheduler','scheduled_refresh',{'slot':'2026-11-15-evening'},once=True)
    assert work.enqueue('_scheduler','scheduled_refresh',{'slot':'2026-11-15-evening'},once=True)['id']==first['id']
    with repository.transaction() as tx:tx.execute("UPDATE work_jobs SET status='error' WHERE id=?",(first['id'],))
    assert work.enqueue('_scheduler','scheduled_refresh',{'slot':'2026-11-15-evening'},once=True)['id']!=first['id']
