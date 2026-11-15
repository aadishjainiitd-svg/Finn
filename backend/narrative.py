"""One bounded cached selection, with explicit missing aspects and no paid fallback."""
import hashlib,json,re
from . import repository,store
from .documents import retrieve
from .llm import synthesize,source_spans,relevant_aspect
from .config import MODEL
from .network import SourceError

ASPECTS=('business','favourable','adverse','accounting')


def business_source(annual):
    for doc in annual:
        name=re.sub(r'\b(?:limited|ltd)\b','',doc.get('name',''),flags=re.I).strip()
        stem=' '.join(name.split()[:2])
        actor=r'(?:\b(?:the|our|your) (?:company|group)\b'+('|'+re.escape(stem) if stem else '')+')'
        action=r'(?:is (?:principally )?engaged in|manufactures|enabling|provides [A-Za-z -]{0,45}(?:products|solutions|services))'
        with store.db() as c:
            rows=c.execute("SELECT id,page,text FROM chunks WHERE hash=? AND (text LIKE '%engaged in%' OR text LIKE '%manufactur%' OR text LIKE '%provides%' OR text LIKE '%enabling%') ORDER BY page,id",(doc['version'],))
            for row in rows:
                for span in source_spans([{**doc,**dict(row)}]).values():
                    quote=span['quote']
                    if len(quote.split())<=70 and re.search(actor+r'.{0,90}\b'+action+r'\b',quote,re.I) and not re.search(r'shareholders|information|not (?:directly )?engaged|global',quote,re.I):
                        return {'aspect':'business','nature':'reported','selection_method':'explicit_issuer_description','sources':[{'quote':quote,'evidence':span['evidence']}]}
    return None


def sanitise(result,annual=()):
    observations=[o for o in result.get('observations',[]) if (o['aspect']!='business' or o.get('selection_method')=='explicit_issuer_description') and (o['aspect']=='business' or relevant_aspect(o['aspect'],' '.join(s['quote'] for s in o['sources'])))]
    if not any(o['aspect']=='business' for o in observations):
        business=business_source(annual)
        if business:observations.insert(0,business)
    bounded=[];words=0
    for item in observations:
        count=sum(len(s['quote'].split()) for s in item['sources'])
        if words+count<=160:bounded.append(item);words+=count
    observed={o['aspect'] for o in bounded}
    return {**result,'observations':bounded,'missing':[a for a in ASPECTS if a not in observed],
        'status':'selected' if len(observed)==4 else 'partial','policy':'research-spans-v2'}


async def build(documents,progress):
    from .research import VERSION
    annual=[d for d in documents if d['kind']=='annual'][:1]
    calls=[d for d in documents if d['kind']=='transcript'][:1]
    key=hashlib.sha256(json.dumps([sorted(d['version'] for d in annual+calls),MODEL,VERSION,'research-spans-v2']).encode()).hexdigest()
    cached=repository.get('_public','narratives',key)
    if cached:return {**cached,'cache_hit':True}
    selections=[retrieve(annual,'What does the company do business products segments?')[:1],
        retrieve(calls or annual,'demand growth backlog orders outlook')[:1],
        retrieve(calls or annual,'risk challenges slower demand uncertainty margin pressure')[:1],
        retrieve(annual,'contingent liabilities litigation related party auditor qualification impairment')[:1]]
    evidence=list({e['id']:e for selected in selections for e in selected}.values())
    base={'observations':[],'missing':list(ASPECTS),'cache_hit':False,
        'coverage':'Selected passages from the latest readable report and call; not an exhaustive risk audit.',
        'limitation':'Favourable and adverse selection is an interpretation. Unselected or unread risks may still exist.'}
    if not evidence:return {**base,'status':'missing_sources'}
    try:
        progress['stage']='Selecting a balanced, source-backed research view'
        result=await synthesize('Select the disclosed business, a favourable case, an adverse case and any substantive accounting concern. Preserve qualifications.',evidence,progress,mode='research')
        observed={o['aspect'] for o in result['observations']}
        result=sanitise({**base,**result},annual)
        repository.save('_public','narratives',key,result)
        return result
    except SourceError as exc:
        # Public excerpts/financial facts remain useful when inference cannot run.
        return {**base,'status':'unavailable','error':exc.message}
