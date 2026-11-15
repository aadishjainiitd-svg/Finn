# FINN experience proposal

> **Target superseded, 15 November 2026:** The [final integrated change plan](FINN_INTEGRATED_CHANGE_PLAN.md), especially sections 4, 5, 8 and 9, defines the five-tab journey, exact visual tokens, reusable components, all requested features and shared states. This document is the earlier two-workflow experience history, not the current feature boundary. The HTML/screenshot govern Today/event appearance; the integrated plan governs behaviour and evidence. No new interface was built during this review.

> Current implementation status (15 November 2026): approved scope is implemented and deployed on Render Free. Production Groq 120B, hosted CROMPTON research, restart provenance and final mobile workflows are verified. The earlier HAVELLS partial answer is resolved and verified on the deployed app; see the HAVELLS repair record in the audit. See [final audit](EVIDENCE_AUDIT.md), [implemented architecture](../ARCHITECTURE.md), [QA results](QA_REVIEW.md) and [checkpoint](RESUME.md). Historical planning-only statements below are retained as the decision record, not current authorisation. No deferred feature was added.

14 November 2026. Recommendation for the agreed 6-8 hour build; not an approved visual design system or a rendered prototype.

Methods: design-consultation for product context, visual coherence and deliberate differentiation; pm-product-discovery:prioritize-features for impact, effort, risk and strategic alignment. Existing assignment analysis and observed source-access results are the evidence base. No investor interviews, usability tests or competitor UI audit have been performed. No independent design agents were used.

## The experience in one sentence

Open a short brief, understand the few changes that deserve review, inspect the evidence, investigate a company, and leave knowing what remains unresolved.

The remembered promise: FINN helps me know when I am caught up, and lets me verify why something matters.

Assumed user: a professional public-markets investor monitoring the fixed mock portfolio, often using a phone between meetings. Daytime office and travel use favour a light, readable interface. The workflow ends in a research decision, not a trade recommendation.

## Four moments, one product

| Moment | Investor question | Smallest useful answer | Next action | Surface |
|---|---|---|---|---|
| First check of the day | What changed since I finished reviewing, and what needs attention first? | A short ordered list of new material events plus previously unreviewed items; one sentence of relevance per event; explicit source coverage and latest EOD session | Open the first relevant event, or acknowledge an already-understood item | Brief |
| Between meetings | Did anything new happen that is worth interrupting me for? | New or updated events distinguished from unchanged items; no repeated daily recap; a truthful quiet state when no priority items arrived | Read the delta, mark reviewed, or leave it outstanding | Same Brief, default view |
| Important-event investigation | What exactly changed, how strong is the evidence, and what should I check next? | What happened; why it may matter; what is still unknown; source excerpt and date | Verify the filing, then open company research with an editable question | Expanded event -> evidence drawer -> Research |
| End-of-day review | What did I learn today, what remains unreviewed, and did the completed session show unusual activity? | Today's prioritised events with review states, outstanding items, and dated EOD signals | Finish reviewing or deliberately leave an item outstanding for next time | Brief with Today selected |

Do not create morning, intraday and evening dashboards. These are views of the same information and review state. EOD data cannot support intraday price monitoring. At a quiet or non-trading time, show the last completed session date instead of manufacturing new activity.

## Prioritisation method and top five

No reliable reach, satisfaction or usage data exists, so numerical RICE/ICE scores would be invented precision. Rank on time saved, evidence trust, repeat-use value, effort and failure risk. Effort is relative incremental work within the already agreed two-workflow product, not an independently estimated delivery promise.

