import asyncio
import hashlib
import json
import time
import uuid
from . import store
from .config import MODEL,PARSER
from .sources import ticker,identity,discover,now
from .documents import ingest,retrieve
from .llm import synthesize
from .network import SourceError

jobs={}
worker=asyncio.Lock()
inflight={}
VERSION='retrieval-1-prompt-2-schema-1-'+PARSER+'-'+MODEL

async def run(job, symbol, question):
    started=time.monotonic()
    try:
        async with worker:
            job['stage']='Resolving exchange identity'
            company=await identity(symbol); job['company']=company
            job['stage']='Discovering primary documents'
            sources=await discover(company); documents=[]; gaps=[]
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
            if hit: result={**hit,'cache_hit':True}
            else:
                result=await synthesize(question,evidence,job)
                result.update(company=company,question=question,documents=documents,gaps=gaps,answered_at=now(),cache_hit=False)
                store.put('answer-'+key,result)
            job.update(status='complete',stage='Complete',result=result)
    except SourceError as e:
        job.update(status='error',stage='Could not complete',error={'code':e.code,'message':e.message})
    except Exception as e:
        # Log only class, never keys, source text or private question contents.
        print('research_error='+type(e).__name__,flush=True)
        job.update(status='error',stage='Could not complete',error={'code':'internal','message':'Processing was interrupted. Please retry.'})
    finally:
        job['elapsed_seconds']=round(time.monotonic()-started,2)
        inflight.pop((symbol,question.strip().lower()),None)

def submit(symbol,question):
    symbol=ticker(symbol); key=(symbol,question.strip().lower())
    if key in inflight: return jobs[inflight[key]]
    active=sum(j['status']=='running' for j in jobs.values())
    if active>=2: raise SourceError('busy','One investigation is running and one is waiting. Please retry shortly.')
    # Bounded metadata in process; large evidence is never retained indefinitely.
    for jid in list(jobs):
        if len(jobs)>25 and jobs[jid]['status']!='running': jobs.pop(jid)
    job={'id':uuid.uuid4().hex,'symbol':symbol,'status':'running','stage':'Waiting to process','created_at':now()}
    jobs[job['id']]=job; inflight[key]=job['id']
    asyncio.create_task(run(job,symbol,question))
    return job

