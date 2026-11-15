"""Strict two-column annual statements with explicit scope, dates and units.

Only recognisable primary statement pages are accepted. A missing/ambiguous
column is not assigned by an LLM. All row and header references are retained.
"""
import calendar,re,hashlib,json
from datetime import datetime,timedelta
from decimal import Decimal
from .numbers import decimal,UNITS
from .facts import growth

DATE=r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+20\d{2}'
CELL=r'(?:\(?-?\d[\d,]*\.\d{1,2}\)?|[–—-])'
INCOME={
 'revenue':r'Revenue from operations',
 'other_income':r'Other income',
 'finance_cost':r'Finance costs?',
 'depreciation':r'Depreciation and amortisation expense',
 'pbt_continuing':r'Profit from continuing operations before tax|Profit before tax from continuing operations',
 'pbt':r'Profit before tax(?! from| and)',
 'pat_continuing':r'Profit from continuing operations after tax',
 'pat':r'Profit for the year',
 'nii':r'Net interest income',
 'operating_profit':r'Operating profit before provisions(?: and contingencies)?',
 'interest_earned':r'Interest earned',
 'interest_expended':r'Interest expended',
}
CASH={
 'cfo':r'Net cash flow (?:from|generated from|provided by) operating activities',
 'cfi':r'Net cash flow (?:from / \(used in\)|used in|from) investing activities',
 'cff':r'Net cash flow (?:from / \(used in\)|used in|from) financing activities',
 'capex':r'Purchase of property, plant and equipment',
 'acquisitions':r'Acquisition of subsidiar(?:y|ies),? net of cash acquired',
 'dividends':r'Dividend paid(?: \(including tax on dividend\))?',
 'lease_principal':r'Payment of principal portion of lease liabilities',
 'debt_repayment':r'Repayment of borrowings',
 'investments':r'Investment in bank deposits \(with maturity more than three months\)',
 'fx':r'Effects of exchange \(loss\) / gain on cash and cash equivalents',
 'opening_cash':r'Cash and cash equivalents \(opening balance\)',
 'closing_cash':r'Cash and cash equivalents \(closing balance\)',
}
BALANCE={
 'total_assets':r'Total assets',
 'total_equity':r'Total equity(?! and)',
 'current_liabilities':r'Total current liabilities',
 'current_borrowings':r'Borrowings',
 'noncurrent_borrowings':r'Borrowings',
 'inventories':r'Inventories',
 'receivables':r'Trade receivables',
 'cash_balance':r'Cash and cash equivalents',
 'advances':r'(?:Gross )?Advances',
 'deposits':r'Deposits',
}



def ref(doc,rows,quote):
    row=next((r for r in rows if quote in r['text']),None)
    return {'quote':quote,'evidence':{**doc,**dict(row)}} if row else None


def page_text(rows):
    text=''
    for row in sorted(rows,key=lambda r:int(re.search(r'-c(\d+)$',r['id'])[1]) if re.search(r'-c(\d+)$',r['id']) else 0):
        part=row['text'];overlap=0
        for length in range(min(len(text),len(part),1000),19,-1):
            if text.endswith(part[:length]):overlap=length;break
        text+=part[overlap:]
    return text


def annual_dates(text):
    candidates=re.findall(DATE,text[:500],re.I)
    dates=[]
    for candidate in candidates:
        try:value=datetime.strptime(candidate.replace(',',''),'%B %d %Y').date()
        except ValueError:return None
        if value not in dates:dates.append(value)
    if len(dates)!=2 or dates[0].year-dates[1].year!=1 or (dates[0].month,dates[0].day)!=(dates[1].month,dates[1].day):return None
    return dates


