import type {Event} from './types.ts';
export type ReviewState={version:1;started:string;known:Record<string,string>;eligible:Record<string,boolean>;reviewed:Record<string,string>};
export function observe(events:Event[], prior:ReviewState|null, at=new Date()):ReviewState {
  const next:ReviewState=prior?{...prior,known:{...prior.known},eligible:{...prior.eligible},reviewed:{...prior.reviewed}}:{version:1,started:at.toISOString(),known:{},eligible:{},reviewed:{}};
  for(const event of events){
    if(!prior){if(!event.published_at || Date.parse(event.published_at)>=+at-86400000)next.eligible[event.id]=true;}
    else if(next.known[event.id]!==event.revision)next.eligible[event.id]=true;
    next.known[event.id]=event.revision;
  }
  return next;
}
export function acknowledge(state:ReviewState,event:Event){return {...state,reviewed:{...state.reviewed,[event.id]:event.revision}};}
export function undo(state:ReviewState,id:string){const reviewed={...state.reviewed};delete reviewed[id];return {...state,reviewed};}
export function isReviewed(state:ReviewState|null,event:Event){return state?.reviewed[event.id]===event.revision;}
export function inWindow(event:Event,window:string,state:ReviewState|null,at=new Date()){
  if(window==='since')return !!state?.eligible[event.id]&&!isReviewed(state,event);
  if(!event.published_at)return true;
  const published=Date.parse(event.published_at);
  if(window==='today'){
    const india=+at+330*60000;const midnight=Math.floor(india/86400000)*86400000-330*60000;return published>=midnight;
  }
  return published>=+at-Number(window)*86400000;
}
export function changedCount(current:Event[],incoming:Event[]){const old=new Map(current.map(e=>[e.id,e.revision]));return incoming.filter(e=>old.get(e.id)!==e.revision).length;}
export function readStored<T>(key:string):T|null{try{return JSON.parse(localStorage.getItem(key)||'null');}catch{return null;}}
export function saveStored(key:string,value:unknown){try{localStorage.setItem(key,JSON.stringify(value));return true;}catch{return false;}}
