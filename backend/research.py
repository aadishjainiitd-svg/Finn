import asyncio
import hashlib
import json
import time
import uuid
from . import store
from .config import MODEL,PARSER
from .sources import ticker,identity,discover,now
from .documents import ingest,retrieve,latest_key
from .llm import synthesize,grounded_display
from .calculations import numerical_answer
from .network import SourceError

jobs={}
worker=asyncio.Lock()
inflight={}
background_active=False
VERSION='retrieval-9-prompt-10-schema-4-'+PARSER+'-'+MODEL

def question_key(symbol,question,filing_id=None):
    signature=None
    if filing_id:
        from .brief import events_by_id
        signature=events_by_id.get(filing_id,{}).get('source_signature')
    fields=[symbol,question.strip().lower(),filing_id,VERSION]
    if filing_id:fields.append(signature)
    return 'recent-answer-'+hashlib.sha256(json.dumps(fields).encode()).hexdigest()

def recent_answer(symbol,question,filing_id=None):
    # Report/call answers are dated observations. Reuse for a day, invalidating
    # immediately when a newer known source version or prompt changes the key.
    result=store.cached(question_key(symbol,question,filing_id),86400)
    if not result:return None
    with store.db() as c:
        for doc in result['documents']:
            version=doc.get('version',doc['hash'])
            if not result.get('is_demo_seed') and not c.execute('SELECT 1 FROM documents WHERE hash=?',(version,)).fetchone():return None
            pointer=store.cached(latest_key(doc))
            if pointer and pointer!=version:return None
    return grounded_display({**result,'cache_hit':True})

async def run(job, symbol, question, filing_id=None):
    started=time.monotonic()
    try:
        async with worker:
            job['queue_seconds']=round(time.monotonic()-started,2)
            recent=recent_answer(symbol,question,filing_id)
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
            evidence=retrieve(documents,question); job['evidence']=evidence
            key=hashlib.sha256(json.dumps([symbol,question.strip().lower(),[e['id'] for e in evidence],VERSION]).encode()).hexdigest()
            hit=store.cached('answer-'+key)
            if hit: result=grounded_display({**hit,'cache_hit':True})
            else:
                result=numerical_answer(question,evidence)
                if result is None:result=await synthesize(question,evidence,job)
                result.update(company=company,question=question,documents=documents,gaps=gaps,answered_at=now(),cache_hit=False)
                store.put('answer-'+key,result)
            store.put(question_key(symbol,question,filing_id),result)
            job.update(status='complete',stage='Complete',result=result)
    except SourceError as e:
        job.update(status='error',stage='Could not complete',error={'code':e.code,'message':e.message})
    except Exception as e:
        # Log only class, never keys, source text or private question contents.
        print('research_error='+type(e).__name__,flush=True)
        job.update(status='error',stage='Could not complete',error={'code':'internal','message':'Processing was interrupted. Please retry.'})
    finally:
        job['elapsed_seconds']=round(time.monotonic()-started,2)
        inflight.pop((symbol,question.strip().lower(),filing_id),None)

def prune_jobs():
    for jid in list(jobs):
        if len(jobs)>=25 and jobs[jid]['status']!='running':jobs.pop(jid)

def submit(symbol,question,filing_id=None):
    symbol=ticker(symbol); key=(symbol,question.strip().lower(),filing_id)
    recent=recent_answer(symbol,question,filing_id)
    if recent:return {'id':'cache','symbol':symbol,'status':'complete','stage':'Complete','result':recent,'elapsed_seconds':0,'documents':recent['documents'],'gaps':recent['gaps']}
    if key in inflight: return jobs[inflight[key]]
    active=sum(j['status']=='running' for j in jobs.values())+int(background_active)
    if active>=2: raise SourceError('busy','One investigation is running and one is waiting. Please retry shortly.')
    # Bounded metadata in process; large evidence is never retained indefinitely.
    prune_jobs()
    job={'id':uuid.uuid4().hex,'symbol':symbol,'status':'running','stage':'Waiting to process','created_at':now()}
    jobs[job['id']]=job; inflight[key]=job['id']
    asyncio.create_task(run(job,symbol,question,filing_id))
    return job

