"""Every fetched filing stays accounted for. Only positively assessed routine items collapse."""
import asyncio
import hashlib
import json
import re
from datetime import datetime,timezone
from . import research,store,events as event_tools
from .config import PORTFOLIO
from .sources import filings,price,identity,now
from .documents import ingest
from .numbers import daily_signal,IST
from .network import SourceError

refresh_lock=asyncio.Lock()
assessment_task=None
events_by_id={}
filing_inflight={}
ASSESSMENT_POLICY='claim-linked-v8'
ENRICHMENT_POLICY='event-context-v4'
EXTRA_FIELDS=('category','event_key','event_period','management_profile','upcoming_dates','results')

def event_extras(event,rows,doc):
    event={k:v for k,v in event.items() if k not in EXTRA_FIELDS}
    if re.search(r'newspaper|publication',doc.get('title',''),re.I) and any(r['page']>1 for r in rows):
        rows=[r for r in rows if r['page']==1]
    enriched=event_tools.enrich(event,rows,doc)
    return {k:enriched[k] for k in EXTRA_FIELDS if k in enriched}

def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()

def filing_revision(signature,content_hash=None):
    return digest([signature,content_hash,'priority-v2'])[:20]

def pending_priority(event):
    """Conservative review routing, never confirmation of a title's allegation."""
    if 'url' in event and event['url'].strip() in ('','-','NA','N/A'):
        event={**event,'url':'','assessment_error':'The exchange did not provide a PDF attachment. Inspect its notice; no document contents were inferred.',
            'exchange_notice':event.get('exchange_notice') or {'text':event.get('description','').partition(' · ')[2],
                'source':'NSE announcement feed','checked_at':event.get('checked_at'),'signature':event.get('source_signature'),
                'url':'https://www.nseindia.com/companies-listing/corporate-filings-announcements'}}
    title=(event.get('description') or event.get('title','')).split(' · ')[0]
    sensitive=bool(re.search(r'news verification|rumour verification|fraud|default|insolvency|auditor|regulatory|action\(s\) taken|financial results|resign|change in (?:director|management)|appointment|outcome of board|capacity addition|raising of funds|allotment of securities',title,re.I))
    return {**event,'tier':0 if sensitive else min(event.get('tier',1),1),
        'reason':'Potentially important exchange notice; attachment evidence is incomplete. Review the original notice.' if sensitive else event.get('reason','Attachment evidence is incomplete; kept visible.')}

