"""Package only dated, audited observations; no secrets or full PDFs."""
import asyncio,json,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from backend import store,brief,research
from backend.llm import grounded_display,admission_key
from backend.config import MODEL

async def main():
    store.init();snapshot=await brief.get_brief(force=True)
    if brief.assessment_task:
        brief.assessment_task.cancel();await asyncio.gather(brief.assessment_task,return_exceptions=True)
    candidate=next(e for e in snapshot['events'] if e['symbol']=='HDFCBANK' and 'Director' in e['title'])
    async with research.worker:await brief.assess(candidate)
    snapshot=await brief.get_brief(force=True)
    if brief.assessment_task:
        brief.assessment_task.cancel();await asyncio.gather(brief.assessment_task,return_exceptions=True)
    for event in snapshot['events']:event['evidence']=event.get('evidence',[])[:1]
    answers=[]
    for case in ('S1','S2','S3'):
        answer=grounded_display(json.loads((ROOT/'data/evaluation'/f'{case}.json').read_text(encoding='utf-8'))['job']['result'])
        cited={c['evidence_id'] for claim in answer['claims'] for c in claim['citations']}
        answer['evidence']=[e for e in answer['evidence'] if e['id'] in cited]
        answer['is_demo_seed']=True;answers.append(answer)
    folder=ROOT/'seed';folder.mkdir(exist_ok=True)
    day=datetime.now(timezone.utc).strftime('%Y-%m-%d')
    known={'day':day,**(store.cached('admission-'+day) or {'reserved_tokens':0,'requests':0})}
    model_admissions=[{'provider':'groq','model':MODEL,'day':day,**(store.cached(admission_key('groq',MODEL,day)) or {'reserved_tokens':0,'requests':0})}]
    (folder/'demo.json').write_text(json.dumps({'captured_at':snapshot['checked_at'],'known_admission':known,'model_admissions':model_admissions,'brief':snapshot,'answers':answers},ensure_ascii=False),encoding='utf-8')
    print(json.dumps({'seed_bytes':(folder/'demo.json').stat().st_size,'filings':snapshot['counts'],'answers':[a['company']['symbol'] for a in answers]}))
asyncio.run(main())
