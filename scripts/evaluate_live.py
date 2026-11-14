"""Execute preregistered questions; output is ungraded until source audit."""
import json,time,sys
from pathlib import Path
import httpx
ROOT=Path(__file__).resolve().parents[1]
cases=json.loads((ROOT/'docs/evaluation-cases.json').read_text())['cases']
base=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8000'
only=set(sys.argv[2:])
out=ROOT/'data/evaluation';out.mkdir(exist_ok=True)
with httpx.Client(timeout=95) as c:
    for case in cases:
        if case['type'].endswith('fixture') or (only and case['id'] not in only):continue
        started=time.monotonic();r=c.post(base+'/api/research',json={'symbol':case['symbol'],'question':case['question']})
        j=r.json();previous=None
        while j.get('status')=='running' and time.monotonic()-started<420:
            if j.get('stage')!=previous:
                previous=j.get('stage');print(case['id'],previous,flush=True)
            time.sleep(2);r=c.get(base+'/api/jobs/'+j['id']);j=r.json()
        record={'case':case['id'],'surface':base,'http_status':r.status_code,'wall_seconds':round(time.monotonic()-started,2),'job':j}
        (out/(case['id']+'.json')).write_text(json.dumps(record,indent=2),encoding='utf-8')
        print(json.dumps({'case':case['id'],'status':j.get('status',j.get('error',{}).get('code')),'answer':j.get('result',{}).get('status'),'seconds':record['wall_seconds']}),flush=True)
