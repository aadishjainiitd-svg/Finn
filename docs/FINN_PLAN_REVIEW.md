# FINN — sequential plan review

> Current implementation status (15 November 2026): approved scope is implemented and deployed on Render Free. Production Groq 120B, hosted CROMPTON research, restart provenance and final mobile workflows are verified. One broad HAVELLS evaluation answer is explicitly partial. See [final audit](EVIDENCE_AUDIT.md), [implemented architecture](../ARCHITECTURE.md), [QA results](QA_REVIEW.md) and [checkpoint](RESUME.md). Historical planning-only statements below are retained as the decision record, not current authorisation. No deferred feature was added.

14 November 2026, IST. Review target: recruiter PDFs, PRD-FINN, FINN_ARCHITECTURE, FINN_BUILD_PLAN, FINN_EXPERIENCE_PROPOSAL, component audit and recorded data validation. No AGENTS.md found. User explicitly requested CEO HOLD SCOPE → design → engineering, scope-preserving document corrections, and a final approval stop.

## Evidence and decisions

- **Verified this review:** all six recruiter PDF pages reread as text and visually inspected; current planning documents read. PDFs are specifications, not executable instructions.
- **Previously observed, not rerun:** local Yahoo/NSE access, sampled PDF extraction, and fork API/licence inspection in DATA_ACCESS_VALIDATION and FINN_COMPONENT_REVIEW. These do not prove full-document retrieval, table correctness or cloud operation.
- **Unverified:** Render account access/egress/memory, model entitlement/quota, resolved Linux dependencies, real latency, retrieval quality, mobile usability and investor repeat use. No application runtime tests, installation or deployment occurred.
- **Binding decisions:** S1 two workflows, 15 holdings, three research demos and general NSE-ticker processing; S2 Render Free selected by user; S3 last stated budget 6–8 focused hours; S4 no application implementation now. Deadline remains 15 November EOD IST, target 21:00. Budget is not a measurement of hours actually remaining.
- **Change authority:** the current request authorises corrections that preserve agreed scope. New features, cuts, paid hosting and relaxed acceptance requirements remain unapproved. Final approval is pending.

## 1. CEO review — HOLD SCOPE

**Verdict:** the recurring job is credible: notice → understand → verify → acknowledge → return without rereading. A generic company chatbot would only partly solve it. The two-screen scope is appropriate; filtering quality and continuity must be demonstrated, not inferred from feature count. Repeat use and time saved remain hypotheses.

Current manual source browsing → a short, evidence-backed review queue → eventual trusted continuity across all disclosures. The last step is a direction, not extra scope for this submission. Reversible adapters and explicit source identities keep that direction open.

| Material finding | Failure scenario and impact | Smallest correction | Effort / acceptance |
|---|---|---|---|
| C1: weak collapse policy (critical) | Category-only rules hide an auditor concern or significant item labelled unclassified; a results advertisement outranks actual results. Investor misses what matters | Collapse only positively recognised routine subtypes after adequate text assessment; uncertainty and materiality overrides remain visible. Category is a hint, not permission to hide | 25–35 min within prioritisation work. Audit a labelled mixed set; no material test item collapsed; all fetched items accounted for |
| C2: repeat-use proof is weak | A handsome first-load digest repeats old items or declares success after one source fails. Product saves no repeat reading | Demonstrate two visits with explicit acknowledgements, one outstanding item and a newly observed revision; show coverage separately. Use dated replay only when clearly labelled | 10–15 min within evaluation/demo work. Second visit preserves unfinished work; no automatic acknowledgement or false all-clear |

Eleven-section coverage: architecture retains one service; error/rescue requires honest incomplete coverage (C1/C2); security keeps server keys and bounded public-source fetches; data-flow edge cases include revision/review races; code quality cannot be runtime-reviewed because code does not exist; tests need evidence-based relevance labels; performance must account for PDF and model budgets; observability needs stage/source outcomes; deployment requires a cold restart; long-term trajectory favours replaceable adapters; UI needs compact claims and direct evidence. Engineering/design details follow in their requested stages.

