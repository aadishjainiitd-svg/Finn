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
    with db() as c:
        row = c.execute('SELECT value,fetched FROM cache WHERE key=?',(key,)).fetchone()
    if row and (ttl is None or time.time()-row['fetched'] < ttl):
        return json.loads(row['value'])
    return None

def put(key,value):
    with db() as c:
        c.execute('INSERT OR REPLACE INTO cache VALUES (?,?,?)',(key,json.dumps(value),time.time()))

def evidence(eid):
    with db() as c:
        row = c.execute('SELECT c.*,d.meta FROM chunks c JOIN documents d ON c.hash=d.hash WHERE c.id=?',(eid,)).fetchone()
    if not row:
        return None
    return {**json.loads(row['meta']), 'id':row['id'],'page':row['page'],'text':row['text']}

