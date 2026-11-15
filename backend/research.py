import asyncio
import hashlib
import json
import re
import time
import uuid
from . import store,repository
from .config import MODEL,PARSER
from .sources import ticker,identity,discover,now
from .documents import ingest,retrieve,latest_key,source_exclusion
from .llm import synthesize,grounded_display
from .calculations import numerical_answer
from .network import SourceError

jobs={}
worker=asyncio.Lock()
inflight={}
background_active=False
VERSION='retrieval-15-prompt-11-schema-4-'+PARSER+'-'+MODEL

def question_key(symbol,question,filing_id=None,owner=None):
    signature=None
    if filing_id:
        from .brief import events_by_id
        signature=events_by_id.get(filing_id,{}).get('source_signature')
    fields=[symbol,question.strip().lower(),filing_id,VERSION]
    if filing_id:fields.append(signature)
    if owner:fields.append(owner)
    return 'recent-answer-'+hashlib.sha256(json.dumps(fields).encode()).hexdigest()

def recent_answer(symbol,question,filing_id=None,owner=None):
    # Report/call answers are dated observations. Reuse for a day, invalidating
    # immediately when a newer known source version or prompt changes the key.
    key=question_key(symbol,question,filing_id,owner)
    retained=repository.get(owner,'answers',key) if owner else None
    result=retained.get('answer') if retained and time.time()-retained['_updated']<86400 else store.cached(key,86400)
    if not result and owner:
        demo=store.cached(question_key(symbol,question,filing_id),86400)
        if demo and demo.get('is_demo_seed'):result=demo
    if not result:return None
    with store.db() as c:
        for doc in result['documents']:
            version=doc.get('version',doc['hash'])
            if not result.get('is_demo_seed') and not c.execute('SELECT 1 FROM documents WHERE hash=?',(version,)).fetchone():
                if not owner or not all(repository.evidence(e['id']) for e in result.get('evidence',[]) if e.get('version',e['hash'])==version):return None
            pointer=store.cached(latest_key(doc))
            if pointer and pointer!=version:return None
    return grounded_display({**result,'cache_hit':True})

async def run(job, symbol, question, filing_id=None,owner=None,conversation=None):
    from .conversations import prompt,query,focus_evidence,exact_qualification
    focused=prompt(question,conversation)
    started=time.monotonic()
    try:
        async with worker:
            job['queue_seconds']=round(time.monotonic()-started,2)
            recent=None if conversation else recent_answer(symbol,question,filing_id,owner)
            if recent:
                job.update(status='complete',stage='Complete',result=recent,documents=recent['documents'],gaps=recent['gaps'])
                return
            job['stage']='Resolving exchange identity'
            company=await identity(symbol); job['company']=company
            job['stage']='Discovering primary documents'
            sources=await discover(company); documents=[]; gaps=[]
            if filing_id:
                from .brief import events_by_id
                event=events_by_id.get(filing_id)
                if not event or event['symbol']!=symbol:
                    raise SourceError('event_expired','Refresh the brief and select this company’s filing again.')
                sources.insert(0,{'kind':'filing','title':event['title'],'discovery_period':event['published_at'] or 'Date unavailable',
                    'download_url':event['url'],'original_url':event['url']})
            for source in sources:
                job['stage']='Reading '+source['title']
                try: documents.append(await ingest(company,source,job))
                except SourceError as e: gaps.append({'kind':source['kind'],'code':e.code,'message':e.message})
            for kind in ('annual','transcript'):
                if not any(s['kind']==kind for s in sources): gaps.append({'kind':kind,'code':'missing_document','message':'No primary '+kind+' was discovered.'})
            job['documents']=documents; job['gaps']=gaps
            if not documents: raise SourceError('no_readable_documents','No issuer-verified documents could be read.')
            for doc in documents:
                if source_exclusion(doc):
                    gaps.append({'kind':'filing','code':'issuer_layout_unverified','message':source_exclusion(doc)+' This attachment is excluded from generated answers; inspect the original.'})
            evidence=focus_evidence(question,conversation,retrieve(documents,query(question,conversation))); job['evidence']=evidence
            key=hashlib.sha256(json.dumps([symbol,focused.strip().lower(),[e['id'] for e in evidence],VERSION,owner]).encode()).hexdigest()
            hit=store.cached('answer-'+key)
            if hit: result=grounded_display({**hit,'cache_hit':True})
            else:
                result=exact_qualification(question,evidence) if conversation else numerical_answer(question,evidence)
                if result is None:result=await synthesize(focused,evidence,job)
                if any(g.get('code')=='issuer_layout_unverified' for g in gaps):
                    result['status']='partial' if result.get('claims') else 'insufficient_evidence'
                result.update(company=company,question=question,documents=documents,gaps=gaps,answered_at=now(),cache_hit=False)
                store.put('answer-'+key,result)
            if conversation:result={**result,'conversation':conversation}
            else:
                store.put(question_key(symbol,question,filing_id,owner),result)
                if owner:repository.save(owner,'answers',question_key(symbol,question,filing_id,owner),{'answer':result})
            job.update(status='complete',stage='Complete',result=result)
    except SourceError as e:
        job.update(status='error',stage='Could not complete',error={'code':e.code,'message':e.message})
    except Exception as e:
        # Log only class, never keys, source text or private question contents.
        print('research_error='+type(e).__name__,flush=True)
        job.update(status='error',stage='Could not complete',error={'code':'internal','message':'Processing was interrupted. Please retry.'})
    finally:
        job['elapsed_seconds']=round(time.monotonic()-started,2)
        inflight.pop((symbol,question.strip().lower(),filing_id,owner) if owner else (symbol,question.strip().lower(),filing_id),None)

