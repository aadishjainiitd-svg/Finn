"""Bounded extractive report comparison and attributed commitment ledger.

These selectors do not turn unmatched text into an absence claim, or an
aspiration into a completed promise. All displayed wording is source wording.
"""
import hashlib
import re
from datetime import datetime,timedelta,timezone
from difflib import SequenceMatcher
from . import store
from .documents import retrieve
from .llm import source_spans
from .facts import promise_verdict
from .statements import DATE


def typed_target(quote,evidence):
    """Only explicit currency/basis, minimum or band and dated period qualify."""
    amount=r'([\d,]+(?:\.\d+)?)'
    pattern=(r'\b(consolidated|standalone)\s+(revenue|profit after tax)\s+(?:of\s+)?'
             r'(?:(at least|a minimum of)\s+|(between|in the range of)\s+)'
             r'(INR|Rs\.?|₹)\s*'+amount+r'(?:\s*(crores?|lakhs?|millions?))?'
             r'(?:\s*(?:and|to|[-–])\s*(?:INR|Rs\.?|₹)?\s*'+amount+r')?'
             r'\s*(crores?|lakhs?|millions?)?\s+for (?:the )?(year|quarter) (?:ending|ended)\s+('+DATE+')')
    m=re.search(pattern,quote,re.I)
    if not m or re.search(r'approximately|around|about|subject to|assuming',quote,re.I):return None
    from .numbers import decimal
    from .results import quarter_start
    unit=(m[9] or m[7] or '').lower().rstrip('s')
    if not unit or (m[7] and m[9] and m[7].lower().rstrip('s')!=unit):return None
    if bool(m[4])!=bool(m[8]):return None
    if m[8] and decimal(m[8].replace(',',''))<decimal(m[6].replace(',','')):return None
    try:
        end=datetime.strptime(m[11].replace(',',''),'%B %d %Y').date()
        if m[10].lower()=='quarter':
            import calendar
            if end.month not in (3,6,9,12) or end.day!=calendar.monthrange(end.year,end.month)[1]:return None
            start=quarter_start(end)
        else:start=end.replace(year=end.year-1)+timedelta(days=1)
    except ValueError:return None
    return {'symbol':evidence.get('symbol'),'metric':{'revenue':'revenue','profit after tax':'pat'}[m[2].lower()],
        'scope':m[1].lower(),'currency':'INR','unit':unit,
        'minimum':m[6].replace(',',''),'maximum':m[8].replace(',','') if m[8] else None,
        'period_kind':'quarter' if m[10].lower()=='quarter' else 'annual',
        'period_start':start.isoformat(),'period_end':end.isoformat(),'due':end.isoformat(),
        'evidence_id':evidence['id'],'quote':quote,
        'status':'withdrawn' if re.search(r'\bwithdraw',quote,re.I) else 'revised' if re.search(r'\brevis',quote,re.I) else 'issued'}

TOPICS={
    'Contingencies':r'contingent liabilit|litigation|legal proceedings',
    'Related parties':r'related.part(?:y|ies)',
    'Receivables':r'trade receivables|expected credit loss',
    'Inventory':r'inventor(?:y|ies)|obsolescen',
    'Liquidity':r'liquidity risk|debt covenant|default on',
    'Capital spending':r'capital expenditure|capital commitment',
}


def sentences(doc):
    with store.db() as c:
        rows=c.execute('SELECT id,page,text FROM chunks WHERE hash=? ORDER BY page,id',(doc['version'],)).fetchall()
    candidates={}
    for row in rows:
        evidence={**doc,**dict(row)}
        for span in source_spans([evidence]).values():
            quote=span['quote']
            if 100<=len(quote)<=1000:
                candidates.setdefault(quote,{'quote':quote,'evidence':evidence})
    return list(candidates.values())


