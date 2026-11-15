"""Private, versioned thesis interpretations. Source silence remains unknown."""
import asyncio
import hashlib
import json
from . import repository,store,portfolio
from .config import MODEL
from .sources import now
from .network import SourceError

POLICY='thesis-spans-v1'


def key(holding,event):
    return hashlib.sha256(json.dumps([holding['symbol'],holding.get('thesis_version'),holding['thesis'],
        event['id'],event['revision'],event.get('assessment_policy'),POLICY,MODEL]).encode()).hexdigest()


def sources(event,thesis):
    from .brief import ASSESSMENT_POLICY
    from .documents import retrieve
    if event.get('assessment')=='pending' or event.get('assessment_policy')!=ASSESSMENT_POLICY:return []
    assessment=store.cached('assessed-'+event['id']) or {}
    version=assessment.get('version')
    if not version or assessment.get('source_signature')!=event.get('source_signature'):return []
    if not store.rehydrate(version):return []
    with store.db() as db:
        row=db.execute('SELECT meta FROM documents WHERE hash=?',(version,)).fetchone()
    if not row:return []
    doc=json.loads(row['meta'])
    if doc['symbol']!=event['symbol']:return []
    return retrieve([doc],thesis+' risks limitations contrary evidence')[:4]


def context(owner,symbol=None):
    holdings=[h for h in portfolio.book(owner)['holdings'] if h.get('thesis') and (not symbol or h['symbol']==symbol)]
    snapshot=store.cached('brief-snapshot') or {'events':[]}
    events=[e for e in snapshot['events'] if e['kind']=='filing']
    return holdings,events


async def batch(progress,owner,symbol=None,event_id=None):
    from .llm import synthesize
    holdings,events=await asyncio.to_thread(context,owner,symbol)
    if event_id:events=[e for e in events if e['id']==event_id]
    if '_thesis_tasks' not in progress:
        progress['_thesis_tasks']=[{'symbol':h['symbol'],'thesis_version':h.get('thesis_version'),
            'event_id':e['id'],'revision':e['revision']} for h in holdings for e in events if h['symbol']==e['symbol']]
        progress['thesis_total']=len(progress['_thesis_tasks']);progress['thesis_checked']=0
    while progress['_thesis_tasks']:
        task=progress['_thesis_tasks'].pop(0)
        h=next((h for h in holdings if h['symbol']==task['symbol'] and h.get('thesis_version')==task['thesis_version']),None)
        e=next((e for e in events if e['id']==task['event_id'] and e['revision']==task['revision']),None)
        if not h or not e:continue # A changed thesis/source cannot inherit a stale in-flight verdict.
        cache_key=key(h,e)
        existing=await asyncio.to_thread(repository.get,owner,'thesis_assessments',cache_key)
        if existing:progress['thesis_checked']+=1;continue
        progress['stage']='Checking thesis evidence · '+h['symbol']
        evidence=await asyncio.to_thread(sources,e,h['thesis'])
        result={'observations':[],'provider':'deterministic','model':None}
        if evidence:
            # Reinsert on failure: a retry or restart must not silently skip this filing.
            progress['_thesis_tasks'].insert(0,task)
            result=await synthesize('Investor thesis: '+h['thesis'],evidence,progress,mode='thesis')
            progress['_thesis_tasks'].pop(0)
        value={**result,'symbol':h['symbol'],'thesis_version':h.get('thesis_version'),
            'thesis':h['thesis'],'event_id':e['id'],'revision':e['revision'],'title':e['title'],
            'checked_at':now(),'policy':POLICY,'coverage':'Selected retained passages only; not a complete thesis audit.',
            'gap':None if result['observations'] else 'No relevant, readable passage established an effect. This is not supportive evidence.'}
        await asyncio.to_thread(repository.save,owner,'thesis_assessments',cache_key,value)
        progress['thesis_checked']+=1
        if evidence:break # One model flight; allow foreground Ask between filing batches.
    progress['status']='queued' if progress['_thesis_tasks'] else 'complete'
    progress['stage']=f"Thesis evidence checked for {progress['thesis_checked']} of {progress['thesis_total']} filings"


