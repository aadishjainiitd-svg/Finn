import asyncio
import pytest
from backend import research_pack,repository,narrative,research


@pytest.mark.parametrize('same_version',[True,False])
def test_quota_failure_keeps_only_same_version_selection_and_retains_history_request(monkeypatch,same_version):
    evidence={'id':'old-p1','version':'old','kind':'annual','symbol':'TEST','text':'Demand remained strong.'}
    previous={'annual_reports_requested':5,'checked_at':'2026-11-14T10:00:00Z',
        'narrative':{'status':'partial','coverage':'Selected passages','observations':[{'aspect':'favourable','nature':'interpretation',
            'sources':[{'quote':'Demand remained strong.','evidence':evidence}]}],'missing':['business','adverse','accounting']}}
    repository.save('_public','research_packs',research_pack.key('TEST'),previous)
    observed=[]
    async def identity(symbol):return {'symbol':symbol,'name':'Test Limited'}
    async def discover(company,annual_count,transcript_count):
        observed.append((annual_count,transcript_count));return [{'title':'Report','discovery_period':'2025'}]
    async def ingest(*args):return {'version':'old' if same_version else 'replacement','hash':'bytes','kind':'annual','symbol':'TEST','period':'2025'}
    async def unavailable(*args):return {'status':'unavailable','error':'Free daily allowance exhausted.','observations':[]}
    monkeypatch.setattr(research,'worker',asyncio.Lock())
    monkeypatch.setattr(research_pack,'identity',identity);monkeypatch.setattr(research_pack,'discover',discover)
    monkeypatch.setattr(research_pack,'ingest',ingest);monkeypatch.setattr(research_pack,'retrieve',lambda *args:[])
    monkeypatch.setattr(narrative,'build',unavailable)
    result=asyncio.run(research_pack.build({},'TEST'))
    assert observed==[(5,4)] and result['annual_reports_requested']==5
    assert bool(result['narrative'].get('retained_selection'))==same_version
    if same_version:
        assert result['narrative']['selection_checked_at']==previous['checked_at']
        assert result['narrative']['observations'][0]['sources'][0]['evidence']['version']=='old'
    else:assert not result['narrative']['observations']
