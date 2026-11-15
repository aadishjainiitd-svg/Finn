import {useLayoutEffect,useRef,useState} from 'react';

export type Tab='today'|'research'|'ask'|'watch'|'book';
const tabs:Tab[]=['today','research','ask','watch','book'];
function selected():Tab{
 const value=history.state?.finnTab;
 if(tabs.includes(value))return value;
 const hash=location.hash.slice(1).split('-')[0] as Tab;
 return tabs.includes(hash)?hash:'today';
}

/** Keep navigation local to the browser. Opening a tab never marks a filing read. */
export function useNavigation(ready:boolean,onLeave:()=>void){
 const [tab,setTab]=useState<Tab>(selected);const current=useRef(tab);
 const positions=useRef<Partial<Record<Tab,number>>>({});const restore=useRef<number|null>(null);
 const leave=useRef(onLeave);leave.current=onLeave;
 useLayoutEffect(()=>{
   const previous=history.scrollRestoration;history.scrollRestoration='manual';
   history.replaceState({...history.state,finnTab:current.current},'');
   const scroll=()=>{positions.current[current.current]=globalThis.scrollY;};
   const back=()=>{const next=selected();if(next===current.current)return;
     leave.current();current.current=next;restore.current=positions.current[next]||0;setTab(next);
   };
   addEventListener('scroll',scroll,{passive:true});addEventListener('popstate',back);
   return()=>{history.scrollRestoration=previous;removeEventListener('scroll',scroll);removeEventListener('popstate',back);};
 },[]);
 useLayoutEffect(()=>{
   if(!ready||restore.current===null)return;
   const top=restore.current;restore.current=null;
   globalThis.scrollTo({top,behavior:'instant'});
 },[tab,ready]);
 const navigate=(next:Tab)=>{
   leave.current();if(next===current.current)return;
   positions.current[current.current]=globalThis.scrollY;
   history.replaceState({...history.state,finnTab:current.current,finnSheets:[]},'');
   history.pushState({finnTab:next,finnSheets:[]},'','#'+next);
   current.current=next;restore.current=positions.current[next]||0;setTab(next);
 };
 return {tab,navigate};
}
