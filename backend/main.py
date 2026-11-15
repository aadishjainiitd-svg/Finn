"""Small real backend; extended only after source and hosting checks."""
import os
import platform
import time
from datetime import datetime,timezone
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, Depends
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .config import ROOT
from pydantic import BaseModel, Field
from . import store,research,brief,repository,portfolio,watches,work,events as event_tools
from .owners import owner,mutation
from .network import SourceError
from .sources import filings,price,ticker
from .llm import metrics

@asynccontextmanager
async def lifespan(app):
    store.init()
    repository.init()
    from .seed import restore
    restore()
    # Hosted cold starts must not issue one remote lookup per old seed filing.
    # /api/today keeps older assessments visible as pending; explicit assessment
    # jobs upgrade their evidence under the global worker lease.
    if not repository.configured():brief.upgrade_stored_snapshot()
    import asyncio
    worker=asyncio.create_task(work.loop()) if os.getenv('FINN_WORKER','true')=='true' else None
    try:yield
    finally:
        if worker:
            worker.cancel()
            await asyncio.gather(worker,return_exceptions=True)
        repository.close()

app = FastAPI(title='FINN', docs_url=None, redoc_url=None, lifespan=lifespan)
app.mount('/assets',StaticFiles(directory=ROOT/'frontend/dist/assets',check_dir=False),name='assets')
app.mount('/fonts',StaticFiles(directory=ROOT/'frontend/dist/fonts',check_dir=False),name='fonts')
clients={}

@app.exception_handler(repository.Conflict)
async def state_conflict(request,exc):
    return JSONResponse(status_code=409,content={'error':{'code':'state_conflict','message':str(exc)}})

def visit_key(request:Request):
    value=request.headers.get('X-Finn-Visit','')
    if value and (len(value)!=32 or any(c not in '0123456789abcdef' for c in value)):
        raise SourceError('invalid_visit','Reload this tab to start a valid visit.')
    return value or None

@app.get('/api/session')
def session(request:Request,identity:str=Depends(owner)):
    from .theses import book_health
    return {'book':book_health(identity,portfolio.book(identity)),'review':portfolio.review(identity,visit_key(request)),
        'storage':{'mode':'persistent_postgres' if repository.configured() else 'local_development',
                   'recovery':'This browser only; clearing the session cookie loses access to private state.'},
        'telegram':{'configured':False,'connected':False,'enabled':False}}

@app.get('/api/holding/{symbol}')
def holding_detail(symbol:str,identity:str=Depends(owner)):
    from .numbers import daily_signal,IST
    symbol=ticker(symbol)
    holding=next((h for h in portfolio.book(identity)['holdings'] if h['symbol']==symbol),None)
    if not holding:return JSONResponse(status_code=404,content={'error':{'message':'This ticker is not in your book.'}})
    data=store.cached('price-'+symbol);bars=[]
    if data:
        for stamp in data['chart'].get('timestamp',[]):
            session=datetime.fromtimestamp(stamp,IST)
            at=session.replace(hour=16,minute=0,second=0,microsecond=0)
            if at>datetime.now(timezone.utc):continue
            signal=daily_signal(data['chart'],at)
            if signal.get('close') is not None and (not bars or bars[-1]['session']!=signal['session']):bars.append(signal)
    snapshot=store.cached('brief-snapshot') or {'events':[]}
    from . import theses
    return {'holding':holding,'bars':bars[-30:],'checked_at':data['checked_at'] if data else None,
        'thesis':theses.detail(identity,holding,snapshot['events']),
        'read_across':event_tools.read_across(snapshot['events'],portfolio.book(identity)['holdings']),
        'price_basis':'Unadjusted daily close; corporate actions may cause discontinuities.'}

class ThesisRequest(BaseModel):
    symbol:str=Field(max_length=30)
    event_id:str|None=Field(default=None,max_length=180)

