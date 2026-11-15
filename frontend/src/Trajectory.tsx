import React,{useState} from 'react';
import type {Evidence} from './types';
import {Glyph,Notice,Pill} from './ui';

type Fact={metric:string;reported_label:string;crore:string|null;scope:string;scope_basis?:string;period_start:string;period_end:string;quote:string;evidence_id:string;restatement:string};
type Derived={value:string;operands:string[];label?:string;formula:string};
export type TrajectoryYear={fiscal_year:string;period_end:string|null;gap:boolean;values:Record<string,string>;restated:Record<string,{newer:string;older:string}>;growth:Record<string,{percent:string;current:string;prior:string;formula:string}>;derived:Record<string,Derived>};
type Use={label:string;value:string;facts:string[];reported:boolean;residual?:boolean};
export type Allocation={years:{fiscal_year:string;cfo:string;cfo_fact:string;uses:Use[];net_change:string;check:{reconciled:boolean;residual:string;fx_row:boolean;operands:string[]}|null}[];totals:{label:string;value:string;share_of_cfo:string|null;years_with_row:number}[];total_cfo:string;net_change:string;net_change_share:string|null;excluded:string[];reconciled_years:number;checked_years:number;formula:string};
export type TrajectoryData={scope:string;scope_basis:string[];year_end:string;years:TrajectoryYear[];allocation:Allocation|null;notes:string[];complete:boolean;gaps:string[];coverage:string};

const amount=(v:string|null|undefined)=>{if(v==null)return '—';const n=Number(v);return n.toLocaleString('en-IN',{maximumFractionDigits:Math.abs(n)>=1000?0:1});};
const percent=(v:string)=>{const n=Number(v);return (n>0?'+':'')+n.toFixed(1)+'%';};
export const yearLabel=(fiscal:string,yearEnd:string)=>yearEnd==='12-31'?fiscal:'FY'+fiscal.slice(2);
const METRICS:[string,string][]=[['revenue','Revenue'],['pat','Profit'],['cfo','Operating cash'],['ebitda_margin','EBITDA proxy margin']];

