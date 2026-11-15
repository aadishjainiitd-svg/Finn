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

PCT=r'(\d{1,2}(?:\.\d{1,2})?)\s?(?:%|percent)'
BAND=r'(\d{1,2}(?:\.\d{1,2})?)\s?(?:%|percent)?\s*(?:-|–|to)\s*'+PCT


def fiscal_period(quote,doc):
    """Year from the sentence, else the call's own label (Q2 FY27 -> FY27)."""
    def from_text(text):
        m=re.search(r'\b(FY|CY)\s?[\'’]?(20)?(\d{2})\b',text,re.I)
        if m:return m[1].upper(),2000+int(m[3])
        m=re.search(r'\b(?:financial|fiscal) year\s+20(\d{2})(?:\s*-\s*20?(\d{2}))?',text,re.I)
        if m:return 'FY',2000+int(m[2] or m[1])
        return None
    stated=from_text(quote);basis='stated in the sentence'
    if not stated:
        stated=from_text(doc.get('period') or doc.get('discovery_period') or '');basis="the call's fiscal year (not stated in the sentence)"
        if stated and re.search(r'\bnext (?:financial |fiscal )?year\b',quote,re.I):
            stated=(stated[0],stated[1]+1);basis="the year after the call's fiscal year ('next year')"
    if not stated:return None
    kind,year=stated
    end=f'{year}-03-31' if kind=='FY' else f'{year}-12-31'
    label=f'FY{str(year)[2:]}' if kind=='FY' else str(year)
    return {'period_end':end,'label':label,'period_basis':basis}


def percent_target(quote,doc):
    """Margin bands and revenue-growth guidance stated by management in percent."""
    if quote.rstrip().endswith('?') or not re.search(r'\b(?:guid\w*|target\w*|expect\w*|aim\w*|outlook)\b',quote,re.I):return None
    if re.search(r'\bEBITDA\b',quote,re.I):metric='ebitda_margin';name='EBITDA margin'
    elif re.search(r'\b(?:revenue|top[- ]?line|sales)\s+growth\b|\bgrow (?:our )?(?:revenue|top[- ]?line|sales)\b',quote,re.I):metric='revenue_growth';name='Revenue growth'
    elif re.search(r'\bvolume growth\b',quote,re.I):metric='volume_growth';name='Volume growth'
    else:return None
    band=re.search(BAND,quote,re.I);approx=False
    if band:low,high=band[1],band[2]
    else:
        single=re.search(r'(at least|minimum of|around|about|approximately|~)?\s*'+PCT,quote,re.I)
        if not single:return None
        qualifier=(single[1] or '').lower()
        if qualifier in ('at least','minimum of'):low,high=single[2],None
        elif qualifier:
            approx=True;low,high=str(float(single[2])-1),str(float(single[2])+1)
        else:low=high=single[2]
    from .numbers import decimal
    if high is not None and decimal(high)<decimal(low):return None
    period=fiscal_period(quote,doc)
    body=re.sub(r'^[A-Z][\w.\' ]{1,40}:\s*','',quote)
    segment=re.match(r'([A-Z][a-z]+(?: [A-Z][a-z]+)?),\s+we\b',body) or re.search(r'\bfor (?:the |our )?([a-z]+) (?:business|segment|division)\b',body,re.I)
    ambiguous=len(re.findall(BAND,quote,re.I))>1
    shown=(f'{low}–{high}%' if high and high!=low else f'{low}%' if high else f'at least {low}%')
    if approx:shown=f'about {float(low)+1:g}% (read as {low}–{high}%)'
    return {'kind':'percent','symbol':doc.get('symbol'),'metric':metric,'minimum':low,'maximum':high,'approximate':approx,
            'scope':'segment: '+segment[1].lower() if segment else 'company','ambiguous':ambiguous,
            'label':(f'{segment[1]} · ' if segment else '')+f'{name} {shown}'+(f' · {period["label"]}' if period else ' · period not stated'),
            'period_end':period['period_end'] if period else None,'period_basis':period['period_basis'] if period else None,
            'due':period['period_end'] if period else None,'evidence_id':doc['id'],'quote':quote,'status':'issued'}


