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
DAY_FIRST=r'\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December),?\s+20\d{2}'
ANY_DATE='(?:'+DATE+'|'+DAY_FIRST+')'
CELL=r'(?:\(?-?\d[\d,]*\.\d{2}\)?|[–—-])'
WHOLE=r'(?:\(?-?\d{1,3}(?:,\d{2,3})+\)?|\(?-?\d{1,6}\)?|[–—-])'
# Note references: 24, 3(A), 10(a); decimal-style pages may also print 23.8.
NOTE={'decimal':r'(?:\d{1,2}(?:\.\d|\s?\([a-zA-Z]{1,3}\))?\s+)?','whole':r'(?:\d{1,2}(?:\s?\([a-zA-Z]{1,3}\))?\s+)?'}
# Row markers such as (A), [B], (V-VI) or (A+B+C) printed after a total label.
SUFFIX=r'(?:\s*[\[(]?(?:[IVX]{1,5}|[A-D])(?:\s*[-+]\s*(?:[IVX]{1,5}|[A-D]))*[\])]?(?=\s))?'
NOTE_REF=r'\s*\((?:refer )?notes?(?: no\.?)? ?[\dA-Za-z(). ,]{1,15}\)'
FILLER=r"(?:[A-Za-z ,\-&/'’]{0,90}?)(?:\s*\([A-Za-z ,\-&/'’]{2,80}\))?(?:"+NOTE_REF+')?'


def FLOW(activity):
    return (r'Net cash(?: flows?| inflows?| outflows?)?(?:\s*(?:\(used in\)|\(used\)|generated|provided|used|from|by|in|/))*\s+'
            +activity+' activities'+'(?:'+NOTE_REF+')?')


