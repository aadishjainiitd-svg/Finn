"""Primary-source financial facts. Unknown basis is data, never a default.

The conservative summary reader accepts an explicitly titled annual history,
currency/unit header and exactly one value per year. It does not infer table
columns elsewhere in a flattened PDF, or rename operating profit as EBITDA.
"""
import re
from decimal import Decimal
from .numbers import decimal,UNITS,comparable_growth

METRICS={
    'revenue':r'Revenue from operations|Net revenue|Revenue from Operations',
    'pat':r'Profit after tax(?:es)?',
    'pbt':r'Profit before tax and after exceptional(?: items)?|Profit before tax(?! and)',
    'operating_profit':r'Operating profit before interest and depreciation',
    'net_worth':r'Net worth(?! per)',
    'borrowings':r'Borrowings',
    'dividends':r'Dividend / Dividend tax',
    'orders':r'Orders received',
    'order_backlog':r'Orders backlog',
}
NUMBER=r'(?:\(?-?\d[\d,]*(?:\.\d+)?\)?|[–—-]|Nil)'


def summary_facts(doc,rows):
    facts=[]
    for row in rows:
        text=row['text']
        title=re.search(r'\b(?:FIVE|5|TEN|10)[ -]YEAR\s+(?:FINANCIAL\s+)?(?:SUMMARY|HIGHLIGHTS)\b',text,re.I)
        if not title:continue
        header=text[title.start():title.start()+450]
        unit=re.search(r'(₹|INR|Rs\.?)\s*(?:in\s+)?(crores?|lakhs?|millions?|billions?)',header,re.I)
        years=re.search(r'(?<!\d)((?:20\d{2}\s+){3,9}20\d{2})(?!\d)',header)
        if not unit or not years:continue
        labels=years[1].split();values=[int(y) for y in labels]
        if len(set(values))!=len(values) or values!=sorted(values,reverse=True):continue
        if any(a-b!=1 for a,b in zip(values,values[1:])):continue
        scope='consolidated' if re.search(r'\bconsolidated\b',header,re.I) else 'standalone' if re.search(r'\bstandalone\b',header,re.I) else 'unspecified'
        unit_name=unit[2].lower().rstrip('s')
        for metric,pattern in METRICS.items():
            matches=list(re.finditer(r'(?<!\w)('+pattern+r')\s+('+NUMBER+r'(?:\s+'+NUMBER+r'){'+str(len(labels)-1)+r'})(?![\d,.])',text,re.I))
            for match in matches:
                # A sixth numeric column could be a percentage or note. Do not
                # silently assign the first five values to a five-year header.
                if re.match(r'\s+'+NUMBER+r'(?:\s|$)',text[match.end():],re.I):continue
                cells=re.findall(NUMBER,match[2],re.I)
                if len(cells)!=len(labels):continue
                quote=match[0]
                for year,cell in zip(labels,cells):
                    value=None if cell in ('–','—','-') else Decimal(0) if cell.lower()=='nil' else decimal(cell.replace(',','').replace('(','-').replace(')',''))
                    facts.append({'symbol':doc['symbol'],'metric':metric,'reported_label':match[1],
                        'year':year,'value':str(value) if value is not None else None,
                        'crore':str(value*UNITS[unit_name]/UNITS['crore']) if value is not None else None,
                        'unit':unit_name,'currency':'INR','scope':scope,'period_kind':'annual_summary',
                        'period_start':None,'period_end':None,'restatement':'not established',
                        'qualification':'Includes discontinued operations' if re.search('includes discontinued operations',text,re.I) else 'Comparability must be checked in the statement notes',
                        'evidence':{**doc,**dict(row)},'quote':quote,'header_quote':header[:years.end()],
                        'comparison_status':'Dates and accounting basis require verification before growth calculations'})
    distinct={ (f['metric'],f['year'],f['scope'],f['value'],f['evidence']['id']):f for f in facts }
    ambiguous=set()
    values_by_key={}
    for f in distinct.values():
        key=(f['metric'],f['year'],f['scope'])
        values_by_key.setdefault(key,set()).add(f['value'])
        if len(values_by_key[key])>1:ambiguous.add(key)
    return [f for f in distinct.values() if (f['metric'],f['year'],f['scope']) not in ambiguous]


def growth(current,prior):
    if current['symbol']!=prior['symbol']:raise ValueError('Different issuers')
    if current.get('scope') not in ('consolidated','standalone'):raise ValueError('Unknown accounting basis')
    if current.get('restatement')!=prior.get('restatement'):raise ValueError('Different restatement bases')
    return str(comparable_growth(current,prior))


def promise_verdict(target,actual,today):
    """No kept-count credit without due, comparable, independently cited facts."""
    if target.get('status') in ('revised','withdrawn'):return target['status']
    if not target.get('due') or target['due']>today:return 'not_due'
    if not actual:return 'not_comparable'
    keys=('symbol','metric','currency','scope','period_start','period_end','period_kind')
    if any(not target.get(k) or target[k]!=actual.get(k) for k in keys):return 'not_comparable'
    if target.get('scope') not in ('consolidated','standalone'):return 'not_comparable'
    if not all(x.get('evidence_id') and x.get('quote') for x in (target,actual)):return 'not_comparable'
    try:
        a=decimal(actual['value'])*UNITS[actual['unit']]
        low=decimal(target['minimum'])*UNITS[target['unit']]
        high=decimal(target['maximum'])*UNITS[target['unit']] if target.get('maximum') is not None else None
    except (KeyError,ValueError,ArithmeticError):return 'not_comparable'
    return 'met' if a>=low and (high is None or a<=high) else 'missed'


def cash_bridge(cash_from_operations,capex,acquisitions,dividends,net_debt_flow,other_cash_flow,opening,closing):
    operands=[decimal(v) for v in (cash_from_operations,capex,acquisitions,dividends,net_debt_flow,other_cash_flow,opening,closing)]
    cfo,capex,acq,div,debt,other,start,end=operands
    # Uses are positive; debt and other are signed net inflows. Never add gross
    # borrowing and net borrowing, or capex including acquisitions twice.
    computed=start+cfo-capex-acq-div+debt+other
    return {'computed_closing':str(computed),'reported_closing':str(end),'residual':str(end-computed),
            'reconciled':abs(end-computed)<=Decimal('.01')}
