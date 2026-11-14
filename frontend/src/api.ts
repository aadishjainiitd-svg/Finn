import type {Job} from './types';
export async function api<T>(path:string,body?:unknown):Promise<T>{
 const r=await fetch(path,{method:body?'POST':'GET',headers:body?{'Content-Type':'application/json'}:undefined,body:body?JSON.stringify(body):undefined,signal:AbortSignal.timeout(90000)});
 const data=await r.json().catch(()=>null);
 if(!r.ok)throw new Error(data?.error?.message||'FINN could not complete this request. Please retry.');
 return data as T;
}
export async function followJob(job:Job,onProgress:(j:Job)=>void,isCurrent:()=>boolean){
 let current=job;
 while(current.status==='running'&&isCurrent()){
  onProgress(current);await new Promise(r=>setTimeout(r,1500));if(!isCurrent())return null;
  current=await api<Job>('/api/jobs/'+current.id);
 }
 return isCurrent()?current:null;
}