| Rank | Capability | Impact / alignment | Effort | Risk | Decision and trade-off |
|---|---|---|---|---|---|
| 1 | Prioritised brief with a concise reason per event | Very high: directly answers what matters | Medium | High: false suppression or overstatement | MVP. Keep routine items accessible and expose unassessed items rather than silently burying them |
| 2 | Evidence drawer attached to claims | Very high: makes concise answers trustworthy | Low-medium | Medium: wrong page or weak support | MVP. Show original excerpts, source date and page; do not build an embedded PDF editor/viewer |
| 3 | Contextual, source-grounded company research | High: turns a signal into an investigation and satisfies pull | Medium-high | High: retrieval gaps and unsupported conclusions | MVP. Business context plus a focused answer; no eight-section report |
| 4 | Since your last review and explicit review state | High: creates a reason to return without rereading | Low-medium | Medium: premature clearing or lost local state | MVP. Opening is not reviewing; explicit per-event acknowledgement with Undo |
| 5 | Grouped filing presentation | Medium-high: reduces duplication and scanning | Low for company sections; high for semantic event clustering | Medium-high if unrelated disclosures are merged | MVP only for company sections and verified exact duplicates; keep distinct events visible |

## Evaluate the proposed ideas

| Idea | Investor benefit | Scope call | Boundary |
|---|---|---|---|
| Since your last review | Avoid rereading and preserve unfinished work | MVP | Review is an explicit action; automatic refresh/opening never clears events |
| Grouped filings | See a company once, inspect its distinct changes together | MVP, constrained | Group by company within priority tier; exact duplicates can share a source row. Do not infer one event merely from matching company/date/category |
| Followed management commitments | Remember a promise and check subsequent delivery | Stretch, after this submission | Requires metric, baseline, deadline, qualification, comparable actuals and update detection. A transcript quote alone is not a tracked commitment |
| Evidence drawers | Verify without losing the current question or scroll position | MVP | One shared drawer for filing and research citations; excerpt, document title, period/date, page and original link |
| Challenge this conclusion | Counter confirmation bias | Stretch as a visible preset; the underlying question can be typed in MVP | Ask for contrary evidence in the retrieved sources, missing coverage and conditions that would change the assessment. No invented bear case and no second model merely to disagree |

Do not add a visible challenge button until a small test set demonstrates supported counterevidence and honest abstention. It reuses Research, not a debate room, agent council or separate screen. For a question spanning filings and fundamentals, only draw a comparison if both evidence sets are actually retrieved; otherwise state the gap.

## Navigation and screens

Two primary destinations in a fixed bottom navigation: **Brief** and **Research**. One shared evidence drawer. Event expansion is inline, not a third dashboard or another nested overlay. Preserve scroll position when returning from Research.

### Brief

Top area, in this order:

1. FINN and a compact refresh action.
2. "Since your last review" names the queue; a separately labelled "Checked at …" reports last successful source checking. That timestamp is never described as the user's review time. First use instead says "Your first brief · Last 24 hours"; no fabricated prior review.
3. One truthful summary sentence with computed counts, such as "2 new events to review; 1 still unreviewed." These numbers are illustrative UI copy, not validated dataset classifications.
4. Coverage status: completed company checks and the EOD session date. Failed-source details expand inline. Never combine filings and price coverage into one misleading success count.
5. A simple view selector: Since review, Today, Last 7 days, Last 14 days. It replaces a custom date-range picker.

Content sections:

- **Review first:** content-supported changes with potential relevance to the investment case.
- **Worth a look:** lower-priority substantive updates and standalone EOD threshold signals.
- **Routine filings (N):** collapsed but searchable by company through the same list/filter. Do not promise global full-text search in MVP.
- Unparsed or unclassified potentially relevant filings remain visible with an "Assessment pending" label, outside the routine bucket.

Within a tier, group event rows by company. Put the highest-priority/newest event first; show each event title, source publication date, review state and one-line relevance. Do not add a company card around event cards. The layout is a list of company headings and event rows with restrained separators.

An expanded event contains at most:

- **What changed:** factual headline and one short supporting statement.
- **Why review it:** a conditional implication grounded in the event; no confident stock-price prediction.
- **Not established:** the most important uncertainty, only when present.
- **Evidence** and **Research company** actions.
- **Mark reviewed**, followed by a reversible confirmation and Undo.

