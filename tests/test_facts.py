import pytest
from backend.facts import summary_facts,growth,promise_verdict,cash_bridge


def summary(text):return summary_facts({'symbol':'TEST','version':'v1'},[{'id':'v1-p27','page':27,'text':text}])


def test_primary_summary_keeps_unknown_scope_and_dash_is_not_zero():
    source='FIVE-YEAR SUMMARY (₹ in Crores) Description 2025 2024 2023 2022 2021 Revenue from operations 13,203 12,188 10,447 8,568 6,934 Borrowings – – Nil 4 (5) Note - Includes discontinued operations'
    facts=summary(source)
    revenue=[f for f in facts if f['metric']=='revenue']
    assert [f['crore'] for f in revenue]==['13203','12188','10447','8568','6934']
    assert all(f['scope']=='unspecified' and f['period_end'] is None for f in revenue)
    assert all(f['quote'] in source and f['header_quote'] in source for f in facts)
    assert [f['value'] for f in facts if f['metric']=='borrowings']==[None,None,'0','4','-5']
    with pytest.raises(ValueError):growth(revenue[0],revenue[1])


def test_ambiguous_columns_units_and_conflicting_values_fail_closed():
    header='FIVE-YEAR SUMMARY (₹ in Crores) Description 2025 2024 2023 2022 2021 '
    assert not summary(header+'Revenue from operations 1 2 3 4 5 6')
    assert not summary(header.replace('₹','USD')+'Revenue from operations 1 2 3 4 5')
    assert not summary(header.replace('2024','2025')+'Revenue from operations 1 2 3 4 5')
    assert not summary(header+'Revenue from operations 1 2 3 4 5. Revenue from operations 6 7 8 9 10.')


def test_promise_kept_count_requires_due_comparable_sources_and_honours_revisions():
    target={'symbol':'TEST','metric':'revenue','currency':'INR','scope':'consolidated','period_kind':'annual',
        'period_start':'2025-04-01','period_end':'2026-03-31','due':'2026-03-31',
        'unit':'crore','minimum':'100','maximum':'110','evidence_id':'target-p1','quote':'We target 100 to 110 crore.'}
    actual={**target,'unit':'lakh','value':'10500','evidence_id':'actual-p2','quote':'Revenue was 10500 lakh.'}
    assert promise_verdict(target,actual,'2026-11-15')=='met'
    assert promise_verdict(target,{**actual,'value':'9000'},'2026-11-15')=='missed'
    assert promise_verdict({**target,'status':'revised'},actual,'2026-11-15')=='revised'
    assert promise_verdict(target,{**actual,'period_kind':'quarter'},'2026-11-15')=='not_comparable'
    assert promise_verdict(target,None,'2026-02-01')=='not_due'


def test_cash_bridge_exposes_unexplained_residual_instead_of_forcing_balance():
    good=cash_bridge('100','20','10','15','-5','2','50','102')
    assert good['reconciled'] and good['residual']=='0'
    bad=cash_bridge('100','20','10','15','-5','2','50','110')
    assert not bad['reconciled'] and bad['residual']=='8'
