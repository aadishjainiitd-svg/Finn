import {useEffect,useRef,useState} from 'react';
type Recognition={lang:string;continuous:boolean;interimResults:boolean;start:()=>void;abort:()=>void;onresult:((event:{results:{[n:number]:{[n:number]:{transcript:string}}}})=>void)|null;onerror:((event:unknown)=>void)|null;onend:(()=>void)|null};
export function useDictation(onText:(text:string)=>void,onError:(message:string)=>void){
 const active=useRef<Recognition|null>(null);const callbacks=useRef({onText,onError});callbacks.current={onText,onError};
 const [listening,setListening]=useState(false);
 useEffect(()=>()=>{if(active.current){active.current.onresult=null;active.current.onerror=null;active.current.onend=null;active.current.abort();}},[]);
 function dictate(){
  if(active.current){active.current.abort();active.current=null;setListening(false);return;}
  const browser=globalThis as unknown as {SpeechRecognition?:new()=>Recognition;webkitSpeechRecognition?:new()=>Recognition};
  const Constructor=browser.SpeechRecognition||browser.webkitSpeechRecognition;
  if(!Constructor){callbacks.current.onError('Speech input is unavailable. Typing is still available.');return;}
  const recognition=new Constructor();active.current=recognition;recognition.lang='en-IN';recognition.continuous=false;recognition.interimResults=false;
  recognition.onresult=event=>callbacks.current.onText(event.results[0][0].transcript.slice(0,600));
  recognition.onerror=()=>callbacks.current.onError('Microphone input did not complete. Typing is still available.');
  recognition.onend=()=>{active.current=null;setListening(false);};
  try{recognition.start();setListening(true);}catch{active.current=null;setListening(false);callbacks.current.onError('Microphone input could not start. Typing is still available.');}
 }
 return {dictate,listening};
}
