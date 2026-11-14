# FINN

A mobile investor brief and primary-source research workspace for the ENAM hiring assignment. FINN helps an investor notice changes, inspect the evidence and avoid rereading reviewed disclosures.

**[Open FINN](https://finn-enam-yije.onrender.com)** · [AI build history](docs/AI_BUILD_HISTORY.md) · [Evidence audit](docs/EVIDENCE_AUDIT.md) · [Demo and submission draft](docs/SUBMISSION.md)

Release status: the product is deployed and the hosted feasibility gate passed. Final acceptance remains open: FINN's conservative Groq allowance currently blocks new synthesis, and the broad TCS demo is explicitly partial. Prepared answers, Brief and source evidence remain available. See the audit for exact outcomes; no blanket 12/12 pass is claimed.

## What works

- **Brief:** 15 fixed NSE holdings; separate filing/price coverage; company groups, explainable priority, pending assessments and accessible routine items. Every fetched filing is accounted for. Since review / Today / 7 days / 14 days, explicit Mark reviewed and Undo.
- **Research:** generic NSE-symbol identity, annual-report and transcript discovery, bounded PDF processing and page-cited answers. TCS, KPITTECH and ASTRAL examples are dated real-pipeline observations. HAVELLS passed live unseen-company research; CROMPTON passed post-implementation hosted document processing, with synthesis capacity still blocked.
- **Evidence:** exact excerpts, issuer, period, PDF page, original URL, retrieval time and source version. A missing server version after restart yields an explicit saved-excerpt notice; citations are never redirected to replacement text.
- **Numbers:** completed-session price/volume signals and constrained narrative unit conversion use Decimal. Incompatible periods, unknown accounting bases and unsupported questions produce limits or abstention.

The model selects passages; the server displays attributable source wording. This sacrifices some fluency to prevent unsupported paraphrases. Company context can be expanded separately from the focused answer.

## Backend

Python 3.12 and Node 24.21.0. Install `requirements.txt` in a virtual environment, then `npm ci --prefix frontend` and `npm run build --prefix frontend`. Put local provider keys in `.env` (see `.env.example`); never commit keys. Run `python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000`. Visit port 8000 for the production build. For development, run `npm run dev --prefix frontend`; Vite proxies the API to port 8000.

Render uses a **Free** native Python web service with one worker. Build: `bash scripts/build.sh`. Start: `python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT`. Health: `/health`.

Deployment credentials belong only in ignored `.env.deploy`, never in the app environment or frontend. Source PDFs and raw caches stay out of Git. Provider: **Groq**, not xAI Grok. No paid model or hosting plan is enabled.

## Architecture and deliberate limits

One FastAPI process serves React/Vite and serialises PDF ingestion into a bounded subprocess. SQLite FTS5 retrieves page-local chunks. No vector database, agent framework, Redis, Docling, LlamaIndex, Instructor, yfinance wrapper or GPL NSE wrapper is required. [Architecture](docs/FINN_ARCHITECTURE.md) · [Component review](docs/FINN_COMPONENT_REVIEW.md) · [Third-party notices](THIRD_PARTY_NOTICES.md).

Source classes: Yahoo daily bars; official NSE identity/disclosures; issuer/BSE/NSE reports and calls, discovered via Screener. Screener is an index, never research evidence. Public endpoint access is not a production market-data redistribution licence. Source availability is observed, not guaranteed.

Render Free sleeps and loses writable files on restart. The dated seed preserves a useful demonstration, while fresh source coverage refreshes separately. Review state and one saved answer live in this browser only. A real PDF link can change after capture; the recorded hash and excerpt retain the original identity.

Limits: 40 MB / 500 pages / 180 seconds per ingestion, 440 MB combined memory guard, one extraction plus one waiting investigation, one model flight per minute and conservative daily admission. PDFs requiring OCR, arbitrary URLs, BSE-only identities and broad financial-table calculations are unsupported. New research can take tens of seconds after service wake and admission wait; prepared-answer latency is not a cold-start claim.

No accounts, portfolio editing, native notifications, live quotes, commitment tracking or challenge/debate feature. Gemini fallback stays disabled until its account limits are verified; no paid usage is enabled.

## Validation and next steps

See [TESTING.md](TESTING.md) for executable checks, [QA review](docs/QA_REVIEW.md), [hosted feasibility measurements](docs/FEASIBILITY_RESULTS.md), and [research audit](docs/EVIDENCE_AUDIT.md). Tests distinguish live requests from controlled failure fixtures and cached replays.

Next: resolve free synthesis capacity, improve the TCS question's retrieval coverage, then durable budget/cache storage and investor feedback on ranking. Deferred product features remain deferred. [Implementation log](docs/IMPLEMENTATION_LOG.md) and [resumable checkpoint](docs/RESUME.md) record exact remaining work.
