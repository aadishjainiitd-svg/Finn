"""Real storage contract probe. Never prints a DSN, password or raw exception."""
import json
import subprocess
import sys
import time
import uuid
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend import repository


def main():
    if len(sys.argv)>1:
        owner=sys.argv[1]
        row=repository.get(owner,'probe','record')
        cite=repository.evidence(owner+'-old-p1')
        assert row and row['value']=='survives process restart'
        assert cite and cite['text']=='Synthetic storage probe: original value 100.'
        print(json.dumps({'separate_process_read':True,'old_citation':True}))
        return
    report={'kind':'live Neon requests; evidence content is a synthetic storage fixture',
            'started_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'checks':{}}
    owner='_probe_'+uuid.uuid4().hex
    stage='connect'
    try:
        assert repository.configured(),'No database configured'
        started=time.monotonic()
        with repository.transaction() as tx:
            server=tx.execute('SELECT version() AS server').fetchone()
            tls=tx.execute('SELECT ssl FROM pg_stat_ssl WHERE pid=pg_backend_pid()').fetchone()
            report['server_major']=server['server'].split()[1].split('.')[0]
            report['pooler_server_tls_observed']=bool(tls and tls['ssl'])
            report['tls_scope']='Client-to-pooler TLS verified; no end-to-end TLS claim.'
            report['checks']['client_tls']=bool(tx.connection.pgconn.ssl_in_use)
            assert report['checks']['client_tls']
        report['connect_seconds']=round(time.monotonic()-started,3)
        stage='schema';repository.init();report['checks']['schema']=True
        stage='state'
        row=repository.save(owner,'probe','record',{'value':'survives process restart'},expected=0)
        assert repository.get(owner,'probe','record')['value']==row['value']
        assert repository.get(owner+'-other','probe','record') is None
        report['checks']['owner_isolation']=True
        stage='concurrency'
        def write(i):
            try:repository.save(owner,'probe','race',{'writer':i},expected=0);return True
            except repository.Conflict:return False
        with ThreadPoolExecutor(max_workers=8) as pool:winners=sum(pool.map(write,range(8)))
        assert winners==1;report['checks']['eight_writers_one_winner']=True
        stage='evidence'
        for label,value in [('old',100),('new',99)]:
            version=owner+'-'+label
            repository.retain_document({'version':version,'hash':version,'symbol':'STORAGE-PROBE','kind':'fixture'},
                [{'id':version+'-p1','page':1,'text':f'Synthetic storage probe: {"original" if label=="old" else "replacement"} value {value}.'}])
        assert repository.evidence(owner+'-old-p1')['text']!=repository.evidence(owner+'-new-p1')['text']
        report['checks']['replacement_does_not_alias']=True
        stage='process_restart'
        child=subprocess.run([sys.executable,__file__,owner],capture_output=True,text=True,timeout=60)
        if child.returncode:raise RuntimeError('Separate process verification failed; output withheld')
        report['checks'].update(json.loads(child.stdout))
        stage='cleanup'
        with repository.transaction() as tx:
            tx.execute('DELETE FROM records WHERE owner=?',(owner,))
            for label in ('old','new'):
                tx.execute('DELETE FROM evidence_pages WHERE version=?',(owner+'-'+label,))
                tx.execute('DELETE FROM evidence_versions WHERE version=?',(owner+'-'+label,))
        report['checks']['own_probe_cleanup']=True;report['status']='passed'
    except Exception as exc:
        report.update(status='failed',failed_stage=stage,error_type=type(exc).__name__)
    Path('docs/neon-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))
    if report['status']!='passed':sys.exit(1)


if __name__=='__main__':main()
