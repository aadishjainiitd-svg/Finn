import asyncio
import pytest
from backend import portfolio,repository,store,theses
from backend.llm import resolve_thesis
from backend.network import SourceError


def save(monkeypatch,thesis='Revenue has durable demand.'):
    async def identity(symbol):return {'symbol':symbol,'name':'Test issuer','isin':'TEST'}
    monkeypatch.setattr(portfolio,'identity',identity)
    book=portfolio.book('alice')
    return asyncio.run(portfolio.save_book('alice',[{'symbol':'TCS','thesis':thesis}],book['_version']))


def event():
    return {'id':'filing','revision':'r1','symbol':'TCS','kind':'filing','title':'Results',
        'tier':0,'assessment':'assessed','reason':'Financial results','published_at':'2026-11-15','evidence':[]}


def test_thesis_revision_history_is_atomic_and_weight_changes_do_not_rewrite(monkeypatch):
    book=save(monkeypatch);revision=book['holdings'][0]['thesis_version']
    same=asyncio.run(portfolio.save_book('alice',[{'symbol':'TCS','thesis':book['holdings'][0]['thesis'],'weight':10}],book['_version']))
    assert same['holdings'][0]['thesis_version']==revision
    with pytest.raises(repository.Conflict):
        asyncio.run(portfolio.save_book('alice',[{'symbol':'TCS','thesis':'Different thesis'}],book['_version']))
    assert len(repository.listing('alice','thesis_versions'))==1
    newer=save(monkeypatch,'A revised thesis')
    assert newer['holdings'][0]['thesis_version']!=revision
    assert len(repository.listing('alice','thesis_versions'))==2
    assert repository.listing('bob','thesis_versions')==[]


def test_selection_keeps_qualifier_discards_generated_claim_and_rejects_unknown_source():
    evidence=[{'id':'bytes-p2-c0','symbol':'TCS','kind':'filing','text':'Demand grew in export markets. This excludes our domestic operations.'}]
    raw={'observations':[{'effect':'supports','nature':'interpretation','text':'All markets grew strongly.',
        'citations':[{'source_id':'E1S1'}]}]}
    result=resolve_thesis(raw,evidence)
    assert result[0]['sources'][0]['quote']==evidence[0]['text']
    assert 'All markets' not in str(result)
    raw['observations'][0]['citations'][0]['source_id']='E9S9'
    with pytest.raises(SourceError):resolve_thesis(raw,evidence)
    assert resolve_thesis({'observations':[]},evidence)==[]


def test_contradictions_survive_version_change_and_broken_requires_current_evidence(monkeypatch):
    book=save(monkeypatch);h=book['holdings'][0];e=event()
    observation=lambda direction:{'effect':direction,'sources':[{'quote':'Demand slowed.','evidence':{'id':'quote'}}]}
    record={'symbol':'TCS','thesis_version':h['thesis_version'],'thesis':h['thesis'],'event_id':e['id'],'revision':'r1',
        'observations':[observation('supports'),observation('weakens')]}
    repository.save('alice','thesis_assessments',theses.key(h,e),record)
    store.put('brief-snapshot',{'events':[e]})
    summary=theses.detail('alice',h,[e])
    assert summary['status']=='weakening' and len(summary['items'][0]['assessment']['observations'])==2
    assert theses.detail('bob',h,[e])['status']=='unknown'
    theses.confirm('alice','TCS',h['thesis_version'],True)
    assert theses.detail('alice',h,[e])['status']=='broken'
    newer=save(monkeypatch,'Margins should be resilient.')['holdings'][0]
    assert theses.detail('alice',newer,[e])['status']=='unknown'
    assert len(theses.detail('alice',newer,[e])['history'])==1
    with pytest.raises(SourceError):theses.confirm('alice','TCS',h['thesis_version'],True)
    with pytest.raises(SourceError):theses.confirm('alice','TCS',newer['thesis_version'],True)


def test_thesis_batch_is_owner_scoped_cached_and_preserves_unknown(monkeypatch):
    from backend import llm
    h=save(monkeypatch)['holdings'][0];e=event();store.put('brief-snapshot',{'events':[e]})
    calls=[]
    monkeypatch.setattr(theses,'sources',lambda *args:[{'id':'q'}])
    async def synthesize(question,evidence,progress,mode):
        calls.append(mode);return {'observations':[],'provider':'fixture'}
    monkeypatch.setattr(llm,'synthesize',synthesize)
    progress={};asyncio.run(theses.batch(progress,'alice'))
    assert progress['status']=='complete' and calls==['thesis']
    assert theses.detail('alice',h,[e])['items'][0]['effect']=='unknown'
    asyncio.run(theses.batch({},'alice'));assert len(calls)==1
    assert theses.assessments('bob',[h],[e])['filing'] is None
    # A replaced source cannot inherit its earlier interpretation.
    assert theses.assessments('alice',[h],[{**e,'revision':'r2'}])['filing'] is None


def test_thesis_adverse_adjustment_never_hides_critical_event(monkeypatch):
    h=save(monkeypatch)['holdings'][0];e=event()
    records={e['id']:{'observations':[{'effect':'weakens','sources':[{'evidence':{'id':'q'}}]}]}}
    ranked=portfolio.rank([e],[h],{'feedback':{e['id']:'noise'},'promotions':[]},records)[0]
    assert ranked['tier']==0 and ranked['thesis_status']=='weakens'
    assert ranked['score']==90
    assert any(r['label']=='Adverse thesis evidence' and r['evidence'][0]['id']=='q' for r in ranked['ranking_reasons'])
