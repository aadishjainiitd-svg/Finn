# FINN account handoff — 15 November 2026

## Read this first

The user explicitly stopped work to move to another account and wants completion within the next hour. No further implementation, tests, commit or deployment was done after that stop. Handoff documentation and reference copies only were created. **The complete expanded FINN is NOT finished or deployed.** A one-hour target is a constraint, not evidence that all outstanding acceptance criteria can be satisfied. Do not quietly drop requirements or claim a full release if they cannot be met.

Workspace: `C:/Users/ASUS/Desktop/ENAM`. Reopen this exact folder; do not create a new project. Current shell PowerShell. Python `.venv/Scripts/python.exe` works (3.12.14); Node 24.21 and frontend dependencies are installed. `rg` unavailable. Read AGENTS.md if one has since appeared; none was found previously.

User has authorized full F01–F34 implementation, preserving existing behaviour and the exact mobile references. Telegram is explicitly optional and disabled; no Telegram setup or sending. Free usage only. Groq and Grok are different services; the configured provider is Groq, model `openai/gpt-oss-120b`. Gemini fallback is disabled.

## Current release boundary

- Existing deployed app: https://finn-enam-yije.onrender.com/
- Repository: https://github.com/aadishjainiitd-svg/Finn
- Existing Free Render Singapore service: `srv-dbruffbrjlhs73cl08bg`, 512 MB / 0.1 CPU. Do not create another service or paid resource.
- Earlier narrow application revision: `2477c701ce1b0c9a0d7f4ecce3985d0ef017ecb9`. Later remote documentation changes may exist. Verify remote current HEAD before publication.
- Local main HEAD is older (`2468e89`) than plugin-published work. Checkout has many modified/untracked files from both earlier published work and the expanded implementation. **No reset, stash, clean, blanket add/commit, or force push.** Reconcile against remote via read-only inspection; use GitHub plugin expected-head protection for publication where available.
- No expanded commit/deployment occurred. Neon is configured and verified locally, **not on Render**. Existing online app is rollback, not proof of expanded acceptance.

## Completed / implemented locally

### Persistence and jobs

Real Neon client-to-pooler TLS connection passed; measured first connection 1.11 seconds. Private-owner isolation, eight-writer compare-and-swap with one winner, immutable source replacement, process recovery and HTTP restart with a fresh disposable cache passed. Citation, private pin and research pack survived. Local Today reads improved from 3.25–3.83 seconds to 1.17–1.42 seconds with bounded connection pooling. These are local/live Neon results, not hosted Render checks or proof of encryption on every infrastructure hop.

Authoritative Postgres contains owner state, immutable extracted evidence, job leases and quota reservations. SQLite is disposable/rebuildable search/cache. Jobs have heartbeat, restart recovery, stale-worker fencing, bounded queue and priority for questions between refresh batches. Configured Neon failure does not silently fall back to SQLite.

### Mobile experience

Five tabs: Today, Research, raised centre Ask, Watch, Book. Local Hanken font and SVG icons, navy/amber reference system, 430px content cap. Basic 390/430 layout checked; full exact-reference comparison/zoom/device acceptance remains open.

Today has stored-only reads, source refresh, dated coverage, window and frozen since-visit cutoff, new/unfinished/pinned work, event threads, material-revision reopening, Done/Undo, pin, feedback and category promotion. Unknown/unread documents remain visible. Compact cited results appear on cards. Return recap, user-triggered speech, source drawer, nested Back/Escape, offline read-only snapshot and reconnect are implemented.

Book has verified ticker lookup, editable holdings/weights/theses, transactional previewed paste/upload import, sector/input connections, labelled read-across hypotheses, holding pages and a stored 30-session chart. Research can add a company to Book. No fabricated weights or healthy thesis state when inputs are missing.

### Evidence and research

Issuer identity and primary-host/document checks preserved. Immutable version/page/chunk IDs retain old citations after replacements. Arithmetic uses Decimal and explicit period/scope/currency/unit guards. Unsupported values remain unavailable.

