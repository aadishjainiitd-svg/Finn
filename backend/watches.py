"""Explicit, non-executable rule grammar and one evaluator for replay and live runs."""
import re
import uuid
from datetime import datetime,timezone,timedelta
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel,ConfigDict,Field
from . import repository,store
from .numbers import daily_signal,IST,decimal
from .sources import ticker,identity
from .network import SourceError


class Rule(BaseModel):
    model_config=ConfigDict(extra='forbid')
    symbol:str=Field(min_length=1,max_length=30)
    metric:Literal['price_rise','price_fall','price_move','volume','category']
    operator:Literal['gt','gte']='gte'
    threshold:Decimal|None=Field(default=None,gt=0,le=10000)
    category:Literal['results','management','audit','capital','credit']|None=None
    enabled:bool=True
    channel:Literal['in_app','telegram']='in_app'
    rationale:str=Field(default='',max_length=1200)


def draft(sentence):
    """Full-string grammar: never quietly drop an unsupported trailing clause."""
    text=sentence.strip().rstrip('.').strip()
    prefix=r'(?:alert me (?:when|if) |notify me (?:when|if) |watch )?'
    symbol=r'(?P<symbol>[A-Z][A-Z0-9&-]{0,24})'
    comparison=r'(?P<op>at least|more than|above|over)'
    number=r'(?P<value>\d+(?:\.\d+)?)'
    patterns=[(prefix+symbol+r' (?P<direction>rises|falls|moves) '+comparison+r' '+number+r'\s*%(?: (?:in a day|daily))?','price'),
              (prefix+symbol+r'(?: volume is| volume exceeds) '+comparison+r' '+number+r'\s*(?:x|×|times)(?: (?:usual|average|its usual)(?: volume)?)?','volume')]
    for pattern,kind in patterns:
        m=re.fullmatch(pattern,text,re.I)
        if not m:continue
        metric='volume' if kind=='volume' else {'rises':'price_rise','falls':'price_fall','moves':'price_move'}[m['direction'].lower()]
        return Rule(symbol=ticker(m['symbol']),metric=metric,operator='gte' if m['op'].lower()=='at least' else 'gt',threshold=m['value']).model_dump(mode='json')
    m=re.fullmatch(prefix+symbol+r' (?:files|announces) (?P<category>results|management|audit|capital|credit)(?: disclosures?)?',text,re.I)
    if m:return Rule(symbol=ticker(m['symbol']),metric='category',category=m['category'].lower()).model_dump(mode='json')
    raise SourceError('unsupported_rule','Use a supported rule such as “TCS falls more than 5%”, “TCS volume is at least 2x usual”, or “TCS files results”. Other conditions need clarification; no weaker rule was saved.')


def describe(rule):
    rule=Rule.model_validate(rule)
    if rule.metric=='category':return f'{rule.symbol} files a {rule.category} disclosure'
    operator='at least' if rule.operator=='gte' else 'more than'
    metric={'price_rise':'rises','price_fall':'falls','price_move':'moves','volume':'volume is'}[rule.metric]
    return f'{rule.symbol} {metric} {operator} {rule.threshold}'+('× its prior-20-session average' if rule.metric=='volume' else '% in a completed session')


def evaluate(rule,signal):
    rule=Rule.model_validate(rule)
    if rule.metric=='category':return None
    op=signal.get('operands',{})
    try:
        if rule.metric=='volume':
            if signal.get('volume_multiple') is None:return None
            value=decimal(op.get('current_volume'))/decimal(op.get('average_previous_20_volume'))
        else:
            if signal.get('change_percent') is None:return None
            value=(decimal(op.get('current_close'))/decimal(op.get('previous_close'))-1)*100
            if rule.metric=='price_fall':value=-value
            if rule.metric=='price_move':value=abs(value)
        return value>=rule.threshold if rule.operator=='gte' else value>rule.threshold
    except (ValueError,TypeError,ArithmeticError):return None


def preview(rule,chart):
    rule=Rule.model_validate(rule).model_dump(mode='json')
    if rule['metric']=='category':return {'status':'unavailable','message':'A complete historical filing interval is required for category replay. No count inferred.','eligible_sessions':0,'firings':[]}
    sessions=[];now=datetime.now(timezone.utc)
    for stamp in chart.get('timestamp',[]):
        day=datetime.fromtimestamp(stamp,IST)
        close=datetime.combine(day.date(),datetime.min.time(),IST)+timedelta(hours=16)
        if close>now:continue
        signal=daily_signal(chart,close)
        fired=evaluate(rule,signal)
        if not sessions or sessions[-1]['session']!=signal.get('session'):
            sessions.append({'session':signal.get('session'),'fired':fired,'signal':signal})
    last=sessions[-30:];eligible=sum(x['fired'] is not None for x in last)
    return {'status':'complete' if eligible==30 else 'partial','evaluated_sessions':len(last),'eligible_sessions':eligible,
            'requested_sessions':30,'firings':[x for x in last if x['fired']],
            'message':f'{eligible} of 30 requested completed sessions have comparable inputs. Current session is excluded from its own volume baseline.',
            'sessions':last}


