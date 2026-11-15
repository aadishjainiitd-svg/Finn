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


def report(version,year,revenue,prior_revenue,pat=(200,100),title='CONSOLIDATED STATEMENT OF PROFIT AND LOSS',month='December 31'):
    doc={'symbol':'TEST','version':version,'kind':'annual'}
    text=(f'{title} For the year ended {month}, {year} (INR in Crores) {month}, {year} {month}, {year-1} Income '
          f'Revenue from operations 24 {revenue:,.2f} {prior_revenue:,.2f} Profit for the year {pat[0]:.2f} {pat[1]:.2f} ')
    return extract(doc,[{'id':version+'-p1-c0','page':1,'text':text}])


def test_trajectory_prefers_newest_report_marks_restatement_and_keeps_gaps():
    from backend.statements import trajectory
    facts=report('v25',2025,1200,1000)+report('v24',2024,990,900)
    path=trajectory(facts)
    assert [y['fiscal_year'] for y in path['years']]==['2021','2022','2023','2024','2025']
    assert path['gaps']==['2021','2022'] and not path['complete']
    y2024=next(y for y in path['years'] if y['fiscal_year']=='2024')
    assert y2024['values']['revenue']['value']=='1000.00' and y2024['values']['revenue']['restatement'].endswith('v25')
    assert y2024['restated']['revenue']['older']['value']=='990.00'
    # Growth for 2024 comes from the 2024 report's own pair, never across reports.
    assert y2024['growth']['revenue']['percent']=='10.0'
    assert y2024['growth']['revenue']['prior']['restatement'].endswith('v24')
    assert next(y for y in path['years'] if y['fiscal_year']=='2023')['growth']=={}


def test_trajectory_breaks_series_at_year_end_change():
    from backend.statements import trajectory
    facts=report('v25',2025,1200,1000,month='March 31')+report('v23',2023,800,700)
    path=trajectory(facts)
    assert path['notes'] and all(y['period_end'] is None or y['period_end'].endswith('03-31') for y in path['years'])


def test_cash_allocation_reconciles_to_operating_cash_and_reported_closing_cash():
    from decimal import Decimal
    from backend.statements import trajectory
    text=('CONSOLIDATED STATEMENT OF CASH FLOWS For the year ended December 31, 2025 (INR in Crores) December 31, 2025 December 31, 2024 '
          'Purchase of property, plant and equipment (30.00) (20.00) Net cash flow used in investing activities (50.00) (25.00) '
          'Dividend paid (40.00) (30.00) Net cash flow from / (used in) financing activities (45.00) (35.00) '
          'Net cash flow from operating activities 100.00 90.00 Effects of exchange (loss) / gain on cash and cash equivalents 1.00 0.00 '
          'Cash and cash equivalents (opening balance) 50.00 20.00 Cash and cash equivalents (closing balance) 56.00 50.00 ')
    facts=report('v25',2025,1200,1000)+extract({'symbol':'TEST','version':'v25','kind':'annual'},[{'id':'v25-p2-c0','page':2,'text':text}])
    allocation=trajectory(facts)['allocation']
    row=next(r for r in allocation['years'] if r['fiscal_year']=='2025')
    uses={u['label']:Decimal(u['value']) for u in row['uses']}
    assert uses['Capex']==30 and uses['Dividends']==40 and uses['Acquisitions']==0
    assert not next(u for u in row['uses'] if u['label']=='Acquisitions')['reported']
    assert sum(uses.values())+Decimal(row['net_change'])==Decimal(row['cfo'])
    assert row['check']['reconciled'] and allocation['reconciled_years']==2


def test_unlabelled_scope_glyph_declaration_and_whole_number_columns():
    doc={'symbol':'TEST','version':'w1','kind':'annual'}
    page=('Statement of Profit and Loss (H crore) Note Year ended March 31, 2026 Year ended March 31, 2025 '
          'Revenue from operations 12 2,67,021 2,55,324 Other income 13 4,402 3,962 Profit for the year 49,454 48,797 ')
    declaration='These standalone financial statements have been prepared in Indian Rupee (H) which is the functional currency.'
    rows=[{'id':'w1-p1-c0','page':1,'text':page},{'id':'w1-p2-c0','page':2,'text':declaration}]
    parsed={f['metric']+f['year']:f for f in extract(doc,rows)}
    assert parsed['revenue2026']['crore']=='267021' and parsed['revenue2025']['crore']=='255324'
    assert parsed['other_income2026']['crore']=='4402'
    assert parsed['revenue2026']['scope']=='standalone' and 'Only set' in parsed['revenue2026']['scope_basis']
    assert not extract(doc,[rows[0],{**rows[1],'text':declaration.replace('(H)','(J)')}])
    running=[{**rows[0],'text':'Consolidated Financial Statements '+page},rows[1]]
    assert not extract(doc,running)


def test_working_capital_days_use_closing_balance_and_same_report_revenue():
    from decimal import Decimal
    from backend.statements import trajectory
    facts=report('v25',2025,1200,1000)
    balance=('CONSOLIDATED BALANCE SHEET as at December 31, 2025 (INR in Crores) December 31, 2025 December 31, 2024 '
             'Inventories 120.00 100.00 Trade receivables 240.00 200.00 Total assets 1000.00 900.00 ')
    facts+=extract({'symbol':'TEST','version':'v25','kind':'annual'},[{'id':'v25-p3-c0','page':3,'text':balance}])
    y=next(y for y in trajectory(facts)['years'] if y['fiscal_year']=='2025')
    assert Decimal(y['derived']['receivable_days']['value'])==Decimal(240)/Decimal(1200)*365
    assert Decimal(y['derived']['inventory_days']['value'])==Decimal(120)/Decimal(1200)*365


def test_trajectory_scope_follows_latest_window_not_stale_older_years():
    from backend.statements import trajectory
    old=report('o23',2023,800,700)+report('o22',2022,700,600)
    new=report('n26',2026,1200,1000,title='STANDALONE STATEMENT OF PROFIT AND LOSS')
    path=trajectory(old+new)
    assert path['scope']=='standalone' and path['years'][-1]['fiscal_year']=='2026' and not path['years'][-1]['gap']
