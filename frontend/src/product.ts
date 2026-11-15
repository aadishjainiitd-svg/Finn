import type {Event} from './types';

import type {ResultCut} from './Results';

import type {ThesisRecord} from './Thesis';

export type Holding={symbol:string;name?:string;isin?:string;weight:string|null;thesis:string;thesis_version?:string;thesis_health?:{status:string;supporting:number;adverse:number;unknown:number;total:number};sector:string;inputs:string[]};

export type Book={holdings:Holding[];is_demo:boolean;label:string;_version:number;health_counts?:Record<string,number>;thesis_processing?:string};

export type Review={reviewed:Record<string,string>;pins:Record<string,boolean>;feedback:Record<string,string>;promotions:string[];known?:Record<string,string>;eligible?:Record<string,string>;_version:number;visit:null|{opened_at:number;active_at:number;cutoff:number;first:boolean;returning:boolean}};

export type Session={book:Book;review:Review;storage:{mode:string;recovery:string};telegram:{configured:boolean;connected:boolean}};

export type RankedEvent=Event&{results?:ResultCut;thesis_assessment?:ThesisRecord|null;children?:RankedEvent[];lead_filing_id?:string;category?:string;management_profile?:{text:string;evidence:Event['evidence'][number];label:string};score?:number;promoted?:boolean;weight?:string|null;thesis?:string;thesis_status?:string;ranking_note?:string;ranking_reasons?:{label:string;value:number;explanation:string;evidence?:Event['evidence']}[]};

export function reviewed(review:Review|undefined,event:Event){return review?.reviewed[event.id]===event.revision;}

export function inPeriod(event:Event,window:string,review:Review|undefined,start='',end='',now=Date.now()){

 const stamp=event.published_at?Date.parse(event.published_at):null;

 if(window==='since')return !!review?.pins[event.id]||(!reviewed(review,event)&&(

   review?.eligible?.[event.id]===event.revision||stamp===null||stamp>=(review?.visit?.cutoff??now/1000-86400)*1000));

 if(window==='custom')return stamp===null||stamp>=Date.parse(start+'T00:00:00+05:30')&&stamp<=Date.parse(end+'T23:59:59+05:30');

 return stamp===null||stamp>=now-Number(window)*86400000;

}

export const date=(value?:string|null,full=false)=>value?new Intl.DateTimeFormat('en-IN',{timeZone:'Asia/Kolkata',day:'numeric',month:'short',...(full?{year:'numeric' as const}:{})}).format(new Date(value)):'Date unavailable';


// Header date in the reference style, e.g. "Sun 15 Nov" (IST).
export const weekday=(value:Date)=>new Intl.DateTimeFormat('en-IN',{timeZone:'Asia/Kolkata',weekday:'short',day:'numeric',month:'short'}).formatToParts(value).filter(p=>p.type!=='literal').map(p=>p.value).join(' ');

// Per-filing thesis effect (backend: weakens|supports|neutral|unknown). Holding-level
// health (weakening/broken) is a different field shown in Book.
export const thesisLabel=(status?:string|null):[string,''|'red'|'green']=>status==='weakens'?['Weakens your thesis','red']:status==='supports'?['Supports your thesis','green']:status==='neutral'?['No thesis effect found','']:['Thesis not assessed',''];
// Short event type for the card subtitle, from the verified category or kind.
export const eventType=(e:{kind:string;category?:string;description?:string})=>{if(e.kind==='price')return 'Unusual move';const raw=(e.category||(e.description||'').split(' · ')[0]||'Disclosure').slice(0,40);return raw.charAt(0).toUpperCase()+raw.slice(1);};

// Readable title for a threaded results event; original filing titles are unchanged.
export const displayTitle=(title:string)=>{const m=title.match(/results period ended (\d{4}-\d{2}-\d{2})/);return m?'Results for the period ended '+date(m[1],true):title;};
/** Icon colour family for an event: price, results, people, capital, or other filing. */
export const typeTone=(e:{kind?:string;category?:string;title?:string;reason?:string})=>{
 if(e.kind==='price')return 'price';
 const text=`${e.category||''} ${e.title||''} ${e.reason||''}`.toLowerCase();
 if(/result|earning|financial/.test(text))return 'results';
 if(/director|appoint|management|resign|ceo|cfo|auditor/.test(text))return 'people';
 if(/dividend|capital|allot|buyback|bonus|split|rating|debt|borrow/.test(text))return 'capital';
 return 'filing';};
