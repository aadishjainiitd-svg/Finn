import asyncio
import hashlib
import json
import os
import re
import sys
import time
import uuid
from pathlib import Path
import psutil
from .config import DATA, PARSER
from .network import fetch, SourceError
from .sources import now
from .store import db

def normal(text): return ' '.join(text.split())

def validate_identity(company, doc, opening):
    text=normal(opening).lower()
    name=re.sub(r'[^a-z0-9 ]',' ',company['name'].lower())
    terms=[t for t in name.split() if t not in ('limited','ltd','india','and')]
    # First distinctive issuer token and a majority of the remaining words.
    if not terms or terms[0] not in text or sum(t in text for t in terms)<max(1,(len(terms)+1)//2):
        raise SourceError('issuer_mismatch','PDF issuer does not match the exchange identity. Document quarantined.')
    if doc['kind']=='annual':
        if not re.search(r'annual\s+report',text): raise SourceError('type_mismatch','PDF is not identifiable as an annual report.')
        year=re.search(r'20\d{2}',doc['discovery_period'])
        if year and year[0] not in text: raise SourceError('period_mismatch','Annual-report year cannot be verified in the document.')
    elif doc['kind']=='transcript' and not ('transcript' in text or ('moderator' in text and 'call' in text)):
        raise SourceError('type_mismatch','PDF is not an earnings-call transcript.')
    # Preserve the actual source period phrase; do not infer fiscal year from fetch date.
    patterns=[r'(?:quarter|half.year|year)\s+ended\s+[A-Za-z0-9, /-]{6,35}',r'(?:Q[1-4]\s*(?:FY)?\s*\d{2,4})',r'(?:20\d{2}\s*[-–]\s*(?:20)?\d{2})']
    periods=[m[0].strip() for p in patterns for m in list(re.finditer(p,normal(opening),re.I))[:3]]
    return '; '.join(dict.fromkeys(periods))[:180] or doc['discovery_period']+' (source label; period not independently extracted)'

async def ingest(company,doc,progress):
    started=time.monotonic(); path=DATA/(uuid.uuid4().hex+'.pdf'); proc=None
    try:
        _,download=await fetch(doc['download_url'],40_000_000,path)
        with path.open('rb') as f:
            if f.read(5)!=b'%PDF-': raise SourceError('not_pdf','Source did not return a PDF.')
            f.seek(0); digest=hashlib.file_digest(f,'sha256').hexdigest()
        with db() as c:
            old=c.execute('SELECT meta FROM documents WHERE hash=?',(digest,)).fetchone()
        if old: return json.loads(old['meta'])
        meta={**company,**doc,**download,'original_url':doc['original_url'],'hash':digest,'fetched_at':now(),'parser':PARSER,'publication_date':None}
        proc=await asyncio.create_subprocess_exec(sys.executable,'-m','backend.extract_worker',str(path),
                  stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.DEVNULL,limit=2_000_000)
        peak=0; count=0; chars=0; opening=[]
        async def monitor():
            nonlocal peak
            while proc.returncode is None:
                try:
                    combined=psutil.Process().memory_info().rss+psutil.Process(proc.pid).memory_info().rss
                    peak=max(peak,combined)
                    if combined>440*1024*1024:
                        proc.kill(); raise SourceError('memory_limit','Document processing exceeded the hosting memory budget.')
                except psutil.NoSuchProcess: break
                await asyncio.sleep(.1)
        async def read_pages():
            nonlocal count,chars
            while line:=await proc.stdout.readline():
                row=json.loads(line); count=row['page']; content=normal(row['text']); chars+=len(content)
                if count<=12: opening.append(content)
                # Page-local overlap preserves sentence context and stable PDF page coordinates.
                with db() as c:
                    for index,start in enumerate(range(0,len(content),1800)):
                        text=content[start:start+2200]
                        if len(text)<30: continue
                        eid=f'{digest}-p{count}-c{index}'
                        c.execute('INSERT OR REPLACE INTO chunks VALUES (?,?,?,?)',(eid,digest,count,text))
                        c.execute('INSERT INTO search VALUES (?,?,?)',(eid,digest,text))
                progress.update({'pages':count,'document':doc['title']})
            await proc.wait()
            if proc.returncode: raise SourceError('parse_failed','PDF extraction failed within the processing limits.')
        tasks=[asyncio.create_task(read_pages()),asyncio.create_task(monitor())]
        try:
            async with asyncio.timeout(max(1,180-(time.monotonic()-started))):
                await asyncio.gather(*tasks)
        finally:
            for task in tasks: task.cancel()
            if proc.returncode is None: proc.kill(); await proc.wait()
            await asyncio.gather(*tasks,return_exceptions=True)
        if chars<500: raise SourceError('empty_extraction','PDF has too little readable text. OCR is outside this prototype.')
        meta['period']=validate_identity(company,doc,' '.join(opening))
        meta.update(pages=count,characters=chars,processing_seconds=round(time.monotonic()-started,2),combined_peak_mb=round(peak/1024**2,1))
        with db() as c: c.execute('INSERT INTO documents VALUES (?,?,?,?)',(digest,company['symbol'],doc['kind'],json.dumps(meta)))
        return meta
    except TimeoutError:
        raise SourceError('processing_timeout','Document exceeded the 180-second processing limit.') from None
    finally:
        if proc and proc.returncode is None: proc.kill(); await proc.wait()
        path.unlink(missing_ok=True)
        # Incomplete versions cannot become retrievable evidence.
        with db() as c:
            c.execute('DELETE FROM search WHERE hash NOT IN (SELECT hash FROM documents)')
            c.execute('DELETE FROM chunks WHERE hash NOT IN (SELECT hash FROM documents)')

def retrieve(documents,question):
    words=re.findall(r'[a-zA-Z]{3,}',question.lower())
    stop={'what','which','does','from','this','that','with','have','their','about','were','company','latest','annual','report','transcript','the','and'}
    terms=[w for w in words if w not in stop]
    expansions={'risk':['risk','challenge','uncertainty'],'outlook':['outlook','expect','demand','growth'], 'margin':['margin','profitability'], 'business':['segment','business','products']}
    for key, extra in expansions.items():
        if any(key in w for w in words): terms.extend(extra)
    query=' OR '.join('"'+w+'"' for w in dict.fromkeys(terms)) or '"business"'
    results=[]
    with db() as c:
        for doc in documents:
            rows=c.execute('SELECT id,text FROM search WHERE search MATCH ? AND hash=? ORDER BY bm25(search) LIMIT 4',(query,doc['hash'])).fetchall()
            if not rows:
                rows=c.execute('SELECT id,text FROM chunks WHERE hash=? ORDER BY page LIMIT 2',(doc['hash'],)).fetchall()
            for r in rows:
                row=c.execute('SELECT page FROM chunks WHERE id=?',(r['id'],)).fetchone()
                results.append({**doc,'id':r['id'],'page':row['page'],'text':r['text']})
    return results