@app.post('/api/thesis/assess',status_code=202,dependencies=[Depends(mutation)])
def assess_thesis(body:ThesisRequest,identity:str=Depends(owner)):
    symbol=ticker(body.symbol)
    holding=next((h for h in portfolio.book(identity)['holdings'] if h['symbol']==symbol),None)
    if not holding or not holding.get('thesis'):raise SourceError('thesis_required','Save a reason for owning this company in Book first.')
    if body.event_id:
        snapshot=store.cached('brief-snapshot') or {'events':[]}
        if not any(e['id']==body.event_id and e['symbol']==symbol and e['kind']=='filing' for e in snapshot['events']):
            raise SourceError('event_expired','This filing is no longer in the stored source window. Reload before assessing it.')
    return work.enqueue(identity,'thesis',{'symbol':symbol,'thesis_version':holding.get('thesis_version'),'event_id':body.event_id})

class ThesisJudgement(ThesisRequest):
    thesis_version:str=Field(min_length=1,max_length=80)
    broken:bool

@app.post('/api/thesis/judgement',dependencies=[Depends(mutation)])
def thesis_judgement(body:ThesisJudgement,identity:str=Depends(owner)):
    from . import theses
    return theses.confirm(identity,ticker(body.symbol),body.thesis_version,body.broken)

class ReminderRequest(BaseModel):
    event_id:str=Field(max_length=180)
    date:str=Field(pattern=r'^\d{4}-\d{2}-\d{2}$')
    kind:str=Field(max_length=40)
    enabled:bool=True

@app.get('/api/reminders')
def get_reminders(identity:str=Depends(owner)):
    from .scheduled import reminders
    reminders(identity,datetime.now(timezone.utc))
    return {'items':repository.listing(identity,'reminders'),'statuses':repository.listing(identity,'reminder_status')}

@app.post('/api/internal/schedule')
def scheduled_refresh(request:Request):
    from . import scheduled
    if not scheduled.authenticate(request.headers.get('Authorization','')):
        return JSONResponse(status_code=401,content={'error':{'message':'Scheduler authentication required.'}})
    return scheduled.submit()

@app.get('/api/internal/schedule/{job_id}')
def scheduled_status(job_id:str,request:Request):
    from . import scheduled
    if not scheduled.authenticate(request.headers.get('Authorization','')):
        return JSONResponse(status_code=401,content={'error':{'message':'Scheduler authentication required.'}})
    result=work.get('_scheduler',job_id)
    return result or JSONResponse(status_code=404,content={'error':{'message':'Scheduled job not found.'}})

@app.post('/api/reminders',dependencies=[Depends(mutation)])
def set_reminder(body:ReminderRequest,identity:str=Depends(owner)):
    import hashlib
    key=hashlib.sha256((body.event_id+body.date+body.kind).encode()).hexdigest()
    if not body.enabled:
        previous=repository.get(identity,'reminders',key)
        if not previous:raise SourceError('date_changed','No saved reminder matches this date.')
        return repository.save(identity,'reminders',key,{**previous,'enabled':False},expected=previous['_version'])
    snapshot=store.cached('brief-snapshot') or {'events':[]}
    symbols={h['symbol'] for h in portfolio.book(identity)['holdings']}
    dates=event_tools.upcoming([e for e in snapshot['events'] if e['symbol'] in symbols])
    event=next((d for d in dates if d['event_id']==body.event_id and d['date']==body.date and d['kind']==body.kind),None)
    if not event or event['status']=='cancelled':raise SourceError('date_changed','This date is no longer a current scheduled event. Refresh Week ahead.')
    return repository.save(identity,'reminders',key,{'event':event,'enabled':body.enabled,
        'delivery':'in_app','note':'Saved for Week ahead. No push or Telegram message is scheduled.'})

@app.post('/api/refresh',status_code=202,dependencies=[Depends(mutation)])
def refresh_sources(identity:str=Depends(owner)):
    return work.enqueue(identity,'refresh',{})

class BookRequest(BaseModel):
    holdings:list[portfolio.Holding]=Field(max_length=50)
    version:int=Field(ge=0)

