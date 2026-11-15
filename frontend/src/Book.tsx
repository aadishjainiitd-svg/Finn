import React,{useState} from 'react';

import {api} from './api';

import type {Book,Holding} from './product';

import {Glyph,Notice,Pill,Sheet} from './ui';



export function BookView({book,onSave,onHolding}:{book:Book;onSave:(b:Book)=>void;onHolding:(h:Holding)=>void}){

 const [filter,setFilter]=useState('');const [edit,setEdit]=useState<Holding|null>(null);const [importing,setImporting]=useState(false);

 const [text,setText]=useState('');const [preview,setPreview]=useState<Holding[]|null>(null);const [error,setError]=useState('');const [busy,setBusy]=useState(false);const [merge,setMerge]=useState(true);

 async function save(rows:Holding[]){setBusy(true);setError('');try{const b=await api<Book>('/api/book',{holdings:rows.map(({symbol,weight,thesis,sector,inputs})=>({symbol,weight,thesis,sector,inputs})),version:book._version});onSave(b);setEdit(null);setImporting(false);setPreview(null);}catch(e){setError((e as Error).message);}finally{setBusy(false);}}

 async function check(){setBusy(true);setError('');try{const r=await api<{holdings:Holding[]}>('/api/book/preview',{text});setPreview(r.holdings);}catch(e){setError((e as Error).message);}finally{setBusy(false);}}

 const hasWeight=book.holdings.filter(h=>h.weight!==null).length;

 return <>{book.thesis_processing&&<Notice>{book.thesis_processing}</Notice>}<section className="fn-c"><div className="fn-row"><h3>{book.holdings.length} holdings</h3><Pill>{book.is_demo?'Demonstration book':'Your book'}</Pill></div>{book.is_demo&&<p className="fn-gap">Mock portfolio of {book.holdings.length} NSE companies across {new Set(book.holdings.map(h=>(h.sector||'').split(' · ')[0]).filter(Boolean)).size} sectors, large, mid and small caps.</p>}<p className="fn-m fn-gap">{hasWeight}/{book.holdings.length} weights entered · {book.holdings.filter(h=>h.thesis).length} theses written</p><div className="fn-in fn-gap">{book.health_counts&&<><div className="fn-healthbar" role="img" aria-label={Object.entries(book.health_counts).map(([s,n])=>`${n} ${s}`).join(', ')}>{Object.entries(book.health_counts).filter(([,n])=>n>0).map(([s,n])=><span key={s} style={{flex:n,background:s==='broken'?'#c0392f':s==='weakening'?'#d39b24':'#cbd1dd'}}/>)}</div><p>{Object.entries(book.health_counts).map(([s,n])=>`${n} ${s}`).join(' · ')}</p></>}Open a holding to inspect its thesis evidence. Missing evidence is never counted as healthy.</div><button className="fn-button fn-gap" onClick={()=>{setImporting(true);setError('');}}>Add, paste or upload holdings <Glyph name="arrow"/></button></section>

 <label className="fn-search">Find a holding<input value={filter} onChange={e=>setFilter(e.target.value)} placeholder="Ticker, name or thesis"/></label>

 {book.holdings.filter(h=>(h.symbol+' '+(h.name||'')+' '+h.thesis).toLowerCase().includes(filter.toLowerCase())).map(h=><article className="fn-c fn-holding" key={h.symbol}><button className="fn-open fn-row" onClick={()=>onHolding(h)}><div><h3>{h.symbol}</h3><p className="fn-m fn-f">{h.sector||h.name||'NSE holding'}</p></div><span className="fn-weight">{h.weight===null?'No weight':h.weight+'%'}</span></button>{h.thesis?<p className="fn-in fn-gap">{h.thesis}</p>:<button className="fn-addthesis" onClick={()=>{setEdit({...h});setError('');}}>+ Add your reason for owning it</button>}<div className="fn-row"><span className="fn-m fn-f">Thesis: {h.thesis_health?.status||'unknown'}{h.thesis_health?` · ${h.thesis_health.adverse} adverse / ${h.thesis_health.unknown} unknown`:''}</span><button className="fn-hit" onClick={()=>{setEdit({...h});setError('');}}>Edit <Glyph name="arrow" size={16}/></button></div></article>)}

 {edit&&<Sheet title={'Edit '+edit.symbol} onClose={()=>setEdit(null)}><label>Position weight (%)<input type="number" min="0" max="100" step="any" value={edit.weight??''} onChange={e=>setEdit({...edit,weight:e.target.value||null})}/></label><label>Your reason for owning it<textarea maxLength={400} value={edit.thesis} onChange={e=>setEdit({...edit,thesis:e.target.value})}/></label><label>Sector (your classification)<input maxLength={80} value={edit.sector} onChange={e=>setEdit({...edit,sector:e.target.value})}/></label><label>Shared inputs (comma separated)<input value={edit.inputs.join(", ")} onChange={e=>setEdit({...edit,inputs:e.target.value.split(",").map(x=>x.trim()).filter(Boolean).slice(0,10)})}/></label><p className="fn-m">Sector and inputs identify possible read-across connections, not proven effects.</p><p className="fn-m">An empty weight stays unknown. Other holdings are not automatically rescaled.</p>{error&&<Notice error>{error}</Notice>}<button className="fn-button" disabled={busy} onClick={()=>save(book.holdings.map(h=>h.symbol===edit.symbol?edit:h))}>{busy?'Saving…':'Save holding'}</button><button className="fn-button secondary" disabled={busy} onClick={()=>save(book.holdings.filter(h=>h.symbol!==edit.symbol))}>Remove from Book</button></Sheet>}

 {importing&&<Sheet title="Add to your book" onClose={()=>setImporting(false)}><p>Paste NSE tickers, or CSV with symbol, weight and thesis columns. Every company is checked before saving.</p><label>Tickers or CSV<textarea rows={5} value={text} onChange={e=>{setText(e.target.value);setPreview(null);}} placeholder="TCS, INFY"/></label><label>Upload CSV<input type="file" accept=".csv,text/csv" onChange={async e=>{const f=e.target.files?.[0];if(f){if(f.size>40000){setError('Choose a CSV smaller than 40 KB.');return;}setText(await f.text());setPreview(null);}}}/></label>{error&&<Notice error>{error}</Notice>}<button className="fn-button secondary" disabled={busy||!text.trim()} onClick={check}>{busy?'Checking identities…':'Preview import'}</button>{preview&&<><div className="fn-c">{preview.map(h=><p key={h.symbol}>{h.symbol} · {h.name} · {h.weight===null?'unweighted':h.weight+'%'}</p>)}</div><label>Import mode<select value={merge?'merge':'replace'} onChange={e=>setMerge(e.target.value==='merge')}><option value="merge">Merge — update matching tickers</option><option value="replace">Replace — remove holdings absent from import</option></select></label><button className="fn-button" disabled={busy} onClick={()=>save(merge?[...book.holdings.filter(h=>!preview.some(p=>p.symbol===h.symbol)),...preview]:preview)}>Save {merge?'merged':'replacement'} book</button></>}</Sheet>}

 </>;

}

