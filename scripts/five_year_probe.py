"""Live nine-document build and narrative selection through a leased Neon job."""
import asyncio,json,sys,time,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend import repository,store,work

async def main():
    store.init();repository.init();owner='_probe_'+uuid.uuid4().hex;started=time.monotonic()
    report={'kind':'Live ABB nine-document requests, Groq research selection and Neon leased job; local runtime'}
    try:
        with repository.transaction() as tx:
            if tx.execute("SELECT COUNT(*) AS n FROM work_jobs WHERE status IN ('queued','running')").fetchone()['n']:raise RuntimeError('Existing work must finish first')
        queued=work.enqueue(owner,'research_pack',{'symbol':'ABB','annual_count':5});job=work.claim()
        if not job or job['id']!=queued['id']:raise RuntimeError('Own lease not acquired')
        await work.run_one(job);result=work.get(owner,job['id']);pack=result.get('result') or {}
        narrative=pack.get('narrative',{});checks=[]
        for observation in narrative.get('observations',[]):
            for source in observation['sources']:
                e=repository.evidence(source['evidence']['id'])
                checks.append(bool(e and e['symbol']=='ABB' and source['quote'] in ' '.join(e['text'].split())))
        report.update(job_status=result['status'],error=result.get('error'),narrative=narrative,
            exact_narrative_citations=checks,documents=[{k:d.get(k) for k in ('kind','period','version','processing_seconds','combined_peak_mb')} for d in pack.get('documents',[])],
            financial_fact_count=len(pack.get('financials',{}).get('facts',{})),years=[{'year':y['year'],'scope':y['scope'],'cash_reconciled':bool(y.get('cash_bridge',{}).get('reconciled')) if y.get('cash_bridge') else None} for y in pack.get('financials',{}).get('years',[])],gaps=pack.get('gaps'),
            model_attempts=result.get('model_attempts'),provider_usage=result.get('provider_usage_total'),
            status='passed' if result['status']=='complete' and checks and all(checks) else 'partial',
            limitation='Exact citation and pipeline checks only; substantive balance and relevance require semantic review. Hosted expanded memory/restart remain unverified.')
    except Exception as exc:report.update(status='failed',error_type=type(exc).__name__)
    finally:
        with repository.transaction() as tx:
            tx.execute('DELETE FROM records WHERE owner=?',(owner,));tx.execute('DELETE FROM work_jobs WHERE owner=?',(owner,))
    report['elapsed_seconds']=round(time.monotonic()-started,2)
    Path('docs/five-year-source-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='narrative'}))

if __name__=='__main__':asyncio.run(main())
