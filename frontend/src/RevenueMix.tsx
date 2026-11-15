import React,{useState} from 'react';
import type {Evidence} from './types';
import {Glyph,Notice,Pill} from './ui';

type Segment={name:string;crore:string;prior_crore:string;share:string|null;growth:string|null;quote:string;evidence:Evidence|null};
type Mix={kind:string;period_end:string;scope:string;unit:string;total_crore:string;segments:Segment[];total_quote:string;total_evidence:Evidence|null;reconciles_to:{crore:string;quote:string;evidence:Evidence;reported_label:string};method:string};
export type RevenueMixData={business:Mix|null;geography:Mix|null}|null;

const amount=(v:string)=>{const n=Number(v);return n.toLocaleString('en-IN',{maximumFractionDigits:Math.abs(n)>=1000?0:1});};
const yearOf=(end:string)=>end.endsWith('12-31')?end.slice(0,4):'FY'+end.slice(2,4);
const COLORS=['#16213e','#d39b24','#3d6fb6','#7a8aa6','#a35d2a','#5c8f6b','#b8c0cf','#6b4300'];

export function RevenueMix({data,onEvidence}:{data?:RevenueMixData;onEvidence:(e:Evidence)=>void}){
 const [view,setView]=useState<'business'|'geography'>('business');
 const mix=data?.[view]||data?.business||data?.geography;
 if(!mix)return <section id="research-mix" className="fn-c"><h3>Revenue mix</h3><Notice>No segment table added up to reported revenue in the reports read, so no mix is shown. Nothing has been estimated.</Notice></section>;
 const active=data?.[view]?view:mix.kind;
 return <section id="research-mix" className="fn-c">
  <div className="fn-row"><h3>Revenue mix</h3><Pill>{yearOf(mix.period_end)} · {mix.scope}</Pill></div>
  {data?.business&&data?.geography&&<div className="fn-tiers" role="group" aria-label="Mix view">{(['business','geography'] as const).map(k=><button key={k} className="fn-hit" aria-pressed={active===k} onClick={()=>setView(k)}><Pill tone={active===k?'navy':'white'}>{k==='business'?'By segment':'By geography'}</Pill></button>)}</div>}
  <div className="fn-mixbar" role="img" aria-label={mix.segments.map(s=>`${s.name} ${Number(s.share).toFixed(0)}%`).join(', ')}>{mix.segments.map((s,i)=><i key={s.name} style={{width:Math.max(0,Number(s.share))+'%',background:COLORS[i%COLORS.length]}}>{Number(s.share)>=12?Math.round(Number(s.share))+'%':''}</i>)}</div>
  <ul className="fn-list">{mix.segments.map((s,i)=><li key={s.name} className="fn-mixrow">
   <span className="fn-dot" style={{background:COLORS[i%COLORS.length]}} aria-hidden="true"/>
   <span className="fn-mixname">{s.name}</span>
   <button className="fn-num" disabled={!s.evidence} onClick={()=>s.evidence&&onEvidence({...s.evidence,quote:s.quote})} aria-label={`${s.name}: ₹${amount(s.crore)} crore, ${Number(s.share).toFixed(1)}% of revenue. Open source row`}>{Number(s.share).toFixed(0)}%</button>
   <span className="fn-f fn-m fn-mixval">₹{amount(s.crore)}</span>
   <span className={'fn-f fn-mixval '+(s.growth==null?'fn-m':Number(s.growth)<0?'fn-neg':'fn-pos')}>{s.growth==null?'—':(Number(s.growth)>0?'+':'')+Number(s.growth).toFixed(1)+'%'}</span>
  </li>)}</ul>
  <p className="fn-f fn-m fn-gap">₹ crore, with growth against the prior year. Segments add up to ₹{amount(mix.total_crore)} crore, which equals reported revenue from operations.</p>
  <button className="fn-hit" onClick={()=>onEvidence({...mix.reconciles_to.evidence,quote:mix.reconciles_to.quote})}>Reported revenue row <Glyph name="file"/></button>
  {mix.total_evidence&&<button className="fn-hit" onClick={()=>onEvidence({...mix.total_evidence!,quote:mix.total_quote})}>Segment total row <Glyph name="file"/></button>}
 </section>;
}
