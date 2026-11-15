# FINN final checkpoint

15 November 2026. Implementation, final runtime verification and submission-package publication are complete. Unauthenticated prototype, repository, AI history, submission, audit and screenshot links all returned HTTP200. No email sent.

- App: https://finn-enam-yije.onrender.com
- Repository: https://github.com/aadishjainiitd-svg/Finn
- Final application revision: `2477c701ce1b0c9a0d7f4ecce3985d0ef017ecb9`. Later commits may change only documents, verification helpers and screenshots; no app redeploy is needed for those.
- Render: existing FINN Free Singapore service `srv-dbruffbrjlhs73cl08bg`; do not touch unrelated services or enable paid usage.
- Runtime: repaired `.venv/Scripts/python.exe`, Python 3.12.14. Node 24.21. Provider Groq `openai/gpt-oss-120b`. Gemini fallback disabled; billing disabled is confirmed but account limits remain unverified.
- Tests: 56 Python, 8 Node, 7 Playwright; Vite build. Final hosted CROMPTON supported, both PDFs, 35.27s; annual peak 424.3 MB below 440 MB guard. Real restart plus saved-excerpt mobile state verified. See [hosted record](hosted-verification.json) and [QA](QA_REVIEW.md).
- Evaluation: 17 claims / 26 exact references across the 12-case set; HAVELLS S4 is now supported across report risks, demand and specific margin pressure. Fresh hosted run 32.28s, exact evidence endpoints and identical cache replay. Unsupported questions still abstain. See [audit](EVIDENCE_AUDIT.md).
- Submission: [covering email and demo](SUBMISSION.md), [README](../README.md), [as-built architecture](../ARCHITECTURE.md), [actual sanitised AI history](AI_BUILD_HISTORY.md). Deadline: 15 November EOD IST; target 21:00 IST. Candidate reviews and sends the email.

## Operational limits

Render Free sleeps and loses caches; browser retains one answer and local review state. Restarted missing citations return HTTP410 with the captured excerpt, never replacement text. Known quota seed baselines restore; uncheckpointed usage may be lost and provider free limits remain authoritative. No OCR, universal ticker guarantee, intraday quotes, configurable portfolio or deferred features.

## Safe continuation

Secrets only in ignored `.env` / `.env.deploy` and server environment. Never print them or publish `data/`, `tmp/`, raw logs, recruiter PDFs or private reasoning. Public files were scanned for exact secret values before publication. Raw evidence remains ignored locally.

Local Git HEAD predates plugin-published commits; modified files include already-published work. Preserve local history. A mixed reset was rejected; do not retry blindly. Use a read-only fetch/diff or GitHub plugin with an expected-head lease. Application and documents were published through the authorised GitHub plugin.

Commands: `python -m pytest -q`; `npm --prefix frontend test`; `npm --prefix frontend run build`; `npm --prefix frontend run test:e2e` with Vite on 5173. Live probes consume capacity: `python scripts/host_probe.py SYMBOL`; `python scripts/restart_probe.py SYMBOL` actually restarts FINN. Do not run them as routine status checks. Render helper `status` is read-only.

HAVELLS repair: `retrieval-9-prompt-10`; [repair evidence](havells-verification.json). Source/renderer regression tests 56 pass. Prior CROMPTON/restart measurements remain tied to 78ba67e62a68; the final HAVELLS measurement is on 2477c701ce1b.
