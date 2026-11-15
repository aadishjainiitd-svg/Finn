import asyncio
import pytest
from backend import narrative,repository
from backend.llm import resolve_research,source_spans


def evidence(kind='annual'):
    return {'id':'v1-p1','version':'v1','symbol':'TEST','kind':kind,'period':'2025','page':1,'management_speakers':['Anita Rao'],'speaker_before':'Anita Rao',
            'text':'The company manufactures electrical products. Demand remained strong across the product portfolio. Commodity prices remain volatile and could affect margins.'}


def test_narrative_retains_exact_sources_and_rejects_business_from_call():
    e=evidence();spans=source_spans([e]);ids=list(spans)
    data={'observations':[{'text':'Not displayed','nature':'interpretation','aspect':aspect,'citations':[{'source_id':sid}]} for aspect,sid in zip(['business','favourable','adverse'],ids)]}
    result=resolve_research(data,[e])
    assert [o['aspect'] for o in result]==['business','favourable','adverse']
    assert result[0]['nature']=='reported' and result[1]['nature']=='interpretation'
    assert all(s['quote'] in e['text'] for o in result for s in o['sources'])
    assert not any(o['aspect']=='business' for o in resolve_research(data,[evidence('transcript')]))


def test_narrative_cache_and_quota_failure_preserve_missing_aspects(monkeypatch):
    docs=[{'version':'v1','kind':'annual'}];calls=[]
    monkeypatch.setattr(narrative,'retrieve',lambda *args:[evidence()])
    async def model(*args,**kwargs):
        calls.append(1)
        return {'observations':[],'provider':'groq'}
    monkeypatch.setattr(narrative,'synthesize',model)
    result=asyncio.run(narrative.build(docs,{}))
    assert result['status']=='partial' and set(result['missing'])==set(narrative.ASPECTS)
    assert asyncio.run(narrative.build(docs,{}))['cache_hit'] and len(calls)==1
    from backend.network import SourceError
    async def exhausted(*args,**kwargs):raise SourceError('daily_quota','Free allowance exhausted')
    monkeypatch.setattr(narrative,'synthesize',exhausted)
    failed=asyncio.run(narrative.build([{'version':'v2','kind':'annual'}],{}))
    assert failed['status']=='unavailable' and failed['error']=='Free allowance exhausted'



def test_financial_highlight_is_not_business_and_standard_policy_is_not_a_risk():
    from backend.llm import relevant_aspect
    assert not relevant_aspect('business','We closed with record orders and revenues of INR 100 crore.')
    assert not relevant_aspect('accounting','The Company uses percentage-of-completion accounting for fixed-price contracts.')
    assert relevant_aspect('accounting','Estimating costs to completion involves significant management judgement.')
    assert relevant_aspect('business','The company manufactures electrical products.')


def test_business_selection_ignores_question_and_shareholder_service_before_issuer_description():
    from backend import store
    doc={'version':'abb-v','hash':'abb-h','symbol':'ABB','name':'ABB India Limited','kind':'annual'}
    # Recorded ABB report wording; page numbers/citation identity are preserved
    # independently of whether a preceding passage happens to match a keyword.
    actual='ABB INDIA IN 2025 75 YEARS OF MANUFACTURING & INNOVATION IN INDIA Established in 1949, two years after India’s independence, ABB India has spent 75 years enabling electrification, automation and digitalization across utilities, industries, infrastructure and transportation.'
    with store.db() as c:
        for page,text in [(1,'What products does the company manufacture?'),(2,'The company provides information services to shareholders.'),(25,actual)]:
            c.execute('INSERT INTO chunks VALUES (?,?,?,?)',(f'abb-v-p{page}-c0','abb-v',page,text))
    selected=narrative.business_source([doc])
    assert selected['sources'][0]['quote']==actual
    assert selected['sources'][0]['evidence']['page']==25
