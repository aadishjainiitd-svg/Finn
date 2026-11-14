import hashlib
import json
import pytest
from backend import store
from backend.documents import validate_identity
from backend.llm import validate_answer
from backend.llm import resolve_spans
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

def test_overlap_quote_resolves_only_within_supplied_same_page_version():
    a={'status':'supported','claims':[{'text':'Demand was softer.','nature':'reported','citations':[{'evidence_id':'a','quote':'Demand was softer across retail and project segments.'}]}],'limitation':''}
    evidence=[{'id':'a','hash':'version','page':2,'text':'Demand was softer across retail'},
              {'id':'b','hash':'version','page':2,'text':'Demand was softer across retail and project segments.'}]
    assert validate_answer(a,evidence)['claims'][0]['citations'][0]['evidence_id']=='b'
    evidence[1]['page']=3
    with pytest.raises(SourceError):validate_answer(a,evidence)
    evidence[1]['page']=2;evidence[1]['hash']='replacement'
    with pytest.raises(SourceError):validate_answer(a,evidence)

def test_identity_type_and_period_mismatch():
    company={'name':'Havells India Limited'}
    doc={'kind':'transcript','discovery_period':'Oct 2026'}
    with pytest.raises(SourceError,match='issuer'):validate_identity(company,doc,'Tata Consultancy Services Transcript October 2026')
    with pytest.raises(SourceError,match='transcript'):validate_identity(company,doc,'Havells India Limited investor presentation October 2026')
    with pytest.raises(SourceError,match='date'):validate_identity(company,doc,'Havells India Limited transcript October 2025')
    assert validate_identity(company,{'kind':'annual','discovery_period':'Annual Report 2026'},'Havells India Limited Annual Report. AGM notice for 2026-27. Annual report 2025-26.')=='2025-26'
    assert validate_identity(company,doc,'Havells India Limited transcript October 2026 Q2 FY27. Comparison with Q4 FY26.')=='Q2 FY27'

def test_issuer_domain_and_period_discovery():
    html='''<h1>Astral</h1><a href="https://astralpipes.example"><i class="icon-link"></i>Website</a>
    <div class="concalls"><li><div>Feb 2026</div><a href="https://www.bseindia.com/old.pdf">Transcript</a></li>
    <li><div>Nov 2026</div><a href="https://corporate.example/new.pdf">Transcript</a></li></div>'''
    docs=parse_discovery(html,{'symbol':'ASTRAL','name':'Astral Limited'},{'corporate.example'})
    assert docs[0]['discovery_period']=='Nov 2026'
    assert docs[0]['download_url']=='https://corporate.example/new.pdf'

def test_symbol_and_private_url_rejection():
    assert ticker(' nse:HAVELLS.NS ')=='HAVELLS'
    with pytest.raises(SourceError):ticker('Havells India')
    for url in ('http://example.com','https://127.0.0.1/a','https://user:pw@example.com/a'):
        with pytest.raises(SourceError):validate_url(url)

def test_discovery_never_substitutes_presentation_for_transcript():
    html='<h1>Havells</h1><div class="concalls"><a href="https://www.bseindia.com/test.pdf">PPT</a></div>'
    assert parse_discovery(html,{'symbol':'HAVELLS','name':'Havells India Limited'})==[]

def test_sentence_selection_attaches_original_text_and_stable_id():
    e=[{'id':'sha-p9-c1','text':'Management: Demand improved. We cannot give a firm timeline.'}]
    data={'status':'supported','claims':[{'text':'Management declines a firm timeline.','nature':'reported','citations':[{'source_id':'E1S2'}]}],'limitation':''}
    a=resolve_spans(data,e)
    assert a['claims'][0]['citations']==[{'evidence_id':'sha-p9-c1','quote':'We cannot give a firm timeline.'}]
    data['claims'][0]['citations'][0]['source_id']='E2S1'
    with pytest.raises(SourceError):resolve_spans(data,e)

def test_analyst_question_cannot_be_used_as_management_evidence():
    from backend.llm import source_spans
    e=[{'id':'sha-p9-c0','kind':'transcript','management_speakers':['Anil Rai Gupta'],'speaker_before':'',
        'text':'Pavan Kumar: Margins fell by 380 basis points. Is that correct? Anil Rai Gupta: Aluminium prices affected margins. We cannot give a firm timeline.'}]
    quotes=[s['quote'] for s in source_spans(e).values()]
    assert all('380' not in q and 'Is that correct' not in q for q in quotes)
    assert any('Aluminium prices' in q for q in quotes)
    e[0]['text']='Over to you, Samir. Samir Seksaria: We prioritise investments while maintaining margin discipline.'
    e[0]['management_speakers']=['Samir Seksaria']
    assert any('margin discipline' in s['quote'] for s in source_spans(e).values())

def test_parser_replacement_also_versions_citation_coordinates():
    from backend.documents import extraction_version
    digest='a'*64
    assert extraction_version(digest,'parser-a')!=extraction_version(digest,'parser-b')
    assert extraction_version(digest,'parser-a')==extraction_version(digest,'parser-a')

def test_answer_cache_hit_and_source_version_invalidation():
    from backend.research import question_key,recent_answer
    doc={'hash':'bytes','version':'bytes-xparser','download_url':'https://example.com/report.pdf'}
    with store.db() as c:c.execute('INSERT INTO documents VALUES (?,?,?,?)',(doc['version'],'TEST','annual',json.dumps(doc)))
    result={'documents':[doc],'claims':[],'gaps':[]}
    store.put(question_key('TEST','What are the risks?'),result)
    store.put('latest-document-'+doc['download_url'],doc['version'])
    assert recent_answer('TEST','What are the risks?')['cache_hit']
    store.put('latest-document-'+doc['download_url'],'new-bytes-xparser')
    assert recent_answer('TEST','What are the risks?') is None
