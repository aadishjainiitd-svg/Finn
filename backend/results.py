"""Strict disclosed quarterly columns; no inferred units or annual/YTD mixing."""
import calendar,re
from datetime import datetime,timedelta
from .statements import DATE,page_text,ref
from .numbers import decimal,UNITS

POLICY='quarter-columns-v2'
CELL=r'(?:\(?-?(?:\d{1,3}(?:,\d{2})*,\d{3}|\d{1,3}(?:,\d{3})+|\d+)(?:\.\d{1,2})?\)?|[–—-])'
METRICS={
    'revenue':r'(?:Total )?Revenue from operations(?:\s*\(refer note \d+\))?',
    'pbt':r'Profit before tax(?:\s*\([^)]*\))?',
    'reported_ebitda':r'(?:Reported )?EBITDA(?! margin)',
    'pbt_continuing':r'Profit from continuing operations before tax(?:\s*\([^)]*\))?',
    'pat_continuing':r'Profit (?:for the period )?from continuing operations(?: after tax)?(?:\s*\([^)]*\))?',
    'pat':r'Profit for the period(?:\s*\([^)]*\))?',
    'other_income':r'Other income',
    'finance_cost':r'Finance costs?',
    'depreciation':r'Depreciation and amortisation expense',
    'nii':r'Net interest income',
    'operating_profit':r'Operating profit before provisions(?: and contingencies)?',
}


def date_value(text):return datetime.strptime(text.replace(',',''),'%B %d %Y').date()


MONTH=r'(?:January|February|March|April|May|June|July|August|September|October|November|December)'
LONG_DATE=r'(?:'+MONTH+r'\s+\d{1,2},?\s+20\d{2}|\d{1,2}(?:st|nd|rd|th)?\s+'+MONTH+r',?\s+20\d{2})'
SEBI_TITLE=re.compile(r'Statement of (?:Unaudited |Audited |Reviewed )?(Consolidated|Standalone) (?:Unaudited |Audited |Reviewed )?(?:Financial )?Results for the Quarter and (Half[- ]?Year|Six Months|Nine Months) Ended\s+('+LONG_DATE+')',re.I)
SEBI_DATE=r'\d{2}-(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-\d{2}|\d{2}[-.]\d{2}[-.]20\d{2}'


def sebi_date(text):
    """Exact printed date to a date, or None. No correction of damaged text."""
    cleaned=re.sub(r'(\d)(?:st|nd|rd|th)\b',r'\1',text.replace(',','')).strip()
    for fmt in ('%d-%b-%y','%d-%m-%Y','%d.%m.%Y','%B %d %Y','%d %B %Y'):
        try:return datetime.strptime(cleaned,fmt).date()
        except ValueError:pass
    return None


def quarter_start(end):
    month=end.month-2
    return end.replace(month=month,day=1) if month>0 else end.replace(year=end.year-1,month=month+12,day=1)


def comparable_facts(tables):
    """Typed, cited quarterly actuals; derived EBITDA is never a reported fact."""
    facts=[]
    for table in tables:
        for item in table['items']:
            if item['metric'] not in ('revenue','pat','pbt','nii','operating_profit'):continue
            for i,value in enumerate(item['values']):
                if value is None:continue
                evidence=item['evidence']
                facts.append({'symbol':evidence['symbol'],'metric':item['metric'],'scope':table['scope'],
                    'currency':'INR','unit':'crore','value':value,'period_kind':'quarter',
                    'period_start':table['period_starts'][i],'period_end':table['periods'][i],
                    'evidence_id':evidence['id'],'evidence':evidence,'quote':item['quote'],
                    'headers':table['headers'],'restatement':'as presented in this version'})
    return facts


