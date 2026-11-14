# FINN implementation review

14 November 2026. Status: code review converged; final hosted acceptance and design screenshots in progress.

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

- 46 Python tests passed. They cover exact citations, replacement/parser/kind identity, source failure states, unknown ticker, daily arithmetic, numerical unit/period boundaries, missing transcript, model 429, bounded jobs and a cancelled real child process with partial-state cleanup.
- 7 Node review-state tests passed: explicit acknowledgement, Undo, both revision/acknowledgement race orders, late discovery and check windows.
- 6 Playwright browser tests passed at 390px/360px: persistence, evidence opening without acknowledgement, keyboard/focus/Escape, both research-response race orders, coverage loss, lost citation versions, failed first check and stale filing response after navigation.
- Python emits a TestClient dependency deprecation warning. Vite emits Radix `use client` bundling warnings; this is a client-rendered React application, and browser behavior is tested.

These controlled fixtures are not claims of live exchange availability or provider quota. Real measurements are in [FEASIBILITY_RESULTS.md](FEASIBILITY_RESULTS.md); final evidence results will be recorded separately.

## Design review in progress

Initial real gstack browser at 390×844: calm reading hierarchy, two destinations, visible source coverage. First glance goes to “Your brief”, coverage, then the first event. That first event exposed a real misclassification: a director biography mentioning Fraud & Vigilance triggered a credit-risk reason. Positive event patterns and an issuer-written subject fixed it. A negated default statement is also covered by regression testing.

Final review must still record actual mobile/desktop screenshots, 200% zoom, touch targets, reduced motion, console health and the live evidence → Research → return loop. No final design score yet.
