import React,{useEffect,useRef,useState} from 'react';
import {api} from './api';
import type {Evidence} from './types';
import {Financials,type FinancialsData} from './Financials';
import {ResearchInsights,type Changes,type Commitments} from './ResearchInsights';
import {Notice,Skeleton} from './ui';
import {date} from './product';

type Pack={checked_at:string;financials?:FinancialsData;report_changes?:Changes;commitments?:Commitments};
export function HoldingResearch({symbol,onEvidence,onResearch}:{symbol:string;onEvidence:(e:Evidence)=>void;onResearch:()=>void}){
 const [pack,setPack]=useState<Pack|null>(null);const [busy,setBusy]=useState(false);const [loaded,setLoaded]=useState(false);const [error,setError]=useState('');const requested=useRef(false);const active=useRef(true);
 useEffect(()=>{active.current=true;return ()=>{active.current=false;};},[]);
 async function load(){if(requested.current)return;requested.current=true;setBusy(true);setError('');try{const result=await api<{pack:Pack|null}>('/api/research-pack/'+encodeURIComponent(symbol));if(active.current){setPack(result.pack);setLoaded(true);}}catch(e){if(active.current){setError((e as Error).message);requested.current=false;}}finally{if(active.current)setBusy(false);}}
 return <details className="fn-c" onToggle={e=>{if(e.currentTarget.open)load();}}><summary><strong>Cash, commitments and report changes</strong></summary>{busy&&<Skeleton/>}{error&&<Notice error>{error}<button className="fn-hit" onClick={load}>Retry saved research</button></Notice>}{loaded&&!pack&&<Notice>No saved research is available for {symbol}. Open Research to read primary documents.</Notice>}{pack&&<><p className="fn-f fn-m fn-gap">Same saved analysis as Research · sources checked {date(pack.checked_at,true)}.</p><Financials idPrefix={'holding-'+symbol} data={pack.financials} onEvidence={onEvidence}/><ResearchInsights idPrefix={'holding-'+symbol} changes={pack.report_changes} commitments={pack.commitments} onEvidence={onEvidence}/></>}<button className="fn-hit" onClick={onResearch}>Open full research</button></details>;
}
