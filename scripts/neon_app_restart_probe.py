"""Real local HTTP app restart with two empty disposable data directories.

Uses real Neon and retained public ABB evidence. No deployment/model call.
Only the probe's own anonymous session and private records are removed.
"""
import hashlib,json,os,socket,subprocess,sys,tempfile,time
from pathlib import Path
import httpx
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend import repository
from backend.owners import COOKIE

PORT=8016
BASE=f'http://127.0.0.1:{PORT}'

def main():
    report={'kind':'live local HTTP processes with real Neon; empty local caches each start','checks':{}}
    process=None;session_key=None;identity=None
    try:
        with socket.socket() as sock:
            if sock.connect_ex(('127.0.0.1',PORT))==0:raise RuntimeError('Probe port already occupied')
        pack=repository.get('_public','research_packs','primary-pack-v1-ABB')
        if not pack:raise RuntimeError('Run ABB pack probe first')
        evidence=pack['sections'][0]['evidence'][0]
        cookie=None
        for restart in range(2):
            startup=time.monotonic()
            with tempfile.TemporaryDirectory(prefix='finn-restart-') as data:
                env={**os.environ,'FINN_DATA_DIR':data,'FINN_WORKER':'false','FINN_PREWARM':'false'}
                process=subprocess.Popen([sys.executable,'-m','uvicorn','backend.main:app','--host','127.0.0.1','--port',str(PORT),'--no-access-log'],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                with httpx.Client(base_url=BASE,timeout=40) as client:
                    deadline=time.monotonic()+90
                    while time.monotonic()<deadline:
                        if process.poll() is not None:raise RuntimeError('App startup failed; inspect separately without secrets')
                        try:
                            if client.get('/health').status_code==200:break
                        except httpx.HTTPError:pass
                        time.sleep(.5)
                    else:raise RuntimeError('App readiness timeout')
                    report.setdefault('startup_seconds',[]).append(round(time.monotonic()-startup,3))
                    if cookie:client.cookies.set(COOKIE,cookie)
                    session=client.get('/api/session');session.raise_for_status()
                    if not restart:
                        cookie=client.cookies.get(COOKIE);session_key=hashlib.sha256(cookie.encode()).hexdigest()
                        identity=repository.get('_system','sessions',session_key)['owner']
                        response=client.post('/api/review',headers={'X-Finn-Request':'1'},json={'action':'pin','event_id':'restart-probe','value':True})
                        response.raise_for_status()
                    else:
                        assert session.json()['review']['pins'].get('restart-probe') is True
                        report['checks']['private_state_after_restart']=True
                    response=client.get('/api/evidence/'+evidence['id']);response.raise_for_status()
                    assert response.json()['text']==evidence['text'] and response.json()['page']==evidence['page']
                    report['checks']['retained_citation_'+str(restart)]=True
                    stored=client.get('/api/research-pack/ABB');stored.raise_for_status()
                    assert stored.json()['pack']['documents'][0]['version']==pack['documents'][0]['version']
                    report['checks']['research_pack_'+str(restart)]=True
                process.terminate();process.wait(timeout=15);process=None
        report['status']='passed'
    except Exception as exc:report.update(status='failed',error_type=type(exc).__name__)
    finally:
        if process and process.poll() is None:process.terminate();process.wait(timeout=15)
        if identity or session_key:
            with repository.transaction() as tx:
                if identity:tx.execute('DELETE FROM records WHERE owner=?',(identity,))
                if session_key:tx.execute("DELETE FROM records WHERE owner='_system' AND bucket='sessions' AND id=?",(session_key,))
    Path('docs/neon-app-restart-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))
    if report['status']!='passed':raise SystemExit(1)

if __name__=='__main__':main()
