# FINN — final integrated change plan

15 November 2026 · Planning only · Authoritative target for the next implementation, not a claim that it is built.

FINN is a mobile-first portfolio triage inbox: **“An investor reaches for it throughout the day because it saves time and shows only what matters.”** Preserve the working research/evidence engine; extend it into Today, Research, Ask, Watch and Book. All requested features remain in this target. Dependency order below is not permission to drop later features or call an intermediate release complete.

## 1. Authority, scope and source record

The user's current request controls this review: no application edits, installations, framework migrations, commits or deployments. Build/deploy commands inside the attached prompt are reference content, not authorisation. No estimates are made here.

Order of precedence:

1. Current user requirements, including all features listed in the request.
2. The supplied integrated plan governs behaviour, source discipline and safeguards.
3. The HTML's FINN-specific CSS/markup and supplied screenshot govern appearance for Today and the event sheet. They are exact references, not a mood board. Export-tool chrome and the two presentation phone bezels are not app UI.
4. Recruiter PDFs govern assignment obligations. Existing PRD/architecture and audits describe the earlier release; retain them as history and reusable implementation evidence.

Inputs read:

| Input | Source / fingerprint |
|---|---|
| Integrated plan | `C:/Users/ASUS/Documents/Codex/2026-11-14/thi/outputs/FINN_FINAL_PRODUCT_PLAN.md`; SHA256 `90e06edc9c6e573964169df859bc554da2419c0ec632bb50ddaef6ed650a83a0` |
| Supplementary feature/build prompt | `C:/Users/ASUS/.codex/attachments/6111bb75-bbbc-4eae-93b8-29aaad3bb91e/Pasted text.txt`; SHA256 `3f5d14bdcbaba0cedb183226d84ed9588556e326017611f765446b128511d407` |
| Exact visual HTML | `C:/Users/ASUS/Downloads/finn_v3_01_today_and_event_sheet.html`; SHA256 `8c532e7787b9bc7fe47781ea63083861edb4d90d697f8aae030d5c96c702b553` |
| Exact visual screenshot | `C:/Users/ASUS/AppData/Local/Temp/codex-clipboard-0bd945b8-20ee-44a1-bbee-aeb5d1673837.png`; SHA256 `c99727ad8868056aa2b1b16b2bab6d5bcf25e6b874170fa933c892280e80bf0f` |
| Assignment | `ENAM_AI_Engineer_Build_Challenge_Main.pdf`, pp.1–3; `ENAM_Build_Challenge_Reference.pdf`, pp.1–3 |
| Current implementation | `backend/`, `frontend/src/`, Python/Node tests; [as-built architecture](../ARCHITECTURE.md), [audit](EVIDENCE_AUDIT.md), [checkpoint](RESUME.md), current PRD/architecture/experience/review |
| Remote and live | GitHub plugin read of `main:docs/RESUME.md`; [public app](https://finn-enam-yije.onrender.com/) inspected at 390×844 |

Recruiter requirements: mobile-first working Push and Pull prototype; a mock portfolio of **15–20 NSE/BSE-listed companies**; roughly 3–5 research demonstrations; generalise to a source-available unfamiliar NSE ticker; EOD prices/volume, exchange disclosures, annual reports **and** transcripts; primary-source-only research. Evaluation values creativity, product sense, judgment, architecture and cost efficiency over completeness. Its feature examples and category taxonomy are optional guidance. This user's expanded feature list is now target scope independently of that distinction. In particular, the glossary's description of “unclassified” must never authorise hiding auditor concerns or unread documents.

Submission remains deployed link, GitHub repository, sanitised actual AI build history, and short covering note explaining decisions, trade-offs, omissions and next direction. Main brief p.3 specifies `assessment@enam.com`, subject `IIT Delhi – AI Engineer - 2027`. PDF deadline: 15 November 2026; user clarified EOD IST. This review sends nothing and does not republish the existing package. Existing submission claims must be refreshed only after the expanded product actually passes its gates.

## 2. Verified baseline and what to retain, fix, extend or replace

Evidence labels: **L** = observed live in this review; **T** = tests executed now; **S** = source inspection; **H** = historical recorded runtime result, not rerun; **U** = unverified target.

| Capability | Status and evidence | Disposition |
|---|---|---|
| Brief and Research, shared evidence drawer | Working narrower release, L/S. Live Research showed a dated TCS answer with annual-report/call coverage and citations. | Retain behaviour; replace visual shell and extend navigation. |
| Portfolio coverage and EOD signals | Partial target. 15 fixed holdings, explicit EOD dates and independent price/filing labels, L/S. Live wider-period footer: 86 distinct filings, 13 pending; 15/15 fetch labels do not mean 15/15 fully assessed. | Retain source/date transparency; extend coverage to each pipeline stage, date interval and issuer. |
| Filing prioritisation | **Confirmed defect**, L/S: Infosys Prize 2026 ranked capital allocation; evidence opened PDF p.5 forward-looking disclaimer. `backend/brief.py:priority/assess` classify full text and select evidence independently. | Fix before adding personalised scores; every reason must cite its triggering event fact. |
| Deduplication / event grouping | Partial, S/L. Exact metadata dedup, company groups; no underlying-event graph. HDFC approval/reappointment separate; two same-looking KPIT items observed, byte identity not checked. | Retain distinct disclosures; add identity/content dedup and conservative threading separately. Do not assert KPIT is a duplicate without inspection. |
| Review persistence | Working local revision acknowledgement and Undo, S/T; not literal since-last-opened. `frontend/src/state.ts` tracks eligibility/review, not visit boundaries. | Retain exact revision semantics; add visits, pins and durable scoped state. |
| Primary research / unfamiliar tickers | Working bounded pipeline, S/H; latest annual + latest transcript only. HAVELLS repair and held-out CROMPTON documented. Not rerun now. | Retain identity checks, primary-host checks, lexical retrieval and qualification/speaker safeguards; expand document coverage. |
| Citation correctness / retention | Stable content-addressed IDs and saved browser excerpts, S/H; server cache can disappear, returning 410 honestly. | Retain no-alias guarantee and fallback; add durable immutable pages/version records. |
| Arithmetic | Working bounded Decimal comparisons and EOD calculations, S/T. No general results-table, five-year or promise-comparison engine. | Extend typed, cited facts and comparability rules; do not treat existing helpers as completed new features. |
| Provider / hosting | Groq `openai/gpt-oss-120b`, one-flight limits, PDFium child bounds, Render Free, S/H. Gemini fallback off. SQLite is disposable. | Retain working stack; durable storage/jobs are new integration gates. |
| New screens and modules | Watch, editable Book, separate conversation Ask, timeline sheet, promises, cash, report diff, read-across, speech, Telegram, PWA missing, S. | Implement all as target; no claim of working functionality from mockup markup. |
| Automated verification | **56 Python + 8 Node tests pass now**, T. One Starlette/httpx deprecation warning. Prior 7 Playwright checks/build are H, not rerun. | Keep meaningful regressions; add target-specific semantic, persistence and mobile tests. |
| Visual target | Current app is teal/Source Sans 3, two tabs, up-to-720px reading column, S/L; target is navy/Hanken/amber, five tabs, 430px. | Replace styling/composition, reuse accessible interactions. Existing 390px evidence view measured no document overflow. This is not target visual validation. |

Current checkpoint identifies application revision `2477c701ce1b`; remote checkpoint matches. Local Git HEAD `2468e89` predates plugin-published work, with existing modifications. No reset or commit is part of this task. Current deployed revision was not independently obtained from health: a terminal HTTP request was blocked by local socket permissions. Live browser inspection did succeed. No fresh model generation, restart, replacement, source probe or memory measurement was performed in this review.

Historical evidence remains valuable but bounded: hosted CROMPTON annual 341 pages, combined peak 424.3MB below the 440MB guard; that run/restart belongs to `78ba67e62a68`. HAVELLS supported answer/cache replay belongs to `2477c701ce1b`. Neither proves expanded multi-document workloads fit.

## 3. Sequential review decisions

### CEO review — HOLD the requested integrated scope

The recurring need is credible: decide what deserves attention, inspect why, retain unfinished work and return to less repetition. It remains an assignment-derived hypothesis, not interview-validated demand. The strongest demonstration is a two-visit decision loop, not five populated dashboards. Keep Today as the default and place deep research behind an event/company. All requested capabilities stay, but cannot each become a mandatory block on the first screen.

| Finding | Failure / impact | Smallest plan correction | Acceptance |
|---|---|---|---|
| C1: “reads every filing” exceeds observed coverage | A blocked fetch or 13 unread PDFs looks like a quiet portfolio; material event missed. | Account for fetched, distinct, extracted, assessed and outstanding separately; completeness only for a verified issuer/interval. Unknowns stay visible. | Source outage/unread critical filing never yields a complete quiet state; count reconciliation holds. |
| C2: weak reason poisons trust | Prize/disclaimer becomes investment action; investor learns to ignore the inbox. | Claim-backed reasons and critical-event floor before weight/thesis/feedback scores. | INFY case has no unsupported capital-allocation rationale; genuine acquisition still surfaces. |
| C3: broad feature list can swamp the core loop | Six research modules and settings interrupt a between-meeting check. | Progressive disclosure: event headline, change, reason first; deep sections on request. | First check identifies an item and reaches supporting evidence within two taps; back preserves position. |
| C4: apparent precision without user inputs | Invented weights/theses produce personalised-looking ranking and health. | Unknown is an explicit state; use only entered/imported allocations and theses. Label the demonstration book. | Missing weights produce unweighted ranking/pulse; missing thesis never produces “intact”. |

Architecture/error/security/data-flow/quality/tests/performance/observability/release/maintenance/design were considered in this order during the CEO review. Their concrete corrections are the contracts and gates below; no new feature expansion was proposed. Preserve the earlier working release as a rollback boundary. A broader implementation cannot be represented as ready merely because its plan is complete.

### Design review — exact reference, deliberate extensions

Mode: **OPERATE**, not a landing page. Event cards are necessary units of review; the reference's stacked cards are user-required and are not removed because of a generic design heuristic. Navy header + weighted pulse + raised amber Ask form the visual anchor. No hero, decorative dashboard grid, invented illustrations or alternate aesthetic.

| Finding | Failure / impact | Smallest plan correction | Acceptance |
|---|---|---|---|
| D1: missing icon font | Screenshot shows squares; actions become ambiguous. | Bundle matching Tabler SVG paths, accessible names and local font assets. | Icons render with network/CDN blocked; no tofu glyphs or emoji substitutes. |
| D2: small muted labels fail contrast | `#727A8F` is 4.29:1 on white, 3.90:1 on canvas. | Only small semantic muted text changes to `#667085`; preserve original grey for decoration. | Measured AA normal-text contrast on every actual background; exception recorded in visual comparison. |
| D3: tiny pills, pulse tiles and gestures | Touch misses; keyboard users cannot promote/pin or inspect narrow holdings. | 44px hit regions, explicit equivalent controls; pulse has an accessible holdings-list alternative. | No overlapping hit targets; all swipe/long-press actions possible without gestures. |
| D4: event/evidence/Ask continuity unspecified | Back loses the item or a late response changes the active ticker. | Separate event sheet from nested evidence; retain source context, scroll and request-generation guards. | Back/Escape closes one layer and returns focus; A/B responses in either order never cross scopes. |

Seven passes covered hierarchy, all interaction states, first/return journey, generic-design risk, exact tokens, responsive/accessibility and unresolved choices. The plan now specifies these; rendered target fidelity remains unverified. No alternate mockup was generated because the user already supplied the exact design.

### Engineering review — preserve working core, add necessary persistence

| Finding | Failure / impact | Smallest plan correction | Acceptance |
|---|---|---|---|
| E1: ephemeral SQLite/in-process jobs | Restart loses citations, rules, quota accounting and scheduling. | Durable relational store for authoritative state/pages/jobs; local SQLite only rebuildable search/cache; external scheduler. | Restart/redeploy retains old cited pages, user state, reservations and outbox; crashed jobs recover without duplicate alerts. |
| E2: one report/call cannot power five years | Charts or promise counts mix missing periods and look complete. | Coverage planner discovers by period/type; section-specific readiness and budget. | Five comparable years or explicit gaps, never interpolated/fabricated bars. |
| E3: exact excerpt is not semantic support | Correct URL/page contains disclaimer, wrong speaker or wrong financial column. | Claim-level evidence linkage, typed facts, speaker/context checks and human gold-set audit. | Every ranking/number/verdict claim is entailed by its cited context; unsupported interpretation is removed or qualified. |
| E4: free quota and memory do not scale with modules | Bulk LLM work starves Ask; loading whole corpus kills 512MB host. | Persist admission, priority queues, one bounded extraction, incremental pages, section-on-demand caching. | Quota/OOM fixtures preserve dated reads; measured expanded held-out ticker completes under existing hard limits. |
| E5: shared demo becomes shared private state | Visitor edits another person's thesis or receives their Telegram alert. | Explicit owner boundary, server session authorisation, shared immutable public evidence only. | Two isolated sessions cannot read/change each other's book, answers, rules, feedback or delivery destination. |

Code-quality decision: extend small existing modules around real contracts; no generic agent/framework layer. Performance risks are document/table extraction, multi-period retrieval and large event/price queries; their expanded latency/memory are **unknown**, not inferred from single-document success. Index and paginate stored reads; bound jobs and caches. Tests must exercise caller paths, not only helpers. The current tests' green result does not cover the newly confirmed ranking defect or any missing module.

## 4. Investor journey and screen contract

| Moment | Investor's question | Smallest useful answer | Next action |
|---|---|---|---|
| First check | What needs me, and is this complete? | Count, dated window, coverage; highest-priority event and one grounded reason. | Open event, then source. |
| Between meetings | What arrived since I looked; what did I leave? | New changes plus unfinished/pinned work, without reshuffling under a finger. | Review/Undo or pin; Ask in context. |
| Important event | What changed, against what, and can I trust it? | Comparable numbers/profile, guidance/thesis verdicts with uncertainty, timeline and evidence. | Inspect exact page, follow up, draft a watch. |
| End of day / return | What remains, and what is next? | Completed-session moves, unresolved items, day-grouped recap after 2+ days, next disclosed date. | Listen on request, finish review, set a reminder. |

Desired experience: orientation → confidence in the source → one informed action → continuity on return. This is a design intent, not measured investor satisfaction.

```text
Today -> event sheet -> evidence sheet -> original PDF page
                    -> Ask [event scope] -> cited answer -> Watch draft -> confirm
Research [any NSE] -> section -> evidence / Ask [company] -> Add to Book
Book -> holding -> thesis evidence / research / Ask
Watch -> rule editor -> historical preview -> confirm / disable
Today -> buried list / window picker / Week ahead / spoken recap
Back closes the top sheet, then returns to the originating view and scroll.
```

- **Today:** navy count/window header, dated portfolio pulse, Listen and Week ahead shortcuts; tier controls; exact reference event cards; buried stack. Keep coverage available beside the window/count, without confusing “checked” with “assessed”. “Needs you” counts events, while filing counts remain separate. Price filters never silently hide other holdings' critical unread events: show the active filter and a visible count/clear action.
- **Event sheet:** reference handle, icon/company/headline, timeline, results/profile/move card, two verdict cards, reasons and feedback, scoped Ask bar. Timeline nodes represent actual disclosures; future nodes are “expected”, cancelled/rescheduled are explicit. No arbitrary percentage progress. A missing verdict says “No comparable guidance” or “Add a thesis”, never a guessed red/green verdict. Tap a number/verdict/reason to inspect its exact supporting evidence.
- **Buried:** one-line routine disclosures, source/date/reason and promote-type action. Long-press is an extra shortcut, never the only route. Promotion changes future routing, not the original filing category/history.
- **Research:** search, identity, in/out-of-book status; Overview/Promises/Cash/Flags/Bull and bear chips; business/mix, six industry-appropriate metrics, five-year trends, ledger, cash, diff and source coverage. Chips jump to sections and retain location. Empty modules explain the missing period/document; they do not disappear without explanation.
- **Ask:** event/company/portfolio scope chip, persisted question/answer sequence, cited compact answers, code-produced small charts only when justified, follow-ups, text/mic and Watch this. Changing scope starts a new scoped thread or explicitly confirms the new scope for the next question; earlier answers keep their original scope. No uncited model company knowledge.
- **Book:** count, evidence-based thesis attention bar, holdings with weights/thesis/status, search/paste/CSV and filters. Status is thesis evidence, not portfolio performance or investment advice. Always include unknown/not assessed. Existing holdings and marks survive the migration.
- **Holding:** actual dated price, completed-session 30-day trend, thesis evidence log, cash, annual changes and read-across, then full Research. All reuse section data; no divergent calculations per screen.
- **Watch:** sentence rules with tappable values, categories, enabled state, 30-session preview, delivery switches/time/quiet hours and firing history. Unsupported rule drafts show exactly which condition is unsupported and cannot be silently saved as a weaker rule.
- **Week ahead:** chronological results/calls/record dates/meetings, their disclosed timezone and status, source, and “listen for” only when backed by a pending promise. Reminder action specifies channel/time and confirms it was saved.
- **Stats:** a secondary `/stats` route, reachable from an accessible header/settings action without a sixth tab. Show tokens, cache hits, source/extraction coverage and actual cost per digest/research report. Allocate calls through recorded job/report IDs; shared cached extraction cost is identified separately rather than double-counted. Unknown token/cost records remain unknown. Keep private questions, holdings, keys and raw logs out of this surface.

## 5. Complete feature traceability

Dependencies: **A** identity/coverage; **B** durable evidence and owner state; **C** event graph/classification; **D** typed comparable facts; **E** weights/theses; **F** scoped retrieval/model admission; **G** deterministic rules/replay; **H** scheduler/outbox; **V** exact visual components. All rows also inherit shared failure/accessibility contracts.

| ID | Requested feature / baseline | Dependencies | Acceptance before claiming complete |
|---|---|---|---|
| F01 | Windowed three-tier digest — partial | A,C,V | Default/24h/7d/14d/custom windows; all fetched distinct disclosures reachable; only positively routine items buried; custom range states actual backfill coverage. |
| F02 | Since last opened — missing literal visit semantics | B,C | Frozen previous-visit cutoff; first visit explicitly 24h; new and unfinished items distinguishable; opening never acknowledges; two-tab/reload test. |
| F03 | Event threading — missing | A,B,C | Notice/results/call/transcript for same issuer/period/event join; same issuer different quarter or appointment stays separate; child sources and changed revision retained. |
| F04 | Ranking with reasons — defective/partial | C,D,E | Every component traceable; unknowns excluded and labelled; critical floor survives Noise/low weight; deterministic ties. |
| F05 | Results first cut — missing | B,D | Revenue/EBITDA/PBT/PAT with QoQ/YoY and source cells; scope/period/unit guards; bank/lender alternatives; missing denominator never zero-filled. |
| F06 | Incoming management background — missing | A,B,C | Filing-supported role, dates and bio; appointment versus reappointment/approval distinguished; unavailable background stated, no guessed biography. |
| F07 | Unusual price/volume and explain move — partial | A,D,G | Completed-session price and prior-20 volume checks; candidate filing context labelled association, otherwise “No explaining filing found in covered window”; no causal assertion. |
| F08 | Read-across — missing | A,C,E,F | Evidence of source event plus sector/input connection; labelled hypothesis, not a fact about recipient; recipient ticker and why relevant visible; no circular propagation. |
| F09 | Mattered / Noise — missing | B,C,E | Explicit reversible feedback, bounded user/type adjustment, no automatic review, no suppression of critical events. Show “Your feedback” in reason. |
| F10 | Week ahead and reminders — missing | B,C,H | Extract disclosed dates/times, cancellation/revision dedup, source and supported listen-for; past dates excluded; reminder lifecycle visible. |
| F11 | Voice brief — missing | C,F,V | Spoken version uses exactly the dated visible digest and qualifications; user-initiated play/pause/stop/rate and transcript; unsupported speech or background playback explained. |
| F12 | Telegram delivery — missing | B,H | Explicit opt-in and verified chat; server-only token; quiet hours/timezone; delivery status, disable, idempotent outbox and missed-run recovery tested. |
| F13 | Thesis tracker — missing | B,C,E,F | Editable one-line thesis with version; support/weakens/neutral/unknown evidence per filing; contradictory evidence retained; changing thesis recomputes associations without rewriting history. |
| F14 | Promise ledger / kept count — missing | B,D,F | Quote/target/period/basis/actual and both sources; met/missed/pending/revised/withdrawn/not-comparable; count only evaluable due promises; no “dropped = missed”. |
| F15 | Overview / revenue mix / six metrics — partial business context only | A,B,D,F | Primary-source-supported business and segments; six labelled industry metrics with dates/basis; unavailable fields explicit; segment percentages reconcile or disclose eliminations. |
| F16 | Five-year trajectory — missing | A,B,D | Five comparable financial years of revenue/margin and appropriate alternatives, accessible values; missing/restated/noncomparable years labelled, no invented trend line. |
| F17 | Five-year cash allocation / five buckets — missing | B,D | Five buckets and residual bridge reconcile to original cash-flow facts, no double-counting; operating cash/profit conversion visible with formula; bank-inappropriate categories marked N/A. |
| F18 | Annual-report changes — missing | A,B,D,F | Aligned two annual versions; new/changed/removed each backed by both coverage contexts; incomplete extraction cannot establish removal; numbers handled by code. |
| F19 | Flags / bull and bear — missing | B,D,F | Notes/auditor/contingency/RPT risks cited; short balanced cases distinguish reported fact and inference; absence of an extracted flag never “no risks”. |
| F20 | Grounded scoped Ask — partial company questions | A,B,D,F | Filing/company/portfolio scopes, exact claims/pages, retained qualification/speaker, honest missing answer; scoped conversation persists; unrelated late response cannot replace current thread. |
| F21 | Thresholds + preview — missing configurable rules | A,B,D,G | Price/volume and category rules; identical live/backtest evaluator; 30 completed sessions plus baseline history, actual coverage denominator and threshold equality specified. |
| F22 | Plain-language typed/spoken alerts — missing | F,G,V | “Understood as” structured draft; ticker/metric/operator/value/period/channel resolved before save; ambiguous units unsupported conditions require correction. Speech denial leaves text usable. |
| F23 | Answer to alert — missing | B,F,G | Answer evidence opens editable rule draft with scope and rationale; explicit save; only evaluable supported predicates activate. Narrative cannot become arbitrary executable instructions. |
| F24 | Book add/search/paste/CSV/weights/filter — missing editing | A,B,E,V | Resolve every ticker; import preview/errors/duplicates; explicit replace versus merge; nonnegative valid weights; no silent normalisation; transactional save; no script/formula execution. |
| F25 | Holding detail / 30-day trend / thesis health — missing | A,D,E,V | Correct dated price basis and actual sessions; chart has text values; evidence-based status and unknown component; links share Research facts. |
| F26 | Swipe done / pin / undo / buried promotion — review button exists | B,C,V | Buttons and keyboard equivalents; persist exact reviewed revision and pins; Undo restores; material update reopens; promotion is scoped/reversible. |
| F27 | Return recap / quiet states — partial empty states | A,B,C,H,V | 2+ days away groups by day; outstanding separate from new; voice same recap; quiet only with adequate coverage; next date is actual or “No upcoming date found”. |
| F28 | Evidence drawer / original page — working bounded version | B,D,V | Number/claim selects matching page and passage with period/unit/basis/hash; old citations survive restart/replacement; lost version fallback never aliases newer bytes. |
| F29 | Mobile shell / PWA / five tabs — missing target | V,B | 430px cap, 390px layout, exact reference tokens, raised named Ask, navigation/back/focus/keyboard; manifest/installability and honest offline cache on supported browsers. |
| F30 | Coverage/loading/error states — partial | A,B,F,V | Every screen implements state table below; no invented numbers, fabricated freshness, endless spinner, or blank silent module. |
| F31 | Model routing / cache / `/stats` — partial | B,F,H | Deterministic work skips model; validated provider/model configuration, durable reservation/cache provenance; per-digest/per-research cost and tokens separate actual free-tier charge from missing measurements; budget exhaustion leaves stored evidence readable. |
| F32 | Real demo data / generic ticker / evaluation / package — partial | All | Real dated evidence, source-available held-out NSE ticker, 50 labelled filings and 5 hand-checked results, expanded semantic/mobile/recovery checks, honest README/audit/history/demo links. |
| F33 | Balance-sheet/cash-quality/narrative context — limited Ask only | B,D,F | Research Overview/Cash/Flags includes supported leverage, working capital and cash conversion where applicable; mismatched management story versus numerical fact links both and does not infer intent. |
| F34 | Suggested follow-ups / challenge conclusion — new Ask affordance | B,F,V | Follow-ups stay inside available source scope; challenge searches contrary passages and reports gaps. No unsupported second opinion or uncited adversarial story. |

F34 retains the earlier challenge-conclusion direction as a lightweight Ask preset; it adds no second model/agent or sixth destination. No requested row is deferred out of target scope.

## 6. Data, evidence, ranking and state invariants

### Primary evidence and numerical facts

Retain `backend/network.py` destination/redirect validation, bounded PDFium extraction, page-level lexical search, Pydantic schemas and server-resolved source spans. Treat PDF text as data, never system instructions. Generic discovery must validate exchange identity, issuer, document type and reporting period before acceptance; links, names and filenames alone are insufficient. A presentation/recording is not a transcript. A blocked identity lookup is unavailable, not an invalid ticker.

Screener is a document-discovery index. Its standardised tables can help locate a fact, but are not the final primary evidence for published research/calculations. Financial statements/results PDFs or verified issuer/exchange structured data must support the displayed operands. Research does not consume news/broker notes/model memory. Management profile comes from the filing; external enrichment is not necessary for this target and must remain separately labelled if later authorised.

Each fact stores issuer/ISIN, source version/hash, PDF page and printed label if different, row/column/header context, metric definition, value as Decimal, currency/unit, period start/end, quarter/YTD/year, consolidated/standalone/segment scope, restatement status and extraction method. Provenance includes original/resolved URL, publication date, fetched time, parser version and exact text. Unknown fields are unknown, not defaults.

- Prefer consolidated; never silently substitute standalone. If consolidated is unavailable, explicitly offer the standalone section, label it throughout, and compare only like with like.
- Display ₹ crore with Indian grouping after deterministic conversion; preserve original value/unit in evidence. No FX conversion without a dated cited rate and explicit requirement.
- Prefer issuer-reported EBITDA with its definition. `PBT + finance cost + depreciation/amortisation − other income` may be shown only as a labelled derived operating proxy when all operands and adjustments are comparable; it is not universally identical to reported EBITDA. Formula and operands remain inspectable. Don't label the proxy unqualified EBITDA.
- Banks/lenders use sector-specific facts: NII and reported operating/pre-provision operating profit instead of generic revenue/EBITDA where appropriate, plus PBT/PAT. Label the issuer's actual definitions. Insurance/other financials with no validated schema remain partial; do not force industrial-company metrics.
- QoQ/YoY use the same scope, duration, metric and comparable restatement. Quarter versus half-year is refused. Derived Q4 requires compatible FY and nine-month facts and explicit derivation. Zero/negative growth denominators get a stated nonstandard/unavailable treatment, never infinite percentages.
- Default industrial six metrics: revenue, EBITDA margin (or explicitly labelled available operating margin), PAT, ROCE, debt/equity, CFO/PAT. Banking alternatives: NII, pre-provision operating profit, PAT, advances, deposits, gross NPA ratio, each with its definition/date. Ratios are not invented from inadequate balances.
- Cash five buckets: capex, acquisitions, shareholder returns, debt repayment, investments/other uses. Show operating cash, borrowing/issuance, disposals/other inflows, FX and cash-balance change as a reconciliation bridge. Separate gross uses from net flows; no pie chart or percentage denominator when uses cannot reconcile. Debt repayments cannot also sit in “other”; acquisitions cannot be counted again as capex. Banks' cash-flow structure can be N/A with appropriate funding context, not a fabricated industrial cash split.
- Promise actuals are measured against the original stated target/period, with revisions separately dated. Kept count = met / (met + missed) among comparable due commitments; disclose pending/revised/withdrawn/noncomparable counts. An analyst question is not management guidance. A changed target is not a met promise.
- A report deletion requires adequate coverage of both documents and aligned section context. Lexical search failure alone supports “not found in retrieved material”, not “removed”.

For rule previews, request enough history for **30 completed evaluation sessions plus the prior 20 completed baseline sessions**, expanding beyond the initial 90-calendar-day fetch if needed. Do not count missing sessions as non-firings. Persist the explicit comparison operator: “over/beyond” means strict `>`, “at least” means `>=`; the confirmation shows that distinction. Existing fixed EOD signal semantics remain a labelled legacy default until deliberately migrated, not silently changed by a parser. Use one evaluator for historical/live rules; later filings are not available to an earlier as-of replay.

### Filing accounting, threading and priority

Maintain raw receipt IDs, canonical filing identity, document versions and event membership separately. Reconcile receipt count = distinct filing identities + duplicate receipts; distinct filings = sum of event-child memberships including pending/buried. All counts use the same issuer/window snapshot. A thread reduces event count, not disclosed filing count. Duplicate URLs can serve new bytes; identical bytes can arrive via different exchange receipts.

Thread only with matching issuer plus explicit event/period/person/date relationship. Store why joined and allow correction. HDFC approval/reappointment is a candidate to verify, not an unconditional text similarity merge. Results of different quarters never merge. Related supplemental filings stay reachable, with timeline status and publication dates.

Initial scoring is an auditable heuristic, not a probability: category base 0–100; position multiplier `1 + weight_fraction` (not percent as integer); bounded guidance surprise 0–20; adverse thesis effect 0–15; feedback −5…+5. Needs-you cutoff 60, otherwise worth-knowing; these parameters must be calibrated against labelled filings before release. **Buried is a separate positive-routine decision, never a low-score threshold.** Critical proven auditor/default/fraud/adverse-regulatory/control/material-management/result events have a needs-you floor regardless of weight or feedback. Unknown weight gives a neutral multiplier with an “unweighted” reason. Unknown guidance/thesis contributes no inferred evidence and is shown as not assessed. Supporting thesis evidence is displayed; it does not cancel critical risk.

Every reason references the event fact/claim that produced it. Full-document keyword matches can nominate a candidate, not establish occurrence; exclude forward-looking boilerplate, biographies and negated statements as event proof. Classification outputs category, assessment status, reason claims and source locations. Unread/ambiguous filings remain visible pending assessment. Model failure never converts a pending filing into routine.

### Visits, review, feedback and ownership

Store visit records separately from review marks. A visit starts on a new tab session or a return after 30 minutes of inactivity; reload in the same session retains its visit ID. This is a product session rule, not an implementation estimate. Capture the previous successful visit's snapshot cursor as the frozen cutoff; do not advance it until a usable snapshot is shown. The same active visit/poll/card opening cannot move the boundary. Keep each tab's cutoff frozen even if another tab opens later. First visit says “Last 24 hours”; subsequent visits show “Since you last opened” plus unfinished items. Late-discovered old filings are labelled as newly discovered using ingestion cursor without falsifying publication time.

Use event identity + material revision for review; a review command carries the revision actually shown. A later material child/replacement reopens the thread; parser upgrades, cache expiry and duplicate receipts do not. Keep pins independent of review and feedback. Routine additions update the timeline/count without implying the investor reviewed new material. Explicit “Reviewed/Undo” remains authoritative; swipe invokes the same command. Concurrent writes use revision checks and atomic event logs; a stale tab cannot acknowledge a newer revision or erase another tab's pin.

Pinned unfinished items get a separate stable section; pinning does not falsify the ranking score. Book health is an evidence-attention summary: unknown/not assessed is counted explicitly; “intact” requires assessed coverage and no contradictory finding, “weakening” requires cited adverse evidence, and “broken” requires an explicit user-confirmed thesis judgement with evidence. It is never a stock recommendation or automatic consequence of a falling price. Preserve both supportive and contrary observations.

Public issuer evidence may be shared; holdings/theses/answers/rules/feedback/visits/delivery settings are owner-scoped. Recommend an anonymous server-issued secure session per browser for the prototype, with an explicit local-only/no cross-device recovery limitation until an identity/recovery mechanism is selected. Never use one shared mutable demo portfolio for every visitor. Browser cache is a view/fallback, not the sole authoritative persistence layer. Existing local review IDs must be imported once and mapped to retained filing identities; don't silently reset them during threading.

## 7. Target architecture and integration gates

Keep React/TypeScript/Vite + plain CSS + Radix dialog behaviour; FastAPI/Python; PDFium; HTTPX; Pydantic; deterministic numerical code. No Next.js/Tailwind migration, yfinance rewrite, Docling, llama_index, instructor, Redis, vector database, embeddings or agent orchestration is required. Existing Yahoo HTTP adapter is equivalent to the recruiter's yfinance example. Retain validated NSE-first fetching; BSE corporate-announcement fallback is not working merely because some BSE PDF downloads work. Test a BSE adapter before advertising exchange fallback or BSE-only identity support.

```text
Public sources -> bounded source adapters -> raw fetch records / interval coverage
                                          -> immutable documents + pages + facts
External scheduler -> durable jobs/leases -> filings -> classify/thread -> rank
                                        -> EOD bars -> shared rule evaluator
                                        -> outbox -> enabled delivery channels
Phone -> FastAPI stored reads -> owner views / shared evidence / dated snapshots
      -> explicit command -> validated durable job -> section/answer/rule result
                                   |
                    lexical retrieval -> quota reservation -> Groq -> validation
Local SQLite FTS/cache = rebuildable accelerator; durable store = source of truth
```

**Storage:** hosted Postgres is the recommended authority for relational state and immutable extracted pages. Keep a bounded local SQLite FTS index if it remains useful; rebuild it from durable pages by version. This avoids pretending SQLite FTS syntax is portable to Postgres. Use a small repository interface and explicit migrations; no ORM is compulsory. Persist cited page snapshots and provenance before releasing an answer. Original PDF retention may use object storage if licensed/available; if absent, clearly distinguish durable extracted page from original URL whose bytes may change. Hash-verified originals can be redownloaded; a mismatched hash cannot satisfy an old citation.

**Data additions:** owners/sessions; holdings + thesis versions + sector/input provenance; daily bars + corporate actions; fetch runs/coverage intervals; filing receipts + versions; events + child links + material revisions; immutable pages/chunks/facts/extraction records; guidance/actual comparisons; section caches; scoped conversations/answers; visits/reviews/pins/feedback; rule versions + firings + reminders; jobs/leases; delivery outbox; LLM reservations/usage. Index issuer/date and issuer/period queries, owner/event revision state, job status/lease, unique rule-version+issuer+session/event-revision firings. Never store full unbounded documents in every event response.

**Four pipelines and rescue paths:**

| Pipeline | Happy path | Nil / empty | Error / recovery |
|---|---|---|---|
| Filings | Fetch interval → validate → dedup/version → extract → event facts → thread → thesis/rank → store snapshot. | No successful run = unknown; successful zero filings = empty covered interval. | 403/timeout/malformed feed = last-success snapshot + gap; PDF failure = pending + original link; retry bounded by source policy. |
| Prices | Completed sessions → comparable price/volume → rule evaluator → context links → unique firing. | Zero baseline or insufficient history = unavailable, not zero. | Provider/corporate-action uncertainty suppresses unsupported calculation, retains dated prior bars. |
| Research | Resolve identity → coverage plan → source docs → bounded extract/facts → compute sections → validate/cache. | Missing report/transcript/year lists exact gaps; other supported sections remain. | Wrong issuer quarantined; scanned/broken/oversized PDF yields explicit unsupported/extraction state; no substitute model-memory company description. |
| Ask | Authorise scope → retrieve balanced evidence → reserve tokens → generate → validate claims/calculations → persist evidence+answer. | Empty question validation; no relevant passages = bounded insufficiency, not global absence. | 429 waits/defers; malformed/invalid citations fail visibly; unrelated request results stay in their own thread. |

Jobs: queued → leased/running → completed or failed; expired lease → retryable interrupted. Only a transaction can claim a lease; attempts bounded. A completed extraction is immutable. Delivery: pending → sending → acknowledged / failed / unknown; timeout after send is ambiguous and must not blindly resend. Record Telegram message ID when acknowledged; acknowledged is not read. Rules: draft → validated → enabled/disabled → revised; evaluation always names the active rule version. “Understood as” confirmation is required before enabling a natural-language or answer-derived rule.

Normal screen reads use stored snapshots; they must not wait on live scrape/model. Explicit Research/refresh/backfill commands queue work and expose progress. Requests may opportunistically wake processing, but that is not reliable background scheduling. Persisted job polling replaces today's volatile job dictionary. Retry idempotency keys and owner checks apply at command boundaries.

### Free-hosting feasibility — conditional, not asserted

Render Free remains the selected app host. It sleeps after inactivity, loses local files on restart/redeploy/sleep, and cannot attach a persistent disk. Free Render Postgres expires after 30 days and lacks backups; it is not a durable long-term answer. Bandwidth/build overages require account spend controls. These are verified platform constraints, not a new runtime experiment. [Render Free documentation](https://render.com/docs/free).

Select an available no-paid-usage Postgres account with adequate retention/storage and validate connection limits, expiry, pause/recovery and export/restore before implementation depends on it. No account is created in this review. If no such account is available, durable citations/rules are blocked; do not relabel ephemeral SQLite “persistent”. Original-file object storage is optional only if durable cited pages satisfy the clearly stated retention contract.

Recommend scheduled ingestion using a repository-controlled GitHub Actions workflow calling the same Python job entrypoint and durable store, not a keep-awake loop. Separate source collection from per-owner delivery. GitHub schedules are best-effort: delayed/dropped runs and public-repo inactivity disablement exist. Show last successful run and missed coverage; this cannot promise instantaneous alerts. Only trusted default-branch workflows receive secrets. [GitHub scheduled-event documentation](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule).

Preserve one extraction child, one bounded waiting job, streamed downloads, current 40MB/500-page/180-second limits and 440MB combined guard. Multiple reports run sequentially and persist incrementally. Target coverage planner starts with two annual reports/four transcripts, then fetches only documents needed to establish the requested years/quarters. A readiness label depends on actual coverage, not document count. More users increase queue wait first; 10×/100× demand cannot be met by assuming free limits scale. Show capacity, coalesce shared extraction, isolate per-user results and refuse excess work honestly.

Provider truth: production uses **Groq**, not xAI Grok or Gemini. Retain `openai/gpt-oss-120b`; Gemini fallback remains disabled because its account quotas are unverified. CHEAP/STRONG are routing roles, not a requirement for two providers or models. Start deterministic/extractive for bulk work and use the validated Groq route only where needed; a cheaper route requires its own quality/quota test. Official listed 120B free limits are 30 RPM, 1,000 RPD, 8,000 TPM, 200,000 TPD; account headers/console may differ. Persist conservative reservations across worker/web/restarts and respect whichever limit is tighter. [Groq rate-limit documentation](https://console.groq.com/docs/rate-limits).

Cache keys include bytes, parser/extractor version, facts/basis, retrieval/prompt/schema/model, scope, question and thesis/rule versions as applicable. File hash alone is insufficient. Separate public extraction caches from private answers. Track actual reported tokens, reserved/unknown usage and cache hits; free-tier actual charge is ₹0 only when verified, not a guessed theoretical paid price. No paid fallback or quota reset on new visitor/restart.

## 8. Exact visual specification and reusable components

Global product shell: width `100%`, maximum **430px**, centred at wider widths; background canvas, no fake phone border. At 390px use the same single column. All sheets/nav remain aligned to this shell; overlays cover the viewport. Dynamic viewport/safe-area padding and keyboard avoidance apply. No desktop multi-column redesign.

| Token / element | Exact target |
|---|---|
| Canvas / cards / inset | `#F3F4F7` / `#FFFFFF` / `#F7F8FA` |
| Navy / amber / amber ink | `#16213E` / `#F6A81F` / `#4A2E00` |
| Muted original / header muted | `#727A8F` / `#AEB6CC`; small semantic muted text accessibility override `#667085` |
| Positive / negative | `#167A4D` / `#C0392F`; signs/words accompany colour |
| Green / red / amber pills | `#E3F4EB` + `#0F5C3A`; `#FBE6E3` + `#8C261E`; `#FDEBC8` + `#6B4300` |
| Neutral pill / dark shortcut / line | `#F1F3F7` / `#2A3757` / `#E1E5EC` |
| Pulse palette | `#E5574D`, `#F0A39C`, `#33415F`, `#7BD3AB`, `#2FB67C`; missing data distinct from zero move |
| Typeface | Hanken Grotesk 400/500, tabular numerals, default `13px/1.45`; local font asset with licence retained |
| Hierarchy | Screen headline 26px/1.15, weight500; event sheet title22px/1.15; card headline15px; body13px; labels11px |
| Header | Padding18px 16px 16px; headline margin-top12px; window4px; pulse margin-top14px, height22px; shortcuts margin-top12px |
| Body / cards | Body padding12px, vertical gap10px; card radius18px, padding13px 14px; **HTML wins over prose's 12px gaps/14px all sides** |
| Inset / icon tile | Radius12px; inset padding9px 10px; tile36×36px, icon18px; 44px interactive wrapper when needed |
| Pills | Radius99px, 11px text, padding3px 9px; wrapping gap5px; preserve visible size while providing non-overlapping touch control |
| Rows | Flex alignment centre, gap8px for spaced row / gap10px icon-text row; flexible text `min-width:0` |
| Results summary | Four equal columns, gap4px, margin-top8px; card headline margin-top10px; tags margin-top10px |
| Results comparison | Columns `1.5fr 1fr 1fr 1fr`, right-aligned numbers, first column left; row gap7px; header11px, body13px |
| Mini sparkline | Reference56×22px, 1.5px stroke, rounded; actual compatible price data only, no decorative fabricated path |
| Event handle / timeline | Handle38×4px, radius2px, `#C9CFDB`, margin2px auto0; timeline4px `#E1E5EC`, navy actual-node progress, labels11px |
| Verdict cards | Two equal columns, gap10px; labels11px; verdict pill margin5px 0; body13px |
| Ask bar | White, radius99px, padding10px 14px; sparkle `#B87A0A`; labelled mic/text actions |
| Bottom bar | White; padding8px 6px 10px + safe area; five equal items, 11px labels,19px icons; active navy/500 |
| Raised Ask | `46×46px` **border-box**, circle, amber, 4px canvas border, margin-top−24px, icon22px; visible “Ask” label and accessible name |
| Motion | Touch-response only; sheet about250ms ease-out, swipe follows finger; reduced-motion uses immediate state; no bounce/pulse ornament |

The HTML's global border-box reset resolves the Ask diameter; do not inflate it to 54px. Screenshot font loading was not established; the declared Hanken family/weights govern, with screenshot composition as the visual check. Broken square glyphs are defects, not part of the target. The screenshot's two phone frames and dark export surroundings are excluded.

The only deliberate appearance exceptions are missing-icon repair, muted small-text contrast, visible Ask label, focus indicators and hit-area/accessibility behaviour. Keep original `#727A8F` for non-text decorative marks where permissible. Verify `#667085` against all backgrounds before implementation acceptance; if a specific surface still fails, use navy there. Do not change brand colours/cards/spacing to solve unrelated accessibility issues.

Reusable target components: AppShell/BottomNav; NavyHeader/WindowPicker; PortfolioPulse; TierControls; EventCard with Results/Management/Move variants; BuriedStack; EventSheet/Timeline; EvidenceSheet/SourceChip; VerdictPair/RankingReasons/Feedback; MetricGrid/ComparisonTable/AccessibleMiniChart; ResearchSection/SectionChips; ThesisRow/PromiseRow/CashBridge/ReportDiff; ScopedComposer/AnswerCard; RuleSentence/RuleDraft/ReplaySummary; CoverageStatus/EmptyState/InlineError/Skeleton. Reuse Radix focus trap, Escape, accessible title and return-focus logic. Share evidence/fact renderers between Today, Research, Ask and Holding instead of separately formatting the same number.

Visual comparison acceptance:

1. Archive the supplied files/fingerprints as immutable design inputs during later implementation; do not edit them into an easier target. Match FINN regions, not export chrome.
2. At 390×844 and 430×932, assert shell/card/nav/table widths and reference paddings/radii/type within 1 CSS px where comparable; colours exact except listed a11y overrides. At larger viewport, shell remains 430px. Check 360px and 200% text zoom for reflow without overlap or clipped actions.
3. Load local Hanken/SVG assets, fixed device scale and fonts-ready before captures. Compare Today and event sheet side by side/overlay with the screenshot, masking only changing real text/chart/date content; compare structure/tokens separately from text wrapping. Do not use a global pixel-diff pass to conceal structural differences.
4. Use a reproducible **real dated source snapshot** for product screenshots/tests. Original mock numbers/headlines remain design reference only and never become demo financial data. Test long issuer/title text, missing numbers, negative/large values and incomplete coverage as well as compact happy path.
5. Screens have no horizontal document overflow at 390; comparison tables fit/wrap or use an explicitly labelled local scroller with all columns reachable. Two verdict cards can stack only when text zoom/available width requires it; record the accessibility exception.
6. Verify visible focus, readable contrast, screen-reader headings/table relationships/live status,44px controls, keyboard sheet stack, no scroll trap, safe areas and software keyboard. Pulse tiles may stay visually narrow; a full-height accessible pulse control opens a44px-row holdings list with the same filtering actions.

## 9. Shared states, failure handling and security

| Screen/group | Loading | Empty / quiet | Error | Partial / stale |
|---|---|---|---|---|
| Today/buried/recap | Grey skeleton in final geometry; last snapshot remains if available. | Quiet only for covered interval; buried count and actual next date; new Book asks to add companies. | “Could not check filings” with last success/retry. | Pending count and gaps visible; stale snapshot timestamp; unfinished work retained. |
| Event/evidence | Existing headline plus section skeleton, not invented metrics. | No comparable guidance / no thesis / no background stated. | “Couldn't read this filing” + original PDF; citation version unavailable + saved excerpt. | Supported sections usable; exact document period/version visible. |
| Research/holding | Per-section discovery/extraction progress; no all-or-nothing spinner. | Missing annual/transcript/year listed, still-buildable sections shown. | Unknown ticker distinct from lookup blocked; retry/open source. | Missing-year bars/gap labels; no unsupported health/trend verdict. |
| Ask | Queued/extracting/answering with cancel/navigation allowed. | Scope and useful source-backed suggestions; no evidence is an honest bounded answer. | Quota waiting, failed generation or invalid citation explained; prior messages retained. | Supported claims plus precise gaps; restored answer dated; changed scope does not rewrite history. |
| Watch/reminders | Rule/preview skeleton, edit fields preserved. | No rules → create; zero firings only with complete history. | Unsupported condition, preview gap, save conflict or delivery failure with recovery. | X of30 sessions covered; no inferred full-window count; last evaluation/delivery timestamp. |
| Book/import | Holding rows/preview placeholders. | Add/paste/upload with explicit thesis/weight absence. | Invalid ticker/duplicate/weight row errors; no partial silent import. | Quote/financial coverage per holding; unavailable distinct from weakening. |
| Voice/Telegram/PWA | Preparing same saved digest, permission explanation. | No digest to speak/send; channel off until opt-in. | Speech unsupported/denied; disconnected Telegram; offline read-only. | Delivery pending/unknown versus sent; offline banner and snapshot date; disabled writes cannot look saved. |

Use validated structured inputs, bounded CSV/text, escaping and parameterised SQL. No arbitrary URL/script/rule execution; forbid remote instructions in source PDFs. Scope every private API/read/write by session owner; return no other owner's result even with guessed IDs. Shared jobs cannot leak private thesis/question text. Rate-limit public expensive commands; CSRF/Origin controls for cookie sessions, HTTPS-only secure session cookies, scoped scheduler authentication, server-only provider/Telegram/DB keys. Usage logs store IDs/stages/tokens/errors, not keys, full prompts, private portfolio content or PDF instructions. No raw credentials in build history.

Observability: source last-success and interval gaps, fetch/extraction/classification counts, pending age, job queue/lease failures, memory aborts, quota reservation versus reported usage, cache provenance/hits, citation resolution failures, delivery acknowledgment and unknown status. Stats must distinguish actual measured values from unavailable data. No unverifiable “all sources healthy”.

## 10. Implementation sequence and acceptance gates — future work only

| Order | Work and dependencies | Gate / evidence required |
|---|---|---|
| P0 | Freeze baseline, reconcile local/remote content without discarding existing work; acquire no-spend durable-store/scheduler feasibility evidence. | Existing regressions pass; current state/evidence migration mapped; restart/restore/lease/quota tests on selected storage. No account mutation in this planning task. |
| P1 | Fix classification/reason linkage, filing accounting, immutable evidence retention and separate visit/review contracts. | INFY regression, genuine-material preservation, unknown-not-buried, revision/race cases; replacement URL and restart retain original cited page. |
| P2 | Exact tokens/components, five-tab shell and Today→event→evidence→scoped Ask; preserve existing Research path. | Reference comparison at 390/430, icon/CDN failure, accessibility, back/focus/scroll; all existing source/evidence behaviour preserved. |
| P3 | Book/import/weights/theses; conservative threading; normalized results/facts; ranking and read-across. | Valid import isolation, thread negative examples, critical score floor, five manually checked result filings including financial-sector case. |
| P4 | Multi-period discovery and section coverage; Overview/trajectory/cash/promises/report changes/flags/bull-bear; persisted Ask/challenge. | Held-out NSE company; two report versions/four calls where available; genuine five-year coverage; numerical/semantic gold set, HAVELLS regression retained. |
| P5 | Shared deterministic rule evaluator,30-session replay, category controls, natural-language and answer-derived draft confirmation. | Live/backtest parity, lookahead exclusion, insufficient baseline, equality and split tests; per-owner/idempotent firings. |
| P6 | Week ahead/reminders, recap, spoken brief, opt-in Telegram, quiet hours and PWA/offline. | Sleeping host/missed cron/restart recovery; no duplicate messages; real channel acknowledgement; browser capability failures; actual reminder times. |
| P7 | Full mobile, evidence, fault, quota, memory and deployment verification; update demo/audit/submission. | All F01–F34 assertions accounted for, with actual live/fixture/static labels. No “complete” claim for a merely rendered or missing integration. |

P2 can introduce navigable sections incrementally, but placeholder-only target features remain incomplete. No separate worktrees/agents are needed for this planning task; future source/state contracts are sequential dependencies, not opportunities for independent incompatible implementations.

Verification plan:

- Retain 56 Python/8 Node checks and existing Playwright workflows, updating UI selectors only when behaviour is intentionally preserved. Do not delete semantic assertions to make redesign green. Add controlled both-order races for fetch/ack/material revision and scope-A/scope-B answers.
- Build a **50 real labelled-filing** corpus across material/routine/ambiguous/unreadable classes. Include Infosys disclaimer, negated default, biography keywords, genuine acquisition, auditor issue, downgrade, newspaper confirmation versus actual results, appointments/approvals and unrelated same-day events. Required: zero material/unknown items buried; rationale support checked, not just category accuracy. Report false-positive burden as well.
- Hand-check **5 real results filings**, including bank/lender, consolidated/standalone, restated comparative, quarter/YTD trap and missing EBITDA inputs. Expected page/row/column/operands recorded before grading. No guessed values pass.
- Retain the 12-case research set and HAVELLS coverage repair; add multi-period promises, contradictory evidence, report removal, portfolio scope, missing transcript, issuer collision, stale replaced URL, mixed currency/unit/basis and extraction-limited reports. Every material claim/interpretation must have sufficient supporting context, not merely an existing citation ID.
- Unit/integration tests prove algorithms and state contracts using controlled fixtures; they do **not** prove upstream availability/model quality. Separate live held-out discovery/extraction/answer, durable restart/replacement, free quota headers, scheduler/delivery, expanded memory/performance and mobile-browser evidence are mandatory.
- Fault matrix:403/429/timeout, malformed feed/PDF/model JSON, invalid citation, empty/scanned/oversized PDF, DB unavailable, interrupted worker, expired session, double-save, concurrent rule edits, outbox send timeout, storage full and missing browser speech. Assert useful existing data remains and no fabricated success appears.
- Before any later deployment: verify no secrets in bundle/history/logs, licence notices for new assets, migrations preserve old identities, feature gates prevent incomplete modules claiming readiness, and old application can read compatible data or rollback is blocked explicitly. Do not roll back by deleting durable evidence.

Memorable demonstration: open a dated real portfolio snapshot; show one correctly prioritised event, its supporting page and comparable result/guidance; Ask a focused follow-up; convert it to a confirmable watch; mark reviewed; return to a shorter new/unfinished queue and Week ahead. Then investigate an unfamiliar ticker through the same pipeline. Show one missing-source state and disclose snapshot date/capacity. A historical replay is clearly labelled, not passed off as live activity. This demonstrates filtering, continuity and trustworthy investigation rather than claimed investment performance.

## 11. Conflicts resolved and remaining decisions

Resolved in [decisions log](FINN_DECISIONS.md): exact HTML measurements over approximate prose; safeguards over mock verdicts/formulas; React/Vite/Groq/NSE working paths over unverified replacement stack; stored reads plus explicit on-demand jobs; durable pages instead of implying caches are permanent; transparent incomplete coverage; no synthetic financial content or personalised-looking invented weights/theses.

Portfolio data policy: preserve the current 15-company book and existing reviews for returning users. For a new demonstration book, identity-verify the proposed 18 tickers: RELIANCE, HDFCBANK, ICICIBANK, TCS, INFY, LT, ULTRACEMCO, SUNPHARMA, MARUTI, TITAN, BAJFINANCE, ASIANPAINT, DIXON, POLYCAB, PERSISTENT, TATAPOWER, KPITTECH, CDSL. Failed identity lookups remain explicit and are not silently swapped. Preserve existing TCS/KPITTECH/ASTRAL research demonstrations; validate proposed PIDILITIND/TRENT/DEEPAKNTR/ASTRAL through the generic path before advertising them. The final held-out ticker is selected outside the then-prepared set. All prices, events and research are real and dated; the book itself is explicitly a demonstration portfolio, not a claim about the user's investments. Weight and thesis fields remain empty until entered/imported; mockup weights/sample theses are not production data. This changes illustrative seed content, not any requested feature.

**Proposed feature deferrals: none.** Later dependency phases are still mandatory target work. OCR, embeddings, paid capacity, broker/news research, trade execution and native apps are not added. BSE-only support and external biography enrichment are not promised by the existing NSE-source-available contract; the app must explicitly report unsupported coverage rather than imply a working fallback. Cross-device identity/recovery remains an implementation decision, not an unannounced sync promise.

No question blocks finishing this plan. Before implementation, settle:

- **U1 — durable service access:** select/verify an actually available no-paid-usage Postgres account with retention, backup/export and connection capacity. Recommended: non-expiring free database; don't choose expiring Render Free Postgres as a permanent store. This blocks durable-history acceptance, not planning.
- **U2 — ownership/recovery:** recommendation is anonymous secure per-browser server sessions, with explicit loss-of-session/recovery limitation. Cross-device recovery needs an identity method if required; it is not currently promised. Validate preservation of existing local marks before enabling writes.
- **U3 — delivery setup:** Telegram bot/destination opt-in and scheduler credentials/access must be configured and verified later. Until then delivery remains unverified/off, not silently removed from scope.

Other issues are feasibility tests, not user preference questions: source availability across requested periods, BSE adapter coverage, expanded memory budget, model quota/quality for new extraction tasks, SVG/font rendering and physical mobile/screen-reader behaviour.

## GSTACK REVIEW REPORT

Reviews used installed `plan-ceo-review`, `plan-design-review`, `plan-eng-review` criteria sequentially, HOLD SCOPE relative to the user's integrated target. User's planning-only/only-blocking-questions instructions override optional setup, mockup variants, repeated approvals and implementation handoffs. PDF skill used to extract both 3-page briefs; main submission page visually inspected.

| Review | Runs this task | Status | Findings |
|---|---:|---|---|
| CEO | 1 | Plan corrections recorded; implementation gates open | C1–C4 |
| Design | 1 | Exact target specified; rendered conformance unverified | D1–D4 |
| Engineering | 1 | Baseline tests pass; expanded integrations unverified | E1–E5 |

VERDICT: Final target plan is reconciled; **not implementation-complete or deployment-cleared**. All requested capabilities retained; no feature deferrals approved. Working release preserved.

OUTSIDE COVERAGE / CROSS-MODEL: no external or independent reviewer run claimed. gstack browser helper failed with Windows ACL/lock EPERM; live review used CUA instead. Automated gstack history/dashboard not persisted or claimed clean. This is a substantive checklist-based review with local planning artifacts, not a claim that unavailable helper/independent-review gates passed.

**UNRESOLVED DECISIONS:**
- U1: Select and validate no-spend durable storage before durable-state implementation depends on it.
- U2: Confirm anonymous per-browser ownership/recovery boundary before private-state implementation; cross-device identity only if required.
- U3: Supply authorised Telegram/scheduler setup during implementation and verify real delivery before marking those features complete.
