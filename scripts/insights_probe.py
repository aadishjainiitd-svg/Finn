"""Reprocess retained primary pages, not a new source/model request."""
import json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend import store,repository,research_pack,statements
from backend.report_insights import compare_reports,commitment_ledger
from backend.sources import now

def main():
    report={'kind':'Retained live ABB primary-source reprocessing; real Neon reads/writes; no new download or model inference','checked_at':now()}
    started=time.monotonic()
    try:
        pack=research_pack.get('ABB')
        if not pack:raise ValueError('Pack absent')
        for doc in pack['documents']:
            if not store.rehydrate(doc['version']):raise ValueError('Source unavailable')
        changes=compare_reports(pack['documents'])
        facts=[]
        with store.db() as c:
            for doc in pack['documents']:
                if doc['kind']=='annual':facts.extend(statements.extract(doc,c.execute('SELECT id,page,text FROM chunks WHERE hash=? ORDER BY page,id',(doc['version'],)).fetchall()))
        financials=statements.compact(statements.analyse(facts))
        ledger=commitment_ledger(pack['documents'],facts)
        passages=[p for item in changes['items'] for p in (item['prior'],item['current'])]+ledger['items']
        for passage in passages:
            source=repository.evidence(passage['evidence']['id'])
            assert source and passage['quote'] in source['text'] and source['page']==passage['evidence']['page']
        retained={eid:repository.evidence(eid) for eid in financials['evidence']}
        for fact in financials['facts'].values():
            assert fact['quote'] in retained[fact['evidence_id']]['text']
            for header in fact['headers']:assert header['quote'] in retained[header['evidence_id']]['text']
        repository.save('_public','research_packs',research_pack.key('ABB'),{**pack,'report_changes':changes,'commitments':ledger,'financials':financials})
        report.update(status='passed',changed_passage_pairs=len(changes['items']),commitment_candidates=len(ledger['items']),
            exact_citations_verified=len(passages),evaluable_commitments=ledger['evaluable'],
            statement_facts=len(financials['facts']),financial_payload_bytes=len(json.dumps(financials).encode()),
            annual_comparisons=[{'year':y['year'],'scope':y['scope'],'growth':[{'metric':g['metric'],'percent':g['percent']} for g in y['growth']],
                'cash_reconciled':y['cash_bridge']['reconciled'] if y['cash_bridge'] else None,
                'cash_residual':y['cash_bridge']['residual'] if y['cash_bridge'] else None} for y in financials['years']],
            limitation='Automated exact-text/typed statement checks, not visual PDF audit. No verified target/actual promise pairs; no full new/removed-section or semantic review claimed.')
    except Exception as exc:report.update(status='failed',error_type=type(exc).__name__)
    report['elapsed_seconds']=round(time.monotonic()-started,2)
    Path('docs/insights-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report))
    repository.close()

if __name__=='__main__':main()
