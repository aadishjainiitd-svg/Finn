"""Bounded public HTTPS fetching. Source URLs are discovered, never supplied by users."""
import ipaddress
import socket
from urllib.parse import urlparse, urljoin
import httpx

HEADERS = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36',
           'Accept':'application/json,text/html,*/*','Referer':'https://www.nseindia.com/'}

class SourceError(Exception):
    def __init__(self, code, message):
        self.code, self.message = code, message
        super().__init__(message)

def validate_url(url):
    p = urlparse(url)
    if p.scheme != 'https' or not p.hostname or p.username or p.password or p.port not in (None,443):
        raise SourceError('unsafe_url','Only public HTTPS sources are allowed.')
    try:
        addresses = socket.getaddrinfo(p.hostname,443,type=socket.SOCK_STREAM)
    except OSError:
        raise SourceError('dns','Source host could not be resolved.') from None
    if not addresses or any(not ipaddress.ip_address(a[4][0]).is_global for a in addresses):
        raise SourceError('unsafe_url','Source address is not public.')

async def fetch(url, limit=6_000_000, path=None):
    original = url
    async with httpx.AsyncClient(headers=HEADERS,timeout=httpx.Timeout(35,connect=12),follow_redirects=False) as c:
        for _ in range(5):
            validate_url(url)
            try:
                async with c.stream('GET',url) as r:
                    if r.status_code in (301,302,303,307,308):
                        url=urljoin(url,r.headers.get('location','')); continue
                    if r.status_code != 200:
                        raise SourceError('http_'+str(r.status_code),'Source returned HTTP '+str(r.status_code)+'. Retry later.')
                    if int(r.headers.get('content-length','0') or 0)>limit:
                        raise SourceError('size_limit','Document exceeds the 40 MB processing limit.')
                    count=0; body=bytearray(); f=open(path,'wb') if path else None
                    try:
                        async for part in r.aiter_bytes():
                            count+=len(part)
                            if count>limit: raise SourceError('size_limit','Source exceeds the processing size limit.')
                            if f: f.write(part)
                            else: body.extend(part)
                    finally:
                        if f: f.close()
                    return bytes(body), {'original_url':original,'url':url,'bytes':count,'content_type':r.headers.get('content-type','')}
            except httpx.TimeoutException:
                raise SourceError('timeout','Source timed out. Retry later.') from None
            except httpx.HTTPError:
                raise SourceError('network','Source connection failed. Retry later.') from None
    raise SourceError('redirect_limit','Source redirected too many times.')

