# FINN: locked scope and build plan

Decision date: 14 November 2026, IST.
Recruiter deadline: 15 November 2026, EOD IST (confirmed by the user).
Target submission: 15 November, 21:00 IST. Available focused work: 6-8 hours.

Planning refinement (14 November): [focused PRD](PRD-FINN.md), [architecture and acceptance](FINN_ARCHITECTURE.md), [fork/component audit](FINN_COMPONENT_REVIEW.md), and [pre-mortem](PreMortem-FINN-2026-11-14.md). The subsequent [CEO → design → engineering review](FINN_PLAN_REVIEW.md) preserves scope and revises the estimate to 7¼ hours plus 45 minutes reserve. The user selected Render Free. Final plan approval is pending; implementation has not started.

Experience refinement: see [FINN_EXPERIENCE_PROPOSAL.md](FINN_EXPERIENCE_PROPOSAL.md) for the proposed review-state semantics, screens, feature ranking and demo. It keeps the two-workflow scope and does not constitute visual-design approval.

## Product promise

An investor reaches for it throughout the day because it saves time and shows only what matters.

Two connected workflows:

1. **Since your last review:** a mobile portfolio inbox with prioritised exchange filings, short explanations of relevance, expandable routine items, source links, publication and retrieval timestamps, explicit reviewed/unreviewed state, and EOD price/volume signals. Opening the app does not mark items reviewed. First use defaults to 24 hours; subsequent checks surface new events and unfinished review. Today, 7-day and 14-day views support broader review. An empty window stays empty; never quietly substitute historical events.
2. **Investigate this company:** open from a filing or enter an NSE ticker; get a short business snapshot and ask a focused question grounded in annual reports and earnings-call transcripts. Every material answer claim carries a document/page reference. Missing evidence is stated explicitly.

Push means an automatically populated inbox, refreshed on opening and periodically while active. This prototype does not promise background phone notifications or real-time market prices.

## Company set

Portfolio: RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK, LT, BHARTIARTL, ITC, SUNPHARMA, MARUTI, TITAN, ULTRACEMCO, KPITTECH, APLAPOLLO, CERA.

Research demos: TCS, KPITTECH, ASTRAL. Astral is outside the portfolio. CROMPTON was used for a separate discovery/download smoke check; final acceptance must also try another ticker not used during implementation.

These are mock holdings selected for the assignment, not investment recommendations. Research discovery and processing must take a ticker as input; no company-specific answers or hard-coded document URLs in the normal path.

## Recommended stack

| Layer | Choice | Reason |
|---|---|---|
| Mobile UI | React + TypeScript + Vite; plain CSS with shared design tokens | Two screens with fast iteration and few dependencies |
| API and ingestion | Python 3.12 + FastAPI + httpx + Pydantic | Strong PDF tooling; bounded HTTP requests; validated output contracts |
| PDF extraction | pypdf with fontTools; pdfplumber only if needed | Page-level provenance; observed font warnings justify the extra dependency |
| HTML discovery | Beautiful Soup | Read Screener's document links and company identity; do not use its derived financial tables as research evidence |
| Storage/retrieval | SQLite + FTS5, standard-library sqlite3; content-hashed document cache | Simple lexical retrieval with page metadata; no vector service setup |
| LLM | Groq `openai/gpt-oss-120b` primary; Gemini `gemini-3.5-flash-lite` fallback | Both providers offered by the user; compact grounded requests, structured output and cached results; account access and answer quality still require a smoke test |
| Hosting | One Render Free service serving both API and compiled UI; selected by the user | One origin and deployment; disclose cold starts and disposable server storage |

FastAPI can serve Vite's compiled static assets. No separate frontend server is needed in production. No agent framework, vector database, authentication, or multi-service queue in this scope.

### Model policy

Use a small common synthesis interface with at most two provider adapters. Groq's GPT-OSS 120B supports strict JSON-schema output; Gemini 3.5 Flash-Lite is listed with free-tier input/output. These are candidate defaults, not a claim that either account has been authenticated or its quota verified. Confirm model access and active quotas before use. Do not automatically enable paid billing.

Start with Groq for grounded research answers and selected material-filing summaries. Use Gemini on a transient provider failure or exhausted quota, subject to its own limit; respect retry guidance and do not rotate keys to evade limits. Keep the retrieved evidence and output schema the same. Do not call both providers for every answer. Treat insufficient evidence as a valid result, not a reason to ask another model to invent an answer.

Simple price/volume calculations, deduplication and routine category rules require no LLM. Keep requests small (initial target: approximately 4,000 evidence tokens, with a quota-aware lower cap if needed), validate evidence IDs, and cache by provider/model as well as source hash. Use application-level caching; do not depend on paid provider context caching. Disable web-search grounding and built-in browsing for pull analysis. Two smoke-test questions per provider should check a supported answer and an unsupported claim before enabling fallback.

Render free services sleep after 15 minutes and lose filesystem changes on restart; those properties are incompatible with assuming durable SQLite or continuous monitoring. If using that tier, seed a dated real-data snapshot at build time, treat server caches as disposable, store read state in browser localStorage, and show refresh status. An already-available always-on service is preferable for the review experience. Do not purchase hosting without user authorisation.