def extract(doc,rows):
    pages={};tables=[];gaps=[]
    from .documents import filing_exclusion
    if filing_exclusion(doc,' '.join(r['text'] for r in rows if r['page']==1)) or re.search(r'newspaper|publication',doc.get('title',''),re.I):
        return {'policy':POLICY,'tables':[],'gaps':['Referenced or newspaper extracts require issuer/table boundary verification. Use the original results filing.']}
    for row in rows:pages.setdefault(row['page'],[]).append(row)
    for page,parts in pages.items():
        text=page_text(parts)
        title=re.search(r'Statement of (Consolidated|Standalone) (?:Unaudited |Audited )?(?:Financial )?Results for the Quarter[^.]{0,100}?Ended\s+('+DATE+')',text,re.I)
        # The labelled three-quarter profile needs its own "quarter ended <date>"
        # labels; otherwise the SEBI six-date profile below may apply.
        if title and (re.search(r'quarter ended\s+'+DATE,text[title.end():],re.I) or not SEBI_TITLE.search(text)):
            scope=title[1].lower();header=text[title.end():]
            marker=re.search(r'(?:Continuing operations|Revenue from operations|Interest earned)',header,re.I)
            if not marker:gaps.append(f'Page {page}: column/header boundary unverified.');continue
            header=header[:marker.start()]
            unit=re.search(r'(₹|INR|Rs\.?)\s*(?:in\s+)?(crores?|lakhs?|millions?)\b',header,re.I)
            if not unit:gaps.append(f'Page {page}: currency/unit header could not be verified; no numbers inferred.');continue
            labels=list(re.finditer(r'(?:(?:Preceding|Corresponding)\s+)?quarter ended\s+('+DATE+')',header,re.I))
            dates=list(re.finditer(DATE,header,re.I))
            try:ends=[date_value(m[1]) for m in labels]
            except ValueError:continue
            if len(labels)!=3 or len(dates) not in (3,5,6):gaps.append(f'Page {page}: ambiguous quarterly columns.');continue
            try:
                if ends[0]!=date_value(title[2]):continue
            except ValueError:continue
            count=len(dates);header_quotes=[title[0],unit[0],*(m[0] for m in labels)]
        elif sebi:=SEBI_TITLE.search(text):
            # SEBI half-year / nine-month profile: "Quarter ended | Half year (or
            # Six/Nine months) ended | Year ended" over six explicit dates. Dates are
            # parsed exactly as printed; OCR-damaged dates or units fail closed.
            scope=sebi[1].lower();header=text[sebi.end():]
            marker=re.search(r'Revenue from operations|Interest earned',header,re.I)
            if not marker:gaps.append(f'Page {page}: column/header boundary unverified.');continue
            header=header[:marker.start()]
            if not (re.search(r'(?:Quarter|3 months|Three months) ended',header,re.I) and re.search(r'(?:Half[- ]?year|Six months|6 months|Nine months|9 months) ended',header,re.I) and re.search(r'Year ended',header,re.I)):
                gaps.append(f'Page {page}: quarter/year-to-date/year column groups unverified.');continue
            unit=re.search(r'(₹|INR|Rs\.?)\s*(?:in\s+)?(crores?|lakhs?|millions?)\b',header,re.I)
            if not unit:gaps.append(f'Page {page}: currency/unit header could not be verified; no numbers inferred.');continue
            # A lone extracted column rule (| or I) may sit between dates; no digit is altered.
            columns=re.search(r'('+SEBI_DATE+r')(?:\s+(?:[|I]\s+)?(?:\(?(?:Un-?audited|Audited|Reviewed)\)?\s+)*('+SEBI_DATE+r')){5}',header,re.I)
            tokens=re.findall(SEBI_DATE,columns[0],re.I) if columns else []
            all_ends=[sebi_date(t) for t in tokens]
            if len(all_ends)!=6 or None in all_ends:gaps.append(f'Page {page}: six printed column dates could not be verified.');continue
            ends=all_ends[:3]
            if sebi_date(sebi[3])!=ends[0] or all_ends[3]!=ends[0] or all_ends[4]!=ends[2]:
                gaps.append(f'Page {page}: column dates do not match the statement period.');continue
            span=(ends[0]-all_ends[5]).days
            nine=bool(re.search(r'nine|9 months',sebi[2]+header,re.I))
            if not ((260<=span<=280) if nine else (170<=span<=185)):
                gaps.append(f'Page {page}: year column does not match the reporting calendar.');continue
            count=6;header_quotes=[sebi[0],unit[0],columns[0]]
        else:
            # Explicit six-column profile: month/day cells and their year row
            # are separated in PDF content order. Never infer years by position
            # without the six disclosed years and 3/6/12-month grouping labels.
            title=re.search(r'Audited (Consolidated|Standalone) Interim Statement of Financial Results',text,re.I)
            if not title:continue
            scope=title[1].lower()
            if not re.search(r'Three months ended\s+Six months ended',text,re.I) or not re.search(r'Year ended',text,re.I):continue
            unit=re.search(r'(₹|INR|Rs\.?)\s*(?:in\s+)?(crores?|lakhs?|millions?)\b',text,re.I)
            if not unit:gaps.append(f'Page {page}: currency/unit header could not be verified; no numbers inferred.');continue
            day=r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?'
            split=re.search('('+day+r'(?:\s+'+day+r'){5})\s+((?:20\d{2}\s+){5}20\d{2})(?!\d)',text,re.I)
            if not split:gaps.append(f'Page {page}: split date/year columns could not be verified.');continue
            try:all_ends=[date_value(d.rstrip(',')+' '+y) for d,y in zip(re.findall(day,split[1],re.I),re.findall(r'20\d{2}',split[2]))]
            except ValueError:continue
            ends=all_ends[:3]
            if all_ends[3]!=ends[0] or all_ends[4]!=ends[2] or not 170<=(ends[0]-all_ends[5]).days<=185:continue
            count=6;header_quotes=[title[0],unit[0],split[0],split[0],split[0]]
        try:
            if not all(e.month in (3,6,9,12) and e.day==calendar.monthrange(e.year,e.month)[1] for e in ends):continue
            if ends[1]!=(quarter_start(ends[0])-timedelta(days=1)) or ends[2]!=ends[0].replace(year=ends[0].year-1):continue
        except ValueError:continue
        unit_name=unit[2].lower().rstrip('s')
        headers=[ref(doc,parts,q) for q in header_quotes]
        if not all(headers):gaps.append(f'Page {page}: header crosses unavailable citation boundaries.');continue
        metrics={};conflicts=set()
        for metric,pattern in METRICS.items():
            regex=r'(?<!\w)('+pattern+r')\s+('+CELL+r'(?:\s+'+CELL+r'){'+str(count-1)+r'})(?![\d.,])'
            for match in re.finditer(regex,text,re.I):
                following=text[match.end():]
                # Another numeric cell means more columns than verified; a lone 1-2
                # digit serial followed by the next row label is a row number.
                if re.match(r'\s+'+CELL+r'(?:\s|$)',following) and not re.match(r'\s+\d{1,2}\s+[A-Za-z(]',following):continue
                source=ref(doc,parts,match[0])
                if not source:continue
                cells=re.findall(CELL,match[2]);values=[]
                for cell in cells[:3]:
                    values.append(None if cell in ('-','–','—') else str(decimal(cell.replace(',','').replace('(','-').replace(')',''))*UNITS[unit_name]/UNITS['crore']))
                if metric in metrics and metrics[metric]['values']!=values:conflicts.add(metric)
                metrics[metric]={'label':match[1],'values':values,**source}
        for key in conflicts:metrics.pop(key,None)
        if not metrics:gaps.append(f'Page {page}: no unambiguous supported numeric rows.');continue
        financial=bool('nii' in metrics or re.search(r'Interest earned|Interest expended',text,re.I))
        pbt='pbt_continuing' if 'pbt_continuing' in metrics else 'pbt'
        names=['nii','operating_profit',pbt,'pat'] if financial else ['revenue','reported_ebitda',pbt,'pat']
        if 'pat' not in metrics:names[-1]='pat_continuing'
        items=[]
        for metric in names:
            row=metrics.get(metric)
            if not row:continue
            current,prior,year=row['values'];changes={}
            for label,base in [('qoq',prior),('yoy',year)]:
                changes[label]=str((decimal(current)/decimal(base)-1)*100) if current is not None and base is not None and decimal(base)>0 else None
            items.append({'metric':metric,**row,**changes})
        if not financial and 'reported_ebitda' not in metrics:
            components=[pbt,'finance_cost','depreciation','other_income']
            if not re.search(r'discontinued operations',text,re.I) and all(m in metrics and all(v is not None for v in metrics[m]['values']) for m in components):
                values=[str(sum(decimal(metrics[m]['values'][i])*(-1 if m=='other_income' else 1) for m in components)) for i in range(3)]
                items.insert(1,{'metric':'ebitda_proxy','label':'EBITDA proxy'+(' · continuing operations' if pbt=='pbt_continuing' else ''),'values':values,
                    'qoq':str((decimal(values[0])/decimal(values[1])-1)*100) if decimal(values[1])>0 else None,
                    'yoy':str((decimal(values[0])/decimal(values[2])-1)*100) if decimal(values[2])>0 else None,
                    'formula':('Continuing-operations PBT' if pbt=='pbt_continuing' else 'PBT')+' + finance costs + depreciation/amortisation − other income',
                    'operands':[metrics[m] for m in components]})
        tables.append({'scope':scope,'industry_schema':'financial' if financial else 'general','page':page,
            'periods':[e.isoformat() for e in ends],'period_starts':[quarter_start(e).isoformat() for e in ends],
            'unit':'₹ crore','reported_unit':unit_name,'headers':headers,'items':items,
            'comparison_basis':'Same issuer, scope and source version; current, preceding and corresponding quarters as presented. YTD/annual columns excluded.'})
    consolidated=[t for t in tables if t['scope']=='consolidated']
    selected=consolidated or tables
    return {'policy':POLICY,'tables':selected,'gaps':gaps or ([] if selected else ['No verified quarterly statement layout was found.'])}
