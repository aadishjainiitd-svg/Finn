"""Small real backend; extended only after source and hosting checks."""
import os
import platform
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from . import store,research
from .network import SourceError
from .sources import filings,price,ticker
from .llm import metrics

@asynccontextmanager
async def lifespan(app):
    store.init()
    yield

app = FastAPI(title='FINN', docs_url=None, redoc_url=None, lifespan=lifespan)
clients={}

@app.exception_handler(SourceError)
async def source_error(request,exc):
    status=429 if exc.code=='busy' else 422 if exc.code in ('invalid_ticker','unknown_ticker') else 503
    return JSONResponse(status_code=status,content={'error':{'code':exc.code,'message':exc.message}})

class ResearchRequest(BaseModel):
    symbol:str=Field(min_length=1,max_length=30)
    question:str=Field(min_length=10,max_length=600)

@app.post('/api/research',status_code=202)
async def start_research(body:ResearchRequest,request:Request):
    host=request.client.host if request.client else 'unknown'
    stamp=time.monotonic()
    for key in list(clients):
        if stamp-clients[key][0]>600: clients.pop(key)
    entries=[t for t in clients.get(host,[]) if stamp-t<60]
    if len(entries)>=5: raise SourceError('busy','Please wait a minute before starting another investigation.')
    clients[host]=entries+[stamp]
    return research.submit(body.symbol,body.question)

@app.get('/api/jobs/{job_id}')
async def job(job_id:str):
    if job_id not in research.jobs:
        return JSONResponse(status_code=410,content={'error':{'code':'job_expired','message':'This investigation was interrupted or expired. Please start it again.'}})
    return research.jobs[job_id]

@app.get('/api/evidence/{evidence_id}')
async def evidence(evidence_id:str):
    result=store.evidence(evidence_id)
    if result is None:
        return JSONResponse(status_code=410,content={'error':{'code':'version_unavailable','message':'This source version is no longer cached. Use the saved excerpt; the current URL may contain a newer version.'}})
    return result

@app.get('/api/source-check/{symbol}')
async def source_check(symbol:str):
    import asyncio
    symbol=ticker(symbol)
    results=await asyncio.gather(filings(),price(symbol),return_exceptions=True)
    out={}
    for name,res in zip(('filings','price'),results):
        out[name]={'status':'error','message':res.message if isinstance(res,SourceError) else 'Source unavailable'} if isinstance(res,Exception) else {
            'status':res['status'],'checked_at':res['checked_at'],
            'count':len([x for x in res['rows'] if x.get('symbol')==symbol]) if name=='filings' else len(res['chart'].get('timestamp',[]))}
    return out

@app.get('/api/capacity')
async def capacity():
    return metrics


@app.get('/health')
def health():
    return {'status': 'ok', 'service': 'finn', 'python': platform.python_version(),
            'revision': os.getenv('RENDER_GIT_COMMIT', 'local')[:12]}


@app.get('/')
def home():
    return {'product': 'FINN', 'stage': 'Feasibility gate in progress', 'health': '/health'}