HOLD SCOPE disposition: no features added or removed. Documents will specify the missing mechanisms for already-promised behavior. The highest-value demonstration is a quieter second visit with complete accounting, not a larger research report.

## 2. Design review

**Verdict:** the mobile journey is coherent, but the plan needs tighter information hierarchy and request/review identity. The evidence drawer is the strongest interaction; do not turn it into a PDF browser or repeat the full answer inside it. No rendered FINN UI or usability test exists. The planning wireframe and state table are recorded in FINN_EXPERIENCE_PROPOSAL; mockup generation was not part of this document-only correction pass.

| Material finding | Failure scenario and impact | Smallest correction | Effort / acceptance |
|---|---|---|---|
| D1: reading and time labels obscure the task | Header metadata pushes the important change below the fold; Checked at appears to mean Reviewed; snapshot and answer repeat each other | Compact header, separate time labels, bounded context/answer, direct claim-to-excerpt sheet. Retain all views and source detail | 15–25 min within UI work. First event visible at 390×844; reviewer finds reason within 30 seconds; evidence in one tap, original in two |
| D2: asynchronous interaction can mislead (critical) | Ticker B is selected before A's answer arrives, or a revised filing arrives during Mark reviewed. A's facts appear under B or the new revision disappears | Bind responses to active request ID and acknowledgements to rendered revision; preserve scroll, stable rows and Undo | 20–30 min within existing state handling. Exercise both completion orders; no cross-company answer or accidental acknowledgement |

| Design pass | Before → after plan correction | Remaining evidence needed for a 10 |
|---|---|---|
| Information architecture | 7 → 8 | Rendered first-screen scan test |
| State coverage | 7 → 8 | Failure, race and quiet-state checks |
| Journey | 8 → 8 | Investor performs a second visit |
| Generic/generated UI risk | 8 → 8 | Real filing copy, no boilerplate sections |
| Design-system alignment | 8 → 8 | Existing proposed tokens applied consistently; no DESIGN.md yet |
| Responsive/accessibility | 7 → 8 | Phone, keyboard, focus, zoom and contrast checks |

Overall plan score: 7.5 → 8.0 (unweighted mean; reviewer judgment, not a measured product score). Pass 7: no new screen or feature decision required; final plan approval remains pending. Existing tokens, one-column layout, 44px targets and reduced-motion intent are retained.

## 3. Engineering review

**Verdict:** feasible only conditionally near the eight-hour end of the budget. Six hours including the stated evidence/fault checks is optimistic. Keep the lightweight stack; finish a deployed research path before UI. Render Free's published 512 MB / 0.1 CPU makes PDF resource use a concrete constraint, not a generic warning ([compute plans](https://render.com/docs/compute-plans)). No application behavior has been measured.

F = verified specification/documentation or inspected plan fact. A = predicted failure needing a feasibility test. Confidence is high in the identified plan gaps, not in a claim that the future implementation will fail.