## Data flow and controls

- Prices: server-side Yahoo daily chart endpoint, isolated behind a small adapter. Request approximately three months. Compute daily close change and volume versus the preceding 20 completed sessions; exclude the current bar from the baseline. Initial fixed thresholds: absolute price change of 5%, volume of 2x baseline. Label these heuristics, not explanations of causality. Show each ticker's actual latest session date.
- Filings: NSE per-symbol, date-bounded queries. Validate symbol and time range locally, deduplicate by exchange ID/document identity, and retain every fetched item. Download material filings for evidence before producing detail beyond the exchange title. Routine suppression is reversible and relevance uses content as well as category. Do not rely on exchange-generated summaries as a substitute for the filing.
- Fundamentals: Screener consolidated page, then standalone page if appropriate; discover annual-report and transcript URLs by document type and reporting period. Fetch issuer/exchange documents, verify PDF content, and store page text and source identity. A missing transcript means incomplete coverage, not permission to substitute a presentation or outside knowledge.
- Retrieval: split within page boundaries; FTS5 ranking plus a small, explicit query synonym map. Retrieve evidence from both report and transcript where the question requires both. Cap context and answer length. Return an insufficient-evidence response when retrieval is weak.
- Cache keys include document hashes, question, prompt version and model. Deduplicate in-flight requests. Only prewarm the three research demos; do not preprocess annual reports for all 15 holdings.
- Use size/time limits, bounded fetch concurrency, public HTTP(S) URLs only, and secret-free client code. Treat fetched document text as evidence, never instructions.
- Return loading, unavailable, stale and partial-data states. Preserve original source dates even when processing happens today.

## Build sequence: revised after sequential review

| Elapsed work | Deliverable and exit condition |
|---|---|
| 0:00-0:20 | Repository, health shell, runtime/version and model-credential checks. |
| 0:20-1:30 | Highest-risk deployed fresh-ticker path: primary report + transcript, full extraction/retrieval and supported answer; price/NSE access, resource/quota measurements. |
| 1:30-2:30 | 15-company portfolio adapters, priority accounting, provenance and deterministic arithmetic. |
| 2:30-3:45 | Research/evidence, token admission, caching, version/restart and failure behavior. |
| 3:45-5:15 | Two mobile screens, shared evidence sheet and stable review/request state. |
| 5:15-6:30 | Twelve-case evidence audit, relevance fixtures, unseen ticker, faults, cold restart and phone checks. |
| 6:30-7:15 | README/notices, source limits, public links, AI history, demo and covering-email draft. |
| 7:15-8:00 | Contingency for failed gates. No extra features. |

Local source-access validation is recorded separately. The revised estimate assumes usable accounts and a passing first gate; it is not a delivery guarantee. A hard six-hour limit or a blocked first gate requires a new scope/time decision, not silently weaker grounding, reduced generalisation or omitted sources. Deployment in this sequence is future work after approval, not an action performed during planning.

## Acceptance checks

- All 15 price fetches have explicit success/stale/error states; stale CERA data must not be labelled current.
- Filing window and ticker filters work; routine items remain accessible and deduplication prevents repeated cards.
- Sample priorities are manually checked against the actual filing, including a management-change item and routine paperwork.
- Sample calculations use the previous completed sessions, handle missing data, and do not infer an event caused a price move.
- Three research demos cite actual supporting pages; at least one question exercises annual-report and transcript evidence together.
- A newly chosen ticker uses the same discovery/retrieval pipeline. Missing source coverage is an honest partial result, not a fabricated answer.
- No unsupported claims in a small hand-checked answer set; document citations resolve to their stated pages.
- A narrow phone viewport has no horizontal overflow; loading/failure states work; research remains reachable from the inbox.
- Reviewer can open the deployed link and repository, and access the supplied AI build history.

## Explicitly deferred

Native app and notifications; voice; user accounts; portfolio editing; biography enrichment; configurable thresholds; all-eight-section research reports; full quarterly-results comparisons; four-quarter guidance tracking; OCR for scanned-only documents; broad semantic retrieval infrastructure.

## Submission

To: assessment@enam.com
Subject: IIT Delhi – AI Engineer - 2027

Provide prototype URL, GitHub repository, coding-agent/LLM history exports or share links, and a concise covering email describing implemented behaviour, decisions, trade-offs, omissions and next steps. No email has been sent.

## Technical references checked

- https://vite.dev/guide/
- https://fastapi.tiangolo.com/tutorial/static-files/
- https://pypdf.readthedocs.io/en/stable/user/extract-text.html
- https://render.com/docs/free
- https://console.groq.com/docs/models
- https://console.groq.com/docs/structured-outputs
- https://console.groq.com/docs/rate-limits
- https://aistudio.google.com/docs/models/gemini-3.5-flash-lite
- https://aistudio.google.com/docs/pricing
- https://aistudio.google.com/docs/rate-limits

No application code or dependency installation was performed during planning/source validation.