The Research action carries the company and an editable suggested question. Do not imply that annual reports and transcripts contain a new filing's facts. The filing remains separately cited; questions that require cross-document analysis disclose unavailable evidence.

### Review-state rules

- Opening FINN, scrolling, opening evidence, and changing date windows never mark an event reviewed.
- Mark reviewed acknowledges the current event revision only. New filings or a substantive source revision remain eligible for attention.
- Marking one item changes its state in place. Move it out of the default unreviewed list on the next intentional refresh/navigation, not from under the user's finger.
- Previously encountered, unreviewed material items appear in **Still to review**, even when their publication timestamp is outside the current short window, within retained source coverage.
- Newly discovered older filings are labelled with their original publication date and "newly found" if needed. Do not pretend they were just published.
- First use has no review baseline. After first successful ingestion, track event identities/revisions and explicit acknowledgements; a last-open timestamp is not enough.
- Review state is local to this browser/device in MVP. Clearing browser data resets the state; do not promise cross-device continuity.
- No bulk "all reviewed" action in MVP. It adds race conditions and encourages accidental acknowledgement of unseen events.

### Research

1. Company/ticker input with clear company identity after resolution; start with three prepared examples, but permit any NSE ticker with available documents.
2. A compact source-coverage line naming the actual annual-report year and transcript quarter/date.
3. A short business snapshot, with citations, followed by an editable question. Example prompts: "What is management's stated outlook?" and "What supports or limits that outlook?" A change comparison is offered only when comparable earlier evidence is available; these prompts are not promises that the sources contain an answer.
4. A concise response: **Answer**, **Supporting evidence**, and **Limits / what to check next** where relevant. Avoid an automatic report template full of empty sections.
5. Inline citations open the shared evidence drawer. A new question replaces the active answer; preserve the previous question locally only if cheap. A full conversational history is outside MVP.

Fetch and parse once per document version. User-facing progress should say "Finding company reports", "Reading the transcript", or "Preparing your answer". Do not expose embeddings, token counts, cache keys or provider routing in the product flow.

### Evidence drawer

On phones, a bottom sheet with a visible close button and an optional full-height expansion. On wider screens, it may become a side panel. It returns focus and scroll position to the initiating claim. No nested drawers.

Show source title, issuer, reporting period/publication date, PDF page number, verbatim relevant excerpt and **Open original**. Separate original wording from FINN's interpretation. If page text is unreliable, show that limitation and the original link; do not present generated prose as a quotation. The PDF viewer's page number and a printed page number may differ: label the number as "PDF page".

## Priority rules

Use explicit rules and explanations, not a decorative 0-100 importance score.

1. **Eligibility:** portfolio company, genuine source and valid publication time. Separate late-discovered and revised events. Apply the selected window without silently importing older material as new.
2. **Material content before category:** leadership departures/appointments, changes to guidance, reported financial outcomes, substantial transactions, financing or regulatory developments may deserve Review first when supported by the actual filing. Category alone is a candidate signal, not a verdict.
3. **Routine means checked routine:** meeting schedules, publication notices, repeat disclosures and ordinary administrative updates usually collapse. A resignation must not be hidden merely because the category sounds administrative. Ambiguous items stay visible as unassessed.
4. **Price/volume:** show a signal when absolute daily move exceeds 5% or completed-session volume exceeds 2x its preceding 20-session average, subject to valid data and adequate baseline. Label the observed session. Standalone threshold signals normally go in Worth a look; do not infer a cause from a concurrent filing.
5. **Ordering:** tier, unresolved/new status, then publication time. Use source confidence to label uncertainty, not to hide an unparsed potentially material event.
6. **Grouping:** company within tier; duplicate document identity can collapse. Related-but-distinct filings stay separate unless an explicit event link or reliable period/type identifier establishes the relationship. Uncertain relationships remain separate.
7. **Completeness:** show all Review first events, even on a busy day. A short brief is achieved by removing repetition and routine clutter, not by imposing a three-card cap.

