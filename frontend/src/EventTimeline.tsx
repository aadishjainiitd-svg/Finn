import React from 'react';
import {date,type RankedEvent} from './product';
export function EventTimeline({event,onRead}:{event:RankedEvent;onRead:(e:RankedEvent)=>void}){
 const items=event.children||[event];
 const label=(e:RankedEvent)=>/transcript/i.test(e.title+' '+e.description)?'Transcript':/presentation/i.test(e.title+' '+e.description)?'Presentation':/financial results|board meeting/i.test(e.title+' '+e.description)?'Results':/call/i.test(e.title+' '+e.description)?'Call notice':/newspaper|publication/i.test(e.title+' '+e.description)?'Publication':'Disclosure';
 return <div className="fn-c"><h3 className="sr-only">Disclosure timeline</h3><div className="fn-eventline" role="list" aria-label="Observed disclosures; no future completion inferred">{items.map(child=><div role="listitem" key={child.id}><span className="fn-eventtrack"/><button className="fn-hit fn-timelink" onClick={()=>onRead(child)} aria-label={'Inspect disclosure: '+child.title}><span>{label(child)}<span className="fn-f fn-m fn-recapline">{date(child.published_at)}</span></span></button></div>)}</div>{items.length===1&&<p className="fn-f fn-m">One retained disclosure. No further event stage is assumed complete.</p>}</div>;
}