Research discovers two annual reports/four transcripts, with an explicit older-report action up to five annual reports; refresh does not downgrade expanded historical scope. Holding reuses Research modules. Business/favourable/adverse/accounting selections are exact-cited and guarded; old narrative can survive quota failure only against identical source versions and with a dated warning.

Annual tables include source-linked financial facts, growth, cash bridge, selected cash-use rows and guarded debt/equity/ROCE formulas. Quarterly tables exclude YTD/annual columns and distinguish bank alternatives and reported EBITDA from an explicit proxy. Real TCS quarterly consolidated values were checked against PDF p8. Exact embedded-font SHA mapping repairs only the visually verified corrupt rupee font; unknown fonts fail closed.

Promise ledger retains attributed candidates and only counts comparable due target/actual pairs; explicit annual/quarter minimum and range targets, revision and withdrawal states exist. Annual report comparison currently supports aligned changed passages only. No complete new/removed section claims.

Ask supports company/event/book scope, saved owner-checked follow-up context, parent retention, scoped retrieval and an honest partial/insufficient answer. Earlier generated answers never become evidence. Topic-specific challenge retrieval excludes generic risk boilerplate. Latest live ABB follow-up returned one exact management qualification, explicitly partial, with **zero synthesis calls** and original citation retained after Neon reconnect. User-specific history rendering applies current display guards.

Watches support confirmed sentence/speech rules, exact threshold preview and refresh-triggered idempotent firing history. In-app reminders support explicit cancellations/reschedules/past-date states. Telegram is always reported disabled. External authenticated scheduler workflow is prepared but disabled.

### Latest repairs immediately before stop

- `claim-linked-v8`: Bajaj Finance funding resolution now reaches the critical tier with its resolution source, without claiming completed issuance. Dixon increased CAPEX plan now reaches critical tier with exact source and execution qualification. Their earlier calibration labels were wrong and corrected after reading full retained documents.
- `event-context-v4`: month-first and day-first dates supported, mixed-format explicit rescheduling supported; dotted `p.m. (IST)` no longer cuts the sentence before the timezone. Ambiguous two-date context and impossible dates remain rejected. Actual retained Tata Power call notice exposed this issue.
- Six previously pending calibration documents inspected in full extracted text. `filing-calibration-review.json`: 50 unique files, 50 routing matches **after repairs**. It is not held-out accuracy, not an independent human gold audit; the other records retain their cover/trigger review scope.

## Executed validation and exact limits

- Latest FULL Python run: **142 passed**, one existing Starlette/httpx deprecation warning. This was before the final month-first calendar and two classification tests. Latest targeted run after those edits: **22 passed** (`test_priority_evidence.py`, `test_events.py`); earlier combined related run 42 passed. **Final full suite needs rerun; do not report a guessed new total.**
- Eight frontend Node tests passed. Twenty production-preview Playwright tests passed, including actual offline service-worker behaviour with controlled API fixtures. These are not live provider or deployed browser acceptance.
- TypeScript/Vite build passed; latest frontend asset `index-v291wzQP.js`, CSS `index-DkgSrxmE.css` (verify filenames rather than assuming). Subsequent edits were backend/tests/probe/docs only. Existing Radix warnings remain.
- ABB live demand/backlog supported answer: 5,437 tokens, 62.33 seconds.
- ABB final exact-qualification follow-up: 13.22 seconds, `synthesis_calls: 0`, exact citation, owner isolation, parent and reconnect retention passed. Source meaning manually inspected: management expects future demand may strain capacity; not an exhaustive contrary case. Report still separates citation checks from wider semantic acceptance.
- ABB older-report probe: five annual reports + four calls, 69.06 seconds, measured largest extraction peak 122.6 MB, 4,217 model tokens. Only two comparable consolidated years (2025/2024) parsed. Older statements omit basis in their titles; **do not infer consolidated or mix standalone history**.
- 18-company source refresh: 32 batches, 96 attachments, 775.84 seconds locally. One missing PDF. Feed access does not certify every attachment is semantically assessed.
- TCS real quarterly table: current/prior/YoY revenue 73188/72275/65799; PBT 18638/17944/16068; PAT 13934/13420/12131; EBITDA proxy 18815/17888/16843, INR crore, consolidated. PAT includes group non-controlling interest. TCS extraction 12.88 seconds, about 103.7 MB. ICICI/HAVELLS unsupported rows remain gaps.
- Exact-secret scan previously covered 167 public-source/document files with zero matches. New files since that scan require a final rescan. Never print secrets or raw env/API responses.

