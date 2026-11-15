# Third-party components

FINN application code is original. Runtime dependencies remain under their own licences. No yfinance, NseIndiaApi, Docling, LlamaIndex or Instructor code is bundled.

| Component | Use | Licence |
|---|---|---|
| FastAPI, Pydantic | API and contracts | MIT |
| Uvicorn, HTTPX | Server and HTTP client | BSD-3-Clause |
| Beautiful Soup | Document discovery | MIT |
| pypdfium2 5.15.2 | Bounded text extraction | Apache-2.0 OR BSD-3-Clause |
| PDFium, bundled by pypdfium2 | Native PDF parser | BSD-style; bundled dependency notices apply |
| psutil | Worker memory measurement | BSD-3-Clause |
| python-dotenv | Local server configuration | BSD-3-Clause |
| pypdf (development only) | Synthetic PDF test fixtures | BSD-3-Clause |
| pytest (development only) | Tests | MIT |
| React / React DOM | Mobile interface | MIT |
| Radix Dialog | Accessible evidence sheet | MIT |
| Vite / TypeScript | Build and type checking | MIT / Apache-2.0 |
| Playwright (development only) | Browser regression tests | Apache-2.0 |
| Adobe Source Sans 3 | Self-hosted typeface | SIL Open Font License 1.1; notice in frontend/public/fonts |
| Hanken Grotesk | Integrated product's self-hosted typeface | SIL Open Font License 1.1; `frontend/public/fonts/HankenGrotesk-OFL.txt` |
| Psycopg / psycopg-binary 3.3.9 | PostgreSQL adapter | LGPL-3.0-only (verified installed metadata); installed package retains its licence notices; repository references the wheel, not a redistributed binary |

The pypdfium2 and PDFium notices are retained in `LICENSES/pdfium/`. The installed wheel includes the complete platform-dependent dependency licences under its distribution's `licenses/BUILD_LICENSES` directory. This repository references the wheel; it does not redistribute PDFium binaries.

Primary financial documents belong to their issuers/exchanges. FINN links originals and uses bounded supporting excerpts; it does not claim ownership. Yahoo and NSE access is public-source integration for an assignment prototype, not a licensed production market-data feed. No redistribution licence for complete source datasets is asserted.

Sources: [pypdfium2 licensing](https://pypdfium2-team.github.io/pypdfium2/readme.html#licensing), [PDFium licence](https://pdfium.googlesource.com/pdfium/+/refs/heads/main/LICENSE).

Psycopg Pool 3.3.3 — LGPL-3.0-only. Official optional Psycopg component; bounded server-side connection reuse. https://pypi.org/project/psycopg-pool/
