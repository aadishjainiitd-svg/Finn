"""Small dated observations, never live coverage or permanent PDF storage."""
import json
from datetime import datetime,timezone
from .config import ROOT
from . import store

def restore():
    path=ROOT/'seed/demo.json'
    if not path.exists():return
    data=json.loads(path.read_text(encoding='utf-8'))
    day=datetime.now(timezone.utc).strftime('%Y-%m-%d')
    baseline=data.get('known_admission',{})
    if baseline.get('day')==day:
        key='admission-'+day;current=store.cached(key) or {'reserved_tokens':0,'requests':0}
        store.put(key,{k:max(current[k],baseline[k]) for k in ('reserved_tokens','requests')})
    if not store.cached('brief-snapshot') and data.get('brief'):
        brief=data['brief'];brief['is_demo_seed']=True;brief['source_status']='demo'
        for coverage in brief['coverage']:
            for source in ('price','filings'):coverage[source]['status']='demo'
        store.put('brief-snapshot',brief)
    from .research import question_key
    for answer in data.get('answers',[]):
        key=question_key(answer['company']['symbol'],answer['question'])
        if not store.cached(key):store.put(key,{**answer,'is_demo_seed':True,'cache_hit':True})