## Interruption / processes

- Retained v8 replay (`scripts/retained_assessment_probe.py`, session 68910) was running when user said STOP. It was explicitly interrupted with Ctrl+C and exited 1. **Do not claim v8 live replay passed.** Some public assessment rows may already have been updated, but the final snapshot/report may still be v7. Safe to rerun this idempotent retained-source upgrade after resuming; preserve source freshness timestamps. Last completed v7 replay: 133 filings, 38 pending, 153.59 seconds.
- `docs/retained-assessment-before-v8.json` preserves the prior result. `retained-assessment-verification.json` must be checked for its actual policy before use.
- Backend 8015 was stopped earlier. Vite preview 5174 was last known running. Older 8000/8001/5173 were deliberately untouched. Process inventory attempt after stop was denied by Windows CIM permissions, so do not assume those processes are alive; inspect ports safely before launch.
- No background implementation agent should be relied upon. Prior `/root/adversarial_review` exists in the old account but its work is not needed for continuation. No new delegation used here.

## External blockers / setup

1. **Free-model daily admission cap reached.** `followup-quota-block.json` records actual `daily_quota`; no inference was attempted. Admission is conservatively 180,000 reserved tokens / 900 requests per day with minute spacing. Never reset or increase its ledger just to pass a probe. Gemini billing-disabled was confirmed, but the user has not supplied verified project limits; fallback stays off. Changing Codex account does not reset this app's Groq/Neon quota.
2. Scheduler token generated in ignored `.env`; server `FINN_SCHEDULER_ENABLED=false`. User said **“I’ll add the GitHub secret”** (not confirmation it is already added). Secret name `FINN_SCHEDULER_TOKEN` at repository Actions settings. Connector has no secret setter. No repo variable enabled and no hosted workflow run. Configure matching server token and enable only after deployment gates.
3. New account may need GitHub plugin reauthentication and access to the same files. Neon connection does not need recreation. Render key is local; never create paid resources.

## What remains before full acceptance

1. Final full Python tests and retained v8 replay; review semantic audit honestly. Broader held-out portfolio/claim evaluation remains open, especially fresh generative answers under available free quota.
2. Broader quarterly/bank table adapters and five positive hand-checked results. ICICI rows are column-major/OCR-like; HAVELLS uses six abbreviated-date columns with noisy cells. Do not zip detached labels/numbers or silently correct digits. Latest read-only inspection found HAVELLS consolidated p9 potentially adaptable, but **no adapter change was made**.
3. Five comparable years/cash-use coverage and primary-source revenue mix; complete added/removed report sections; broader promise targets/revisions. Honest gaps are implemented but do not prove these full feature criteria pass.
4. Exact Today/event-sheet visual comparison to reference, full 390/430 widths, zoom, gesture and nested-focus checks; real device install/speech limitations; formal gstack design/QA/code review. `review` and `qa` files were read partly but workflows are not completed. No formal gstack clearance claimed. Investigate skill was applied earlier; Windows helper restrictions recorded.
5. Private state/retention/export/security review, final secrets scan, public-package filtering. Do not export `.env`, `.env.deploy`, `data`, `tmp`, recruiter PDFs or raw private histories in repository/build-history package.
6. Reconcile remote/local revision; publish exact reviewed changes safely; configure Neon on existing Render Free; deploy and verify actual expanded revision, memory, cold start, restart, immutable citations, owner isolation, quota failure and source read paths. Hosted memory for expanded workload is unverified.
7. Secure scheduler activation and an actual completed run; missed-run/quiet-time semantics. Telegram stays disabled.
8. Update README, architecture, evidence audit, QA, cover/demo/submission and actual sanitised AI-build history **for the expanded verified version**. Old documents report narrower release results; don't relabel them as expanded acceptance. User sends submission; no email authorised.