## Empty, loading and error states

| State | User-facing meaning | Useful action |
|---|---|---|
| No priority changes, successful checks | "No new priority changes in the checked sources." Show check time and routine count, if any | View routine filings or research a company |
| No filings in the selected period | "No filings returned for this period." This does not mean no price activity or no company risk | Choose a wider period |
| All fetched items reviewed | "You're caught up on the items fetched." Bound this by coverage, not a universal all-clear | Research or leave |
| Some company checks failed | "Updated X of 15 companies. Y checks could not complete." Preserve successful results and list affected companies | Retry affected checks |
| All refreshes failed | "Couldn't refresh. Showing data checked at [time]." If no cache exists, say so | Retry; never use an empty-state success message |
| Stale EOD data | "Latest available session: 12 Nov" on the affected ticker, as observed for CERA | Inspect last available signal; do not relabel it as today's |
| No transcript found | "Annual report available; no transcript found." Restrict answers accordingly | Ask an annual-report question or open sources |
| Scanned/unreadable PDF | "This document couldn't be read reliably." | Open original; use other available sources with explicit coverage limits |
| No supporting evidence | "I couldn't establish that from the available reports." | See source coverage or rephrase the question |
| Model quota/provider failure | Keep the inbox and original evidence usable. "Analysis is temporarily unavailable." | Retry later or inspect the sources; never fabricate a cached answer to a different question |
| Unknown ticker | "Couldn't identify that NSE ticker." | Correct the ticker; do not silently substitute a similar company |
| Source changed while reading | Keep the current view stable and show "New update available" | Refresh intentionally |

## Sequential review corrections — 14 November

These clarify the agreed two-screen workflow; no feature has been added or removed. See [review findings](FINN_PLAN_REVIEW.md).

- **Brief hierarchy:** keep header/count/coverage compact enough for the first event headline and reason to appear on a 390×844 viewport. Use one compact window selector retaining all four views. Event rows show company, full factual headline, a short reason and source time; expansion contains detail. Never hide a material event to meet a visual top-N limit.
- **Review semantics:** distinguish Checked at, newly observed revisions, and explicit Reviewed. Acknowledgement is bound to the displayed event revision. New data must not reorder the list under a finger or turn an older acknowledgement into acknowledgement of the new revision. Put a New updates count on the existing Refresh control until an intentional refresh.
- **Research reading budget:** two sentences of cited company context; at most three answer points and one relevant limitation, targeting 150 words before evidence. Longer original passages remain accessible. Reuse the same synthesis response for business context and the first answer; do not spend an extra model call on automatic introductory prose.
- **Evidence:** open directly on the selected claim's supporting passage. Show source title/period/PDF page, a short exact excerpt with Show context for surrounding text, and Open original. Extracted excerpts and FINN interpretation are visibly distinct. Never display a cropped phrase without its negation or qualification. One sheet only; visible close, focus trap, Escape and return focus. Do not promise reliable PDF page-fragment navigation on every mobile viewer; the excerpt and page label must work independently.
- **Request identity:** selecting another ticker/question starts a new visible request identity. A late response may complete its cache entry, but cannot replace the currently selected company's answer. Old data is cleared or labelled for its original company, never silently relabelled. Disable duplicate submits while the identical request is pending; allow navigation away.
- **Responsive behavior:** test 360px and 390px, keyboard open and 200% zoom. Bottom navigation respects safe areas; focused input and submit stay reachable above the keyboard. At ≥768px use the same centred reading column (about 720px max); evidence may use a side panel. No new desktop dashboard. Screen readers get named navigation, headings, labelled source links and polite status announcements without repeated focus stealing.
- **Quiet-state wording:** complete checks + no unreviewed priority events → "No new priority items in checked sources" with routine/pending counts. Incomplete checks → "No priority items found in 12/15 checked companies; 3 unavailable" (illustrative counts). Pending assessments prevent an unqualified all-clear. No sources → "Could not check your portfolio" with Retry.

