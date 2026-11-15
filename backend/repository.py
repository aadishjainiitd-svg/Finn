"""Authoritative state repository: Postgres in hosting, SQLite for local development.

No ORM or connection URL in logs. Caller-owned transactions make imports and
compare-and-swap mutations atomic on both backends. Public evidence is immutable.
"""
import json
import os
import sqlite3
import time
import threading
import logging
from contextlib import contextmanager
from .config import DATA
from .network import SourceError


class Conflict(Exception):
    pass


_pool=None
_pool_lock=threading.Lock()


class PoolLogFilter(logging.Filter):
    def filter(self,record):
        # Driver diagnostics can contain connection details. Keep only the
        # operational event class in logs; API errors are already sanitised.
        record.msg='Postgres connection pool recovery event';record.args=()
        record.exc_info=None;record.exc_text=None
        return True


def pool():
    global _pool
    from psycopg_pool import ConnectionPool
    from psycopg.rows import dict_row
    with _pool_lock:
        if _pool is None:
            logger=logging.getLogger('psycopg.pool')
            if not any(isinstance(f,PoolLogFilter) for f in logger.filters):logger.addFilter(PoolLogFilter())
            _pool=ConnectionPool(os.environ['FINN_DATABASE_URL'],kwargs={'sslmode':'require','connect_timeout':8,
                'row_factory':dict_row},min_size=0,max_size=4,max_waiting=16,timeout=8,max_idle=60,
                max_lifetime=300,reconnect_timeout=8,num_workers=1,name='finn-state',open=True)
        return _pool


def close():
    global _pool
    with _pool_lock:
        if _pool is not None:_pool.close();_pool=None


def configured():
    return bool(os.getenv('FINN_DATABASE_URL'))


class Transaction:
    def __init__(self, connection, postgres):
        self.connection, self.postgres = connection, postgres

    def execute(self, sql, values=()):
        return self.connection.execute(sql.replace('?', '%s') if self.postgres else sql, values)

    def executemany(self,sql,rows):
        with self.connection.cursor() if self.postgres else _sqlite_cursor(self.connection) as cursor:
            cursor.executemany(sql.replace('?', '%s') if self.postgres else sql,rows)

@contextmanager
def _sqlite_cursor(connection):
    cursor=connection.cursor()
    try:yield cursor
    finally:cursor.close()


