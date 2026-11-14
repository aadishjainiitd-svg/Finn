"""Checks a saved citation against a real free-service process restart."""
import json
import subprocess
import sys
import time
from pathlib import Path
import httpx

BASE='https://finn-enam-yije.onrender.com'
job=json.loads(Path('data/host-havells.json').read_text(encoding='utf-8'))
cite=job['result']['claims'][0]['citations'][0]
eid=cite['evidence_id']
subprocess.run([sys.executable,'scripts/render_control.py','restart'],check=True)
start=time.monotonic()
with httpx.Client(timeout=10) as c:
    for attempt in range(60):
        try:
            health=c.get(BASE+'/health')
            if health.status_code==200 and time.monotonic()-start>50:
                r=c.get(BASE+'/api/evidence/'+eid)
                if r.status_code in (200,410):
                    result=r.json()
                    correct=r.status_code==410 or (' '.join(cite['quote'].split()) in ' '.join(result['text'].split()) and result['hash']==eid.split('-p')[0])
                    record={'operation':'real Render restart','elapsed_seconds':round(time.monotonic()-start,2),'evidence_status':r.status_code,'correct':correct,'saved_citation':cite,'revision':health.json()['revision']}
                    Path('data/restart-verification.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
                    print(json.dumps(record));raise SystemExit(0 if correct else 1)
        except httpx.HTTPError:pass
        time.sleep(3)
raise SystemExit('Restart did not become ready within the probe deadline.')
