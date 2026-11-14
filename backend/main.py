"""Small real backend; extended only after source and hosting checks."""
import os
import platform
from fastapi import FastAPI

app = FastAPI(title='FINN', docs_url=None, redoc_url=None)


@app.get('/health')
def health():
    return {'status': 'ok', 'service': 'finn', 'python': platform.python_version(),
            'revision': os.getenv('RENDER_GIT_COMMIT', 'local')[:12]}


@app.get('/')
def home():
    return {'product': 'FINN', 'stage': 'Feasibility gate in progress', 'health': '/health'}
