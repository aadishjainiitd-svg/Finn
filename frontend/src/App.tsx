import React,{useEffect,useRef,useState} from 'react';

import {api,followJob} from './api';

import type {Brief,Evidence,Job} from './types';

import {type Session,type RankedEvent,type Review,type Holding,type Book,reviewed,inPeriod,date,weekday,thesisLabel,eventType,displayTitle,typeTone,noticeLine,ago} from './product';

import {Glyph,Notice,Pill,Sheet,Skeleton} from './ui';

import {EvidenceView,Research,PriceView} from './legacy';

import {BookView} from './Book';

import {WatchView} from './Watch';

import {ResearchPack} from './ResearchPack';
import {GuidanceCard} from './Guidance';

import {HoldingDetail} from './Holding';

import {GestureCard} from './GestureCard';

import {Stats} from './Stats';

import {Recap,recapText} from './Recap';

import {useNavigation,type Tab} from './useNavigation';

import {Results,ResultsSummary} from './Results';

import {ThesisEvidence} from './Thesis';

import {EventTimeline} from './EventTimeline';

import {readStored,saveStored,type ReviewState} from './state';

import './product.css';



type Panel={kind:'event';event:RankedEvent}|{kind:'evidence';evidence:Evidence}|{kind:'coverage'}|{kind:'holding';holding:Holding}|{kind:'voice';recap?:boolean}|{kind:'week'}|{kind:'stats'}|null;

const tabs:Tab[]=['today','research','ask','watch','book'];