def priority(title,text=None):
    if not text:return {'tier':1,'assessment':'pending','reason':'Attachment not yet assessed; kept visible.'}
    # A title supplies routing context, never evidence of a transaction. Match
    # within source sentences so a disclaimer cannot borrow an event's verb.
    protected=re.sub(r'\b(Mr|Ms|Mrs|Dr|Prof|No)\.',lambda m:m[0][:-1]+'\uE000',text)
    protected=re.sub(r'\b([A-Z])\.(?=\s+[A-Z])',lambda m:m[0][:-1]+'\uE000',protected)
    sentences=[s.strip().replace('\uE000','.') for s in re.split(r'(?<=[.!?])\s+(?=[A-Z])|[\r\n]+|\s*[•✓]\s*',protected) if s.strip()]
    patterns=[(r'non\s*[-–]?\s*operational credit','Accounting remeasurement disclosed; inspect its effect on reported profit.'),
        (r'\b(?:bags|has (?:secured|won|received))\b.{0,100}\b(?:order|contract)\b','New order disclosed; inspect size and conditions.'),
        (r'(?:special resolution|description of\s*resolution considered)\s*[:–-]?\s*issuance of (?:warrants on a preferential basis|securities under qualified institutions placement)',
         'Capital raising resolution disclosed; inspect the proposal and voting outcome. This does not establish completed issuance.'),
        (r'\b(?:we are|the company is)\s+(?:upping|increasing|raising)\s+(?:our|its|the)\s+(?:CAPEX|capital expenditure|investment)\s+(?:plans?|budget|commitment)\s+(?:to|from)\s+(?:INR|Rs\.?|₹)\s*\d',
         'Capital spending plan increased; inspect the stated scope and execution assumptions.'),
        (r'(?:approv(?:ed|ing)|allotted|opening).{0,180}(?:allotment.{0,160}(?:warrants|non-convertible debentures)|(?:commercial paper|CPs)|issue of.{0,160}(?:warrants|equity)|(?:floor|issue) price|qualified institutional placement)|(?:qualified institutions placement|preferential issue).{0,120}(?:approved|allotted)', 'Capital raising terms disclosed; review dilution and funding.'),
        (r'(?:appoint|re.appoint).{0,200}(?:statutory|internal|secretarial) auditor|(?:statutory|internal|secretarial) auditor.{0,100}(?:appoint|re.appoint)','Auditor appointment or reappointment disclosed; inspect the terms.'),
        (r'auditor.{0,100}(resign|\bqualified|concern)|\bqualified.{0,40}opinion','Auditor or audit concern; inspect the disclosure.'),
        (r'downgrad|(?:has|have|in)\s+default(?:ed)?\b|default\s+on\s+(?:payment|loan|debt)|(?:detected|reported|discovered)\s+(?:a\s+)?fraud|insolvency\s+(?:proceedings|petition)|material.{0,30}litigation|penalty.{0,30}(crore|million)|(?:has|have) filed (?:a )?(?:notice of )?appeal|(?:court|tribunal).{0,80}(?:has directed|has ordered|dismissed|attachment)|(?:served notices|order).{0,80}attachment','Credit, legal or regulatory development; review exposure.'),
        (r'(resign|retire|retirement|re.appoint|appoint).{0,160}(director|chief|\bcfo\b|\bceo\b)|(?:director|chief).{0,100}(resign|retire|retirement|re.appoint)','Board or senior-management change; review the terms.'),
        (r'\b(?:approved|completed|entered|executed|signed|proposes|proposed|announced|agreed)\b.{0,180}(?:\bacquisition(?![- ]related)|scheme of.{0,30}(?:merger|amalgamation)|capital expenditure|(?:an? )?investment (?:of|in)|sale of.{0,30}(?:business|subsidiary))|(?:\bacquisition(?![- ]related)|scheme of.{0,30}(?:merger|amalgamation)).{0,100}\b(?:approved|completed|signed)\b|\b(?:has|have)\s+(?:successfully\s+)?acquired\s+.{2,100}(?:limited|ltd\b|stake|shares|business|subsidiary|for\s+(?:INR|Rs|₹))',
         'Capital allocation or ownership development; inspect commitments.')]
    # Whole-document check computed once (it was re-run for every sentence).
    historical_timeline=len(re.findall(r'\b(?:19\d{2}|20[01]\d)[:–-]',text))>=3
    for pattern,reason in patterns:
        for sentence in sentences:
            # Do not discard the rest of a document after a disclaimer heading:
            # a genuine subsequent transaction disclosure must still surface.
            if re.search(r'forward.?looking|risks? (?:and uncertainties|include|relating to)|may (?:include|result)|not (?:in default|defaulted)|never defaulted',sentence,re.I):continue
            if re.search(r'(?:meets? the criteria|eligib(?:le|ility)) for appointment|(?:EBITDA|EBITA|operating profit).{0,45}(?:represents|defined as|calculated as)',sentence,re.I):continue
            if reason.startswith('Board or') and re.search(r'scrutiniz|statutory auditor|practicing company secretary|practising company secretary|board appointed committees|charters of|during the last quarter|in the previous year',sentence,re.I):continue
            if reason.startswith('Capital spending plan') and '?' in sentence:continue
            if reason.startswith('Capital allocation') and historical_timeline:continue
            if reason.startswith('Capital allocation') and re.search(r'completed in (?:Q[1-4]|FY|20\d{2})|previous(?:ly| year)|historical',sentence,re.I):continue
            if re.search(pattern,sentence,re.I|re.S):
                return {'tier':0,'assessment':'assessed','reason':reason,'trigger_quote':sentence}
    combined=(title+' '+text).lower()
    publication='newspaper' in combined or 'publication' in title.lower()
    substantive=bool(re.search(r'revenue|profit before|profit after|total income|balance sheet',text.lower()))
    reported_quarter=bool(re.search(r'\b(?:posts|reported|announced)\b.{0,100}\bresults\b',text,re.I) and re.search(r'\bQ[1-4]\s*(?:FY|CY)\s*\d{2,4}\b',text,re.I) and substantive)
    # A recording, transcript, clarification or reference to old/parent results
    # does not itself announce a new quarterly result.
    if re.search(r'news verification|rumour verification|clarification regarding news',title,re.I):
        match=next((x for x in sentences if re.search(r'does not concern any new event|not aware of any material',x,re.I)),None) or next((x for x in sentences if re.search(r'clarification|news report',x,re.I)),None)
        if match:return {'tier':0,'assessment':'assessed','reason':'Exchange clarification response; inspect event timing and issuer qualifications.','trigger_quote':match}
    for sentence in sentences:
        if re.search(r'audio|recording|transcript|to discuss|conference call|reference to|in continuation|to be approved|will be approved',sentence,re.I):continue
        disclosed=(re.search(r'financial results',sentence,re.I) and re.search(r'approved|enclos(?:ed|ing)|forward|attach|share with|statement of',sentence,re.I))
        if disclosed or (reported_quarter and re.search(r'\b(?:posts|reported|announced)\b.{0,100}\bresults\b',sentence,re.I)):
            return {'tier':0,'assessment':'assessed','reason':'Financial results disclosed; review performance and basis.','trigger_quote':sentence}
    routine=(publication and len(text)<1800 and not substantive and 'enclosed' in text.lower()) or (
        'closure of trading window' in combined and len(text)<2500) or ('loss of share certificate' in combined and len(text)<2500)
    if routine:return {'tier':3,'assessment':'routine','reason':'Routine procedural disclosure, confirmed from the attachment.'}
    return {'tier':1,'assessment':'assessed','reason':'Source read; no material-rule match. Kept available for review.'}

