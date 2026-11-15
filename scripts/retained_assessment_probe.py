"""Replay retained primary bytes; update public assessments, not fetch dates."""
import json,sys,time,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend import brief,store,repository
from backend.results import extract
from backend.sources import now

def main():
    report={'kind':'Retained primary-source replay with real Neon public-cache writes; no fresh download or inference','checked_at':now(),'policy':brief.ASSESSMENT_POLICY}
    started=time.monotonic()
    try:
        before=store.cached('brief-snapshot')
        if not before:raise ValueError('No retained snapshot')
        # Existing metadata remains the authoritative source receipt. The
        # replay must not make stale source coverage appear freshly fetched.
        receipt=before.get('checked_at')
        brief.upgrade_stored_snapshot()
        after=store.cached('brief-snapshot')
        assert after['checked_at']==receipt
        report['filings']=sum(e['kind']=='filing' for e in after['events'])
        report['pending']=sum(e['assessment']=='pending' for e in after['events'])
        report['selected']=[]
        for symbol,title in [('ABB','Press Release'),('CERA','Copy of Newspaper Publication')]:
            candidates=[e for e in after['events'] if e['symbol']==symbol and title.lower() in (e['title']+' '+e.get('description','')).lower()]
            for event in candidates:
                report['selected'].append({'id':event['id'],'symbol':symbol,'tier':event['tier'],'assessment':event['assessment'],'reason':event['reason'],
                    'pages':[e['page'] for e in event.get('evidence',[])]})
        with store.db() as c:
            row=c.execute("SELECT hash,meta FROM documents WHERE symbol='ABB' AND kind='filing' AND meta LIKE '%Outcome of Board Meeting%' ORDER BY hash LIMIT 1").fetchone()
            if row:
                doc=json.loads(row['meta']);rows=c.execute('SELECT id,page,text FROM chunks WHERE hash=? ORDER BY page,id',(row['hash'],)).fetchall()
                result=extract(doc,rows)
                report['abb_quarterly']={'verified_tables':len(result['tables']),'gaps':result['gaps'],'version':row['hash']}
        report['source_checked_at_preserved']=True
        report['status']='passed'
        report['limitation']='Processing and selected regression checks only. No full semantic gold-set acceptance or hosted runtime validation.'
    except Exception as exc:report.update(status='failed',error_type=type(exc).__name__)
    finally:repository.close()
    report['elapsed_seconds']=round(time.monotonic()-started,2)
    report['implementation_sha256']=hashlib.sha256(Path('backend/brief.py').read_bytes()).hexdigest()
    Path('docs/retained-assessment-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
