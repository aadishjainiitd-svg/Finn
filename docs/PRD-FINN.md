# FINN — focused PRD

> Implementation status, 14 November 2026: user approved this reviewed scope. The hosted feasibility gate passed; implementation and acceptance testing are underway. Historical planning-only statements below describe the review date, not current authorisation. Current evidence: [implementation log](IMPLEMENTATION_LOG.md) and [feasibility results](FEASIBILITY_RESULTS.md). Runtime extractor is PDFium 5.15.2 after a measured pypdf timeout; Groq is primary and Gemini fallback remains disabled pending account quotas.
14 November 2026 · Planning only. The two-workflow scope, 6–8 hour budget and Render Free hosting are agreed; implementation details below are recommendations, not evidence of a working product.

## Summary

FINN helps a public-markets investor notice relevant changes, verify their evidence, and investigate a company from a phone. Its promise: **“An investor reaches for it throughout the day because it saves time and shows only what matters.”** The submission should demonstrate a complete, trustworthy loop rather than a large dashboard.

## Background

The recruiter PDFs require a mobile-first prototype with portfolio monitoring, on-demand research, and three source classes: EOD prices/volume, exchange filings, and annual reports plus concall transcripts. The latter two document types must both work. Research must use primary sources. The assignment rewards judgment, product usefulness, architecture and reliability; examples in the brief are not all mandatory features.

Local source probes succeeded, but a deployed end-to-end research request and authenticated model calls remain untested. See [validation evidence](DATA_ACCESS_VALIDATION.md).

## Objective

Before submission, demonstrate these acceptance targets, not claimed usage results:

1. On a 390px phone viewport, a reviewer can identify the next event to inspect and reach its evidence in at most two taps; returning preserves review state.
2. All 15 holdings show explicit price and filing coverage. Three prepared research companies and one newly selected, source-available NSE ticker work through the same pipeline.
3. A 12-case research evaluation passes: every material factual claim is supported by its cited page, numerical answers match deterministic calculations, and missing evidence produces a bounded answer or abstention.

## Market segment

One initial segment: an investor monitoring several Indian listed companies, with short checks between meetings and occasional deeper investigation. This is an assumed workflow from the assignment, not validated interview evidence. Trading execution, retail onboarding and institution-wide collaboration are outside scope.

## Value proposition

| Part | FINN's answer |
|---|---|
| Who | The investor repeatedly checking a portfolio |
| Why | Find changes worth investigating without rereading everything |
| Before | Assumed workflow: exchange lists, company PDFs and separate market-data tabs |
| How | A prioritised brief with explicit review state, followed by page-cited research |
| After | Know what changed, why it merits attention, and what remains uncertain |
| Alternatives | Manual source browsing or generic chat; FINN combines continuity with inspectable evidence |

FINN turns scattered disclosures into a short review queue and makes every investigation easy to verify.

## Solution

Two destinations, **Brief** and **Research**, share one evidence sheet. Details are in the [experience proposal](FINN_EXPERIENCE_PROPOSAL.md); this document defines the build boundary.

| Moment | Smallest useful answer | Next action |
|---|---|---|
| First check | New material events and unfinished review | Inspect highest-priority event |
| Between meetings | What changed since the previous check | Review or leave outstanding |
| Important event | What changed, why review it, what is unproven | Open evidence; investigate company |
| End of day | Today's events, outstanding items and dated EOD signals | Finish review or retain outstanding work |

**MVP:** 15 fixed holdings from the existing build plan; company grouping within priority tiers; exact deduplication; “Since review”, Today, 7-day and 14-day views; explicit Mark reviewed/Undo; dated EOD signals; three research demos (TCS, KPITTECH, ASTRAL); generic ticker discovery; brief company context and focused questions; cited evidence and visible coverage/failures. Opening the app never acknowledges an event. An updated source revision can reopen it. Routine items remain accessible; unassessed filings cannot silently become routine.

The brief refreshes on opening and while active. This is the prototype's push experience; native phone notifications and intraday prices are excluded. Quiet, stale, partial and unavailable are distinct states.

Scope-preserving review correction: collapse only positively assessed routine subtypes, never generic categories or failed extractions. Account for every fetched filing. The demo must include a second visit showing less repeated reading, an outstanding item and separate source-coverage status; this demonstrates behavior, not measured retention.

**Technology:** React/TypeScript/Vite, plain CSS, FastAPI/Python, page-based PDF extraction, SQLite FTS5, and bounded Groq synthesis with a tested Gemini fallback. See [architecture and acceptance](FINN_ARCHITECTURE.md) and [component audit](FINN_COMPONENT_REVIEW.md).

**Assumptions:** focused work really remains 6–8 hours; Render account access and model credentials are usable; primary documents are discoverable and contain extractable text. No universal ticker/PDF coverage claim. The user selected Render Free; source, extraction and model capability checks remain technical gates, not additional product decisions.

## Release

Revised estimate: 7¼-hour core plus 45-minute contingency within the stated 6–8 hour range, conditional on the hosted feasibility gate. A six-hour delivery is no longer a credible commitment for all listed acceptance checks. Deadline: **15 November 2026 EOD IST**, user-confirmed; aim to submit at 21:00 IST. Deliver a public prototype, repository, AI build history, and short covering email with trade-offs and omissions. Submission instructions remain in [the build plan](FINN_BUILD_PLAN.md#submission). Final plan approval remains pending.

Stretch only after acceptance: a “Challenge this conclusion” preset that reuses research. Defer management-commitment tracking, OCR, vector infrastructure, full quarterly comparisons, configurable alerts, accounts and portfolio editing.

Demo: review a real material filing, inspect its page, ask a follow-up, mark it reviewed, return to a quieter brief, then research a ticker outside the prepared set. Any replay of historical events is explicitly dated and labelled.
