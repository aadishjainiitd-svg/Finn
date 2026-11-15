"""Live discovery/extraction/retention probe. No model request or private data."""
import asyncio,json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend import repository,store
from backend.sources import identity,discover
from backend.documents import ingest
from backend.network import SourceError

async def main():
    symbol=sys.argv[1] if len(sys.argv)>1 else 'ABB'
    report={'kind':'live source requests and Neon evidence retention'+('; live free-tier model request' if '--answer' in sys.argv else '; no model generation'),'symbol':symbol,'documents':[]}
    started=time.monotonic();store.init();repository.init()
    try:
        company=await identity(symbol)
        report['issuer']=company
        docs=await discover(company,annual_count=2,transcript_count=4)
        report['discovered']=[{k:d[k] for k in ('kind','discovery_period','original_url')} for d in docs]
        for source in docs:
            progress={};timer=time.monotonic()
            try:
                doc=await ingest(company,source,progress)
                with store.db() as c:
                    row=c.execute('SELECT id,page,text FROM chunks WHERE hash=? ORDER BY page,id LIMIT 1',(doc['version'],)).fetchone()
                retained=repository.evidence(row['id'])
                assert retained and retained['text']==row['text'] and retained['page']==row['page']
                result={k:doc.get(k) for k in ('kind','period','version','pages','processing_seconds')}
                result.update(status='retained',end_to_end_seconds=round(time.monotonic()-timer,2),
                    peak_mb=progress.get('processing_peak_mb'),citation_resolved=True)
            except SourceError as exc:result={'kind':source['kind'],'status':'unavailable','code':exc.code,'message':exc.message}
            except Exception as exc:result={'kind':source['kind'],'status':'failed','error_type':type(exc).__name__}
            report['documents'].append(result)
            print(json.dumps(result),flush=True)
        report['status']='passed' if len(report['documents'])==6 and all(d['status']=='retained' for d in report['documents']) else 'partial'
        if '--pack' in sys.argv:
            from backend.research_pack import build
            pack=await build({},symbol)
            report['research_pack']={'documents':len(pack['documents']),'facts':len(pack['facts']),
                'sections':len(pack['sections']),'gaps':pack['gaps'],
                'fact_citations_valid':all(f['quote'] in f['evidence']['text'] and f['header_quote'] in f['evidence']['text'] for f in pack['facts']),
                'revenue_summary':[{'year':f['year'],'crore':f['crore'],'scope':f['scope'],'page':f['evidence']['page']} for f in pack['facts'] if f['metric']=='revenue']}
        if '--answer' in sys.argv:
            from backend import research
            question='What does ABB management say about demand and its order backlog?'
            job={}
            await research.run(job,symbol,question)
            result=job.get('result',{})
            report['focused_answer']={'status':job.get('status'),'answer_status':result.get('status'),
                'claims':result.get('claims',[]),'limitation':result.get('limitation'),
                'provider_usage':job.get('provider_usage'),
                'error':job.get('error'),
                'citations_retained':all(repository.evidence(c['evidence_id']) for claim in result.get('claims',[]) for c in claim['citations'])}
            if result.get('status')!='supported' or not result.get('claims'):report['status']='partial'
    except Exception as exc:report.update(status='failed',error_type=type(exc).__name__)
    report['elapsed_seconds']=round(time.monotonic()-started,2)
    Path('docs/source-pack-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({'status':report['status'],'elapsed_seconds':report['elapsed_seconds']}))

if __name__=='__main__':asyncio.run(main())
