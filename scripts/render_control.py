"""Operate only FINN's explicitly Free Render service. Never emit env values."""
import json
import os
import sys
from pathlib import Path
import httpx
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / '.env')
load_dotenv(ROOT / '.env.deploy')
STATE = ROOT / 'data/render-service.json'
BASE = 'https://api.render.com/v1'
action = sys.argv[1]
secrets = [v for k, v in os.environ.items() if v and (k.endswith('API_KEY') or k in ('FINN_DATABASE_URL', 'FINN_SCHEDULER_TOKEN'))]


def clean(text):
    for value in secrets:
        text = text.replace(value, '[REDACTED]')
    return text


with httpx.Client(headers={'Authorization': 'Bearer ' + os.environ['RENDER_API_KEY']}, timeout=40) as client:
    if action == 'create':
        if STATE.exists():
            raise SystemExit('Service state already exists; refusing duplicate creation.')
        owners = client.get(BASE + '/owners').json()
        if len(owners) != 1:
            raise SystemExit('Workspace selection required; no service created.')
        owner = owners[0]['owner']['id']
        payload = {
            'type': 'web_service', 'name': 'finn-enam', 'ownerId': owner,
            'repo': 'https://github.com/aadishjainiitd-svg/Finn', 'branch': 'main',
            'autoDeployTrigger': 'off',
            'envVars': [{'key': k, 'value': v} for k, v in {
                'PYTHON_VERSION': '3.12.14', 'GROQ_API_KEY': os.environ['GROQ_API_KEY'],
                'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY', ''),
                'FINN_LLM_PROVIDER': 'groq', 'FINN_LLM_MODEL': 'openai/gpt-oss-120b',
                'FINN_GEMINI_MODEL': 'gemini-3.5-flash-lite', 'FINN_GEMINI_FALLBACK': 'false',
            }.items()],
            'serviceDetails': {'runtime': 'python', 'plan': 'free', 'region': 'singapore',
                'numInstances': 1, 'healthCheckPath': '/health',
                'envSpecificDetails': {'buildCommand': 'pip install -r requirements.txt',
                    'startCommand': 'python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT'}},
        }
        assert payload['serviceDetails']['plan'] == 'free'
        response = client.post(BASE + '/services', json=payload)
        if response.status_code != 201:
            print(json.dumps({'status': response.status_code, 'error': clean(response.text)[:800]}))
            raise SystemExit(1)
        result = response.json()
        service = result.get('service', result)
        saved = {'id': service['id'], 'owner': owner, 'url': service.get('serviceDetails', {}).get('url'),
                 'plan': service.get('serviceDetails', {}).get('plan'), 'deployId': result.get('deployId')}
        STATE.write_text(json.dumps(saved, indent=2), encoding='utf-8')
        print(json.dumps(saved))
    else:
        state = json.loads(STATE.read_text())
        sid = state['id']
        service = client.get(BASE + '/services/' + sid).json()
        if service.get('serviceDetails', {}).get('plan') != 'free':
            raise SystemExit('Free-plan invariant failed; refusing operation.')
        if action == 'status':
            deploys = client.get(BASE + '/services/' + sid + '/deploys?limit=3').json()
            print(json.dumps({'service': sid, 'url': service['serviceDetails'].get('url'), 'plan': 'free',
                              'deploys': deploys}, indent=2))
        elif action == 'configure':
            response=client.patch(BASE+'/services/'+sid,json={'serviceDetails':{'envSpecificDetails':{'buildCommand':'bash scripts/build.sh'}}})
            print(json.dumps({'status':response.status_code,'operation':'configure FINN build','plan':'free'}))
            response.raise_for_status()
        elif action == 'deploy':
            response = client.post(BASE + '/services/' + sid + '/deploys', json={'clearCache': 'do_not_clear'})
            print(clean(json.dumps({'status': response.status_code, 'result': response.json()})))
        elif action == 'set-database':
            # Copies the locally verified Neon URL to the existing Free service.
            # The value is sent only to Render's API and is never printed.
            value = os.environ['FINN_DATABASE_URL']
            response = client.put(BASE + '/services/' + sid + '/env-vars/FINN_DATABASE_URL', json={'value': value})
            print(json.dumps({'status': response.status_code, 'operation': 'set FINN_DATABASE_URL', 'plan': 'free'}))
            response.raise_for_status()
        elif action == 'restart':
            response = client.post(BASE + '/services/' + sid + '/restart')
            print(json.dumps({'status': response.status_code, 'operation': 'restart'}))
        elif action == 'logs':
            response=client.get(BASE+'/logs',params={'ownerId':state['owner'],'resource':sid,'limit':40,'type':'app'})
            if response.status_code!=200:print('Log status',response.status_code)
            else:
                data=response.json()
                rows=data.get('logs',[]) if isinstance(data,dict) else data
                for row in rows:
                    message=row.get('message',row.get('text',''))
                    print(clean(str(message))[:1000])
        else:
            raise SystemExit('Unknown operation')
