"""Owner-scoped portfolio and review commands; opening never acknowledges."""
import asyncio
import csv
import io
import time
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel,Field,ConfigDict
from . import repository
from .config import PORTFOLIO
from .sources import identity,ticker
from .network import SourceError


class Holding(BaseModel):
    model_config=ConfigDict(extra='forbid')
    symbol:str=Field(min_length=1,max_length=30)
    weight:Decimal|None=Field(default=None,ge=0,le=100)
    thesis:str=Field(default='',max_length=400)
    sector:str=Field(default='',max_length=80)
    inputs:list[str]=Field(default_factory=list,max_length=10)


def book(owner):
    saved=repository.get(owner,'state','book')
    if saved:return saved
    default={'holdings':[{'symbol':s,'weight':None,'thesis':'','sector':'','inputs':[]} for s in PORTFOLIO],
             'is_demo':True,'label':'Demonstration book · weights and theses not supplied'}
    try:return repository.save(owner,'state','book',default,expected=0)
    except repository.Conflict:return repository.get(owner,'state','book')


async def validate_holdings(rows):
    if len(rows)>50:raise SourceError('invalid_book','A book can contain at most 50 holdings.')
    items=[];seen=set();total=Decimal(0)
    for row in rows:
        h=Holding.model_validate(row);symbol=ticker(h.symbol)
        if symbol in seen:raise SourceError('invalid_book','Duplicate symbol: '+symbol)
        seen.add(symbol);total+=h.weight or 0
        items.append({**h.model_dump(mode='json'),'symbol':symbol})
    if total>100:raise SourceError('invalid_book','Entered weights exceed 100%. FINN never silently normalises them.')
    semaphore=asyncio.Semaphore(4)
    async def resolve(item):
        async with semaphore:
            company=await identity(item['symbol'])
            return {**item,'name':company['name'],'isin':company.get('isin')}
    return await asyncio.gather(*(resolve(item) for item in items))


async def save_book(owner,rows,version):
    # Resolve all identities before atomic save; partial imports never change Book.
    validated=await validate_holdings(rows)
    import uuid
    from .sources import now
    # One transaction commits the book and immutable thesis revision records.
    # A changed weight never rewrites a thesis or its earlier interpretation.
    with repository.transaction() as tx:
        previous=repository.get(owner,'state','book',tx) or {'holdings':[]}
        old={h['symbol']:h for h in previous['holdings']}
        for holding in validated:
            before=old.get(holding['symbol'],{})
            if holding['thesis']==before.get('thesis','') and before.get('thesis_version'):
                holding['thesis_version']=before['thesis_version']
            elif holding['thesis'] or before.get('thesis'):
                revision=uuid.uuid4().hex;holding['thesis_version']=revision
                repository.save(owner,'thesis_versions',revision,{'symbol':holding['symbol'],
                    'thesis':holding['thesis'],'previous_version':before.get('thesis_version'),'created_at':now()},expected=0,tx=tx)
        return repository.save(owner,'state','book',{'holdings':validated,'is_demo':False,'label':'Your book'},expected=version,tx=tx)


def parse_import(text):
    if len(text)>40000:raise SourceError('invalid_import','Import exceeds 40,000 characters.')
    lines=[line.strip() for line in text.splitlines() if line.strip()]
    if not lines:return []
    if ',' in lines[0] and any(h in lines[0].lower().split(',') for h in ('symbol','ticker')):
        rows=list(csv.DictReader(io.StringIO('\n'.join(lines))))
        return [{'symbol':r.get('symbol') or r.get('ticker') or '', 'weight':r.get('weight') or None,
                 'thesis':r.get('thesis') or '', 'sector':r.get('sector') or '', 'inputs':[]} for r in rows]
    # Plain paste accepts symbols separated by whitespace, commas or semicolons.
    import re
    return [{'symbol':part} for part in re.split(r'[\s,;]+',text.strip()) if part]


def view_review(state,visit_id=None):
    result={k:v for k,v in state.items() if k!='visits'}
    if visit_id:result['visit']=state.get('visits',{}).get(visit_id)
    return result


def review(owner,visit_id=None):
    state=repository.get(owner,'state','review') or {'reviewed':{},'pins':{},'feedback':{},'promotions':[],
        'known':{},'eligible':{},'visit':None,'_version':0}
    return view_review(state,visit_id) if visit_id else state


