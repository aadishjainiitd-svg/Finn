import asyncio
import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from pypdf import PdfWriter
from backend import store,documents,research,llm
from backend.main import app
from backend.network import SourceError

@pytest.fixture(autouse=True)
def isolated(tmp_path,monkeypatch):
    monkeypatch.setattr(store,'DATA',tmp_path)
    monkeypatch.setattr(documents,'DATA',tmp_path)
    store.init()
    research.jobs.clear();research.inflight.clear()

def test_unreadable_pdf_has_no_retrievable_partial_version(tmp_path,monkeypatch):
    async def fake_download(url,limit,path):
        path.write_bytes(b'%PDF-1.7\nthis is not a valid PDF')
        return b'',{'url':url,'bytes':42}
    monkeypatch.setattr(documents,'fetch',fake_download)
    with pytest.raises(SourceError,match='extraction failed'):
        asyncio.run(documents.ingest({'symbol':'TEST','name':'Test Limited'},{'kind':'annual','title':'Annual Report','discovery_period':'2026','download_url':'https://example.com/a.pdf','original_url':'https://example.com/a.pdf'},{}))
    assert not list(tmp_path.glob('*.pdf'))
    with store.db() as c: assert c.execute('SELECT count(*) FROM chunks').fetchone()[0]==0

def test_blank_document_is_evidence_gap(tmp_path,monkeypatch):
    async def blank(url,limit,path):
        w=PdfWriter();w.add_blank_page(width=300,height=300)
        with path.open('wb') as f:w.write(f)
        return b'',{'url':url,'bytes':path.stat().st_size}
    monkeypatch.setattr(documents,'fetch',blank)
    with pytest.raises(SourceError,match='too little readable text'):
        asyncio.run(documents.ingest({'symbol':'TEST','name':'Test Limited'},{'kind':'annual','title':'Annual Report','discovery_period':'2026','download_url':'https://example.com/a.pdf','original_url':'https://example.com/a.pdf'},{}))

@pytest.mark.parametrize('code',['http_403','http_429','timeout','identity_unavailable'])
def test_source_failure_becomes_terminal_state_not_empty_success(monkeypatch,code):
    async def fail(symbol):raise SourceError(code,'Source unavailable for this check.')
    monkeypatch.setattr(research,'identity',fail)
    job={};asyncio.run(research.run(job,'TEST','What are the risks?'))
    assert job['status']=='error' and job['error']['code']==code
    assert 'result' not in job

def test_input_validation_and_expired_jobs():
    with TestClient(app) as client:
        assert client.post('/api/research',json={'symbol':'TCS','question':'short'}).status_code==422
        assert client.post('/api/research',json={'symbol':'https://127.0.0.1','question':'What are the risks?'},headers={'X-Finn-Request':'1'}).status_code==422
        assert client.get('/api/jobs/does-not-exist').status_code==410
        assert client.get('/api/evidence/does-not-exist').status_code==410

def test_malformed_model_output_rejected():
    from pydantic import ValidationError
    with pytest.raises(ValidationError):llm.validate_answer({'claims':'not a list'},[])
    with pytest.raises(SourceError):llm.validate_answer({'status':'supported','claims':[],'limitation':''},[])

def test_queue_is_bounded_and_duplicate_requests_coalesce(monkeypatch):
    async def scenario():
        release=asyncio.Event()
        async def hold(job,symbol,question,filing_id=None):await release.wait()
        monkeypatch.setattr(research,'run',hold)
        first=research.submit('TCS','What are the risks?')
        assert research.submit('TCS','What are the risks?')['id']==first['id']
        research.submit('INFY','What are the risks?')
        with pytest.raises(SourceError,match='waiting'):research.submit('ITC','What are the risks?')
        release.set();await asyncio.sleep(0)
    asyncio.run(scenario())
