"""Authenticated external wake-up; bounded source-only work, no Telegram/LLM."""
import asyncio,json,os,secrets
from datetime import datetime,timezone
from . import repository,work,brief,watches,portfolio
from .config import PORTFOLIO
from .network import SourceError
from .sources import now
from .numbers import IST


def configured():return os.getenv('FINN_SCHEDULER_ENABLED','false')=='true' and len(os.getenv('FINN_SCHEDULER_TOKEN',''))>=32


def authenticate(header):
    token=os.getenv('FINN_SCHEDULER_TOKEN','')
    if not configured():raise SourceError('scheduler_disabled','Unattended refresh is not connected.')
    provided=header.removeprefix('Bearer ') if header.startswith('Bearer ') else ''
    return bool(provided) and secrets.compare_digest(provided,token)


def submit(at=None):
    at=at or datetime.now(timezone.utc)
    slot=at.strftime('%Y-%m-%d')+('-morning' if at.hour<8 else '-evening')
    return work.enqueue('_scheduler','scheduled_refresh',{'slot':slot},once=True)


def targets():
    # Only configured rules/reminders trigger owner evaluation. Public demo
    # observations refresh separately; private questions never enter this job.
    with repository.transaction() as tx:
        rows=tx.execute("SELECT owner,bucket,value FROM records WHERE bucket IN ('rules','reminders') ORDER BY updated DESC LIMIT 5001").fetchall()
    owners=set();symbols=set(PORTFOLIO);active=0
    for row in rows:
        record=json.loads(row['value'])
        if row['bucket']=='rules' and record.get('rule',{}).get('enabled'):
            owners.add(row['owner']);symbols.add(record['rule']['symbol']);active+=1
        elif row['bucket']=='reminders' and record.get('enabled'):
            owners.add(row['owner']);symbols.add(record['event']['symbol']);active+=1
    for owner in owners:
        symbols.update(h['symbol'] for h in portfolio.book(owner)['holdings'])
    # No silently truncated book. If the free-service batch cannot cover the
    # configured scope, retain the last dated snapshot and expose the failure.
    # Capacity counts enabled rules and reminders only; disabled rows cost nothing.
    if len(symbols)>100 or active>=1000 or len(rows)>5000:
        raise SourceError('schedule_capacity','Scheduled scope exceeds this free service’s bounded batch. Explicit per-book refresh remains available.')
    return sorted(owners),sorted(symbols)


def reminders(owner,at):
    snapshot=brief.store.cached('brief-snapshot') or {'events':[]}
    # Keep explicit past/cancelled notices for lifecycle reconciliation. A
    # missing notice in a rolling source window is not proof of cancellation.
    current={}
    for filing in sorted(snapshot['events'],key=lambda e:e.get('published_at') or ''):
        for event in filing.get('upcoming_dates',[]):
            current[(event['symbol'],event['date'],event['kind'])]=event
    for saved in repository.listing(owner,'reminders'):
        if not saved.get('enabled'):continue
        event=saved['event'];key=(event['symbol'],event['date'],event['kind'])
        fresh=current.get(key)
        today=at.astimezone(IST).date().isoformat()
        if fresh and fresh.get('replacement_date'):status='rescheduled_review_required'
        elif fresh and fresh['status']=='cancelled':status='cancelled'
        elif event['date']<today:status='past_date_not_delivered'
        elif not fresh:status='date_no_longer_in_current_coverage'
        else:status='due_today' if event['date']==today else 'scheduled'
        repository.save(owner,'reminder_status',saved['id'],{'event':event,'latest_notice':fresh,'status':status,'checked_at':now(),
            'delivery':'in_app','note':'Open FINN to view this reminder. Telegram and push delivery are disabled.'})


async def run(progress):
    stamp=progress.setdefault('_schedule_started_at',now())
    try:
        if '_assessment_ids' not in progress:
            owners,symbols=await asyncio.to_thread(targets)
            progress['stage']='Refreshing scheduled public sources'
            snapshot=await brief.get_brief(force=True,symbols=symbols,background=False)
            progress['_schedule_owners']=owners;progress['_schedule_symbols']=symbols
            progress['_assessment_ids']=[e['id'] for e in snapshot['events'] if e['symbol'] in symbols and e['kind']=='filing' and (e['assessment']=='pending' or e.get('assessment_policy')!=brief.ASSESSMENT_POLICY)]
            progress.update(attachments_total=len(progress['_assessment_ids']),attachments_checked=0,attachments_failed=0)
        owners,symbols=progress['_schedule_owners'],progress['_schedule_symbols']
        await work.assess_batch(progress)
        if progress['_assessment_ids']:
            progress.update(status='queued',stage=f"{progress['attachments_checked']} of {progress['attachments_total']} scheduled attachments checked")
            return
        snapshot=brief.store.cached('brief-snapshot')
        for owner in owners:
            await asyncio.to_thread(watches.evaluate_owner,owner,snapshot)
            await asyncio.to_thread(reminders,owner,datetime.now(timezone.utc))
        status={'status':'complete','checked_at':now(),'started_at':stamp,'symbols_checked':len(symbols),
            'note':'Best-effort scheduled refresh; inspect per-source coverage. No model inference or Telegram sending.'}
        repository.save('_public','operations','scheduler',status)
        progress.update(status='complete',stage='Scheduled sources checked',result=status)
    except Exception as exc:
        repository.save('_public','operations','scheduler',{'status':'error','checked_at':now(),'started_at':stamp,
            'message':exc.message if isinstance(exc,SourceError) else 'Scheduled refresh did not complete. Prior dated observations remain available.'})
        raise
