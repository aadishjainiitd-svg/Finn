export function filingExcerpt(text:string){
 const start=text.search(/\b(?:In furtherance|Pursuant to|we wish to inform|the board|we hereby)\b/i);
 const body=start>=0?text.slice(start):text;
 // Protect honorifics and initials before sentence splitting. Restore exact bytes
 // afterwards; the resulting quote must be a contiguous source substring.
 const protectedText=body.replace(/\b(Mr|Ms|Mrs|Dr|No)\./g,'$1\uE000').replace(/\b([A-Z])\.(?=\s+[A-Z])/g,'$1\uE000');
 const sentences=protectedText.split(/(?<=[.!?])\s+/).map(s=>s.replaceAll('\uE000','.'));
 const quote=sentences.find(s=>/approved|appoint|resign|financial results|revenue|investment/i.test(s)&&s.length>50&&s.length<=1400)||sentences.find(s=>s.length>60&&s.length<=1400);
 return quote&&text.includes(quote)?quote:text;
}
