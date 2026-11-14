from datetime import datetime,timedelta,timezone
from decimal import Decimal
import pytest
from backend.brief import priority
from backend.numbers import daily_signal,comparable_growth,IST

def chart(count=22):
    start=datetime(2026,1,1,9,15,tzinfo=IST)
    return {'timestamp':[int((start+timedelta(days=i)).timestamp()) for i in range(count)],
        'indicators':{'quote':[{'close':[100]*(count-1)+[110],'volume':[100]*(count-1)+[200]}]},'meta':{'currency':'INR'}}

def test_exact_daily_arithmetic_excludes_current_volume_from_baseline():
    s=daily_signal(chart(),datetime(2026,2,1,tzinfo=timezone.utc))
    assert s['change_percent']==10 and s['volume_multiple']==2
    assert s['operands']['average_previous_20_volume']=='100'
    assert len(s['operands']['previous_20_volumes'])==20

def test_unfinished_bar_is_excluded_without_assuming_weekdays():
    s=daily_signal(chart(),datetime(2026,1,22,12,tzinfo=IST))
    assert s['session']=='2026-01-21' and s['change_percent']==0 and s['volume_multiple']==1

def test_missing_volume_does_not_hide_latest_price_move():
    c=chart();c['indicators']['quote'][0]['volume'][-1]=None
    s=daily_signal(c,datetime(2026,2,1,tzinfo=timezone.utc))
    assert s['change_percent']==10 and s['volume_multiple'] is None and s['session']=='2026-01-22'

def test_split_zero_and_insufficient_history():
    c=chart();c['events']={'splits':{str(c['timestamp'][-1]):{'date':c['timestamp'][-1]}}}
    s=daily_signal(c,datetime(2026,2,1,tzinfo=timezone.utc));assert s['change_percent'] is None and s['volume_multiple'] is None
    c=chart();c['indicators']['quote'][0]['volume']=[0]*22
    assert daily_signal(c,datetime(2026,2,1,tzinfo=timezone.utc))['volume_multiple'] is None
    assert daily_signal(chart(5),datetime(2026,2,1,tzinfo=timezone.utc))['volume_multiple'] is None

def test_units_scope_and_periods_are_checked_before_growth():
    base={'metric':'Revenue','currency':'INR','scope':'consolidated','period_kind':'year','evidence_id':'sha-p1-c0','quote':'A cited source operand','unit':'crore'}
    prior={**base,'value':'100','period_start':'2024-04-01','period_end':'2025-03-31'}
    current={**base,'value':'11000','unit':'lakh','period_start':'2025-04-01','period_end':'2026-03-31'}
    assert comparable_growth(current,prior)==Decimal('10')
    for field,value in [('scope','standalone'),('period_kind','quarter'),('currency','USD')]:
        with pytest.raises(ValueError):comparable_growth({**current,field:value},prior)
    with pytest.raises(ValueError):comparable_growth({**current,'period_start':'2025-10-01'},prior)
    with pytest.raises(ValueError):comparable_growth(current,{**prior,'value':0})

@pytest.mark.parametrize('title,text,tier',[
    ('Financial Results','The board approved financial results. Revenue was INR 100 crore.',0),
    ('Newspaper Publication','Please find enclosed the newspaper publication confirmation.',3),
    ('Newspaper Publication','Enclosed financial results. Total income was INR 100 crore.',0),
    ('Auditor change','The statutory auditor resigned after a qualified opinion.',0),
    ('Rating update','The agency downgraded the rating.',0),
    ('Change in Director(s)','The board approved re-appointment of the whole-time director.',0),
    ('General update','A generic announcement with no positively identified routine subtype.',1),
    ('Newspaper Publication',None,1),
    ('Auditor change',None,1),
])
def test_labelled_priority_set_never_hides_material_or_unread(title,text,tier):
    assert priority(title,text)['tier']==tier


def test_director_biography_is_not_a_credit_or_fraud_event():
    text='The board approved re-appointment of the whole-time director. He heads Fraud & Vigilance. The company is not in default.'
    assert 'management change' in priority('Change in Director(s)',text)['reason']

def test_issuer_subject_is_used_without_inventing_a_resignation():
    from backend.brief import source_headline
    text='Sub: Re-appointment of Mr. V. Srinivasa Rangan as Executive Director Ref: Regulation 30'
    assert source_headline('Change in Director(s)',text)=='Re-appointment of Mr. V. Srinivasa Rangan as Executive Director'