def source_headline(title,text):
    if not text:return title
    # Use an issuer-written subject, never a model inference or truncated assertion.
    match=re.search(r'\bSub(?:ject)?\s*:\s*(.{20,350}?)(?=\s+(?:Ref\s*:|In furtherance|Pursuant|Dear|We wish|This is))',text,re.I)
    return match[1].strip() if match and len(match[1])<=240 else title

def valid_assessment(eid,signature,url):
    assessed=store.cached('assessed-'+eid,600)
    if assessed and not assessed.get('error') and assessed.get('policy')!=ASSESSMENT_POLICY:return None
    if assessed and assessed.get('source_signature')!=signature:return None
    latest=store.cached('latest-document-filing-'+url)
    if assessed and assessed.get('version') and latest and latest!=assessed['version']:return None
    return assessed

def make_filing(row,checked):
    symbol=row['symbol'];source={'title':row.get('desc') or 'Unclassified disclosure','description':row.get('attchmntText') or '',
        'url':row.get('attchmntFile') or '', 'published':row.get('an_dt') or row.get('sort_date') or ''}
    try:published=datetime.strptime(source['published'],'%d-%b-%Y %H:%M:%S').replace(tzinfo=IST).isoformat()
    except ValueError:
        try:published=datetime.fromisoformat(source['published']).replace(tzinfo=IST).isoformat()
        except ValueError:published=None
    eid='filing-'+symbol+'-'+str(row.get('seq_id') or digest(source)[:16])
    signature=digest(source)
    assessed=valid_assessment(eid,signature,source['url'])
    # Assessment freshness controls coverage, not whether the disclosure changed.
    # Keep the last observed byte hash across TTL expiry and parser-only upgrades.
    observed=store.cached('latest-document-filing-'+source['url']) or (assessed or {}).get('version')
    revision=filing_revision(signature,observed.split('-x')[0] if observed else None)
    state=assessed.get('classification') if assessed else None
    if state is None:state=priority(source['title'],assessed.get('text') if assessed else None)
    event={'id':eid,'revision':revision,'symbol':symbol,'name':row.get('sm_name') or symbol,'kind':'filing',
        'title':source_headline(source['title'],assessed.get('text') if assessed else None),'description':source['title']+' · '+source['description'],'published_at':published,'checked_at':checked,
        'url':source['url'],'source_signature':signature,**state,'evidence':assessed.get('evidence',[]) if assessed else [],
        'assessment_error':assessed.get('error') if assessed else None,'assessment_policy':ASSESSMENT_POLICY,
        **(assessed.get('enrichment',{}) if assessed else {})}
    if source['url'].strip() in ('','-','NA','N/A'):
        event.update(url='',assessment='pending',assessment_error='The exchange did not provide a PDF attachment. Its notice remains available below.',
            exchange_notice={'text':source['description'],'source':'NSE announcement feed','checked_at':checked,
                'signature':signature,'url':'https://www.nseindia.com/companies-listing/corporate-filings-announcements'})
    return pending_priority(event) if event['assessment']=='pending' else event

