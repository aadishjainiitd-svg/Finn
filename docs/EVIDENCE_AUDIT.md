# FINN evidence audit — 14 November 2026

**Grounding checks pass; full-question completion remains open for S1. Fresh CROMPTON synthesis is blocked by FINN's conservative daily allowance.** This is not a claim that all release criteria pass.

Expectations were recorded before grading in [evaluation-cases.json](evaluation-cases.json). The [results](evaluation-results.json) retain source URLs, hashes, parser versions and PDF pages. Six factual questions, two unanswerable questions, two numerical questions and two identity/source-failure cases were exercised.

The original source discovery, PDF extraction and model selections used real requests. Final API replays reused those cached selections through the corrected source-exact renderer; they are **not eleven fresh model calls**. I2 is an isolated missing-transcript fixture. Early failed attempts remain in ignored local `data/evaluation-attempt*` folders; credentials and raw caches are not published.

| Case | Result | Source/context audit |
|---|---|---|
| S1 TCS business / AI / deals | **Partial; completion open** | Annual PDF55 supports business and AI spending context; PDF25 supports deal momentum. No latest-call passage selected. The answer says so and is marked partial. Do not count this as a full answer to the original question. |
| S2 KPIT demand | Pass | Annual PDF5; call PDF10/14. OEM pressure, possible recovery and expected growth remain attributed management statements. No invented sequence between statements. |
| S3 ASTRAL margins | Pass | Annual PDF4; call PDF2. 17.4% is explicitly **H1**, not Q2. Guidance is distinguished from the reported observation. |
| S4 HAVELLS risks | Pass, bounded selection | Annual PDF216 and call PDF9. Demand/cost risks and management's margin-volatility qualification are supported; no unsupported causal link is added. Not a comprehensive risk report. |
| S5 HAVELLS timeline | Pass | Call PDF9 preserves management's inability to give a firm Lloyd recovery timeline. |
| S6 TCS revenue / TCV | Pass after correction | Call PDF3: quarterly INR73,188 crore and US$9.6 billion TCV. Adjacent Porsche/Best Buy exclusion now stays with TCV. Decimal-exclusion regression also passes. |
| U1 exact future stock price | Pass | Abstention; no forecast invented. |
| U2 exact FY2035 revenue | Pass | Abstention; unavailable future figure not invented. |
| N1 crore → lakh | Pass | Decimal arithmetic: 73,188 × 100 = 7,318,800 lakh. Same quarterly operand, currency retained; unspecified accounting scope disclosed. |
| N2 quarter vs half-year growth | Pass | Declines incompatible period comparison; no LLM arithmetic. |
| I1 unknown NSE ticker | Pass, live identity path | Successful official identity lookup precedes `unknown_ticker`; no guessed substitution. |
| I2 missing transcript | Pass, **fixture** | Explicit missing-source gap; no claim that a transcript was loaded. |

All **21 displayed citations** across the factual/numerical cases match supplied versioned page text exactly. Human context review checked units, periods, attribution, negation and qualifications; exact membership alone is not a semantic test. S1's safe partial answer is a retrieval/completion limitation, not a grounding success disguised as full coverage.

## Fresh-company and resource evidence

HAVELLS, outside the prepared research set, passed the original hosted gate with both document types and a supported answer. The post-implementation CROMPTON test used the same generic NSE identity → Screener discovery → primary PDF pipeline, without a company-specific URL map.

The first CROMPTON attempt hit the 440 MB combined memory guard late in the annual report. A local controlled comparison identified document-cache accumulation: reopening the PDF handle every 32 pages reduced parser/launcher peak from 329.1 to 305.3 MB, preserving the complete 341-page output hash `aa61d5b41e0a54d632376008ade81e4b979e60af0d76d9b1837f4b2d49effe38`.

Hosted replay at revision `2468e8954836`:

| Document | Size / pages | Processing | Combined API + worker peak |
|---|---|---|---|
| CROMPTON annual 2025–26 | 19,853,481 bytes / 341 | 32.08 s | 423.6 MB |
| CROMPTON Q2 FY27 transcript | 559,632 bytes / 17 | 1.60 s | 149.5 MB |

Both documents passed issuer, type and period checks; source gaps were empty. Total job time was 36.90 s. Synthesis then stopped at `daily_quota`; **no new CROMPTON answer is claimed**. The memory guard was not raised. Local Windows measurements before the corrected profiler omitted launcher descendants and should not be compared with these corrected numbers; the earlier Linux hosted measurements used the direct parser process.

## Capacity and release blocker

Groq `openai/gpt-oss-120b` is selected. FINN reserves estimated input/schema/output tokens before calling, allows one call per 61 seconds, and stops at 180,000 reserved tokens / 900 requests per UTC day. The current ledger contains 178,548 reserved tokens and 26 requests, so another normal request is refused. This is FINN's guard, **not an observed provider 429 or proof of actual token exhaustion**. The known ledger baseline survives today's redeploy via the dated seed.

Gemini generation was smoke-tested and the user confirmed billing disabled, but account RPM/TPM/RPD remain pending. Automatic fallback is disabled. Do not clear the ledger, enable paid usage, or relabel a cached answer as fresh to complete the audit.

Remaining exit checks: verify Gemini's account limits and test independently budgeted free routing, or wait for the legitimate daily reset; then rerun S1 and a focused CROMPTON question, audit all new claims, and refresh this record. The UTC-day reset is 15 November 05:30 IST; that is an application-policy boundary, not a promise about provider capacity.
