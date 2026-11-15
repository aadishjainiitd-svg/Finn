"""One real retained filing, live free-provider request and private Neon retention.

The hypothesis is a test input, not the user's investment thesis. The probe only
removes its own temporary owner records; public source evidence is unchanged.
"""
import asyncio,json,sys,time,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend import repository,store,work,theses,llm
from backend.sources import now

async def main():
    owner='_probe_'+uuid.uuid4().hex;version=uuid.uuid4().hex;started=time.monotonic()
    report={'kind':'Live Groq request, real retained ABB filing, Neon leased work and owner isolation; synthetic thesis hypothesis',
        'hypothesis':'Demand for ABB electrification products remains strong.'}
    store.init();repository.init()
    try:
        with repository.transaction() as tx:
            if tx.execute("SELECT COUNT(*) AS n FROM work_jobs WHERE status IN ('queued','running')").fetchone()['n']:raise RuntimeError('Existing work must finish first')
        events=store.cached('brief-snapshot')['events']
        event=next(e for e in events if e['symbol']=='ABB' and e['kind']=='filing' and e['assessment']=='assessed' and 'Press Release' in e['description'])
        h={'symbol':'ABB','thesis':report['hypothesis'],'thesis_version':version,'weight':None,'sector':'','inputs':[]}
        repository.save(owner,'state','book',{'holdings':[h],'is_demo':True})
        repository.save(owner,'thesis_versions',version,{'symbol':'ABB','thesis':h['thesis'],'created_at':now()})
        queued=work.enqueue(owner,'thesis',{'symbol':'ABB','thesis_version':version,'event_id':event['id']})
        job=work.claim()
        if not job or job['id']!=queued['id']:raise RuntimeError('Probe did not obtain its lease')
        await work.run_one(job)
        result=work.get(owner,queued['id'])
        report.update(job_status=result['status'],event_id=event['id'],model_attempts=result.get('model_attempts',0),
            provider_usage=result.get('provider_usage_total'),error=result.get('error'))
        record=repository.get(owner,'thesis_assessments',theses.key(h,event))
        report['record']=record
        citations=[s for o in (record or {}).get('observations',[]) for s in o['sources']]
        checks=[]
        for source in citations:
            e=source['evidence'];actual=repository.evidence(e['id'])
            checks.append(bool(actual and actual['symbol']=='ABB' and actual['page']==e['page'] and actual['hash']==e['hash'] and source['quote'] in ' '.join(actual['text'].split())))
        repository.close();repository.init()
        report.update(restart_retained=repository.get(owner,'thesis_assessments',theses.key(h,event))==record,
            owner_isolation=repository.get(owner+'-other','thesis_assessments',theses.key(h,event)) is None,
            exact_citations=checks,source_count=len(citations),effect=theses.effect(record),
            status='passed' if result['status']=='complete' and citations and all(checks) else 'partial',
            limitation='Exact source retention is checked. Direction remains a model interpretation requiring semantic review; this is not a full thesis audit.')
    except Exception as exc:report.update(status='failed',error_type=type(exc).__name__)
    finally:
        with repository.transaction() as tx:
            tx.execute('DELETE FROM records WHERE owner=?',(owner,));tx.execute('DELETE FROM work_jobs WHERE owner=?',(owner,))
    report['elapsed_seconds']=round(time.monotonic()-started,2)
    Path('docs/thesis-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='record'},indent=2))
if __name__=='__main__':asyncio.run(main())