export function Trajectory({data,facts,evidence,onEvidence,onReadOlder,busy}:{data:TrajectoryData;facts:Record<string,Fact>;evidence:Record<string,Evidence>;onEvidence:(e:Evidence)=>void;onReadOlder?:()=>void;busy?:boolean}){
 const [metric,setMetric]=useState('revenue');
 const open=(id?:string)=>{const f=id?facts[id]:undefined;if(f&&evidence[f.evidence_id])onEvidence({...evidence[f.evidence_id],quote:f.quote});};
 const label=(y:TrajectoryYear)=>yearLabel(y.fiscal_year,data.year_end);
 const value=(y:TrajectoryYear,m:string)=>m==='ebitda_margin'?y.derived.ebitda_margin?.value??null:(y.values[m]?facts[y.values[m]]?.crore??null:null);
 const source=(y:TrajectoryYear,m:string)=>m==='ebitda_margin'?y.derived.ebitda_margin?.operands[0]:y.values[m];
 const shown=data.years.map(y=>({y,v:value(y,metric)}));
 const numbers=shown.filter(s=>s.v!=null).map(s=>Number(s.v));
 const high=Math.max(0,...numbers),low=Math.min(0,...numbers);const pos=(v:number)=>100-(v-low)/(high-low||1)*92;
 const restated=data.years.flatMap(y=>Object.entries(y.restated).map(([m,r])=>({y,m,r})));
 const scope=data.scope==='consolidated'?'Consolidated':'Standalone';
 const cell=(y:TrajectoryYear,m:string,text:string,id?:string,tone='')=>y.gap?<td key={y.fiscal_year} className="fn-m">—</td>:text==='—'?<td key={y.fiscal_year} className="fn-m">—</td>:
  <td key={y.fiscal_year} className={tone}><button className="fn-num" aria-label={`${label(y)} ${m}: ${text}. Open source row`} onClick={()=>open(id)}>{text}</button>{y.restated[m]&&<sup aria-label="restated">R</sup>}</td>;
 const rows:[string,string,(y:TrajectoryYear)=>React.ReactNode][]=[
  ['revenue','Revenue',y=>cell(y,'revenue',amount(value(y,'revenue')),y.values.revenue)],
  ['growth','Revenue YoY',y=>{const g=y.growth.revenue;return g?cell(y,'growth',percent(g.percent),g.current,Number(g.percent)<0?'fn-neg':'fn-pos'):cell(y,'growth','—');}],
  ['ebitda','EBITDA proxy margin',y=>{const d=y.derived.ebitda_margin;return d?cell(y,'ebitda',Number(d.value).toFixed(1)+'%',d.operands[0]):cell(y,'ebitda','—');}],
  ['pat','Profit for the year',y=>cell(y,'pat',amount(value(y,'pat')),y.values.pat)],
  ['patg','Profit YoY',y=>{const g=y.growth.pat;return g?cell(y,'patg',percent(g.percent),g.current,Number(g.percent)<0?'fn-neg':'fn-pos'):cell(y,'patg','—');}],
  ['cfo','Operating cash flow',y=>cell(y,'cfo',amount(value(y,'cfo')),y.values.cfo)],
  ['capex','Capex (cash paid)',y=>{const id=y.values.capex;const v=id?facts[id]?.crore:null;return cell(y,'capex',v==null?'—':amount(String(-Number(v))),id);}],
  ['recv','Receivable days',y=>{const d=y.derived.receivable_days;return d?cell(y,'recv',Math.round(Number(d.value))+'d',d.operands[0]):cell(y,'recv','—');}],
  ['inv','Inventory days',y=>{const d=y.derived.inventory_days;return d?cell(y,'inv',Math.round(Number(d.value))+'d',d.operands[0]):cell(y,'inv','—');}],
  ['conv','Cash conversion',y=>{const d=y.derived.cash_conversion;return d?cell(y,'conv',Number(d.value).toFixed(2)+'×',d.operands[0]):cell(y,'conv','—');}],
 ];
 const formulas=Object.values(Object.fromEntries(data.years.flatMap(y=>Object.values(y.derived)).map(d=>[d.formula,d])));
 return <section id="research-trajectory" className="fn-c">
  <div className="fn-row"><h3>Five-year trajectory</h3><Pill tone={data.complete?'':'amber'}>{data.complete?'5 of 5 years':`${5-data.gaps.length} of 5 years`}</Pill></div>
  <p className="fn-f fn-m">{scope} · ₹ crore · {data.year_end==='12-31'?'calendar years':'years ending '+new Date('2000-'+data.year_end+'T00:00:00').toLocaleDateString('en-GB',{day:'numeric',month:'long'})}. {5-data.gaps.length} of 5 years read from primary statements{data.gaps.length?`; ${data.gaps.map(g=>yearLabel(g,data.year_end)).join(', ')} not read yet`:''}.</p>
  <div className="fn-tiers" role="group" aria-label="Chart metric">{METRICS.map(([id,name])=><button key={id} className="fn-hit" aria-pressed={metric===id} onClick={()=>setMetric(id)}><Pill tone={metric===id?'navy':'white'}>{name}</Pill></button>)}</div>
  <div className="fn-bars" role="img" aria-label={shown.map(s=>label(s.y)+': '+(s.y.gap?'not read':s.v==null?'not established':metric==='ebitda_margin'?Number(s.v).toFixed(1)+'%':amount(s.v)+' crore')).join('; ')}>
   {shown.map(({y,v})=><div key={y.fiscal_year}>
    <span>{y.gap?'Not read':v==null?'—':metric==='ebitda_margin'?Number(v).toFixed(1)+'%':amount(v)}</span>
    <svg viewBox="0 0 50 110" aria-hidden="true"><line x1="0" x2="50" y1={pos(0)} y2={pos(0)} stroke="#b8c0cf"/>
     {y.gap?<rect x="8" y="30" width="34" height={pos(0)-30} rx="4" fill="none" stroke="#b8c0cf" strokeDasharray="3 3"/>:v!=null&&<rect x="8" width="34" rx="4" y={Math.min(pos(0),pos(Number(v)))} height={Math.max(1,Math.abs(pos(Number(v))-pos(0)))} fill={Number(v)<0?'#c0392f':'#d39b24'} onClick={()=>open(source(y,metric))}/>}
    </svg><small>{label(y)}</small></div>)}
  </div>
  <p className="fn-f fn-m">Bars are separate reported years. Missing years stay empty; no trend line is drawn through them.</p>
  <div className="fn-scroll"><table className="fn-cmp fn-traj"><thead><tr><th scope="col">₹ crore</th>{data.years.map(y=><th scope="col" key={y.fiscal_year}>{label(y)}</th>)}</tr></thead>
   <tbody>{rows.map(([id,name,render])=><tr key={id}><th scope="row">{name}</th>{data.years.map(y=><React.Fragment key={y.fiscal_year}>{render(y)}</React.Fragment>)}</tr>)}</tbody></table></div>
  <p className="fn-f fn-m">Tap a number to open its statement row. Each year uses the newest report that prints it; growth uses both years from one statement.</p>
  {restated.length>0&&<details className="fn-gap"><summary>{restated.length} restated {restated.length===1?'value':'values'} <sup>R</sup></summary>{restated.map(({y,m,r})=><div className="fn-in fn-gap" key={y.fiscal_year+m}><p>{label(y)} · {facts[r.newer]?.reported_label}</p><p className="fn-f fn-m">Newer report {amount(facts[r.newer]?.crore)} · earlier report {amount(facts[r.older]?.crore)} crore. The newer figure is shown.</p><button className="fn-hit" onClick={()=>open(r.newer)}>Newer report row <Glyph name="file"/></button><button className="fn-hit" onClick={()=>open(r.older)}>Earlier report row <Glyph name="file"/></button></div>)}</details>}
  <details className="fn-gap"><summary>How these are calculated</summary>{formulas.map(d=><p className="fn-f fn-m fn-gap" key={d.formula}>{d.label||'Cash conversion'}: {d.formula}</p>)}
   {data.scope_basis.map(b=><p className="fn-f fn-m fn-gap" key={b}>Scope: {b}.</p>)}{data.notes.map(n=><p className="fn-f fn-m fn-gap" key={n}>{n}</p>)}</details>
  {data.gaps.length>0&&onReadOlder&&<button className="fn-hit" disabled={busy} onClick={onReadOlder}>Read older annual reports for {data.gaps.map(g=>yearLabel(g,data.year_end)).join(', ')} <Glyph name="file"/></button>}
 </section>;
}