def percent_verdict(target,facts,today):
    """Revenue growth is scored on cited statement growth; margins only indicatively."""
    from .numbers import decimal
    if target.get('ambiguous'):
        return 'not_comparable',None,'The sentence gives more than one range, so FINN does not pick one to score.'
    if target.get('scope','company')!='company':
        return 'not_comparable',None,'This guidance is for one business segment; segment results are not yet read from the statements.'
    if target['metric']=='volume_growth':
        return 'not_comparable',None,'Volume is not reported in the financial statements, so this cannot be checked from primary numbers.'
    if not target['due']:return 'not_comparable',None,'No fiscal year could be tied to this statement, so it is not scored.'
    if target['due']>today:return 'not_due',None,f'The guided year ends {target["due"]}; not scored until results for it are read.'
    selected=[f for f in facts if f.get('symbol')==target['symbol'] and f.get('period_kind')=='annual' and f.get('value') is not None]
    def value(metric,end,basis=None):
        rows=[f for f in selected if f['metric']==metric and f['period_end']==end and (basis is None or f['restatement']==basis)]
        consolidated=[f for f in rows if f['scope']=='consolidated']
        return (consolidated or rows or [None])[0]
    end=target['due']
    revenue=value('revenue',end)
    if not revenue:return 'not_comparable',None,'Results for the guided year have not been read from an annual statement yet.'
    basis=revenue['restatement']
    if target['metric']=='revenue_growth':
        from .statements import prior_year
        prior=value('revenue',prior_year(datetime.fromisoformat(end).date()).isoformat(),basis)
        if not prior or prior['scope']!=revenue['scope']:return 'not_comparable',None,'The prior year is not printed in the same statement, so growth is not scored.'
        actual=(decimal(revenue['crore'])/decimal(prior['crore'])-1)*100
        operands=[revenue,prior]
        low=decimal(target['minimum']);high=decimal(target['maximum']) if target['maximum'] else None
        status='met' if actual>=low and (high is None or actual<=high) else 'missed'
        return status,{'value':f'{actual:.1f}','unit':'percent','operands':operands,'quote':revenue['quote'],'evidence':revenue['evidence'],
                       'formula':'Revenue ÷ prior-year revenue − 1, both from one statement'},(
            'Reported revenue growth is inside the guided range.' if status=='met' else
            'Reported revenue growth is outside the guided range'+(' (above it).' if high is not None and actual>high else '.'))
    parts=[value(m,end,basis) for m in ('pbt','finance_cost','depreciation','other_income')]
    if not all(parts) or decimal(revenue['crore'])<=0:return 'not_comparable',None,'The statement rows needed for an EBITDA proxy were not all found.'
    proxy=(decimal(parts[0]['crore'])+decimal(parts[1]['crore'])+decimal(parts[2]['crore'])-decimal(parts[3]['crore']))/decimal(revenue['crore'])*100
    low=decimal(target['minimum']);high=decimal(target['maximum']) if target['maximum'] else None
    inside=proxy>=low and (high is None or proxy<=high)
    return 'indicative',{'value':f'{proxy:.1f}','unit':'percent (EBITDA proxy)','operands':[*parts,revenue],'quote':revenue['quote'],'evidence':revenue['evidence'],
        'formula':'(PBT + finance costs + depreciation − other income) ÷ revenue'},(
        f'FINN\'s EBITDA proxy is {"inside" if inside else "outside"} the guided band. The company\'s own EBITDA definition may differ, so this is not counted as kept or missed.')


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
    if calls:
        # Percent guidance is usually phrased around margins and growth.
        known={e['id'] for e in evidence}
        evidence+=[e for e in retrieve(calls,'guidance EBITDA margin percent revenue growth range') if e['id'] not in known]
    today=today or datetime.now(timezone.utc).date().isoformat()
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
            status=promise_verdict(target,actual,today)
        custom=None
        if not target and status=='not_comparable':
            target=percent_target(quote,doc)
            if target:status,actual,custom=percent_verdict(target,facts,today)
        reasons={'met':'The cited comparable actual meets the disclosed minimum or falls within the explicit range; this is not a judgement on broader execution.',
            'missed':'The cited comparable actual falls outside the explicit target. Inspect the target and actual; an upside range miss is not evidence of weaker performance.',
            'not_due':'The disclosed target period has not ended; excluded from the kept count.',
            'revised':'Revised guidance is not scored as kept. Inspect the original and revision before comparing.',
            'withdrawn':'Withdrawn guidance is not scored as kept.',
            'not_comparable':'A metric, accounting basis, due period and cited actual have not all been verified; excluded from the kept count.'}
        items.append({'id':hashlib.sha256((doc['id']+quote).encode()).hexdigest()[:24],
            'quote':quote,'evidence':doc,'speaker':span['speaker'],'status':status,
            'target':target,'actual':actual,'due':target['due'] if target else None,'reason':custom or reasons.get(status,'')})
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
    by_call=promised_vs_delivered(calls,items,facts)
    return {'items':items,'by_call':by_call,'met':met,'missed':missed,'evaluable':met+missed,'kept_percent':100*met/(met+missed) if met+missed else None,
        'coverage':'Candidate commitments from retrieved management passages, not an exhaustive transcript audit.',
        'limitation':'No promise receives kept-count credit without a comparable target and actual. Revised or withdrawn targets never count as met.'}