@app.post('/api/book',dependencies=[Depends(mutation)])
async def update_book(body:BookRequest,identity:str=Depends(owner)):
    previous=portfolio.book(identity)
    saved=await portfolio.save_book(identity,[h.model_dump() for h in body.holdings],body.version)
    old={h['symbol']:h.get('thesis_version') for h in previous['holdings']}
    if any(h.get('thesis') and h.get('thesis_version')!=old.get(h['symbol']) for h in saved['holdings']):
        try:
            work.enqueue(identity,'thesis',{'book_version':saved['_version']})
            saved['thesis_processing']='Thesis saved; evidence checks are queued. Existing findings retain their original thesis version.'
        except SourceError as exc:
            saved['thesis_processing']='Thesis saved. Evidence checks could not be queued: '+exc.message+' Open the holding and retry assessment.'
    return saved

class ImportRequest(BaseModel):
    text:str=Field(max_length=40000)

@app.get('/api/watches')
def get_watches(identity:str=Depends(owner)):
    from . import scheduled
    return {'rules':repository.listing(identity,'rules'),'firings':repository.listing(identity,'firings'),
            'evaluation':repository.get(identity,'state','watch_evaluation'),
            'scheduler':{'configured':scheduled.configured(),'last_run':repository.get('_public','operations','scheduler')},
            'monitoring':'Scheduled refresh is configured; inspect the last run and per-source coverage. Delivery is best effort.' if scheduled.configured() else 'Evaluated on explicit source refresh and filing assessment. Scheduled unattended monitoring is not connected.'}

class RuleDraft(BaseModel):
    sentence:str=Field(min_length=3,max_length=600)

@app.post('/api/watches/draft',dependencies=[Depends(mutation)])
def draft_watch(body:RuleDraft,identity:str=Depends(owner)):
    rule=watches.draft(body.sentence)
    return {'rule':rule,'sentence':watches.describe(rule),'saved':False}

class RuleSave(BaseModel):
    rule:watches.Rule
    id:str|None=Field(default=None,max_length=80)
    version:int=Field(default=0,ge=0)

@app.post('/api/watches',dependencies=[Depends(mutation)])
async def save_watch(body:RuleSave,identity:str=Depends(owner)):
    return await watches.save(identity,body.rule.model_dump(mode='json'),body.id,body.version)

@app.post('/api/watches/preview',dependencies=[Depends(mutation)])
def preview_watch(body:watches.Rule,identity:str=Depends(owner)):
    symbol=ticker(body.symbol);data=store.cached('price-'+symbol)
    if not data:return {'status':'unavailable','message':'No stored daily bars for '+symbol+'. Refresh source coverage before replay.','eligible_sessions':0,'firings':[]}
    return {**watches.preview(body,data['chart']),'checked_at':data['checked_at']}

@app.post('/api/book/preview',dependencies=[Depends(mutation)])
async def preview_book(body:ImportRequest,identity:str=Depends(owner)):
    from pydantic import ValidationError
    try:holdings=await portfolio.validate_holdings(portfolio.parse_import(body.text))
    except ValidationError:raise SourceError('invalid_import','Use symbol, weight (0–100), and thesis columns. No changes saved.') from None
    return {'holdings':holdings,'saved':False}

class ReviewRequest(BaseModel):
    action:str=Field(max_length=20)
    event_id:str=Field(default='',max_length=180)
    revision:str=Field(default='',max_length=80)
    value:bool|str|None=None

class ReviewMigration(BaseModel):
    known:dict[str,str]=Field(default_factory=dict,max_length=5000)
    reviewed:dict[str,str]=Field(default_factory=dict,max_length=5000)
    eligible:dict[str,bool]=Field(default_factory=dict,max_length=5000)

@app.post('/api/review/migrate',dependencies=[Depends(mutation)])
def migrate_review(body:ReviewMigration,identity:str=Depends(owner)):
    state=portfolio.review(identity)
    if state.get('legacy_imported'):return state
    for key,value in body.known.items():
        if len(key)>180 or len(value)>80:raise SourceError('invalid_migration','Review import contains an invalid identifier.')
        state.setdefault('known',{}).setdefault(key,value)
        if body.eligible.get(key):state.setdefault('eligible',{}).setdefault(key,value)
    for key,value in body.reviewed.items():
        if key in body.known and body.known[key]==value:state['reviewed'].setdefault(key,value)
    state['legacy_imported']=True
    return repository.save(identity,'state','review',state,expected=state['_version'])

