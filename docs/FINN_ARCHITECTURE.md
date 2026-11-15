# FINN — architecture, acceptance and build sequence

> Current implementation status (15 November 2026): approved scope is implemented and deployed on Render Free. Production Groq 120B, hosted CROMPTON research, restart provenance and final mobile workflows are verified. The earlier HAVELLS partial answer is resolved and verified on the deployed app; see the HAVELLS repair record in the audit. See [final audit](EVIDENCE_AUDIT.md), [implemented architecture](../ARCHITECTURE.md), [QA results](QA_REVIEW.md) and [checkpoint](RESUME.md). Historical planning-only statements below are retained as the decision record, not current authorisation. No deferred feature was added.

14 November 2026 · Proposed implementation of the agreed scope. No application code, dependency resolution, hosted deployment or model inference has been performed. Existing assets are PDFs and planning/source-validation documents; there is no Git repository yet.

## Architecture

One Render Free Linux service runs FastAPI and serves the compiled React/Vite application; hosting was selected by the user on 14 November. Node is build-time only; Python 3.12 is the runtime. Keep plain CSS and shared tokens; reuse only the audited shadcn Sheet structure, adapting its styles/imports and retaining its MIT notice and Radix accessibility behavior. No full UI monorepo, agent framework, vector service or Redis.

```text
Phone: Brief / Research / shared evidence sheet
   | same-origin API                 | localStorage: reviewed event revisions
FastAPI: validation, limits, jobs, response contracts
   |-- Yahoo daily bars -----------> deterministic EOD signals
   |-- NSE disclosures ------------> exact dedup + source-backed priority
   |-- ticker identity + discovery -> issuer/exchange annual report + transcript
   |                                    |
   |                         bounded PDF extraction subprocess (one at a time)
   |                                    |
   +-- SQLite: documents, pages/chunks + FTS5, events, jobs, answer cache
                                         |
                          retrieved pages -> Groq -> schema/citation checks
                                               \-> Gemini on eligible failure
                                         |
                              cited answer or explicit evidence gap
```

### Contracts and identity

Proposed routes: `GET /api/brief?window=…`, `POST /api/research` with ticker/question, `GET /api/jobs/{id}`, and `GET /api/evidence/{id}`. Cache hits return immediately; uncached research returns 202 and a job ID. Responses carry `status`, source coverage, publication/session dates and retrieval time. Progress stages are discovery, extraction and answering; a spinner is not the only feedback.

Normalise ticker case, whitespace and recognised exchange suffixes; validate against an exchange identity record, not a three-company map. Keep exchange, symbol, legal name and ISIN where available. Resolve the company before selecting documents. Ambiguous names require a choice; unknown symbols produce a specific error. BSE-only identifiers remain unsupported in this NSE-focused prototype. Screener is a discovery index, never research evidence; verify issuer/period against the PDF and primary host. User input cannot supply arbitrary download URLs.

Identity lookup is itself an unverified integration: choose and test the exchange identity source in T1. A failed/blocked lookup means identity unavailable, not invalid ticker. Discovery tries the consolidated company page, then standalone; select primary links by document type and actual period, not page position or filename alone. A recording/presentation is not a transcript. If sources conflict about issuer or period, quarantine that document and show the mismatch. Test a fresh ticker chosen after implementation, a standalone-only path, a missing transcript and a mismatched issuer. No company-specific URL map in the normal path. IR fallback is used only when discoverable from verified company identity; arbitrary-web search is not added.

### Grounding and provenance

Store original/resolved URL, issuer and ticker, document type, reporting period, publication date when known, fetch time in UTC, SHA-256, parser version, PDF page number and chunk ID. Printed page labels may be shown separately. Chunk within page boundaries; citations open the matching excerpt and original document/page. A URL alone is insufficient provenance. Changed bytes create a new version; prior citations never silently point to replacement text.

Pull answers use issuer/exchange documents only. FTS5 plus explicit query synonyms retrieves bounded passages; annual report and transcript are both searched when the question requires both. Filing context from Brief is separately included and cited when needed. No news, broker research, browser tools or model-memory company facts. Document instructions are untrusted content.

The answer schema contains claims, evidence IDs and evidence gaps. Validate it with Pydantic and reject unknown evidence IDs. Schema correctness does not prove factual support: human evaluation checks that pages entail the claims. Low-quality extraction or insufficient evidence yields a partial answer or abstention, never an uncited completion.

