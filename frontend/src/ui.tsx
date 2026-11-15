import React,{useEffect,useRef} from 'react';
import * as Dialog from '@radix-ui/react-dialog';

export function Glyph({name,size=19}:{name:string;size?:number}){
 const paths:Record<string,React.ReactNode>={
 today:<><path d="M5 4h14v16H5zM8 8h8M8 12h8M8 16h4"/></>,research:<><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/></>,
 ask:<><path d="M4 4h16v12H9l-5 4zM8 8h8M8 12h5"/></>,watch:<><path d="M6 17V10a6 6 0 0 1 12 0v7l2 2H4zM10 22h4"/></>,book:<><path d="M4 5h16v16H4zM8 2v6M16 2v6M8 12h8M8 16h5"/></>,
 arrow:<path d="M5 12h14m-5-5 5 5-5 5"/>,close:<path d="m6 6 12 12M6 18 18 6"/>,check:<path d="m5 12 4 4L19 6"/>,
 pin:<path d="m9 3 6 0-1 6 4 4v2H6v-2l4-4zM12 15v7"/>,volume:<><path d="m4 9 4 0 5-4v14l-5-4H4zM16 8a6 6 0 0 1 0 8M19 5a10 10 0 0 1 0 14"/></>,
 calendar:<><path d="M4 5h16v16H4zM8 2v6M16 2v6M4 10h16"/></>,chart:<><path d="M4 3v17h17M8 16v-5M13 16V6M18 16V9"/></>,file:<><path d="M6 3h8l4 4v14H6zM14 3v5h4M9 12h6M9 16h6"/></>,
 more:<><circle cx="5" cy="12" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/></>,refresh:<><path d="M20 7v5h-5M4 17v-5h5M5 9a7 7 0 0 1 12-4l3 4M4 15l3 4a7 7 0 0 0 12-4"/></>};
 return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name]||paths.file}</svg>;
}
export function Pill({children,tone=''}:{children:React.ReactNode;tone?:string}){return <span className={'fn-tag '+tone}>{children}</span>;}
export function Notice({children,error=false}:{children:React.ReactNode;error?:boolean}){return <div className={'fn-note '+(error?'error':'')} role={error?'alert':'status'}>{children}</div>;}
export function Sheet({title,header,children,onClose,trigger}:{title:string;header?:React.ReactNode;children:React.ReactNode;onClose:()=>void;trigger?:HTMLElement|null}){
 const returnFocus=useRef(document.activeElement as HTMLElement|null);
 const id=useRef(crypto.randomUUID());const closeRef=useRef(onClose);closeRef.current=onClose;
 useEffect(()=>{
   const parent:string[]=history.state?.finnSheets||[];
   history.pushState({...history.state,finnSheets:[...parent,id.current]},'');
   const back=()=>{if(!(history.state?.finnSheets||[]).includes(id.current))closeRef.current();};
   addEventListener('popstate',back);
   return()=>{removeEventListener('popstate',back);const stack:string[]=history.state?.finnSheets||[];
     // A successful form save or navigation can remove a sheet without Back.
     // Remove its marker and descendants; Forward must never resurrect a form.
     const index=stack.indexOf(id.current);if(index>=0)history.replaceState({...history.state,finnSheets:stack.slice(0,index)},'');
   };
 },[]);
 const dismiss=()=>{const stack:string[]=history.state?.finnSheets||[];if(stack.at(-1)===id.current)history.back();else closeRef.current();};
 return <Dialog.Root open onOpenChange={open=>{if(!open)dismiss();}}><Dialog.Portal><Dialog.Overlay className="fn-overlay"/><Dialog.Content className="fn-sheet" aria-describedby={undefined} onCloseAutoFocus={e=>{const target=trigger||returnFocus.current;if(target?.isConnected){e.preventDefault();target.focus({preventScroll:true});}}}>
 <div className="fn-handle"/><div className="fn-row fn-sheet-heading">{header?<><Dialog.Title className="sr-only">{title}</Dialog.Title><div className="fn-grow">{header}</div></>:<Dialog.Title>{title}</Dialog.Title>}<Dialog.Close className="fn-close" aria-label={'Close '+title}><Glyph name="close"/></Dialog.Close></div>
 <div className="fn-bd">{children}</div></Dialog.Content></Dialog.Portal></Dialog.Root>;
}
export function Skeleton(){return <div className="fn-skeleton" role="status" aria-label="Loading"><div/><div/><div/></div>;}
