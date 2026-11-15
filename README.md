# FINN

A mobile investor brief and primary-source research workspace for the ENAM hiring assignment. FINN shows what changed across a portfolio's holdings, why it matters, and the exact source behind every claim.

**[Open FINN](https://finn-enam-yije.onrender.com)** (best at phone width; Render Free can take about a minute to wake) · [Submission note](docs/SUBMISSION.md) · [Release status and open items](docs/ACCOUNT_HANDOFF.md) · [Hosted verification](docs/hosted-release-verification.json)

Release status, 15 November 2026: revision `0be0c56` is live on Render Free with durable Neon Postgres storage. It is a **partial release** of the integrated plan (F01–F34): the features below are deployed and verified as stated, and the open items are listed at the end.

## What works

- **Today:** real NSE disclosures for an 18-company demonstration book, ranked into Needs you / Worth knowing / Buried with explainable scores. Unread or unassessed filings stay visible; the day is never called quiet when coverage is incomplete. Review, pin and undo persist per browser.
- **Event sheet:** timeline, cited evidence, quarterly results comparison (current vs comparator columns, signed QoQ/YoY, every number opens its PDF row), saved management guidance with its status, thesis effect and ranking reasons.
- **Research:** annual reports and earnings calls read from primary sources.
  - *Five-year trajectory:* revenue, growth, EBITDA proxy margin, profit, operating cash, capex and cash conversion. Each year comes from the newest report that prints it; restated values are marked with both rows cited; growth uses two years from one statement; unread years stay empty.
  - *Where the cash went:* capex, acquisitions, dividends, debt and lease repayment and the exact investing/financing remainder add up to operating cash, checked against reported opening and closing cash.
  - *Revenue mix:* segment and geography splits, accepted only when the rows add up to reported revenue from operations.
  - *Promises:* management guidance (EBITDA margin bands, revenue growth) tied to a fiscal year. Revenue growth is scored met/missed from statement numbers; margins are only indicative against FINN's EBITDA proxy; analyst questions, segment guidance and ambiguous ranges are never scored.
  - Report changes, flags, a balanced bull/bear view and scoped follow-up questions.
- **Book and Watch:** editable holdings with weights and theses; rule-based watches with a 30-session historical preview.

## How numbers are kept honest

Model output can only cite server-held passages. Numbers come from code with explicit scope, period, unit and currency checks: unlabelled statements are treated as standalone only when nothing on the page says otherwise; a broken rupee glyph is accepted only when the same document maps it ("prepared in Indian Rupee (H)"); tables that do not reconcile are dropped rather than repaired. Missing values are shown as missing, never zero.

## Running locally

Python 3.12 and Node 24. Install `requirements.txt` in a virtual environment, then `npm ci --prefix frontend` and `npm run build --prefix frontend`. Put provider keys in `.env` (see `.env.example`); never commit keys. Run `python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000`. Without `FINN_DATABASE_URL`, state uses local SQLite (development only).

Render: one **Free** Python web service, build `bash scripts/build.sh`, start `python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT`, health `/health`. Durable state is Neon Postgres (Free). Deployment credentials live only in ignored `.env.deploy`. Provider: **Groq** (`openai/gpt-oss-120b`), not xAI Grok. No paid model or hosting plan is enabled; Gemini fallback stays disabled.

## Limits and safeguards

One FastAPI process with leased background jobs (two global slots, one long job at a time), bounded PDF extraction, a durable shared daily model-quota ledger, and a rolling 24-hour share per browser (15 questions or research builds, 40 filing reads). Expired sessions are pruned hourly. Scheduled refresh is built but disabled. Telegram is disabled. Prices are end-of-day.

## Validation

169 Python tests, 11 frontend unit tests and 23 Playwright browser workflows pass. The hosted probe passes 9/9 on `0be0c56` (Postgres storage, secure cookies, stored Today digest, same-origin writes accepted and cross-site writes rejected, session isolation, cited evidence). See [hosted verification](docs/hosted-release-verification.json).

## Open items

Held-out accuracy evaluation; exact visual and gesture comparison with the reference design; more hand-checked quarterly tables and bank layouts; column-layout segment tables (e.g. ABB); hosted memory under multi-report research; scheduled refresh activation; retention policy for the shared snapshot and public evidence (review findings F9, F11, F14). Details in [release status](docs/ACCOUNT_HANDOFF.md).
