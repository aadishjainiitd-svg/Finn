import asyncio,json,time
import httpx,pytest
from backend import store,research,brief,llm,documents
from backend.calculations import numerical_answer
from backend.network import SourceError

@pytest.fixture(autouse=True)
def isolation(tmp_path,monkeypatch):
    monkeypatch.setattr(store,'DATA',tmp_path);monkeypatch.setattr(documents,'DATA',tmp_path);store.init()
    research.jobs.clear();research.inflight.clear();brief.filing_inflight.clear();brief.events_by_id.clear()
    monkeypatch.setattr(research,'worker',asyncio.Lock());monkeypatch.setattr(research,'background_active',False)
    monkeypatch.setattr(llm,'lock',asyncio.Lock());monkeypatch.setattr(llm,'next_allowed',0)
    monkeypatch.setattr(llm,'daily_remaining',None);monkeypatch.setattr(llm,'daily_remaining_day',None)

def test_display_cannot_invert_a_valid_quotation_and_cache_uses_same_renderer():
    e={'id':'v-p1','kind':'annual','text':'Revenue decreased by ten percent.'}
    raw={'provider':'groq','status':'supported','claims':[{'text':'Revenue increased by ten percent.','nature':'reported','citations':[{'evidence_id':e['id'],'quote':e['text']}]}],'evidence':[e],'limitation':''}
    result=llm.grounded_display(raw)
    assert result['claims'][0]['text']=='Annual report: Revenue decreased by ten percent.'
    assert 'increased' not in result['claims'][0]['text']
    assert llm.grounded_display(result)==result

def test_revised_filing_cannot_inherit_routine_assessment_even_at_same_url():
    row={'symbol':'TCS','seq_id':'1','desc':'Newspaper Publication','attchmntFile':'https://example.com/a.pdf','an_dt':'14-Nov-2026 10:00:00'}
    e=brief.make_filing(row,'2026-11-14')
    store.put('assessed-'+e['id'],{'source_signature':e['source_signature'],'version':'old','text':'Please find enclosed the newspaper publication confirmation.','evidence':[]})
    assert brief.make_filing(row,'2026-11-14')['assessment']=='routine'
    store.put('latest-document-filing-'+row['attchmntFile'],'new')
    assert brief.make_filing(row,'2026-11-14')['assessment']=='pending'
    assert brief.make_filing({**row,'attchmntFile':'https://example.com/new.pdf'},'2026-11-14')['assessment']=='pending'

def test_missing_transcript_is_explicit_and_cache_hit_makes_no_model_call(monkeypatch):
    calls=[];doc={'hash':'h','version':'h-annual','kind':'annual','title':'Annual report','download_url':'https://example.com/report.pdf'}
    with store.db() as c:c.execute('INSERT INTO documents VALUES (?,?,?,?)',(doc['version'],'TEST','annual',json.dumps(doc)))
    async def identity(symbol):return {'symbol':symbol,'name':'Test Limited'}
    async def discover(company):return [doc]
    async def ingest(*args):return doc
    async def synthesize(*args):
        calls.append(1);return {'provider':'groq','status':'insufficient_evidence','claims':[],'evidence':[],'limitation':'No transcript passage.'}
    monkeypatch.setattr(research,'identity',identity);monkeypatch.setattr(research,'discover',discover);monkeypatch.setattr(research,'ingest',ingest);monkeypatch.setattr(research,'retrieve',lambda *_:[]);monkeypatch.setattr(research,'synthesize',synthesize)
    async def scenario():
        question='What does management say in the missing earnings transcript?';job={'status':'running'}
        await research.run(job,'TEST',question)
        assert job['status']=='complete' and job['result']['status']=='insufficient_evidence'
        assert job['gaps']==[{'kind':'transcript','code':'missing_document','message':'No primary transcript was discovered.'}]
        assert research.submit('TEST',question)['result']['cache_hit']
        assert len(calls)==1
    asyncio.run(scenario())

def test_kind_is_part_of_provenance_coordinates():
    assert documents.extraction_version('abc',kind='filing')!=documents.extraction_version('abc',kind='transcript')

def test_numeric_conversion_and_incompatible_period_refusal():
    e={'id':'h-p3','hash':'h','page':3,'kind':'transcript','period':'Q2 FY27','text':'Revenue for the quarter was INR 73,188 crore.','speaker_before':'Manager','management_speakers':['Manager']}
    result=numerical_answer('Convert quarterly revenue from crore to lakh.',[e])
    assert result['status']=='supported' and '7,318,800.00 lakh' in result['claims'][0]['text']
    assert result['calculation']['operand']['scope']=='Not specified in the cited narrative'
    assert numerical_answer('Calculate Q2 revenue growth versus H1 revenue.',[e])['status']=='insufficient_evidence'

