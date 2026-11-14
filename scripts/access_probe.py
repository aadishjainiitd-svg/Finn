"""Live, read-only account discovery plus a minimal model smoke request.

Secrets are loaded locally and never emitted. Do not log HTTP request objects.
"""
import json
import os
import sys
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / '.env')
load_dotenv(ROOT / '.env.deploy')
sys.stdout.reconfigure(encoding='utf-8')
SECRETS = [os.getenv(k, '') for k in ('GROQ_API_KEY', 'GEMINI_API_KEY', 'RENDER_API_KEY')]


def clean(value):
    text = str(value)
    for secret in SECRETS:
        if secret:
            text = text.replace(secret, '[REDACTED]')
    return text


def probe(client, name, method, url, **kwargs):
    started = time.monotonic()
    try:
        response = client.request(method, url, **kwargs)
        result = {'probe': name, 'status': response.status_code,
                  'seconds': round(time.monotonic() - started, 3),
                  'limits': {k: v for k, v in response.headers.items()
                             if k.startswith('x-ratelimit') or k == 'retry-after'}}
        payload = response.json()
        if response.status_code >= 400:
            result['error'] = clean(json.dumps(payload))[:500]
        elif name == 'render_owners':
            result['owners'] = [{k: row.get('owner', row).get(k) for k in ('id', 'name', 'type')}
                                for row in payload]
        elif name == 'render_services':
            result['services'] = [{k: row.get('service', row).get(k) for k in ('id', 'name', 'type')}
                                  for row in payload]
        elif name == 'groq_models':
            result['models'] = [m['id'] for m in payload.get('data', []) if 'gpt-oss' in m['id']]
        elif name == 'gemini_models':
            result['models'] = [m['name'] for m in payload.get('models', []) if 'flash' in m['name']]
        else:
            result['usage'] = payload.get('usage')
            result['reply'] = payload.get('choices', [{}])[0].get('message', {}).get('content')
        return result
    except Exception as exc:
        return {'probe': name, 'error_class': type(exc).__name__, 'seconds': round(time.monotonic()-started, 3)}


with httpx.Client(timeout=25, follow_redirects=False) as client:
    groq = {'Authorization': 'Bearer ' + os.getenv('GROQ_API_KEY', '')}
    render = {'Authorization': 'Bearer ' + os.getenv('RENDER_API_KEY', '')}
    results = [
        probe(client, 'render_owners', 'GET', 'https://api.render.com/v1/owners', headers=render),
        probe(client, 'render_services', 'GET', 'https://api.render.com/v1/services?limit=20', headers=render),
        probe(client, 'groq_models', 'GET', 'https://api.groq.com/openai/v1/models', headers=groq),
        probe(client, 'gemini_models', 'GET', 'https://generativelanguage.googleapis.com/v1beta/models',
              headers={'x-goog-api-key': os.getenv('GEMINI_API_KEY', '')}),
        probe(client, 'groq_smoke', 'POST', 'https://api.groq.com/openai/v1/chat/completions', headers=groq,
              json={'model': 'openai/gpt-oss-120b', 'messages': [{'role': 'user', 'content': 'Reply with OK.'}],
                    'max_completion_tokens': 128, 'reasoning_effort': 'low', 'temperature': 0}),
    ]
report = {'evidence_type': 'live_local_network', 'checked_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
          'results': results, 'billing_changed': False}
(ROOT / 'data').mkdir(exist_ok=True)
(ROOT / 'data/access-probe.json').write_text(clean(json.dumps(report, indent=2)), encoding='utf-8')
print(clean(json.dumps(report, indent=2)))