def extract(doc,rows):
    pages={}
    for row in rows:pages.setdefault(row['page'],[]).append(row)
    facts=[]
    declarations={}
    for row in rows:
        for m in re.finditer(r'(?:The )?(consolidated|standalone) financial statements are presented in (?:INR|Indian [Rr]upees?) in (crores?|lakhs?|millions?)',row['text'],re.I):
            declarations[m[1].lower()]=(m[2].lower().rstrip('s'),ref(doc,[row],m[0]))
    for page,parts in pages.items():
        text=page_text(parts)
        title=re.search(r'(CONSOLIDATED|STANDALONE) STATEMENT OF (PROFIT AND LOSS|CASH FLOWS)\s+For the year ended\s+('+DATE+')',text,re.I)
        balance=re.search(r'(CONSOLIDATED|STANDALONE) BALANCE SHEET\s+as at\s+('+DATE+')',text,re.I)
        if not title and not balance:continue
        if title:scope=title[1].lower();kind='income' if title[2].lower()=='profit and loss' else 'cash';title_label=title[3]
        else:title=balance;scope=title[1].lower();kind='balance';title_label=title[2]
        dates=annual_dates(text)
        if not dates:continue
        title_date=datetime.strptime(title_label.replace(',',''),'%B %d %Y').date()
        if dates[0]!=title_date:continue
        header=text[:max(250,text.find('Income') if kind=='income' and 'Income' in text[:500] else 250)]
        units=re.search(r'\(([^()]{1,20}?)\s+in\s+(crores?|lakhs?|millions?)\)',header,re.I)
        if not units:continue
        unit=units[2].lower().rstrip('s');currency=units[1].strip().lower()
        currency_source=None
        if currency not in ('₹','inr','rs.','rs','indian rupees'):
            # Broken rupee glyphs are common. Resolve only through an explicit
            # same-scope presentation-currency declaration, not a glyph mapping.
            declared=declarations.get(scope)
            if not declared or declared[0]!=unit or len(currency)!=1:continue
            currency_source=declared[1]
        headers=[ref(doc,parts,title[0]),ref(doc,parts,units[0])]
        for date in dates:
            candidate=next((m[0] for m in re.finditer(DATE,text[:500],re.I) if datetime.strptime(m[0].replace(',',''),'%B %d %Y').date()==date),None)
            headers.append(ref(doc,parts,candidate) if candidate else None)
        if currency_source:headers.append(currency_source)
        if not all(headers):continue
        for metric,pattern in (INCOME if kind=='income' else BALANCE if kind=='balance' else CASH).items():
            search_text=text
            if metric in ('current_borrowings','noncurrent_borrowings'):
                label='Non-current liabilities' if metric=='noncurrent_borrowings' else 'Current liabilities'
                block=re.search(r'(?<![\w-])'+label+r'(.*?)Total '+label,text,re.I|re.S)
                if not block:continue
                search_text=block[1]
            regex=r'(?<!\w)('+pattern+r')\s+(?:\d{1,2}\s+)?('+CELL+r')\s+('+CELL+r')(?![\d.,])'
            for m in re.finditer(regex,search_text,re.I):
                if re.match(r'\s+'+CELL+r'(?:\s|$)',search_text[m.end():]):continue
                citation=ref(doc,parts,m[0])
                if not citation:continue
                for end,cell in zip(dates,(m[2],m[3])):
                    previous=end.replace(year=end.year-1,day=min(end.day,calendar.monthrange(end.year-1,end.month)[1]))
                    value=None if cell in ('–','—','-') else decimal(cell.replace(',','').replace('(','-').replace(')',''))
                    facts.append({'symbol':doc['symbol'],'metric':metric,'reported_label':m[1],
                        'year':str(end.year),'value':str(value) if value is not None else None,
                        'crore':str(value*UNITS[unit]/UNITS['crore']) if value is not None else None,
                        'currency':'INR','unit':unit,'scope':scope,'period_kind':'instant' if kind=='balance' else 'annual','statement':kind,
                        'period_start':end.isoformat() if kind=='balance' else (previous+timedelta(days=1)).isoformat(),'period_end':end.isoformat(),
                        'restatement':'as_presented_in_'+doc['version'],'evidence_id':citation['evidence']['id'],
                        **citation,'headers':headers,'qualification':'Comparative values as presented in the same statement; continuing/discontinued labels retained.'})
    distinct={}
    conflicts=set()
    for fact in facts:
        key=(fact['metric'],fact['period_end'],fact['scope'])
        if key in distinct and distinct[key]['value']!=fact['value']:conflicts.add(key)
        else:distinct[key]=fact
    return [value for key,value in distinct.items() if key not in conflicts]


