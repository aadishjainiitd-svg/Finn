"""Retain real exchange results PDFs under an isolated leased worker."""
import asyncio,json,sys,time,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend import repository,store,work,brief
from backend.sources import now

async def main():
    store.init();repository.init();owner='_probe_'+uuid.uuid4().hex;report=[]
    try:
        with repository.transaction() as tx:
            if tx.execute("SELECT COUNT(*) AS n FROM work_jobs WHERE status IN ('queued','running')").fetchone()['n']:raise RuntimeError('Existing work must finish first')
        rows=json.loads(Path('data/quarterly-receipts.json').read_text())
        for row in rows:
            if str(row['seq_id'])=='106805363':continue # Separate TCS board update, not the quarterly results.
            start=time.monotonic();event=brief.make_filing(row,now());queued=work.enqueue(owner,'filing',{'event':event})
            job=work.claim()
            if not job or job['id']!=queued['id']:raise RuntimeError('Own lease not acquired')
            await work.run_one(job);result=work.get(owner,queued['id'])
            record=store.cached('assessed-'+event['id']) or {}
            item={'symbol':event['symbol'],'event_id':event['id'],'url':event['url'],'job_status':result['status'],
                'version':record.get('version'),'seconds':round(time.monotonic()-start,2),'error':result.get('error'),
                'results':record.get('enrichment',{}).get('results')}
            report.append(item);print(json.dumps({k:v for k,v in item.items() if k!='results'}),flush=True)
    except Exception as exc:report.append({'error_type':type(exc).__name__})
    finally:
        with repository.transaction() as tx:
            tx.execute('DELETE FROM records WHERE owner=?',(owner,));tx.execute('DELETE FROM work_jobs WHERE owner=?',(owner,))
    Path('docs/quarterly-source-verification.json').write_text(json.dumps({'kind':'Real NSE receipt requests and original PDF ingestion, local leased worker with Neon retention; no model calls','items':report},indent=2),encoding='utf-8')
if __name__=='__main__':asyncio.run(main())
