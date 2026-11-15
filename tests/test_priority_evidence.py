"""Recorded primary-source regression plus adversarial synthetic boundaries."""
import json
from pathlib import Path
from backend.brief import priority, classify_with_evidence


def test_recorded_infy_award_is_not_capital_allocation():
    fixture = json.loads((Path(__file__).parent / 'fixtures/infy-prize-filing.json').read_text(encoding='utf-8'))
    text = ' '.join(c['text'] for c in fixture['chunks'])
    result = priority('Press Release', text)
    assert result['tier'] == 1
    assert 'Capital allocation' not in result['reason']
    state,evidence=classify_with_evidence('Press Release',fixture['chunks'],{'hash':'recorded'})
    assert state['tier']==1
    assert evidence[0]['page']==1


def test_genuine_acquisition_after_disclaimer_is_not_suppressed():
    text = ('Forward-looking statements: risks include acquisitions and capital expenditure. '
            'Transaction update: The board approved the acquisition of ABC Limited for INR 100 crore.')
    result = priority('Acquisition', text)
    assert result['tier'] == 0
    assert 'board approved' in result['trigger_quote']
    assert 'risks include' not in result['trigger_quote']


def test_title_alone_cannot_establish_an_event_fact():
    result = priority('Acquisition', 'This is a routine contact address update for shareholders.')
    assert result['tier'] == 1


def test_default_negation_is_not_a_credit_event():
    result = priority('Disclosure', 'The company has not defaulted on any payment of debt.')
    assert result['tier'] == 1


def test_priority_citation_is_the_trigger_not_an_unrelated_keyword():
    rows=[{'id':'p1','page':1,'text':'For shareholders: investment information is available online.'},
          {'id':'p2','page':2,'text':'The board approved the acquisition of ABC Limited for INR 100 crore.'}]
    state,evidence=classify_with_evidence('Update',rows,{'hash':'recorded'})
    assert state['tier']==0
    assert evidence[0]['id']=='p2'
    assert evidence[0]['quote']==state['trigger_quote']
    assert evidence[0]['quote'] in evidence[0]['text']


def test_recorded_accounting_definition_does_not_establish_an_acquisition():
    case=json.loads((Path(__file__).parent/'fixtures/priority-source-boundaries.json').read_text())[0]
    state,evidence=classify_with_evidence(case['meta']['title'],case['chunks'],case['meta'])
    assert 'Capital allocation' not in state['reason']
    assert state['tier']==0 and 'Financial results' in state['reason'] and evidence[0]['page']==2


def test_recorded_newspaper_cannot_cite_another_issuer_or_hide_unverified_layout():
    case=json.loads((Path(__file__).parent/'fixtures/priority-source-boundaries.json').read_text())[1]
    state,evidence=classify_with_evidence(case['meta']['title'],case['chunks'],case['meta'])
    assert state['assessment']=='pending' and state['tier']!=3
    assert evidence[0]['page']==1
    assert 'Lloyds' not in evidence[0].get('quote','') and 'lloyds.in' not in evidence[0].get('quote','')
    from backend.brief import event_extras
    from backend.documents import retrieve
    meta={**case['meta'],'kind':'filing'}
    assert retrieve([meta],'What financial results were reported?')==[]
    enriched=event_extras({'id':'e','symbol':'CERA','kind':'filing','title':meta['title'],'reason':state['reason']},case['chunks'],meta)
    assert not enriched.get('management_profile')


def test_actual_completed_acquisition_still_surfaces_but_eligibility_is_not_appointment():
    assert priority('Update','The Company has acquired ABC Limited for INR 100 crore.')['tier']==0
    assert priority('Profile','She meets the criteria for appointment as an independent director.')['tier']==1


def test_missing_pdf_clarification_is_prominent_without_confirming_the_news(monkeypatch):
    from backend import brief
    monkeypatch.setattr(brief,'valid_assessment',lambda *args:None)
    monkeypatch.setattr(brief.store,'cached',lambda *args:None)
    row={'symbol':'SUNPHARMA','desc':'News Verification','seq_id':'106839459','attchmntFile':'-',
        'attchmntText':'The Exchange has sought clarification. The response from the Company is awaited.'}
    event=brief.make_filing(row,'2026-11-15T08:00:00Z')
    assert event['tier']==0 and event['assessment']=='pending' and not event['url']
    assert event['exchange_notice']['text']==row['attchmntText']
    assert not event['evidence'] and 'incomplete' in event['reason']
    assert 'PDF attachment' in event['assessment_error']



