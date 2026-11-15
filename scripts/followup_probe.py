"""Live bounded follow-up using a synthetic conversation and real ABB sources."""
import asyncio,json,sys,time,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend import repository,store,work,conversations,research


async def main():
    owner='_probe_'+uuid.uuid4().hex;started=time.monotonic();store.init();repository.init()
    report={'kind':'Live primary-source requests and Neon persistence; deterministic qualification, synthetic conversation input',
        'earlier_question':'What does ABB management say about electrification demand and backlog?',
        'question':'What risks or qualifications could challenge that outlook?'}
    synthesis_calls=0;original_synthesize=research.synthesize
    async def no_inference(*args,**kwargs):
        nonlocal synthesis_calls
        synthesis_calls+=1
        raise RuntimeError('This zero-inference probe must not call a model')
    research.synthesize=no_inference
    try:
        with repository.transaction() as tx:
            if tx.execute("SELECT COUNT(*) AS n FROM work_jobs WHERE status IN ('queued','running')").fetchone()['n']:raise RuntimeError('Existing work must finish first')
        repository.save(owner,'history','parent',{'symbol':'ABB','filing_id':None,'question':report['earlier_question'],
            'answer':{'claims':[]},'created_at':'2026-11-15T08:00:00+00:00'})
        context=conversations.prepare(owner,'parent','ABB')
        queued=work.enqueue(owner,'research',{'symbol':'ABB','question':report['question'],'conversation':context})
        job=work.claim()
        if not job or job['id']!=queued['id']:raise RuntimeError('Probe did not obtain its lease')
        await work.run_one(job);result=work.get(owner,queued['id']);answer=result.get('result') or {}
        checked=[]
        for claim in answer.get('claims',[]):
            for cite in claim['citations']:
                e=repository.evidence(cite['evidence_id'])
                checked.append(bool(e and e['symbol']=='ABB' and cite['quote'] in ' '.join(e['text'].split())))
        record=repository.get(owner,'history',job['id']);repository.close();repository.init()
        report.update(job_status=result['status'],answer=answer,error=result.get('error'),exact_citations=checked,
            model_attempts=result.get('model_attempts'),provider_usage=result.get('provider_usage_total'),synthesis_calls=synthesis_calls,
            owner_isolation=repository.get(owner+'-other','history',job['id']) is None,
            reconnect_retained=repository.get(owner,'history',job['id'])==record,
            parent_retained=bool(record and record.get('parent_id')=='parent'),
            status='passed' if result['status']=='complete' and checked and all(checked) and synthesis_calls==0 and answer.get('method')=='exact_qualification' else 'partial',
            limitation='Exact citations and context retention checked; source relevance requires separate semantic inspection. Local runtime, not deployed Render.')
    except Exception as exc:report.update(status='failed',error_type=type(exc).__name__)
    finally:
        research.synthesize=original_synthesize
        with repository.transaction() as tx:
            tx.execute('DELETE FROM records WHERE owner=?',(owner,));tx.execute('DELETE FROM work_jobs WHERE owner=?',(owner,))
    report['elapsed_seconds']=round(time.monotonic()-started,2)
    Path('docs/followup-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('answer','question','earlier_question')}))

if __name__=='__main__':asyncio.run(main())
