import React,{useEffect,useRef,useState} from 'react';
import {createRoot} from 'react-dom/client';
import * as Dialog from '@radix-ui/react-dialog';
import type {Answer,Brief,Claim,Evidence,Event,Job} from './types';
import {api,followJob} from './api';
import {acknowledge,changedCount,inWindow,isReviewed,observe,readStored,saveStored,undo,type ReviewState} from './state';
import './style.css';

const when=(value:string|null|undefined,full=false)=>value?new Intl.DateTimeFormat('en-IN',{timeZone:'Asia/Kolkata',day:'numeric',month:'short',...(full?{year:'numeric' as const}: {})}).format(new Date(value)):'Date unavailable';
const clock=(value:string|null|undefined)=>value?new Intl.DateTimeFormat('en-IN',{timeZone:'Asia/Kolkata',hour:'numeric',minute:'2-digit'}).format(new Date(value)):'not checked';
const kindName=(kind:string)=>kind==='annual'?'Annual report':kind==='transcript'?'Earnings call':'Exchange filing';
const normal=(s:string)=>s.replace(/\s+/g,' ').trim();
const original=(e:Evidence)=>e.url?.startsWith('https://')?e.url.split('#')[0]+'#page='+e.page:undefined;
function Icon({name,size=20}:{name:string;size?:number}){const paths:Record<string,React.ReactNode>={
 brief:<><path d="M5 4h14v16H5zM8 8h8M8 12h8M8 16h4"/></>,search:<><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/></>,
 arrow:<path d="M5 12h14m-6-6 6 6-6 6"/>,refresh:<><path d="M20 7v5h-5M4 17v-5h5"/><path d="M6 7a7 7 0 0 1 12-1l2 3M4 15l2 3a7 7 0 0 0 12-1"/></>,
 check:<path d="m5 12 4 4L19 6"/>,close:<path d="m6 6 12 12M6 18 18 6"/>,external:<><path d="M14 4h6v6m-1-5-9 9M10 4H4v16h16v-6"/></>,
 file:<><path d="M6 3h8l4 4v14H6zM14 3v5h4M9 12h6M9 16h6"/></>,chevron:<path d="m9 5 7 7-7 7"/>,info:<><circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7v1"/></>};
 return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name]||paths.file}</svg>;
}
function ErrorNote({children}:{children:React.ReactNode}){return <div className="error-note" role="alert"><Icon name="info"/><span>{children}</span></div>;}
type SheetState={kind:'evidence';evidence:Evidence}|{kind:'coverage'}|{kind:'price';event:Event}|null;

function EvidenceView({evidence}:{evidence:Evidence}){
 const [unavailable,setUnavailable]=useState(false);
 useEffect(()=>{let live=true;fetch('/api/evidence/'+evidence.id).then(async r=>{
   if(!live)return;if(!r.ok){setUnavailable(true);return;}const e=await r.json();
   if(e.hash!==evidence.hash||e.page!==evidence.page||!normal(e.text).includes(normal(evidence.quote||'')))setUnavailable(true);
 }).catch(()=>live&&setUnavailable(true));return()=>{live=false;};},[evidence.id]);
 return <><div className="source-line"><span className="tag">{evidence.kind==='annual'?'Annual report':evidence.kind==='transcript'?'Earnings call':'Exchange filing'}</span><span>PDF page {evidence.page}</span></div>
 <h3 className="source-company">{evidence.name||evidence.symbol}</h3><p className="muted">{evidence.period}</p>
 {unavailable&&<div className="notice">Version unavailable on the server. This is the saved excerpt from {when(evidence.fetched_at,true)}; the original link may now contain a newer version.</div>}
 <p className="eyebrow space-top">EXACT SOURCE EXCERPT</p><blockquote>{evidence.quote||evidence.text}</blockquote>
 {evidence.quote&&<details className="context"><summary>Show surrounding context</summary><p>{evidence.text}</p></details>}
 <div className="source-foot"><span>Retrieved {when(evidence.fetched_at,true)} · {clock(evidence.fetched_at)} IST</span><span>Source version {evidence.hash.slice(0,12)}</span></div>
 <a className="button primary wide" href={original(evidence)} target="_blank" rel="noreferrer">Open original · PDF page {evidence.page}<Icon name="external"/></a>
 <p className="fine-print">Some PDF viewers open at the beginning. Use the PDF page number shown above.</p></>;
}