export default function App(){

 const [lastDone,setLastDone]=useState<RankedEvent|null>(null);const [session,setSession]=useState<Session|null>(null);const [brief,setBrief]=useState<Brief|null>(null);

 const [offline,setOffline]=useState(!navigator.onLine);const [reconnected,setReconnected]=useState(false);const [loading,setLoading]=useState(true);const [error,setError]=useState('');const [window,setWindow]=useState('since');const [tier,setTier]=useState('needs');

 const [reminders,setReminders]=useState<{event:{event_id:string;date:string;kind:string};enabled:boolean}[]>([]);const [reminderStatuses,setReminderStatuses]=useState<{id:string;status:string;event:{symbol:string;date:string;kind:string};latest_notice?:{replacement_date?:string}}[]>([]);const [reminderNotice,setReminderNotice]=useState('');const [watchOrigin,setWatchOrigin]=useState<{symbol:string;rationale:string}|null>(null);const [pending,setPending]=useState<Brief|null>(null);const [refreshing,setRefreshing]=useState(false);const [refreshStage,setRefreshStage]=useState('');

 const [start,setStart]=useState('');const [end,setEnd]=useState('');const [panel,setPanel]=useState<Panel>(location.pathname==='/stats'?{kind:'stats'}:null);const [nested,setNested]=useState<Evidence|null>(null);

 const [context,setContext]=useState<{symbol:string;event?:RankedEvent;question?:string;nonce:number}|null>(null);const [reading,setReading]=useState(false);const [speaking,setSpeaking]=useState(false);const [rate,setRate]=useState(1);

 const trigger=useRef<HTMLElement|null>(null);const request=useRef(0);

 const evidenceTrigger=useRef<HTMLElement|null>(null);

 const open=(next:Panel)=>{request.current++;trigger.current=document.activeElement as HTMLElement;setPanel(next);setError('');};

 const close=()=>{request.current++;setPanel(null);setReading(false);if(location.pathname==='/stats')history.replaceState(history.state,'','/');};

 const {tab,navigate:changeTab}=useNavigation(!loading,close);const visited=useRef(new Set<Tab>());visited.current.add(tab);

 async function load(){setLoading(true);setError('');setReconnected(false);if(!navigator.onLine){const saved=readStored<{session:Session;brief:Brief}>('finn.offline.v1');if(saved){setSession(saved.session);setBrief(saved.brief);}else setError('No saved brief is available on this device. Reconnect to load one.');setLoading(false);return;}try{const s=await api<Session>('/api/session');setSession(s);const b=await api<Brief>('/api/today');setBrief(b);setLoading(false);const old=readStored<ReviewState>('finn.review.v1');if(old?.version===1)await api('/api/review/migrate',{known:old.known,reviewed:old.reviewed,eligible:old.eligible});const r=await api<Review>('/api/review',{action:'visit'});setSession(current=>current?{...current,review:r._version>=current.review._version?r:current.review}:{...s,review:r});}catch(e){setError((e as Error).message);}finally{setLoading(false);}}

 useEffect(()=>{const changed=()=>{setOffline(!navigator.onLine);if(navigator.onLine)setReconnected(true);};addEventListener('online',changed);addEventListener('offline',changed);return()=>{removeEventListener('online',changed);removeEventListener('offline',changed);};},[]);

 useEffect(()=>{if(session&&brief&&!loading&&navigator.onLine)saveStored('finn.offline.v1',{session,brief});},[session,brief,loading]);

 useEffect(()=>{load();return()=>{if('speechSynthesis' in globalThis)speechSynthesis.cancel();};},[]);

 useEffect(()=>{const timer=setInterval(()=>{if(document.visibilityState==='visible'&&navigator.onLine)api<Brief>('/api/today').then(data=>{

   setPending(data);setBrief(current=>current?{...current,coverage:data.coverage,source_status:data.source_status}:data);

 }).catch(()=>setError('Source coverage could not be refreshed. The previous observation is still shown.'));},60000);return()=>clearInterval(timer);},[]);

 async function refreshSources(){setRefreshing(true);setError('');try{const first=await api<Job>('/api/refresh',{});const result=await followJob(first,j=>setRefreshStage(j.stage),()=>true);if(result?.status==='error')throw new Error(result.error?.message);const updated=await api<Brief>('/api/today');setPending(updated);setRefreshStage('Sources refreshed. Apply the new snapshot when ready.');}catch(e){setError((e as Error).message);}finally{setRefreshing(false);}}

 async function change(action:string,event?:RankedEvent,value?:string|boolean|null){try{const r=await api<Review>('/api/review',{action,event_id:event?.id,revision:event?.revision,value});setSession(s=>s?{...s,review:r._version>=s.review._version?r:s.review}:s);if(action==='review'&&event)setLastDone(event);if(action==='undo')setLastDone(null);if(action==='feedback'||action==='promote')setBrief(await api<Brief>('/api/today'));}catch(e){setError((e as Error).message);}}

 function navigate(next:Tab,symbol?:string,event?:RankedEvent){changeTab(next);if(symbol)setContext({symbol,event:event?{...event,id:event.lead_filing_id||event.id}:undefined,nonce:Date.now()});}

 async function read(event:RankedEvent){evidenceTrigger.current=document.activeElement as HTMLElement;const generation=++request.current;setReading(true);try{let evidence=event.evidence;if(!evidence.length){const first=await api<Job>('/api/filings/'+encodeURIComponent(event.lead_filing_id||event.id)+'/assess',{});const result=await followJob(first,()=>{},()=>request.current===generation);if(result?.status==='error')throw new Error(result.error?.message);evidence=result?.result?.evidence||[];}if(request.current===generation&&evidence.length)setNested(evidence[0]);}catch(e){if(request.current===generation)setError((e as Error).message);}finally{if(request.current===generation)setReading(false);}}

 useEffect(()=>{if(panel?.kind==='week')api<{items:typeof reminders;statuses:typeof reminderStatuses}>('/api/reminders').then(r=>{setReminders(r.items);setReminderStatuses(r.statuses||[]);}).catch(e=>setError(e.message));},[panel?.kind]);

 const events=(brief?.events||[]) as RankedEvent[];

 const visible=events.filter(e=>inPeriod(e,window,session?.review,start,end));
 // A first visit with nothing in the last 24 hours opens on the last 14 days
 // instead of an empty screen, and says so. Only once, never on return visits.
 const widened=useRef(false);const [autoWide,setAutoWide]=useState(false);
 useEffect(()=>{if(widened.current||loading||!brief||!session?.review.visit?.first||window!=='since')return;widened.current=true;
  if(!visible.length&&events.some(e=>inPeriod(e,'14',session?.review,start,end))){setWindow('14');setAutoWide(true);}},[loading,brief,session,window,visible.length]);

 const active=visible.filter(e=>e.tier!==3);const buried=visible.filter(e=>e.tier===3);

 const needs=active.filter(e=>e.tier===0&&!reviewed(session?.review,e)).length;

 const pinned=events.filter(e=>session?.review.pins[e.id]&&!reviewed(session?.review,e)).sort((a,b)=>a.id.localeCompare(b.id));

 const needsTier=active.filter(e=>e.tier===0);const worthTier=active.filter(e=>e.tier!==0);
 const shown=(tier==='buried'?buried:tier==='needs'?needsTier:tier==='worth'?worthTier:active).filter(e=>!pinned.some(p=>p.id===e.id));

 const nextDate=brief?.upcoming?.filter(d=>d.status!=='cancelled'&&Date.parse(d.date)>=Date.now()).sort((a,b)=>a.date.localeCompare(b.date))[0];

 const newItem=(e:RankedEvent)=>!!e.published_at&&Date.parse(e.published_at)/1000>=(session?.review.visit?.cutoff||0);

 const checked=brief?.coverage.filter(c=>c.filings.status==='live').length||0;
 const sourced=brief?.coverage.filter(c=>c.filings.status==='live'||c.filings.status==='stale').length||0;const stale=!!brief?.coverage.some(c=>c.filings.status==='stale');

 const updates=pending?.events.filter(e=>!brief?.events.some(old=>old.id===e.id&&old.revision===e.revision)).length||0;

 const voiceText=panel?.kind==='voice'&&panel.recap&&session?recapText(events,session.review):`FINN. Stored digest checked ${date(brief?.checked_at,true)}. ${needs} events need review. `+[...pinned,...shown].map(e=>`${e.symbol}. ${e.title}. ${e.reason}.`).join(' ')+' Prices are completed-session observations. Source coverage may be incomplete.';

 function speak(){if(!('speechSynthesis' in globalThis)){setError('Speech playback is unavailable in this browser. Read the transcript below.');return;}speechSynthesis.cancel();const utterance=new SpeechSynthesisUtterance(voiceText);utterance.rate=rate;utterance.onend=()=>setSpeaking(false);utterance.onerror=()=>setSpeaking(false);speechSynthesis.speak(utterance);setSpeaking(true);}

 const weighted=!!session?.book.holdings.length&&session.book.holdings.every(h=>h.weight!=null&&Number(h.weight)>0);
 const titles={today:`${needs} ${needs===1?'thing needs':'things need'} you`,research:'Understand the business.',ask:'Ask what matters.',watch:'Keep an eye on it.',book:'Your book.'};

 const renderEvent=(e:RankedEvent)=><GestureCard disabled={offline} onDone={()=>change(reviewed(session?.review,e)?'undo':'review',e)} onPin={()=>change('pin',e,!session?.review.pins[e.id])} onPromote={e.assessment==='routine'?()=>change('promote',e,!e.promoted):undefined} className={'fn-c fn-card tier-'+(e.assessment==='pending'?'p':e.tier)+(reviewed(session?.review,e)?' fn-reviewed':'')} key={e.id}><button className="fn-open" onClick={()=>open({kind:'event',event:e})}><div className="fn-flex"><span className={'fn-ic type-'+typeTone(e)}><Glyph name={e.kind==='price'?'chart':'file'}/></span><div className="fn-grow"><div className="fn-row"><span className="fn-grow"><strong>{e.name&&e.name!==e.symbol?e.name:e.symbol}</strong>{e.name&&e.name!==e.symbol&&<span className="fn-f fn-m"> {e.symbol}</span>}</span><span className="fn-f fn-m">{date(e.published_at)}</span></div><span className="fn-f fn-m">{eventType(e)}{e.weight==null?'':` · ${e.weight}% of book`} · {newItem(e)?<span className="fn-new">New</span>:'Outstanding'}</span></div></div><h3 className="fn-gap fn-cardtitle">{displayTitle(e.title)}</h3>{noticeLine(e)&&<p className="fn-noticeline"><span className="fn-noticetag">NSE notice</span> {noticeLine(e)}</p>}<div className="fn-tags fn-gap">{(e.assessment==='pending'||tier==='all')&&<Pill tone={e.tier===0?'red':e.assessment==='pending'?'amber':''}>{e.assessment==='pending'?'Not yet assessed':e.tier===0?'Needs you':e.tier===3?'Routine':'Worth knowing'}</Pill>}{session?.review.pins[e.id]&&<Pill>Pinned</Pill>}</div><p className="fn-gap fn-m">{e.reason}</p><ResultsSummary result={e.results}/>{e.thesis&&<div className="fn-tags fn-gap"><Pill tone={thesisLabel(e.thesis_status)[1]}>{thesisLabel(e.thesis_status)[0]}</Pill></div>}</button><div className="fn-row fn-cardactions"><button className="fn-hit" onClick={()=>change(reviewed(session?.review,e)?'undo':'review',e)}><Glyph name="check" size={16}/>{reviewed(session?.review,e)?'Reviewed · Undo':'Mark done'}</button><button className="fn-close" onClick={()=>change('pin',e,!session?.review.pins[e.id])} aria-label={session?.review.pins[e.id]?'Unpin '+e.symbol:'Pin '+e.symbol} aria-pressed={!!session?.review.pins[e.id]}><Glyph name="pin" size={16}/></button></div>{(e.assessment==='routine'||e.promoted)&&<button className="fn-hit" aria-pressed={!!e.promoted} onClick={()=>change('promote',e,!e.promoted)}>{e.promoted?'Undo category promotion':'Promote this category'}</button>}</GestureCard>;

 return <div className="fn-app"><a className="skip" href="#main">Skip to content</a><header className="fn-hd"><div className="fn-date"><span className="fn-m">{weekday(new Date())}</span><button className="fn-close" aria-label="Open statistics" onClick={()=>open({kind:'stats'})}><Glyph name="chart"/></button></div><h1>{tab==='today'?(loading?'Opening your brief…':!brief?'Brief unavailable.':!needs&&visible.some(e=>e.assessment==='pending')?'Changes to check.':titles[tab]):titles[tab]}</h1>

 {tab==='today'?<><div className="fn-row fn-window"><label className="sr-only" htmlFor="period">Digest period</label><select id="period" value={window} onChange={e=>setWindow(e.target.value)}><option value="since">{session?.review.visit?.first?'First visit · last 24h + outstanding':'Since last opened + outstanding'}</option><option value="1">Last 24 hours</option><option value="7">Last 7 days</option><option value="14">Last 14 days</option><option value="custom">Custom range</option></select></div>{autoWide&&window==='14'&&<p className="fn-autowide">Nothing arrived in the last 24 hours, so this first look covers the last 14 days.</p>}

 <button className="fn-stripbutton" onClick={()=>navigate('book')} aria-label="Inspect portfolio holdings; colours show completed-session price direction, not thesis health"><span className="fn-pulse">{session?.book.holdings.map(h=>{const change=brief?.coverage.find(c=>c.symbol===h.symbol)?.price.change_percent;return <span key={h.symbol} title={h.symbol} style={{flexGrow:weighted?Number(h.weight):1,background:change==null?'#53607b':change<=-3?'#e5574d':change<0?'#f0a39c':change>=3?'#2fb67c':change>0?'#7bd3ab':'#33415f'}}/>;})}</span><span className="fn-f fn-m">{session?.book.holdings.length||0} holdings. {weighted?'Width is your entered weight':'Equal widths: no weights entered'}; colour is the last completed session's move.</span></button><div className="fn-actions"><button className="fn-hit" onClick={()=>open({kind:'voice'})}><Pill tone="amber"><Glyph name="volume" size={15}/>Listen</Pill></button><button className="fn-hit" onClick={()=>open({kind:'week'})}><Pill tone="dark"><Glyph name="calendar" size={15}/>Week ahead</Pill></button><button className="fn-hit" onClick={()=>open({kind:'coverage'})}><Pill tone={stale?'amber':'dark'}>{`Checked ${sourced}/${session?.book.holdings.length||0} · ${ago(brief?.filing_checked_at||brief?.checked_at)}`}</Pill></button></div></>:<p className="fn-m fn-gap">{tab==='book'?'Your holdings, weights and reasons.':tab==='watch'?'Rules you can understand and inspect.':'Primary documents. Inspectable evidence.'}</p>}

 </header><main id="main" className="fn-bd">{offline&&<Notice>Offline · read-only saved snapshot from {date(brief?.checked_at,true)}. No source checks or changes can be saved. Clear this site’s browser data to remove local snapshots.</Notice>}{reconnected&&<Notice>Back online. This view is still the saved snapshot. <button className="fn-hit" onClick={load}>Reload stored data</button></Notice>}{!brief&&!loading&&<button className="fn-button" disabled={refreshing} onClick={refreshSources}>Refresh sources</button>}{error&&<Notice error>{error} <button className="fn-hit" onClick={load}>Retry stored data</button></Notice>}

 {session?.storage.mode==='local_development'&&<Notice>Development storage · Neon is not connected. Do not rely on this state surviving a hosted restart.</Notice>}

 {loading?<Skeleton/>:<>

 {tab==='today'&&<>{window==='custom'&&<div className="fn-c"><label>From<input type="date" value={start} onChange={e=>setStart(e.target.value)}/></label><label>To<input type="date" value={end} onChange={e=>setEnd(e.target.value)}/></label><p className="fn-m">Only the stored source interval is covered; this does not backfill missing dates.</p></div>}

 {pending&&<button className="fn-button" onClick={async()=>{setBrief(pending);setPending(null);const r=await api<Review>('/api/review',{action:'visit'});setSession(s=>s?{...s,review:r._version>=s.review._version?r:s.review}:s);}}>{updates?updates+' new changes':'Refreshed sources'} · update this view</button>}

 {brief?.is_demo_seed&&<Notice>Dated demonstration · {date(brief.checked_at,true)}. These are real saved observations, not live coverage.</Notice>}

 {session?.review.visit?.returning&&<Recap events={events} review={session.review} onDay={day=>{setStart(day);setEnd(day);setWindow('custom');setTier('all');}} onListen={()=>open({kind:'voice',recap:true})}/>}

 {lastDone&&<Notice><span role="status">{lastDone.symbol} marked done.</span> <button className="fn-hit" onClick={()=>change('undo',lastDone)}>Undo last review</button></Notice>}<div className="fn-tiers">{[['needs',`Needs you ${needsTier.length}`],['worth',`Worth knowing ${worthTier.length}`],['buried',`Buried ${buried.length}`]].map(([id,label])=><button className="fn-hit" key={id} onClick={()=>setTier(id)} aria-pressed={tier===id}><Pill tone={tier===id?'navy':'white'}>{label}</Pill></button>)}</div>

 {!shown.length&&!pinned.length&&<div className="fn-c"><h3>{checked===session?.book.holdings.length&&!brief?.counts.pending?'Nothing needs you in this view.':'No items in this view. Coverage is incomplete.'}</h3><p className="fn-m fn-gap">{checked===session?.book.holdings.length?'Inspect another period or your outstanding items.':'Missing or unread filings cannot establish a quiet day.'}</p>{tier==='needs'&&worthTier.length>0&&<button className="fn-hit" onClick={()=>setTier('worth')}>See {worthTier.length} worth knowing <Glyph name="arrow"/></button>}<button className="fn-hit" onClick={()=>{setTier('needs');setWindow('14');}}>Look back 14 days <Glyph name="arrow"/></button>{nextDate?<button className="fn-hit" onClick={()=>open({kind:'week'})}>Next: {nextDate.symbol} · {nextDate.kind} · {date(nextDate.date)}</button>:<p className="fn-m">No upcoming date found in assessed filings.</p>}</div>}

 {pinned.length>0&&<section aria-label="Pinned unfinished"><h3 className="fn-gap">Pinned unfinished · {pinned.length}</h3>{pinned.map(renderEvent)}</section>}

 {shown.map(renderEvent)}

 <button className="fn-c fn-open" onClick={()=>setTier(tier==='buried'?'needs':'buried')} aria-expanded={tier==='buried'}><span className="fn-buriedlines" aria-hidden="true">{[1,2,3,4,5].map(n=><i key={n}/>)}</span><span className="fn-row"><span className="fn-m">{buried.length} routine {buried.length===1?'event':'events'}, buried</span><Glyph name="arrow" size={16}/></span></button>

 <p className="fn-f fn-m">{brief?.counts.distinct_filings||0} retained distinct filings · {brief?.counts.pending||0} awaiting assessment. Updated {date(brief?.checked_at,true)}.</p></>}

 {visited.current.has('research')&&<div hidden={tab!=='research'}><ResearchPack inBook={session?.book.holdings.map(h=>h.symbol)} onAdd={async symbol=>{if(!session)return;const book=await api<Book>('/api/book',{holdings:[...session.book.holdings.map(({symbol,weight,thesis,sector,inputs})=>({symbol,weight,thesis,sector,inputs})),{symbol,weight:null,thesis:'',sector:'',inputs:[]}],version:session.book._version});setSession(s=>s?{...s,book}:s);setBrief(await api<Brief>('/api/today'));}} initial={context?.symbol} onEvidence={e=>open({kind:'evidence',evidence:e})} onAsk={(symbol,question)=>{navigate('ask');setContext({symbol,question,nonce:Date.now()});}}/></div>}

 {visited.current.has('ask')&&<div hidden={tab!=='ask'}><Research hidden={tab!=='ask'} context={context} onEvidence={e=>open({kind:'evidence',evidence:e})} onWatch={(symbol,rationale)=>{setWatchOrigin({symbol,rationale});navigate('watch');}}/></div>}

 {visited.current.has('book')&&<div hidden={tab!=='book'}>{session&&<BookView book={session.book} onSave={b=>{setSession({...session,book:b});api<Brief>('/api/today').then(setBrief).catch(e=>setError(e.message));}} onHolding={h=>open({kind:'holding',holding:h})}/>}</div>}

 {visited.current.has('watch')&&<div hidden={tab!=='watch'}><WatchView fromAnswer={watchOrigin}/></div>}

 </>}

 </main><nav className="fn-nav" aria-label="Main navigation">{tabs.map(t=><button key={t} aria-current={tab===t?'page':undefined} onClick={()=>navigate(t)}>{t==='ask'?<span className="fn-askround"><Glyph name="ask" size={22}/></span>:<Glyph name={t}/>}<span>{t[0].toUpperCase()+t.slice(1)}</span></button>)}</nav>

 {panel&&<Sheet header={panel.kind==='event'?<div className="fn-flex"><span className={'fn-ic '+(panel.event.tier===0?'red':panel.event.kind==='price'?'amber':'')}><Glyph name={panel.event.kind==='price'?'chart':'file'}/></span><div className="fn-grow"><strong className="fn-sheet-name">{panel.event.name&&panel.event.name!==panel.event.symbol?panel.event.name:panel.event.symbol}</strong>{panel.event.name&&panel.event.name!==panel.event.symbol&&<span className="fn-f fn-m"> {panel.event.symbol}</span>}<p className="fn-m">{eventType(panel.event)}{(panel.event.children?.length||0)>1?`, ${panel.event.children!.length} filings in one`:` · ${date(panel.event.published_at,true)}`}</p></div></div>:undefined} title={panel.kind==='event'?'The change':panel.kind==='evidence'?'The evidence':panel.kind==='holding'?panel.holding.symbol:panel.kind==='voice'?'Your spoken brief':panel.kind==='week'?'Week ahead':panel.kind==='stats'?'Behind FINN':'Source coverage'} onClose={close} trigger={trigger.current}>

 {panel.kind==='event'&&<><div><h2 className="fn-sheet-title">{displayTitle(panel.event.title)}</h2>{panel.event.kind!=='price'&&<p className="fn-m fn-sheet-sub">{panel.event.reason}</p>}</div><EventTimeline event={panel.event} onRead={read}/>

 {panel.event.kind==='price'?<div className="fn-c"><PriceView event={panel.event}/></div>:<div className="fn-c">{panel.event.assessment_error&&<Notice error>Couldn’t read this filing. {panel.event.assessment_error}</Notice>}<button className="fn-button secondary" onClick={()=>read(panel.event)} disabled={reading||!panel.event.url}>{reading?'Reading the attachment…':'Inspect supporting evidence'}<Glyph name="file"/></button><a className="fn-hit" href={panel.event.url||panel.event.exchange_notice?.url} target="_blank" rel="noreferrer">{panel.event.url?'Open original filing':'Open exchange notices'} <Glyph name="arrow" size={16}/></a>{panel.event.exchange_notice&&<div className="fn-gap"><h3>Exchange notice</h3><p>{panel.event.exchange_notice.text}</p><p className="fn-f fn-m">{panel.event.exchange_notice.source} · checked {date(panel.event.exchange_notice.checked_at,true)}. This is exchange notice text, with no PDF page citation.</p></div>}</div>}

 {panel.event.results&&<Results result={panel.event.results} onEvidence={e=>{evidenceTrigger.current=document.activeElement as HTMLElement;setNested(e);}}/>}

 {panel.event.management_profile&&<div className="fn-c"><h3>Management background</h3><p className="fn-f fn-m">{panel.event.management_profile.label}</p><p className="fn-gap">{panel.event.management_profile.text}</p><button className="fn-hit" onClick={()=>{evidenceTrigger.current=document.activeElement as HTMLElement;setNested(panel.event.management_profile!.evidence);}}>Inspect profile source <Glyph name="file" size={14}/></button></div>}

 <div className="fn-grid2 fn-verdicts"><GuidanceCard symbol={panel.event.symbol} onEvidence={e=>{evidenceTrigger.current=document.activeElement as HTMLElement;setNested(e);}}/><div className="fn-c"><h3 className="fn-label">Your thesis</h3><Pill tone={panel.event.thesis?thesisLabel(panel.event.thesis_status)[1]:''}>{panel.event.thesis?thesisLabel(panel.event.thesis_status)[0]:'Add a thesis'}</Pill><p>{panel.event.thesis||'Capture your reason for owning this stock in Book.'}</p></div></div>

 <ThesisEvidence record={panel.event.thesis_assessment} onEvidence={e=>{evidenceTrigger.current=document.activeElement as HTMLElement;setNested(e);}}/><div className="fn-c"><h3 className="fn-label">Why it ranks here</h3>{panel.event.ranking_reasons?.map((r,i)=><div className="fn-gap" key={i}><div className="fn-row"><span>{r.label}</span><strong>{r.value>0?'+':''}{r.value}</strong></div><p className="fn-f fn-m">{r.explanation}</p>{r.evidence?.[0]&&<button className="fn-hit" onClick={()=>{evidenceTrigger.current=document.activeElement as HTMLElement;setNested(r.evidence![0]);}}>Inspect this reason <Glyph name="file" size={14}/></button>}</div>)}<p className="fn-f fn-m fn-gap">{panel.event.ranking_note}</p><div className="fn-row fn-gap"><span className="fn-m">Worth your time?</span><span className="fn-tags"><button className="fn-hit" aria-pressed={session?.review.feedback[panel.event.id]==='mattered'} onClick={()=>change('feedback',panel.event,session?.review.feedback[panel.event.id]==='mattered'?null:'mattered')}><Pill tone={session?.review.feedback[panel.event.id]==='mattered'?'navy':''}>Mattered</Pill></button><button className="fn-hit" aria-pressed={session?.review.feedback[panel.event.id]==='noise'} onClick={()=>change('feedback',panel.event,session?.review.feedback[panel.event.id]==='noise'?null:'noise')}><Pill tone={session?.review.feedback[panel.event.id]==='noise'?'navy':''}>Noise</Pill></button></span></div></div><button className="fn-askbar" onClick={()=>navigate('ask',panel.event.symbol,panel.event)}>Ask about this event <Glyph name="ask"/></button></>}

 {panel.kind==='evidence'&&<EvidenceView evidence={panel.evidence}/>}

 {panel.kind==='coverage'&&<><button className="fn-button" disabled={refreshing} onClick={refreshSources}>{refreshing?'Refreshing…':'Refresh sources for this book'}</button>{refreshStage&&<p role="status">{refreshStage}</p>}<p>Fetching a disclosure does not mean its attachment was successfully read.</p>{brief?.coverage.map(c=><div className="fn-c" key={c.symbol}><h3>{c.symbol}</h3><p>Filings · {c.filings.status} · {date(c.filings.checked_at)}</p><p>Prices · {c.price.status} · session {date(c.price.session)}</p>{(c.filings.error||c.price.error)&&<Notice>{c.filings.error||c.price.error}</Notice>}</div>)}</>}

 {panel.kind==='holding'&&<HoldingDetail holding={panel.holding} onResearch={()=>navigate('research',panel.holding.symbol)} onEvidence={e=>{evidenceTrigger.current=document.activeElement as HTMLElement;setNested(e);}}/>}

 {panel.kind==='voice'&&<><p className="fn-m">{panel.recap?'Reads the same retained day-by-day return recap.':'Reads the same dated digest visible in Today.'} Playback may stop when this browser is backgrounded.</p><label>Playback speed<select value={rate} onChange={e=>setRate(Number(e.target.value))}><option value="0.8">0.8×</option><option value="1">1×</option><option value="1.2">1.2×</option></select></label><div className="fn-row"><button className="fn-button" onClick={speak}>{speaking?'Restart':'Play'}</button><button className="fn-hit" disabled={!('speechSynthesis' in globalThis)} onClick={()=>speechSynthesis.paused?speechSynthesis.resume():speechSynthesis.pause()}>Pause / resume</button><button className="fn-hit" disabled={!('speechSynthesis' in globalThis)} onClick={()=>{speechSynthesis.cancel();setSpeaking(false);}}>Stop</button></div><div className="fn-c"><h3>Transcript</h3><p className="fn-gap">{voiceText}</p></div></>}

 {panel.kind==='week'&&<>{reminderStatuses.length>0&&<details className="fn-c"><summary>Saved reminder status</summary>{reminderStatuses.map(r=><div className="fn-in fn-gap" key={r.id}><strong>{r.event.symbol} · {r.event.kind}</strong><p>{date(r.event.date,true)} · {r.status.replaceAll('_',' ')}</p>{r.latest_notice?.replacement_date&&<p>New disclosed date: {date(r.latest_notice.replacement_date,true)}. Save the new date below after reviewing its source.</p>}</div>)}<p className="fn-f fn-m fn-gap">In-app only. No push or Telegram message was sent; elapsed dates do not confirm that an event occurred.</p></details>}{reminderNotice&&<Notice>{reminderNotice}</Notice>}{brief?.upcoming?.length?brief.upcoming.map((d,i)=><div className="fn-c" key={i}><div className="fn-row"><h3>{d.symbol} · {d.kind}</h3><Pill>{d.status}</Pill></div><p className="fn-gap">{date(d.date,true)} · {d.time}</p>{d.status!=='cancelled'&&<button className="fn-hit" onClick={async()=>{try{await api('/api/reminders',{event_id:d.event_id,date:d.date,kind:d.kind,enabled:!reminders.some(r=>r.enabled&&r.event.event_id===d.event_id&&r.event.date===d.date&&r.event.kind===d.kind)});setReminders((await api<{items:typeof reminders}>('/api/reminders')).items);setReminderNotice('Reminder preference saved. Push and Telegram delivery are disabled.');}catch(e){setError((e as Error).message);}}}>{reminders.some(r=>r.enabled&&r.event.event_id===d.event_id&&r.event.date===d.date&&r.event.kind===d.kind)?'Reminder saved · remove':'Save reminder'} <Glyph name="calendar" size={14}/></button>}<button className="fn-hit" onClick={()=>{evidenceTrigger.current=document.activeElement as HTMLElement;setNested({...d.evidence,quote:d.quote});}}>Inspect disclosed date <Glyph name="file" size={14}/></button></div>):<Notice>No future dates were found in the assessed filings. Unread attachments remain a coverage gap.</Notice>}</>}

 {panel.kind==='stats'&&<><div className="fn-c"><h3>Evidence first</h3><p>{brief?.counts.distinct_filings||0} distinct stored filings, {brief?.counts.pending||0} pending assessment.</p></div><Stats/><p className="fn-m">{session?.storage.recovery}</p></>}

 {error&&<Notice error>{error}</Notice>}

 </Sheet>}

 {nested&&<Sheet title="The evidence" onClose={()=>setNested(null)} trigger={evidenceTrigger.current}><EvidenceView evidence={nested}/></Sheet>}

 </div>;

}

