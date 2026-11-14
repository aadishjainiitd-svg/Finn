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
from .store import db,put

def normal(text): return ' '.join(re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]','',text).split())

SPEAKER=re.compile(r'(?<!\w)((?:[A-Z][A-Za-z]*|[A-Z]\.)(?:\s+(?:[A-Z][A-Za-z]*|[A-Z]\.)){0,4}):')

def speaker_key(name):return re.sub(r'[^a-z]','',name.lower())

def extraction_version(digest,parser=PARSER,kind='document'):
    return digest+'-x'+hashlib.sha256(parser.encode()).hexdigest()[:10]+'-'+kind

def management_names(opening):
    names=[]
    pattern=r'\b(?:MR|MS|MRS|DR)\.?\s+([A-Za-z.]+(?:\s+[A-Za-z.]+){0,4}?)\s*(?:[–—-]|,)'
    for m in re.finditer(pattern,opening,re.I):
        role=opening[m.end():m.end()+100].lower()
        # Stop at the next named participant, so an analyst cannot inherit a later officer's role.
        role=re.split(r'\b(?:mr|ms|mrs|dr)\.?\s',role)[0]
        if re.search(r'chief|director|president|head|\bcfo\b|\bceo\b|\bcoo\b',role):names.append(m[1])
    return list(dict.fromkeys(names))

def validate_identity(company, doc, opening):
    text=normal(opening).lower()
    name=re.sub(r'[^a-z0-9 ]',' ',company['name'].lower())
    terms=[t for t in name.split() if t not in ('limited','ltd','india','and')]
    # Require every distinctive legal-name token; a shared group name is insufficient.
    if not terms or not all(re.search(r'\b'+re.escape(t)+r'\b',text) for t in terms):
        raise SourceError('issuer_mismatch','PDF issuer does not match the exchange identity. Document quarantined.')
    if doc['kind']=='filing':return doc['discovery_period']
    if doc['kind']=='annual':
        if not re.search(r'annual\s+report',text): raise SourceError('type_mismatch','PDF is not identifiable as an annual report.')
        year=re.search(r'20\d{2}',doc['discovery_period'])
        if year and year[0] not in text: raise SourceError('period_mismatch','Annual-report year cannot be verified in the document.')
    elif doc['kind']=='transcript' and not ('transcript' in text or ('moderator' in text and 'call' in text)):
        raise SourceError('type_mismatch','PDF is not an earnings-call transcript.')
    if doc['kind']=='transcript':
        year=re.search(r'20\d{2}',doc['discovery_period'])
        if year and year[0] not in text:
            raise SourceError('period_mismatch','Transcript date does not match the discovery period.')
    # Preserve the actual source period phrase; do not infer fiscal year from fetch date.
    if doc['kind']=='annual':
        end=int(re.search(r'20\d{2}',doc['discovery_period'])[0])
        match=re.search(str(end-1)+r'\s*[-–]\s*(?:'+str(end)+'|'+str(end)[2:]+r')\b',text)
        if match:return match[0]
        match=re.search(r'year\s+ended\s+\d{1,2}(?:st|nd|rd|th)?\s+[a-z]+,?\s+'+str(end),text)
        if match:return match[0]
    elif doc['kind']=='transcript':
        # First call heading, not every comparator quarter mentioned later in Q&A.
        match=re.search(r'Q[1-4]\s*FY\s*\d{2,4}',normal(opening),re.I)
        if match:return match[0].upper()
        match=re.search(r'(?:quarter|half.year)\s+ended\s+\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+,?\s+20\d{2}',normal(opening),re.I)
        if match:return match[0]
    return doc['discovery_period']+' (source label; accounting period unverified)'