def analyse(facts):
    available_scopes={f['scope'] for f in facts}
    scope='consolidated' if 'consolidated' in available_scopes else 'standalone'
    selected=[f for f in facts if f['scope']==scope]
    financial=any(f['metric'] in ('nii','interest_earned','interest_expended') for f in selected) or {'advances','deposits'}<={f['metric'] for f in selected}
    years=sorted({f['year'] for f in selected},reverse=True)
    summaries=[]
    for year in years:
        # Prefer latest report's restatement basis and never merge components
        # from different versions into one calculation.
        candidates=[f for f in selected if f['year']==year]
        basis=candidates[0]['restatement']
        current={f['metric']:f for f in candidates if f['restatement']==basis}
        comparisons=[]
        for metric in ('revenue','pat','pbt','pbt_continuing','nii','operating_profit'):
            fact=current.get(metric)
            prior=next((f for f in selected if f['metric']==metric and f['year']==str(int(year)-1) and f['restatement']==basis),None)
            if not fact or not prior:continue
            try:change=growth(fact,prior)
            except (ValueError,ArithmeticError):continue
            comparisons.append({'metric':metric,'percent':change,'current':fact,'prior':prior,'formula':'100 × (current / prior − 1)'})
        bridge=None;conversion=None;ratios={}
        earnings=None
        components=('pbt_continuing','finance_cost','depreciation','other_income','revenue')
        if not financial and all(current.get(m,{}).get('crore') is not None for m in components) and decimal(current['revenue']['crore'])>0:
            proxy=decimal(current['pbt_continuing']['crore'])+decimal(current['finance_cost']['crore'])+decimal(current['depreciation']['crore'])-decimal(current['other_income']['crore'])
            earnings={'value':str(proxy),'margin_percent':str(proxy/decimal(current['revenue']['crore'])*100),
                'label':'EBITDA proxy · continuing operations, not reported EBITDA',
                'formula':'PBT from continuing operations + finance costs + depreciation/amortisation − other income; margin = proxy / revenue × 100',
                'operands':[current[m] for m in components]}
        required=('cfo','cfi','cff','fx','opening_cash','closing_cash')
        if all(current.get(m,{}).get('crore') is not None for m in required):
            values={m:decimal(current[m]['crore']) for m in required}
            computed=values['opening_cash']+values['cfo']+values['cfi']+values['cff']+values['fx']
            residual=values['closing_cash']-computed
            bridge={'computed_closing':str(computed),'reported_closing':str(values['closing_cash']),'residual':str(residual),
                'reconciled':abs(residual)<=Decimal('.01'),'operands':{m:current[m] for m in required},
                'formula':'Opening cash + operating + investing + financing cash flow + FX = closing cash'}
        if current.get('cfo',{}).get('crore') is not None and current.get('pat',{}).get('crore') is not None and decimal(current['pat']['crore'])>0:
            conversion={'value':str(decimal(current['cfo']['crore'])/decimal(current['pat']['crore'])),
                'operands':[current['cfo'],current['pat']],'formula':'Operating cash flow / profit for the year (including discontinued operations)'}
        if not financial:
            debt=('current_borrowings','noncurrent_borrowings','total_equity')
            if all(current.get(m,{}).get('crore') is not None for m in debt) and decimal(current['total_equity']['crore'])>0 and len({current[m]['period_end'] for m in debt})==1:
                ratios['debt_equity']={'value':str((decimal(current['current_borrowings']['crore'])+decimal(current['noncurrent_borrowings']['crore']))/decimal(current['total_equity']['crore'])),
                    'formula':'Current + non-current reported borrowings / closing total equity. Lease liabilities excluded; missing borrowing rows are not zero.',
                    'operands':[current[m] for m in debt]}
            previous={f['metric']:f for f in selected if f['year']==str(int(year)-1) and f['restatement']==basis and f['period_kind']=='instant'}
            required=('pbt','finance_cost','total_assets','current_liabilities')
            if all(current.get(m,{}).get('crore') is not None for m in required) and all(previous.get(m,{}).get('crore') is not None for m in ('total_assets','current_liabilities')):
                pbt=current['pbt'];start=datetime.fromisoformat(pbt['period_start']).date()
                opening=datetime.fromisoformat(previous['total_assets']['period_end']).date()
                average=(decimal(current['total_assets']['crore'])-decimal(current['current_liabilities']['crore'])+decimal(previous['total_assets']['crore'])-decimal(previous['current_liabilities']['crore']))/2
                if opening==start-timedelta(days=1) and average>0 and all(current[m]['period_end']==pbt['period_end'] for m in required):
                    ratios['roce']={'value':str((decimal(pbt['crore'])+decimal(current['finance_cost']['crore']))/average*100),
                        'formula':'100 × (total PBT + finance costs) / average opening and closing (total assets − current liabilities). This stated definition may differ from issuer-reported ROCE.',
                        'operands':[current[m] for m in required]+[previous[m] for m in ('total_assets','current_liabilities')]}
        buckets=[{'label':label,'facts':[current[m] for m in metrics if m in current],
                  'complete':False,'note':'Identified source rows only; unreported components are not zero.'}
                 for label,metrics in [('Capex',['capex']),('Acquisitions',['acquisitions']),('Shareholder returns',['dividends']),
                                      ('Debt repayment',['debt_repayment','lease_principal']),('Investments / other uses',['investments'])]]
        if financial:buckets=[] # Industrial cash-use buckets do not describe a lender's operating funding.
        summaries.append({'year':year,'scope':scope,'facts':list(current.values()),'growth':comparisons,'cash_bridge':bridge,
            'cash_conversion':conversion,'earnings_proxy':earnings,'cash_buckets':buckets,'ratios':ratios})
    return {'scope':scope if selected else 'unavailable','industry_schema':'financial' if financial else 'general','years':summaries,
        'coverage':'Recognised two-column annual statements only. Quarterly columns, unrecognised layouts and absent years remain gaps. Cash buckets are identified rows, not a reconciled gross-use allocation.'}


