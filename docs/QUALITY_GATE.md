# KPI delivery quality gate — implemented 2026-10-27

## WHY
An earlier demo calculating paid-ad ROAS from **all store revenue / ad spend** could overstate paid-channel return. Correct numerator is only paid-attributed net sales; total store revenue includes Organic Search and Email, which must be excluded from paid ROAS. AI-generated code is not evidence of financial accuracy.

## WORKING IMPLEMENTATION
**Current deliverable source bundle in the 2026-10-27 ChatGPT chat:**
`Freelancer_KPI_Application_QA_v3.zip`

It contains actual executable files:
- `audit_kpi.py`: separate Decimal arithmetic, CSV schema/row reconciliation, duplicate detection, date/channel coverage, financial KPI recalculation, paid-only ROAS and CAC, dynamic target recomputation, JSON/CSV/HTML/PDF consistency, missing/invalid data blocking.
- `test_qa_fault_injection.py`: seven distinct corruptions simulated against disposable copies; all must produce FAIL.
- `BUILD_ALL.py`: after building, invokes the independent audit; nonzero exit on FAIL.
- `BUILD_AND_PACKAGE.py`: rebuilds, audits, runs negative tests, *then* atomically emits the delivery ZIP only if PASS; removes previous release before starting, so a stale release is not treated as fresh.
- `BUILD_WINDOWS.bat`: runs the fail-closed package command, shows error on failure.
- `QA_REPORT.json`: machine-readable assertion and metric summary; `RELEASE_MANIFEST.json` contains SHA256 checksums.

**Verified in this ChatGPT container (2026-10-27):**
- 2,806 synthetic orders + 184 daily channel ad-spend rows.
- **85,783 assertion evaluations passed**, mostly per-row finite/amount/uniqueness and calculated-output checks; do **not** misstate as 85,783 independent test cases.
- **7 negative fault-injection scenarios all blocked:**
  1. inflated paid ROAS; 2. order net-revenue inconsistency; 3. duplicate order; 4. missing ad-spend day; 5. tampered dynamic ROAS target; 6. changed HTML target; 7. malformed PDF.
- 3-page PDF rendered and third page inspected visually.
- Spreadsheet *separately spot-checked* with spreadsheet tooling: workbook Dashboard B7 = 192975.16 and D7 = 2.622836..., Monthly Inputs July/Feb/Sep totals matched; **full xlsx cell-by-cell audit is not yet part of automatic gate**.
- Example baseline: quarter net sales $192,975.16; attributed paid-channel revenue $104,275.26; ad spend $39,756.68; paid ROAS 2.623x.
- September Meta attributed ROAS 1.773x vs **illustrative cost-derived break-even** 2.287x. These are **SYNTHETIC** values, not real customer's KPI formula.

## CRITICAL LIMITS
This is a **synthetic portfolio demo**, not a production service or proof of live-client delivery reliability.
- The sample BUILD_ALL script **regenerates synthetic input from a seed each run**. In real client work, NEVER run it over customer CSVs. Build a separate read-only ingestion, immutable input snapshots and secure data isolation.
- Correct arithmetic cannot validate client data provenance, attribution accuracy, business definitions, whether ad lift is causal, or whether customer-provided targets are appropriate.
- Current automatic audit does not fully verify all Excel workbook cells, interpret every natural-language claim or test PDF appearance automatically. A visual/client review remains mandatory.
- Do not send customer data to ChatGPT/other external AI services until the customer's data policy authorizes it.
- Don't promote `QA PASS` as zero defects guaranteed, 100% correctness or enterprise compliance.
- Distinguish the per-row assert-evaluation count from fault-injection test count.

## REQUIRED REAL-CLIENT DELIVERY GATE
1. Owner-approved scope, exact KPI formula dictionary, client template and data-use permission.
2. Immutable input snapshot with SHA256, row-count/schema checks, timezone/currency/duplicates/refunds handling.
3. Independent recomputation from original exports using approved client semantics (Decimal where money).
4. Scenario and adversarial tests for zero denominator, negative/missing fees, duplicate payment/refund, missing channel, month-end, currency, target changes.
5. Cross-format reconciliation PDF, workbook, HTML/CSV and explanatory prose.
6. *STOP* if any discrepancy; save exceptions, seek resolution and rerun, do not quietly coerce.
7. Human visual review + KPI definitions/limitations + signed scope; only then delivery with a clear version and checksum.

## ACTION FOR USER
Before paying Connects, inspect Upwork's exact application cost and account visibility, download v3 ZIP, extract, open `dashboard.html`. Scripted rebuild optional; no paid API required. Loom still not recorded; application not submitted.

## What this repository does / does not store
The full source and binary artifacts are in the conversation downloadable ZIP, **not mirrored into this GitHub repo**. If the owner switches chats and files are not attached in the next chat, ask to upload that ZIP. Do not claim Github has copied binaries/source which were never committed.
