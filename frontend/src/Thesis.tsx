import React from 'react';
import type {Evidence} from './types';
import {date} from './product';
import {Glyph,Pill} from './ui';

export type ThesisRecord={thesis:string;thesis_version?:string;title:string;checked_at:string;gap?:string;observations:{effect:'supports'|'weakens'|'neutral';sources:{quote:string;evidence:Evidence}[]}[]};
export type ThesisDetail={status:string;assessed:number;total:number;unknown:number;note:string;confirmation?:{broken:boolean;confirmed_at:string}|null;items:{event_id:string;title:string;effect:string;assessment:ThesisRecord|null}[];versions:{id:string;thesis:string;created_at:string}[];history:ThesisRecord[]};
export function ThesisEvidence({record,onEvidence}:{record?:Pick<ThesisRecord,'observations'>|null;onEvidence:(e:Evidence)=>void}){
 return <>{record?.observations.map((o,i)=><div className="fn-gap" key={i}><Pill tone={o.effect==='weakens'?'red':''}>{o.effect} · FINN interpretation</Pill>{o.sources.map((s,n)=><div key={n}><p className="fn-gap">{s.quote}</p><button className="fn-hit" onClick={()=>onEvidence({...s.evidence,quote:s.quote})}>Inspect PDF p. {s.evidence.page} <Glyph name="file" size={15}/></button></div>)}</div>)}</>;
}
export function ThesisHistory({data,onEvidence}:{data:ThesisDetail;onEvidence:(e:Evidence)=>void}){
 return <details className="fn-c"><summary>Thesis versions · {data.versions.length}</summary>{data.versions.map(v=><div className="fn-gap" key={v.id}><p>{v.thesis||'Thesis cleared'}</p><p className="fn-f fn-m">Saved {date(v.created_at,true)}</p>{data.history.filter(r=>r.thesis_version===v.id).map((r,i)=><details key={i}><summary>{r.title} · earlier interpretation</summary><ThesisEvidence record={r} onEvidence={onEvidence}/>{r.gap&&<p>{r.gap}</p>}</details>)}</div>)}</details>;
}
