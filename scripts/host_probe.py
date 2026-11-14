"""Record safe, bounded live verification artifacts; never records request credentials."""
import json
import sys
import time
from pathlib import Path
import httpx

base='https://finn-enam-yije.onrender.com'
symbol=sys.argv[1] if len(sys.argv)>1 else 'HAVELLS'
question='What risks to demand or margins does management discuss in the latest earnings call, and what business context does the annual report provide?'
with httpx.Client(timeout=90) as c:
    start=time.monotonic()
    r=c.post(base+'/api/research',json={'symbol':symbol,'question':question})
    print('submit',r.status_code,flush=True); r.raise_for_status(); job=r.json()
    while job['status']=='running':
        time.sleep(3)
        r=c.get(base+'/api/jobs/'+job['id']); r.raise_for_status(); job=r.json()
        print(json.dumps({k:job.get(k) for k in ('status','stage','pages','document')}),flush=True)
        if time.monotonic()-start>420: raise SystemExit('Hosted probe exceeded 420s; job may still be running.')
    Path('data/host-'+symbol.lower()+'.json').write_text(json.dumps(job,indent=2),encoding='utf-8')
    print(json.dumps({'status':job['status'],'elapsed':job.get('elapsed_seconds'),'error':job.get('error'),
        'documents':[{k:d.get(k) for k in ('kind','pages','bytes','combined_peak_mb','processing_seconds','period')} for d in job.get('documents',[])],
        'claims':job.get('result',{}).get('claims'), 'gaps':job.get('gaps')}),flush=True)
