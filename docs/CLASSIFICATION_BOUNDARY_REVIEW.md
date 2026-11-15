# Filing boundary investigation — 15 November 2026

Status: **DONE_WITH_CONCERNS**. The named bugs reproduce before the fix and pass after it; expanded semantic acceptance and hosted deployment remain outstanding.

| Finding | Root cause | Correction | Evidence |
|---|---|---|---|
| ABB results release called an acquisition | `acquired businesses` inside an Operational EBITA definition matched a loose event pattern | Require transaction verbs, exclude accounting definitions; retain the real quarterly-results reason | Actual retained ABB release, PDF p.2 results and accounting-definition page; regression rejects the acquisition reason while keeping results in Needs you |
| CERA publication cited a different issuer | Filing-level identity was incorrectly extended to every advertisement on a newspaper page | Multi-page publications remain visible and pending issuer-layout verification. Only the cover is offered for inspection; newspaper content is excluded from generated answers and enrichment | Actual retained CERA publication previously cited `lloyds.in`/another company's table. Current citation is cover p.1, pending, never buried |
| Completed acquisition missed | Bare `has acquired ABC Limited` was not recognised unless another acquisition noun occurred later | Recognise the explicit completed-transaction clause while rejecting eligibility/profile wording | Controlled positive and negative source-text regression |

The three new regression tests first failed (3 failed, 5 passed), then passed (8 passed). Full suite at that point: 107 passed. The evidence fixtures preserve source URLs, byte/version identities and relevant unaltered chunks; they are replayed retained primary sources, not new network requests. No model call was used.

Classification policy is now `claim-linked-v5`; stale assessments remain visible pending reassessment. Research cache policy is `retrieval-11` to invalidate pre-boundary answers. Previously recorded source-refresh results remain evidence for the earlier processing policy, not proof of the new policy's classification accuracy. No blanket 50-filing semantic-audit pass is claimed: the initial scan included duplicate extraction versions and exposed these defects.

gstack investigate was used for reproduction, hypothesis, regression and verification. Its scope-lock helper failed with a Windows path-permission error; no lock token was acquired or removed. Edits were manually confined to the classifier/retrieval/cache boundary and their regressions. Optional routing-file setup was not introduced into this existing authorised implementation. This is not final pre-landing review clearance.

Durable learning: a primary source's issuer identity does not make every page issuer-specific; financial metric definitions do not establish corporate actions. Unknown newspaper layout must stay visible, and must not supply another company's facts to Ask.
