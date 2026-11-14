# FINN implementation log

## Checkpoint 0 — implementation authorised, 14 November 2026 IST

- User approved the revised plan with unchanged scope and authorised implementation/deployment, free tiers only.
- Read PRD-FINN, FINN_ARCHITECTURE, FINN_PLAN_REVIEW and FINN_EXPERIENCE_PROPOSAL.
- No application code, dependency installation or deployment yet. Feasibility gate has NOT passed.
- Live local inspection: GROQ_API_KEY, GEMINI_API_KEY, GOOGLE_API_KEY, RENDER_API_KEY, GITHUB_TOKEN and GH_TOKEN are absent from process and user environment. Only presence was printed, never values.
- GitHub plugin can write files/trees/commits in accessible repositories but exposes no repository-creation tool. No Render connector exists in the enabled toolset.
- Browser account inspection was stopped by the user with Escape; no deployment/account mutation occurred.
- Added secret-safe environment templates and Git exclusions before requesting credentials. Recruiter PDFs, source-data caches and raw temporary output are excluded from Git.

## Resume

1. Obtain an accessible FINN repository URL, a free-tier model key in ignored .env, and Render access (ignored .env.deploy or user-assisted dashboard).
2. Never print/read secret values into tool output. Load secrets inside processes and emit only sanitised status/quota measurements.
3. Implement the minimum backend and run the five approved feasibility checks on Render Free. Record live versus fixture/static evidence separately.
4. Only after the hosted gate passes, continue the approved build order and gstack QA/design/code review.

Current blocker is account access, not a validated runtime incompatibility. No model response, full-document ingestion, hosted memory measurement or source request has been performed during this implementation turn.

## Checkpoint 1 — live backend and source pipeline, 14 November 10:30 IST

- Credentials were supplied and loaded into ignored local files; none were committed. Public repository: https://github.com/aadishjainiitd-svg/Finn. Render service: https://finn-enam-yije.onrender.com, explicitly Free, Singapore, Python 3.12.14, one process. No billing setting changed.
- Live minimal deployment returned HTTP 200. The source pipeline is deployed at commit de67be3560520bbfaa6542d0d89250e2da0858f3; the hosted held-out HAVELLS job is currently running. Gate NOT yet passed.
- Groq (not Grok) openai/gpt-oss-120b returned a real answer. Response headers: 8,000 tokens/minute, 1,000 requests/day. Official free-tier documentation also lists 200,000 tokens/day; the first implementation needs daily-token accounting before release. Gemini gemini-3.5-flash-lite returned a cited real-evidence answer; abstention check is running. Fallback remains disabled.
- Live local HAVELLS: generic NSE equity CSV identity (ISIN INE176B01034), Screener discovery, primary BSE annual report 442 pages + transcript 17 pages; 23.33 seconds total, 64.8 MB observed combined peak. Three claims with exact matching citations across both documents. This is local evidence, not hosted performance.
- Live hosted sources: HAVELLS 63 Yahoo daily bars, 4 NSE filings. Health answered in 0.20 seconds during extraction. NSE quote endpoint returned 403 locally; official EQUITY_L.csv works and replaces that dependency. Filings follow NSE's redirect to nseindia.in.
- No frontend yet. Deferred features remain excluded. Next: finish hosted extraction, audit cited pages, restart/version tests; resolve performance if the 180-second bound fails, then implement Brief and mobile UI.

## Checkpoint 2 — gate corrections, 14 November 11:05 IST

- Gate remains OPEN. HAVELLS fully ingests on Render (latest full run 149.78 seconds; observed peak 171 MB), but manual answer audit caught analyst statements attributed to management. TCS annual-report extraction hit the 180-second timeout; transcript succeeded. Both failures are recorded, not waived.
- Replaced fragile model-copied citations and sentence ranges with constrained passage IDs. The server attaches original text and permanent evidence IDs. No arbitrary citation repair across pages/documents. A real local response passed exact-source and semantic checks.
- Transcript synthesis now uses attributable management turns extracted from participant introductions; analyst questions cannot serve as management assertions. Source passages retain full sentences, negation and qualifications. Reported claims still require manual entailment evaluation.
- Switched runtime extractor to pypdfium2 5.15.2 (Apache-2.0/BSD-3-Clause wrapper; BSD PDFium) after measured TCS timeout. Local HAVELLS annual 6.84s, transcript 0.91s; TCS annual 9.44s, transcript 0.88s. Local peak 53–62 MB. These are not hosted performance claims.
- Extraction version is now document SHA + parser fingerprint. Parser changes cannot reuse old citation coordinates. Eighteen source/failure tests passed before parser swap; nineteen after it. TestClient emits a dependency deprecation warning but tests execute successfully.
- Discovery now resolves the corporate/IR host from the issuer website, sorts actual document periods, and tries standalone when consolidated lacks a type. Astral's November 2026 transcript is 19 pages on astralltd.com, linked from astralpipes.com. The older index link was an audio notice and correctly failed type validation.
- User confirmed Gemini billing disabled and will provide limits. Its automatic fallback stays off. Groq is selected primary. No paid usage enabled.
- Current remote head/deployment: 31eef44794228c6b5e460cf96097aeefbe57e1f4; Render build in progress. Local files mirror this code; local Git history was connected to origin while preserving working files. No UI or Brief implementation yet.
- Next: run HAVELLS and TCS on the PDFium deployment, audit their answers, repeat restart with versioned citations, then finish the approved build order. If this gate exceeds 90 minutes from ~10:15 IST, report unresolved blockers/time decision as planned.