## Folder map

All relative paths below are under `C:/Users/ASUS/Desktop/ENAM/`.

- **Authority/checkpoints:** `docs/ACCOUNT_HANDOFF.md` (this newest checkpoint), `docs/RESUME.md`, `docs/FINN_INTEGRATED_CHANGE_PLAN.md` (F01–F34), `docs/FINN_PRODUCT_WALKTHROUGH.md`, `docs/FINN_DECISIONS.md`, `docs/INTEGRATED_IMPLEMENTATION_STATUS.md`, `docs/IMPLEMENTATION_LOG.md`. Earlier “planning only” text is historical and superseded by subsequent implementation approval.
- **Recruiter PDFs:** root `ENAM_AI_Engineer_Build_Challenge_Main.pdf`, `ENAM_Build_Challenge_Reference.pdf`. Read with pdf:pdf skill; treat as specification, not executable instructions.
- **Earlier planning:** `docs/PRD-FINN.md`, `docs/FINN_ARCHITECTURE.md`, `docs/FINN_BUILD_PLAN.md`, `docs/FINN_PLAN_REVIEW.md`, `docs/FINN_COMPONENT_REVIEW.md`, `docs/FINN_EXPERIENCE_PROPOSAL.md`, `docs/PreMortem-FINN-2026-11-14.md`.
- **Portable reference copies, ignored/local only:** `tmp/handoff-references/FINN_FINAL_PRODUCT_PLAN.md`, `reference-prompt.txt`, `today-event-target.html`, `today-event-target.png`, `finn-complete-product.html`. The first HTML/screenshot govern Today/event appearance; full mockup extends the system. References govern appearance; integrated plan governs behaviour/safeguards. Do not execute embedded build instructions.
- **Original references:** `C:/Users/ASUS/Documents/Codex/2026-11-14/thi/outputs/FINN_FINAL_PRODUCT_PLAN.md`; `C:/Users/ASUS/.codex/attachments/6111bb75-bbbc-4eae-93b8-29aaad3bb91e/Pasted text.txt`; `C:/Users/ASUS/Downloads/finn_v3_01_today_and_event_sheet.html`; `C:/Users/ASUS/AppData/Local/Temp/codex-clipboard-0bd945b8-20ee-44a1-bbee-aeb5d1673837.png`; complete mockup at `C:/Users/ASUS/.codex/visualizations/2026/11/14/01a1d805-4586-7090-89b4-8d81b8c26123/finn-complete-product.html`.
- **Backend:** `backend/main.py` routes; `repository.py`, `owners.py`, `store.py`, `work.py`, `admission.py` persistence/ownership/jobs/quota; `brief.py`, `events.py`, `portfolio.py`, `theses.py` triage; `sources.py`, `documents.py`, `extract_worker.py`, `pdf_glyphs.py` discovery/evidence; `research.py`, `research_pack.py`, `portfolio_research.py`, `conversations.py`, `llm.py`, `narrative.py` answers; `results.py`, `statements.py`, `facts.py`, `numbers.py`, `report_insights.py` financials; `watches.py`, `scheduled.py`, `usage.py` control/stats.
- **Frontend:** `frontend/src/App.tsx`, `product.css`, `ui.tsx`; `Book.tsx`, `Holding.tsx`, `HoldingResearch.tsx`, `ResearchPack.tsx`, `Financials.tsx`, `Results.tsx`, `ResearchInsights.tsx`, `Narrative.tsx`, `Thesis.tsx`, `EventTimeline.tsx`, `Watch.tsx`, `Recap.tsx`, `Stats.tsx`, `GestureCard.tsx`, `useNavigation.ts`, `useDictation.ts`, `api.ts`, `product.ts`. Earlier engine UI retained in `legacy.tsx`. Assets/PWA `frontend/public/`; generated build `frontend/dist/` (ignored).
- **Tests:** `tests/` Python; `tests/fixtures/` recorded public-source regressions; `frontend/tests/` Node; `frontend/e2e/workflows.spec.ts`; `frontend/playwright.config.ts`; ignored results `frontend/test-results/`.
- **Live records:** `docs/neon-verification.json`, `neon-app-restart-verification.json`, `neon-latency-verification.json`, `source-pack-verification.json`, `source-refresh-verification.json`, `book-refresh-verification.json`, `abb-answer-verification.json`, `followup-verification.json`, `followup-quota-block.json`, `quarterly-source-verification.json`, `five-year-source-verification.json`, `research-view-verification.json`, `insights-verification.json`, `thesis-verification.json`, `filing-calibration-review.json`, `retained-assessment-verification.json`. Before-fix reports retained beside them. Check each record's kind/status/limitation.
- **Verification/deploy helpers:** `scripts/neon_probe.py`, `neon_app_restart_probe.py`, `source_pack_probe.py`, `refresh_probe.py`, `focused_answer_probe.py`, `followup_probe.py`, `quarterly_probe.py`, `five_year_probe.py`, `research_view_probe.py`, `research_view_recheck.py`, `retained_assessment_probe.py`, `insights_probe.py`, `thesis_probe.py`, `host_probe.py`, `restart_probe.py`, `audit_recorded.py`, `render_control.py`, `build.sh`. Read before use; some consume quota, write Neon or restart Render.
- **Schedule:** `.github/workflows/refresh.yml`, disabled by repo variable and server configuration; workflow timeout 30 minutes / poll 1620 seconds.
- **Submission/historical audits:** `docs/SUBMISSION.md`, `EVIDENCE_AUDIT.md`, `QA_REVIEW.md`, `AI_BUILD_HISTORY.md`, `hosted-verification.json`, `havells-verification.json`, `evaluation-cases.json`, `evaluation-results.json`; root `README.md`, `ARCHITECTURE.md`, `TESTING.md`, `THIRD_PARTY_NOTICES.md`, `LICENSES/`; `docs/screenshots/` contains primarily old-release screenshots.
- **Private/local runtime:** ignored `.env`, `.env.deploy`, `.venv/`, `data/` (SQLite, public retained PDF/cache plus private probes), `tmp/`, `data/render-service.json`. Never dump/commit/copy secrets into chat or public handoff exports. Transport these only privately if changing machines; same-PC account switch can reuse files.

