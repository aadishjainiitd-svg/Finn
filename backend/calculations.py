"""Narrow, auditable numerical answers. No general table inference."""
import re
from .numbers import decimal,UNITS
from .llm import source_spans

def numerical_answer(question,evidence):
    q=question.lower()
    if not re.search(r'\b(calculate|compute|convert)\b|percentage.point difference',q):return None
    result={'status':'insufficient_evidence','claims':[],'limitation':'The retrieved passages do not establish comparable operands with a verified period, currency, unit and accounting basis. FINN has not calculated or guessed the result.',
            'provider':'deterministic','model':None,'evidence':evidence}
    # One explicit narrative amount can be converted without comparing accounting
    # bases or periods. Unknown accounting scope stays explicitly unknown.
    target=re.search(r'\b(?:to|in|into)\s+(lakh|crore|million|billion|rupee)s?\b',q)
    if 'convert' not in q or not target or 'revenue' not in q:return result
    if re.search(r'growth|difference|versus|compare|standalone|consolidated',q):return result
    candidates=[]
    pattern=r'\bRevenue for the quarter was\s*(₹|INR|Rs\.?)\s*([\d,]+(?:\.\d+)?)\s*(crore|lakh|million|billion)\b'
    for span in source_spans(evidence).values():
        match=re.search(pattern,span['quote'],re.I);doc=span['evidence']
        if match and doc['kind']=='transcript' and re.search(r'Q[1-4].*FY',doc['period'],re.I):candidates.append((match,span))
    distinct={(m[2],m[3].lower(),s['evidence']['hash'],s['evidence']['page']):(m,s) for m,s in candidates}
    if len(distinct)!=1:return result
    match,span=next(iter(distinct.values()));source_unit=match[3].lower();target_unit=target[1]
    value=decimal(match[2].replace(',',''));converted=value*UNITS[source_unit]/UNITS[target_unit];doc=span['evidence']
    text=f"Reported quarterly revenue of INR {value:,.2f} {source_unit} equals INR {converted:,.2f} {target_unit} ({doc['period']})."
    return {**result,'status':'supported','claims':[{'text':text,'nature':'reported','citations':[{'evidence_id':doc['id'],'quote':span['quote']}]}],
        'limitation':'This converts the one amount management reported. The excerpt does not explicitly identify consolidated or standalone scope; no cross-period or cross-basis comparison is made.',
        'calculation':{'formula':f'{value} × {UNITS[source_unit]} ÷ {UNITS[target_unit]} = {converted}',
            'operand':{'metric':'quarterly revenue','value':str(value),'currency':'INR','unit':source_unit,'period':doc['period'],
                       'scope':'Not specified in the cited narrative','evidence_id':doc['id'],'quote':span['quote']},'result_unit':target_unit}}
