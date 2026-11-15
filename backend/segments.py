"""Revenue mix from segment notes, accepted only when it reconciles.

A segment table qualifies only if its rows add up to its total in both
printed years and that total equals revenue from operations in a cited
annual statement of the same year. The match also fixes the table's unit.
Shares are computed from the cited rows; nothing is inferred for missing
segments or eliminations.
"""
import re
from decimal import Decimal
from .numbers import decimal,UNITS
from .statements import page_text,ref

NUM=r'\(?-?\d[\d,]*(?:\.\d+)?\)?'
ROW=re.compile(r'([A-Z][A-Za-z,&()/\'’\- ]{2,70}?)\s+((?:'+NUM+r'\s+){1,5}'+NUM+r')(?=\s|$)')
TOTAL_LABEL=re.compile(r'^(?:total(?: segment revenue| revenue)?|revenue from operations|segment revenue)$',re.I)
SKIP=re.compile(r'\b(?:less|inter[- ]?segment|elimination|year ended|particulars|segment profit|segment result)\b',re.I)


def value(cell):
    return decimal(cell.replace(',','').replace('(','-').replace(')',''))


def close(a,b):
    return abs(a-b)<=max(Decimal('0.6'),abs(b)*Decimal('0.0015'))


def candidates(text):
    """Rows as (label, [numbers], raw) in reading order."""
    rows=[]
    for m in ROW.finditer(text):
        label=m[1].strip(' ,-')
        # Drop a table caption run into the first row label.
        label=re.sub(r'^.*\)\s+(?=[A-Z])','',label)
        label=re.sub(r'^(?:Segment Revenue|Revenue from operations|Segment)\s+','',label,flags=re.I).strip()
        cells=re.findall(NUM,m[2])
        values=[value(c) for c in cells]
        # "Others 1,726.93 1,378.93 22,465.56 21,745.81": a last segment row
        # followed by an unlabelled total of the same width.
        previous=[r for r in rows if r[0] and not SKIP.search(r[0])][-1:]
        if previous and all(len(r[1])*2==len(values) for r in previous):
            half=len(values)//2;numbers=re.findall(NUM,m[2])
            rows.append((label,values[:half],label+' '+' '.join(numbers[:half])))
            rows.append(('',values[half:],' '.join(numbers[half:])));continue
        rows.append((label,values,m[0]))
    return rows


def extract(doc,rows,statement_facts):
    revenues={}
    for f in statement_facts:
        if f['metric']=='revenue' and f['period_kind']=='annual' and f['value'] is not None:
            revenues.setdefault(f['period_end'],[]).append(f)
    if not revenues:return []
    pages={}
    for row in rows:pages.setdefault(row['page'],[]).append(row)
    found=[]
    for page,parts in pages.items():
        text=page_text(parts)
        for start in re.finditer(r'segment revenue',text,re.I):
            window=text[start.start():start.start()+1800]
            table=candidates(window)
            for t,(label,cells,raw) in enumerate(table):
                if label and not TOTAL_LABEL.match(label):continue
                total_now,total_prior=cells[0],(cells[1] if len(cells)>1 else None)
                if total_prior is None:continue
                width=len(cells)
                for k in range(2,9):
                    block=table[max(0,t-k):t]
                    if len(block)<k:break
                    if any(len(c)!=width or SKIP.search(l) or TOTAL_LABEL.match(l) for l,c,_ in block):continue
                    if not close(sum(c[0] for _,c,_ in block),total_now) or not close(sum(c[1] for _,c,_ in block),total_prior):continue
                    match=reconcile(total_now,total_prior,revenues)
                    if match:found.append(build(doc,parts,block,(label,cells,raw),match))
                    break
    # Same table can be read twice (overlapping windows); keep distinct.
    distinct={}
    for item in found:distinct.setdefault((item['kind'],item['period_end'],item['scope'],tuple(s['name'] for s in item['segments'])),item)
    return list(distinct.values())


def reconcile(now,prior,revenues):
    for end,facts in revenues.items():
        for fact in facts:
            for unit,factor in UNITS.items():
                scale=factor/UNITS['crore']
                if close(now*scale,decimal(fact['crore'])):
                    prior_fact=next((p for p in revenues.get(prior_end(end),[]) if p['scope']==fact['scope'] and p['restatement']==fact['restatement']),None)
                    if prior_fact and close(prior*scale,decimal(prior_fact['crore'])):
                        return {'revenue':fact,'prior_revenue':prior_fact,'scale':scale,'unit':unit}
    return None


def prior_end(end):
    from datetime import date
    from .statements import prior_year
    return prior_year(date.fromisoformat(end)).isoformat()


def build(doc,parts,block,total,match):
    scale=match['scale'];revenue=match['revenue']
    total_now=total[1][0]*scale
    segments=[]
    for label,cells,raw in block:
        now=cells[0]*scale;prior=cells[1]*scale
        citation=ref(doc,parts,raw.strip())
        segments.append({'name':label,'crore':str(now),'prior_crore':str(prior),
            'share':str(now/total_now*100) if total_now else None,
            'growth':str((now/prior-1)*100) if prior>0 else None,
            'quote':raw.strip(),'evidence':citation['evidence'] if citation else None})
    total_ref=ref(doc,parts,total[2].strip())
    names=' '.join(l for l,_,_ in block)
    kind='geography' if re.search(r'\b(?:domestic|overseas|india|outside|export|international|geograph\w*|market|rest of)\b',names,re.I) else 'business'
    return {'symbol':doc['symbol'],'kind':kind,'period_end':revenue['period_end'],'scope':revenue['scope'],'unit':match['unit'],
            'total_crore':str(total_now),'segments':segments,
            'total_quote':total[2].strip(),'total_evidence':total_ref['evidence'] if total_ref else None,
            'reconciles_to':{'crore':revenue['crore'],'quote':revenue['quote'],'evidence':revenue['evidence'],'reported_label':revenue['reported_label']},
            'method':'Segment rows add up to the segment total in both years, and the total equals revenue from operations in the cited statement.'}


def latest(mixes):
    """Newest business mix plus newest geographic split, consolidated first."""
    pick=lambda kind:max((m for m in mixes if m['kind']==kind),key=lambda m:(m['period_end'],m['scope']=='consolidated'),default=None)
    business,geography=pick('business'),pick('geography')
    return {'business':business,'geography':geography} if business or geography else None
