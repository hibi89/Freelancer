# BID AX — full independent product blueprint v1

**Purpose:** Public procurement preparation assistant for authorized bidder staff on a customer-owned Windows PC. Reduce manual bid search, evidence checking, deadline loss and version confusion; never autonomously submit bids or guarantee legal eligibility. This blueprint is the product's full 100% denominator, not the short prototype.

## End-to-end flow

Official authorized API+original document with source time/version → seven-day bounded incremental collection and local checkpoints → normalized immutable source-linked notice ledger (dedupes/revisions) → customer-controlled profile/verified licenses, regions, price and documents → deterministic fail-closed three-state preliminary screening + human approval → document checklist/expiry/deadline/reminder → printable Korean/JSON/PDF evidence report + backup/restore → customer acceptance.

## Requirement trace (full 100% product scope, approved weights not assigned)

| ID | Outcome / acceptance evidence | 2026-11-13 offline prototype |
|---|---|---|
| R01 | Official data.go.kr API current terms/operations, rights and provenance record | metadata checked; no live authorization |
| R02 | Authorized incremental listing/detail collection, all bid types, pagination | pure seven-day query plan only |
| R03 | Customer-owned API key, quota, throttle, retries and 429/5xx | unimplemented |
| R04 | Official source original attachments with timestamp and source version | official-domain URL guard only |
| R05 | Normalized notice field contract and validation | implemented + unit tested |
| R06 | Per-notice version history/immutable fingerprint/idempotent import | implemented + unit tested |
| R07 | Transactional local SQLite, dedupe, failure recovery | core implemented, restore unimplemented |
| R08 | Profile input validation, offline read/export | implemented input path; no profile persistence |
| R09 | Region/license/budget-based rules with explanations | prototype tested; real qualification unverified |
| R10 | Missing/unknown info never construed as legal qualification | review/fail-closed warnings tested |
| R11 | Required supporting documents with expiry and missing checks | prototype tested; no file inspection |
| R12 | Correct timezone deadlines and reminder scheduling | deadlines tested; reminders unimplemented |
| R13 | Audit/source-linked report + JSON/CSV/PDF export | JSON CLI only |
| R14 | Human final review/acceptance record and role separation | unimplemented |
| R15 | Update diff, deadline monitoring/checkpoint after PC resume | event history only |
| R16 | Korean interactive Windows GUI and guided setup | unimplemented |
| R17 | Windows installer/EXE, migration/uninstall/SmartScreen tests | unimplemented |
| R18 | Encryption/access hygiene, secure key handling, backup+restore | no key kept, backup created; restore unimplemented |
| R19 | 100 live notice cases and 10 qualification reviews incl. failure | unimplemented |
| R20 | Licensing/rights/terms, disclaimers, user guide and support | metadata checked; legal/customer acceptance unimplemented |
| R21 | Actual Windows10/11/customer pilot and owner release approval | unimplemented / RELEASE HOLD |

## Two designs and approved execution path

A — Hosted crawler/SaaS: stronger always-on, weaker infrastructure/PII/key security and recurring fees, larger ops burden. B — local Python/SQLite customer-owned key: zero required server fees, offline evidence security, cheap testability, but relies on on-PC refresh and user API quota. **B selected for the explicitly requested backend-first prototype**. The selected option does not erase any final R01-R21 acceptance gates.

## Official API context verified 2026-11-13

Official portal https://www.data.go.kr/data/15129394/openapi.do shows update **2026-11-10** and the max query period changed from one month to **seven days**, with JSON/XML, free use, license shown as unrestricted and developer baseline **1,000** requests. Service type-specific operations must be used; only the request-plan helper is implemented. No user key acquired, no remote call, no access to real notice, attachments, or business records. Full commercial conditions will be reconfirmed before sale.

## Progress and independent scoring

The 50-stage prototype target is an independent offline engine, input/output contract, API/rights metadata review and tests. The complete 100% blueprint has 21 requirements, many still absent. User-approved requirement weights remain **NOT_APPROVED**; therefore official final completion **UNASSESSED**, independent of the stage label. Never overwrite previous final completion records or release status based on a milestone pass alone.