MAX_ENABLED_RULES=25


async def save(owner,data,rule_id=None,version=0):
    rule=Rule.model_validate(data);rule.symbol=ticker(rule.symbol)
    await identity(rule.symbol)
    if rule.metric=='category' and not rule.category:raise SourceError('invalid_rule','Choose a disclosure category.')
    if rule.metric!='category' and rule.threshold is None:raise SourceError('invalid_rule','Enter a positive threshold.')
    if rule.channel=='telegram':raise SourceError('delivery_unavailable','Connect and verify Telegram before enabling that delivery channel. In-app watches are available.')
    import time
    previous=repository.get(owner,'rules',rule_id) if rule_id else None
    if rule.enabled and not (previous and previous.get('rule',{}).get('enabled')):
        enabled=sum(1 for r in repository.listing(owner,'rules') if r.get('rule',{}).get('enabled'))
        if enabled>=MAX_ENABLED_RULES:
            raise SourceError('rule_limit',f'Up to {MAX_ENABLED_RULES} watches can be on at once. Turn one off before adding another.')
    return repository.save(owner,'rules',rule_id or uuid.uuid4().hex,{'rule':rule.model_dump(mode='json'),
        'sentence':describe(rule),'delivery_status':'in_app_only','created_at':previous.get('created_at',time.time()) if previous else time.time(),
        'active_since':time.time()},expected=version)


def evaluate_owner(owner,snapshot):
    """Replay and live evaluation share operands; store each firing once.

    A rule starts at confirmation, never retrospectively notifies for a preview.
    Correlated disclosures are context, never an asserted cause of a move.
    """
    import hashlib,time
    from . import store
    from .events import category
    made=0;gaps=[]
    for saved in repository.listing(owner,'rules'):
        rule=Rule.model_validate(saved['rule'])
        if not rule.enabled:continue
        since=saved.get('active_since',saved['_updated']);matches=[]
        own=[e for e in snapshot['events'] if e['symbol']==rule.symbol and e['kind']=='filing']
        if rule.metric=='category':
            for event in own:
                if not event.get('published_at'):continue
                if datetime.fromisoformat(event['published_at']).timestamp()<since:continue
                if event['assessment']=='pending':
                    gaps.append({'rule_id':saved['id'],'message':'Unread filings remain unevaluated.'});continue
                if category(event)==rule.category:
                    matches.append({'identity':event['id']+'-'+event['revision'],'event':event,
                        'observed_at':event['published_at'],'context_label':'Matching assessed disclosure'})
        else:
            data=store.cached('price-'+rule.symbol)
            if not data:
                gaps.append({'rule_id':saved['id'],'message':'No stored daily bars.'});continue
            replay=preview(rule,data['chart'])
            if replay['status']!='complete':gaps.append({'rule_id':saved['id'],'message':replay['message']})
            for firing in replay['firings']:
                closed=datetime.fromisoformat(firing['session']+'T15:30:00+05:30')
                if closed.timestamp()<since:continue
                context=[e for e in own if e.get('published_at') and abs(datetime.fromisoformat(e['published_at']).timestamp()-closed.timestamp())<=172800]
                matches.append({'identity':firing['session'],'observed_at':closed.isoformat(),'signal':firing['signal'],
                    'filing_context':context,'context_label':'Disclosures within 48 hours; causality not established' if context else 'No matching disclosure found; move unexplained'})
        for match in matches:
            key=hashlib.sha256(f"{saved['id']}:{saved['_version']}:{match['identity']}".encode()).hexdigest()
            try:
                repository.save(owner,'firings',key,{'rule_id':saved['id'],'rule_version':saved['_version'],
                    'symbol':rule.symbol,'sentence':saved['sentence'],'rule':saved['rule'],
                    'evaluated_at':datetime.now(timezone.utc).isoformat(),'delivery':'in_app','observation':match},expected=0)
                made+=1
            except repository.Conflict:pass
    repository.save(owner,'state','watch_evaluation',{'checked_at':datetime.now(timezone.utc).isoformat(),
        'source_checked_at':snapshot['checked_at'],'gaps':gaps,'new_firings':made})
    return made
