from backend.report_insights import percent_target,percent_verdict

CALL={'id':'call-p1-c0','symbol':'TEST','period':'Q2 FY25','kind':'transcript'}


def fact(metric,end,crore,version='v25'):
    return {'symbol':'TEST','metric':metric,'period_end':end,'period_kind':'annual','scope':'consolidated','value':crore,'crore':crore,
            'restatement':'as_presented_in_'+version,'quote':f'{metric} {crore}','evidence':{'id':'r-'+metric}}


def test_band_period_from_call_label_and_not_due_before_year_end():
    t=percent_target('We have given a guidance of 16%-18% EBITDA for the year.',CALL)
    assert (t['metric'],t['minimum'],t['maximum'],t['period_end'],t['scope'])==('ebitda_margin','16','18','2025-03-31','company')
    assert "call's fiscal year" in t['period_basis']
    assert percent_verdict(t,[],'2024-11-15')[0]=='not_due'


def test_revenue_growth_scored_only_from_one_statement():
    t=percent_target('We expect revenue growth of 10% to 12% in FY25.',CALL)
    facts=[fact('revenue','2025-03-31','1110'),fact('revenue','2024-03-31','1000')]
    status,actual,_=percent_verdict(t,facts,'2025-06-01')
    assert status=='met' and actual['value']=='11.0'
    assert percent_verdict(t,[fact('revenue','2025-03-31','1200'),fact('revenue','2024-03-31','1000')],'2025-06-01')[0]=='missed'
    # Prior year only in an older report: not scored across versions.
    assert percent_verdict(t,[fact('revenue','2025-03-31','1110'),fact('revenue','2024-03-31','1000','v24')],'2025-06-01')[0]=='not_comparable'


def test_approximate_margin_is_indicative_never_kept():
    t=percent_target('We are targeting around 15% EBITDA margin next year.',CALL)
    assert t['approximate'] and (t['minimum'],t['maximum'])==('14.0','16.0') and t['period_end']=='2026-03-31'
    facts=[fact('revenue','2026-03-31','1000','v26'),fact('pbt','2026-03-31','120','v26'),fact('finance_cost','2026-03-31','10','v26'),
           fact('depreciation','2026-03-31','30','v26'),fact('other_income','2026-03-31','10','v26')]
    status,actual,reason=percent_verdict(t,facts,'2026-06-01')
    assert status=='indicative' and actual['value']=='15.0' and 'not counted' in reason


def test_questions_segments_and_two_ranges_are_not_scored():
    assert percent_target('Do you expect margins of 20-21% next year?',CALL) is None
    paint=percent_target('Sandeep: Paint, we have guided 9%-10%, and we will be positive EBITDA around 3%-4%.',CALL)
    assert paint['scope']=='segment: paint' and percent_verdict(paint,[],'2030-01-01')[0]=='not_comparable'
    volume=percent_target('Our guidance of double-digit volume growth and 12% volume growth stays.',CALL)
    assert percent_verdict(volume,[],'2030-01-01')[0]=='not_comparable'