function App(){
 const [tab,setTab]=useState<'brief'|'research'>('brief');const [brief,setBrief]=useState<Brief|null>(null);const briefRef=useRef<Brief|null>(null);
 const [window,setWindow]=useState('since');const [visible,setVisible]=useState<Event[]>([]);const [loading,setLoading]=useState(true);const [refreshing,setRefreshing]=useState(false);
 const [error,setError]=useState('');const [pending,setPending]=useState<Brief|null>(null);const [sheet,setSheetState]=useState<SheetState>(null);const sheetTrigger=useRef<HTMLElement|null>(null);const openingRequest=useRef(0);
 function setSheet(value:SheetState){openingRequest.current++;setOpening(null);if(value)sheetTrigger.current=document.activeElement as HTMLElement;setSheetState(value);}
 const [review,setReview]=useState<ReviewState|null>(()=>readStored<ReviewState>('finn.review.v1'));const reviewRef=useRef(review);const windowRef=useRef(window);
 const [storageError,setStorageError]=useState(false);const [researchContext,setResearchContext]=useState<{symbol:string;event?:Event;nonce:number}|null>(null);
 const [opening,setOpening]=useState<string|null>(null);const [openError,setOpenError]=useState('');
 function persist(next:ReviewState){setReview(next);reviewRef.current=next;if(!saveStored('finn.review.v1',next))setStorageError(true);}
 function apply(data:Brief){const state=observe(data.events,reviewRef.current);persist(state);setBrief(data);briefRef.current=data;
   setVisible(data.events.filter(e=>inWindow(e,windowRef.current,state)));setPending(null);setError('');}
 async function refresh(){setRefreshing(true);try{apply(await api<Brief>('/api/brief'));}catch(e){setError((e as Error).message);}finally{setRefreshing(false);setLoading(false);}}
 function background(data:Brief){if(!briefRef.current){apply(data);return;}setPending(data);setError('');
   const updated={...briefRef.current,coverage:data.coverage,source_status:data.source_status,is_demo_seed:data.is_demo_seed,filing_checked_at:data.filing_checked_at,checked_at:data.checked_at};
   briefRef.current=updated;setBrief(updated);}
 useEffect(()=>{api<Brief>('/api/brief').then(apply).catch(e=>setError(e.message)).finally(()=>setLoading(false));
   const timer=setInterval(()=>{if(document.visibilityState==='visible')api<Brief>('/api/brief').then(background).catch(()=>setError('Could not refresh source coverage. The previous check is still shown; retry to establish current coverage.'));},60000);
   return()=>clearInterval(timer);},[]);
 function changeWindow(value:string){setWindow(value);windowRef.current=value;if(brief)setVisible(brief.events.filter(e=>inWindow(e,value,reviewRef.current)));}
 function navigate(to:'brief'|'research'){openingRequest.current++;setOpening(null);setTab(to);if(to==='brief'&&brief)setVisible(brief.events.filter(e=>inWindow(e,windowRef.current,reviewRef.current)));document.querySelector('main')?.scrollIntoView({block:'start'});}
 function investigate(event:Event){openingRequest.current++;setOpening(null);setResearchContext({symbol:event.symbol,event,nonce:Date.now()});setTab('research');globalThis.scrollTo({top:0,behavior:'auto'});}
 function toggleReview(event:Event){if(reviewRef.current)persist(isReviewed(reviewRef.current,event)?undo(reviewRef.current,event.id):acknowledge(reviewRef.current,event));}
 async function openEvent(event:Event){
   const request=++openingRequest.current;
   setOpenError('');if(event.kind==='price'){setSheet({kind:'price',event});return;}
   let evidence=event.evidence;
   if(!evidence.length){setOpening(event.id);try{const first=await api<Job>('/api/filings/'+encodeURIComponent(event.id)+'/assess',{});
     const result=await followJob(first,()=>{},()=>openingRequest.current===request);if(result?.status==='error')throw new Error(result.error?.message);evidence=result?.result?.evidence||[];
   }catch(e){if(openingRequest.current===request)setOpenError((e as Error).message);}finally{if(openingRequest.current===request)setOpening(null);}}
   if(openingRequest.current!==request)return;
   if(evidence.length){const e=evidence[0];const sentences=e.text.split(/(?<=[.!?])\s+/);const quote=sentences.find(s=>/appoint|resign|approved|financial results|revenue|investment/i.test(s)&&s.length>50)||sentences.find(s=>s.length>60)||e.text;
     setSheet({kind:'evidence',evidence:{...e,quote}});}
 }
 const newCount=pending&&brief?changedCount(brief.events,pending.events):0;
 const coverage=brief?.coverage||[];const priceCount=coverage.filter(c=>c.price.status==='live').length;const filingCount=coverage.filter(c=>c.filings.status==='live').length;
 const unreviewed=visible.filter(e=>!isReviewed(review,e)&&e.assessment!=='routine').length;
 const groups=[0,1,2].map(tier=>({tier,events:visible.filter(e=>e.tier===tier)}));
 const routine=visible.filter(e=>e.tier===3);
 const sheetTitle=sheet?.kind==='evidence'?'The evidence':sheet?.kind==='price'?'Behind the signal':'Source coverage';
 return <><a className="skip" href="#main">Skip to content</a><header className="brand-bar"><div className="brand"><span className="brand-mark">f</span><span>FINN</span></div><span className="brand-note">A little less noise.</span></header>
 <main id="main" className="reading-column">
 <div hidden={tab!=='brief'}>
  <div className="page-heading"><div><p className="eyebrow">{new Intl.DateTimeFormat('en-IN',{timeZone:'Asia/Kolkata',weekday:'long',day:'numeric',month:'long'}).format(new Date())}</p><h1>Your brief<span className="teal-dot">.</span></h1></div>
   <button className="icon-button refresh" onClick={refresh} disabled={refreshing} aria-label={newCount?`Refresh, ${newCount} updates available`:'Refresh brief'}><Icon name="refresh"/>{newCount>0&&<span className="update-count">{newCount}</span>}</button></div>
  <p className="intro">What changed. Why it deserves a look.</p>
  <button className="coverage-link" onClick={()=>setSheet({kind:'coverage'})}><span className={'status-dot '+(filingCount===15&&priceCount===15?'good':'warning')}/>{loading?'Checking 15 companies':`${filingCount}/15 filings · ${priceCount}/15 prices`}<Icon name="chevron" size={16}/></button>
  {brief&&<p className="checked">Filings checked {clock(brief.filing_checked_at)} IST · Prices are end of day</p>}
  {brief?.is_demo_seed&&<div className="notice">Dated demonstration · {when(brief.checked_at,true)}. These are saved observations, not live coverage.</div>}
  {storageError&&<ErrorNote>Review state could not be saved in this browser. Keep this tab open to retain it.</ErrorNote>}
  {error&&<ErrorNote>{error} {brief?'Your previous check is still shown.':''} <button className="text-button" onClick={refresh}>Retry</button></ErrorNote>}
  <div className="window-row"><label className="sr-only" htmlFor="window">Review window</label><select id="window" value={window} onChange={e=>changeWindow(e.target.value)}><option value="since">Since review</option><option value="today">Today</option><option value="7">Last 7 days</option><option value="14">Last 14 days</option></select><span>{!loading&&`${unreviewed} to review`}</span></div>
  {loading?<div className="loading-state" role="status"><span className="pulse"/><h2>Checking your companies</h2><p>Fetching exchange filings and completed trading sessions.</p></div>:<>
   {!visible.length&&<div className="empty-state"><span className="empty-icon"><Icon name="check" size={28}/></span><h2>{(!brief||brief.source_status==='unavailable')?'Could not check your portfolio':'A quieter review window'}</h2><p>{(!brief||brief.source_status==='unavailable')?'Source checks did not complete. Retry to establish coverage.':`No unreviewed items in this window. ${brief?.counts.pending?`${brief.counts.pending} filings in the wider period still await assessment.`:'This is bounded by the sources and period checked.'}`}</p><button className="button secondary" onClick={()=>changeWindow('14')}>Look back 14 days<Icon name="arrow"/></button></div>}
   {groups.map(group=>group.events.length>0&&<section className="event-section" key={group.tier}><div className="section-title"><h2>{group.tier===0?'Review first':group.tier===1?'Also to review':'At the last close'}</h2><span>{group.events.length}</span></div>
     {Array.from(new Set(group.events.map(e=>e.symbol))).map(symbol=><div className="company-group" key={symbol}><div className="company-heading"><span>{symbol}</span><span>{group.events.find(e=>e.symbol===symbol)?.name}</span></div>
       {group.events.filter(e=>e.symbol===symbol).map(event=><EventRow key={event.id+event.revision} event={event} reviewed={isReviewed(review,event)} onReview={()=>toggleReview(event)} onEvidence={()=>openEvent(event)} onResearch={()=>investigate(event)} opening={opening===event.id}/>)}</div>)}
   </section>)}
   {routine.length>0&&<details className="routine"><summary>Routine filings <span>{routine.length}</span><span className="summary-note">Available, without interrupting your review</span></summary>{routine.map(event=><EventRow key={event.id+event.revision} event={event} reviewed={isReviewed(review,event)} onReview={()=>toggleReview(event)} onEvidence={()=>openEvent(event)} onResearch={()=>investigate(event)} opening={opening===event.id}/>)}</details>}
   {openError&&<ErrorNote>{openError} The original filing remains available in the event.</ErrorNote>}
   {brief&&<div className="brief-footer"><span>{brief.counts.fetched_filings} filings fetched in the wider period</span><span>{brief.counts.distinct_filings} distinct · {brief.counts.exact_duplicates} exact duplicates · {brief.counts.pending} pending assessment</span><p>Review marks belong to this browser. Opening an item never marks it reviewed.</p></div>}
  </>}
 </div>
 <Research hidden={tab!=='research'} context={researchContext} onEvidence={e=>setSheet({kind:'evidence',evidence:e})}/>
 </main>
 <nav className="bottom-nav" aria-label="Main navigation"><div><button className={tab==='brief'?'active':''} onClick={()=>navigate('brief')} aria-current={tab==='brief'?'page':undefined}><Icon name="brief"/><span>Brief</span></button><button className={tab==='research'?'active':''} onClick={()=>navigate('research')} aria-current={tab==='research'?'page':undefined}><Icon name="search"/><span>Research</span></button></div></nav>
 <Dialog.Root open={!!sheet} onOpenChange={open=>{if(!open)setSheet(null);}}><Dialog.Portal><Dialog.Overlay className="sheet-overlay"/><Dialog.Content className="sheet" aria-describedby={undefined} onCloseAutoFocus={e=>{e.preventDefault();sheetTrigger.current?.focus();}}><div className="sheet-handle"/><header className="sheet-header"><Dialog.Title>{sheetTitle}</Dialog.Title><Dialog.Close className="icon-button" aria-label="Close evidence"><Icon name="close"/></Dialog.Close></header><div className="sheet-body">
  {sheet?.kind==='evidence'&&<EvidenceView key={sheet.evidence.id+(sheet.evidence.quote||'')} evidence={sheet.evidence}/>}
  {sheet?.kind==='coverage'&&<><p className="muted">Price and filing checks are separate. A successful check does not imply that every attachment has been assessed.</p>{coverage.length?coverage.map(c=><div className="coverage-row" key={c.symbol}><h3>{c.symbol}</h3><div><span className={'coverage-status '+(c.filings.status==='live'?'':'amber')}>Filings · {c.filings.status}</span><small>Checked {clock(c.filings.checked_at)} IST</small></div><div><span className={'coverage-status '+(c.price.status==='live'&&!c.price.older_session?'':'amber')}>Prices · {c.price.status}{c.price.older_session?' · older session':''}</span><small>Session {when(c.price.session)} · {c.price.close!=null?`${c.price.currency||'INR'} ${c.price.close.toLocaleString('en-IN')}`:'price unavailable'}</small></div>{(c.price.error||c.filings.error)&&<p className="fine-print amber">{c.price.error||c.filings.error}</p>}</div>):<p>Source checks are not complete yet.</p>}</>}
  {sheet?.kind==='price'&&<PriceView event={sheet.event}/>}
 </div></Dialog.Content></Dialog.Portal></Dialog.Root></>;
}