def test_recorded_call_notices_scrutinizers_parent_results_and_arbitration():
    cases=json.loads((Path(__file__).parent/'fixtures/priority-live-corrections.json').read_text(encoding='utf-8'))
    expected={
        # The scrutinizer's appointment is not a management change, but the
        # full report also contains the Anup Bagchi director/CEO resolution.
        'filing-HDFCBANK-106851783':(0,'Board or'),
        'filing-TITAN-106848291':(0,'Auditor appointment'),
        'filing-CDSL-106847538':(1,'Source read'),
        'filing-MARUTI-106854012':(1,'Referenced results'),
        'filing-TATAPOWER-106852712':(0,'Credit, legal'),
        'filing-SUNPHARMA-106840669':(0,'Exchange clarification'),
        'filing-TATAPOWER-106855738':(1,'Source read'),
    }
    for case in cases:
        state,evidence=classify_with_evidence(case['title'],case['chunks'],case['meta'])
        tier,reason=expected[case['id']]
        assert state['tier']==tier and state['reason'].startswith(reason),(case['id'],state)
        if state.get('trigger_quote'):assert state['trigger_quote'] in evidence[0]['text']
        if case['id'].startswith('filing-SUNPHARMA'):assert 'does not concern any new event' in state['trigger_quote']
        if case['id'].startswith('filing-MARUTI'):
            from backend.results import extract
            assert state['assessment']=='pending' and not extract(case['meta'],case['chunks'])['tables']


def test_recorded_approvals_funding_and_historical_slides():
    cases=json.loads((Path(__file__).parent/'fixtures/priority-capital-approval.json').read_text(encoding='utf-8'))
    expected={
        'filing-HDFCBANK-106857049':'Board or', 'filing-TATAPOWER-106855429':'Capital allocation',
        'filing-TATAPOWER-106855404':'Financial results','filing-BAJFINANCE-106855359':'Capital raising',
        'filing-BAJFINANCE-106854062':'Capital raising','filing-BAJFINANCE-106854034':'Capital raising',
        'filing-LT-106853097':'New order','filing-ASIANPAINT-106851770':'Board or',
        'filing-TITAN-106848400':'Board or','filing-TITAN-106847693':'Accounting remeasurement',
        'filing-PERSISTENT-106844222':'Capital raising','filing-RELIANCE-106859406':'Investor-meeting logistics',
    }
    for case in cases:
        state,refs=classify_with_evidence(case['title'],case['chunks'],case['meta'])
        assert state['tier']==(3 if case['id']=='filing-RELIANCE-106859406' else 0),(case['id'],state)
        assert state['reason'].startswith(expected[case['id']]),(case['id'],state)
        assert refs and state['trigger_quote'] in refs[0]['text']
    routine=cases[-1]
    # Appending an actual adverse filing paragraph must beat the routine floor.
    adverse={'id':'p2','page':2,'text':'The company has defaulted on its loan repayment.'}
    state,_=classify_with_evidence(routine['title'],[*routine['chunks'],adverse],routine['meta'])
    assert state['tier']==0 and state['reason'].startswith('Credit,')


def test_funding_resolution_stays_prominent_without_inventing_an_issuance():
    case=json.loads((Path(__file__).parent/'fixtures/priority-funding-resolution.json').read_text(encoding='utf-8'))
    state,refs=classify_with_evidence(case['title'],case['chunks'],case['meta'])
    assert state['tier']==0 and state['reason'].startswith('Capital raising resolution')
    assert 'Issuance of Warrants on a preferential basis' in state['trigger_quote']
    assert refs[0]['page']==3 and state['trigger_quote'] in refs[0]['text']
    assert priority('Governance policy','A special resolution may be required for issuance of warrants on a preferential basis.')['tier']==1


def test_disclosed_increase_in_capex_plan_is_not_downgraded_as_generic_transcript():
    case=json.loads((Path(__file__).parent/'fixtures/priority-capex-plan.json').read_text(encoding='utf-8'))
    state,refs=classify_with_evidence(case['title'],case['chunks'],case['meta'])
    assert state['tier']==0 and state['reason'].startswith('Capital spending plan')
    assert 'CAPEX plans to INR 500 crores' in state['trigger_quote']
    assert refs[0]['page']==10 and state['trigger_quote'] in refs[0]['text']
    assert priority('Question','Are we increasing our CAPEX plans to INR 500 crores?')['tier']==1
