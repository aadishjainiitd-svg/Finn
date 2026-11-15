import React from 'react';
import type {Evidence} from './types';
import {Glyph,Notice,Pill} from './ui';
import {date} from './product';

type Aspect='business'|'favourable'|'adverse'|'accounting';
export type NarrativeData={retained_selection?:boolean;selection_checked_at?:string;refresh_error?:string;status:string;observations:{aspect:Aspect;nature:string;sources:{quote:string;evidence:Evidence}[]}[];missing:Aspect[];coverage:string;limitation:string;error?:string};
export function Narrative({data,onEvidence}:{data?:NarrativeData;onEvidence:(e:Evidence)=>void}){
 const labels:Record<Aspect,string>={business:'What the business does',favourable:'The favourable case',adverse:'The adverse case',accounting:'Notes that deserve a look'};
 function point(aspect:Aspect){const observation=data?.observations.find(o=>o.aspect===aspect);return <div className="fn-in fn-gap"><h4>{labels[aspect]}</h4>{observation?<><Pill>{observation.nature==='interpretation'?'FINN interpretation':'Reported in source'}</Pill>{observation.sources.map((s,i)=><div key={i}><blockquote>{s.quote}</blockquote><button className="fn-hit" onClick={()=>onEvidence({...s.evidence,quote:s.quote})}>{s.evidence.kind==='annual'?'Annual report':'Management call'} · {s.evidence.period} · p. {s.evidence.page} <Glyph name="file"/></button></div>)}</>:<p className="fn-f fn-m fn-gap">{aspect==='business'?'No complete business description selected.':aspect==='accounting'?'No substantive accounting concern selected; this does not establish that none exists.':`No ${aspect} point passed the source checks. This side of the case is incomplete.`}</p>}</div>;}
 return <section className="fn-c" id="research-case"><details><summary><strong>Business, bull and bear</strong><span className="fn-f fn-m"> · {data?.observations.length||0} cited points</span></summary>{data?<>{data.retained_selection&&<Notice>Saved selection from {date(data.selection_checked_at,true)}. {data.refresh_error}</Notice>}{data.error&&<Notice error>{data.error}</Notice>}<p className="fn-f fn-m fn-gap">{data.coverage}</p>{point('business')}{point('favourable')}{point('adverse')}{point('accounting')}<p className="fn-f fn-m fn-gap">{data.limitation}</p></>:<Notice>Read primary documents to build the balanced view. No case is inferred from the saved excerpts alone.</Notice>}</details></section>;
}
