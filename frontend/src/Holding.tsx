import React,{useEffect,useRef,useState} from 'react';

import {api,followJob} from './api';
import {HoldingResearch} from './HoldingResearch';

import {ThesisEvidence,ThesisHistory,type ThesisDetail} from './Thesis';

import {date,type Holding} from './product';

import type {Evidence,Signal,Job} from './types';

import {Glyph,Notice,Skeleton} from './ui';



export function HoldingDetail({holding,onResearch,onEvidence}:{holding:Holding;onResearch:()=>void;onEvidence:(e:Evidence)=>void}){

 const [data,setData]=useState<{thesis:ThesisDetail;bars:Signal[];checked_at:string;price_basis:string;read_across:{symbol:string;source_symbol:string;text:string;connection:string;evidence:Evidence[]}[]}|null>(null);const [error,setError]=useState('');const [busy,setBusy]=useState(false);const [stage,setStage]=useState('');const alive=useRef(true);useEffect(()=>{alive.current=true;return()=>{alive.current=false;};},[]);

 async function reload(){const result=await api<NonNullable<typeof data>>('/api/holding/'+encodeURIComponent(holding.symbol));if(alive.current)setData(result);}

 async function assess(){setBusy(true);setError('');try{const job=await api<Job>('/api/thesis/assess',{symbol:holding.symbol});const result=await followJob(job,j=>setStage(j.stage),()=>alive.current);if(result?.status==='error')throw new Error(result.error?.message);if(alive.current)await reload();}catch(e){if(alive.current)setError((e as Error).message);}finally{if(alive.current)setBusy(false);}}

 async function confirm(broken:boolean){setBusy(true);setError('');try{await api('/api/thesis/judgement',{symbol:holding.symbol,thesis_version:holding.thesis_version,broken});await reload();}catch(e){if(alive.current)setError((e as Error).message);}finally{if(alive.current)setBusy(false);}}

 useEffect(()=>{let current=true;api<typeof data>('/api/holding/'+encodeURIComponent(holding.symbol)).then(r=>{if(current)setData(r);}).catch(e=>current&&setError(e.message));return()=>{current=false;};},[holding.symbol]);

 const bars=data?.bars||[];const prices=bars.map(b=>b.close!);const lo=Math.min(...prices),hi=Math.max(...prices);const y=(v:number)=>105-(v-lo)/(hi-lo||1)*90;const x=(i:number)=>10+i/(bars.length-1||1)*320;

 return <><div className="fn-c"><h3>{holding.name||holding.symbol}</h3><p className="fn-gap">{holding.thesis||'No thesis entered.'}</p><p className="fn-m">{holding.weight===null?'Unweighted':holding.weight+'% of book'} · {holding.sector||'Sector not supplied'}</p></div>

 {error&&<Notice error>{error}</Notice>}{!data&&!error?<Skeleton/>:<div className="fn-c"><h3>Last {bars.length} completed sessions</h3>{bars.length?<><p className="fn-gap">₹{bars.at(-1)?.close?.toLocaleString('en-IN')} · {date(bars.at(-1)?.session,true)}</p><svg viewBox="0 0 340 120" width="100%" role="img" aria-label={`${holding.symbol}: daily close, ${date(bars[0].session)} to ${date(bars.at(-1)?.session)}. Minimum ${lo}, maximum ${hi} rupees.`}><polyline points={bars.map((b,i)=>x(i)+','+y(b.close!)).join(' ')} fill="none" stroke="#16213e" strokeWidth="2"/></svg><details><summary>Inspect daily observations</summary><table><thead><tr><th>Date</th><th>Close ₹</th><th>Volume</th></tr></thead><tbody>{bars.map(b=><tr key={b.session}><td>{date(b.session)}</td><td>{b.close?.toLocaleString('en-IN')}</td><td>{b.volume?.toLocaleString('en-IN')??'Missing'}</td></tr>)}</tbody></table></details></>:<Notice>No completed-session price observations are stored. Refresh source coverage.</Notice>}<p className="fn-f fn-m fn-gap">{data?.price_basis} Source checked {date(data?.checked_at,true)}.</p></div>}

 {data?.thesis&&<><section className="fn-c"><h3>Thesis evidence · {data.thesis.status}</h3><p className="fn-m fn-gap">{data.thesis.note}</p><p className="fn-f">{data.thesis.assessed}/{data.thesis.total} retained filings checked · {data.thesis.unknown} unknown effects</p>{holding.thesis&&<button className="fn-hit" disabled={busy} onClick={assess}>{busy?stage||'Checking…':'Check evidence against this thesis'}</button>}{data.thesis.items.map(i=><details className="fn-gap" key={i.event_id}><summary>{i.title} · {i.effect}</summary><ThesisEvidence record={i.assessment} onEvidence={onEvidence}/>{(!i.assessment||i.assessment.gap)&&<p className="fn-m">{i.assessment?.gap||'This thesis version has not been checked against this filing.'}</p>}</details>)}{data.thesis.status==='weakening'&&<details className="fn-gap"><summary>Record my judgement</summary><p>After reviewing the cited adverse evidence, you can explicitly confirm this thesis is broken. FINN never makes this judgement automatically.</p><button className="fn-button secondary" disabled={busy} onClick={()=>confirm(true)}>I confirm this thesis is broken</button></details>}{data.thesis.confirmation?.broken&&<><p className="fn-m">Your judgement saved {date(data.thesis.confirmation.confirmed_at,true)}.</p><button className="fn-hit" disabled={busy} onClick={()=>confirm(false)}>Clear my broken-thesis judgement</button></>}</section><ThesisHistory data={data.thesis} onEvidence={onEvidence}/></>}

 {data?.read_across.filter(r=>r.symbol===holding.symbol).map((r,i)=><div className="fn-c" key={i}><h3>Read-across hypothesis · {r.source_symbol}</h3><p className="fn-m fn-gap">{r.connection}</p><p className="fn-gap">{r.text}</p>{r.evidence[0]&&<button className="fn-hit" onClick={()=>onEvidence(r.evidence[0])}>Inspect source disclosure <Glyph name="file"/></button>}</div>)}

 <HoldingResearch key={holding.symbol} symbol={holding.symbol} onResearch={onResearch} onEvidence={onEvidence}/>
 <button className="fn-button" onClick={onResearch}>Open research <Glyph name="arrow"/></button></>;

}