@app.post('/api/review',dependencies=[Depends(mutation)])
def update_review(body:ReviewRequest,request:Request,identity:str=Depends(owner)):
    if body.action=='visit' and not store.cached('brief-snapshot'):
        raise SourceError('snapshot_unavailable','The visit starts after a usable digest is available.')
    snapshot=store.cached('brief-snapshot') or {'events':[]}
    symbols={h['symbol'] for h in portfolio.book(identity)['holdings']}
    raw=[e for e in snapshot['events'] if e['symbol'] in symbols]
    events=event_tools.thread(raw)
    if body.action=='visit':events=[*raw,*events]
    return portfolio.update_review(identity,body.action,body.event_id,body.revision,body.value,events,visit_key(request))

@app.get('/api/today')
def today(identity:str=Depends(owner)):
    snapshot=store.cached('brief-snapshot')
    if not snapshot:raise SourceError('snapshot_unavailable','No stored digest is available yet. Refresh sources to begin.')
    book=portfolio.book(identity);state=portfolio.review(identity)
    public_events=[]
    for event in snapshot['events']:
        if event['kind']=='filing' and event.get('assessment_policy')!=brief.ASSESSMENT_POLICY:
            event={**event,'tier':min(event.get('tier',1),1),'assessment':'pending','reason':'Stored disclosure awaiting the current evidence assessment; kept visible.'}
            event={k:v for k,v in event.items() if k not in brief.EXTRA_FIELDS}
            event['evidence']=[]
        if event['kind']=='filing' and event.get('assessment')=='pending':event=brief.pending_priority(event)
        public_events.append(event)
        brief.events_by_id[event['id']]=event
    from . import theses
    thesis_records=theses.assessments(identity,book['holdings'],public_events) if any(h.get('thesis') for h in book['holdings']) else {}
    ranked=portfolio.rank(public_events,book['holdings'],state,thesis_records)
    events=event_tools.thread(ranked)
    symbols={h['symbol'] for h in book['holdings']}
    coverage=[c for c in snapshot['coverage'] if c['symbol'] in symbols]
    coverage=[{**c,'filings':dict(c['filings']),'price':dict(c['price'])} for c in coverage]
    for item in coverage:
        for source,maximum_age in [('filings',1200),('price',129600)]:
            receipt=item[source]
            if receipt.get('status')!='live':continue
            try:age=(datetime.now(timezone.utc)-datetime.fromisoformat(receipt['checked_at'])).total_seconds()
            except (ValueError,TypeError,KeyError):age=float('inf')
            if age>maximum_age:
                receipt.update(status='stale',error='Stored observation is older than the refresh interval. Refresh sources to check for changes.')
    covered={c['symbol'] for c in coverage}
    for symbol in sorted(symbols-covered):
        coverage.append({'symbol':symbol,'price':{'status':'unavailable'},
                         'filings':{'status':'unavailable','checked_at':None,'error':'Not fetched for this book yet.'}})
    own=[e for e in public_events if e['symbol'] in symbols]
    counts={'distinct_filings':sum(e['kind']=='filing' for e in own),
            'pending':sum(e['assessment']=='pending' for e in own),'routine':sum(e['assessment']=='routine' for e in own)}
    return {**snapshot,'events':events,'coverage':coverage,'counts':counts,'book_version':book['_version'],
            'upcoming':event_tools.upcoming(ranked),'read_across':event_tools.read_across(ranked,book['holdings']),
            'snapshot_note':'Stored observation. Check the source dates; fetch coverage is not extraction coverage.'}

@app.exception_handler(SourceError)
async def source_error(request,exc):
    status=429 if exc.code=='busy' else 422 if exc.code in ('invalid_ticker','unknown_ticker') else 404 if exc.code=='scheduler_disabled' else 503
    return JSONResponse(status_code=status,content={'error':{'code':exc.code,'message':exc.message}})

class ResearchRequest(BaseModel):
    symbol:str=Field(min_length=1,max_length=30)
    question:str=Field(min_length=10,max_length=600)
    filing_id:str|None=Field(default=None,max_length=160)
    scope:str=Field(default='company',pattern='^(company|portfolio)$')
    parent_id:str|None=Field(default=None,max_length=100)

