"""Recheck the retained live view; no new model or source request."""
import json,sys,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend import repository,research_pack,narrative,store,statements
from backend.sources import now

pack=repository.get('_public','research_packs',research_pack.key('ABB'))
annual=[d for d in pack['documents'] if d['kind']=='annual']
for doc in pack['documents']:store.rehydrate(doc['version'])
corrected=narrative.sanitise(pack['narrative'],annual[:1]);facts=[]
with store.db() as c:
    for doc in annual:
        facts.extend(statements.extract(doc,c.execute('SELECT id,page,text FROM chunks WHERE hash=? ORDER BY page,id',(doc['version'],)).fetchall()))
financials=statements.compact(statements.analyse(facts))
for observation in corrected['observations']:
    for source in observation['sources']:
        evidence=repository.evidence(source['evidence']['id'])
        assert evidence and source['quote'] in evidence['text'] and evidence['symbol']=='ABB'
repository.save('_public','research_packs',research_pack.key('ABB'),{**pack,'narrative':corrected,'financials':financials,'analysis_checked_at':now()})
report={'kind':'Retained real ABB pages and live Neon read/write; no new download or model inference',
    'checked_at':now(),'source_checked_at':pack['checked_at'],'narrative':corrected,
    'financial_facts':len(financials['facts']),'ratios_by_year':{y['year']:list(y.get('ratios',{})) for y in financials['years']},
    'exact_citations':True,'status':'partial',
    'limitation':'Business/favourable/adverse points inspected; no substantive accounting concern selected. No exhaustive risk coverage or hosted acceptance claimed.',
    'implementation_sha256':{name:hashlib.sha256(Path(name).read_bytes()).hexdigest() for name in ('backend/narrative.py','backend/llm.py','backend/statements.py')}}
Path('docs/research-view-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='narrative'}))
repository.close()
