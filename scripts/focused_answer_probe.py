"""One public, focused held-out question under normal free-tier admission."""
import asyncio,json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend import repository,store,research

async def main():
    store.init();repository.init();job={};started=time.monotonic()
    await research.run(job,'ABB','What does ABB management say about demand and its order backlog?')
    result=job.get('result',{})
    report={'kind':'live source discovery and Groq generation under durable admission; local host',
        'status':result.get('status','failed'),'claims':result.get('claims',[]),'limitation':result.get('limitation'),
        'error':job.get('error'),'usage':job.get('provider_usage'),'elapsed_seconds':round(time.monotonic()-started,2),
        'citations_retained':all(repository.evidence(c['evidence_id']) for claim in result.get('claims',[]) for c in claim['citations'])}
    Path('docs/abb-answer-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))
if __name__=='__main__':asyncio.run(main())