INCOME={
 'revenue':r'Revenue from operations',
 'other_income':r'Other income',
 'finance_cost':r'Finance costs?',
 'depreciation':r'Depreciation and amorti[sz]ation expenses?',
 'pbt_continuing':r'Profit from continuing operations before tax|Profit before tax from continuing operations',
 'pbt':r'Profit before tax(?! from| and)',
 'pat_continuing':r'Profit from continuing operations after tax',
 'pat':r'Profit for the year(?! from)',
 'nii':r'Net interest income',
 'operating_profit':r'Operating profit before provisions(?: and contingencies)?',
 'interest_earned':r'Interest earned',
 'interest_expended':r'Interest expended',
}
CASH={
 'cfo':FLOW('operating'),
 'cfi':FLOW('investing'),
 'cff':FLOW('financing'),
 'capex':r'(?:Payments? for (?:(?:purchase|acquisition)s? of )?|(?:purchase|acquisition)s? of )property, plant and equipment'+FILLER,
 'acquisitions':r'(?:Payments? for )?Acquisition of (?:a )?subsidiar(?:y|ies)'+FILLER,
 'dividends':r'Dividends? paid'+FILLER,
 'lease_principal':r'(?:Payment|Repayment)s? of (?:principal portion of )?lease liabilities'+FILLER+r'|Principal (?:payment|repayment)s? of lease liabilities'+FILLER,
 'debt_repayment':r'Repayment of (?:long[- ]term |short[- ]term |non-current |current )?borrowings'+FILLER,
 'investments':r'Investment in bank deposits \(with maturity more than three months\)',
 'fx':r'Effects? of exchange \(loss\) / gain on cash and cash equivalents|Effects? of exchange differences on (?:restatement of foreign currency |translation of foreign currency )?cash and cash equivalents'+FILLER+r'|Exchange differences? on translation of foreign currency cash and cash equivalents|Effects? of (?:foreign )?exchange rate changes on cash and cash equivalents'+FILLER,
 'opening_cash':r'Cash and cash equivalents (?:\(opening balance\)|at (?:the )?beginning of the (?:year|period))'+FILLER,
 'closing_cash':r'Cash and cash equivalents (?:\(closing balance\)|at (?:the )?end of the (?:year|period))'+FILLER,
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
TITLE=re.compile(r'(?:\b(consolidated|standalone)\s+)?\b(statement of profit and loss|balance sheet|statement of cash ?flows?|cash flow statement)\b',re.I)
UNIT=re.compile(r'\((?:all )?(?:amounts? )?(?:are )?(?:in\s+)?(Indian Rupees|[^\s()]{1,6})\s*(?:in\s+)?(crores?|lakhs?|millions?)\b[^()]{0,60}\)',re.I)
DECLARATION=re.compile(r'(?:the\s+)?(?:(consolidated|standalone)\s+)?financial statements (?:are|have been) presented in (?:INR|Indian (?:National currency )?Rupees?|₹)(?:[^.]{0,60}?\bin (crores?|lakhs?|millions?))?',re.I)
RUPEE=('₹','inr','rs.','rs','indian rupees')
# A report may print the rupee sign as another glyph and say so, e.g.
# "prepared in Indian Rupee (H)". Only that same-document mapping is trusted.
GLYPH=re.compile(r'(?:(consolidated|standalone)\s+)?(?:financial statements (?:are|have been) (?:presented|prepared) in|functional currency of the Company[^.]{0,60}? is(?: the)?) Indian Rupees? \((\S)\)',re.I)
LATE_TITLE=re.compile(r'\b(consolidated|standalone)\s+(statement of profit and loss|balance sheet|statement of cash ?flows?)\s+(?:for the year ended|as at)\s+'+ANY_DATE,re.I)


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


def parse_date(value):
    value=re.sub(r'(?<=\d)(?:st|nd|rd|th)','',value.replace(',',''))
    value=re.sub(r'\s+',' ',value).strip()
    for pattern in ('%B %d %Y','%d %B %Y'):
        try:return datetime.strptime(value,pattern).date()
        except ValueError:pass
    return None


def annual_dates(text):
    candidates=re.findall(DATE,text[:500],re.I)
    dates=[]
    for candidate in candidates:
        try:value=datetime.strptime(candidate.replace(',',''),'%B %d %Y').date()
        except ValueError:return None
        if value not in dates:dates.append(value)
    if len(dates)!=2 or dates[0].year-dates[1].year!=1 or (dates[0].month,dates[0].day)!=(dates[1].month,dates[1].day):return None
    return dates


def prior_year(end):
    return end.replace(year=end.year-1,day=min(end.day,calendar.monthrange(end.year-1,end.month)[1]))


def column_dates(window,late_title=None):
    """Two printed period columns one year apart, or a dated title plus 'YYYY YYYY-1' columns."""
    stated=re.search(r'(?:for the year ended|year ended|as at)\s+('+ANY_DATE+')',late_title or window,re.I)
    title_date=parse_date(stated[1]) if stated else None
    if stated and not title_date:return None
    if late_title:stated=None
    quotes=[];dates=[]
    for m in re.finditer(ANY_DATE,window,re.I):
        value=parse_date(m[0])
        if value is None:return None
        if value not in dates:dates.append(value);quotes.append(m[0])
    if len(dates)==2:
        if dates[0].year-dates[1].year!=1 or (dates[0].month,dates[0].day)!=(dates[1].month,dates[1].day):return None
        if title_date and title_date!=dates[0]:return None
        return dates,quotes
    if title_date and stated and dates==[title_date]:
        years=re.search(r'(?<![\d,.])('+str(title_date.year)+r')\s+('+str(title_date.year-1)+r')(?![\d,.])',window[stated.end():])
        if years:return [title_date,prior_year(title_date)],[stated[0],years[0]]
    return None


def extract(doc,rows):
    pages={}
    for row in rows:pages.setdefault(row['page'],[]).append(row)
    facts=[]
    declarations={};glyphs={}
    for row in rows:
        for m in DECLARATION.finditer(row['text']):
            declarations.setdefault((m[1] or '').lower(),((m[2] or '').lower().rstrip('s') or None,ref(doc,[row],m[0])))
        for m in GLYPH.finditer(row['text']):
            glyphs.setdefault(((m[1] or '').lower(),m[2]),ref(doc,[row],m[0]))
    texts={page:page_text(parts) for page,parts in pages.items()}
    labelled_consolidated=any(re.search(r'\bconsolidated\s+(?:statement of profit and loss|balance sheet|statement of cash ?flows?)',t[:400],re.I) for t in texts.values())
    for page,parts in pages.items():
        text=texts[page]
        title=TITLE.search(text[:400]);late=None
        if not title:
            # Some layouts print the dated title under the table; the period
            # columns and unit then sit at the top of the page.
            title=late=LATE_TITLE.search(text)
            if not title:continue
        name=title[2].lower()
        kind='income' if 'profit' in name else 'balance' if 'balance' in name else 'cash'
        if title[1]:
            scope=title[1].lower();scope_basis='Labelled on the statement page'
        else:
            # Unlabelled statements are standalone only when nothing on the page
            # says otherwise; a consolidated running header makes them ambiguous.
            if re.search(r'consolidated',text[:title.end()+200],re.I):continue
            scope='standalone'
            scope_basis=('Unlabelled statement; this report labels its consolidated statements separately' if labelled_consolidated
                         else 'Only set of statements in this report (no consolidated statements presented)')
        window=text[:450] if late else text[title.start():title.start()+450]
        found=column_dates(window,late[0] if late else None)
        if not found:continue
        dates,date_quotes=found
        units=UNIT.search(window)
        if not units:continue
        unit=units[2].lower().rstrip('s');currency=units[1].strip().lower()
        currency_source=None
        if currency not in RUPEE:
            # Broken rupee glyphs are common. Resolve only through an explicit
            # same-scope (or scope-free) INR presentation declaration.
            glyph=glyphs.get((scope,units[1].strip())) or glyphs.get(('',units[1].strip()))
            declared=declarations.get(scope) or declarations.get('')
            if len(currency)!=1:continue
            if glyph:currency_source=glyph
            elif declared and (not declared[0] or declared[0]==unit):currency_source=declared[1]
            else:continue
        headers=[ref(doc,parts,title[0]),ref(doc,parts,units[0])]+[ref(doc,parts,q) for q in date_quotes]
        if currency_source:headers.append(currency_source)
        if not all(headers):continue
        decimals=len(re.findall(r'\d\.\d{2}(?!\d)',text));grouped=len(re.findall(r'\d{1,3}(?:,\d{2,3})+(?!\d)',text))
        style='decimal' if decimals*2>=grouped and decimals>=4 else 'whole'
        cell=CELL if style=='decimal' else WHOLE
        for metric,pattern in (INCOME if kind=='income' else BALANCE if kind=='balance' else CASH).items():
            search_text=text
            if metric in ('current_borrowings','noncurrent_borrowings'):
                label='Non-current liabilities' if metric=='noncurrent_borrowings' else 'Current liabilities'
                block=re.search(r'(?<![\w-])'+label+r'(.*?)Total '+label,text,re.I|re.S)
                if not block:continue
                search_text=block[1]
            regex=r'(?<!\w)((?:'+pattern+r'))'+SUFFIX+r'\s+'+NOTE[style]+r'('+cell+r')\s+('+cell+r')(?![\d.,])'
            for m in re.finditer(regex,search_text,re.I):
                if re.match(r'\s+'+cell+r'(?:\s|$)',search_text[m.end():]):continue
                citation=ref(doc,parts,m[0])
                if not citation:continue
                for end,raw in zip(dates,(m[2],m[3])):
                    value=None if raw in ('–','—','-') else decimal(raw.replace(',','').replace('(','-').replace(')',''))
                    facts.append({'symbol':doc['symbol'],'metric':metric,'reported_label':m[1].strip(),
                        'year':str(end.year),'value':str(value) if value is not None else None,
                        'crore':str(value*UNITS[unit]/UNITS['crore']) if value is not None else None,
                        'currency':'INR','unit':unit,'scope':scope,'scope_basis':scope_basis,'period_kind':'instant' if kind=='balance' else 'annual','statement':kind,
                        'period_start':end.isoformat() if kind=='balance' else (prior_year(end)+timedelta(days=1)).isoformat(),'period_end':end.isoformat(),
                        'restatement':'as_presented_in_'+doc['version'],'evidence_id':citation['evidence']['id'],
                        **citation,'headers':headers,'qualification':'Comparative values as presented in the same statement; continuing/discontinued labels retained.'})
    distinct={}
    conflicts=set()
    for fact in facts:
        key=(fact['metric'],fact['period_end'],fact['scope'])
        if key in distinct and distinct[key]['value']!=fact['value']:conflicts.add(key)
        else:distinct.setdefault(key,fact)
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
        ends=report_ends(selected)
        basis=max(candidates,key=lambda f:ends[f['restatement']])['restatement']
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
        'trajectory':trajectory(facts,financial),
        'coverage':'Recognised two-column annual statements only. Quarterly columns, unrecognised layouts and absent years remain gaps. Cash buckets are identified rows, not a reconciled gross-use allocation.'}