def test_shared_job_retention_and_filing_coalescing(monkeypatch):
    research.jobs.update({str(n):{'status':'error'} for n in range(40)})
    async def scenario():
        gate=asyncio.Event()
        async def run(job,event):await gate.wait()
        monkeypatch.setattr(brief,'run_filing',run)
        brief.events_by_id['event']={'id':'event','symbol':'TEST','evidence':[],'source_signature':'x','url':'https://example.com/a.pdf'}
        first=brief.submit_filing('event');assert brief.submit_filing('event')['id']==first['id']
        assert len(research.jobs)<=25
        gate.set();await asyncio.sleep(0)
    asyncio.run(scenario())

def test_provider_429_is_bounded_and_preserves_source_state(monkeypatch):
    client=httpx.AsyncClient;requests=[]
    def respond(request):requests.append(request);return httpx.Response(429,headers={'retry-after':'70'},json={'error':'fixture'})
    monkeypatch.setattr(llm.httpx,'AsyncClient',lambda **kw:client(transport=httpx.MockTransport(respond),**kw))
    e={'id':'h-p1','symbol':'TEST','kind':'annual','period':'2026','page':1,'text':'The company manufactures pipes and valves.'}
    with pytest.raises(SourceError,match='quota'):asyncio.run(llm.synthesize('What does this company do?',[e],{}))
    assert len(requests)==1 and llm.next_allowed>time.monotonic()+60

def test_cancelled_worker_is_reaped_and_partial_state_removed(monkeypatch):
    children=[];real_create=asyncio.create_subprocess_exec
    async def fake_fetch(url,max_bytes,path):path.write_bytes(b'%PDF-1.4 fixture');return None,{'url':url,'bytes':16,'content_type':'application/pdf'}
    async def worker(*args,**kwargs):
        proc=await real_create(args[0],'-c','import json,time; print(json.dumps({"page":1,"text":"Test Limited annual report 2026. "*100}),flush=True); time.sleep(60)',**kwargs);children.append(proc);return proc
    monkeypatch.setattr(documents,'fetch',fake_fetch);monkeypatch.setattr(documents.asyncio,'create_subprocess_exec',worker)
    async def scenario():
        progress={};task=asyncio.create_task(documents.ingest({'symbol':'TEST','name':'Test Limited'},{'kind':'annual','title':'Annual Report 2026','discovery_period':'Annual Report 2026','download_url':'https://example.com/a.pdf','original_url':'https://example.com/a.pdf'},progress))
        async with asyncio.timeout(5):
            while not progress.get('pages'):await asyncio.sleep(.02)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):await task
    asyncio.run(scenario());assert children[0].returncode is not None
    with store.db() as c:assert c.execute('SELECT count(*) FROM chunks').fetchone()[0]==0
    assert not list(documents.DATA.glob('*.pdf'))


def test_failed_assessment_remains_pending_without_automatic_retry():
    store.put('assessed-event',{'version':None,'source_signature':'x','error':'Large attachment remains pending','evidence':[]})
    store.put('latest-document-filing-https://example.com/a.pdf','parsed-version')
    assert brief.valid_assessment('event','x','https://example.com/a.pdf')['error']

def test_source_connection_pins_validated_address_and_preserves_tls_hostname(monkeypatch):
    import socket
    from backend import network
    seen=[];client=httpx.AsyncClient
    monkeypatch.setattr(network.socket,'getaddrinfo',lambda *a,**kw:[(socket.AF_INET,socket.SOCK_STREAM,6,'',('8.8.8.8',443))])
    def response(request):
        seen.append(request)
        assert request.url.host=='8.8.8.8'
        assert request.headers['Host']=='example.com' and request.extensions['sni_hostname']=='example.com'
        return httpx.Response(200,content=b'fixture')
    monkeypatch.setattr(network.httpx,'AsyncClient',lambda **kw:client(transport=httpx.MockTransport(response),**kw))
    body,meta=asyncio.run(network.fetch('https://example.com/a.pdf'))
    assert body==b'fixture' and meta['url']=='https://example.com/a.pdf' and len(seen)==1


def test_model_budget_is_separate_without_resetting_existing_ledger():
    day="2026-11-14"
    old=llm.admission_key("groq","openai/gpt-oss-120b",day)
    new=llm.admission_key("groq","openai/gpt-oss-20b",day)
    store.put(old,{"reserved_tokens":178548,"requests":26})
    store.put(new,{"reserved_tokens":1000,"requests":1})
    assert old=="admission-"+day and new!=old
    assert store.cached(old)["reserved_tokens"]==178548
    assert store.cached(new)["reserved_tokens"]==1000