async def assess(event):
    if event['url'].strip() in ('','-','NA','N/A'):raise SourceError('missing_attachment','The exchange did not provide a PDF attachment. Inspect the exchange notice; no document contents were inferred.')
    company=await identity(event['symbol'])
    source={'kind':'filing','title':event['title'],'discovery_period':event['published_at'] or 'Date not supplied',
            'download_url':event['url'],'original_url':event['url']}
    doc=await ingest(company,source,{})
    version=doc['version']
    with store.db() as c:
        rows=c.execute('SELECT id,page,text FROM chunks WHERE hash=? ORDER BY page,id',(version,)).fetchall()
    if sum(len(r['text']) for r in rows)>1_000_000:raise SourceError('assessment_limit','Large attachment remains pending; inspect the original document.')
    # The full extracted content informs classification; no title-only suppression.
    text=' '.join(r['text'] for r in rows)
    # CPU-heavy regex classification runs off the event loop so heartbeats and requests continue.
    classification,evidence=await asyncio.to_thread(classify_with_evidence,event['title'],rows,doc)
    assessment={'version':version,'text':text,'evidence':evidence,
        'classification':classification,'policy':ASSESSMENT_POLICY,'source_signature':event['source_signature'],
        'enrichment':event_extras({**event,**classification},rows,doc)}
    store.put('assessed-'+event['id'],assessment)
    apply_assessments(event['id'],assessment)
    return evidence


def apply_assessments(event_id=None,assessment=None):
    """Update assessed events without dropping the last good source receipt."""
    snapshot=store.cached('brief-snapshot')
    if not snapshot:return
    for event in snapshot['events']:
        if event['kind']!='filing':continue
        if event_id and event['id']!=event_id:continue
        assessed=assessment if event_id else valid_assessment(event['id'],event['source_signature'],event['url'])
        if assessed and assessed.get('source_signature')!=event['source_signature']:continue
        if not assessed or not assessed.get('classification'):continue
        for field in (*EXTRA_FIELDS,'trigger_quote','assessment_scope'):event.pop(field,None)
        event.update(**assessed['classification'],evidence=assessed['evidence'],
            assessment_error=None,
            assessment_policy=ASSESSMENT_POLICY,enrichment_policy=ENRICHMENT_POLICY,
            **assessed.get('enrichment',{}))
        event['revision']=filing_revision(event['source_signature'],assessed['evidence'][0]['hash'] if assessed['evidence'] else None)
        events_by_id[event['id']]=event
    snapshot['counts']['pending']=sum(e['assessment']=='pending' for e in snapshot['events'])
    snapshot['counts']['routine']=sum(e['assessment']=='routine' for e in snapshot['events'])
    store.put('brief-snapshot',snapshot)