def report_ends(facts):
    """Each source version's own latest period: the newest presentation wins."""
    ends={}
    for f in facts:ends[f['restatement']]=max(ends.get(f['restatement'],''),f['period_end'])
    return ends


def trajectory(facts,financial=False,span=5):
    """Up to five comparable fiscal years, each value from the newest report presenting it.

    Years are never interpolated. A year presented differently by an older report
    is marked restated with both cited values. Growth uses only a pair printed in
    the same statement. A change of year-end breaks the series.
    """
    annual=[f for f in facts if f['period_kind']=='annual' and f['value'] is not None]
    if not annual:return None
    counts={s:len({f['period_end'] for f in annual if f['scope']==s and f['metric']=='revenue'}) for s in ('consolidated','standalone')}
    scope=max(counts,key=lambda s:(counts[s],s=='consolidated'))
    if not counts[scope]:return None
    ends=report_ends(facts)
    selected=[f for f in annual if f['scope']==scope]
    periods=sorted({f['period_end'] for f in selected if f['metric']=='revenue'},reverse=True)
    month_day=periods[0][5:]
    series=[];notes=[]
    for end in periods:
        if end[5:]!=month_day:
            notes.append(f'Year-end changed before {series[-1]["period_end"] if series else end}; earlier years are not comparable and are excluded.');break
        series.append({'period_end':end})
    newest=int(periods[0][:4])
    window=[str(newest-i) for i in range(span)]
    present={s['period_end'][:4]:s['period_end'] for s in series}
    def pick(metric,end):
        candidates=sorted((f for f in selected if f['metric']==metric and f['period_end']==end),key=lambda f:ends[f['restatement']],reverse=True)
        if not candidates:return None,None
        chosen=candidates[0]
        other=next((f for f in candidates[1:] if decimal(f['value'])!=decimal(chosen['value'])),None)
        return chosen,other
    def comparable(metric,current):
        # Growth comes from the report in which this year is the current column,
        # so both numbers sit in one statement.
        current=next((f for f in selected if f['metric']==metric and f['period_end']==current['period_end'] and ends[f['restatement']]==current['period_end']),current)
        prior_end=prior_year(datetime.fromisoformat(current['period_end']).date()).isoformat()
        prior=next((f for f in selected if f['metric']==metric and f['period_end']==prior_end and f['restatement']==current['restatement']),None)
        if not prior:return None
        try:return {'percent':growth(current,prior),'current':current,'prior':prior,'formula':'100 × (current / prior − 1), both from the same statement'}
        except (ValueError,ArithmeticError):return None
    years=[]
    for label in window:
        end=present.get(label)
        if not end:
            years.append({'fiscal_year':label,'period_end':None,'gap':True,'values':{},'restated':{},'growth':{},'derived':{}});continue
        values={};restated={}
        for metric in ('revenue','nii','pbt','pbt_continuing','pat','cfo','cfi','cff','capex','acquisitions','dividends','debt_repayment','lease_principal','fx','opening_cash','closing_cash','finance_cost','depreciation','other_income'):
            chosen,other=pick(metric,end)
            if chosen:values[metric]=chosen
            if other:restated[metric]={'newer':chosen,'older':other}
        changes={m:g for m in ('revenue','pat','cfo') if m in values and (g:=comparable(m,values[m]))}
        derived={}
        revenue=values.get('revenue')
        pbt_key='pbt_continuing' if 'pbt_continuing' in values else 'pbt'
        operands=[values.get(m) for m in (pbt_key,'finance_cost','depreciation','other_income')]
        if not financial and revenue and decimal(revenue['crore'])>0 and all(operands) and len({revenue['restatement'],*[o['restatement'] for o in operands]})==1:
            proxy=decimal(operands[0]['crore'])+decimal(operands[1]['crore'])+decimal(operands[2]['crore'])-decimal(operands[3]['crore'])
            derived['ebitda_margin']={'value':str(proxy/decimal(revenue['crore'])*100),'operands':[*operands,revenue],
                'label':'EBITDA proxy margin'+(' · continuing operations' if pbt_key=='pbt_continuing' else ''),
                'formula':('PBT from continuing operations' if pbt_key=='pbt_continuing' else 'PBT')+' + finance costs + depreciation/amortisation − other income, ÷ revenue × 100. Not reported EBITDA.'}
        if values.get('cfo') and values.get('pat') and decimal(values['pat']['crore'])>0 and values['cfo']['restatement']==values['pat']['restatement']:
            derived['cash_conversion']={'value':str(decimal(values['cfo']['crore'])/decimal(values['pat']['crore'])),'operands':[values['cfo'],values['pat']],
                'formula':'Operating cash flow ÷ profit for the year'}
        # Working-capital days: closing balance ÷ the same year's revenue, from one report.
        if not financial and revenue and decimal(revenue['crore'])>0:
            for metric,key,name in (('receivables','receivable_days','Receivable days'),('inventories','inventory_days','Inventory days')):
                balance=next((f for f in facts if f['metric']==metric and f['period_kind']=='instant' and f['scope']==scope and f['period_end']==end
                              and f['restatement']==revenue['restatement'] and f['value'] is not None),None)
                if balance:
                    derived[key]={'value':str(decimal(balance['crore'])/decimal(revenue['crore'])*365),'operands':[balance,revenue],'label':name,
                                  'formula':f'Closing {metric} ÷ revenue × 365, both from the same report. Year-end balance, not an average.'}
        years.append({'fiscal_year':label,'period_end':end,'gap':False,'values':values,'restated':restated,'growth':changes,'derived':derived})
    years.reverse()
    allocation=None if financial else cash_allocation(years)
    gaps=[y['fiscal_year'] for y in years if y['gap']]
    used=[f for y in years for f in y['values'].values()]
    basis=sorted({f.get('scope_basis') for f in used if f.get('scope_basis')})
    return {'scope':scope,'scope_basis':basis,'year_end':month_day,'years':years,'allocation':allocation,'notes':notes,
            'complete':not gaps,'gaps':gaps,
            'coverage':(f'{span-len(gaps)} of {span} fiscal years read from primary statements.'+(' Missing: '+', '.join(gaps)+'. Older annual reports may supply them.' if gaps else ''))}