def effect(record):
    values={o['effect'] for o in (record or {}).get('observations',[])}
    return 'weakens' if 'weakens' in values else 'supports' if 'supports' in values else 'neutral' if values else 'unknown'


def assessments(owner,holdings,events):
    retained={r['id']:r for r in repository.listing(owner,'thesis_assessments',limit=5000)}
    return {e['id']:retained.get(key(h,e)) for h in holdings if h.get('thesis') for e in events
            if e['kind']=='filing' and e['symbol']==h['symbol']}


def book_health(owner,book):
    snapshot=store.cached('brief-snapshot') or {'events':[]}
    records=assessments(owner,book['holdings'],snapshot['events']) if any(h.get('thesis') for h in book['holdings']) else {}
    judgements={r['id']:r for r in repository.listing(owner,'thesis_judgements')} if records else {}
    holdings=[]
    for h in book['holdings']:
        own=[e for e in snapshot['events'] if e['kind']=='filing' and e['symbol']==h['symbol']]
        effects=[effect(records.get(e['id'])) for e in own]
        confirmed=judgements.get(h.get('thesis_version'),{}).get('broken')
        status='broken' if confirmed else 'weakening' if 'weakens' in effects else 'unknown'
        holdings.append({**h,'thesis_health':{'status':status,'supporting':effects.count('supports'),
            'adverse':effects.count('weakens'),'unknown':effects.count('unknown'),'total':len(own)}})
    return {**book,'holdings':holdings,'health_counts':{s:sum(h['thesis_health']['status']==s for h in holdings)
        for s in ('weakening','broken','unknown')}}


def detail(owner,holding,events):
    own=[e for e in events if e['kind']=='filing' and e['symbol']==holding['symbol']]
    records=assessments(owner,[holding],own)
    items=[{'event_id':e['id'],'revision':e['revision'],'title':e['title'],'effect':effect(records.get(e['id'])),
        'assessment':records.get(e['id'])} for e in own]
    confirmation=repository.get(owner,'thesis_judgements',holding.get('thesis_version') or '-')
    adverse=[item for item in items if item['effect']=='weakens']
    # Even complete selection coverage is not an exhaustive assessment of a thesis.
    status='broken' if confirmation and confirmation.get('broken') else 'weakening' if adverse else 'unknown'
    return {'status':status,'items':items,'assessed':sum(bool(i['assessment']) for i in items),'total':len(items),
        'unknown':sum(i['effect']=='unknown' for i in items),'confirmation':confirmation,
        'note':'Directions are FINN interpretations of cited passages. Unknown is not intact. Broken is your explicit judgement.',
        'history':[r for r in repository.listing(owner,'thesis_assessments') if r['symbol']==holding['symbol'] and r.get('thesis_version')!=holding.get('thesis_version')],
        'versions':[r for r in repository.listing(owner,'thesis_versions') if r['symbol']==holding['symbol']]}


def confirm(owner,symbol,version,broken):
    holding=next((h for h in portfolio.book(owner)['holdings'] if h['symbol']==symbol),None)
    if not holding or holding.get('thesis_version')!=version:raise SourceError('thesis_changed','Reload the current thesis before confirming a judgement.')
    events=(store.cached('brief-snapshot') or {'events':[]})['events']
    reviewed=detail(owner,holding,events)
    adverse=[i for i in reviewed['items'] if i['effect']=='weakens']
    if broken and not adverse:raise SourceError('evidence_required','A broken judgement requires retained adverse thesis evidence. Inspect or reassess the filings first.')
    return repository.save(owner,'thesis_judgements',version,{'broken':broken,'confirmed_at':now(),
        'sources':[i['assessment'] for i in adverse] if broken else [],'symbol':symbol,'thesis_version':version})
