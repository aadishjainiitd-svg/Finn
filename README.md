# FINN

A mobile investor brief and primary-source research workspace for the ENAM hiring assignment.

Implementation is in progress. The live feasibility gate passed on Render Free. Full workflow evaluation and QA are in progress.

## Backend

Python 3.12. Install `requirements.txt` in a virtual environment. Put local provider keys in `.env` (see `.env.example`); never commit keys. Run `python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000`.

Render uses a **Free** native Python web service with one worker. Build: `bash scripts/build.sh`. Start: `python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT`. Health: `/health`.

Deployment credentials belong only in ignored `.env.deploy`, never in the app environment or frontend. Source PDFs and raw caches stay out of Git. Provider: **Groq**, not xAI Grok. No paid model or hosting plan is enabled.

See `docs/IMPLEMENTATION_LOG.md` for current evidence and resumable checkpoints.
