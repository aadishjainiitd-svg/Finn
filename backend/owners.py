"""Anonymous browser ownership. No shared private book or client-selected owner."""
import hashlib
import secrets
import time
from urllib.parse import urlsplit
from fastapi import Request, Response, HTTPException
from . import repository

COOKIE='finn_session'


def owner(request:Request,response:Response):
    token=request.cookies.get(COOKIE,'')
    key=hashlib.sha256(token.encode()).hexdigest() if 32<=len(token)<=128 else ''
    session=repository.get('_system','sessions',key) if key else None
    if session and session['expires']>time.time():return session['owner']
    token=secrets.token_urlsafe(32);key=hashlib.sha256(token.encode()).hexdigest()
    identity=secrets.token_hex(24)
    repository.save('_system','sessions',key,{'owner':identity,'expires':time.time()+365*86400})
    response.set_cookie(COOKIE,token,max_age=365*86400,httponly=True,secure=https(request),
                        samesite='lax',path='/')
    return identity


def https(request:Request):
    # Render terminates TLS and forwards plain HTTP. A forwarded https marker can
    # only make the cookie stricter, so trusting it here is safe.
    forwarded=request.headers.get('x-forwarded-proto','').split(',')[0].strip().lower()
    return request.url.scheme=='https' or forwarded=='https'


def mutation(request:Request):
    # Custom header disallows cross-site form submissions. No permissive CORS.
    if request.headers.get('x-finn-request')!='1':raise HTTPException(403,'Same-origin app request required.')
    origin=request.headers.get('origin')
    # Compare host only: behind a TLS proxy the app sees http while the page is https.
    if origin and urlsplit(origin).netloc.lower()!=request.headers.get('host','').lower():
        raise HTTPException(403,'Cross-origin changes are not allowed.')