def classify_with_evidence(title,rows,doc):
    """The rationale and citation share the same decision; never pick separately."""
    publication=re.search(r'newspaper|publication',title,re.I)
    if publication and any(r['page']>1 for r in rows):
        # Newspaper scans contain unrelated advertisements, often interleaved
        # within a single extracted chunk. Document identity is not page-level
        # issuer identity. A cover letter is inspectable; unverified layout is
        # never an affirmative event claim or permission to bury the filing.
        cover=[r for r in rows if r['page']==1]
        matched=next((r for r in cover if re.search(r'financial results',r['text'],re.I)),None)
        state={'tier':0 if matched else 1,'assessment':'pending',
            'reason':'Newspaper attachment needs issuer-specific layout verification; kept visible.',
            'assessment_scope':'cover_only'}
        selected=[matched] if matched else cover[:1]
        return state,[{**doc,'id':r['id'],'page':r['page'],'text':r['text']} for r in selected]
    from .documents import filing_exclusion
    opening=' '.join(r['text'] for r in rows if r['page']==1)
    if filing_exclusion(doc,opening):
        return {'tier':1,'assessment':'pending','reason':'Referenced results require issuer/basis verification; kept visible.','assessment_scope':'cover_only'},[{**doc,**dict(r)} for r in rows[:1]]
    candidates=[]
    for row in rows:
        state=priority(title,row['text'])
        if state.get('trigger_quote'):
            candidates.append((state,row))
    if candidates:
        def order(pair):
            reason=pair[0]['reason']
            severity=0 if reason.startswith('Auditor or') else 1 if reason.startswith('Credit,') else 2 if reason.startswith('Auditor appointment') else 3 if reason.startswith('Board or') else 4 if reason.startswith('Capital allocation') else 5
            return pair[0]['tier'],severity
        state,row=min(candidates,key=order)
        return state,[{**doc,'id':row['id'],'page':row['page'],'text':row['text'],'quote':state['trigger_quote']}]
    state=priority(title,' '.join(r['text'] for r in rows))
    # A cross-chunk inference cannot ship as a supported critical claim.
    if state.get('trigger_quote'):
        state={'tier':1,'assessment':'assessed','reason':'Possible material disclosure; inspect the original. A supporting passage could not be isolated.'}
    # Positive routine evidence is evaluated only after every readable chunk's
    # critical candidates. A schedule title alone never authorises burial.
    text=' '.join(r['text'] for r in rows)
    if len(text)<=5000 and re.search(r'(?:schedule|scheduled|participat).{0,100}(?:investor|conference)|(?:investor|analyst).{0,60}(?:meeting|meet|conference)',text,re.I):
        safe=next((r for r in rows if re.search(r'no (?:unpublished )?price sensitive information.{0,80}(?:shared|disclosed|discussed)',r['text'],re.I)),None)
        if safe and state['assessment']=='assessed':
            quote=re.search(r'[^.!?]*\bno (?:unpublished )?price sensitive information.{0,80}(?:shared|disclosed|discussed)[^.!?]*[.!?]',safe['text'],re.I)
            if quote:
                state={'tier':3,'assessment':'routine','reason':'Investor-meeting logistics; the issuer states no unpublished price-sensitive information is to be shared.','trigger_quote':quote[0].strip()}
                return state,[{**doc,**dict(safe),'quote':state['trigger_quote']}]
    first=rows[:1]
    return state,[{**doc,'id':r['id'],'page':r['page'],'text':r['text']} for r in first]

def upgrade_stored_snapshot():
    """Reclassify retained bytes once; never pretend this is a fresh source fetch."""
    snapshot=store.cached('brief-snapshot')
    if not snapshot:return
    changed=False
    for event in snapshot['events']:
        if event['kind']!='filing' or (event.get('assessment_policy')==ASSESSMENT_POLICY and event.get('enrichment_policy')==ENRICHMENT_POLICY and event.get('assessment')!='pending'):continue
        version=store.cached('latest-document-filing-'+event['url'])
        # Earlier seed releases retained PDF bytes locally without a durable
        # latest-version pointer. Migrate only one unambiguous byte identity at
        # this exact issuer URL, never choose between replacement documents.
        if not version:
            with store.db() as c:
                candidates=c.execute("SELECT hash,meta FROM documents WHERE symbol=? AND kind='filing' AND json_extract(meta,'$.original_url')=?",(event['symbol'],event['url'])).fetchall()
            if candidates and len({json.loads(d['meta'])['hash'] for d in candidates})==1:
                candidate=max(candidates,key=lambda d:(json.loads(d['meta']).get('fetched_at',''),d['hash']))
                version=candidate['hash']
                store.retain(version)
                store.put('latest-document-filing-'+event['url'],version)
        with store.db() as c:
            doc=c.execute('SELECT meta FROM documents WHERE hash=?',(version,)).fetchone() if version else None
            rows=c.execute('SELECT id,page,text FROM chunks WHERE hash=? ORDER BY page,id',(version,)).fetchall() if doc else []
        if rows and sum(len(r['text']) for r in rows)<=1_000_000:
            store.retain(version)
            meta=json.loads(doc['meta']);state,evidence=classify_with_evidence(event['title'],rows,meta)
            extras=event_extras({**event,**state},rows,meta)
            for field in (*EXTRA_FIELDS,'trigger_quote','assessment_scope'):event.pop(field,None)
            event.update(**state,evidence=evidence,assessment_policy=ASSESSMENT_POLICY,**extras)
            store.put('assessed-'+event['id'],{'version':version,'text':' '.join(r['text'] for r in rows),
                'classification':state,'evidence':evidence,'policy':ASSESSMENT_POLICY,'source_signature':event['source_signature'],'enrichment':extras})
        else:
            for field in (*EXTRA_FIELDS,'trigger_quote','assessment_scope'):event.pop(field,None)
            event.update(tier=min(event.get('tier',1),1),assessment='pending',reason='Stored disclosure awaiting the current evidence assessment; kept visible.',assessment_policy=ASSESSMENT_POLICY,evidence=[])
        event['enrichment_policy']=ENRICHMENT_POLICY
        changed=True
    if changed:
        snapshot['counts']['pending']=sum(e['assessment']=='pending' for e in snapshot['events'])
        snapshot['counts']['routine']=sum(e['assessment']=='routine' for e in snapshot['events'])
        store.put('brief-snapshot',snapshot)

