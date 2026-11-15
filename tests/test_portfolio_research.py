import asyncio
import pytest
from backend import repository,store,portfolio_research as pull

@pytest.fixture(autouse=True)
def isolated(tmp_path,monkeypatch):
    monkeypatch.setattr(repository,'DATA',tmp_path);monkeypatch.setattr(store,'DATA',tmp_path)
    repository.init();store.init()
    monkeypatch.setattr(pull.research_pack,'get',lambda symbol:None)

def test_book_scope_does_not_import_other_holdings_or_hide_unanswered_companies(monkeypatch):
    def event(symbol):return {'symbol':symbol,'assessment':'assessed','evidence':[{'symbol':symbol,'id':symbol+'-p1','text':'The board approved the expansion of the manufacturing plant.','kind':'filing','hash':symbol,'version':symbol}]}
    store.put('brief-snapshot',{'events':[event('A'),event('B'),event('PRIVATE_OTHER')]})
    calls=[]
    async def synthesize(question,evidence,progress):
        calls.append(evidence)
        assert {e['symbol'] for e in evidence}=={'A','B'}
        return {'status':'supported','evidence':evidence,'claims':[{'text':'A only','citations':[{'evidence_id':'A-p1','quote':evidence[0]['text']}]}],'limitation':'Selected sources.'}
    monkeypatch.setattr(pull,'synthesize',synthesize)
    payload={'symbols':['A','B','MISSING'],'book_version':1,'question':'What changed in the book?'}
    job={};asyncio.run(pull.run(job,'alice',payload));answer=job['result']
    assert answer['status']=='partial' and answer['scope']['symbols']==['A','B','MISSING']
    assert any(g['message'].startswith('B:') for g in answer['gaps'])
    assert any(g['message'].startswith('MISSING:') for g in answer['gaps'])
    cached={};asyncio.run(pull.run(cached,'alice',payload));assert cached['result']['cache_hit']
    asyncio.run(pull.run({},'bob',payload));assert len(calls)==2

def test_empty_document_scope_abstains_without_a_model_call(monkeypatch):
    def forbidden(*args):raise AssertionError('Should not call the model without evidence')
    monkeypatch.setattr(pull,'synthesize',forbidden)
    job={};asyncio.run(pull.run(job,'a',{'symbols':['NEW'],'book_version':2,'question':'What are the risks?'}))
    assert job['result']['status']=='insufficient_evidence' and job['result']['claims']==[]
