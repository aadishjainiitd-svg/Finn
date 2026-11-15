"""Conservative event identity and source-exact enrichment. Ambiguity stays separate."""
import hashlib
import json
import re
from calendar import monthrange
from datetime import datetime,timezone,timedelta

MONTHS={name.lower():i for i,name in enumerate(['','January','February','March','April','May','June','July','August','September','October','November','December']) if name}
MONTHS.update({k[:3]:v for k,v in list(MONTHS.items())})
DATE=r'(?P<day>\d{1,2})(?:st|nd|rd|th)?\s+(?P<month>January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[,\s]+(?P<year>20\d{2})'


def category(event):
    text=(event.get('description','')+' '+event.get('reason','')+' '+event.get('title','')).lower()
    if 'auditor' in text or 'audit concern' in text:return 'audit'
    if any(s in text for s in ('rating','credit, legal','regulatory development')):return 'credit'
    if any(s in text for s in ('director','management change','chief','appointment')):return 'management'
    if any(s in text for s in ('capital allocation','capital raising','capital spending plan','acquisition','merger')):return 'capital'
    if any(s in text for s in ('financial results','outcome of board meeting','earnings','con. call','conference call','transcript')):return 'results'
    return 'other'


def period_identity(text):
    ends=set()
    for m in re.finditer(r'(?:quarter|half.year|year)\s+ended\s+'+DATE,text,re.I):
        try:ends.add(datetime(int(m['year']),MONTHS[m['month'].lower()],int(m['day'])).date().isoformat())
        except ValueError:pass
    from .statements import DATE as MONTH_FIRST_DATE
    for m in re.finditer(r'(?:quarter|half.year|year)\s+ended\s+('+MONTH_FIRST_DATE+')',text,re.I):
        try:ends.add(datetime.strptime(m[1].replace(',',''),'%B %d %Y').date().isoformat())
        except ValueError:pass
    for m in re.finditer(r'\bQ([1-4])\s*FY\s*(\d{2}|20\d{2})\b',text,re.I):
        fy=int(m[2]);fy=2000+fy if fy<100 else fy;q=int(m[1]);month={1:6,2:9,3:12,4:3}[q];year=fy if q==4 else fy-1
        ends.add(datetime(year,month,monthrange(year,month)[1]).date().isoformat())
    return next(iter(ends)) if len(ends)==1 else None


def enrich(event,rows,meta):
    opening=' '.join(r['text'] for r in rows if r['page']<=2)[:5000]
    event={**event,'category':category(event)}
    from .results import extract
    results=extract(meta,rows)
    if results['tables'] or event['category']=='results':event['results']=results
    period=period_identity(opening)
    if event['category']=='results' and period:event['event_key']=event['symbol']+'-results-'+period;event['event_period']=period
    if event['category']=='management':
        profile=next((r for r in rows if re.search(r'brief profile|years? of experience|chartered accountant|holds a.{0,40}degree',r['text'],re.I)),None)
        if profile:event['management_profile']={'text':profile['text'],'evidence':{**meta,**dict(profile)},'label':'Issuer-supplied profile'}
    event['upcoming_dates']=schedule_dates(event,rows,meta)
    return event


def date_mentions(text):
    """Both explicit date orders; never assign a date to an ambiguous numeric form."""
    month_names='|'.join(sorted(MONTHS,key=len,reverse=True))
    month_first=r'(?P<month>'+month_names+r')\s+(?P<day>\d{1,2})(?:st|nd|rd|th)?[,\s]+(?P<year>20\d{2})'
    found=[]
    for pattern in (DATE,month_first):
        for m in re.finditer(pattern,text,re.I):
            try:day=datetime(int(m['year']),MONTHS[m['month'].lower()],int(m['day'])).date().isoformat()
            except ValueError:day=None
            found.append({'start':m.start(),'end':m.end(),'date':day})
    return sorted(found,key=lambda m:m['start'])


