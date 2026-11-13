# WORKNOVA Desk — complete final product blueprint

Baseline: the 2026-11-12 central KMONG three-product candidate and 2026-11-13 owner P50 development command. Whole-product scope remains unchanged. A formally validated final-completion percentage requires approved weights and item-level proof; the bounded P50 engineering milestone is not automatically 50% of the final design.

## Buyer problem and target
Korean freelancers and small agencies need a single local tool for customer registration → tax-aware KRW quote → agreed scope and work milestones → revisions and delivery acceptance → recorded receivables → printable customer evidence and recoverable history. Hypothetical Basic 49,000 / Standard 119,000 / Premium 199,000 KRW pricing, not a validated offer.

## Architecture alternatives
| Model | Performance/cost | Security/maintenance | Decision |
|---|---|---|---|
| A: PayPal/cloud/AI marketplace | requires hosting and external connectivity; recurring cloud/provider costs | accounts, webhooks, personal data, payment compliance | not for this local product |
| B: independently authored local-first Python 3.11+ SQLite engine and later guided Windows GUI | fast local transactions, no mandatory cloud charges | DB and backups need OS protection and migration policy | selected |

No PayPal API or other original hackathon code is imported; the original quote→contract→milestone concepts are used as functional background only.

## Complete requirement IDs (full scope; no owner-approved percent weights yet)
| ID | Buyer-facing acceptance | Current state |
|---|---|---|
| WD-01 | customer/identity CRUD with safe roles and disclosure controls | local create/search/list; edit/delete/multiuser roles pending |
| WD-02 | integer KRW line items, explicit 10% VAT/tax-exempt and rounding, invalid money rejected | core and regression tested |
| WD-03 | immutable versioned quote and separately recorded approval | **v2 revisions + parent lineage, distinct approvals, local tests**; buyer verification pending |
| WD-04 | contract scope tied to approved quote, separate human activation | core and test |
| WD-05 | one-to-many milestone sum, ordered state, validation | core and test |
| WD-06 | delivery evidence, revision rounds, explicit buyer acceptance; robust change history | basic separate transitions tested, rich history pending |
| WD-07 | partial manual collections, remaining balances, idempotent references, no automatic payment | core and test; external settlement not validated |
| WD-08 | auditable append-only event integrity, detection and safer reconciliation | SHA256 hash-chain test; owner rewrite not prevented |
| WD-09 | durable SQLite, point-in-time backup, restore drill, migration, failure isolation | v1 backup+explicit migrate, SHA-pin restore-new, integrity/audit regression; Windows recovery pending |
| WD-10 | privacy-safe client JSON/HTML, clear fee/tax wording and offline provenance | redacted reports and quote preview with CSP escaped markup tested |
| WD-11 | end-user Windows GUI workflow with search, customer/quote selection and error guidance | Tk prototype and Xvfb widget flow PASS; actual Windows/UX NOT_RUN |
| WD-12 | Korean DOCX/PDF with fonts, version preservation, print UX | NOT BUILT |
| WD-13 | secure Win10/11 install/upgrade/uninstall, local access controls, encrypted storage option | NOT BUILT |
| WD-14 | 10+ realistic industry samples, legal/tax review, rights/NOTICE, commercial owner acceptance and support | NOT RUN |

## Data and money contracts
- Input item `{description: string, quantity: positive integer, unit_krw: positive integer}` (1..100 lines); no float, no external pricing API. Taxable subtotal VAT `(subtotal+5)//10` (10% round half up to 1 KRW); non-taxable VAT 0. All milestone gross amounts sum exactly to the approved quote total.
- Tables: `customers`, `quotes`, `contracts`, `milestones`, `receipts`, `audit_events` in a customer-owned SQLite v1 file. Foreign keys, `BEGIN IMMEDIATE` transaction and `PRAGMA integrity_check`.
- State: quote DRAFT→APPROVED, contract DRAFT→ACTIVE on named human action, milestone PLANNED→DELIVERED→(REVISION_REQUESTED→DELIVERED)*→ACCEPTED. Only accepted milestone accepts a manual payment note, with partial receivables and no excess amount or duplicate reference.
- No PayPal CREATE/CAPTURE, bank account query, automatic sending, paid AI, digital signature or tax filing. `reference` is an owner-entered string, **not bank verified**. Human/legal acceptance separate from app status.
- No personal data sent via network. The local SQLite file is **not encrypted** and audit hashes do not prevent a full DB rewrite. Protect it with OS file permissions/encryption and never publish customer data.

## Engineering gates vs formal completion
- **P50:** independently implemented offline ledger, KRW/VAT, discrete human approvals, contract/milestone/receipts, event audit, backup and executable CLI/regressions.
- **P70:** guided GUI, full quote revisions/history, recovery/migration and failure UX, quote document previews. Locally implemented on Linux Python/Tk Xvfb; full Windows/customer/formal 70% **not yet certified**.
- **P85:** robust Korean DOCX/PDF and Windows build/installer with security/retention/role tests.
- **P95:** real Windows10/11, at least 10 scenarios, migration/backup drill and legal/license checks.
- **P100:** end-customer acceptance, support/returns, clear full coverage and owner release approval.

These stages are directional deliverable gates, **not agreed 100-point weights** for the entire WD-01..14. Formal final-completion rate remains UNASSESSED until approval and exact-SHA evidence.