export function CashAllocation({data,facts,evidence,onEvidence,yearEnd}:{data:Allocation|null;facts:Record<string,Fact>;evidence:Record<string,Evidence>;onEvidence:(e:Evidence)=>void;yearEnd:string}){
 const open=(id?:string)=>{const f=id?facts[id]:undefined;if(f&&evidence[f.evidence_id])onEvidence({...evidence[f.evidence_id],quote:f.quote});};
 if(!data)return <section id="research-allocation" className="fn-c"><h3>Where the cash went</h3><Notice>Operating, investing and financing totals were not all found in the same statement for any year, so no allocation is shown. Nothing has been filled in.</Notice></section>;
 const years=data.years.map(r=>yearLabel(r.fiscal_year,yearEnd));
 const span=years.length>1?`${years[0]}–${years[years.length-1]}`:years[0];
 const net=Number(data.net_change);
 const bar=(share:string|null)=>{const n=share==null?0:Math.max(0,Math.min(100,Number(share)));return <div className="fn-alloc" aria-hidden="true"><i style={{width:n+'%'}}/></div>;};
 return <section id="research-allocation" className="fn-c">
  <div className="fn-row"><h3>Where the cash went</h3><Pill tone={data.checked_years&&data.reconciled_years===data.checked_years?'':'amber'}>{data.checked_years?`Ties to closing cash ${data.reconciled_years}/${data.checked_years}`:'Closing cash not checked'}</Pill></div>
  <p className="fn-f fn-m">{span} · operating cash ₹{amount(data.total_cfo)} crore across {years.length} {years.length===1?'year':'years'}. Shares are of operating cash.</p>
  <ul className="fn-list fn-gap">{[...data.totals].sort((a,b)=>(a.label.startsWith('Other')?1:0)-(b.label.startsWith('Other')?1:0)||(b.years_with_row?1:0)-(a.years_with_row?1:0)||Number(b.value)-Number(a.value)).map(t=><li key={t.label} className="fn-gap"><div className="fn-row"><span>{t.label}</span><strong>{t.years_with_row?`₹${amount(t.value)}`:'No row'}</strong></div>
   {t.years_with_row>0?<>{bar(t.share_of_cfo)}<p className="fn-f fn-m">{t.share_of_cfo==null?'Share not meaningful (operating cash not positive)':Number(t.share_of_cfo).toFixed(0)+'% of operating cash'}{t.years_with_row<years.length&&t.label!=='Other investing and financing (net)'?` · separate row in ${t.years_with_row} of ${years.length} years`:''}</p></>
    :<p className="fn-f fn-m">No separate row in these statements; any such flow is inside Other. Not zero.</p>}</li>)}
   <li className="fn-gap"><div className="fn-row"><span>{net>=0?'Added to cash':'Drawn from cash'}</span><strong className={net<0?'fn-neg':''}>₹{amount(String(Math.abs(net)))}</strong></div>{net>0&&bar(data.net_change_share)}</li></ul>
  <p className="fn-f fn-m fn-gap">Other is the exact remainder of reported investing and financing cash flow after the named rows, including deposits, investments, interest and borrowings drawn. {data.formula}</p>
  {data.excluded.length>0&&<p className="fn-f fn-m">Left out: {data.excluded.map(y=>yearLabel(y,yearEnd)).join(', ')}. Their operating, investing and financing totals were not all found in one statement.</p>}
  <details className="fn-gap"><summary>Inspect each year</summary>{data.years.map(r=><div className="fn-in fn-gap" key={r.fiscal_year}><div className="fn-row"><strong>{yearLabel(r.fiscal_year,yearEnd)}</strong>{r.check?<Pill tone={r.check.reconciled?'':'amber'}>{r.check.reconciled?'Ties to closing cash':`Unexplained ₹${amount(r.check.residual)}`}</Pill>:<Pill tone="amber">Opening/closing cash not found</Pill>}</div>
   <button className="fn-hit" onClick={()=>open(r.cfo_fact)}>Operating cash ₹{amount(r.cfo)} <Glyph name="file"/></button>
   {r.uses.map(u=><div className="fn-row" key={u.label}><span className="fn-f">{u.label}</span>{u.reported?<button className="fn-num fn-f" onClick={()=>open(u.facts[0])}>₹{amount(u.value)}</button>:<span className="fn-f fn-m">No row</span>}</div>)}
   {r.check&&!r.check.reconciled&&<p className="fn-f fn-m">{r.check.fx_row?'Reported cash movement differs from the totals.':'No exchange-difference row was identified; the gap may be FX or a row this reader did not recognise.'}</p>}
  </div>)}</details>
 </section>;
}