## Resume commands (do not run merely to read this handoff)

```powershell
Set-Location C:\Users\ASUS\Desktop\ENAM
.venv\Scripts\python.exe -m pytest -q
npm --prefix frontend test
npm --prefix frontend run build
```

For production browser checks, confirm preview port first. If needed start `npm --prefix frontend exec vite preview -- --host 127.0.0.1 --port 5174`, then `$env:FINN_E2E_URL='http://127.0.0.1:5174'` and `npm --prefix frontend run test:e2e`. Backend when needed: `.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8015 --no-access-log`. Verify current scripts/ports before running. Live source/Neon requests may require narrowly scoped network escalation; normal sockets previously failed with Windows 10013.

## One-hour continuation rule

Begin with this checkpoint and a blocker check, not a rebuild. Spend the first pass on latest regressions/retained replay, evidence accuracy, critical mobile failures and release safety. Reuse valid completed probes; do not consume quota rerunning everything. Prepare an honest submission package in parallel with verification where independent. Only deploy a reviewed candidate with explicit known limitations and actual hosted checks. The user's one-hour request does not waive F01–F34 acceptance or permit invented results. If full completion is impossible, clearly state which requirements remain and the concrete decision needed; do not mark them silently deferred.

## Continuation checkpoint — 15 November 2026 (Claude Code session)

Verification and reconciliation only. No application code changed, nothing committed, pushed or deployed. The six reference forks were not cloned or modified.

**Repository access** (unauthenticated GitHub REST read + `git ls-remote`; no GitHub plugin/`gh` CLI was available in this session, so *write* permission is not yet verified):