def compact(report):
    """One copy per fact and cited chunk, instead of duplicating PDF pages."""
    facts={};evidence={}
    def register(fact):
        key=hashlib.sha256(json.dumps([fact['symbol'],fact['metric'],fact['period_end'],fact['scope'],fact['restatement']]).encode()).hexdigest()[:24]
        if key not in facts:
            evidence[fact['evidence']['id']]=fact['evidence']
            headers=[]
            for header in fact['headers']:
                evidence[header['evidence']['id']]=header['evidence']
                headers.append({'quote':header['quote'],'evidence_id':header['evidence']['id']})
            facts[key]={k:v for k,v in fact.items() if k not in ('evidence','headers')}
            facts[key]['headers']=headers
        return key
    years=[]
    for year in report['years']:
        bridge=year['cash_bridge'];conversion=year['cash_conversion'];earnings=year['earnings_proxy']
        years.append({**year,'facts':[register(f) for f in year['facts']],
            'growth':[{**g,'current':register(g['current']),'prior':register(g['prior'])} for g in year['growth']],
            'cash_bridge':{**bridge,'operands':{k:register(f) for k,f in bridge['operands'].items()}} if bridge else None,
            'cash_conversion':{**conversion,'operands':[register(f) for f in conversion['operands']]} if conversion else None,
            'earnings_proxy':{**earnings,'operands':[register(f) for f in earnings['operands']]} if earnings else None,
            'ratios':{k:{**v,'operands':[register(f) for f in v['operands']]} for k,v in year.get('ratios',{}).items()},
            'cash_buckets':[{**b,'facts':[register(f) for f in b['facts']]} for b in year['cash_buckets']]})
    return {**report,'years':years,'facts':facts,'evidence':evidence}
