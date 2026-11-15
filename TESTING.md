# FINN verification

Use Python 3.12 and Node 24.21.0. Install `requirements-dev.txt` in a virtual environment and run `npm ci --prefix frontend`.

```text
python -m pytest -q
cd frontend
npm test
npm run build
npx playwright install chromium
npm run test:e2e
```

Browser tests expect Vite at `http://127.0.0.1:5173` (`npm run dev`). They intercept source APIs with labelled, isolated fixtures; they never call an LLM. The Python tests use temporary SQLite stores and set `FINN_PREWARM=false`.

Live checks are deliberate: `python scripts/evaluate_live.py [base-url] [case-ids...]`, `python scripts/host_probe.py SYMBOL`, and `python scripts/restart_probe.py [SYMBOL]`. They consume free provider capacity or restart the owned service. Never bypass quota guards to make an evaluation green. Expectations are recorded in `docs/evaluation-cases.json`; raw local results remain ignored under `data/`. `python scripts/audit_recorded.py` verifies the captured evaluation's quote/hash/page membership without model calls; it requires the ignored raw capture directories and does not replace semantic review.

Credentials belong in ignored `.env` and `.env.deploy`. Tests, screenshots and exported build history must never contain their values. Frontend assets are served by FastAPI after the Vite build; development uses its API proxy.
