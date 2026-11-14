import hashlib
import json
import pytest
from backend import store
from backend.documents import validate_identity
from backend.llm import validate_answer
from backend.network import SourceError,validate_url
from backend.sources import ticker,parse_discovery

@pytest.fixture(autouse=True)
def isolated_store(tmp_path,monkeypatch):
    monkeypatch.setattr(store,'DATA',tmp_path)
    store.init()

def test_unknown_citation_and_modified_quote_rejected():
    e=[{'id':'version-p1-c0','text':'Demand was softer, but margins improved.'}]
    a={'status':'supported','claims':[{'text':'Demand was softer.','nature':'reported','citations':[{'evidence_id':'other','quote':'Demand was softer'}]}],'limitation':''}
    with pytest.raises(SourceError,match='source check'):validate_answer(a,e)
    a['claims'][0]['citations'][0]['evidence_id']='version-p1-c0'
    assert validate_answer(a,e)['status']=='supported'
    a['claims'][0]['citations'][0]['quote']='Demand was stronger'
    with pytest.raises(SourceError):validate_answer(a,e)

def test_same_url_replacement_never_relabels_old_citation():
    ids=[]
    for text in ('Revenue was 100 crore.','Revenue was 200 crore.'):
        digest=hashlib.sha256(text.encode()).hexdigest();eid=digest+'-p1-c0';ids.append(eid)
        with store.db() as c:
            c.execute('INSERT INTO documents VALUES (?,?,?,?)',(digest,'TEST','annual',json.dumps({'url':'https://example.com/report.pdf','hash':digest})))
            c.execute('INSERT INTO chunks VALUES (?,?,?,?)',(eid,digest,1,text))
    store.init() # re-open the same persistent cache, like a process restart
    assert store.evidence(ids[0])['text']=='Revenue was 100 crore.'
    assert store.evidence(ids[1])['text']=='Revenue was 200 crore.'
    with store.db() as c:c.execute('DELETE FROM documents WHERE hash=?',(ids[0].split('-p')[0],))
    assert store.evidence(ids[0]) is None
    assert store.evidence(ids[1])['text']=='Revenue was 200 crore.'

def test_identity_type_and_period_mismatch():
    company={'name':'Havells India Limited'}
    doc={'kind':'transcript','discovery_period':'Oct 2026'}
    with pytest.raises(SourceError,match='issuer'):validate_identity(company,doc,'Tata Consultancy Services Transcript October 2026')
    with pytest.raises(SourceError,match='transcript'):validate_identity(company,doc,'Havells India Limited investor presentation October 2026')
    with pytest.raises(SourceError,match='date'):validate_identity(company,doc,'Havells India Limited transcript October 2025')

def test_symbol_and_private_url_rejection():
    assert ticker(' nse:HAVELLS.NS ')=='HAVELLS'
    with pytest.raises(SourceError):ticker('Havells India')
    for url in ('http://example.com','https://127.0.0.1/a','https://user:pw@example.com/a'):
        with pytest.raises(SourceError):validate_url(url)

def test_discovery_never_substitutes_presentation_for_transcript():
    html='<h1>Havells</h1><div class="concalls"><a href="https://www.bseindia.com/test.pdf">PPT</a></div>'
    assert parse_discovery(html,{'symbol':'HAVELLS','name':'Havells India Limited'})==[]