def latest_quarter_growth(facts,symbol):
    """Newest quarterly revenue with its year-ago column from the same results table."""
    from .numbers import decimal
    quarters=[f for f in facts if f.get('symbol')==symbol and f.get('period_kind')=='quarter' and f.get('metric')=='revenue' and f.get('value') is not None]
    for current in sorted(quarters,key=lambda f:f['period_end'],reverse=True):
        year,rest=current['period_end'][:4],current['period_end'][4:]
        prior=next((f for f in quarters if f['period_end']==str(int(year)-1)+rest and f.get('evidence_id')==current.get('evidence_id') and f.get('scope')==current.get('scope')),None)
        if prior and decimal(prior['value'])>0:
            return {'period_end':current['period_end'],'value':f"{(decimal(current['value'])/decimal(prior['value'])-1)*100:.1f}",
                    'scope':current.get('scope'),'quote':current.get('quote'),'evidence':current.get('evidence'),
                    'label':'Revenue growth vs the same quarter last year, both columns from one results table'}
    return None


def promised_vs_delivered(calls,items,facts):
    """The last four calls, newest first: what management guided on each call
    and what has been delivered so far. Calls without numerical guidance are
    listed so the four-quarter coverage is explicit."""
    ordered=sorted({(c.get('version') or c.get('id') or str(i)):c for i,c in enumerate(calls)}.values(),key=lambda c:c.get('fetched_at') or '',reverse=True)
    def call_key(c):
        import re as _re
        m=_re.search(r'Q([1-4])\s*(?:FY|CY)\s*[\'’]?(?:20)?(\d{2})',c.get('period') or c.get('discovery_period') or '',_re.I)
        return (int(m[2]),int(m[1])) if m else (0,0)
    groups={}
    for c in sorted(ordered,key=call_key,reverse=True):
        groups.setdefault(c.get('period') or c.get('discovery_period') or c.get('title'),[]).append(c)
    rows=[]
    for label,versions in list(groups.items())[:4]:
        call=versions[0];ids={v.get('version') for v in versions if v.get('version')}
        guided=[i for i in items if i['evidence'].get('version') in ids and i.get('target') and i['target'].get('label')]
        entries=[]
        for item in guided:
            target=item['target'];delivered=None
            if item.get('actual'):
                delivered={'value':item['actual']['value'],'unit':item['actual'].get('unit'),'quote':item['actual'].get('quote'),'evidence':item['actual'].get('evidence'),'label':'Reported for the guided year'}
            elif item['status']=='not_due' and target.get('metric')=='revenue_growth':
                progress=latest_quarter_growth(facts,target.get('symbol'))
                if progress:delivered={**progress,'unit':'percent','label':'Progress so far · '+progress['label']}
            entries.append({'promise':target['label'],'status':item['status'],'reason':item['reason'],'quote':item['quote'],
                            'speaker':item.get('speaker'),'evidence':item['evidence'],'delivered':delivered})
        rows.append({'call':label,'evidence':{k:call.get(k) for k in ('title','original_url','version','period')},
                     'entries':entries,'note':None if entries else 'No numerical management guidance passed the checks in this call.'})
    return rows