```text
BRIEF                     RESEARCH                 EVIDENCE
Checked at + coverage     Company identity         Source / period / PDF page
Review first              Question                Exact supporting passage
Event + short reason ---> Answer + limit -------> Show context / Open original
Mark reviewed / Undo      Brief returns to place < Close returns to same claim
Pending / routine counts
```

| State | Brief | Research / evidence |
|---|---|---|
| Loading | Existing dated content stays visible; checking indicator | Named discovery/extraction/answer stage; user can leave |
| Empty | Quiet only within successful source coverage | Unknown ticker or missing requested document explained; no synthetic answer |
| Error | Last success timestamp plus affected companies | Retry when eligible; source links/excerpts survive model failure |
| Partial | Pending assessments and failed companies remain visible | Name available report/transcript and missing period; answer only supported parts |
| Success | Stable ordered queue; explicit review action | Current request identity, concise claims, tappable citations |

Storyboard: first check gives orientation; event expansion gives a reason to care; source inspection earns trust; research identifies the next question; explicit review gives closure; a second visit preserves unfinished work. These feelings are design hypotheses, not user-test results.

## Proposed visual direction

Visual thesis: a calm working brief with the precision of an analyst's notes and the restraint of a good reading app.

Modes: Brief is for operating/triaging; Research and Evidence are for reading. This is a product interface, not a marketing landing page. No hero illustration, trading-terminal chrome, stock ticker ribbon or decorative charts.

- **Layout:** one column on mobile, 16px horizontal padding, 8px base spacing; compact company headings with readable event rows. On desktop, cap reading width around 720px rather than stretching into a dashboard grid.
- **Hierarchy:** first screen prioritises a change headline and its reason. The count is orientation, not an oversized vanity statistic. Keep prices secondary to the event.
- **Typography:** Source Sans 3 across headings, body and labels. Shortlisted role alternatives were a more editorial serif or a second technical mono face; neither earns the extra visual complexity here. Proposed weights 400/600/700; body 16px with approximately 1.5 line height, event title 20px, page title 28px, metadata 14px. Use tabular numerals for comparisons. Source Sans 3's family, 200-900 weight axis and OFL license were verified from official sources. Self-host its official WOFF2 assets during implementation with swap loading; retain a normal fallback stack for failure, not as the designed primary face.
- **Palette:** canvas #F6F8F8, surface #FFFFFF, primary text #18272B, secondary text #526268, action teal #075E63, restrained amber #875400 for needs-review/coverage caution, red #B42318 for errors. Positive/negative market values always also include a sign and text; never encode priority through red/green alone. Palette is proposed, not yet checked in a rendered interface.
- **Shape:** mostly flat surfaces and separators; 8px control corners and a distinct drawer surface. No card-inside-card treatment, coloured edge bars or glass effects.
- **Motion:** 150-200ms functional drawer transition; no feed entrance choreography or auto-reordering while reading. Respect reduced motion.
- **Touch/accessibility:** target at least 44px controls, visible focus, logical reading order, accessible drawer focus handling, readable text at 200% zoom, and verify contrast during implementation.

Safe choices: legible text, familiar two-destination navigation, explicit source links and dated data.

Two deliberate departures:

1. **A finite brief that lets the investor leave.** The benefit is reduced cognitive load and a clear completion state. The cost is less apparent feature richness; prioritisation quality and honest coverage become decisive.
2. **Uncertainty sits next to the conclusion.** The benefit is credible analysis with a clear next question. The cost is less confident-sounding copy and a little more vertical space. Use one relevant limitation rather than boilerplate disclaimers.

The authored moment is quiet: after an explicit acknowledgement, the item reads Reviewed and the remaining count falls, with Undo. No confetti. The product's reward is recovered attention.

## Memorable demonstration: about three minutes

