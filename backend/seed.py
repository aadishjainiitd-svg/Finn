"""Small dated observations, never live coverage or permanent PDF storage."""
import json
from .config import ROOT
from . import store

def restore():
    path=ROOT/'seed/demo.json'
    if not path.exists():return
    data=json.loads(path.read_text(encoding='utf-8'))
    if not store.cached('brief-snapshot') and data.get('brief'):
        brief=data['brief'];brief['is_demo_seed']=True;brief['source_status']='demo'
        for coverage in brief['coverage']:
            for source in ('price','filings'):coverage[source]['status']='demo'
        store.put('brief-snapshot',brief)
    from .research import question_key
    for answer in data.get('answers',[]):
        key=question_key(answer['company']['symbol'],answer['question'])
        if not store.cached(key):store.put(key,{**answer,'is_demo_seed':True,'cache_hit':True})