function EventRow({event,reviewed,onReview,onEvidence,onResearch,opening}:{event:Event;reviewed:boolean;onReview:()=>void;onEvidence:()=>void;onResearch:()=>void;opening:boolean}){
 const [expanded,setExpanded]=useState(false);
 return <article className={'event-row '+(reviewed?'reviewed':'')}><div className="event-topline"><span className={'event-label '+(event.assessment==='pending'?'amber':'')}>{reviewed?'Reviewed':event.assessment==='pending'?'Assessment pending':event.kind==='price'?'EOD signal':event.assessment==='routine'?'Routine':'Source assessed'}</span><time dateTime={event.published_at||undefined}>{when(event.published_at)}{event.kind==='filing'&&event.published_at?' · '+clock(event.published_at):''}</time></div>
 <button className="event-title" onClick={()=>setExpanded(!expanded)} aria-expanded={expanded}><span>{event.title}</span><span className={expanded?'turn':''}><Icon name="chevron" size={18}/></span></button>
 <p className="event-reason">{event.reason}</p>
 {expanded&&<div className="event-detail"><p>{event.description}</p>{event.assessment_error&&<p className="amber">{event.assessment_error}</p>}<button className="text-button" onClick={onResearch}>Research {event.symbol}<Icon name="arrow" size={17}/></button><a href={event.url} target="_blank" rel="noreferrer" className="source-original">Original disclosure<Icon name="external" size={14}/></a></div>}
 <div className="event-actions"><button onClick={onEvidence} className="text-button" disabled={opening}><Icon name="file" size={17}/>{opening?'Reading attachment…':'Evidence'}</button><button onClick={onReview} className={'review-button '+(reviewed?'done':'')}>{reviewed?<><Icon name="check" size={16}/>Reviewed <span>Undo</span></>:'Mark reviewed'}</button></div></article>;
}