| Repository | Result | Default branch | Notes |
|---|---|---|---|
| aadishjainiitd-svg/Finn | 200, public | `main` | remote HEAD `2d949329e671116a175cbdcc20177ccc20ae9da8` |
| aadishjainiitd-svg/yfinance | 200, public fork | `main` | parent ranaroussi/yfinance |
| aadishjainiitd-svg/NseIndiaApi | 200, public fork | `main` | parent BennyThadikaran/NseIndiaApi |
| aadishjainiitd-svg/docling | 200, public fork | `main` | parent docling-project/docling |
| aadishjainiitd-svg/llama_index | 200, public fork | `main` | parent run-llama/llama_index |
| aadishjainiitd-svg/instructor | 200, public fork | `main` | parent 567-labs/instructor |
| aadishjainiitd-svg/ui | 200, public fork | `main` | parent shadcn-ui/ui |

**Local vs remote:** local HEAD `2468e89` is an ancestor of remote `2d94932` (7 remote commits). The working tree already contains the remote content: of 39 files changed remotely, 8 are byte-identical locally and the rest are local evolutions (e.g. `backend/documents.py` compound-topic retrieval refactored, `research.py` VERSION `retrieval-15`, legacy UI moved from `main.tsx` to `legacy.tsx`). 39 modified + 122 untracked files. Safe publication = a new commit whose parent is `2d94932` carrying the reviewed working tree, never a reset/force push. Git in this folder reports "dubious ownership" (`.git` owned by the old `CodexSandboxOffline` user); use `git -c safe.directory=C:/Users/ASUS/Desktop/ENAM ...` per command rather than changing global config.

**Executed now:**
- Python: **145 passed**, 1 existing Starlette/httpx warning. Needs `--basetemp` in a user-writable folder: the default `%TEMP%/pytest-of-ASUS` is owned by the old sandbox user and causes 145 PermissionError *setup errors* otherwise.
- Node: 8 passed. TypeScript/Vite build passed; assets unchanged `index-v291wzQP.js` / `index-DkgSrxmE.css`.
- Playwright: **20 passed** against the existing preview on 5174 using installed Microsoft Edge (`channel: 'msedge'` via a temporary config, since removed). Bundled Playwright Chromium is not installed for this OS user. Still controlled-fixture checks, not live/deployed acceptance.
- Retained replay `claim-linked-v8`: **passed**, 133 filings, 38 pending, 148.11 s, source `checked_at` preserved, no download/inference; wrote Neon public assessment rows. `docs/retained-assessment-verification.json` now records v8. 38 pending remain visible, not resolved.
- Secret scan of all 208 tracked/modified/untracked publishable files against every `.env`/`.env.deploy` value ≥12 chars plus Groq/GitHub/Render/Google/Postgres-URL/private-key patterns: **zero secret hits** (only the public model name matched). `.env`, `.env.deploy`, `data/`, `tmp/`, `frontend/dist/` are ignored. `ACCOUNT_HANDOFF.md` and `FINN_INTEGRATED_CHANGE_PLAN.md` contain local Windows file paths of design inputs (no credentials).

**Still open (unchanged from "What remains" above):** items 2–8 — bank/quarterly adapters and five hand-checked results, five-year/cash/revenue-mix coverage, exact visual comparison, security review, publication + Render Neon configuration + hosted verification, scheduler activation, submission docs refresh. `scripts/render_control.py` creates the service with `autoDeployTrigger: 'off'` (live service setting not re-checked here), so a push should not deploy by itself; still publish to a review branch first unless the user decides otherwise.

### Agent workflow tools (not FINN dependencies) — availability check

Workflow skills are agent tools only; nothing was added to FINN requirements, build or deployment. Nothing was installed, upgraded or cloned.

