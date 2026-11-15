"""Disposable cache; content-addressed evidence never aliases a replacement."""
import json
import sqlite3
import time
from contextlib import contextmanager
from .config import DATA

@contextmanager
def db():
    c = sqlite3.connect(DATA / 'finn.sqlite', timeout=10)
    c.row_factory = sqlite3.Row
    try:
        yield c
        c.commit()
    finally:
        c.close()

def init():
    with db() as c:
        c.executescript('''
        PRAGMA journal_mode=WAL;
        CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, value TEXT, fetched REAL);
        CREATE TABLE IF NOT EXISTS documents (hash TEXT PRIMARY KEY, symbol TEXT, kind TEXT, meta TEXT);
        CREATE TABLE IF NOT EXISTS chunks (id TEXT PRIMARY KEY, hash TEXT, page INTEGER, text TEXT);
        CREATE VIRTUAL TABLE IF NOT EXISTS search USING fts5(id UNINDEXED, hash UNINDEXED, text, tokenize='porter unicode61');
        ''')

def cached(key, ttl=None):
    from . import repository
    if repository.configured() and durable_key(key):
        retained=repository.get('_public','source_cache',key)
        if retained:
            if ttl is not None and time.time()-retained['fetched']>=ttl:return None
            return retained['value']
    with db() as c:
        row = c.execute('SELECT value,fetched FROM cache WHERE key=?',(key,)).fetchone()
    if row and (ttl is None or time.time()-row['fetched'] < ttl):
        return json.loads(row['value'])
    return None

def put(key,value):
    from . import repository
    stamp=time.time()
    if repository.configured() and durable_key(key):
        repository.save('_public','source_cache',key,{'value':value,'fetched':stamp})
    with db() as c:
        c.execute('INSERT OR REPLACE INTO cache VALUES (?,?,?)',(key,json.dumps(value),stamp))


def durable_key(key):
    # Explicit public-data allowlist. Questions, answers and owner state must
    # never enter a shared cache, even if their keys happen to contain a ticker.
    return key in ('brief-snapshot','filings','nse-equity-identity') or key.startswith(
        ('price-','latest-document-','assessed-','discovery-'))


def rehydrate(version):
    """Rebuild disposable page search from immutable retained extraction."""
    from . import repository
    with db() as c:
        if c.execute('SELECT 1 FROM documents WHERE hash=?',(version,)).fetchone():return True
    if not repository.configured():return False
    retained=repository.document(version)
    if not retained:return False
    meta,pages=retained
    with db() as c:
        c.execute('INSERT OR IGNORE INTO documents VALUES (?,?,?,?)',
            (version,meta['symbol'],meta['kind'],json.dumps(meta)))
        c.execute('DELETE FROM search WHERE hash=?',(version,))
        c.executemany('INSERT OR REPLACE INTO chunks VALUES (?,?,?,?)',
            ((p['id'],version,p['page'],p['text']) for p in pages))
        c.executemany('INSERT INTO search(id,hash,text) VALUES (?,?,?)',
            ((p['id'],version,p['text']) for p in pages))
    return True

def evidence(eid):
    with db() as c:
        row = c.execute('SELECT c.*,d.meta FROM chunks c JOIN documents d ON c.hash=d.hash WHERE c.id=?',(eid,)).fetchone()
    if not row:
        from . import repository
        return repository.evidence(eid) if repository.configured() else None
    return {**json.loads(row['meta']), 'id':row['id'],'page':row['page'],'text':row['text']}

def retain(version):
    """Persist complete public evidence before returning it to any caller."""
    from . import repository
    if not repository.configured():return
    with db() as c:
        row=c.execute('SELECT meta FROM documents WHERE hash=?',(version,)).fetchone()
        if not row:raise ValueError('Incomplete evidence cannot be retained')
        repository.retain_document(json.loads(row['meta']),
            c.execute('SELECT id,page,text FROM chunks WHERE hash=? ORDER BY page,id',(version,)))