function PriceView({event}:{event:Event}){const s=event.signal!;return <><p className="eyebrow">{event.symbol} · COMPLETED SESSION</p><h3 className="source-company">{when(s.session,true)}</h3><div className="price-facts"><div><span>Close</span><strong>{s.currency} {s.close?.toLocaleString('en-IN')}</strong></div><div><span>Daily change</span><strong>{s.change_percent==null?'Unavailable':`${s.change_percent>0?'+':''}${s.change_percent}%`}</strong></div><div><span>Volume / prior 20 sessions</span><strong>{s.volume_multiple==null?'Unavailable':s.volume_multiple+'×'}</strong></div></div>
 <p className="muted">{s.price_basis}. This signal does not establish why the price or volume changed.</p><details className="context"><summary>Show calculation and inputs</summary><p>{s.formula}</p><dl>{Object.entries(s.operands||{}).filter(([k])=>k!=='previous_20_volumes').map(([k,v])=><div key={k}><dt>{k.replaceAll('_',' ')}</dt><dd>{String(v??'Unavailable')}</dd></div>)}</dl></details>{s.comparison_limit&&<div className="notice">{s.comparison_limit}</div>}<a className="button primary wide" href={s.url} target="_blank" rel="noreferrer">Open daily market data<Icon name="external"/></a></>;}

