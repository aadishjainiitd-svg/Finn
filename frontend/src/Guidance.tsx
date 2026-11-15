import React,{useEffect,useState} from 'react';
import {api} from './api';
import type {Evidence} from './types';
import {Glyph,Pill} from './ui';

export type GuidanceItem={label:string;status:string;reason:string;quote:string;speaker?:string;evidence:Evidence;due?:string|null;actual?:{value:string;unit?:string;quote?:string;evidence:Evidence}|null};
type Guidance={available:boolean;checked_at?:string;items:GuidanceItem[]};

export const guidancePill=(status:string):[string,string]=>({
 met:['Met','green'],missed:['Missed','red'],indicative:['Indicative only','amber'],not_due:['Not due yet',''],
 revised:['Revised','amber'],withdrawn:['Withdrawn','amber'],not_comparable:['Not comparable','']} as Record<string,[string,string]>)[status]||[status.replaceAll('_',' '),''];

export function GuidanceCard({symbol,onEvidence}:{symbol:string;onEvidence:(e:Evidence)=>void}){
 const [data,setData]=useState<Guidance|null>(null);const [failed,setFailed]=useState(false);
 useEffect(()=>{let live=true;setData(null);setFailed(false);
  api<Guidance>('/api/guidance/'+encodeURIComponent(symbol)).then(d=>{if(live)setData(d);}).catch(()=>{if(live)setFailed(true);});
  return()=>{live=false;};},[symbol]);
 const top=data?.items[0];
 const [label,tone]=top?guidancePill(top.status):['No guidance read',''];
 return <div className="fn-c"><h3 className="fn-label">Their guidance</h3>
  {!data&&!failed?<p className="fn-f fn-m">Checking saved research…</p>:failed?<><Pill>Unavailable</Pill><p>Saved guidance could not be loaded.</p></>:
   !data!.available?<><Pill>No research yet</Pill><p>Read {symbol}'s latest call in Research to find management guidance.</p></>:
   !top?<><Pill>{label}</Pill><p>No numerical management guidance passed the checks in the calls read. That does not mean none was given.</p></>:
   <><Pill tone={tone}>{label}</Pill><p>{top.label}</p>
    {top.actual&&<p className="fn-f">Actual {Number(top.actual.value).toFixed(1)}%{top.actual.unit?.includes('proxy')?' (EBITDA proxy)':''}</p>}
    <p className="fn-f fn-m">{top.reason}</p>
    <button className="fn-hit" onClick={()=>onEvidence({...top.evidence,quote:top.quote})}>{top.speaker?top.speaker.split(' ')[0]+"'s words":'Source'} <Glyph name="file" size={14}/></button>
    {data!.items.length>1&&<p className="fn-f fn-m">{data!.items.length-1} more in Research › Promises.</p>}</>}
 </div>;
}
