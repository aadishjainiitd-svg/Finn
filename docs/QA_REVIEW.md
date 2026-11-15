# FINN implementation review

15 November 2026. Status: scoped code review, executable regressions and final hosted/mobile revalidation complete. Historical observations below retain their dates. Broad HAVELLS case S4 is now repaired and hosted-verified; the current [evidence audit](EVIDENCE_AUDIT.md) supersedes the earlier capacity/TCS blockers.

Scope: FINN's backend, source jobs, mobile Brief/Research and shared evidence sheet. Owned local service and isolated browser fixtures; live source/provider observations are recorded separately. No external messages sent or paid plans enabled.

## gstack code review

Native same-harness adversarial review inspected the full first-party implementation. Fixtures were reviewed in summary mode by the reviewer; the parent executed the actual tests. This is not independent-model consensus. The optional Claude Code outside reviewer was unavailable. The gstack registry helper failed on a Windows path/permission error, so this document is the review record; no registry success is claimed.

| Finding | Correction | Verification |
|---|---|---|
| Valid quote can accompany a contradictory paraphrase | Server displays source-exact factual assertions; model selects passages. Cached answers use the same renderer. Browser answer storage version changed | Synthetic contradiction becomes the original quotation; idempotent renderer test; live answer audit |
| Changed/replaced filing can inherit routine status | Shared signature, source-version and 10-minute assessment validation on both Brief and evidence paths | Replacement/signature fixtures; native re-review |
| Full assessment allocation after parser monitor | Six-million-character extraction cap and one-million-character assessment cap | Code review; existing measured hosted extraction; failure stays pending |
| Filing jobs grow without bound | Shared 25-job retention and coalescing | Bounded-retention fixture |
| Older filing response can replace a newer sheet/tab | Generation invalidated by opening, navigation and other sheet actions | Browser delayed-response test |
| Quota exhaustion latches into next day | UTC date resets provider header state; daily ledger remains dated | Static review; daily accounting retained |
| Background failure leaves green coverage | Coverage metadata updates without reordering; fetch errors stay visible | Browser coverage-loss fixture |
| DNS check and connection can resolve differently | Connect to validated public IP; preserve Host and TLS SNI; no environment proxy or keepalive reuse across redirected hosts | Real NSE identity, Screener and Yahoo HTTPS requests passed; transport fixture verifies address/Host/SNI |