BUCKETS=[('Capex',('capex',)),('Acquisitions',('acquisitions',)),('Dividends',('dividends',)),('Debt and lease repayment',('debt_repayment','lease_principal'))]


def cash_allocation(years):
    """Where operating cash went, by year and in total, reconciled to reported totals.

    Named rows are cited outflows. 'Other investing and financing' is the exact
    remainder of reported investing + financing cash flow after named rows, so
    the buckets plus the change in cash always equal operating cash flow; each
    year is then checked against reported opening and closing cash.
    """
    rows=[];excluded=[]
    for year in years:
        if year['gap']:continue
        v=year['values']
        required=[v.get(m) for m in ('cfo','cfi','cff')]
        if not all(required) or len({f['restatement'] for f in required})!=1:
            excluded.append(year['fiscal_year']);continue
        basis=required[0]['restatement']
        cfo,cfi,cff=(decimal(f['crore']) for f in required)
        uses=[];named=Decimal(0)
        for label,metrics in BUCKETS:
            parts=[v[m] for m in metrics if m in v and v[m]['restatement']==basis]
            amount=-sum((decimal(f['crore']) for f in parts),Decimal(0))
            named-=amount
            uses.append({'label':label,'value':str(amount),'facts':parts,'reported':bool(parts)})
        other=-(cfi+cff-named)
        net_change=cfo+cfi+cff
        uses.append({'label':'Other investing and financing (net)','value':str(other),'facts':[v['cfi'],v['cff']],'reported':True,'residual':True})
        check=None
        if all(m in v and v[m]['restatement']==basis for m in ('opening_cash','closing_cash')):
            fx=decimal(v['fx']['crore']) if 'fx' in v and v['fx']['restatement']==basis else Decimal(0)
            computed=decimal(v['opening_cash']['crore'])+net_change+fx
            residual=decimal(v['closing_cash']['crore'])-computed
            check={'reconciled':abs(residual)<=Decimal('0.05'),'residual':str(residual),'fx_row':'fx' in v,
                   'operands':[v[m] for m in ('opening_cash','closing_cash','fx') if m in v and v[m]['restatement']==basis]}
        rows.append({'fiscal_year':year['fiscal_year'],'cfo':str(cfo),'cfo_fact':v['cfo'],'uses':uses,'net_change':str(net_change),'check':check})
    if not rows:return None
    total_cfo=sum((decimal(r['cfo']) for r in rows),Decimal(0))
    totals=[]
    for i,(label,_) in enumerate([*BUCKETS,('Other investing and financing (net)',())]):
        amount=sum((decimal(r['uses'][i]['value']) for r in rows),Decimal(0))
        totals.append({'label':label,'value':str(amount),'share_of_cfo':str(amount/total_cfo*100) if total_cfo>0 else None,
                       'years_with_row':sum(r['uses'][i]['reported'] for r in rows)})
    net=sum((decimal(r['net_change']) for r in rows),Decimal(0))
    return {'years':rows,'totals':totals,'total_cfo':str(total_cfo),'net_change':str(net),
            'net_change_share':str(net/total_cfo*100) if total_cfo>0 else None,'excluded':excluded,
            'reconciled_years':sum(bool(r['check'] and r['check']['reconciled']) for r in rows),
            'checked_years':sum(r['check'] is not None for r in rows),
            'formula':'Operating cash = capex + acquisitions + dividends + debt/lease repayment + other investing and financing (net) + increase in cash. Outflows shown positive.'}


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
    path=report.get('trajectory')
    if path:
        path={**path,'years':[{**y,'values':{m:register(f) for m,f in y['values'].items()},
            'restated':{m:{'newer':register(r['newer']),'older':register(r['older'])} for m,r in y['restated'].items()},
            'growth':{m:{**g,'current':register(g['current']),'prior':register(g['prior'])} for m,g in y['growth'].items()},
            'derived':{k:{**d,'operands':[register(f) for f in d['operands']]} for k,d in y['derived'].items()}} for y in path['years']]}
        if path['allocation']:
            a=path['allocation']
            path['allocation']={**a,'years':[{**r,'cfo_fact':register(r['cfo_fact']),
                'uses':[{**u,'facts':[register(f) for f in u['facts']]} for u in r['uses']],
                'check':{**r['check'],'operands':[register(f) for f in r['check']['operands']]} if r['check'] else None} for r in a['years']]}
    return {**report,'years':years,'trajectory':path,'facts':facts,'evidence':evidence}
