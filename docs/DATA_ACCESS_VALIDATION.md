# FINN data-access validation

Checked 14 November 2026 from the user's Windows machine using read-only HTTPS requests and existing bundled Python libraries. Initial sandbox socket errors were environmental; approved network-enabled probes below reached the sources. No credentials were used, no packages installed, and downloaded PDFs were parsed in memory.

## Result

All three required source classes have a demonstrated local access path. This is an access and sampled text-extraction check, not proof of full ingestion correctness, unrestricted availability, or access from a future deployment host.

## 1. EOD prices and volume: pass

Endpoint pattern: https://query1.finance.yahoo.com/v8/finance/chart/TCS.NS?range=3mo&interval=1d

All 15 proposed portfolio tickers returned usable daily close and volume pairs:

| Tickers | Valid bars | Latest observed daily bar |
|---|---:|---|
| RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK, LT, BHARTIARTL, ITC, SUNPHARMA, MARUTI, TITAN, ULTRACEMCO, KPITTECH, APLAPOLLO | 63 each | 13 November 2026 |
| CERA | 62 | 12 November 2026 |

The latest volume was positive for each. Example TCS response: HTTP 200, close 2407.5, volume 3344738. These are observed source values, not independently reconciled financial facts. Source timestamps represent daily bars, not fetch time or close-time guarantees. The endpoint is an unofficial integration surface; isolate it, cache results and handle failure.

## 2. Exchange filings: pass via NSE; BSE feed unavailable

Date window: 1-14 November 2026.

Working NSE query pattern:
https://www.nseindia.com/api/corporate-announcements?index=equities&symbol=TCS&from_date=01-11-2026&to_date=14-11-2026

The broad query returned 9,993 records, 85 matching the portfolio. Independent per-symbol requests confirmed the following counts and returned only the requested symbol:

| Symbol | Filings |
|---|---:|
| RELIANCE | 5 |
| TCS | 3 |
| INFY | 2 |
| HDFCBANK | 5 |
| ICICIBANK | 5 |
| LT | 5 |
| BHARTIARTL | 16 |
| ITC | 6 |
| SUNPHARMA | 5 |
| MARUTI | 5 |
| TITAN | 13 |
| ULTRACEMCO | 3 |
| KPITTECH | 4 |
| APLAPOLLO | 0 |
| CERA | 8 |
| Total | 85 |

APLAPOLLO returned an empty list; this proves the observed response, not independently verified absence of disclosures. Prefer bounded per-ticker requests to the large market-wide feed.

Attachment check: HDFCBANK management-change filing, published 13 November 2026 at 16:35:23 in the source. HTTP 200, application/pdf, 699,666 bytes, four pages; all four yielded 5,875 text characters in total.
https://nsearchives.nseindia.com/corporate/HDFCBANK3_13112026163422_SE_Intimation-_VSR.pdf

BSE's AnnSubCategoryGetData feed returned HTTP 403 for the tested request. BSE-hosted document downloads did work. Do not equate that feed failure with all BSE resources being inaccessible. No bypass was attempted.

## 3. Annual reports and earnings-call transcripts: pass with coverage caveats

Discovery used https://www.screener.in/company/{SYMBOL}/consolidated/ and selected document links by label. Documents were then fetched from exchange or company hosts. No Screener financial-table values were used as primary research evidence.

| Company | Document | Pages | Bytes | Extraction check |
|---|---|---:|---:|---|
| TCS | Annual Report 2026 | 361 | 17,427,580 | First four pages: 4,071 characters |
| TCS | Latest linked transcript | 29 | 723,462 | First four pages: 6,446 characters |
| ITC | Annual Report 2026 | 416 | 14,678,177 | First four pages: 2,699 characters |
| ITC | Transcript | — | — | No transcript link found on inspected company page; presentations are not substitutes |
| KPITTECH | Annual Report 2026 | 210 | 10,301,220 | First four pages: 5,828 characters |
| KPITTECH | Latest linked transcript | 21 | 492,051 | First four pages: 7,769 characters |
| ASTRAL | Annual Report 2026 | 247 | 25,692,481 | First four pages: 10,701 characters |
| ASTRAL | Latest linked transcript | 19 | 259,587 | First four pages: 9,868 characters |
| CROMPTON | Annual Report 2026 | 341 | 19,853,481 | Pages 1, 2, 3, 4, 171, 256: 22,491 characters |
| CROMPTON | Latest linked transcript | 17 | 559,632 | Pages 1, 2, 3, 4, 9, 13: 15,613 characters |

All listed downloaded documents returned parsable PDFs. The first three planned research demos are now TCS, KPITTECH and ASTRAL. CROMPTON was selected separately, outside the portfolio and demos, and went through the same ticker-to-page-to-document procedure. This validates a generic discovery approach on one extra ticker; the application engine and broad NSE coverage are not yet implemented or proven.

### Observed document URLs

- TCS annual: https://www.bseindia.com/xml-data/corpfiling/AttachHis/ad42e748-d73c-4c79-8c52-bcf1b1399bc1.pdf
- TCS transcript: https://www.bseindia.com/stockinfo/AnnPdfOpen.aspx?Pname=7dc14216-f892-46f1-bf82-5c7b387a83b9.pdf
- ITC annual: https://www.bseindia.com/xml-data/corpfiling/AttachHis/590b42ae-15c9-44cf-be69-e58053128a6b.pdf
- KPIT annual: https://www.bseindia.com/xml-data/corpfiling/AttachHis/4d2467e3-e28a-472b-8492-7fd9e46e63c4.pdf
- KPIT transcript: https://www.bseindia.com/stockinfo/AnnPdfOpen.aspx?Pname=a7331811-fe14-4c79-896d-f0a9df901335.pdf
- Astral annual: https://www.bseindia.com/xml-data/corpfiling/AttachHis/5772a6ee-bd33-47d5-bbd1-85b269bd26c3.pdf
- Astral transcript: https://www.astralltd.com/wp-content/uploads/2026/11/Equirus-Astral-Nov05-2026-1.pdf
- Crompton annual: https://www.bseindia.com/xml-data/corpfiling/AttachHis/685e1a8a-ced3-47bd-a15e-3509e7db4bd3.pdf
- Crompton transcript: https://www.bseindia.com/stockinfo/AnnPdfOpen.aspx?Pname=b6ca15fa-ca99-4b81-89d7-ed91ffbd96e0.pdf

## Findings that change implementation

1. Display source freshness per company: CERA was one daily bar behind most holdings.
2. Use NSE for the filing feed; do not spend the deadline attempting to repair the blocked BSE feed.
3. Use Astral instead of ITC for the third research demo, because its transcript path was validated.
4. Annual reports are 10-26 MB in these samples: prewarm demo documents, bound concurrent downloads, and provide progress for a new ticker.
5. pypdf produced fontTools-related encoding warnings on some annual-report fonts. Include fontTools when implementation is authorised, and verify extracted financial passages. Successful text extraction does not prove table accuracy.
6. Do not assume a link labelled latest is sufficient: validate document identity, reporting period and document type during ingestion.
7. Repeat price, filing, and PDF downloads from the actual hosting environment before committing to deployment. No hosted access or LLM response has been tested yet.

## Existing local runtime

Node 24.21.0; bundled Python 3.12.14; SQLite 3.53.1 with a successful in-memory FTS5 table check. pypdf and pdfplumber are present. FastAPI, uvicorn, httpx, Beautiful Soup and fontTools are not present in that bundled Python environment. No dependencies were installed or application files created.