async def assess_background(events):
    for event in events:
        if research.worker.locked() or any(j['status']=='running' for j in research.jobs.values()):break
        research.background_active=True
        try:
            async with research.worker:
                await assess(event)
        except SourceError as e:
            store.put('assessed-'+event['id'],{'version':None,'text':None,'evidence':[], 'error':e.message,'source_signature':event['source_signature']})
        except Exception as e:
            print('filing_error='+type(e).__name__,flush=True)
            store.put('assessed-'+event['id'],{'version':None,'text':None,'evidence':[],'error':'Attachment processing was interrupted. Retry explicitly.','source_signature':event['source_signature']})
        finally:research.background_active=False

async def get_brief(force=False,symbols=None,background=True):
    global assessment_task,events_by_id
    symbols=list(dict.fromkeys(PORTFOLIO if symbols is None else symbols))
    hit=None if force else store.cached('brief-snapshot',60)
    if hit:
        events_by_id={e['id']:e for e in hit['events']};return hit
    async with refresh_lock:
        hit=None if force else store.cached('brief-snapshot',60)
        if hit:
            events_by_id={e['id']:e for e in hit['events']};return hit
        previous=store.cached('brief-snapshot')
        coverage={s:{'symbol':s} for s in symbols};events=[];source_status='live';duplicates=0;fetched=0
        try:
            data=await filings()
        except SourceError as e:
            data=store.cached('filings');source_status='stale' if data else 'unavailable'
            filing_error=e.message
        else:filing_error=None
        if data:
            rows=[r for r in data['rows'] if r.get('symbol') in symbols];fetched=len(rows)
            def prepare():
                seen=set();prepared=[];repeats=0
                for row in rows:
                    fingerprint=digest({k:row.get(k) for k in ('symbol','an_dt','desc','attchmntText','attchmntFile')})
                    if fingerprint in seen:repeats+=1;continue
                    seen.add(fingerprint);prepared.append(make_filing(row,data['checked_at']))
                return prepared,repeats
            # Remote cache lookups are synchronous. A large book must not
            # starve the async lease heartbeat while those reads finish.
            events,duplicates=await asyncio.to_thread(prepare)
        for symbol in symbols:
            coverage[symbol]['filings']={'status':source_status,'checked_at':data['checked_at'] if data else None,'error':filing_error}
        semaphore=asyncio.Semaphore(4)
        async def one(symbol):
            async with semaphore:
                try:p=await price(symbol);state='live';error=None
                except SourceError as e:p=store.cached('price-'+symbol);state='stale' if p else 'unavailable';error=e.message
                if not p:return symbol,{'status':state,'error':error,'checked_at':None}
                try:signal=daily_signal(p['chart'])
                except (ValueError,KeyError,TypeError,IndexError):return symbol,{'status':'unavailable','error':'Daily bars could not be verified.','checked_at':p['checked_at']}
                return symbol,{**signal,'status':state if signal['status']=='available' else 'unavailable','checked_at':p['checked_at'],'error':error,
                    'url':'https://finance.yahoo.com/quote/'+symbol+'.NS/history/'}
        for symbol,result in await asyncio.gather(*(one(s) for s in symbols)):
            coverage[symbol]['price']=result
            change=result.get('change_percent');multiple=result.get('volume_multiple')
            if (change is not None and abs(change)>=5) or (multiple is not None and multiple>=2):
                title=f'{change:+.2f}% at the last close' if change is not None and abs(change)>=5 else f'{multiple:.2f}× usual daily volume'
                eid='price-'+symbol+'-'+result['session']
                events.append({'id':eid,'revision':digest(result['operands'])[:20],'symbol':symbol,'name':symbol,'kind':'price','tier':2,
                    'assessment':'calculated','title':title,'description':'End-of-day signal. The data does not establish the cause.',
                    'reason':'Crossed the fixed 5% move or 2× volume review threshold.','published_at':result['session']+'T15:30:00+05:30',
                    'checked_at':result['checked_at'],'url':result['url'],'signal':result,'evidence':[]})
        latest=max((v['price'].get('session','') for v in coverage.values()),default='')
        for item in coverage.values():item['price']['older_session']=bool(item['price'].get('session') and item['price']['session']<latest)
        events.sort(key=lambda e:(e['tier'],-datetime.fromisoformat(e['published_at']).timestamp() if e['published_at'] else 0))
        events_by_id={e['id']:e for e in events}
        snapshot={'events':events,'coverage':list(coverage.values()),'checked_at':now(),'filing_checked_at':data['checked_at'] if data else None,
            'counts':{'fetched_filings':fetched,'distinct_filings':fetched-duplicates,'exact_duplicates':duplicates,
                'pending':sum(e['assessment']=='pending' for e in events),'routine':sum(e['assessment']=='routine' for e in events)},
            'source_status':source_status,'window':'Last 14 days','is_demo_seed':False}
        # Preserve other books and unfinished events when refreshing this book.
        # An exchange's rolling response must not erase retained disclosures.
        if previous:
            ids={e['id'] for e in events}
            snapshot['events'] += [e for e in previous['events'] if e['id'] not in ids]
            snapshot['coverage'] += [c for c in previous['coverage'] if c['symbol'] not in symbols]
        events_by_id={e['id']:e for e in snapshot['events']}
        store.put('brief-snapshot',snapshot)
        # A small assessment budget prioritises recent events; all others remain visible.
        candidates=[e for e in events if e['kind']=='filing' and e['assessment']=='pending' and not e['assessment_error']]
        if background and candidates and (assessment_task is None or assessment_task.done()):
            assessment_task=asyncio.create_task(assess_background(candidates[:12]))
        return snapshot

