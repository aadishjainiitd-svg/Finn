"""Live leased source refresh for an isolated one-company probe book."""
import asyncio,json,sys,time,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend import repository,store,work
from backend.config import PORTFOLIO
from backend.sources import identity

async def main():
    owner='_probe_'+uuid.uuid4().hex;job_id=None
    symbols=PORTFOLIO if '--book' in sys.argv else ['ABB']
    report={'kind':'live Neon leased batches, NSE/Yahoo requests and primary PDF assessments; synthetic probe book','symbols':symbols}
    store.init();repository.init();started=time.monotonic()
    try:
        with repository.transaction() as tx:
            if tx.execute("SELECT COUNT(*) AS n FROM work_jobs WHERE status IN ('queued','running')").fetchone()['n']:
                raise RuntimeError('Existing work must finish before isolated queue probe')
        companies=[]
        for symbol in symbols:companies.append(await identity(symbol))
        report['identities']=[{k:c.get(k) for k in ('symbol','name','isin')} for c in companies]
        repository.save(owner,'state','book',{'holdings':[{'symbol':symbol,'weight':None,'thesis':'','sector':'','inputs':[]} for symbol in symbols],'is_demo':True})
        queued=work.enqueue(owner,'refresh',{});job_id=queued['id']
        for batch in range(80):
            job=work.claim()
            if not job or job['id']!=job_id:raise RuntimeError('Probe did not obtain its own lease')
            await work.run_one(job)
            result=work.get(owner,job_id)
            print(json.dumps({'batch':batch+1,'job_status':result['status'],'attachments_checked':result.get('attachments_checked'),'attachments_failed':result.get('attachments_failed')}),flush=True)
            if result['status']!='running':break
        report['batches']=batch+1
        report['job_status']=result['status'];report['owner_isolation']=work.get(owner+'-other',job_id) is None
        if result['status']=='error':report['error']=result['error']
        snapshot=store.cached('brief-snapshot') or {'coverage':[],'events':[]}
        coverage=[c for c in snapshot['coverage'] if c['symbol'] in symbols]
        report['coverage']=coverage if '--book' in sys.argv else next(iter(coverage),None)
        report['retained_filings']=sum(e['symbol'] in symbols and e['kind']=='filing' for e in snapshot['events'])
        report['assessments']=[{k:e.get(k) for k in ('id','title','assessment','assessment_error','tier')} for e in snapshot['events'] if e['symbol'] in symbols and e['kind']=='filing']
        report['attachments_checked']=result.get('attachments_checked');report['attachments_failed']=result.get('attachments_failed')
        report['status']='passed' if result['status']=='complete' and len(coverage)==len(symbols) and all(c[s]['status']=='live' for c in coverage for s in ('filings','price')) else 'partial'
        report['classification_policy']=__import__('backend.brief',fromlist=['ASSESSMENT_POLICY']).ASSESSMENT_POLICY
        report['limitation']='A completed queue and live fetches do not establish semantic correctness or complete newspaper layout extraction; pending assessments remain visible.'
    except Exception as exc:report.update(status='failed',error_type=type(exc).__name__)
    finally:
        with repository.transaction() as tx:
            tx.execute('DELETE FROM records WHERE owner=?',(owner,))
            tx.execute('DELETE FROM work_jobs WHERE owner=?',(owner,))
    report['elapsed_seconds']=round(time.monotonic()-started,2)
    Path('docs/'+('book-refresh-verification.json' if '--book' in sys.argv else 'source-refresh-verification.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))
if __name__=='__main__':asyncio.run(main())
