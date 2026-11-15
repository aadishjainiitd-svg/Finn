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