def compare_reports(documents):
    annual=[d for d in documents if d['kind']=='annual']
    result={'status':'missing_documents','items':[],
        'limitation':'Only aligned extracted passages are compared. Unmatched text is not labelled new or removed: full textual and section coverage has not been established.'}
    if len(annual)<2:return result
    # Discovery returns newest first. Require distinct verified reporting labels
    # and the same issuer, not merely two downloaded URLs.
    current,prior=annual[:2]
    if current['symbol']!=prior['symbol'] or current['period']==prior['period']:
        return {**result,'status':'not_comparable'}
    left,right=sentences(prior),sentences(current)
    exact_left={s['quote'] for s in left};exact_right={s['quote'] for s in right}
    result.update(status='compared',current_period=current['period'],prior_period=prior['period'])
    used=set()
    for label,pattern in TOPICS.items():
        olds=[s for s in left if s['quote'] not in exact_right and re.search(pattern,s['quote'],re.I)][:80]
        news=[s for s in right if s['quote'] not in exact_left and re.search(pattern,s['quote'],re.I)][:80]
        pairs=[]
        for new in news:
            nw=set(re.findall(r'[a-z]{4,}',new['quote'].lower()))
            for old in olds:
                ow=set(re.findall(r'[a-z]{4,}',old['quote'].lower()))
                if len(nw&ow)/max(1,len(nw|ow))<.6:continue
                ratio=SequenceMatcher(None,old['quote'].lower(),new['quote'].lower(),autojunk=False).ratio()
                if .72<=ratio<1:pairs.append((ratio,old,new))
        for ratio,old,new in sorted(pairs,key=lambda p:-p[0]):
            if old['quote'] in used or new['quote'] in used:continue
            used.update((old['quote'],new['quote']))
            result['items'].append({'topic':label,'status':'wording_changed','prior':old,'current':new,
                'note':'Similar passages with different wording. Inspect both contexts before interpreting the change.'})
            break
    return result


def commitment_ledger(documents,facts=(),today=None):
    calls=[d for d in documents if d['kind']=='transcript']
    evidence=retrieve(calls,'management guidance target commitment expect plan achieve capacity revenue margin next year') if calls else []
    items=[];seen=set()
    for span in source_spans(evidence).values():
        quote=span['quote']
        if not re.search(r'\b(?:expect|aim|plan|target|guidance|will|withdraw|withdrawn|revised)\b',quote,re.I):continue
        if not re.search(r'\d|next (?:year|quarter)|by (?:march|june|september|december)|\bwithdraw(?:n)?\b|\brevised\b',quote,re.I):continue
        # A refusal to guide is useful evidence, but not an issued promise.
        if re.search(r'\b(?:not|no|never)\b.{0,35}\b(?:guidance|target)|do not provide',quote,re.I):continue
        if quote in seen:continue
        seen.add(quote)
        doc=span['evidence']
        target=typed_target(quote,doc);actual=None;status='not_comparable'
        if re.search(r'\bwithdraw(?:n)?\b.{0,50}\b(?:guidance|target)|\b(?:guidance|target)\b.{0,50}\bwithdrawn\b',quote,re.I):status='withdrawn'
        elif re.search(r'\brevis(?:ed|e)\b.{0,50}\b(?:guidance|target)',quote,re.I):status='revised'
        if target:
            matches=[f for f in facts if all(f.get(k)==target.get(k) for k in ('symbol','metric','scope','currency','period_start','period_end','period_kind')) and f.get('value') is not None]
            # Conflicting report versions require an explicit restatement review.
            if matches and len({(f['value'],f['unit']) for f in matches})==1:actual=matches[0]
            status=promise_verdict(target,actual,today or datetime.now(timezone.utc).date().isoformat())
        reasons={'met':'The cited comparable actual meets the disclosed minimum or falls within the explicit range; this is not a judgement on broader execution.',
            'missed':'The cited comparable actual falls outside the explicit target. Inspect the target and actual; an upside range miss is not evidence of weaker performance.',
            'not_due':'The disclosed target period has not ended; excluded from the kept count.',
            'revised':'Revised guidance is not scored as kept. Inspect the original and revision before comparing.',
            'withdrawn':'Withdrawn guidance is not scored as kept.',
            'not_comparable':'A metric, accounting basis, due period and cited actual have not all been verified; excluded from the kept count.'}
        items.append({'id':hashlib.sha256((doc['id']+quote).encode()).hexdigest()[:24],
            'quote':quote,'evidence':doc,'speaker':span['speaker'],'status':status,
            'target':target,'actual':actual,'due':target['due'] if target else None,'reason':reasons[status]})
        if len(items)>=12:break
    # Changed targets for the same metric/period are not two independent wins.
    groups={}
    for item in items:
        t=item['target']
        if t:groups.setdefault(tuple(t.get(k) for k in ('symbol','metric','scope','period_start','period_end')),[]).append(item)
    for group in groups.values():
        if len(group)>1:
            for item in group:
                if item['status'] in ('revised','withdrawn'):continue
                item.update(status='not_comparable',reason='Multiple guidance statements for this metric and period require revision/order review; excluded from the kept count.')
    met=sum(i['status']=='met' for i in items);missed=sum(i['status']=='missed' for i in items)
    return {'items':items,'met':met,'missed':missed,'evaluable':met+missed,'kept_percent':100*met/(met+missed) if met+missed else None,
        'coverage':'Candidate commitments from retrieved management passages, not an exhaustive transcript audit.',
        'limitation':'No promise receives kept-count credit without a comparable target and actual. Revised or withdrawn targets never count as met.'}