The pinned-address implementation follows the [official HTTPX extension](https://www.python-httpx.org/advanced/extensions/), also checked in the installed HTTPX/HTTPCore source. No network exploit was attempted.

## Executed tests

- 53 Python tests passed on 15 November. They cover exact citations, replacement/parser/kind identity, source failure states, unknown ticker, daily arithmetic, numerical unit/period boundaries, missing transcript, model 429, bounded jobs, retrieval coverage, cache-render idempotence and a cancelled real child process with partial-state cleanup.
- 8 Node tests passed: explicit acknowledgement, Undo, both revision/acknowledgement race orders, late discovery and check windows.
- 7 Playwright browser tests passed at 390px/360px: persistence, evidence opening without acknowledgement, keyboard/focus/Escape, both research-response race orders, coverage loss, lost citation versions, failed first check and stale filing response after navigation.
- Python emits a TestClient dependency deprecation warning. Vite emits Radix `use client` bundling warnings; this is a client-rendered React application, and browser behavior is tested.

These controlled fixtures are not claims of live exchange availability or provider quota. Real measurements are in [FEASIBILITY_RESULTS.md](FEASIBILITY_RESULTS.md); final evidence results will be recorded separately.

## Design review and release replays

Initial real gstack browser at 390×844: calm reading hierarchy, two destinations, visible source coverage. First glance goes to “Your brief”, coverage, then the first event. That first event exposed a real misclassification: a director biography mentioning Fraud & Vigilance triggered a credit-risk reason. Positive event patterns and an issuer-written subject fixed it. A negated default statement is also covered by regression testing.

The bounded exploratory browser run ended at 07:05:29 UTC. Its deadline was not reset. Subsequent checks are the explicit release acceptance and repair replays described below, not an extension of exploratory QA. No full automated design score or physical-device certification is claimed.

## Release verification and repairs

| Contract | Executed check / result |
|---|---|
| Mobile first event and evidence | Live 390×844 browser: actual HDFCBANK event and Evidence action visible; full decision sentence and readable publication date verified after the honorific splitter fix. [After](screenshots/mobile-evidence-after.jpg) |
| Focused research response | Live ASTRAL dated example returned in 212 ms; answer scrolled to the top and Edit question was available. This is cached latency, not fresh synthesis. [Capture](screenshots/mobile-research-after.jpg) |
| Narrow screen / targets | Live 360×800 and 390×844: no horizontal overflow; measured visible interactive targets at least 44×44px. |
| Desktop / reflow | Live 1440×900: 720px reading column. CSS zoom 200% retained horizontal fit and visible navigation. This is a reflow approximation, not native browser-toolbar zoom or a physical keyboard test. |
| Reduced motion | Chromium media emulation matched `prefers-reduced-motion: reduce`; computed animation was `none`. |
| Current console | Fresh reload after clearing old buffer produced no console errors. Earlier buffer contained 503/405 during earlier deployment/probes; those are not erased from this record or attributed without evidence. |
| Review persistence | Real acknowledgement changed browser state to Reviewed/Undo and survived reload. This exposed the TTL/parser revision defect below, now covered by a deterministic regression. |
| Error plus missing source | New browser fixture verifies that generation failure retains loaded document periods, explicit missing annual-report reason and source excerpts. |

Additional corrections:

- **Sentence boundaries:** `Mr.` and initials no longer cut off filing decisions. Adjacent exclusions remain with financial amounts; a reviewer caught a decimal truncation in the first fix, and the INR1.5-billion regression now passes.
- **Review continuity:** assessment expiry now affects coverage/pending status without changing an unchanged filing's acknowledgement revision. The last observed PDF byte hash survives TTL and parser-only upgrades; actual replacement bytes reopen the filing. The seed uses the same canonical identity. This was discovered during live reload, not just inferred from code.
- **Reading order:** long company context remains expandable with its citations; the focused answer is promoted. Final screenshot/replay must use the latest deployed frontend before this repair is called verified.

Gstack usage was adapted to the available Windows host: its headless browse CLI worked; Aside was unavailable. Native adversarial review was same-harness, not an independent external model. The browser report template was absent; the installed functional template informed this report. The full exploratory run's unfinished charters are not counted as passes.

Local replay notes are retained under `.gstack/qa-final/browser/exploration-002.json` through `exploration-011.json` (ignored; these include pre-fix observations). Public screenshots and the committed tests provide the reviewable evidence. Fixtures do not prove real endpoint availability.

## Final replay — 15 November

- Repaired Python 3.12.14 venv; 53 Python, 8 Node and 7 Playwright tests pass. Vite production build passes. Last review found two cache-render edge cases (dropped first claim and mixed citations); regressions and same-harness re-review close both. All recorded evaluation answers, seeds and the held-out answer remain unchanged through the final renderer.
- Live final app revision `78ba67e62a68`: ASTRAL shows a dated demonstration label, collapsed annual company context, focused demand/margins answer, and explicit H1 margin wording. [Final capture](screenshots/mobile-research-final.jpg).
- At 390×844, the dated 14-day Brief shows HDFCBANK's decision and Evidence action within one viewport. No horizontal overflow; all measured fully visible buttons/selects are at least 44×44px. [Brief](screenshots/mobile-brief-final.jpg), [evidence](screenshots/mobile-evidence-final.jpg).
- Actual HDFCBANK opening/closing left Mark reviewed unchanged. Explicit acknowledgement survived reload as Reviewed/Undo in the 14-day window. Undo restored Mark reviewed. The adjacent item remained outstanding. These were real API/browser interactions, not fixtures.
- Real final-code restart: healthy at the 51.23-second probe window, old CROMPTON citation HTTP410, saved browser quote/page/period/hash retained with a visible warning. [Capture](screenshots/mobile-restart-final.jpg). The console contained the expected 410 resource error from this deliberate test; no unexpected JavaScript exception was observed.
- Earlier same-turn 390×420 reduced-height check kept the focused question and submit control above navigation. This approximates reduced keyboard space; it is not a physical keyboard test. Earlier 360px, desktop, CSS reflow and reduced-motion checks remain recorded above.

Remaining limits: physical iOS/Android keyboard and screen-reader testing are not executed; source/provider availability can change; S4 now covers the three requested topics. Universal retrieval coverage is not claimed. The runtime and mandatory grounding/failure contracts are supported by the listed evidence.

## HAVELLS follow-up

56 Python tests pass after a demonstrated failing retrieval regression and two segment-context cases. Existing 8 Node/7 Playwright results remain prior checks on unchanged frontend code; no full new browser-fixture sweep is claimed. Fresh S3 and S5 provider regressions pass. Fresh deployed S4 on 2477c701ce1b completes in 32.28s; every citation resolves and cache replay is identical. Actual 390×844 browser replay shows the complete three-topic answer and correctly attributed Lloyd excerpt. New screenshots are linked in the audit. Earlier runtime/restart results retain their recorded revision.

The gstack investigation helper could not acquire its Windows state lock (permission/path failure); no lock ownership or cleanup success is claimed. Scope was kept manually to retrieval/prompt/cache version, grounding regressions and the requested verification documents. The same-harness reviewer rechecked the final small diff and found no material issue. No unrelated skill-routing changes were made.
