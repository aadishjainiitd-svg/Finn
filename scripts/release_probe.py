"""Hosted release checks with no model calls and no secrets recorded.

Usage: python scripts/release_probe.py [before-restart|after-restart]
Writes docs/hosted-release-verification.json (merged per phase). The probe's own
anonymous session token is kept only in data/ (ignored) so the after-restart phase
can confirm the same private pin survived; it is never written to docs.
"""
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
import httpx

BASE = 'https://finn-enam-yije.onrender.com'
HOST = BASE.split('://')[1]
OUT = Path('docs/hosted-release-verification.json')
PRIVATE = Path('data/release-probe-session.json')
phase = sys.argv[1] if len(sys.argv) > 1 else 'before-restart'
WRITE = {'X-Finn-Request': '1', 'Origin': BASE, 'Content-Type': 'application/json'}
report = json.loads(OUT.read_text(encoding='utf-8')) if OUT.exists() else {
    'kind': 'Hosted release verification; no model calls; probe-owned anonymous sessions only'}
checks = {}


def record(name, ok, detail=''):
    checks[name] = {'passed': bool(ok), 'detail': detail}
    print(('PASS ' if ok else 'FAIL ') + name + (' - ' + detail if detail else ''), flush=True)


with httpx.Client(base_url=BASE, timeout=120, follow_redirects=False) as alice:
    started = time.monotonic()
    health = alice.get('/health').json()
    record('health_revision', health.get('revision', '').startswith(sys.argv[2] if len(sys.argv) > 2 else ''), health.get('revision', ''))
    checks['cold_or_warm_health_seconds'] = round(time.monotonic() - started, 2)
    if phase == 'after-restart' and PRIVATE.exists():
        alice.cookies.set('finn_session', json.loads(PRIVATE.read_text())['token'], domain=HOST)
    session = alice.get('/api/session')
    cookie = session.headers.get('set-cookie', '')
    data = session.json()
    record('storage_persistent_postgres', data['storage']['mode'] == 'persistent_postgres', data['storage']['mode'])
    if phase == 'before-restart':
        record('session_cookie_secure_httponly', 'secure' in cookie.lower() and 'httponly' in cookie.lower())
        PRIVATE.write_text(json.dumps({'token': alice.cookies.get('finn_session')}), encoding='utf-8')
    today = alice.get('/api/today')
    body = today.json() if today.headers.get('content-type', '').startswith('application/json') else {}
    record('today_stored_snapshot', today.status_code == 200, f"status {today.status_code}; counts {body.get('counts')}; checked_at {body.get('checked_at')}")
    if phase == 'before-restart':
        pin = alice.post('/api/review', json={'action': 'pin', 'event_id': 'release-probe-event', 'value': True}, headers=WRITE)
        record('same_origin_write_behind_proxy', pin.status_code == 200, f'status {pin.status_code}')
        evil = alice.post('/api/review', json={'action': 'pin', 'event_id': 'x', 'value': True}, headers={**WRITE, 'Origin': 'https://evil.invalid'})
        record('cross_origin_write_rejected', evil.status_code == 403, f'status {evil.status_code}')
        bare = alice.post('/api/review', json={'action': 'pin', 'event_id': 'x', 'value': True}, headers={'Content-Type': 'application/json'})
        record('missing_app_header_rejected', bare.status_code == 403, f'status {bare.status_code}')
        with httpx.Client(base_url=BASE, timeout=120) as bob:
            pins = bob.get('/api/session').json()['review']['pins']
            record('second_session_isolated', 'release-probe-event' not in pins)
        ids = [e['id'] for ev in body.get('events', []) for e in ev.get('evidence', [])][:1]
        if ids:
            cite = alice.get('/api/evidence/' + ids[0])
            record('cited_evidence_resolves', cite.status_code == 200, f'status {cite.status_code}')
        else:
            checks['cited_evidence_resolves'] = {'passed': None, 'detail': 'No evidence id on visible Today events; not checked'}
    else:
        pins = data['review']['pins']
        record('private_pin_survived_restart', pins.get('release-probe-event') is True)

report[phase] = {'checked_at': datetime.now(timezone.utc).isoformat(), 'revision': health.get('revision'), 'checks': checks}
OUT.write_text(json.dumps(report, indent=2), encoding='utf-8')
