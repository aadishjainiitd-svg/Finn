# Submission package — partial expanded release, ready for candidate review, not sent

**Release status, 15 November 2026:** the expanded five-tab FINN is deployed at revision `98ac63899373` with durable Neon-backed owner state. It is a **partial release**: the hosted checks below passed, but the full integrated feature plan (F01–F34) has not passed acceptance. Fresh AI answers could not be re-verified on this revision because the free daily model allowance was exhausted; the allowance was not reset or raised. Nothing has been sent. The candidate reviews and sends the email.

Deadline: **15 November 2026, EOD IST**, confirmed by the candidate.

To: assessment@enam.com  
Subject: IIT Delhi – AI Engineer - 2027

---

Dear ENAM team,

Please find FINN, my mobile-first portfolio triage and primary-source research prototype:

- Prototype: https://finn-enam-yije.onrender.com (best at phone width; Render Free may take about a minute to wake)
- Repository: https://github.com/aadishjainiitd-svg/Finn
- Hosted verification of this release: https://github.com/aadishjainiitd-svg/Finn/blob/main/docs/hosted-release-verification.json
- Release status and open requirements: https://github.com/aadishjainiitd-svg/Finn/blob/main/docs/ACCOUNT_HANDOFF.md
- AI build history (earlier sessions): https://github.com/aadishjainiitd-svg/Finn/blob/main/docs/AI_BUILD_HISTORY.md

FINN is built around one habit: an investor opens it between meetings to see what changed across their holdings, why it matters, and the exact source behind it. Today ranks real NSE disclosures for an 18-company demonstration book, keeps unread or unassessed filings visible rather than calling the day quiet, and remembers what was reviewed, pinned or left unfinished. Each event opens to its timeline and the cited PDF page. Research, Ask, Watch and Book extend the same evidence: company research from annual reports and earnings calls, scoped follow-up questions, rule-based watches with a historical preview, and an editable book with weights and theses. Missing weights, theses or periods are shown as unknown, never filled in.

I kept one FastAPI service with React, bounded PDF extraction and deterministic arithmetic, and added Postgres (Neon Free) for owner state, immutable cited pages, job leases and a conservative shared model-quota ledger, so it stays deployable on Render Free with no paid services. Model output can only cite server-held passages; numbers come from code with period, scope and unit checks.

What was verified on this release: on the live service, durable Postgres storage, secure session cookies, the stored Today digest (97 retained filings, 6 awaiting assessment), same-origin writes accepted and cross-site writes rejected, two browser sessions isolated, cited evidence resolving, and private state surviving a service restart. Locally, 149 Python, 8 frontend and 20 browser workflow tests pass, and a replay of the current filing-assessment policy over 133 retained filings completed. A pre-release code review and adversarial review found nine defects, including one that would have blocked every write behind Render's proxy; all nine were fixed and retested before deployment.

What is not complete: fresh AI answers on this revision (free model allowance exhausted on the day), hosted memory under heavy research workloads, scheduled background refresh (built but disabled), five hand-checked quarterly results and wider bank-table coverage, five comparable years of financials and cash use, full annual-report comparison and promise tracking, exact visual and gesture checks against the design, and a held-out accuracy evaluation. Open risks, such as one visitor exhausting the shared model allowance, are listed in the release status document. Next I would close those gaps, add per-user quota, and test the ranking with investors before adding features.

Regards,  
Aadish Jain

---

## Three-minute demonstration (expanded release)

1. **0:00–0:40 — First check.** Open Today at phone width. A first visit shows the last 24 hours; if it says "No items in this view. Coverage is incomplete.", choose **Look back 14 days**. Point out the dated window, coverage and the pending count: unread filings are never presented as a quiet day. Prices are end-of-day.
2. **0:40–1:20 — One event.** Open a needs-you event. Show its timeline, the ranking reasons and the cited PDF page in the evidence sheet. Back closes one layer and returns to the same card. Opening does not mark it reviewed.
3. **1:20–1:50 — Continuity.** Mark it reviewed, pin another, then Undo. Reload: the state persists for this browser session (server-side, not cross-device).
4. **1:50–2:30 — Book and Watch.** In Book, paste a few symbols with weights; the preview validates tickers and refuses weights above 100% without saving. In Watch, type a price or volume rule and show the "understood as" draft and its 30-session preview before saving.
5. **2:30–3:00 — Research and limits.** Open Research for a company and show source coverage and explicit gaps. If the model allowance is exhausted, FINN says so and keeps stored evidence readable; do not present a saved answer as fresh. Close with the open-requirements list.

Do not use synthetic events, hide source failures, or describe saved answers as live analysis. No email has been sent.

## Included evidence

- This release: [hosted verification](hosted-release-verification.json), [release status and open requirements](ACCOUNT_HANDOFF.md), [integrated plan F01–F34](FINN_INTEGRATED_CHANGE_PLAN.md), [decisions](FINN_DECISIONS.md), [retained-source replay](retained-assessment-verification.json), [filing calibration (not held-out)](filing-calibration-review.json), [Neon checks](neon-verification.json).
- Earlier narrow release (historical, revision `2477c701ce1b`, not evidence for this release): [audit](EVIDENCE_AUDIT.md), [hosted measurements](hosted-verification.json), [research results](evaluation-results.json), [HAVELLS](havells-verification.json), [QA review](QA_REVIEW.md), [architecture](../ARCHITECTURE.md), [component licences](FINN_COMPONENT_REVIEW.md).
- Rollback: the earlier release `2477c701ce1b` can be redeployed on the same Render service if the expanded release misbehaves during review.
