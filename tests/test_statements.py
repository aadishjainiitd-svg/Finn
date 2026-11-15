from backend.statements import extract,analyse

DOC={'symbol':'TEST','version':'v1','kind':'annual'}
TITLE='CONSOLIDATED STATEMENT OF PROFIT AND LOSS For the year ended December 31, 2025 '
HEADER='(H in Crores) Notes December 31, 2025 December 31, 2024 Income '
ROWS='Revenue from operations 24 1,200.00 1,000.00 Profit for the year 200.00 100.00 '
DECL='The consolidated financial statements are presented in INR in crores, rounded off to two decimal places.'

def facts(text=TITLE+HEADER+ROWS,decl=DECL):
    return extract(DOC,[{'id':'v1-p1-c0','page':1,'text':text},{'id':'v1-p2-c0','page':2,'text':decl}])

def test_explicit_scope_dates_currency_note_and_row_support_annual_comparison():
    parsed=facts();report=analyse(parsed)
    revenue=next(f for f in parsed if f['metric']=='revenue' and f['year']=='2025')
    assert revenue['period_start']=='2025-01-01' and revenue['period_end']=='2025-12-31'
    assert revenue['crore']=='1200.00' and revenue['scope']=='consolidated'
    assert revenue['headers'][-1]['evidence']['page']==2
    assert all(h['quote'] in h['evidence']['text'] for h in revenue['headers'])
    growth=next(g for g in report['years'][0]['growth'] if g['metric']=='revenue')
    assert growth['percent']=='20.0'

def test_bad_currency_extra_columns_and_incompatible_dates_fail_closed():
    assert not facts(decl=DECL.replace('consolidated','standalone'))
    assert not facts(TITLE+HEADER.replace('(H in Crores)','(USD in Crores)')+ROWS)
    assert not facts(TITLE+HEADER+ROWS.replace('1,000.00','1,000.00 900.00')) or not any(f['metric']=='revenue' for f in facts(TITLE+HEADER+ROWS.replace('1,000.00','1,000.00 900.00')))
    assert not facts((TITLE+HEADER+ROWS).replace('December 31, 2024','March 31, 2024'))
    assert not facts((TITLE+HEADER+ROWS).replace('December 31, 2024','December 32, 2024'))

def test_cash_reconciliation_never_turns_missing_acquisition_row_into_zero():
    text='CONSOLIDATED STATEMENT OF CASH FLOWS For the year ended December 31, 2025 (INR in Crores) December 31, 2025 December 31, 2024 '
    text+='Net cash flow from operating activities 100.00 90.00 Net cash flow used in investing activities (20.00) (10.00) Net cash flow from / (used in) financing activities (30.00) (25.00) Effects of exchange (loss) / gain on cash and cash equivalents 2.00 1.00 Cash and cash equivalents (opening balance) 50.00 40.00 Cash and cash equivalents (closing balance) 102.00 96.00 '
    parsed=facts(text);result=analyse(parsed)['years'][0]
    assert result['cash_bridge']['reconciled']
    assert next(b for b in result['cash_buckets'] if b['label']=='Acquisitions')['facts']==[]
    mismatch=analyse(facts(text.replace('102.00','110.00')))['years'][0]
    assert not mismatch['cash_bridge']['reconciled'] and mismatch['cash_bridge']['residual']=='8.00'


def test_financial_statement_schema_never_calculates_ebitda_proxy():
    text=TITLE+HEADER+ROWS+' Net interest income 80.00 70.00 Operating profit before provisions 40.00 35.00 Profit from continuing operations before tax 30.00 20.00 Finance costs 10.00 9.00 Depreciation and amortisation expense 3.00 2.00 Other income 4.00 3.00'
    result=analyse(facts(text))
    assert result['industry_schema']=='financial'
    assert all(y['earnings_proxy'] is None for y in result['years'])



def test_balance_ratios_require_both_borrowing_rows_and_comparable_opening_capital():
    income=TITLE+HEADER+ROWS+' Profit before tax 250.00 200.00 Finance costs 10.00 8.00 '
    balance='CONSOLIDATED BALANCE SHEET as at December 31, 2025 (INR in Crores) December 31, 2025 December 31, 2024 Total assets 1000.00 900.00 Total equity 600.00 550.00 Non-current liabilities Borrowings 100.00 90.00 Total non-current liabilities 100.00 90.00 Current liabilities Borrowings 50.00 40.00 Total current liabilities 300.00 260.00 '
    source=[{'id':'v1-p1-c0','page':1,'text':income},{'id':'v1-p2-c0','page':2,'text':DECL},{'id':'v1-p3-c0','page':3,'text':balance}]
    parsed=extract(DOC,source);report=analyse(parsed);ratios=report['years'][0]['ratios']
    assert ratios['debt_equity']['value']=='0.25'
    from decimal import Decimal
    assert Decimal(ratios['roce']['value'])==Decimal(260)/Decimal(670)*100
    assert len(ratios['roce']['operands'])==6
    for f in ratios['roce']['operands']:assert f['quote'] in f['evidence']['text']
    missing=analyse([f for f in parsed if f['metric']!='current_borrowings'])['years'][0]
    assert 'debt_equity' not in missing['ratios']
    wrong=[{**f,'period_end':'2024-03-31'} if f['year']=='2024' and f['metric']=='total_assets' else f for f in parsed]
    assert 'roce' not in analyse(wrong)['years'][0]['ratios']
