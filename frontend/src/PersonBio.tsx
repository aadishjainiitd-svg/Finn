import React,{useEffect,useState} from 'react';
import {Glyph,Pill} from './ui';
export {personName} from './product';

type Summary={title:string;extract:string;url:string};

/** Outside background for an incoming or departing executive. Wikipedia is
 * shown only when its summary mentions the company (so a namesake is never
 * shown); LinkedIn and web searches are always offered. Nothing is stored. */
export function PersonBio({name,company}:{name:string;company:string}){
 const [summary,setSummary]=useState<Summary|null>(null);const [state,setState]=useState<'loading'|'done'>('loading');
 const firstWord=(company||'').split(/\s+/)[0]||'';
 useEffect(()=>{let live=true;setSummary(null);setState('loading');
  fetch('https://en.wikipedia.org/api/rest_v1/page/summary/'+encodeURIComponent(name.replace(/ /g,'_')),{headers:{accept:'application/json'}})
   .then(r=>r.ok?r.json():null).then(d=>{if(!live)return;
    const extract:string=d?.extract||'';
    if(d&&d.type==='standard'&&firstWord.length>2&&extract.toLowerCase().includes(firstWord.toLowerCase()))
     setSummary({title:d.title,extract:extract.length>420?extract.slice(0,417).replace(/\s+\S*$/,'')+'…':extract,url:d.content_urls?.desktop?.page||''});
    setState('done');})
   .catch(()=>{if(live)setState('done');});
  return()=>{live=false;};},[name,firstWord]);
 const query=encodeURIComponent(`${name} ${company}`);
 return <div className="fn-c fn-bio"><div className="fn-row"><h3>Who is {name}?</h3><Pill tone="white">Outside source</Pill></div>
  {state==='loading'?<p className="fn-f fn-m">Looking for a public profile…</p>:summary?<><p className="fn-gap">{summary.extract}</p><a className="fn-hit" href={summary.url} target="_blank" rel="noreferrer">Wikipedia · {summary.title} <Glyph name="arrow" size={14}/></a></>
   :<p className="fn-f fn-m fn-gap">No public encyclopedia profile clearly matches this person and company. Check their professional background directly:</p>}
  <div className="fn-formactions"><a className="fn-button secondary" href={`https://www.linkedin.com/search/results/people/?keywords=${query}`} target="_blank" rel="noreferrer">LinkedIn profile search</a><a className="fn-button secondary" href={`https://duckduckgo.com/?q=${query}`} target="_blank" rel="noreferrer">Web search</a></div>
  <p className="fn-f fn-m">Outside sources are not verified by FINN; the filing itself remains the record.</p></div>;
}