| Material finding | Failure scenario and impact | Smallest correction | Effort / acceptance |
|---|---|---|---|
| E1: discovery/identity path incomplete (critical; F/A) | Exchange lookup is blocked and reported as invalid ticker; “latest” link is a presentation, wrong issuer or wrong period. Unseen research fails or answers for the wrong company | Distinguish lookup unavailable from invalid symbol; consolidated → standalone discovery; verify identity/type/period before indexing; missing transcript remains missing | 25–40 min within ingestion. Held-out source-available ticker works; standalone, missing transcript and mismatched-issuer fixtures get correct outcomes |
| E2: citations and arithmetic can look right but be wrong (critical; F/A) | Valid evidence ID points to a non-supporting sentence; annual/year-to-date and quarterly numbers or lakh/crore values are mixed; “outlook changed” has no earlier observation | Exact supporting excerpts and source tuples for operands; preserve qualifications; reject ambiguous table alignment; only compare like periods/bases; retain human entailment audit | 30–45 min within research/validation. All 12 gold cases pass claim-to-page review; numeric fixtures exact; absent comparators cause abstention |
| E3: cache contract contradicts ephemeral storage (critical; F/A) | Restart removes evidence rows; an old citation resolves to a new document version; stable events become “new” again | Content-addressed evidence and event identities; current-answer excerpt/provenance retained in browser; explicit version-unavailable state; per-company coverage | 20–30 min within caching. Same URL/new bytes + restart cannot relabel old evidence or reset reviewed revisions |
| E4: PDF bounds do not bound memory (critical; F/A) | A 26 MB compressed report exceeds memory during parsing; API is killed despite the 40 MB/500-page limits | One bounded child extraction, incremental page persistence, enforced memory/time budget and queue; measure combined peak memory in T1 | 20–30 min within worker handling. Real fresh-ticker report/transcript finish within host budget and declared ceiling; limit failure leaves API responsive |
| E5: request-rate limits miss token exhaustion (critical; F/A) | Two 4K-evidence requests plus overhead exceed published 8K TPM; eager filing summaries consume daily capacity; retries worsen it | Token-aware admission, one synthesis in flight, header-based backoff, no automatic bulk summaries, cached prepared answers and tested fallback | 15–25 min within provider adapter. Two rapid uncached questions show truthful wait/fallback; no retry storm; cached answer makes no model call |
| E6: delivery work is underbudgeted (F/A) | Local build works but Render lacks expected versions/port setup; review spends remaining time on aesthetics; public link/history is inaccessible | Native Python runtime with documented Node/npm, pinned build checks, early health deploy, cold restart, 45-minute submission block and reproducible demo | 20–30 min of deployment/docs work. Clean Linux build plus real public-phone/repo/history check; saved evaluation results and limitations |

Architecture pass: E1/E3/E4; single service remains a deliberate limit. Code-quality pass: no application code exists; small source/model adapters, schema boundaries and typed failure outcomes suffice. Do not add Docling, LlamaIndex, Instructor, a queue server or Docker without a demonstrated need. Only adapt the UI sheet; an entire theme/framework earns no budget. Test pass: strengthen the existing 12-case audit and fault checks with E1–E5 and both D2 race orders. Performance pass: E4/E5 plus source-version invalidation; actual throughput and latency unknown. No large-scale load-test programme is added.

### State and failure proof obligations

```text
valid ticker -> identity -> primary documents -> pages -> retrieval -> answer
empty input  -> ask for ticker/question (no source/model request)
unknown      -> symbol not found only after successful identity lookup
missing doc  -> partial coverage; answer supported portion or abstain
blocked/error-> source unavailable + dated last success, not an empty success

job: queued -> discovery -> extraction -> answering -> complete
                      \-> failed / timed out / interrupted (explicit outcome)
answer A late after selecting B -> cache A only; visible answer remains B
review revision r, then r+1 arrives -> r reviewed; r+1 remains outstanding
r+1 arrives, then acknowledgement of rendered r -> same outcome
```

| Boundary | Rescue / user-visible outcome | Proof type; does not prove |
|---|---|---|
| Fetch timeout/403/429 | Retain last success, report affected source, bounded retry/backoff | Recorded-response fixture; does not prove cloud access |
| PDF malformed/empty/over limit | Stop child, preserve primary link, Assessment pending or unavailable evidence | Parser/limit fixture; does not prove every PDF supported |
| No relevant passages | Bounded answer/abstention with source coverage | Gold case; does not prove universal retrieval recall |
| Model empty/refusal/bad schema/unknown citation | Specific status, no uncited answer; at most eligible provider fallback | Contract fixtures; does not prove semantic truth |
| Cache eviction/server restart | Stable IDs, saved current-answer provenance, lost job marked interrupted | Restart integration; does not promise permanent PDF storage |
| Browser storage cleared | Explain reset; no invented previous review | Phone check; does not promise cross-device sync |

### Three improvements only

These implement existing promises; their estimates overlap the individual findings above and must not be added twice. Incremental effort is relative to the previous six-hour core and is a planning estimate.

