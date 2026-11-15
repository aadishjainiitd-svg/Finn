"""A bounded, owner-scoped question over documents already read for the book."""
import hashlib,json
from . import repository,store,research_pack
from .documents import retrieve
from .llm import synthesize
from .sources import now


async def run(progress,owner,payload):
    from .research import worker,VERSION
    async with worker:
        symbols=payload['symbols'];question=payload['question']
        from .conversations import prompt,query
        focused=prompt(question,payload.get('conversation'))
        groups=[];documents=[];gaps=[]
        snapshot=store.cached('brief-snapshot') or {'events':[]}
        for symbol in symbols:
            progress['stage']='Reading stored sources for '+symbol
            pack=research_pack.get(symbol)
            docs=[]
            if pack:
                for kind in ('annual','transcript'):
                    selected=next((d for d in pack['documents'] if d['kind']==kind),None)
                    if selected and store.rehydrate(selected['version']):docs.append(selected)
            selected=retrieve(docs,query(question,payload.get('conversation')))[:2] if docs else []
            if not selected:
                selected=[e for event in snapshot['events'] if event['symbol']==symbol and event.get('assessment')=='assessed' for e in event.get('evidence',[])][:2]
            if selected:
                groups.append(selected);documents.extend(docs or [{k:v for k,v in e.items() if k not in ('text','quote')} for e in selected])
            else:gaps.append({'kind':'coverage','message':symbol+': no readable retained report, transcript or assessed filing was available. Open Research to read its documents.'})
        # Round robin before the model's hard token admission, to avoid giving a
        # long first report the entire context budget.
        evidence=[group[i] for i in range(2) for group in groups if i<len(group)]
        progress.update(documents=documents,gaps=gaps,evidence=evidence)
        signature=[owner,symbols,payload['book_version'],focused,[e['id'] for e in evidence],VERSION,'portfolio-v1']
        key=hashlib.sha256(json.dumps(signature).encode()).hexdigest()
        cached=repository.get(owner,'portfolio_answers',key)
        if cached:result={**cached['answer'],'cache_hit':True}
        elif not evidence:
            result={'status':'insufficient_evidence','claims':[],'evidence':[],
                'limitation':'No read primary documents are available for this book. No company knowledge or portfolio conclusion was inferred.','provider':'deterministic'}
        else:
            result=await synthesize(focused,evidence,progress)
            included={e['symbol'] for e in result.get('evidence',[])}
            by_id={e['id']:e for e in result.get('evidence',[])}
            answered={by_id[c['evidence_id']]['symbol'] for claim in result.get('claims',[]) for c in claim['citations'] if c['evidence_id'] in by_id}
            for symbol in symbols:
                if symbol not in included and not any(g['message'].startswith(symbol+':') for g in gaps):
                    gaps.append({'kind':'context_limit','message':symbol+': its passages did not fit the free answer context. Ask a narrower company question.'})
                elif symbol not in answered and not any(g['message'].startswith(symbol+':') for g in gaps):
                    gaps.append({'kind':'unanswered','message':symbol+': no supporting point was selected for this question. This is not evidence of no risk or no change.'})
            if gaps and result.get('claims'):result['status']='partial'
            result['limitation']+=' This is a source selection across the book, not an exhaustive portfolio assessment. No combined financial totals are inferred.'
        if not cached:
            result.update(company={'symbol':'BOOK','name':'Your book · saved scope'},question=question,documents=documents,gaps=gaps,
                answered_at=now(),cache_hit=False,scope={'kind':'portfolio','symbols':symbols,'book_version':payload['book_version']})
            repository.save(owner,'portfolio_answers',key,{'answer':result})
        if payload.get('conversation'):result={**result,'conversation':payload['conversation']}
        progress.update(status='complete',stage='Complete',result=result)
