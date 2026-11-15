import React from 'react';
import type {Evidence} from './types';
import {date} from './product';
import {Notice,Pill} from './ui';
type Source={quote:string;evidence:Evidence};
type Item=Partial<Source>&{metric:string;label:string;values:(string|null)[];qoq:string|null;yoy:string|null;formula?:string;operands?:Source[]};
export type ResultCut={tables:{scope:string;industry_schema:string;page:number;periods:string[];unit:string;headers:Source[];items:Item[];comparison_basis:string}[];gaps:string[]};
const labels:Record<string,string>={revenue:'Revenue',reported_ebitda:'Reported EBITDA',ebitda_proxy:'EBITDA proxy',pbt:'PBT',pbt_continuing:'PBT · continuing',pat:'PAT',pat_continuing:'PAT · continuing',nii:'Net interest income',operating_profit:'Operating profit before provisions'};
const number=(v:string|null,percent=false)=>v===null?'Not comparable':Number(v).toLocaleString('en-IN',{maximumFractionDigits:2})+(percent?'%':'');
export function ResultsSummary({result}:{result?:ResultCut}){
 const table=result?.tables.find(t=>t.scope==='consolidated')||result?.tables[0];
 if(!table)return null;
 const names=table.industry_schema==='financial'?['nii','operating_profit','pbt','pat']:['revenue','reported_ebitda','pbt','pat'];
 const items=names.map(name=>table.items.find(i=>i.metric===name)||(name==='reported_ebitda'?table.items.find(i=>i.metric==='ebitda_proxy'):undefined));
 return <div className="fn-gap"><p className="fn-f fn-m">{table.scope} · {table.unit} · quarter ended {date(table.periods[0])}</p><div className="fn-results-summary">{items.map((item,i)=><div key={names[i]}><span className="fn-f fn-m">{item?labels[item.metric]||item.label:labels[names[i]]}</span><strong>{item?number(item.values[0]):'—'}</strong><span className="fn-f fn-m">{item?.yoy!=null?number(item.yoy,true)+' YoY':'YoY unavailable'}</span></div>)}</div></div>;
}
export function Results({result,onEvidence}:{result:ResultCut;onEvidence:(e:Evidence)=>void}){
 const inspect=(s:Source)=>onEvidence({...s.evidence,quote:s.quote});
 return <details className="fn-c"><summary>Results first cut {result.tables.length?'· verified rows':'· coverage gap'}</summary>
 {result.tables.map((t,i)=><div key={i} className="fn-gap"><Pill>{t.scope} · {t.unit}</Pill><p className="fn-f fn-m fn-gap">Quarter ended {date(t.periods[0],true)}. QoQ: {date(t.periods[1],true)}. YoY: {date(t.periods[2],true)}.</p>
 <table><caption className="sr-only">Quarterly financial results in rupees crore with quarter-on-quarter and year-on-year changes</caption><thead><tr><th>Metric</th><th>Current</th><th>QoQ</th><th>YoY</th></tr></thead><tbody>{t.items.map(item=><tr key={item.metric}><th scope="row">{labels[item.metric]||item.label}</th><td>{number(item.values[0])}</td><td>{number(item.qoq,true)}</td><td>{number(item.yoy,true)}</td></tr>)}</tbody></table>
 <details><summary>Inspect operands and filing pages</summary>{t.items.map(item=><div key={item.metric} className="fn-in fn-gap"><strong>{labels[item.metric]||item.label}</strong><p>{item.values.map(v=>v===null?'Unavailable':number(v)).join(' / ')} · current / prior quarter / prior year</p>{item.formula&&<p className="fn-f fn-m">{item.formula}. This is a proxy, not issuer-reported EBITDA.</p>}{item.evidence&&<button className="fn-hit" onClick={()=>inspect(item as Source)}>Inspect {item.label}</button>}{item.operands?.map((s,j)=><button className="fn-hit" key={j} onClick={()=>inspect(s)}>Inspect proxy operand {j+1}</button>)}</div>)}{t.headers.map((s,j)=><button className="fn-hit" key={j} onClick={()=>inspect(s)}>Inspect {j===0?'scope':j===1?'currency and units':'quarter column '+(j-1)}</button>)}<p className="fn-f fn-m">{t.comparison_basis} Growth = 100 × (current / comparator − 1); zero or negative comparators have no percentage growth.</p></details></div>)}
 {result.gaps.map((gap,i)=><Notice key={i}>{gap}</Notice>)}
 </details>;
}
