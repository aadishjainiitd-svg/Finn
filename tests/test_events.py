from backend.events import period_identity,thread,read_across,upcoming,enrich
from datetime import datetime,timezone


def test_quarter_and_conflicting_periods_are_not_guessed():
    assert period_identity('Q2 FY27')=='2026-09-30'
    assert period_identity('quarter ended 30 September 2026')=='2026-09-30'
    assert period_identity('third quarter ended September 30, 2026')=='2026-09-30'
    assert period_identity('Q2 FY27 compared with Q2 FY26') is None


def test_threads_keep_different_periods_and_unidentified_notices_separate():
    e={'id':'results','symbol':'TCS','tier':0,'score':80,'revision':'v1','published_at':'2026-11-01',
       'event_key':'TCS-results-2026-09-30','event_period':'2026-09-30','title':'Results'}
    events=[e,{**e,'id':'call','revision':'v2'}, {**e,'id':'prior','event_key':'TCS-results-2026-06-30'}]
    result=thread(events)
    assert len(result)==2 and len(result[0]['children'])==2
    assert {c['id'] for c in result[0]['children']}=={'results','call'}
    updated=thread([*events,{**e,'id':'transcript','revision':'v3'}])
    assert updated[0]['revision']!=result[0]['revision']


def test_future_dates_require_scheduling_context_and_source():
    meta={'hash':'source','symbol':'TCS'}
    event={'id':'e','symbol':'TCS','kind':'filing','title':'Meeting','tier':1,'reason':'Read source'}
    rows=[{'id':'p1','page':1,'text':'The call will be held on 20 November 2026. Revenue for the quarter ended 30 September 2026 was reported. The target year ends 31 March 2027.'}]
    enriched=enrich(event,rows,meta)
    dates=upcoming([enriched],datetime(2026,11,15,tzinfo=timezone.utc))
    assert len(dates)==1 and dates[0]['date']=='2026-11-20'
    assert dates[0]['evidence']['id']=='p1'


def test_read_across_is_only_an_explicit_connection_and_hypothesis():
    e={'id':'e','symbol':'TCS','tier':0,'evidence':[{'id':'source'}]}
    holdings=[{'symbol':'TCS','sector':'IT','inputs':[]},{'symbol':'INFY','sector':'IT','inputs':[]},{'symbol':'HDFCBANK','sector':'','inputs':[]}]
    result=read_across([e],holdings)
    assert len(result)==1 and result[0]['symbol']=='INFY' and 'hypothesis' in result[0]['label']


def test_routine_addition_does_not_reopen_thread_but_material_revision_does():
    e={'id':'results','symbol':'TCS','tier':0,'score':80,'revision':'v1','published_at':'2026-11-01',
       'assessment':'assessed','event_key':'TCS-results-2026-09-30','event_period':'2026-09-30','title':'Results'}
    original=thread([e])[0]
    routine={**e,'id':'newspaper','tier':3,'assessment':'routine','revision':'routine-v1'}
    enlarged=thread([e,routine])[0]
    assert original['id']==enlarged['id'] and original['revision']==enlarged['revision']
    assert thread([{**e,'revision':'restated-v2'},routine])[0]['revision']!=original['revision']


def test_calendar_issuer_does_not_inherit_indian_fiscal_quarters():
    from backend.documents import validate_identity
    company={'symbol':'ABB','name':'ABB India Limited'}
    doc={'kind':'transcript','discovery_period':'Aug 2026'}
    opening='ABB India Limited Q2CY2026 Earnings Conference Call transcript. Quarter ended June 30, 2026.'
    assert validate_identity(company,doc,opening)=='Q2CY2026'
    assert validate_identity(company,{'kind':'annual','discovery_period':'Annual Report 2025'},
        'ABB India Limited annual report for the year ended December 31, 2025.')=='year ended december 31, 2025'


def test_thread_keeps_results_when_another_child_leads():
    base={'symbol':'TCS','event_key':'TCS-results-2026-09-30','event_period':'2026-09-30','revision':'1','published_at':'2026-11-01','assessment':'assessed'}
    table={'tables':[{'scope':'consolidated','items':[]}],'gaps':[]}
    result=thread([{**base,'id':'notice','tier':0,'score':100},{**base,'id':'results','tier':1,'score':40,'results':table}])[0]
    assert result['lead_filing_id']=='notice' and result['results']==table


def test_explicit_rescheduling_preserves_old_new_dates_and_disclosed_timezone():
    from backend.events import schedule_dates
    event={'id':'revision','symbol':'TCS'};meta={'symbol':'TCS'}
    text='The earnings call is rescheduled from 20 November 2026 to 23 November 2026 at 4:30 PM IST.'
    rows=[{'id':'p1','page':1,'text':text}]
    values=schedule_dates(event,rows,meta)
    assert [(d['date'],d['status']) for d in values]==[('2026-11-20','cancelled'),('2026-11-23','rescheduled')]
    assert values[0]['replacement_date']=='2026-11-23' and values[1]['time']=='4:30 PM IST'
    assert values[0]['quote']==text
    rows[0]['text']='The call scheduled on 20 November 2026 will discuss results dated 30 September 2026.'
    assert schedule_dates(event,rows,meta)==[]


def test_month_first_dates_and_mixed_format_revision_remain_source_exact():
    from backend.events import schedule_dates
    event={'id':'notice','symbol':'TCS'};meta={'symbol':'TCS'}
    text='The earnings call will be held on November 20, 2026 at 4:30 PM IST.'
    rows=[{'id':'p1','page':1,'text':text}]
    dates=schedule_dates(event,rows,meta)
    assert len(dates)==1 and dates[0]['date']=='2026-11-20'
    assert dates[0]['time']=='4:30 PM IST' and dates[0]['quote']==text
    rows[0]['text']='The call is rescheduled from November 20, 2026 to 23 November 2026.'
    dates=schedule_dates(event,rows,meta)
    assert [(d['date'],d['status']) for d in dates]==[('2026-11-20','cancelled'),('2026-11-23','rescheduled')]
    rows[0]['text']='The call scheduled on November 20, 2026 will discuss results dated September 30, 2026.'
    assert schedule_dates(event,rows,meta)==[]
    rows[0]['text']='The meeting will be held on February 30, 2027.'
    assert schedule_dates(event,rows,meta)==[]
    rows[0]['text']='The Analyst Call to discuss the results for Q2FY27 will be held on Wednesday, November 11, 2026, from 6:00 p.m. (IST) onwards. The mode is Over Call.'
    dates=schedule_dates(event,rows,meta)
    assert dates[0]['date']=='2026-11-11' and dates[0]['time']=='6:00 PM IST'
    assert dates[0]['quote'].endswith('(IST) onwards.')