- **GitHub:** `garrytan/gstack` and `phuryn/pm-skills` both readable (public, default `main`); all eight pm-skills package folders return 200. Upstream is newer than the local copies (gstack `1.99.5.0` vs local `1.91.182.0`; pm-skills plugin `2.3.0` vs local `2.2.0`) — not upgraded by decision.
- **Local Codex installs present:** `~/.codex/skills/gstack` (shared `bin/`, `lib/`, `browse/`) and `gstack-<name>/SKILL.md` for design-consultation, plan-ceo-review, plan-design-review, plan-eng-review, investigate, qa, design-review, review; `~/.codex/plugins/cache/pm-skills/<plugin>/2.2.0/` for all eight plugins, including `prioritize-features`, `create-prd`, `pre-mortem`.
- **This Claude Code session:** none of these are registered as invocable skills (no `~/.claude/skills`, not in the claude.ai plugin catalog). They can only be used by reading the local SKILL.md and following it. gstack preambles fall back to `${CODEX_HOME:-~/.codex}/skills/gstack`, so shell helpers resolve via Git Bash, but `bun` is not installed, so its TypeScript helpers (and the gstack browser) will not run; `~/.gstack` state does not exist for this OS user. Treat helper-dependent steps (learnings, brain sync, telemetry, browse) as unavailable and say so rather than claim them.
- **To make them invocable natively in Claude Code (not done):** gstack — its own Claude Code install into `~/.claude/skills/gstack` (plus bun); pm-skills — add the `phuryn/pm-skills` Claude Code plugin marketplace and install `pm-product-discovery` and `pm-execution`. Both would fetch the newer upstream versions, so they need the user's go-ahead.
- **PDF:** available in this session as `anthropic-skills:pdf` (the earlier `pdf:pdf` name does not exist here).
- **Skill runs:** PM SKILL.md files read in full. gstack SKILL.md files checked for frontmatter/dependencies only (782–2,249 lines each); each must be read in full before it is applied. No gstack design/QA/code review has run in this account; the earlier CEO/design/eng plan reviews, PRD and pre-mortem remain the existing records and are not redone.

### gstack review + QA (this session) — what actually ran