class PackRequest(BaseModel):
    symbol:str=Field(min_length=1,max_length=30)
    annual_count:int=Field(default=2,ge=2,le=5)

@app.get('/api/research-pack/{symbol}')
def get_research_pack(symbol:str,identity:str=Depends(owner)):
    from .research_pack import get,slim
    return {'pack':slim(get(ticker(symbol)))}

@app.get('/api/guidance/{symbol}')
def get_guidance(symbol:str,identity:str=Depends(owner)):
    """Management guidance from the saved research, for the event sheet. No model, no fetch."""
    from .research_pack import get
    pack=get(ticker(symbol))
    if not pack:return {'available':False,'items':[]}
    order={'missed':0,'met':1,'indicative':2,'not_due':3,'revised':4,'withdrawn':5,'not_comparable':6}
    items=[i for i in (pack.get('commitments') or {}).get('items',[]) if i.get('target')]
    items.sort(key=lambda i:(order.get(i['status'],9),(i['target'].get('scope')!='company')))
    keep=lambda e:dict(e)
    return {'available':True,'checked_at':pack.get('checked_at'),'items':[{
        'label':i['target'].get('label') or f"{i['target'].get('metric')} {i['target'].get('minimum')}",'status':i['status'],'reason':i['reason'],
        'quote':i['quote'],'speaker':i.get('speaker'),'evidence':keep(i['evidence']),'due':i.get('due'),
        'actual':{'value':i['actual']['value'],'unit':i['actual'].get('unit'),'quote':i['actual'].get('quote'),'evidence':keep(i['actual'].get('evidence') or {})} if i.get('actual') else None}
        for i in items[:3]]}

@app.post('/api/research-pack',status_code=202,dependencies=[Depends(mutation)])
def create_research_pack(body:PackRequest,identity:str=Depends(owner)):
    return work.enqueue(identity,'research_pack',{'symbol':ticker(body.symbol),'annual_count':body.annual_count})

@app.post('/api/research',status_code=202)
async def start_research(body:ResearchRequest,request:Request,identity:str=Depends(owner)):
    mutation(request)
    # Keyed on the browser session: behind Render's proxy every visitor shares one client address.
    host=identity
    stamp=time.monotonic()
    for key in list(clients):
        if stamp-clients[key][0]>600: clients.pop(key)
    entries=[t for t in clients.get(host,[]) if stamp-t<60]
    if len(entries)>=5: raise SourceError('busy','Please wait a minute before starting another investigation.')
    clients[host]=entries+[stamp]
    from .conversations import prepare
    if body.scope=='portfolio':
        book=portfolio.book(identity)
        if not book['holdings']:raise SourceError('empty_book','Add holdings before asking about your book.')
        if body.filing_id:raise SourceError('scope_conflict','A filing question and a whole-book question are separate scopes.')
        return work.enqueue(identity,'portfolio_research',{'symbol':'BOOK','question':body.question,
            'symbols':[h['symbol'] for h in book['holdings']],'book_version':book['_version'],
            'conversation':prepare(identity,body.parent_id,'BOOK',book_version=book['_version'])})
    symbol=ticker(body.symbol)
    conversation=prepare(identity,body.parent_id,symbol,body.filing_id)
    if conversation:return work.enqueue(identity,'research',{'symbol':symbol,'question':body.question,'filing_id':body.filing_id,'conversation':conversation})
    result=research.submit(symbol,body.question,body.filing_id,identity)
    if result.get('result'):
        import uuid
        history_id=uuid.uuid4().hex
        result['result']={**result['result'],'history_id':history_id,'filing_id':body.filing_id}
        repository.save(identity,'history',history_id,{'symbol':symbol,'question':body.question,
              'filing_id':body.filing_id,'answer':result['result'],'created_at':datetime.now(timezone.utc).isoformat()})
    return {k:v for k,v in result.items() if k!='owner'}

