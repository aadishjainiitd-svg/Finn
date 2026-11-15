from backend.results import extract

DOC={'symbol':'TEST','name':'Test Limited','version':'fixture-v1','kind':'filing','title':'Financial Results'}
HEADER='Statement of Consolidated Unaudited Results for the Quarter and Nine Months Ended September 30, 2026 INR in Crores Particulars Quarter ended September 30, 2026 Preceding quarter ended June 30, 2026 Corresponding quarter ended September 30, 2025 Year to date figures for the current period ended September 30, 2026 Year to date figures for the previous period ended September 30, 2025 Previous year ended December 31, 2025 Unaudited Unaudited Unaudited Unaudited Unaudited Audited Continuing operations '
BODY='Total revenue from operations 120.00 100.00 80.00 350.00 290.00 440.00 Other income 2.00 2.00 2.00 6.00 6.00 8.00 Finance costs 1.00 1.00 1.00 3.00 3.00 4.00 Depreciation and amortisation expense 3.00 3.00 3.00 9.00 9.00 12.00 Profit from continuing operations before tax (3 - 4) 20.00 10.00 8.00 50.00 40.00 60.00 Profit for the period 15.00 7.00 6.00 36.00 31.00 46.00'

def parse(text=HEADER+BODY):return extract(DOC,[{'id':'v1-p3-c0','page':3,'text':text}])

def test_quarter_comparison_excludes_ytd_and_keeps_row_and_header_evidence():
    result=parse();table=result['tables'][0]
    revenue=next(i for i in table['items'] if i['metric']=='revenue')
    assert revenue['values']==['120.00','100.00','80.00']
    assert revenue['qoq']=='20.0' and revenue['yoy']=='50.0'
    assert table['period_starts']==['2026-07-01','2026-04-01','2025-07-01']
    for source in [revenue,*table['headers']]:assert source['quote'] in source['evidence']['text']
    proxy=next(i for i in table['items'] if i['metric']=='ebitda_proxy')
    assert proxy['values']==['22.00','12.00','10.00'] and len(proxy['operands'])==4

def test_broken_currency_columns_dates_or_negative_base_cannot_create_growth():
    assert not parse((HEADER+BODY).replace('INR in Crores','T In Crores'))['tables']
    assert not parse((HEADER+BODY).replace('June 30, 2026','March 31, 2026'))['tables']
    bad=parse((HEADER+BODY).replace('100.00','1.00.00'))['tables'][0]
    assert not any(i['metric']=='revenue' for i in bad['items'])
    negative=parse((HEADER+BODY).replace('100.00','(100.00)'))['tables'][0]
    assert next(i for i in negative['items'] if i['metric']=='revenue')['qoq'] is None
    assert not extract({**DOC,'title':'Newspaper publication'},[{'id':'r','page':1,'text':HEADER+BODY}])['tables']

def test_financial_schema_never_uses_ebitda_and_reported_ebitda_takes_precedence():
    bank=parse(HEADER+BODY+' Net interest income 60.00 50.00 40.00 150.00 120.00 190.00 Operating profit before provisions 30.00 20.00 10.00 60.00 30.00 90.00')['tables'][0]
    assert bank['industry_schema']=='financial'
    assert [i['metric'] for i in bank['items']]==['nii','operating_profit','pbt_continuing','pat']
    reported=parse(HEADER+BODY+' Reported EBITDA 25.00 15.00 10.00 70.00 40.00 90.00')['tables'][0]
    assert any(i['metric']=='reported_ebitda' for i in reported['items'])
    assert not any(i['metric']=='ebitda_proxy' for i in reported['items'])


# Recorded TCS p.8 column ordering and selected rows, not an invented result.
SPLIT_HEADER='Year ended September 30, June 30, September 30, September 30, September 30, March 31, 2026 2026 2025 2026 2025 2026 '
SPLIT_BODY='Revenue from operations 73,188 72,275 65,799 1,45,463 1,29,236 2,67,021 PROFIT BEFORE TAX 18,638 17,944 16,068 36,582 33,047 65,487 Finance costs 252 273 229 525 424 1,227 Depreciation and amortisation expense 1,262 1,239 1,413 2,501 2,774 5,560 Other income 1,337 1,568 867 2,905 2,527 4,402 PROFIT FOR THE PERIOD 13,934 13,420 12,131 27,354 24,950 49,454 '
SPLIT_FOOT='(₹ crore) Audited Consolidated Interim Statement of Financial Results Three months ended Six months ended'


def test_separated_year_row_selects_quarters_with_exact_evidence():
    source=SPLIT_HEADER+SPLIT_BODY+SPLIT_FOOT
    result=parse(source)['tables'][0]
    assert result['scope']=='consolidated'
    assert result['periods']==['2026-09-30','2026-06-30','2025-09-30']
    metrics={m['metric']:m for m in result['items']}
    assert metrics['revenue']['values']==['73188','72275','65799']
    assert metrics['pbt']['values']==['18638','17944','16068']
    assert metrics['pat']['values']==['13934','13420','12131']
    assert metrics['ebitda_proxy']['values']==['18815','17888','16843']
    for item in [*result['headers'],metrics['revenue'],metrics['pbt'],metrics['pat'],*metrics['ebitda_proxy']['operands']]:
        assert item['quote'] in source and item['quote'] in item['evidence']['text']


def test_split_columns_fail_closed_on_missing_year_scope_unit_or_groups():
    source=SPLIT_HEADER+SPLIT_BODY+SPLIT_FOOT
    for before,after in [('2026 2026 2025 2026 2025 2026','2026 2026 2025 2026 2025'),
                         ('2026 2026 2025 2026 2025 2026','2026 2026 2025 2025 2025 2026'),
                         ('Six months ended',''),('₹ crore','? crore'),
                         ('Consolidated','Unverified'),('March 31,','December 31,')]:
        assert not parse(source.replace(before,after))['tables']
    corrupt=parse(source.replace('73,188','73,1%8'))['tables'][0]
    assert not any(m['metric']=='revenue' for m in corrupt['items'])
    discontinued=parse(source+' Discontinued operations')['tables'][0]
    assert not any(m['metric']=='ebitda_proxy' for m in discontinued['items'])
