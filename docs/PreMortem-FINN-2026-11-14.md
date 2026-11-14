# Pre-mortem — FINN

14 November 2026 · Imagine tomorrow's reviewer opens FINN, finds it slow or misleading, and cannot trust the demo. This horizon follows the actual deadline rather than a hypothetical 14-day launch. Risks below are proposed gates, not resolved findings.

## Tigers: real risks

| Risk | Urgency | Mitigation and evidence | Owner / due |
|---|---|---|---|
| Fresh ticker fails on cloud IP, large PDF, extraction memory or model quota | Launch-blocking | First deployed vertical test before UI; one bounded extraction at a time; measure memory/time; preserve explicit partial coverage. Do not substitute a hard-coded answer | Implementation owner (Codex with Aadish) / first 90 build minutes, before 15 Nov submission |
| Plausible answers cite irrelevant pages, wrong issuer or incompatible numbers | Launch-blocking | Company/document identity, page provenance, deterministic arithmetic and 12-case human evidence audit. Disable unsupported answers | Codex implements; Aadish reviews evidence / before final acceptance, 15 Nov |
| “Nothing new” hides a failed fetch or unparsed material filing | Launch-blocking | Separate source coverage from event count; retain assessment-pending items; audit material/routine examples; stale timestamp visible | Implementation owner / before phone acceptance, 15 Nov |
| Free service wakes slowly or loses SQLite and the demo appears broken | Launch-blocking | Render Free selected by Aadish; cold-restart test; dated seed, disposable cache, browser review state and visible loading/coverage. No hidden keep-alive workaround | Codex verifies / before submission |
| A polished local demo consumes the submission window | Launch-blocking | Deploy in T1; reserve final 45 minutes for links, README, notices, history and email draft; spend contingency on core failures | Aadish + Codex / 15 Nov, target 21:00 IST |
| Lexical search misses synonyms or a source format changes | Track; blocks launch if gold set fails | Small synonym map, inspect failed retrievals, retain source links. Add embeddings only after a measured retrieval failure | Implementation owner / acceptance, then after submission if needed |

The real risk is not the existence of missing data; it is silently presenting missing data as complete. Individual unavailable documents can be disclosed. Persistent failure of a mandatory source class or all unseen tickers cannot be excused as a passing demo.

## Paper Tigers: avoid spending the deadline here

- No vector database or multi-agent system: a few documents per question do not justify either before retrieval tests fail.
- No elaborate UI library: two destinations and one evidence sheet need consistent interaction, not a dashboard framework.
- No OCR, management-promise tracker or native push: these are deferred capabilities, not reasons to delay the agreed core.

## Elephants: assumptions to expose

- **Repeat use is unvalidated.** Ask the reviewer to return after one changed event and explain what still needs attention; do not claim retention or time savings from the prototype alone.
- **Free API access is not a capacity commitment.** Verify credentials and actual limits in T1; enable fallback only after a supported-answer and abstention smoke test.
- **Public access is not redistribution permission.** Keep original links and limited evidence excerpts; document source limitations and software notices. Confirm permission before publishing substantial cached source material.
- **The old six-hour estimate is too optimistic.** The sequential review now budgets 7¼ hours core plus 45 minutes reserve. If only six hours remain or T1 is blocked at 90 minutes, reassess feasibility rather than spending the rest on appearance. No scope cut is pre-approved.

Fast-follow, only if this continues beyond the assignment: durable storage and broader retrieval coverage after measuring actual failures. No post-launch work is promised as part of this submission.