async def ingest(company,doc,progress):
    started=time.monotonic(); path=DATA/(uuid.uuid4().hex+'.pdf'); proc=None
    try:
        async with asyncio.timeout(40):
            _,download=await fetch(doc['download_url'],40_000_000,path)
        with path.open('rb') as f:
            if f.read(5)!=b'%PDF-': raise SourceError('not_pdf','Source did not return a PDF.')
            f.seek(0); digest=hashlib.file_digest(f,'sha256').hexdigest()
        version=extraction_version(digest,kind=doc['kind'])
        with db() as c:
            old=c.execute('SELECT meta FROM documents WHERE hash=?',(version,)).fetchone()
        if old:
            saved=json.loads(old['meta'])
            if saved['symbol']!=company['symbol'] or saved['kind']!=doc['kind']:
                raise SourceError('issuer_mismatch','Cached source identity differs from the requested issuer or document type.')
            with db() as c:
                opening=' '.join(r['text'] for r in c.execute('SELECT text FROM chunks WHERE hash=? AND page<=12 ORDER BY page,id',(version,)))
                saved['period']=validate_identity(company,doc,opening)
                saved['management_speakers']=management_names(opening) if doc['kind']=='transcript' else []
                c.execute('UPDATE documents SET meta=? WHERE hash=?',(json.dumps(saved),version))
            put('latest-document-'+doc['download_url'],version)
            return saved
        meta={**company,**doc,**download,'original_url':doc['original_url'],'hash':digest,'version':version,'fetched_at':now(),'parser':PARSER,'publication_date':None}
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
                        eid=f'{version}-p{count}-c{index}'
                        c.execute('INSERT OR REPLACE INTO chunks VALUES (?,?,?,?)',(eid,version,count,text))
                        c.execute('INSERT INTO search VALUES (?,?,?)',(eid,version,text))
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
        meta['management_speakers']=management_names(' '.join(opening)) if doc['kind']=='transcript' else []
        meta.update(pages=count,characters=chars,processing_seconds=round(time.monotonic()-started,2),combined_peak_mb=round(peak/1024**2,1))
        with db() as c: c.execute('INSERT INTO documents VALUES (?,?,?,?)',(version,company['symbol'],doc['kind'],json.dumps(meta)))
        put('latest-document-'+doc['download_url'],version)
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
    groups=[]
    with db() as c:
        for doc in documents:
            version=doc.get('version',doc['hash'])
            results=[]
            transcript_prefix={}
            if doc['kind']=='transcript':
                all_rows=c.execute('SELECT id,page,text FROM chunks WHERE hash=? ORDER BY page,CAST(substr(id,instr(id,"-c")+2) AS INTEGER)',(version,)).fetchall()
                previous=''
                for r in all_rows:
                    matches=list(SPEAKER.finditer(previous))
                    transcript_prefix[r['id']]=matches[-1][1] if matches else ''
                    # Adjacent chunks overlap by 400 characters; scan only their distinct prefix.
                    previous=(previous+' '+r['text'][:1800])[-15000:]
            rows=c.execute('SELECT id,text FROM search WHERE search MATCH ? AND hash=? ORDER BY bm25(search) LIMIT 4',(query,version)).fetchall()
            if doc['kind']=='annual' and (re.search(r'what does .{1,50} do',question,re.I) or 'business' in words):
                first=re.findall(r'[a-zA-Z]+',doc.get('name',''))
                context=[]
                for context_query in (['"about '+first[0]+'"'] if first else [])+['"about the company"','"business overview"']:
                    context=c.execute('SELECT id,text FROM search WHERE search MATCH ? AND hash=? ORDER BY bm25(search) LIMIT 1',(context_query,version)).fetchall()
                    if context:break
                rows=(context+[r for r in rows if not context or r['id']!=context[0]['id']])[:4]
            if not rows:
                rows=c.execute('SELECT id,text FROM chunks WHERE hash=? ORDER BY page LIMIT 2',(version,)).fetchall()
            for r in rows:
                row=c.execute('SELECT page FROM chunks WHERE id=?',(r['id'],)).fetchone()
                results.append({**doc,'id':r['id'],'page':row['page'],'text':r['text'],'speaker_before':transcript_prefix.get(r['id'],'')})
            groups.append(results)
    # Interleave sources so a long annual-report passage cannot consume the entire budget.
    return [group[i] for i in range(4) for group in groups if i<len(group)]
