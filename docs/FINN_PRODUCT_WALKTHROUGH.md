# FINN — the complete product

15 November 2026 · Product vision and mockup companion. This describes the target, not the currently deployed feature set. The [integrated change plan](FINN_INTEGRATED_CHANGE_PLAN.md) remains the detailed acceptance contract.

FINN is a mobile-first triage inbox for an investor's portfolio. Its job is to turn a stream of disclosures and daily market data into a short, explainable list of things worth investigating, then help the investor verify the evidence and retain their decisions between visits.

The recurring loop is **notice → understand → verify → act → return**. It is not a trading terminal, stock-tip generator or generic chatbot.

## Today — what needs me?

- Windowed portfolio digest with Needs you, Worth knowing and Buried tiers.
- Default since-last-opened window, plus unfinished work; first visit defaults to a labelled 24-hour view. Other periods and custom windows remain available with actual coverage.
- One thread for the notice, results, call and transcript of the same underlying event; original disclosures remain accessible.
- Ranking by verified event category, position size, comparable guidance surprise, thesis effect and bounded feedback. Every reason is shown; critical items cannot be buried by low weight or Noise.
- Result cards with Revenue, EBITDA where valid, PBT and PAT, QoQ/YoY comparisons, units and scope; appropriate alternatives for financial companies.
- Management-change cards with filing-backed biography and approval conditions.
- Completed-session price/volume checks, configurable thresholds, nearby filing context or an honest unexplained state. Proximity is not causation.
- Read-across to another holding with a verified sector/input connection, labelled as an interpretation.
- Mattered/Noise feedback; swipe or button actions for reviewed/pinned, with Undo and persistence.
- An inspectable buried list and reversible promotion of a routine filing type.
- A holdings pulse, Week ahead, on-demand spoken brief, return recap grouped by day, and a quiet state only when coverage supports it.

## Event sheet — what changed, and why care?

The sheet contains the event timeline, headline, figures/profile/price context, management-guidance verdict, personal-thesis verdict, ranking reasons, feedback and a scoped Ask bar. Numbers, verdicts and reasons open their own supporting evidence. Unknowns stay unknown. Returning closes one layer and preserves position in the inbox.

The evidence view shows document identity, reporting period, exact excerpt and context, PDF page, immutable source version and original link. Old answers must never silently resolve to replacement source text.

## Research — understand any source-available NSE company

- Business description, segments and revenue mix.
- Six appropriate headline financial measures with period, basis and sources.
- Five-year revenue and margin trajectory; missing or incomparable years remain gaps.
- Balance-sheet, leverage, working-capital and cash-conversion context where supported.
- Promise ledger: management's stated target versus comparable actual, with both sources. Met, missed, pending, revised, withdrawn and noncomparable states; kept count excludes promises that cannot be evaluated.
- Five-year cash use in capex, acquisitions, shareholder returns, debt repayment and investments/other uses, with a reconciled sources-and-uses bridge.
- Annual-report changes: new, changed and removed disclosures, supported by two properly covered versions.
- Flags from audit/notes/contingencies/related-party disclosures; concise bull and bear interpretations with evidence.
- Documents-read and missing-source coverage; add-to-Book and source-backed follow-ups.

## Ask — a question with a defined evidence boundary

Choose event, company or portfolio scope. Keep a conversation with cited answers, small deterministic charts where useful, suggested follow-ups and a challenge-conclusion action that searches for contrary evidence. Use text or speech. Missing evidence produces a bounded answer, not invented certainty.

“Watch this for me” converts an answer into an editable rule draft, never an automatically activated instruction. A new ticker follows identity/discovery/extraction rather than a hard-coded demo lookup.

## Watch — conditions you can inspect before enabling

Create price, volume and announcement-category rules. Adjust values directly or describe a rule in plain language. FINN shows “Understood as” and requires confirmation. Unsupported or ambiguous conditions cannot silently become weaker rules.

Preview the rule over 30 completed trading sessions with enough earlier baseline data, coverage counts and firing dates. Historical replay and live evaluation use the same calculations. Keep versioned firing history and explain possible filing context.

Delivery options are in-app, opt-in Telegram and a prepared voice brief, with timezone and quiet-hour controls. Voice does not autoplay in the background. Delayed, failed and uncertain deliveries remain visible; retries must not create duplicate alerts.

## Book — what I own and why

Add companies by search, pasted list or CSV with a validation preview. Edit allocations and a one-line thesis; filter holdings and open a holding page with dated price, 30-session trend, thesis evidence, cash, report changes, read-across and full Research.

The health/attention bar distinguishes unknown from supported, weakening or a user-confirmed broken thesis. A falling price alone cannot determine thesis health. No invented personal allocations or reasons for ownership.

## Quality that applies everywhere

- Mobile-first five-tab navigation, exact navy/Hanken/amber reference, raised centre Ask button, 430px cap and 390px layout checks.
- Installable PWA and clearly dated offline reads where the browser supports them.
- Layout-matched skeletons, unread-filing/open-PDF recovery, missing-document partial views, stale/quota/queued/unavailable states.
- Keyboard, screen-reader and touch access; no gesture-only actions; repaired icons and sufficient contrast.
- Primary-source research, validated issuer/document identity, preserved speaker/qualifications, deterministic arithmetic and like-for-like financial periods/units.
- Durable citation versions, review/visit/pin state and owner-isolated books/rules. Shared public evidence does not mean shared private portfolios.
- Cached extraction and answers, free-quota admission, bounded processing and stored-data screen reads.
- Secondary Stats view with measured tokens, cache use, source coverage and per-digest/per-research cost.
- Evaluation against real filings, hand-checked results, unfamiliar tickers, failures, restarts, mobile interactions and semantic evidence support; honest submission/demo evidence.

No requested feature has been deferred out of the target. Durable database access, ownership/recovery policy and actual scheduler/Telegram setup are still decisions or integration gates before implementation completion.

## Interactive mockup boundaries

The conversation preview includes 18 views: Today, event, results, evidence, Research, Ask, Watch, Book, holding, buried list, Week ahead, recap, voice, rule draft, import, Stats, delivery settings and coverage. Six selectable states and six research sections expose the rest of the experience.

It uses recorded primary-source excerpts, TCS annual figures/five-year revenue, an HDFC Bank reappointment filing, saved research answers and recorded EOD bars. Figures and records are not illustrative inventions. Missing cash reconciliation, comparable promises and report pairs are shown honestly instead of being populated with fabricated numbers. Historical financial context is distinguished from the current review window.

Interactions affect only the preview. It sends no AI requests or notifications and does not update the deployed app. Source/JavaScript checks and a minimal-DOM interaction exercise passed; actual browser visual inspection was blocked by the browser's local-file policy and is not claimed. No application source, installation, commit or deployment was performed.