def schedule_dates(event,rows,meta):
    dates=[]
    for row in rows:
        text=row['text']
        # A dotted meridiem is not the end of the disclosure sentence. Keep
        # the following explicit timezone inside the original quoted context.
        boundaries=[b.start() for b in re.finditer(r'\.\s+',text)
                    if not re.search(r'\b[ap]\.m\.$',text[:b.start()+1],re.I)]
        for m in date_mentions(text):
            start=max((b+2 for b in boundaries if b<m['start']),default=0)
            end=min((b+1 for b in boundaries if b>=m['end']),default=len(text))
            context=text[start:end]
            mentions=date_mentions(context)
            if len(context)>1200 or not re.search(r'scheduled|will be held|to be held|record date|rescheduled|cancelled|canceled',context,re.I):continue
            if len(mentions)>2:continue
            values=[d['date'] for d in mentions]
            if not all(values):continue
            revised=len(mentions)==2 and re.search(r'rescheduled',context,re.I) and re.search(r'from\s*$',context[:mentions[0]['start']],re.I) and re.fullmatch(r'\s*(?:to|until)\s*',context[mentions[0]['end']:mentions[1]['start']],re.I)
            if len(mentions)!=1 and not revised:continue
            kind='record date' if 'record date' in context.lower() else 'call' if re.search(r'call|conference',context,re.I) else 'meeting'
            status='cancelled' if re.search(r'cancelled|canceled',context,re.I) else 'rescheduled' if revised else 'scheduled'
            clock=re.search(r'\b(1[0-2]|0?[1-9])[:.]([0-5]\d)\s*(a\.?m\.?|p\.?m\.?)\s*(?:\(\s*)?(IST|Indian Standard Time)\b',context,re.I)
            disclosed_time=(clock[1]+':'+clock[2]+' '+clock[3].replace('.','').upper()+' IST') if clock else 'Time not verified'
            for index,day in enumerate(values):
                dates.append({'date':day,'kind':kind,'status':'cancelled' if revised and index==0 else status,
                    'replacement_date':values[1] if revised and index==0 else None,
                    'symbol':event['symbol'],'event_id':event['id'],'time':disclosed_time,
                    'quote':context,'evidence':{**meta,**dict(row)}})
    return list({(d['date'],d['kind']):d for d in dates}.values())


def thread(events):
    groups={}
    for event in events:
        key=event.get('event_key') or event['id'];groups.setdefault(key,[]).append(event)
    result=[]
    for key,children in groups.items():
        if len(children)==1 and not children[0].get('event_key'):result.append(children[0]);continue
        children=sorted(children,key=lambda e:(e.get('published_at') or '',e['id']))
        lead=min(children,key=lambda e:(e['tier'],-e.get('score',0)))
        material=[e for e in children if e.get('assessment')!='routine'] or children
        revision=hashlib.sha256(json.dumps(sorted((e['id'],e['revision']) for e in material)).encode()).hexdigest()[:20]
        observations=[o for child in children for o in (child.get('thesis_assessment') or {}).get('observations',[])]
        from .theses import effect
        # The most important child can be an auditor notice or a later call.
        # Reuse the latest verified results child rather than losing its table
        # when a different disclosure leads the event. Its source IDs remain intact.
        result_child=next((e for e in reversed(children) if e.get('results',{}).get('tables')),None)
        result.append({**lead,'id':'event-'+hashlib.sha256(key.encode()).hexdigest()[:20],
            **({'results':result_child['results']} if result_child else {}),
            'thesis_assessment':{'observations':observations} if observations else None,
            'thesis_status':effect({'observations':observations}),
            'revision':revision,'children':children,'lead_filing_id':lead['id'],'published_at':children[-1]['published_at'],
            'title':lead['symbol']+' · results period ended '+lead.get('event_period',''),
            'description':str(len(children))+' related disclosures. Every source remains available.'})
    return result


def upcoming(events,at=None):
    today=(at or datetime.now(timezone.utc)).astimezone(timezone(timedelta(hours=5,minutes=30))).date().isoformat()
    dates={}
    for event in sorted(events,key=lambda e:e.get('published_at') or ''):
        for item in event.get('upcoming_dates',[]):
            if item['date']>=today:dates[(item['symbol'],item['date'],item['kind'])]=item
    return sorted(dates.values(),key=lambda d:(d['date'],d['symbol']))


def read_across(events,holdings):
    holdings={h['symbol']:h for h in holdings};result=[]
    for event in events:
        source=holdings.get(event['symbol'])
        if not source or event['tier']!=0 or not event.get('evidence'):continue
        for symbol,target in holdings.items():
            if symbol==event['symbol']:continue
            inputs=set(source.get('inputs',[]))&set(target.get('inputs',[]))
            sector=source.get('sector') and source.get('sector')==target.get('sector')
            if inputs or sector:result.append({'symbol':symbol,'source_symbol':event['symbol'],'event_id':event['id'],
                'label':'Read-across hypothesis','connection':'User-entered '+('shared inputs: '+', '.join(sorted(inputs)) if inputs else 'sector: '+source['sector']),
                'text':'This disclosure may warrant checking '+symbol+'. It does not establish an effect on that company.',
                'evidence':event['evidence'][:1]})
    return result
