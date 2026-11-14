# FINN resumable checkpoint

14 November 2026. User authorised implementation, free hosting and publication; no further routine confirmation required. No paid usage. Do not send the submission email.

Workspace: `C:/Users/ASUS/Desktop/ENAM`. Public repo: `aadishjainiitd-svg/Finn`. App: `https://finn-enam-yije.onrender.com`. Owned Render service: `srv-dbruffbrjlhs73cl08bg`, Free Singapore. Do not modify unrelated services.

Current measured parser deployment: `2468e895483642c11c4c4d81d329bc77bc411f31`. Local changes and subsequent commits may be newer; inspect Git status and `/health` before resuming. See [implementation log](IMPLEMENTATION_LOG.md), [audit](EVIDENCE_AUDIT.md), and [QA review](QA_REVIEW.md).

## Remaining release gates

1. Gemini billing disabled is confirmed; RPM, TPM and RPD for `gemini-3.5-flash-lite` are still requested. Do not ask for more keys or enable automatic fallback without verified account limits and separate admission. Groq primary is `openai/gpt-oss-120b`; Groq and xAI Grok are different services.
2. Do not reset the Groq ledger. Today's known baseline is 178,548 reserved tokens / 26 requests, versus FINN's 180,000 / 900 cap. This is conservative admission, not an observed provider exhaustion. If account limits arrive, implement/test bounded Gemini routing; otherwise the next legitimate UTC-day reset is 15 November 05:30 IST.
3. Rerun broad TCS case S1 and a focused CROMPTON question when free capacity is available. S1 currently has a correct but incomplete annual-report answer. CROMPTON's annual report and transcript now pass live extraction; no synthesized answer is claimed.
4. Finish any current hosted/UI revalidation, secret scan and public-link checks, then update the evidence audit and submission draft. Do not change expectations to make results pass.

## Commands and evidence

- Python: `.venv/Scripts/python.exe`; tests: `python -m pytest -q`.
- Frontend: `npm --prefix frontend test`, `npm --prefix frontend run build`; Playwright: `npm --prefix frontend run test:e2e` with Vite on 5173.
- Live cases: `python scripts/evaluate_live.py <base-url> S1`; held-out: `python scripts/host_probe.py CROMPTON`. These can use provider capacity.
- Render: `python scripts/render_control.py status|deploy|restart`. The helper checks Free plan and targets only saved FINN service state.
- Secrets exist only in ignored `.env` / `.env.deploy` and Render server environment. Never print them or include them in history exports. Do not publish `data/`, `tmp/`, raw logs, recruiter PDFs or private reasoning.
- Raw live evidence is ignored under `data/`; public metadata is in `docs/evaluation-results.json`. Browser fixtures are deliberately separate from live source results.

## Invariants to retain

Two destinations only: Brief and Research, shared evidence sheet. Opening never acknowledges. Every filing remains reachable; unknown/failed assessment stays pending. Late responses cannot replace a newer question/sheet. Price and filing coverage update without automatic event reordering. Exact source versions, page numbers, negation, units and periods remain intact. The PDF cache workaround reopens every 32 pages without raising the memory guard; parser v3 gets distinct citation identities.

Submission deadline: 15 November EOD IST; target 21:00 IST. Draft email and demo in [SUBMISSION.md](SUBMISSION.md). Completion requires honest acceptance evidence, not just a live URL.