Each claim references an exact supporting excerpt from a supplied, versioned page chunk; verify excerpt membership after whitespace normalisation. Retain negation, qualifications and speaker attribution. Mark conditional interpretation separately from reported fact; a management forecast remains management's forecast. Citation/excerpt checks cannot prove semantic entailment, so the 12-case human audit remains mandatory. Never assert a change or fulfilled promise without both comparable observations; when only the latest transcript exists, answer its stated outlook and explain that change cannot be established. Default prompts must not promise a comparison the loaded documents cannot support.

### Filing priority and accounting (review correction C1)

Priority is a deterministic, explainable ordering, not a model-generated importance score. Review first: substantive results, control/M&A changes, senior-management departures, auditor concerns, defaults, adverse regulatory orders, rating downgrades and significant funding/capital commitments when supported by the document. Other substantive disclosures and EOD threshold signals follow. An override is a reason to inspect, not a stock-price prediction.

Only a small allowlist of positively identified routine subtypes (for example, a newspaper publication confirmation with no substantive additional disclosure) may collapse after adequate text assessment. Generic categories such as results, management_change, press_release or unclassified never authorise suppression. Failed extraction, ambiguous content, auditor changes and unread attachments stay visible as Assessment pending. A keyword match can raise priority; absence of keywords cannot prove routine status. Keep every fetched filing reachable and reconcile fetched = distinct displayed + exact duplicates, with routine and pending counts visible. Do not cap the list at a hidden top-N.

Within each tier, order companies by their highest-ranked event and then publication time; retain every distinct event within the company. Display the rule/reason. A short filing summary is generated only after source text is available; title-only items retain their exchange title and a verification-pending label.

### Numerical rules

- Calculate outside the LLM. Daily change is `100 × (C[t]/C[previous] − 1)` using completed provider sessions and the same price basis. Do not use an unfinished daily bar or assume every weekday trades. Show the actual last session, not “today” by default.
- Volume multiple is `V[t] / mean(previous 20 valid completed-session volumes)`, excluding the current session. Missing/zero baseline or insufficient history yields unavailable. Fixed 5% absolute change and 2× volume are review heuristics, not causal explanations.
- Preserve provider Close semantics; do not mix dividend-adjusted and unadjusted series. Flag corporate actions and suppress comparisons whose basis is uncertain, including volume windows crossing splits.
- For a requested financial calculation, retain each operand's cited page, period, currency, unit and consolidated/standalone basis. Use Decimal, normalise units before calculating, and round only for display. Do not compare incompatible periods/bases; zero or negative growth bases require explicit handling. If extraction cannot establish these fields, decline the calculation. A general table-extraction/quarterly-comparison engine is out of scope.

An operand is a tuple: metric definition, reported value, unit/currency, period start/end, quarter/year-to-date/full-year, accounting scope and exact source excerpt. Header and row context must identify the same column; a number merely occurring on the page is insufficient. Derivations show the formula and operands. Prefer clear narrative figures for the two numerical evaluation cases; ambiguous PDF tables cause abstention, not guessed column alignment.

### Caching, limits and recovery

Cache filings for 10 minutes, prices for 60 minutes and discovery for 24 hours; manual refresh respects the same upstream throttle. These are initial tunable values. Store successful results separately from errors and show last-success time on stale data. Hash documents for reuse. Answer keys include normalised question, company, selected chunk hashes, retrieval version, prompt/schema version and provider/model. Coalesce identical in-flight jobs; do not prewarm all 15 annual reports.

Initial bounds: one extraction job at a time, streamed download capped at 40 MB, at most 500 PDF pages, 180-second ingestion ceiling and roughly 4,000 evidence tokens per answer. These limits cover the sampled document sizes, not every company. Use a subprocess so extraction can be terminated; bound queued work and return busy/retry guidance. Record failed/interrupted jobs on restart. No external worker service.