@app.get('/api/jobs/{job_id}')
def job(job_id:str,identity:str=Depends(owner)):
    result=work.get(identity,job_id)
    if result:return result
    result=research.jobs.get(job_id)
    if result and result.get('owner') not in (None,identity):result=None
    if not result:
        result=repository.get(identity,'jobs',job_id)
        if result and result['status']=='running' and time.time()-result['_updated']>90:
            result={**result,'status':'error','stage':'Interrupted','error':{'code':'job_interrupted','message':'Processing stopped before completion. Saved evidence remains available; explicitly retry your question.'}}
    if not result:
        return JSONResponse(status_code=410,content={'error':{'code':'job_expired','message':'This investigation was interrupted or expired. Please start it again.'}})
    return {k:v for k,v in result.items() if k!='owner' and not k.startswith('_')}

@app.get('/api/history')
def history(identity:str=Depends(owner)):
    from .llm import grounded_display
    # Keep the saved evidence immutable while applying current display guards
    # to old selections, just as we do for answer-cache reads.
    return {'items':[{**item,'answer':grounded_display(item['answer'])} if item.get('answer') else item
                     for item in repository.listing(identity,'history',50)]}

@app.get('/api/active-jobs')
def active_jobs(identity:str=Depends(owner)):
    return {'items':work.active(identity)}

@app.get('/api/stats')
def statistics(identity:str=Depends(owner)):
    from .usage import for_owner
    return for_owner(identity)

@app.get('/api/evidence/{evidence_id}')
def evidence(evidence_id:str):
    result=store.evidence(evidence_id)
    if result is None:
        return JSONResponse(status_code=410,content={'error':{'code':'version_unavailable','message':'This source version is no longer cached. Use the saved excerpt; the current URL may contain a newer version.'}})
    return result

@app.get('/api/source-check/{symbol}')
async def source_check(symbol:str):
    import asyncio
    symbol=ticker(symbol)
    results=await asyncio.gather(filings(),price(symbol),return_exceptions=True)
    out={}
    for name,res in zip(('filings','price'),results):
        out[name]={'status':'error','message':res.message if isinstance(res,SourceError) else 'Source unavailable'} if isinstance(res,Exception) else {
            'status':res['status'],'checked_at':res['checked_at'],
            'count':len([x for x in res['rows'] if x.get('symbol')==symbol]) if name=='filings' else len(res['chart'].get('timestamp',[]))}
    return out

@app.get('/api/capacity')
async def capacity():
    return metrics

@app.get('/api/brief')
async def portfolio_brief():
    snapshot=store.cached('brief-snapshot')
    if not snapshot:raise SourceError('snapshot_unavailable','No stored digest. Refresh sources to begin.')
    return snapshot

@app.post('/api/filings/{event_id}/assess',status_code=202)
def filing_assessment(event_id:str,request:Request,identity:str=Depends(owner)):
    mutation(request)
    snapshot=store.cached('brief-snapshot') or {'events':[]}
    event=next((e for e in snapshot['events'] if e['id']==event_id and e['kind']=='filing'),None)
    if not event:raise SourceError('event_expired','Refresh sources before reading this filing.')
    assessed=brief.valid_assessment(event_id,event['source_signature'],event['url'])
    if assessed and assessed.get('evidence'):
        return {'id':'cache','status':'complete','result':{'evidence':assessed['evidence']}}
    return work.enqueue(identity,'filing',{'event':event})


@app.get('/health')
def health():
    return {'status': 'ok', 'service': 'finn', 'python': platform.python_version(),
            'revision': os.getenv('RENDER_GIT_COMMIT', 'local')[:12]}

@app.get('/manifest.webmanifest')
def manifest():return FileResponse(ROOT/'frontend/dist/manifest.webmanifest',media_type='application/manifest+json')

@app.get('/icon.svg')
def icon():return FileResponse(ROOT/'frontend/dist/icon.svg',media_type='image/svg+xml')

@app.get('/sw.js')
def service_worker():return FileResponse(ROOT/'frontend/dist/sw.js',media_type='application/javascript',headers={'Cache-Control':'no-cache','Service-Worker-Allowed':'/'})


@app.get('/')
@app.get('/stats')
def home():
    index=ROOT/'frontend/dist/index.html'
    if index.exists():return FileResponse(index)
    return {'product':'FINN','stage':'Interface build pending','health':'/health'}
