import React,{useEffect,useState} from 'react';
import {api} from './api';
import {Notice,Skeleton} from './ui';
type Usage={observed_tokens:number;unknown_usage_jobs:number;cached_answers:number;answered_questions:number;cost_note:string;coverage_note:string;reports:{id:string;kind:string;status:string;wall_seconds:number|null;tokens:number|null;token_status:string}[]};
export function Stats(){
 const [usage,setUsage]=useState<Usage|null>(null);const [error,setError]=useState('');
 useEffect(()=>{let current=true;api<Usage>('/api/stats').then(r=>{if(current)setUsage(r);}).catch(e=>{if(current)setError(e.message);});return()=>{current=false;};},[]);
 return <>{error?<Notice error>{error}</Notice>:!usage?<Skeleton/>:<><div className="fn-grid2"><div className="fn-c"><p className="fn-f fn-m">Observed model tokens</p><strong>{usage.observed_tokens.toLocaleString('en-IN')}</strong></div><div className="fn-c"><p className="fn-f fn-m">Answers from cache</p><strong>{usage.cached_answers} / {usage.answered_questions}</strong></div></div><Notice>{usage.unknown_usage_jobs} jobs have unknown usage. {usage.cost_note}</Notice><details className="fn-c"><summary>Per-investigation record</summary>{usage.reports.map(r=><div className="fn-in fn-gap" key={r.id}><strong>{r.kind.replaceAll('_',' ')} · {r.status}</strong><p className="fn-f fn-m">{r.id.slice(0,8)} · {r.wall_seconds??'…'} seconds including queue · {r.tokens??'Unknown'} tokens</p><p className="fn-f fn-m">{r.token_status}</p></div>)}</details><p className="fn-f fn-m">{usage.coverage_note}</p></>}</>;
}
