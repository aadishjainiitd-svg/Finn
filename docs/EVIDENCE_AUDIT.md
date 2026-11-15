# FINN final evidence audit

15 November 2026. Application revision `2477c701ce1b0c9a0d7f4ecce3985d0ef017ecb9`, Render **Free**, Groq **openai/gpt-oss-120b**. [Prototype](https://finn-enam-yije.onrender.com) · [Machine-readable evaluation](evaluation-results.json) · [Hosted record](hosted-verification.json).

The source, portfolio, supported-claim, numerical-safety and bounded-failure contracts are verified. The previously partial HAVELLS S4 now explicitly covers each requested topic. Unsupported questions still abstain; a supported answer is not an exhaustive risk inventory. No universal ticker coverage, investment accuracy or production availability is claimed.

## Research evaluation

Expectations in [evaluation-cases.json](evaluation-cases.json) were recorded before grading. The initial eight requests used fresh Groq 120B generation on 15 November; two numerical cases are deterministic, one identity lookup rejects the unknown ticker, and one missing-source case is an isolated fixture. Primary PDFs had been fetched and versioned by the real pipeline; some source/cache reuse is expected. Final renderer responses were replayed from cache, then checked again after the last idempotence fix. The initial replay was unchanged. S4 was subsequently repaired and replaced by the final fresh hosted result described below. These are not twelve fresh model calls in one final sweep; unchanged cases retain their earlier validation.

All **17 displayed claims / 26 citation references** pass exact quote membership, byte-hash identity and PDF-page checks. Semantic inspection checked the meaning and attribution, not just string matching:

| Case | Result and semantic audit |
|---|---|
| S1 — TCS business, AI, deals | Supported. Annual PDF55 identifies IT services/consulting. Call PDF12/7 attributes AI observations to management; PDF3 retains US$9.6bn TCV and exclusion of Porsche/Best Buy. |
| S2 — KPIT demand/visibility | Supported. Annual PDF5 identifies mobility engineering. Growth forecasts remain management statements; the positive observation retains the preceding warning of continued pressure from two OEMs. No invented causal timeline. |
| S3 — ASTRAL demand/margins | Supported. Annual PDF4 business context; call PDF2/8 demand and margins. The 17.4% margin is **H1**, not Q2, and the volume-growth antecedent is preserved. |
| S4 — HAVELLS broad risks/demand/margins | **Supported after repair.** Hosted annual PDF216 identifies trade/geopolitical risks; call PDF3 retains macro/commodity qualifications on demand outlook and identifies Lloyd’s raw-material inflation and off-season underabsorption as margin pressures. Every quote resolves through the deployed evidence API. |
| S5 — firm Lloyd recovery timeline | Supported. Call PDF9 explicitly avoids a firm timeline; medium-term profitability remains an aspiration, not a deadline. |
| S6 — quarterly revenue/TCV | Supported. Call PDF3 reports INR73,188 crore and US$9.6bn. Currency and period remain distinct; the deal-value exclusion is retained. |
| U1/U2 — future share price / FY2035 revenue | Correct abstention; no exact future outcome invented. |
| N1 — crore to lakh | Decimal conversion: 73,188 × 100 = 7,318,800 lakh. The source excerpt does not establish accounting scope, which is disclosed. |
| N2 — Q2 versus H1 growth | Correct refusal of incompatible period comparison. |
| I1 — unknown ticker | Official identity dataset lookup returns `unknown_ticker`; no guessed issuer or model call. |
| I2 — missing transcript | Executed controlled fixture reports the missing call and preserves available evidence; not live discovery proof. |

The preliminary 20B candidate failed ASTRAL with HTTP400 and was not promoted. Its precise provider failure cause was not established. The production 120B model passes that question. The previous day's 178,548-token conservative reservation was not an observed provider 429; the new day's legitimate UTC allowance enabled fresh verification. No old ledger was reset to force success.

## Hosted unfamiliar-company gate

CROMPTON is outside the three prepared examples. Generic discovery resolves Crompton Greaves Consumer Electricals Limited, ISIN `INE299U01018`, and validates both primary documents. On the earlier verified application revision `78ba67e62a68`:

| Measurement | Annual report | Earnings call |
|---|---:|---:|
| Period | 2025–26 | Q2 FY27 |
| PDF pages | 341 | 17 |
| Bytes | 19,853,481 | 559,632 |
| Processing seconds | 28.20 | 1.81 |
| Sampled combined RSS peak | 424.3 MB | 150.6 MB |

The full request completed in **35.27 seconds**, with no document gaps and a supported answer citing annual PDF124 and call PDF4. All four citation references match their captured passages. An earlier run also fetched these citations through the deployed evidence endpoint and checked their exact text. Report table headers remain visible in the source-exact annual excerpt; this is a readability limitation, not a fabricated narrative. Memory headroom is narrow: the 440 MB guard remains active and larger PDFs can fail explicitly.

Real hosted source checks observed 63 TCS Yahoo daily bars and three TCS NSE disclosures. The Brief returned **15/15 filing and 15/15 price coverage**, 86 distinct filings, with separate pending assessments. Latest completed price session was 13 November. Cached source checks retain actual fetch timestamps; `live` identifies successful source coverage, not streaming prices or a new fetch on every API hit.

## Reliability, quotas and remaining limits

- 56 Python tests pass after the HAVELLS repair. The unchanged frontend retains its earlier 8 Node and 7 browser test passes. [QA review](QA_REVIEW.md) separates controlled failure fixtures from real browser/source requests. Document replacement and parser-version tests reject cross-version citations; cached-answer rendering is idempotent, including dropped and mixed-source context.
- Groq response headers verified 8,000 token and 1,000 request limits. The [official free-tier table](https://console.groq.com/docs/rate-limits) documents 30 RPM / 200,000 TPD; those two values were not independently exposed by the observed headers. FINN admits one flight per minute, reserves schema/evidence/output within 7,600 tokens, and applies 180,000-token / 900-request daily caps. No paid route was enabled.
- Gemini billing disabled is user-confirmed; account-specific limits remain unverified. Automatic fallback is disabled. Groq and xAI Grok are different services.
- Render sleeps and discards writable files. Saved browser excerpts and dated seeds preserve provenance; they do not permanently archive PDFs. A known quota baseline restores, but uncheckpointed usage can be lost on restart; provider free enforcement is the final backstop.
- Physical iOS/Android keyboards and screen readers were not tested. Narrow Chromium viewports, reduced-height input layout, focus/Escape, motion preference and CSS reflow were checked; these are not physical-device certification.
- No OCR, BSE-only identity support, full financial-table calculations, configurable portfolio, alerts or commitment tracking. No deferred feature was added.

Final restart and signed-out public-link outcomes are recorded in [hosted verification](hosted-verification.json), [QA review](QA_REVIEW.md) and the [implementation log](IMPLEMENTATION_LOG.md). The submission email remains unsent.

## HAVELLS repair — final deployed verification

Revision `2477c701ce1b`, `retrieval-9-prompt-10`, deployed to the same Render Free service. Root cause: broad BM25 matches placed the specific call passage eighth, outside the 10,500-character evidence budget. Demand/margin topic reservations now put relevant passages early. The prompt allocates report risk, demand and margin-driver coverage within the source-word budget; segment-dependent margin excerpts retain the preceding same-speaker identification.

The new retrieval regression failed before the fix. **56 Python tests pass** afterward, including context/idempotence checks. Fresh local ASTRAL demand/margins and HAVELLS no-firm-timeline regressions remain supported with exact quotes. Same-harness scoped code review found no remaining material issue; it was not independent-model consensus.

The final local S4 run contains BCP risk, qualified demand outlook, cables/aluminium pressure, Lloyd-specific costs and H1/rest-of-portfolio context: five citations, 136 source words, idempotent rendering. The independent fresh **hosted S4 completed in 32.28s** and selects three passages: annual trade/geopolitical risk, qualified demand outlook and Lloyd-specific pressure. Its three displayed citations passed exact text/hash/page checks through `/api/evidence`; the next API request returned an identical cached answer. The original expectation examples and earlier failed/overlong attempts remain recorded; the two successful runs select different supported passages, not identical output. The no-firm-Lloyd-timeline qualification is separately checked by S5.

The real 390px mobile replay displays all three topics, no partial warning, and the Lloyd name, Q2 FY27 period and PDF page 3 in the evidence sheet. [Answer](screenshots/mobile-havells-final.jpg) · [Evidence](screenshots/mobile-havells-evidence.jpg) · [Structured results](havells-verification.json).

No quota/grounding guard was relaxed. The deployment seed includes the current local reservation plus conservative reservations for the two known earlier hosted calls; ledgers were not reset. Gemini remains disabled. The CROMPTON/restart measurements above are from the prior revision; they were not rerun for this retrieval-only repair. Earlier saved browser answers remain dated observations; resubmitting the original HAVELLS question obtains the repaired result.
