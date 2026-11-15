"""Owner-only observed work usage. Never exports questions or credentials."""
import json
from . import repository

def for_owner(owner):
    with repository.transaction() as tx:
        rows=tx.execute('SELECT id,kind,status,progress,created,updated FROM work_jobs WHERE owner=? ORDER BY created DESC LIMIT 200',(owner,)).fetchall()
    reports=[]
    for row in rows:
        progress=json.loads(row['progress']);usage=progress.get('provider_usage_total') or progress.get('provider_usage')
        unknown_attempts=max(0,progress.get('model_attempts',0)-progress.get('reported_attempts',0))
        source_only=row['kind'] in ('research_pack','refresh','filing','thesis') and not progress.get('model_attempts')
        cache_hit=progress.get('result',{}).get('cache_hit',False)
        reports.append({'id':row['id'],'kind':row['kind'],'status':row['status'],
            'wall_seconds':round(max(0,row['updated']-row['created']),2) if row['status'] in ('complete','error') else None,
            'tokens':usage.get('total_tokens') if usage else 0 if source_only or cache_hit else None,
            'prompt_tokens':usage.get('prompt_tokens') if usage else None,
            'completion_tokens':usage.get('completion_tokens') if usage else None,
            'cache_hit':progress.get('result',{}).get('cache_hit',False),
            'unknown_attempts':unknown_attempts,
            'token_status':('Observed usage only; '+str(unknown_attempts)+' attempts have no reported usage') if unknown_attempts else 'Provider returned observed usage' if usage else 'No new model inference; cached answer' if cache_hit else 'No model inference in this source-only job' if source_only else 'Usage not returned; not treated as zero'})
    history=repository.listing(owner,'history',200)
    return {'reports':reports,'observed_tokens':sum(r['tokens'] or 0 for r in reports),
        'unknown_usage_jobs':sum(r['tokens'] is None or r['unknown_attempts']>0 for r in reports),
        'cached_answers':sum(bool(r.get('answer',{}).get('cache_hit')) for r in history),
        'answered_questions':len(history),'currency_cost':None,
        'cost_note':'Free-tier configuration only. No billing amount is returned by the provider; an invoice cost is not inferred from token counts.',
        'coverage_note':'Most recent 200 jobs and 200 answers for this browser owner. Shared document extraction is not repeatedly charged to each answer. Historical jobs and earlier interrupted attempts without usage stay unknown.'}