@contextmanager
def transaction():
    postgres = configured()
    if postgres:
        # TLS is mandatory on hosted Postgres. Never downgrade to local storage
        # when configured durable storage is unavailable.
        try:
            current_pool=pool()
            connection=current_pool.getconn(timeout=8)
        except Exception:
            raise SourceError('storage_unavailable', 'Persistent storage is unavailable. Retry; no changes were saved.') from None
    else:
        connection = sqlite3.connect(DATA / 'state.sqlite', timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute('PRAGMA busy_timeout=10000')
        connection.execute('BEGIN IMMEDIATE')
    try:
        if postgres:
            # Neon pooler rejects libpq startup `options`. Transaction-local
            # settings also avoid leaking session configuration between clients.
            connection.execute('SET LOCAL statement_timeout = 10000')
        yield Transaction(connection, postgres)
        connection.commit()
    except Exception as exc:
        try:connection.rollback()
        except Exception:pass
        if postgres:
            import psycopg
            if isinstance(exc,psycopg.OperationalError):
                raise SourceError('storage_unavailable','Persistent storage could not confirm completion. Reload before retrying; saved evidence is unchanged.') from None
        raise
    finally:
        if postgres:current_pool.putconn(connection)
        else:connection.close()


def init():
    with transaction() as tx:
        tx.execute('''CREATE TABLE IF NOT EXISTS records (
            owner TEXT NOT NULL, bucket TEXT NOT NULL, id TEXT NOT NULL,
            value TEXT NOT NULL, version INTEGER NOT NULL, updated DOUBLE PRECISION NOT NULL,
            PRIMARY KEY(owner,bucket,id))''')
        tx.execute('''CREATE TABLE IF NOT EXISTS evidence_versions (
            version TEXT PRIMARY KEY, meta TEXT NOT NULL)''')
        tx.execute('''CREATE TABLE IF NOT EXISTS evidence_pages (
            id TEXT PRIMARY KEY, version TEXT NOT NULL, page INTEGER NOT NULL, text TEXT NOT NULL,
            FOREIGN KEY(version) REFERENCES evidence_versions(version))''')
        tx.execute('CREATE INDEX IF NOT EXISTS evidence_version_pages ON evidence_pages(version,page)')
        tx.execute('''CREATE TABLE IF NOT EXISTS work_jobs (
            id TEXT PRIMARY KEY, owner TEXT NOT NULL, kind TEXT NOT NULL, identity_key TEXT NOT NULL,
            payload TEXT NOT NULL, status TEXT NOT NULL, progress TEXT NOT NULL,
            created DOUBLE PRECISION NOT NULL, updated DOUBLE PRECISION NOT NULL,
            lease_until DOUBLE PRECISION NOT NULL DEFAULT 0, token TEXT, attempts INTEGER NOT NULL DEFAULT 0)''')
        tx.execute('CREATE INDEX IF NOT EXISTS jobs_ready ON work_jobs(status,created)')
        tx.execute('CREATE INDEX IF NOT EXISTS jobs_owner ON work_jobs(owner,identity_key)')
        tx.execute('CREATE TABLE IF NOT EXISTS worker_slots (id TEXT PRIMARY KEY,token TEXT,lease_until DOUBLE PRECISION NOT NULL)')
        tx.execute("INSERT INTO worker_slots VALUES ('global',NULL,0) ON CONFLICT(id) DO NOTHING")


def get(owner, bucket, key, tx=None):
    if tx is None:
        with transaction() as current:
            return get(owner,bucket,key,current)
    row=tx.execute('SELECT value,version,updated FROM records WHERE owner=? AND bucket=? AND id=?',
                   (owner,bucket,key)).fetchone()
    return {**json.loads(row['value']), '_version':row['version'], '_updated':row['updated']} if row else None


def save(owner,bucket,key,value,expected=None,tx=None):
    if tx is None:
        with transaction() as current:
            return save(owner,bucket,key,value,expected,current)
    encoded=json.dumps({k:v for k,v in value.items() if not k.startswith('_')},ensure_ascii=False)
    stamp=time.time()
    if expected is None:
        row=tx.execute('''INSERT INTO records(owner,bucket,id,value,version,updated) VALUES (?,?,?,?,1,?)
            ON CONFLICT(owner,bucket,id) DO UPDATE SET value=excluded.value,
            version=records.version+1,updated=excluded.updated RETURNING version''',
            (owner,bucket,key,encoded,stamp)).fetchone()
    elif expected==0:
        row=tx.execute('''INSERT INTO records(owner,bucket,id,value,version,updated) VALUES (?,?,?,?,1,?)
            ON CONFLICT(owner,bucket,id) DO NOTHING RETURNING version''',
            (owner,bucket,key,encoded,stamp)).fetchone()
    else:
        row=tx.execute('''UPDATE records SET value=?,version=version+1,updated=?
            WHERE owner=? AND bucket=? AND id=? AND version=? RETURNING version''',
            (encoded,stamp,owner,bucket,key,expected)).fetchone()
    if not row:raise Conflict('Another tab changed this record. Reload before saving.')
    return {**json.loads(encoded),'_version':row['version'],'_updated':stamp}


def listing(owner,bucket,limit=500):
    with transaction() as tx:
        rows=tx.execute('SELECT id,value,version,updated FROM records WHERE owner=? AND bucket=? ORDER BY updated DESC,id LIMIT ?',
                        (owner,bucket,limit)).fetchall()
    return [{'id':r['id'],**json.loads(r['value']),'_version':r['version'],'_updated':r['updated']} for r in rows]


def remove(owner,bucket,key,expected):
    with transaction() as tx:
        result=tx.execute('DELETE FROM records WHERE owner=? AND bucket=? AND id=? AND version=?',(owner,bucket,key,expected))
        if result.rowcount!=1:raise Conflict('Record changed or no longer exists.')


def retain_document(meta,chunks):
    """Commit a complete, verified extraction before releasing any citation.

    Same content/parser identity may never map to replacement text. Stream chunks
    from the local DB; no second full-document copy is kept in memory.
    """
    version=meta['version']
    with transaction() as tx:
        existing=tx.execute('SELECT meta FROM evidence_versions WHERE version=?',(version,)).fetchone()
        if existing:
            previous=json.loads(existing['meta'])
            if previous['hash']!=meta['hash'] or previous['symbol']!=meta['symbol']:
                raise ValueError('Immutable evidence identity conflict')
            return
        inserted=tx.execute('INSERT INTO evidence_versions(version,meta) VALUES (?,?) ON CONFLICT(version) DO NOTHING RETURNING version',(version,json.dumps(meta))).fetchone()
        if not inserted:return
        batch=[]
        for chunk in chunks:
            batch.append((chunk['id'],version,chunk['page'],chunk['text']))
            if len(batch)==128:
                tx.executemany('INSERT INTO evidence_pages(id,version,page,text) VALUES (?,?,?,?)',batch);batch=[]
        if batch:tx.executemany('INSERT INTO evidence_pages(id,version,page,text) VALUES (?,?,?,?)',batch)


def evidence(eid):
    with transaction() as tx:
        row=tx.execute('''SELECT p.id,p.page,p.text,v.meta FROM evidence_pages p
            JOIN evidence_versions v ON v.version=p.version WHERE p.id=?''',(eid,)).fetchone()
    return {**json.loads(row['meta']),'id':row['id'],'page':row['page'],'text':row['text']} if row else None


def document(version):
    with transaction() as tx:
        row=tx.execute('SELECT meta FROM evidence_versions WHERE version=?',(version,)).fetchone()
        if not row:return None
        pages=tx.execute('SELECT id,page,text FROM evidence_pages WHERE version=? ORDER BY page,id',(version,)).fetchall()
    return json.loads(row['meta']),pages
