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
