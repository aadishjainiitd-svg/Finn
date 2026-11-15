import asyncio
import pytest
from backend import conversations,repository,work,research,store
from backend.network import SourceError


def save(key,**values):
    repository.save('alice','history',key,{'symbol':'TCS','filing_id':None,'question':'What drove revenue growth?',
        'answer':{'claims':[{'text':'Unverified earlier claim must never be evidence'}]},**values})


def test_context_is_bounded_owner_scoped_and_excludes_prior_answer_assertions():
    for i in range(5):save(str(i),question=f'Question number {i}',parent_id=str(i-1) if i else None)
    context=conversations.prepare('alice','4','TCS')
    assert context=={'parent_id':'4','questions':['Question number 2','Question number 3','Question number 4']}
    prompt=conversations.prompt('And the preceding year?',context)
    assert 'CURRENT QUESTION: And the preceding year?' in prompt
    assert 'Unverified earlier claim' not in prompt and 'Question number 1' not in prompt
    with pytest.raises(SourceError):conversations.prepare('bob','4','TCS')
    with pytest.raises(SourceError):conversations.prepare('alice','4','INFY')


def test_event_and_changed_book_scopes_cannot_inherit_a_conversation():
    save('event',filing_id='results-q2')
    for filing in (None,'results-q1'):
        with pytest.raises(SourceError):conversations.prepare('alice','event','TCS',filing)
    assert conversations.prepare('alice','event','TCS','results-q2')
    save('book',symbol='BOOK',scope={'kind':'portfolio','book_version':3})
    with pytest.raises(SourceError):conversations.prepare('alice','book','BOOK',book_version=4)
    assert conversations.prepare('alice','book','BOOK',book_version=3)


def test_worker_retains_parent_link_and_result_identity(monkeypatch):
    context={'parent_id':'prior','questions':['What drove revenue growth?']}
    observed=[]
    async def run(progress,symbol,question,filing,owner,conversation=None):
        observed.append((symbol,question,filing,owner,conversation))
        progress.update(status='complete',result={'question':question,'claims':[]})
    monkeypatch.setattr(research,'run',run)
    job=work.enqueue('alice','research',{'symbol':'TCS','question':'And the prior year?',
        'filing_id':'result','conversation':context})
    leased=work.claim();assert leased['id']==job['id']
    asyncio.run(work.run_one(leased))
    saved=repository.get('alice','history',job['id'])
    assert observed==[('TCS','And the prior year?','result','alice',context)]
    assert saved['parent_id']=='prior' and saved['answer']['history_id']==job['id']
    assert saved['answer']['filing_id']=='result'
    assert repository.get('bob','history',job['id']) is None


def test_followup_uses_fresh_sources_and_never_reuses_standalone_answer_cache(monkeypatch):
    seen=[]
    async def identity(symbol):return {'symbol':symbol,'name':'Test company'}
    async def discover(company):return [{'kind':'annual','title':'Annual report'}]
    async def ingest(company,source,job):return {**company,**source,'version':'v1'}
    async def synthesize(question,evidence,job):
        seen.append(question)
        return {'status':'partial','claims':[],'evidence':evidence,'limitation':'Fixture','provider':'deterministic'}
    monkeypatch.setattr(research,'identity',identity);monkeypatch.setattr(research,'discover',discover)
    monkeypatch.setattr(research,'ingest',ingest);monkeypatch.setattr(research,'synthesize',synthesize)
    monkeypatch.setattr(research,'retrieve',lambda docs,q:[{'id':'v1-p1','text':'Fresh source','kind':'annual'}])
    monkeypatch.setattr(research,'recent_answer',lambda *args:pytest.fail('Follow-up must not use standalone cache'))
    context={'parent_id':'earlier','questions':['What drove revenue growth?']}
    job={};asyncio.run(research.run(job,'TCS','And the prior year?',owner='alice',conversation=context))
    assert job['status']=='complete' and job['result']['question']=='And the prior year?'
    assert job['result']['conversation']==context and len(seen)==1
    assert 'Earlier questions' in seen[0] and 'Fresh source' not in seen[0]
    assert repository.get('alice','answers',research.question_key('TCS','And the prior year?',owner='alice')) is None


def test_challenge_requires_the_original_topic_not_generic_risk_governance():
    context={'questions':['What does management say about electrification demand and backlog?']}
    generic={'text':'Operational risks are reviewed by the committee.'}
    relevant={'text':'We are increasing capacity because we will be struggling to meet demand.'}
    merely_positive={'text':'Our demand and backlog continue to grow.'}
    selected=conversations.focus_evidence('What risks challenge that outlook?',context,[generic,relevant,merely_positive])
    assert len(selected)==1 and selected[0]['text']==relevant['text']
    assert conversations.focus_evidence('What risks challenge that outlook?',context,[generic])==[]
    assert conversations.focus_evidence('And the preceding year?',context,[generic])==[generic]
    from backend.llm import source_spans
    mixed={**selected[0],'text':relevant['text']+' '+generic['text']}
    assert [s['quote'] for s in source_spans([mixed]).values()]==[relevant['text']]


def test_one_explicit_qualification_needs_no_model_and_is_never_a_complete_verdict():
    e={'id':'v-p21-c0','kind':'annual','symbol':'ABB','focus_terms':['demand'],
        'text':'We will be struggling to meet demand.'}
    answer=conversations.exact_qualification('What challenges that outlook?',[e])
    assert answer['provider']=='deterministic' and answer['status']=='partial'
    assert answer['claims'][0]['citations']==[{'evidence_id':e['id'],'quote':e['text']}]
    assert 'not an exhaustive' in answer['limitation']
    assert conversations.exact_qualification('What challenges that outlook?',[{**e,'focus_terms':[]}]) is None