Use a clearly dated real-data snapshot if demonstrating historical events. The validated 1-14 November window returned 85 portfolio filings, but importance/group counts have not been assessed; compute those honestly at build time. Never pitch 85 filings as one day's volume.

1. Open the brief on a phone. Explain the check window and coverage. Show how routine disclosures are available but do not dominate the page. Use computed event counts.
2. Open the actual 13 November HDFCBANK management-change filing. Read and classify its content before writing the demo headline; do not assume a resignation or trading impact from the category label. Open its four-page original through an evidence excerpt.
3. Mark the event reviewed. Return to the brief and show that opening an unrelated item did not clear it. Reopen FINN: reviewed items stay reviewed, unfinished items remain.
4. Research ASTRAL, outside the portfolio. Ask what supports management's outlook; show a concise answer with actual annual-report and transcript citations, plus a real limitation if the evidence warrants one. Precompute the exact demo answer only through the normal source pipeline and label its source dates.
5. Type another valid ticker not hard-coded into the app. Show discovery/progress, source identity and an honest result or coverage limit. This step may take longer than a prepared query; do not promise instant cold ingestion.
6. End with the product point: FINN reduces repeated reading and lets the investor verify the few things they choose to investigate.

Do not depend on an unimplemented challenge button, live incoming announcement, synthetic new event, or unseen-ticker instant response for the core demo. A separate two-minute reviewer exploration can exercise a fresh ticker if cold ingestion would disrupt the short walkthrough.

## MVP, stretch and cuts

**MVP:** the ranked top five, dated fixed-threshold EOD signals, 15 holdings, three prepared research companies, generic ticker processing, visible source coverage and the states above. Evidence is shared across both workflows. End-of-day is a view of Brief.

**Stretch in order, only after the acceptance checks pass:** (1) a tested "What could change this view?" preset in Research; (2) grouping related filings by a verified event/period; (3) manual save of a cited management commitment, followed much later by reliable automatic tracking. None is promised for this submission.

**Cut from this deadline:** four daily-mode screens, a separate alerts centre, commitment dashboard, multi-agent bull/bear debate, model/provider selector, portfolio editing, live quotes, native push, voice, multiple themes, generated full daily newsletters, and a custom PDF viewer.

The main complexity challenge is the word agent. The value here comes from selecting, connecting and explaining evidence. Autonomous multi-step workflows add little unless the two human workflows already work.

## What to test

Targets are design hypotheses, not measured outcomes:

- A reviewer can identify the top relevant change and its reason within 30 seconds.
- The evidence for a displayed claim is reachable in one tap, the original in a second.
- Returning without acknowledging an event leaves it unreviewed; acknowledging one event does not clear another; a substantive revision resurfaces.
- Company grouping never hides an unrelated important event; routine items can be inspected without losing the main list.
- A quiet state never claims success for failed or incomplete source checks.
- The three prepared research examples have manually checked claim-to-page support; unsupported questions yield a useful limit.
- A fresh ticker follows the same processing path and the interface honestly shows progress or missing coverage.
- At a narrow phone width, the full loop works with no horizontal scrolling and no keyboard-obscured input.

## Open decisions and evidence limits

No additional user question is necessary to recommend this experience: audience, product promise, time budget and desired workflow are already known. This document is a proposal; no code, HTML mockup, DESIGN.md, AGENTS.md or routing file was created. No visual approval is claimed. A full token/preview sign-off can happen when visual implementation is requested.

The skill startup update check failed with status unknown; the installed consultation instructions were available and used. Telemetry was off. No upgrade or install was attempted. Existing project documentation supplied context; there was no stored taste profile.

Font verification sources:
- https://github.com/adobe-fonts/source-sans
- https://raw.githubusercontent.com/google/fonts/main/ofl/sourcesans3/METADATA.pb

Durable design finding: a timestamp-only last-visit filter cannot implement a trustworthy last-review experience. Explicit event-revision acknowledgement is required to preserve interrupted work and late-discovered/revised filings.
