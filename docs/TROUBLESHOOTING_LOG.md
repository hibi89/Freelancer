# KPI Reporting — troubleshooting and defect-prevention log

**Created:** 2026-10-27 KST  
**Scope:** Upwork lead U-001 and the **synthetic portfolio demo**, not a client's live production system.  
**Primary evidence:** [QUALITY_GATE.md](QUALITY_GATE.md), [APPLICATION_U001.md](APPLICATION_U001.md). Current v3 artifact is a separate ChatGPT ZIP; executable source/binaries **not** committed in this GitHub repository.

## Incident KPI-001 — wrong paid ROAS numerator (caught before any customer delivery)
- **Observed:** Early report divided **all-channel store revenue** (including Organic Search and Email) by **paid ads spend**, presenting that as paid ROAS. This inflates the attributed ad effectiveness.
- **Root cause:** Inadequate **metric semantic definition** and mix-up between whole-store sales and *paid-attributed channel sales*; a superficially plausible numeric result was not enough.
- **Impact:** Material misstatement risk. Without correction, advice to raise ad budgets may be financially harmful. No evidence this figure was delivered to a paying client.
- **Correction:** Define the metric contract explicitly:
  - Total store sales = all sales channels.
  - Paid attributed revenue = ads-sourced order net revenue for eligible paid channels only.
  - Paid ROAS = paid attributed net revenue ÷ paid ads spend, with stated assumptions and channel attribution limitations.
  - Distinguish ROAS (attributed) from causal incremental ROAS.
- **Independent countercheck (synthetic 2026 Q3):** whole-store net sales = `$192,975.16`; paid-attributed sales = `$104,275.26`; paid ad spend = `$39,756.68`; correct paid ROAS ≈ **2.623x**. Do **not** put whole-store sales over paid-spend denominator.
- **Preventive action:** Independently recompute from source order/spend CSV with Decimal; check month/channel/date coverage; compare exported JSON/CSV/HTML/PDF; corruption of ROAS must yield FAIL.
- **Resolution evidence:** `audit_kpi.py` + v3 results documented in QUALITY_GATE; forced inflated-ROAS mutation was rejected. **No customer acceptance or external audit claimed.**
- **State:** Fixed in synthetic v3 / future client adaptation required.

## Incident KPI-002 — static or undocumented targets not equal to customer's dynamic rules
- **Observed:** v1 had descriptive KPI performance without per-KPI data-derived targets, despite client requesting dynamic brand-specific target calculations.
- **Root cause:** Demonstration scope did not cover target-versus-actual on every required KPI.
- **Correction:** v2/v3 added 9 synthetic monthly/channel benchmark records. Example **September Meta paid ROAS = 1.773x versus illustrative retrospective break-even target = 2.287x**, with post-ad contribution `-$1,738.33`.
- **Formula in mock demo:** `net_sales / (net_sales - COGS - fulfillment - payment_fees)` from actual observed synthetic costs; denominator must be positive. This is a **retrospective mock financial floor**, not the customer's unknown dynamic-target specification.
- **Preventive action:** Never hardcode customer goals; obtain target formula/owners, align time windows and categories; perform independent recomputation and detect target JSON/HTML alterations.
- **Resolution evidence:** dynamic target recalculation and tamper injection blocked in v3.
- **State:** Demo gap addressed; customer formula awaits receipt after engagement.

## Incident KPI-003 — output drift across formats (anticipated, tested)
- **Failure mode:** CSV/JSON computation changes but report/PDF/HTML/workbook still show stale data, or the PDF is malformed.
- **Prevention:** Build from one versioned snapshot, cross-format invariants, artifact hashes, PDF parse/open check, plus visual review before release.
- **Observed adversarial tests:** Forged HTML target and malformed PDF were rejected by independent gate; workbook key fields separately spot-checked.
- **KNOWN GAP:** Full cell-by-cell workbook audit, visual appearance checks for all pages, and all narrative claims are *not* yet covered in automation.
- **State:** Controls partially implemented, more checks required before client production.

## Incident KPI-004 — duplicated, missing or inconsistent source rows (anticipated, tested)
- **Failure mode:** duplicate order ID; invalid net amount; missing ad spend for one date/channel; malformed currency or denominator. Unchecked source issues change KPIs.
- **Prevention:** reject invalid/missing/duplicate source data, nonfinite amounts, negative/malformed spend without explicitly defined refunds policy; require expected coverage, month aggregation reconciliation, currency/timezone rules.
- **Observed tests:** Duplicate order, wrong order net revenue, and missing ad-spend date produced FAIL.
- **State:** Demo guard checks exercised; extend for real refunds, mixed currencies, timezones and partial attribution once client data contract exists.

## Negative testing: 7/7 defects intentionally injected and blocked
1. Inflated paid ROAS.
2. Incorrect order-level net revenue.
3. Duplicate order.
4. Missing advertising-spend date.
5. Falsified dynamic break-even target.
6. Edited HTML displayed target.
7. Corrupted PDF.

**QA detail:** 85,783 automated assertion evaluations passed in demo (mostly row/invariant checks); this is **NOT 85,783 unique test cases**. No assumption of error-free future delivery.

## Mandatory remediation process for ANY real client error
1. **STOP / fail closed:** don't package/send incorrect result. If already delivered, flag it promptly to client with scope and potential impact, without inventing facts or hiding the issue.
2. **Record:** defect ID, observed result, expected result, original-data hash, date/version, affected files/KPIs, severity, reproducible steps, client guidance, source of metric definition.
3. **Isolate:** preserve readonly original inputs and failing outputs; redact customer PII and never put it in this repo.
4. **Root-cause:** separate bad source data, bad business formula, code defect, presentation mismatch, incorrect narrative and misunderstanding of client instructions.
5. **Fix + independent proof:** reproducible correction, regression test demonstrating fail-before/pass-after, independent source-based recalculation and relevant negative test.
6. **Release gate:** rerun all tests and cross-format comparison; human visual and analytical review; revision note and checksum; get client sign-off where appropriate.
7. **Retrospective:** improve acceptance criteria, tests and SOP; record closure date and evidence. Don't rewrite the original incident history.

## Delivery prevention levels
- **P0 before any client delivery:** read-only ingestion, approved KPI glossary + dynamic targets, source checks, independent arithmetic, cross-format assertions, fail-closed packaging, adverse-input tests, error trail, reviewer approval.
- **P1 before repeat deployments:** client-specific currency/refunds/timezones, full Excel cell audit, visual regression, narrative consistency proof, dependency pinning, recovery/rollback.
- **P2 for scale:** access control, immutable artifact storage, stronger data lineage, monitoring and audited runbooks subject to security constraints.

## Client-facing language — truthful, not 'zero error guaranteed'
> I use an AI-assisted workflow with independent Python-based KPI checks, source-data reconciliation, and a fail-closed report release gate. In my synthetic portfolio demo, I caught and corrected a paid-ROAS attribution mistake before delivery and added regression tests that reject manipulated metrics and malformed outputs. If shortlisted for the paid test, I will adapt those controls to your KPI definitions, dynamic target formulas, and report templates. I do not assume that a passing test eliminates every business-data risk, so I include a final manual review and clear exception reporting.

Don't imply this process is already deployed by the client, has been certified by an auditor, or ensures zero errors.
