from backend.segments import extract,latest

DOC={'symbol':'TEST','version':'v1','kind':'annual'}


def revenue(end,crore,scope='consolidated'):
    return {'metric':'revenue','period_kind':'annual','value':crore,'crore':crore,'period_end':end,'scope':scope,
            'restatement':'as_presented_in_v1','quote':f'Revenue from operations {crore}','reported_label':'Revenue from operations','evidence':{'id':'r'}}


FACTS=[revenue('2026-03-31','1000.00'),revenue('2025-03-31','800.00')]


def run(text,facts=FACTS):
    return extract(DOC,[{'id':'v1-p9-c0','page':9,'text':text}],facts)


def test_unlabelled_total_reconciles_and_shares_and_growth_are_cited():
    text=('Segment Information Year ended March 31, 2026 Year ended March 31, 2025 Segment Revenue (Sales and other operating revenue) '
          'Cables 600.00 450.00 Lighting 300.00 250.00 Others 100.00 100.00 1,000.00 800.00 Less : Inter segment revenue - -')
    [mix]=run(text)
    assert mix['kind']=='business' and [s['name'] for s in mix['segments']]==['Cables','Lighting','Others']
    cables=mix['segments'][0]
    from decimal import Decimal
    assert Decimal(cables['share'])==60 and cables['growth'][:6]=='33.333' and cables['quote'] in text
    assert latest([mix])['business'] is mix


def test_million_unit_is_fixed_by_matching_reported_revenue():
    text='Segment revenue Plumbing 7,000 5,500 900 800 Paints 3,000 2,500 100 90 Total 10,000 8,000 1,000 890 Add: Unallocated'
    [mix]=run(text)
    assert mix['unit']=='million' and mix['total_crore']=='1000.0'


def test_rows_that_do_not_add_up_or_do_not_match_revenue_are_rejected():
    assert run('Segment revenue Cables 600.00 450.00 Lighting 300.00 250.00 Total 1,000.00 800.00')==[]
    assert run('Segment revenue Cables 700.00 550.00 Lighting 300.00 250.00 Total 1,000.00 800.00',[revenue('2026-03-31','990.00'),revenue('2025-03-31','800.00')])==[]


def test_geography_split_is_kept_apart_from_business_mix():
    text='Segment Revenue by location Revenue-Domestic Market 950.00 760.00 Revenue-Overseas Market 50.00 40.00 1,000.00 800.00'
    [mix]=run(text)
    assert mix['kind']=='geography' and latest([mix])['business'] is None