async def owned_run(job,symbol,question,filing_id,owner):
    async def heartbeat():
        while True:
            await asyncio.sleep(15)
            await asyncio.to_thread(repository.save,owner,'jobs',job['id'],job)
    beat=asyncio.create_task(heartbeat())
    try:await run(job,symbol,question,filing_id,owner)
    finally:
        beat.cancel();await asyncio.gather(beat,return_exceptions=True)
        repository.save(owner,'jobs',job['id'],job)
        if job.get('result'):repository.save(owner,'history',job['id'],{'symbol':symbol,'question':question,
            'filing_id':filing_id,'answer':job['result'],'created_at':job['created_at']})

def prune_jobs():
    for jid in list(jobs):
        if len(jobs)>=25 and jobs[jid]['status']!='running':jobs.pop(jid)

def submit(symbol,question,filing_id=None,owner=None):
    symbol=ticker(symbol); key=(symbol,question.strip().lower(),filing_id,owner) if owner else (symbol,question.strip().lower(),filing_id)
    recent=recent_answer(symbol,question,filing_id,owner)
    if recent:return {'id':'cache','symbol':symbol,'status':'complete','stage':'Complete','result':recent,'elapsed_seconds':0,'documents':recent['documents'],'gaps':recent['gaps']}
    if owner:
        from .work import enqueue
        return enqueue(owner,'research',{'symbol':symbol,'question':question,'filing_id':filing_id})
    if key in inflight: return jobs[inflight[key]]
    active=sum(j['status']=='running' for j in jobs.values())+int(background_active)
    if active>=2: raise SourceError('busy','One investigation is running and one is waiting. Please retry shortly.')
    # Bounded metadata in process; large evidence is never retained indefinitely.
    prune_jobs()
    job={'id':uuid.uuid4().hex,'symbol':symbol,'status':'running','stage':'Waiting to process','created_at':now()}
    if owner:
        job['owner']=owner
        repository.save(owner,'jobs',job['id'],job)
    jobs[job['id']]=job; inflight[key]=job['id']
    asyncio.create_task(owned_run(job,symbol,question,filing_id,owner) if owner else run(job,symbol,question,filing_id))
    return job