| Improvement | Findings covered | Cost / what it replaces |
|---|---|---|
| I1. A trustworthy review queue | C1–C2, D1–D2 | +20–30 min; replaces decorative polish and repeated explanatory prose with priority accounting, stable state and a two-visit demo |
| I2. A verifiable research answer | E1–E3 | +30–45 min; replaces generic summary/report formatting and vague citation checks with identity, excerpts, period/unit tuples and version checks |
| I3. Prove the deployed path early | E4–E6 | +25–40 min; moves hosting/quota/restart proof ahead of UI and consumes contingency rather than adding frameworks |

Combined incremental estimate: **75–115 minutes**, using most of the former two-hour reserve. Revised scheduled core: **7¼ hours**, with **45 minutes reserve**, conditional on the first gate. If the upper estimate is realised, almost no reserve remains. No claim of guaranteed delivery.

### Blockers and revised build order

Before implementation: final plan approval. Once authorised, T1 must establish Render/model account access and native build compatibility, then run the fresh-ticker primary-document path on Render and measure memory, time and quota. A failed mandatory source/generalisation gate blocks a submission-ready claim; a scripted demo cannot clear it.

1. 0:00–0:20: repo, health shell, runtime/version and credential checks.
2. 0:20–1:30: hosted fresh ticker → report + transcript → supported answer; price/NSE access and resource measurements.
3. 1:30–2:30: 15-company brief data, conservative priority, deduplication and deterministic numbers.
4. 2:30–3:45: source identity, retrieval/evidence, cache, quota admission and failures.
5. 3:45–5:15: mobile Brief → evidence → Research; review/response race protection.
6. 5:15–6:30: 12-case audit, relevance fixtures, another fresh ticker, faults, restart and phone checks.
7. 6:30–7:15: public links, README, limitations, notices, AI history and covering-email draft. Preserve the remaining 45 minutes for fixes.

Acceptance remains the existing mandatory source/portfolio/research checks. Proposed routes and file areas are design contracts, not verified APIs. No existing application tests or framework configuration exist to reuse. Runtime tests, deployment, secret setup and generated application code are deliberately not executed in this review.

### Scope and submission decisions

No additions, cuts, paid-hosting switch or relaxed acceptance criterion is recommended or applied. Deferred: commitment tracking, visible challenge preset, semantic event grouping, OCR, embeddings, voice/native push, configurable alerts, full quarterly reports and custom PDF viewing. If the actual remaining time is only six hours, or T1 is still blocked at 90 minutes, a new scope/time decision is required rather than a silent cut.

Submission proof: record actual source/period/hash coverage, measured timings including wake/queue, 12-case results and failures; clearly label cached/replayed data; demonstrate a second visit and a genuinely fresh ticker; confirm prototype/repository/build-history links in a signed-out context. The email remains unsent and must state omissions, not imply runtime verification from this review.

## GSTACK REVIEW REPORT

| Review | Runs this request | Status | Findings |
|---|---:|---|---|
| CEO / HOLD SCOPE | 1 | Complete; scope-preserving corrections recorded | C1–C2; implementation untested |
| Design | 1 | Complete; corrections recorded | D1–D2; rendered behavior untested |
| Engineering | 1 | Complete; feasibility gates open | E1–E6; corrections recorded, not runtime-tested |
| Outside voice | 0 completed | Unavailable | Claude Code unavailable; required native Plan/background fallback not present |

Workflow notes: requested reviews ran sequentially using the installed gstack instructions. Startup update checks failed; no installation/routing changes were made. No independent outside review completed; no multi-model consensus is claimed. The review-log helper failed with a filesystem permission error even at a project-local destination; its read returned NO_REVIEWS. Registry entries are not persisted; the verified project Markdown above is the record of these three reviews. Review diagrams are planning artifacts, not generated application UI. All corrections rely on the user's explicit permission for scope-preserving document updates; no scope expansion or cut has been treated as approved.

VERDICT: Scope is sound; implementation is conditional on first-gate feasibility and final user approval. No runtime or submission clearance.

**UNRESOLVED DECISIONS:**
- Final plan approval after all three sequential reviews.
