"""Cross-check two independent readers over the cached annual reports.

The statement reader (backend.statements) and the five-year summary reader
(backend.facts.summary_facts) parse different tables of the same report. Where
both report the same metric and year, they should agree. Disagreements and
coverage are written to docs/extraction-crosscheck.json. No network, no model.
Run: python scripts/extraction_crosscheck.py
"""
import json
import sqlite3
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend import statements  # noqa: E402
from backend.facts import summary_facts  # noqa: E402
from backend.config import DATA  # noqa: E402

PAIRS = {'revenue': 'revenue', 'pat': 'pat'}


def main():
    db = sqlite3.connect(DATA / 'finn.sqlite')
    db.row_factory = sqlite3.Row
    docs = {}
    for row in db.execute("SELECT meta FROM documents WHERE kind='annual'"):
        meta = json.loads(row['meta'])
        if 'version' in meta:
            docs.setdefault(meta['version'], meta)
    by_symbol = {}
    for version, meta in docs.items():
        rows = db.execute('SELECT id,page,text FROM chunks WHERE hash=? ORDER BY page,id', (version,)).fetchall()
        entry = by_symbol.setdefault(meta['symbol'], {'statement': [], 'summary': [], 'reports': 0})
        entry['reports'] += 1
        entry['statement'] += statements.extract(meta, rows)
        entry['summary'] += summary_facts(meta, rows)
    results = []
    for symbol, entry in sorted(by_symbol.items()):
        compared = agreed = 0
        mismatches = []
        for s in entry['summary']:
            if s['metric'] not in PAIRS or s['crore'] is None:
                continue
            candidates = [f for f in entry['statement'] if f['metric'] == PAIRS[s['metric']] and f['year'] == s['year']
                          and f['period_kind'] == 'annual' and f['crore'] is not None
                          and (s['scope'] == 'unspecified' or f['scope'] == s['scope'])]
            if not candidates:
                continue
            compared += 1
            summary_value = Decimal(s['crore'])
            match = any(abs(Decimal(f['crore']) - summary_value) <= Decimal('0.5') for f in candidates)
            agreed += match
            if not match:
                mismatches.append({'metric': s['metric'], 'year': s['year'], 'summary': s['crore'],
                                   'statements': sorted({f['crore'] for f in candidates}), 'summary_scope': s['scope']})
        years = sorted({f['year'] for f in entry['statement'] if f['metric'] == 'revenue' and f['period_kind'] == 'annual'})
        results.append({'symbol': symbol, 'reports_read': entry['reports'], 'statement_revenue_years': years,
                        'compared': compared, 'agreed': agreed, 'mismatches': mismatches})
    total = sum(r['compared'] for r in results)
    report = {'checked_at': datetime.now(timezone.utc).isoformat(),
              'method': 'Statement reader vs five-year summary reader on the same cached reports; tolerance 0.5 crore.',
              'limits': 'Only companies whose reports print a parseable five-year summary can be cross-checked. '
                        'Agreement shows two readers are consistent, not that either is complete. '
                        'These companies were also used while building the readers, so this is not a held-out test.',
              'compared': total, 'agreed': sum(r['agreed'] for r in results), 'companies': results}
    out = ROOT / 'docs' / 'extraction-crosscheck.json'
    out.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(f"compared {total}, agreed {report['agreed']}")
    for r in results:
        print(r['symbol'], 'reports', r['reports_read'], 'years', r['statement_revenue_years'], 'compared', r['compared'], 'agreed', r['agreed'], r['mismatches'][:3])


if __name__ == '__main__':
    main()