const EXAMPLES=[{symbol:'TCS',label:'AI demand',question:'What does TCS do, and what does management say about AI demand and deal momentum?'},{symbol:'KPITTECH',label:'Growth visibility',question:'What does KPIT do, and what does management say about demand and growth visibility?'},{symbol:'ASTRAL',label:'Demand & margins',question:'What does Astral do, and what does management say about demand and operating margins?'}];
function Research({hidden,context,onEvidence}:{hidden:boolean;context:{symbol:string;event?:Event;nonce:number}|null;onEvidence:(e:Evidence)=>void}){
 const saved=useRef(readStored<Answer>('finn.answer.v2'));
 const [symbol,setSymbol]=useState(saved.current?.company.symbol||'');const [question,setQuestion]=useState(saved.current?.question||'What does the company do, and what is management’s stated outlook?');
 const [answer,setAnswer]=useState<Answer|null>(saved.current);const [restored,setRestored]=useState(!!saved.current);const [job,setJob]=useState<Job|null>(null);const [error,setError]=useState('');const [partial,setPartial]=useState<Evidence[]>([]);const [busy,setBusy]=useState(false);const generation=useRef(0);
 function changed(){generation.current++;setAnswer(null);setJob(null);setBusy(false);setError('');setPartial([]);setRestored(false);}
 useEffect(()=>{if(context){changed();setSymbol(context.symbol);setQuestion(context.event?.kind==='filing'?'What does this exchange filing disclose, and what relevant context do the company documents provide?':'What does management’s latest earnings call say about the outlook for this company?');}},[context?.nonce]);
 async function ask(nextSymbol=symbol,nextQuestion=question){const request=++generation.current;setBusy(true);setError('');setAnswer(null);setPartial([]);setRestored(false);
  try{const first=await api<Job>('/api/research',{symbol:nextSymbol,question:nextQuestion,filing_id:nextSymbol===context?.symbol&&context.event?.kind==='filing'?context.event.id:undefined});const result=await followJob(first,setJob,()=>generation.current===request);if(!result)return;
   if(result.status==='error'){setPartial(result.evidence||[]);throw new Error(result.error?.message||'This investigation could not complete.');}
   const a=result.result!;setAnswer(a);setJob(null);saveStored('finn.answer.v2',a);
  }catch(e){if(generation.current===request)setError((e as Error).message);}finally{if(generation.current===request)setBusy(false);}}
 function example(item:typeof EXAMPLES[number]){changed();setSymbol(item.symbol);setQuestion(item.question);ask(item.symbol,item.question);}
 return <div hidden={hidden} className="research-page"><div className="page-heading"><div><p className="eyebrow">FOLLOW THE EVIDENCE</p><h1>Look closer<span className="teal-dot">.</span></h1></div><span className="research-symbol"><Icon name="search" size={27}/></span></div><p className="intro">One company. One question. The source behind it.</p>
 <form className="research-form" onSubmit={e=>{e.preventDefault();ask();}}><label htmlFor="symbol">NSE company symbol</label><input id="symbol" value={symbol} placeholder="e.g. HAVELLS" autoComplete="off" autoCapitalize="characters" spellCheck={false} maxLength={30} onChange={e=>{changed();setSymbol(e.target.value.toUpperCase());}}/>
 <label htmlFor="question">What do you want to understand?</label><textarea id="question" value={question} rows={3} maxLength={600} onChange={e=>{changed();setQuestion(e.target.value);}}/>
 <button className="button primary wide" type="submit" disabled={busy||!symbol.trim()||question.trim().length<10}>{busy?'Investigating…':'Investigate company'}<Icon name="arrow"/></button></form>
 {context?.event&&symbol===context.symbol&&<div className="context-filing"><p className="eyebrow">FROM YOUR BRIEF</p><strong>{context.event.title}</strong><p>This filing is included alongside the annual report and earnings call. Each source keeps its own date and period.</p><a href={context.event.url} target="_blank" rel="noreferrer">Keep the original filing in view <Icon name="external" size={14}/></a></div>}
 {!busy&&!answer&&<div className="examples"><p className="eyebrow">A PLACE TO START</p>{EXAMPLES.map(item=><button key={item.symbol} onClick={()=>example(item)}><span><strong>{item.symbol}</strong><small>{item.label}</small></span><Icon name="arrow" size={18}/></button>)}</div>}
 {busy&&<div className="investigation-progress" role="status" aria-live="polite"><div className="progress-symbol"><span className="pulse"/></div><div><h2>{job?.stage||'Starting your investigation'}</h2><p>{job?.pages?`${job.pages} PDF pages read. `:''}A new company can take a little longer. You can return to your brief.</p></div></div>}
 {error&&<ErrorNote>{error}</ErrorNote>}
 {partial.length>0&&<section className="partial-sources"><h2>The sources are still here</h2><p>Analysis could not complete. Inspect the retrieved passages directly.</p>{partial.slice(0,4).map(e=><button className="source-chip" key={e.id} onClick={()=>onEvidence(e)}>{kindName(e.kind)} · PDF p.{e.page}<Icon name="chevron" size={14}/></button>)}</section>}
 {answer&&<section className="answer-section" aria-label="Research answer"><div className="answer-identity"><span className="ticker">{answer.company.symbol}</span><h2>{answer.company.name}</h2><p>{answer.is_demo_seed?'Dated demonstration answer':restored?'Saved on this device':answer.cache_hit?'Previously verified answer':'Source-based answer'} · {when(answer.answered_at)} · {clock(answer.answered_at)} IST</p></div>
  <div className="document-coverage">{answer.documents.map((d,i)=><span key={d.hash+String(i)}><Icon name="file" size={14}/>{kindName(d.kind)} · {d.period}</span>)}</div>
  {answer.gaps.map((g,i)=><div className="notice" key={i}>{g.message}</div>)}
  {answer.status==='insufficient_evidence'?<div className="empty-answer"><h3>I couldn’t establish that from these sources.</h3><p>Try a narrower question or inspect the available documents.</p></div>:<ol className="claims">{answer.claims.map((claim,i)=><li key={i}><span className="claim-index">0{i+1}</span><div>{claim.nature==='interpretation'&&<span className="event-label">FINN interpretation</span>}<p>{claim.text}</p><Citations claim={claim} answer={answer} onEvidence={onEvidence}/></div></li>)}</ol>}
  {answer.calculation&&<details className="context"><summary>Calculation and source operand</summary><p>{answer.calculation.formula}</p><dl>{Object.entries(answer.calculation.operand).filter(([k])=>k!=="evidence_id"&&k!=="quote").map(([k,v])=><div key={k}><dt>{k.replaceAll("_"," ")}</dt><dd>{v}</dd></div>)}</dl></details>}
  {answer.limitation&&<div className="answer-limit"><span className="eyebrow">WHAT THIS DOESN’T ESTABLISH</span><p>{answer.limitation}</p></div>}
  <p className="fine-print">Answers use selected primary-source passages. Open the evidence to inspect context, period and original documents.</p>
 </section>}
 </div>;
}
function Citations({claim,answer,onEvidence}:{claim:Claim;answer:Answer;onEvidence:(e:Evidence)=>void}){const seen=new Set<string>();return <div className="citations">{claim.citations.map((c,i)=>{const e=answer.evidence.find(x=>x.id===c.evidence_id);if(!e)return null;const key=e.hash+e.page+c.quote;if(seen.has(key))return null;seen.add(key);return <button className="source-chip" key={i} onClick={()=>onEvidence({...e,quote:c.quote})}><Icon name="file" size={13}/>{kindName(e.kind)} · p.{e.page}<Icon name="chevron" size={13}/></button>;})}</div>;}

createRoot(document.getElementById('root')!).render(<App/>);