def update_review(owner,action,event_id='',revision='',value=None,events=(),visit_id=None):
    for attempt in range(5):
        state=review(owner);version=state['_version'];stamp=time.time()
        if action=='visit':
            for event in events:
                children=event.get('children',[])
                material=[c for c in children if c.get('assessment')!='routine'] or children
                if material and all(state['reviewed'].get(c['id'])==c['revision'] for c in material):
                    state['reviewed'][event['id']]=event['revision']
                if any(state['pins'].get(c['id']) for c in children):state['pins'][event['id']]=True
                if any(state.get('eligible',{}).get(c['id'])==c['revision'] for c in material):
                    state.setdefault('eligible',{})[event['id']]=event['revision']
            previous=state['visit']
            visit=state.setdefault('visits',{}).get(visit_id) if visit_id else previous
            if not visit or stamp-visit['active_at']>=1800:
                visit={'opened_at':stamp,'active_at':stamp,
                    'cutoff':previous['opened_at'] if previous else stamp-86400,'first':previous is None,
                    'returning':bool(previous and stamp-previous['opened_at']>=172800)}
                state['visit']=dict(visit)
            else:visit={**visit,'active_at':stamp}
            if visit_id:
                state['visits'][visit_id]=visit
                if len(state['visits'])>50:
                    state['visits']=dict(sorted(state['visits'].items(),key=lambda item:item[1]['active_at'])[-50:])
            else:state['visit']=visit
            known=state.setdefault('known',{});eligible=state.setdefault('eligible',{})
            for event in events:
                published=datetime.fromisoformat(event['published_at']).timestamp() if event.get('published_at') else None
                if known.get(event['id'])!=event['revision'] and (
                    event['id'] in known or not visit['first'] or published is None or published>=visit['cutoff']):
                    eligible[event['id']]=event['revision']
                known[event['id']]=event['revision']
        elif action=='review':
            state['reviewed'][event_id]=revision
            event=next((e for e in events if e['id']==event_id and e['revision']==revision),None)
            if event:
                for child in event.get('children',[]):state['reviewed'][child['id']]=child['revision']
        elif action=='undo':
            state['reviewed'].pop(event_id,None)
            event=next((e for e in events if e['id']==event_id),None)
            if event:
                for child in event.get('children',[]):state['reviewed'].pop(child['id'],None)
        elif action=='pin':
            if value:state['pins'][event_id]=True
            else:state['pins'].pop(event_id,None)
        elif action=='feedback':
            if value not in ('mattered','noise',None):raise SourceError('invalid_feedback','Choose Mattered, Noise or clear feedback.')
            if value:state['feedback'][event_id]=value
            else:state['feedback'].pop(event_id,None)
            event=next((e for e in events if e['id']==event_id),None)
            if event:
                category=event.get('category') or event.get('description','').split(' · ')[0] or event['kind']
                preferences=state.setdefault('category_feedback',{}).setdefault(category,{})
                if value:preferences[event_id]=value
                else:preferences.pop(event_id,None)
                while len(preferences)>20:preferences.pop(next(iter(preferences)))
        elif action=='promote':
            event=next((e for e in events if e['id']==event_id),None)
            if not event:raise SourceError('event_expired','Reload the disclosure before changing its routing.')
            category=event.get('category') or event.get('description','').split(' · ')[0]
            if not category:raise SourceError('unknown_category','This disclosure has no verified category to promote.')
            if value and category not in state['promotions']:state['promotions'].append(category)
            if not value:state['promotions']=[p for p in state['promotions'] if p!=category]
        else:raise SourceError('invalid_action','Unknown review action.')
        try:return view_review(repository.save(owner,'state','review',state,expected=version),visit_id)
        except repository.Conflict:
            if attempt==4:raise


def rank(events,holdings,state,thesis_records=None):
    by_symbol={h['symbol']:h for h in holdings};ranked=[]
    for event in events:
        if event['symbol'] not in by_symbol:continue
        holding=by_symbol[event['symbol']];weight=holding.get('weight')
        critical=event['tier']==0;routine=event['assessment']=='routine'
        base=80 if critical else 45 if event['kind']=='price' else 30 if event['assessment']=='pending' else 35
        reasons=[{'label':'Disclosure category','value':base,'explanation':event['reason'],
                  'evidence':event.get('evidence',[])[:1]}]
        score=Decimal(base)
        from .theses import effect
        thesis_record=(thesis_records or {}).get(event['id'])
        thesis_effect=effect(thesis_record)
        if thesis_effect=='weakens':
            score+=15
            reasons.append({'label':'Adverse thesis evidence','value':15,'explanation':'FINN interpretation; inspect the cited passage against your thesis.',
                'evidence':[s['evidence'] for o in thesis_record['observations'] if o['effect']=='weakens' for s in o['sources']]})
        if weight is not None:
            addition=Decimal(base)*Decimal(str(weight))/100;score+=addition
            reasons.append({'label':'Position weight','value':float(addition),'explanation':str(weight)+'% entered allocation'})
        feedback=state['feedback'].get(event['id']);adjustment=5 if feedback=='mattered' else -5 if feedback=='noise' else 0
        category=event.get('category') or event.get('description','').split(' · ')[0] or event['kind']
        history=state.get('category_feedback',{}).get(category,{})
        if history:
            adjustment=5*sum(1 if value=='mattered' else -1 for value in history.values())/len(history)
            feedback='Category feedback, bounded to ±5 points'
        adjustment=Decimal(str(adjustment))
        score+=adjustment
        if feedback:reasons.append({'label':'Your feedback','value':float(adjustment),'explanation':feedback})
        promoted=category in state['promotions']
        if promoted:reasons.append({'label':'Your routing preference','value':0,'explanation':'You promoted this disclosure category out of Buried.'})
        tier=0 if critical or score>=60 else 3 if routine and not promoted else 1
        ranked.append({**event,'tier':tier,'score':float(score),'ranking_reasons':reasons,
                       'weight':weight,'thesis':holding.get('thesis',''),'thesis_status':thesis_effect,'thesis_assessment':thesis_record,'promoted':promoted,
                       'ranking_note':'Guidance surprise is excluded until comparable facts are verified. Thesis interpretations never remove the critical-event floor.'})
    return sorted(ranked,key=lambda e:(e['tier'],-e['score'],-datetime.fromisoformat(e['published_at']).timestamp() if e['published_at'] else 0,e['id']))
