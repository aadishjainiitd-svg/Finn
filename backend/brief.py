"""Every fetched filing stays accounted for. Only positively assessed routine items collapse."""
import asyncio
import hashlib
import json
import re
from datetime import datetime,timezone
from . import research,store
from .config import PORTFOLIO
from .sources import filings,price,identity,now
from .documents import ingest
from .numbers import daily_signal,IST
from .network import SourceError

refresh_lock=asyncio.Lock()
assessment_task=None
events_by_id={}
filing_inflight={}

def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()

def priority(title,text=None):
    if not text:return {'tier':1,'assessment':'pending','reason':'Attachment not yet assessed; kept visible.'}
    combined=(title+' '+text).lower()
    combined=re.sub(r'\b(?:not|never)\s+(?:in\s+default|defaulted)\b','',combined)
    patterns=[(r'auditor.{0,100}(resign|\bqualified|concern)|\bqualified.{0,40}opinion','Auditor or audit concern; inspect the disclosure.'),
        (r'downgrad|(?:has|have|in)\s+default(?:ed)?\b|default\s+on\s+(?:payment|loan|debt)|(?:detected|reported|discovered)\s+(?:a\s+)?fraud|insolvency\s+(?:proceedings|petition)|material.{0,30}litigation|penalty.{0,30}(crore|million)','Credit, legal or regulatory development; review exposure.'),
        (r'(resign|re.appoint|appoint).{0,160}(director|chief|\bcfo\b|\bceo\b)|(?:director|chief).{0,100}(resign|re.appoint)','Board or senior-management change; review the terms.'),
        (r'acquisition|scheme of.{0,30}(merger|amalgamation)|capital expenditure|investment of|sale of.{0,30}(business|subsidiary)','Capital allocation or ownership development; inspect commitments.')]
    for pattern,reason in patterns:
        if re.search(pattern,combined,re.S):return {'tier':0,'assessment':'assessed','reason':reason}
    publication='newspaper' in combined or 'publication' in title.lower()
    substantive=bool(re.search(r'revenue|profit before|profit after|total income|balance sheet',text.lower()))
    if 'financial results' in combined and (not publication or substantive):
        return {'tier':0,'assessment':'assessed','reason':'Financial results disclosed; review performance and basis.'}
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
    revision=digest([source,assessed.get('version') if assessed else None,'priority-v2'])[:20]
    state=priority(source['title'],assessed.get('text') if assessed else None)
    return {'id':eid,'revision':revision,'symbol':symbol,'name':row.get('sm_name') or symbol,'kind':'filing',
        'title':source_headline(source['title'],assessed.get('text') if assessed else None),'description':source['title']+' · '+source['description'],'published_at':published,'checked_at':checked,
        'url':source['url'],'source_signature':signature,**state,'evidence':assessed.get('evidence',[]) if assessed else [],
        'assessment_error':assessed.get('error') if assessed else None}

async def assess(event):
    if not event['url']:raise SourceError('missing_attachment','The exchange did not provide an attachment URL.')
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
    picks=[r for r in rows if re.search(r'appoint|resign|financial results|default|downgrad|investment|newspaper',r['text'],re.I)] or rows[:1]
    evidence=[{**doc,'id':r['id'],'page':r['page'],'text':r['text']} for r in picks[:3]]
    store.put('assessed-'+event['id'],{'version':version,'text':text,'evidence':evidence,'source_signature':event['source_signature']})
    store.put('brief-snapshot',None)
    return evidence

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

async def get_brief(force=False):
    global assessment_task,events_by_id
    hit=None if force else store.cached('brief-snapshot',60)
    if hit:
        events_by_id={e['id']:e for e in hit['events']};return hit
    async with refresh_lock:
        hit=None if force else store.cached('brief-snapshot',60)
        if hit:
            events_by_id={e['id']:e for e in hit['events']};return hit
        coverage={s:{'symbol':s} for s in PORTFOLIO};events=[];source_status='live';duplicates=0;fetched=0
        try:
            data=await filings()
        except SourceError as e:
            data=store.cached('filings');source_status='stale' if data else 'unavailable'
            filing_error=e.message
        else:filing_error=None
        if data:
            rows=[r for r in data['rows'] if r.get('symbol') in PORTFOLIO];fetched=len(rows);seen=set()
            for row in rows:
                fingerprint=digest({k:row.get(k) for k in ('symbol','an_dt','desc','attchmntText','attchmntFile')})
                if fingerprint in seen:duplicates+=1;continue
                seen.add(fingerprint);events.append(make_filing(row,data['checked_at']))
        for symbol in PORTFOLIO:
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
        for symbol,result in await asyncio.gather(*(one(s) for s in PORTFOLIO)):
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
        store.put('brief-snapshot',snapshot)
        # A small assessment budget prioritises recent events; all others remain visible.
        candidates=[e for e in events if e['kind']=='filing' and e['assessment']=='pending' and not e['assessment_error']]
        if candidates and (assessment_task is None or assessment_task.done()):
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
