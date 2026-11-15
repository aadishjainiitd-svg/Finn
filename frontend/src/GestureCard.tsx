import React,{useRef} from 'react';

/** Optional touch shortcuts; every action retains an explicit button. */
export function GestureCard({children,className,onDone,onPin,onPromote,disabled=false}:{children:React.ReactNode;className:string;onDone:()=>void;onPin:()=>void;onPromote?:()=>void;disabled?:boolean}){
 const start=useRef<{x:number;y:number;at:number}|null>(null);const suppress=useRef(0);
 return <article className={className} style={{touchAction:'pan-y'}}
  onPointerDown={e=>{if(e.pointerType==='touch'&&!disabled)start.current={x:e.clientX,y:e.clientY,at:Date.now()};}}
  onPointerCancel={()=>{start.current=null;}}
  onPointerUp={e=>{const origin=start.current;start.current=null;if(!origin||disabled)return;
   const dx=e.clientX-origin.x,dy=e.clientY-origin.y;
   if(Math.abs(dx)>=80&&Math.abs(dx)>Math.abs(dy)*2){suppress.current=Date.now()+500;if(dx>0)onDone();else onPin();}
   else if(onPromote&&Date.now()-origin.at>=650&&Math.abs(dx)<10&&Math.abs(dy)<10){suppress.current=Date.now()+500;onPromote();}
  }}
  onClickCapture={e=>{if(Date.now()<suppress.current){e.preventDefault();e.stopPropagation();}}}
 >{children}</article>;
}
