import json
from backend import repository,store,work
from backend.usage import for_owner

def test_usage_is_owner_scoped_and_unknown_is_not_zero(tmp_path,monkeypatch):
    monkeypatch.setattr(repository,'DATA',tmp_path);monkeypatch.setattr(store,'DATA',tmp_path)
    repository.init();store.init()
    a=work.enqueue('alice','research',{'question':'Do not export this question'})
    job=work.claim();work.finish(job,{'status':'complete','provider_usage':{'total_tokens':123,'prompt_tokens':100,'completion_tokens':23}})
    work.enqueue('alice','research',{'question':'Interrupted question'})
    job=work.claim();work.finish(job,{'status':'error'})
    work.enqueue('bob','research',{'question':'Other owner'})
    job=work.claim();work.finish(job,{'status':'complete','provider_usage':{'total_tokens':999}})
    report=for_owner('alice')
    assert report['observed_tokens']==123 and report['unknown_usage_jobs']==1
    assert report['currency_cost'] is None and len(report['reports'])==2
    assert 'question' not in json.dumps(report['reports']).lower()