## Checkpoint 3 — feasibility gate passed, 14 November 11:15 IST

- Hosted PDFium HAVELLS: 42.73s end-to-end, annual 26.8s / 288 MB peak, transcript 2.02s / 92.1 MB. Three manually checked claims span annual PDF page 216 and transcript PDF page 9. All citation requests return exact supporting text.
- Hosted TCS: annual 21.9s / 155.7 MB, transcript 1.91s / 98 MB. Original timeout resolved. Broad risk query abstained, so it is not a supported gold-set pass. Fixed an additional speaker-parser edge locally (`Samir. Samir Seksaria:` must identify Samir Seksaria).
- Live sources on the final gate deployment return 63 HAVELLS daily bars and 4 NSE filings. Real restart with new citation IDs yields explicit HTTP 410 for evicted versions. 20 local tests pass.
- Runtime deploy initially stalled after a successful Linux build; one cancel/retry resolved it. Current live revision remains 31eef4479422. Local cache-speed and speaker-prefix fixes are newer than that revision and await the next release.
- Gate passed with Groq primary. Gemini billing disabled is confirmed by user; account limits remain pending and automatic fallback remains disabled. No paid usage enabled.
- Proceeding to Brief adapters/prioritisation/arithmetic, then the two mobile screens, evaluation, QA/design/code review and submission package. No deferred feature was added.

## Checkpoint 4 — mobile workflows and evaluation underway

- Brief requests cover all 15 holdings; 91 distinct filings, no exact duplicates in the initial live window. Prices and filings retain separate coverage. Review state uses explicit event revisions and never changes on opening.
- React/Vite builds; seven review-state tests pass. Real gstack browser at 390px renders both navigation destinations. This is an initial implementation check, not completed QA.
- Visual inspection exposed a wrong priority reason on the HDFCBANK reappointment: a biography mentioning Fraud & Vigilance matched the broad fraud rule. Narrowed positive event patterns and added a negation regression; issuer-written subject lines now provide readable assessed headlines. The initial progress note's suspected default clause was not the actual live trigger.
- Selected filing context is included in Research with separate provenance. Added explicit narrative amount conversion using Decimal; incompatible/unknown calculation operands abstain. Dated seed loader added; audited seed data still pending.
- Recorded the 12 evaluation expectations before grading. Live evaluation is running through the API; results are ungraded. Current local build is newer than the public deployment.
- Next: audit answers, fix any unsupported claims/retrieval failures, bundle dated seed, publish full interface, then formal QA/design/code review and submission evidence.

## Checkpoint 5 — deployed workflows, evidence audit and release corrections

- Full Brief/Research/evidence interface deployed. Real 15/15 price and filing coverage observed; 91 distinct filings retained. Prepared examples are dated real-pipeline results. Secrets remain server-side; public AI history excludes credentials, private reasoning and tool arguments.
- Grounding review rejected model paraphrases despite valid citations. The server now renders exact selected passages, retains adjacent numerical exclusions, and marks a missing-call answer partial. All 21 audited displayed citations match their source pages. S1 remains incomplete for its latest-call component; no full 12/12 claim.
- Final additional unseen ticker CROMPTON exposed a memory failure. Reopening the PDF handle every 32 pages preserved all 341 extracted pages byte-for-byte and passed Render: annual 32.08s / 423.6 MB combined peak, transcript 1.60s / 149.5 MB. Guard remains 440 MB; parser v3 distinguishes extraction versions. Current measured hosted revision: 2468e8954836.
- Groq admission now blocks fresh generation at 178,548 reserved tokens / 26 requests against the conservative 180k/900 cap. This is not an observed provider 429. Known baseline survives today's redeploy. Gemini billing-disabled confirmation is recorded; account limits remain pending and fallback stays disabled. CROMPTON's source-only success is not called an answered question.
- Native code review closed source-version, quotation, queue, request-race and pinned-network-address findings. Its final decimal-exclusion finding was fixed and tested. Live reload then found assessment TTL/parser changes reopening unchanged filings; acknowledgement identity now follows source metadata and PDF bytes independently of assessment freshness.
- Latest executed regressions: 48 Python, 8 Node, 7 Playwright tests pass. Vite builds. Live phone/desktop checks cover source excerpt, answer focus, 360/390px fit, 44px controls, 720px desktop column, CSS 200% reflow, reduced motion and a clean fresh console. Physical keyboard/screen reader remain untested.
- Submission draft, three-minute demo, README, notices, audit and resumable checkpoint are prepared. No email sent. Final publication/revalidation and free-capacity resolution remain. Scope unchanged; deferred features excluded.
