# FINN feasibility evidence

14 November 2026. All times below are measured, not estimates. Public service: https://finn-enam-yije.onrender.com. Hosting explicitly uses Render **Free**, Singapore, one Python 3.12.14 process. No paid service or billing upgrade was enabled.

| Check | Observed result | Evidence class |
|---|---|---|
| Minimal deployment | HTTP 200 `/health`, Python 3.12.14 | Live Render |
| Identity | Official NSE EQUITY_L.csv resolves HAVELLS / Havells India Limited / INE176B01034. Quote endpoint returned 403, so it is not a dependency. | Live exchange |
| Generic discovery | Screener index discovered BSE annual report and transcript; no HAVELLS URLs in application code. Index is not cited as research evidence. | Live |
| Annual report | 442 PDF pages, 8,785,160 bytes, 125.4 seconds, observed combined API + worker peak 236.3 MB | Live Render, initial run |
| Transcript | 17 PDF pages, 981,998 bytes, 6.7 seconds, combined peak 141.1 MB | Live Render, initial run |
| Full investigation | 137.41 seconds. Both documents verified against issuer text and source period. | Live Render, initial run |
| API during parsing | Health HTTP 200 in 0.20 seconds | Live Render |
| Sources from host | 63 Yahoo daily bars; 4 HAVELLS NSE filings, successful JSON responses | Live Render |
| Primary model | Groq `openai/gpt-oss-120b`, HTTP 200. Observed headers: 8,000 token limit and 1,000 request limit. | Live provider |
| Secondary model | Gemini `gemini-3.5-flash-lite` produced a cited answer and abstained on an exact future share-price question. Automatic fallback disabled pending account quota/billing verification. | Live provider |
| Real restart | Render restart API HTTP 200; healthy after 50.48-second probe window. Old citation returned HTTP 410 `version_unavailable`. No replacement text was returned. | Live Render |
| Replacement / persistence | Two different byte versions behind one URL retain different evidence IDs; reopening cache preserves exact original text; evicted version returns unavailable. | Executed isolated fixture |
| Citation validation | Unknown ID, invented quote, other-page match and replacement-version match rejected; an exact overlap within supplied same-page chunks resolves correctly. | Executed isolated fixtures |

## Grounding correction

Manual audit of the initial answer found an unsupported consequence: it paraphrased softer demand and volatile costs as pressure on margins. The annual-report paragraph did not establish that consequence. The prompt now prohibits such additions, strict schema validation is enabled, and the answer cache version changed. The repeated real model response removed that consequence. Its three points are supported by HAVELLS transcript PDF page 9 (aluminium price decreases/contribution margins; Lloyd investment/profitability discussion) and annual-report PDF page 216 (BCP demand and input-cost context).

The model attached one annual-report quote to an overlapping chunk whose last sentence was truncated. The resolver now checks exact membership in another *supplied* chunk of the same hash and PDF page, with a unique match required. It never repairs unknown IDs, changes quote text, searches a different page, or uses a newer document. This is deterministic source resolution, not a semantic entailment guarantee. The 12-case manual evaluation remains required.

## Limits and outstanding gate work

- Corrected hosted full run is in progress; do not mark the gate passed from local tests alone.
- Groq's [official free-tier limits](https://console.groq.com/docs/rate-limits) list 30 RPM, 1,000 RPD, 8,000 TPM and 200,000 TPD. Token admission reserves prompt, evidence and output conservatively, permits one synthesis per minute, and uses a 180,000-token/900-request local daily ceiling. Provider enforcement remains authoritative across an ephemeral-cache loss; process restart waits a full minute. No automatic retries or bulk filing synthesis.
- Gemini account-specific quotas cannot be inferred from successful generation. They remain unverified; it is not automatically selected.
- Memory is sampled every 100 ms. Worker has a Linux 350 MB address-space limit, combined RSS ceiling 440 MB, 40 MB download, 500-page and 180-second processing bounds. These do not establish universal PDF coverage.
- Render's cache is disposable. Browser-retained excerpts are still to be implemented. A saved quote remains traceable to the recorded version, but this prototype does not permanently host original PDFs.
- Six isolated grounding tests currently pass. Frontend, portfolio workflow, full fault suite and submission audit have not yet run.
