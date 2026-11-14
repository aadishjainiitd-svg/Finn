"""Record safe, bounded live verification artifacts; never records request credentials."""
import json
import sys
import time
from datetime import datetime,timezone
from pathlib import Path
import httpx

base='https://finn-enam-yije.onrender.com'
symbol=sys.argv[1] if len(sys.argv)>1 else 'HAVELLS'
question='What risks to demand or margins does management discuss in the latest earnings call, and what business context does the annual report provide?'
with httpx.Client(timeout=90) as c:
    revision=c.get(base+'/health').json().get('revision','unknown')
    start=time.monotonic()
    r=c.post(base+'/api/research',json={'symbol':symbol,'question':question})
    print('submit',r.status_code,flush=True); r.raise_for_status(); job=r.json()
    last=None
    while job['status']=='running':
        time.sleep(3)
        r=c.get(base+'/api/jobs/'+job['id']); r.raise_for_status(); job=r.json()
        state=(job['status'],job['stage'],int(job.get('pages',0) or 0)//40)
        if state!=last:print(json.dumps({k:job.get(k) for k in ('status','stage','pages','document')}),flush=True);last=state
        if time.monotonic()-start>420: raise SystemExit('Hosted probe exceeded 420s; job may still be running.')
    Path('data/host-'+symbol.lower()+'.json').write_text(json.dumps(job,indent=2),encoding='utf-8')
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    Path(f'data/host-{symbol.lower()}-{revision}-{stamp}.json').write_text(json.dumps(job,indent=2),encoding='utf-8')
    print(json.dumps({'status':job['status'],'elapsed':job.get('elapsed_seconds'),'error':job.get('error'),
        'documents':[{k:d.get(k) for k in ('kind','pages','bytes','combined_peak_mb','processing_seconds','period')} for d in job.get('documents',[])],
        'claims':job.get('result',{}).get('claims'), 'gaps':job.get('gaps')}),flush=True)