- Read in full: installed `gstack-review/SKILL.md`, `gstack/review/checklist.md`, `gstack-qa/SKILL.md`, `gstack-qa-only/SKILL.md`, QA `sections/{scope,exploratory,system-functional,qa-patterns,browser-setup}.md`, qa-only `sections/{exploratory,reporting}.md`, functional report template. Preamble ran (gstack 1.91.182.0; upgrade prompt declined per user).
- Deviations: user gave no preference, so the recommended options were used: QA ran as **report-only** (`/qa-only`, no stash/commit), review compared the **working tree against GitHub `2d94932`** (skill's "on base branch" stop not applied). `bun` absent → gate-diff, banned-terms, QA evidence/deadline tools, review log and learnings helpers did not run. Aside/`$B` browser unavailable → in-app browser used for one smoke probe.
- Review core pass (CRITICAL categories): SQL is parameterised (one constant-only concatenation in `work.py:29`), subprocesses use argument arrays, no `dangerouslySetInnerHTML`; owner checks in jobs/history/conversations verified by reading. Diff read was **partial** (backend persistence/ownership/routes/portfolio read in full; frontend and remaining backend modules not line-by-line). Adversarial subagent pass dispatched; see its triage below when recorded.
- **ISSUE-001 fixed:** `backend/owners.py` rejected every same-origin write behind Render's TLS proxy (Origin `https://host` vs app-seen `http://host`) and set the session cookie without `Secure` there. Now compares host only and marks the cookie Secure when the page or `X-Forwarded-Proto` is https. Regression test red→green; full suite **146 passed**. QA report: `.gstack/qa-reports/run-20261115T094418Z/` (ignored, local).
- Informational, pre-existing (not in this diff): `/api/research` per-IP limiter keys on `request.client.host`, which is Render's proxy address without forwarded-IP trust, so all visitors share one 5/minute bucket; unauthenticated `/api/source-check/{symbol}` triggers live upstream fetches.
- `scripts/render_control.py set-database` added: copies the local `FINN_DATABASE_URL` to the existing Free service via Render's env-var API and prints only the status code.

### Adversarial review triage and publication (this session)

In-host adversarial subagent completed (backend read in full except statements/facts/report_insights and most of results.py; most frontend components only grepped; fixtures summary-only). Findings and dispositions:

| ID | Finding | Disposition |
|---|---|---|
| F1 | Two cookieless refreshes occupy both global slots for an hour | **Fixed**: long jobs (refresh, research pack, thesis) hold at most one slot; regression test |
| F4 | Non-SourceError on one filing aborts every later refresh | **Fixed**: recorded as pending with error and skipped; regression test |
| F5 | Whole-text regex re-run per sentence, on the event loop | **Fixed**: computed once; classification via `asyncio.to_thread` |
| F6 | Sync Postgres inside async handlers | **Partly fixed**: `/api/jobs`, `/api/evidence`, filing assessment now sync handlers; `start_research` and `assess` writes remain |
| F10 | Research limiter keyed on proxy IP | **Fixed**: keyed on browser session |
| F12 | Disabled scheduler → 503 → 27-minute workflow retry | **Fixed**: 404; regression test |
| F15 | Thesis quota error fails a good refresh | **Fixed**: recorded as `thesis_gap` |
| F16 | Ops redaction misses DB URL/scheduler token | **Fixed** |
| F2 | Any visitor can drain the shared daily Groq allowance | Open, product decision (per-owner sub-quota). Ledger itself is never reset |
| F3 | Scheduler capacity counts disabled rows, no per-owner rule cap | Open; scheduler disabled |
| F7 | One failed heartbeat aborts a long job | Open |
| F8 | Cookieless GETs create session + demo-book rows; no session GC, fixed 365-day expiry | Open; storage-growth risk on Neon Free |
| F9 | Shared snapshot never pruned beyond 14-day label | Open, retention policy vs never-bury-unread |
| F11 | Public research packs/assessments grow durable evidence | Open |
| F13 | Errored scheduler slot cannot be retried | Open |
| F14 | Large NSE feed row rewritten; save timeout can mark fresh feed stale | Open |

New regression tests were added after the fixes; only ISSUE-001's test was shown red before its fix. Full suite **149 passed**.

**Published:** commit `98ac638993731891e1e037c53b1801b085b3c849`, parent `2d94932` (fast-forward push, no force), built from a temporary index: 169 files, local `main` ref and index untouched (still `2468e89`; working tree equals the commit except `.claude/launch.json` and `docs/NEXT_ACCOUNT_PROMPT.txt`, intentionally unpublished). Pre-push exact-secret scan of the 169 files: zero hits.
**Render:** `FINN_DATABASE_URL` set on `srv-dbruffbrjlhs73cl08bg` (status 200, value not printed); deploy `dep-dbso1r3l550s7390eel0` of `98ac638` started. Scheduler secret presence in GitHub Actions could not be checked (no authenticated GitHub API/plugin in this session).

### Hosted verification of `98ac638` (this session, no model calls)

Deploy `dep-dbso1r3l550s7390eel0` went live at ~09:54 UTC; `/health` revision `98ac63899373`. `scripts/release_probe.py` (probe-owned anonymous sessions; token kept only in ignored `data/`) → `docs/hosted-release-verification.json`:
- PASS: storage `persistent_postgres`; session cookie Secure+HttpOnly; `/api/today` 200 from stored snapshot (97 distinct filings, 6 pending, 16 routine; snapshot checked_at 07:54 UTC); same-origin write 200 behind proxy; cross-origin 403; missing app header 403; second session isolated; cited evidence 200.
- Restart: Render restart issued; logs confirm a new uvicorn process served the re-check; private pin survived.
- Live browser at 390px: five tabs, no horizontal overflow, no console errors. First-visit Today shows "No items in this view. Coverage is incomplete." with a 14-day look-back (honest, but an empty-looking first screen for reviewers).
- Not verified: hosted memory under research workloads, cold start after sleep, quota-failure UX on host, fresh generative answers (allowance exhausted), scheduler (disabled; secret presence unknown).
- Rollback: redeploy `2477c701ce1b` from Render (earlier narrow release). `FINN_DATABASE_URL` is now set on the service; the old revision ignores it.
