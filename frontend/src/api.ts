import type {Job} from './types';
let visitId=crypto.randomUUID().replaceAll('-','');
try{visitId=sessionStorage.getItem('finn.visit.v1')||visitId;sessionStorage.setItem('finn.visit.v1',visitId);}catch{/* Tab-local memory still preserves this page's visit. */}
export async function api<T>(path:string,body?:unknown):Promise<T>{
 if(!navigator.onLine)throw new Error('Offline. Reconnect before changing saved state or requesting new sources.');
 const r=await fetch(path,{method:body?'POST':'GET',headers:{'X-Finn-Visit':visitId,...(body?{'Content-Type':'application/json','X-Finn-Request':'1'}:{})},body:body?JSON.stringify(body):undefined,signal:AbortSignal.timeout(90000)});
 const data=await r.json().catch(()=>null);
 if(!r.ok)throw new Error(data?.error?.message||(typeof data?.detail==='string'?data.detail:'FINN could not complete this request. Please retry.'));
 return data as T;
}
export async function followJob<T>(job:Job<T>,onProgress:(j:Job<T>)=>void,isCurrent:()=>boolean){
 let current=job;
 while(current.status==='running'&&isCurrent()){
  onProgress(current);await new Promise(r=>setTimeout(r,1500));if(!isCurrent())return null;
  current=await api<Job<T>>('/api/jobs/'+current.id);
 }
 return isCurrent()?current:null;
}
