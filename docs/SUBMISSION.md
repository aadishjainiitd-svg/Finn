# Submission package — partial expanded release, ready for candidate review, not sent

**Release status, 15 November 2026:** FINN is deployed at revision `0be0c56` with durable Neon-backed owner state. It is a **partial release** of the integrated plan (F01–F34): the hosted checks below passed and the listed features are verified as stated, but full acceptance is not claimed. Nothing has been sent. The candidate reviews and sends the email.

Deadline: **15 November 2026, EOD IST**, confirmed by the candidate.

To: assessment@enam.com  
Subject: IIT Delhi – AI Engineer - 2027

---

Dear ENAM team,

Please find FINN, my mobile-first portfolio triage and primary-source research prototype:

- Prototype: https://finn-enam-yije.onrender.com (best at phone width; Render Free may take about a minute to wake)
- Repository: https://github.com/aadishjainiitd-svg/Finn
- Hosted verification of this release: https://github.com/aadishjainiitd-svg/Finn/blob/main/docs/hosted-release-verification.json
- Release status and open items: https://github.com/aadishjainiitd-svg/Finn/blob/main/docs/ACCOUNT_HANDOFF.md

FINN is built around one habit: an investor opens it between meetings to see what changed across their holdings, why it matters, and the exact source behind it. Today ranks real NSE disclosures for an 18-company demonstration book, keeps unread filings visible rather than calling the day quiet, and remembers what was reviewed or pinned. Each event opens to its timeline, a quarterly results comparison where every number opens its PDF row, management's own guidance with its status, and the effect on the investor's thesis.

Research reads annual reports and earnings calls directly. It shows up to five fiscal years of revenue, margin, profit and cash, each from the newest report that prints it, with restatements marked; where the operating cash went, reconciled to reported closing cash; and revenue mix, shown only when segments add up to reported revenue. Guidance is scored against reported numbers only when the comparison is like for like; anything else is labelled rather than counted.

I kept one FastAPI service with React and added Postgres (Neon Free) for owner state, immutable cited pages, job leases and a conservative shared model-quota ledger with a per-browser share, so it stays on Render Free with no paid services. Model output can only cite server-held passages; numbers come from code with period, scope, unit and currency checks, and tables that do not reconcile are dropped rather than repaired.

What was verified: on the live service, durable Postgres storage, secure session cookies, the stored Today digest, same-origin writes accepted and cross-site writes rejected, two browser sessions isolated, and cited evidence resolving, private state surviving a service restart, and the quota limit refusing a new answer with a clear message while stored sources stay readable. Locally, 169 Python tests, 11 frontend tests and 23 browser workflows pass. ABB's five-year figures were checked against the source rows, and its cash allocation ties to reported closing cash in every year checked. A code review and an adversarial review found defects including one that would have blocked every write behind Render's proxy; those were fixed and retested, and the remaining open risks are listed in the release status document.

What is not complete: a fresh AI answer on this revision (the free daily allowance was used up on the day and was not raised), a held-out accuracy evaluation, an exact visual and gesture comparison with the design, more hand-checked quarterly tables and bank layouts, column-layout segment tables, hosted memory under heavy multi-report research, scheduled background refresh (built but disabled), and a retention policy for shared public evidence. Next I would close those gaps and test the ranking with investors before adding features.

Regards,  
Aadish Jain

---

## Three-minute demonstration

1. **0:00–0:40 — First check.** Open Today at phone width. If it says "No items in this view. Coverage is incomplete.", choose **Look back 14 days**. Point out the dated window, coverage and pending count: unread filings are never presented as a quiet day. Prices are end-of-day.
2. **0:40–1:20 — One event.** Open a needs-you event. Show the timeline, the results comparison (tap a number to open its PDF row), "Their guidance" and "Why it ranks here". Back closes one layer and returns to the same card.
3. **1:20–2:10 — Research.** Open Research for **ABB** and choose Open saved research. Show the five-year trajectory (tap a number; note the restated 2021 operating cash with both rows cited), then Where the cash went and its closing-cash check.
4. **2:10–2:40 — Continuity.** Mark an event reviewed, pin another, then Undo. Reload: state persists for this browser session.
5. **2:40–3:00 — Limits.** Show an empty year or an unscored guidance line and explain that FINN labels what it cannot verify instead of filling it in. Close with the open-items list.

Do not use synthetic events, hide source failures, or describe saved answers as live analysis. No email has been sent.

## Included evidence

- This release: [hosted verification](hosted-release-verification.json), [release status and open items](ACCOUNT_HANDOFF.md), [integrated plan F01–F34](FINN_INTEGRATED_CHANGE_PLAN.md), [decisions](FINN_DECISIONS.md).
- Earlier narrow release (historical, revision `2477c701ce1b`, not evidence for this release): [audit](EVIDENCE_AUDIT.md), [hosted measurements](hosted-verification.json), [research results](evaluation-results.json), [QA review](QA_REVIEW.md).
- Rollback: earlier revisions can be redeployed on the same Render service if this release misbehaves during review.