async def run_filing(job,event):
    try:
        async with research.worker:
            job['stage']='Reading the exchange attachment'
            evidence=await assess(event)
            job.update(status='complete',stage='Complete',result={'evidence':evidence,'company':{'symbol':event['symbol'],'name':event['name']}})
    except SourceError as e:job.update(status='error',stage='Could not read attachment',error={'code':e.code,'message':e.message})
    except Exception:job.update(status='error',stage='Could not read attachment',error={'code':'processing_error','message':'Attachment processing was interrupted. Retry later.'})
    finally:filing_inflight.pop(event['id'],None)

def submit_filing(eid):
    import uuid
    event=events_by_id.get(eid)
    if not event:raise SourceError('event_expired','Refresh the brief before opening this filing.')
    if eid in filing_inflight:return research.jobs[filing_inflight[eid]]
    cached=valid_assessment(eid,event['source_signature'],event['url'])
    if cached and cached.get('evidence'):
        return {'id':'cache','status':'complete','result':{'evidence':cached['evidence']}}
    active=sum(j['status']=='running' for j in research.jobs.values())+int(research.background_active)
    if active>=2:raise SourceError('busy','Document processing is busy. Open the original or retry shortly.')
    research.prune_jobs()
    job={'id':uuid.uuid4().hex,'symbol':event['symbol'],'status':'running','stage':'Waiting to read attachment','created_at':now()}
    research.jobs[job['id']]=job;filing_inflight[eid]=job['id'];asyncio.create_task(run_filing(job,event));return job
