from backend import report_insights as insights


def test_report_alignment_retains_both_sources_and_never_infers_removal(monkeypatch):
    old='The Company considers the trade receivables to be in default when payments are more than five years past due, based on the circumstances of each customer.'
    new=old.replace('five years','three years')
    docs=[{'kind':'annual','symbol':'TEST','period':'2025','version':'new'},{'kind':'annual','symbol':'TEST','period':'2024','version':'old'}]
    monkeypatch.setattr(insights,'sentences',lambda d:[{'quote':new if d['version']=='new' else old,'evidence':{'id':d['version'],'page':1}}])
    result=insights.compare_reports(docs)
    assert result['items'][0]['prior']['quote']==old
    assert result['items'][0]['current']['quote']==new
    assert result['items'][0]['status']=='wording_changed'
    assert 'not labelled new or removed' in result['limitation']
    assert insights.compare_reports(docs[:1])['status']=='missing_documents'
    assert insights.compare_reports([docs[0],{**docs[1],'symbol':'OTHER'}])['status']=='not_comparable'


def test_commitment_ledger_excludes_analysts_refusals_and_unearned_kept_credit(monkeypatch):
    evidence={'kind':'transcript','id':'call-p2','period':'Q2 CY2026','management_speakers':['Anita Rao'],
        'text':'Analyst: We expect revenue of 500 crore next year. Anita Rao: We expect to open our new factory in 2027. We do not provide revenue guidance for 2027.'}
    monkeypatch.setattr(insights,'retrieve',lambda *args:[evidence])
    ledger=insights.commitment_ledger([{'kind':'transcript'}])
    assert len(ledger['items'])==1
    assert ledger['items'][0]['quote'].endswith('factory in 2027.')
    assert ledger['items'][0]['status']=='not_comparable'
    assert ledger['evaluable']==0 and ledger['kept_percent'] is None


def test_explicit_minimum_pairs_only_with_due_comparable_actual_and_revisions_do_not_double_count(monkeypatch):
    statement='We expect consolidated revenue of at least INR 100 crore for the year ending December 31, 2025.'
    evidence={'kind':'transcript','symbol':'TEST','id':'guidance-p3','period':'Q3 CY2025','management_speakers':['Anita Rao'],
        'text':'Anita Rao: '+statement}
    monkeypatch.setattr(insights,'retrieve',lambda *args:[evidence])
    actual={'symbol':'TEST','metric':'revenue','scope':'consolidated','currency':'INR','period_kind':'annual',
        'period_start':'2025-01-01','period_end':'2025-12-31','unit':'crore','value':'110','evidence_id':'report-p5',
        'quote':'Revenue from operations 110.00','evidence':{'id':'report-p5','text':'Revenue from operations 110.00'}}
    docs=[{'kind':'transcript'}]
    ledger=insights.commitment_ledger(docs,[actual],today='2026-02-01')
    assert ledger['met']==1 and ledger['evaluable']==1 and ledger['items'][0]['actual']['evidence_id']=='report-p5'
    assert insights.commitment_ledger(docs,[actual],today='2025-11-01')['items'][0]['status']=='not_due'
    assert insights.commitment_ledger(docs,[{**actual,'scope':'standalone'}],today='2026-02-01')['evaluable']==0
    assert insights.commitment_ledger(docs,[{**actual,'value':'90'}],today='2026-02-01')['missed']==1
    evidence['text']+=' We now expect consolidated revenue of at least INR 120 crore for the year ending December 31, 2025.'
    revised=insights.commitment_ledger(docs,[actual],today='2026-02-01')
    assert revised['evaluable']==0 and len(revised['items'])==2
    assert insights.typed_target(statement.replace('at least','about'),evidence) is None



def test_explicit_quarter_range_and_withdrawal_preserve_status(monkeypatch):
    quote='We expect consolidated revenue between INR 100 and 120 crore for the quarter ending September 30, 2026.'
    evidence={'kind':'transcript','symbol':'TEST','id':'call-p4','period':'Q1 FY2027','management_speakers':['Anita Rao'],'text':'Anita Rao: '+quote}
    target=insights.typed_target(quote,evidence)
    assert target['minimum']=='100' and target['maximum']=='120'
    assert target['period_start']=='2026-07-01' and target['period_kind']=='quarter'
    for bad in [quote.replace('120','90'),quote.replace('100 and','100 lakh and'),quote.replace('September 30','September 29'),quote.replace('consolidated','')]:
        assert insights.typed_target(bad,evidence) is None
    monkeypatch.setattr(insights,'retrieve',lambda *args:[evidence])
    actual={**target,'value':'110','evidence_id':'result-p8','quote':'Revenue 110','evidence':{'id':'result-p8'}}
    ledger=insights.commitment_ledger([{'kind':'transcript'}],[actual],today='2026-11-15')
    assert ledger['met']==1
    evidence['text']='Anita Rao: We have withdrawn our previously issued revenue guidance due to the market uncertainty.'
    withdrawn=insights.commitment_ledger([{'kind':'transcript'}],[actual],today='2026-11-15')
    assert withdrawn['items'][0]['status']=='withdrawn' and withdrawn['evaluable']==0
