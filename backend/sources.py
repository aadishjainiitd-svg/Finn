import csv
import io
import json
import re
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
from .network import fetch, SourceError
from .store import cached, put

def now():
    return datetime.now(timezone.utc).isoformat()

def ticker(value):
    value=value.strip().upper()
    value=re.sub(r'^(NSE:)', '', value)
    value=re.sub(r'\.NS$', '',value)
    if not re.fullmatch(r'[A-Z0-9&-]{1,25}',value):
        raise SourceError('invalid_ticker','Enter an NSE symbol, for example HAVELLS. Company-name search is not supported.')
    return value

async def identity(symbol):
    records=cached('nse-equity-identity',86400)
    if records is None:
        body,_=await fetch('https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv')
        records=[{k.strip():v.strip() for k,v in r.items()} for r in csv.DictReader(io.StringIO(body.decode('utf-8-sig')))]
        if not records or 'SYMBOL' not in records[0]:
            raise SourceError('identity_unavailable','Exchange identity response is not readable.')
        put('nse-equity-identity',records)
    match=next((r for r in records if r['SYMBOL']==symbol),None)
    if not match: raise SourceError('unknown_ticker','This symbol is not in the NSE equity list. Check the symbol; BSE-only securities are unsupported.')
    return {'symbol':symbol,'name':match['NAME OF COMPANY'],'isin':match['ISIN NUMBER'],'exchange':'NSE'}

def primary_pdf(url):
    # BSE's viewer is an HTML wrapper. Its Pname identifies the same exchange PDF.
    if urlparse(url).hostname in ('www.bseindia.com','bseindia.com') and 'AnnPdfOpen.aspx' in url:
        name=parse_qs(urlparse(url).query).get('Pname',[''])[0]
        if re.fullmatch(r'[a-fA-F0-9-]+\.pdf',name):
            return 'https://www.bseindia.com/xml-data/corpfiling/AttachHis/'+name
    return url

def parse_discovery(html, company):
    soup=BeautifulSoup(html,'html.parser')
    # Verify the discovery index identifies the exchange symbol as well.
    links=[a.get('href','') for a in soup.select('a[href]')]
    if not any(('symbol='+company['symbol']) in u or ('/'+company['symbol']+'/') in u for u in links):
        heading=soup.select_one('h1')
        significant=re.sub(r'\b(limited|ltd|india)\b','',company['name'].lower()).strip().split()
        if not heading or not significant or significant[0] not in heading.get_text().lower():
            raise SourceError('identity_mismatch','Discovery page does not match the exchange issuer.')
    issuer_hosts=set()
    for a in soup.select('.company-links a[href]'):
        h=urlparse(a['href']).hostname
        if h and not any(x in h for x in ('nseindia','bseindia','screener')): issuer_hosts.add(h.removeprefix('www.'))
    docs=[]
    for kind, selector in [('annual','.annual-reports a[href]'),('transcript','.concalls a[href]')]:
        candidates=[]
        for a in soup.select(selector):
            label=a.get_text(' ',strip=True)
            if kind=='annual' and not re.search(r'Annual Report \d{4}',label): continue
            if kind=='transcript' and label.lower()!='transcript': continue
            original=a['href']; url=primary_pdf(original); host=(urlparse(url).hostname or '').removeprefix('www.')
            allowed=host in ('bseindia.com','nsearchives.nseindia.com','archives.nseindia.com') or any(host==h or host.endswith('.'+h) for h in issuer_hosts)
            if not allowed or '.zip' in url.lower(): continue
            period=label if kind=='annual' else a.parent.get_text(' ',strip=True).split('Transcript')[0].strip()
            candidates.append({'kind':kind,'title':label if kind=='annual' else 'Earnings call transcript',
                'discovery_period':period,'download_url':url,'original_url':original})
        if candidates: docs.append(candidates[0])
    return docs

async def discover(company):
    key='discovery-v1-'+company['symbol']; hit=cached(key,86400)
    if hit: return hit
    last=None
    for suffix in ('/consolidated/','/'):
        try:
            body,_=await fetch('https://www.screener.in/company/'+company['symbol']+suffix)
            docs=parse_discovery(body,company)
            if docs:
                put(key,docs); return docs
        except SourceError as e: last=e
    raise last or SourceError('no_documents','No primary annual report or transcript was discovered.')

async def filings():
    hit=cached('filings',600)
    if hit: return hit
    today=datetime.now(timezone(timedelta(hours=5,minutes=30)))
    url='https://www.nseindia.com/api/corporate-announcements?index=equities&from_date='+ (today-timedelta(days=14)).strftime('%d-%m-%Y')+'&to_date='+today.strftime('%d-%m-%Y')
    body,_=await fetch(url,limit=15_000_000)
    try: rows=json.loads(body)
    except ValueError: raise SourceError('malformed','Exchange filing response was not JSON.') from None
    if not isinstance(rows,list): raise SourceError('malformed','Exchange filing response was not a list.')
    result={'rows':rows,'checked_at':now(),'status':'live'}; put('filings',result); return result

async def price(symbol):
    key='price-'+symbol; hit=cached(key,3600)
    if hit: return hit
    body,_=await fetch('https://query1.finance.yahoo.com/v8/finance/chart/'+symbol+'.NS?range=3mo&interval=1d&events=splits')
    try: chart=json.loads(body)['chart']['result'][0]
    except (ValueError,KeyError,IndexError,TypeError): raise SourceError('malformed','Daily price response is incomplete.') from None
    result={'chart':chart,'checked_at':now(),'status':'live'}; put(key,result); return result

