import React from 'react';
import {date,reviewed,type RankedEvent,type Review} from './product';
import {Glyph,Notice,Pill} from './ui';

export function recapGroups(events:RankedEvent[],review:Review){
 const groups=new Map<string,RankedEvent[]>();let undated=0;
 for(const event of events){
   const stamp=Date.parse(event.published_at||'');
   if(!Number.isFinite(stamp)){undated++;continue;}
   if(stamp<(review.visit?.cutoff||0)*1000)continue;
   const day=new Date(stamp+330*60000).toISOString().slice(0,10);
   groups.set(day,[...(groups.get(day)||[]),event]);
 }
 return {groups:[...groups].sort(([a],[b])=>b.localeCompare(a)),undated};
}
export function recapText(events:RankedEvent[],review:Review){
 const {groups,undated}=recapGroups(events,review);
 return 'FINN return recap. Missing days are not proof that nothing happened. '+groups.map(([day,items])=>date(day+'T12:00:00+05:30',true)+'. '+items.map(e=>`${e.symbol}. ${e.title}. ${e.reason}. ${reviewed(review,e)?'Reviewed.':e.tier===3?'Routine.':'Outstanding.'}`).join(' ')).join(' ')+(undated?` ${undated} undated items remain in Today.`:'');
}
export function Recap({events,review,onDay,onListen}:{events:RankedEvent[];review:Review;onDay:(day:string)=>void;onListen:()=>void}){
 const {groups,undated}=recapGroups(events,review);
 return <div className="fn-c"><h3>Welcome back.</h3><p className="fn-m fn-gap">Retained changes since {date(new Date((review.visit?.cutoff||0)*1000).toISOString(),true)}. Missing days are not proof that nothing happened.</p>
 <details><summary>Review changes by day</summary>{groups.map(([day,items])=><button key={day} className="fn-row fn-hit fn-recapday" onClick={()=>onDay(day)}><span>{date(day+'T12:00:00+05:30')} · {items.length} {items.length===1?'event':'events'}<span className="fn-m fn-f fn-recapline">{[...new Set(items.map(e=>e.symbol))].join(' · ')}</span></span><Pill tone="amber">{items.filter(e=>!reviewed(review,e)&&e.tier!==3).length} to review</Pill></button>)}
 {!groups.length&&<Notice>No dated changes are retained for this interval. Outstanding items remain below.</Notice>}{undated>0&&<p className="fn-m">{undated} undated items remain in Today and cannot be assigned to a day.</p>}</details>
 <button className="fn-hit" onClick={onListen}><Glyph name="volume" size={15}/>Listen to this recap</button></div>;
}