Render Free has **512 MB RAM and 0.1 CPU**, per its [compute documentation](https://render.com/docs/compute-plans). Compressed bytes/page count do not bound parser memory. One API process launches at most one extraction subprocess, with one waiting ingestion job; additional requests get Busy. Stream to temporary disk and persist extracted pages incrementally. T1 must measure combined peak memory and set an enforceable child memory limit that leaves the API headroom. Kill/reap on timeout/limit; clean temporary files on failure. If a source-available fresh ticker cannot fit these bounds, the hosted gate fails; a polite error is not a substitute for working generic research.

Limit outbound requests, validate public HTTPS destinations and redirects, reject private/reserved addresses, enforce PDF content checks, and keep provider keys server-side. Add a shared LLM concurrency/budget guard plus client rate limits. At most two model attempts total per question: Groq first, Gemini only for eligible transient/quota failure and only after its own smoke test. Respect Retry-After. No fallback for missing evidence, bad credentials or invalid citations; return a useful failure state. Disable SDK retries if application retrying.

Admission reserves total estimated prompt + evidence + output tokens, not just request count. Groq currently lists 8K TPM for the selected model, with exact account limits potentially different ([official limits](https://console.groq.com/docs/rate-limits)). Two 4K-evidence calls plus overhead can exceed that. Keep one synthesis in flight, use response limit/reset headers and a shared budget, and show Waiting for answer capacity when deferred. Prioritisation/refresh does not automatically summarise every filing; extractive titles/excerpts and deterministic reasons work without a model. Prepared answers and summaries are generated through the normal pipeline and cached. Never reset known quota accounting merely because a new visitor arrives; after server restart re-establish capacity conservatively. Secrets and potentially sensitive questions never enter logs.

Free hosting caches are disposable. Bundle only a small, dated, permitted demo seed and keep review state in the browser. Never turn a seed into apparent live coverage. Show source excerpts/links if synthesis fails. A successful empty filing response, blocked request and unknown coverage are separate states. BSE's locally observed 403 is not a functioning backup.

Evidence IDs use document hash + PDF page + chunk, not database row number. Retain the current answer's cited excerpts and provenance in the same browser (bounded storage), so server eviction cannot relabel an old citation. If a source version cannot be recovered, show the saved excerpt/date and Version unavailable; never resolve it to new bytes. This promises traceability of what was shown, not permanent hosting of every original PDF. Browser storage loss is explicit. Use stable exchange-event identity and separate source revisions so a seed/live refresh neither duplicates events nor resets acknowledgement. Store per-company fetch coverage; one success cannot advance every company's baseline.

Deploy through Render's native Python runtime, which [also includes Node/npm](https://render.com/docs/native-runtimes). Pin Python and compatible frontend versions, print/assert them during build, build Vite assets once and serve them from FastAPI. Bind the assigned PORT on 0.0.0.0; one API worker, bounded SQLite transactions, no in-process task duplication. Health must not depend on upstream services. No Docker unless the native build actually fails; that fallback would need its own time decision. Render's wake page precedes FINN loading UI, so a FINN spinner cannot mask a sleeping service. Log request ID, source, stage, elapsed time, bytes/pages, cache outcome and error class. Roll back to the previous known-good deploy/seed if a release breaks; verify health, Brief and one research query afterwards.

## Acceptance and evaluation

All rows below are **planned, not yet run**.

| Check | Pass condition |
|---|---|
| Hosted source gate | On the chosen host, all three source classes are usable; a fresh source-available NSE ticker completes discovery → PDF extraction → cited answer without company-specific URLs |
| Portfolio | 15 holdings; price and filing coverage shown separately; stale sessions and failed companies explicit |
| Review behavior | Open/refresh does not mark reviewed; Mark reviewed persists across reload; Undo restores; source revision resurfaces; exact duplicates do not multiply |
| Priority | Human audit of material, routine and unparsed filings; no material test item hidden as routine; each priority has a defensible reason |
| Grounding | Three prepared companies plus a held-out ticker; correct issuer/period; annual-report and transcript evidence exercised together in at least one question |
| Research gold set | 12 questions: 6 supported (including cross-document and contrary-evidence cases), 2 unanswerable, 2 numerical and 2 identity/missing-source cases. Expected pages/operands recorded before grading. Every material claim supported; no fabricated citations; correct abstention |
| Arithmetic | Deterministic fixtures cover current-bar exclusion, previous-20 baseline, missing/zero values, corporate action, unit and period mismatch; exact expected results before display rounding |
| Faults | Inject 403, 429, timeout, malformed PDF/output, unknown citation, empty extraction and worker interruption; no invented success or endless loading |
| Cache/provenance | Cache hit avoids another model call; changed source/prompt invalidates; old citations remain traceable; source timestamp never replaced by processing time |
| Mobile | 390px viewport, no horizontal overflow; keyboard/focus/Escape and return focus work for evidence sheet; empty, partial, busy and stale states readable |
| Deployment | Cold restart restores dated seed, reports lost jobs/cache honestly, accepts new ticker; no client secrets; public URL/repo/history links usable |

Strengthen existing checks: labelled filing set includes actual results versus publication notice, auditor concern, downgrade, management change, generic/unclassified title, unreadable attachment and exact duplicate; no material fixture may collapse. Assert both race orders for ticker A/B responses and review/revision arrival. Numerical cases include year-to-date versus quarter and crore/lakh mismatches. Change the bytes behind one URL, then restart: old evidence must not point to the replacement document. Fault fixtures are not proof of live source access; the hosted fresh-ticker and cold-restart checks remain separate.

```text
unit fixtures: identity / numbers / dedup / cache keys
        ↓
integration fixtures: source responses / PDFs / model contracts / failures
        ↓
hosted vertical test: fresh ticker + three sources + both model smoke tests
        ↓
manual acceptance: 12-question evidence audit + phone workflow + restart
```

Timing targets after service wake: cached Brief ≤2 seconds, cached answer ≤2 seconds, admitted warm synthesis ≤20 seconds, new-ticker ingestion ≤180 seconds. Record queue wait, service wake, ingestion and inference separately; never advertise the 20-second target as total time when admission is delayed. These are unmeasured targets. The 180-second extraction ceiling is a protective limit, not proof that sampled documents will finish within it.

## Implementation Tasks

One sequential implementation lane. Estimates are the combined user-plus-Codex focused budget; agent speedups are not assumed. Proposed file areas below do not yet exist.

| Work elapsed | Task and review finding addressed | Exit evidence |
|---|---|---|
| 0:00–0:20 | **T1a / P1:** repository, health shell, pinned native build and credential smoke checks | Build versions and provider access recorded; no secrets in repo |
| 0:20–1:30 | **T1b / P1:** highest-risk hosted vertical test (`backend/sources`, `research`) | Fresh ticker, both document types, supported answer, measured memory/time; price and NSE probes. Stop UI work if blocked |
| 1:30–2:30 | **T2 / P1:** portfolio adapters, priority accounting, provenance, arithmetic (`backend/domain`, `storage`, `tests`) | 15 holdings; labelled priority and numeric fixtures |
| 2:30–3:45 | **T3 / P1:** retrieval, evidence contracts, admission, cache/restart behavior (`backend/research`, `tests`) | Three demos prewarmed; missing-source, quota and version cases |
| 3:45–5:15 | **T4 / P1:** two screens, evidence and stable review/request state (`frontend/src`) | Phone loop; identity races and coverage states |
| 5:15–6:30 | **T5 / P1:** 12-case evidence audit, fresh ticker, faults, cold restart and phone checks | Recorded results; no fabricated citations or concealed failures |
| 6:30–7:15 | **T6 / P1:** README, notices, source coverage, AI history, demo and covering-email draft | Public links and run instructions checked; seed/live distinction clear |
| 7:15–8:00 | Contingency only | Fix failed gates; no additional features |

This revises the optimistic six-hour core to a **7¼-hour core plus 45-minute reserve**, conditional on T1 success. If only six focused hours remain or T1 exceeds 90 minutes, stop and ask for a scope/time decision; do not quietly drop unseen tickers, a source class, grounding or submission evidence. All tasks remain proposed until final plan approval; no application work is authorised by this document.

## GSTACK REVIEW REPORT

Scope preserved: two workflows, one deployed service. Architecture review: hosted fresh-ticker feasibility and ephemeral state remain unproven. Code-quality review: use small adapters and explicit contracts; no existing application code to inspect. Test review: coverage above is specified but unexecuted. Performance review: PDF memory, cold-start latency and free-tier quotas require measurement. Remedies are recommendations recorded in T1–T6, not implemented fixes.

Independent outside review: unavailable. Claude Code was not installed; the skill's required native Plan/background-task fallback is unavailable in this host. No independent-review or clean-pass claim. No application tests have run.

Review record: this Markdown contains the review findings. The gstack registry write failed with a filesystem permission error, including when directed to a project-local state path; no successful registry entry is claimed. This does not prevent using the planning documents and does not clear implementation gates.

User decision resolved: Render Free, accepting documented sleep and disposable-cache constraints. Technical gates remain: Render account access, deployed source access, full-document extraction, authenticated models and resolved package compatibility. Approval status: **final approval of the revised plan pending; implementation deliberately paused at the user's request**. The latest sequential findings and decision ledger are in [FINN_PLAN_REVIEW.md](FINN_PLAN_REVIEW.md).
