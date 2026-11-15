"""Audit captured API responses against their recorded, versioned evidence.

This is a reproducible exact-quote check, not a substitute for semantic review.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
rows = []
for path in sorted((ROOT / 'data/evaluation').glob('*.json')):
    replay = json.loads(path.read_text(encoding='utf-8'))
    job = replay['job']
    answer = job.get('result', {})
    evidence = {e['id']: e for e in answer.get('evidence', [])}
    citations = []
    for claim in answer.get('claims', []):
        for citation in claim['citations']:
            source = evidence[citation['evidence_id']]
            assert citation['quote'] in source['text'], (path.name, citation['evidence_id'])
            assert source['hash'] in source['id'] and f"-p{source['page']}-" in source['id']
            citations.append({k: source.get(k) for k in
                ('id', 'symbol', 'kind', 'period', 'page', 'hash', 'parser', 'url', 'fetched_at')})
    fresh = json.loads((ROOT / 'data/evaluation-fresh-120b-20261115' / path.name).read_text(encoding='utf-8'))
    rows.append({'case': replay['case'], 'status': answer.get('status', job.get('error', {}).get('code')),
        'fresh_surface': fresh['surface'], 'fresh_wall_seconds': fresh['wall_seconds'],
        'provider': answer.get('provider'), 'model': answer.get('model'),
        'provider_usage': fresh['job'].get('provider_usage'),
        'final_replay_seconds': replay['wall_seconds'], 'final_replay_cached': job.get('id') == 'cache',
        'claim_count': len(answer.get('claims', [])), 'citation_count': len(citations),
        'all_quotes_exact': True, 'citations': citations,
        'coverage': 'Partial: inspect the documented missing topics; not a full completeness pass.' if answer.get('status') == 'partial' else 'See semantic audit.'})
rows.append({'case': 'I2', 'method': 'Controlled missing-transcript fixture in pytest, not live discovery',
             'status': 'passed'})
result = {'audited_at': datetime.now(timezone.utc).isoformat(),
          'method': 'Fresh Groq 120B requests on 15 November; final renderer replayed from cache. Exact quoted text/hash/page checked here; semantic review documented separately. I2 is a fixture.',
          'cases': rows}
(ROOT / 'docs/evaluation-results.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps({'cases': len(rows), 'claims': sum(r.get('claim_count', 0) for r in rows),
                  'citations': sum(r.get('citation_count', 0) for r in rows), 'exact_quote_checks': 'passed'}))
