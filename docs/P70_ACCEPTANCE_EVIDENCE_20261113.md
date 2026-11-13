# ONTOINSIGHT AX — 70% engineering checkpoint evidence (2026-11-13 KST)

Full final blueprint: docs/FINAL_BLUEPRINT.md. The official overall 100%-denominator completion remains **UNASSESSED**, not 70%, because approved 100-point weights for all scope and requirement-level proof are incomplete.

| P70 phase criterion | Technical evidence | Status |
|---|---|---|
| Existing P50 CSV SHA/meaning candidate/synthetic KPIs | Original P50 module, included 11 tests | PASS (synthetic) |
| Bounded XLSX + multiple CSV 2-3 sources | New ontoinsight_p70.py and 31 tests, mixed Excel/CSV cases | PASS (synthetic) |
| Explicit business mapping/source digest/reviewed join cardinality | review_sources / approve_mapping / run_approved with digest verification | PASS (local attestation only) |
| Orders/refunds/channels accurate exact totals | per-order Decimal ledger, refund-to-parent, channel 1:1 and 1:N refund, independent summary | PASS (synthetic) |
| Original bytes protected, outputs new | source SHA + CLI exclusive output + negative tests | PASS (synthetic) |
| CLI user flow actual original-source runners | review → attest → run, no-overwrite/digest drift | 2 PASS (Linux + Windows) |
| Official full-blueprint 70% | No approved whole-100 weights; P85+ missing | UNASSESSED / NOT MET |

- Implementation repo: `hibi89/AI_AutoML_Analyst@feature/ontoinsight-ax-p70-20261113`. Exact functional SHA `34e7b16a2fef5e1b0d21f4e6d097c6faaaaf9012`; docs HEAD `0e831106c03efb5ba6cba4d840dcfecf73ec235f`.
- [CI #43378733016](https://github.com/hibi89/AI_AutoML_Analyst/actions/runs/43378733016): Python3.11 Ubuntu24.04 44 PASS / 0 FAIL / 0 SKIP, Windows Server2025 44 PASS / 0 FAIL / 0 SKIP, 2/2 SUCCESS, compileall PASS.
- Sample synthetic: orders 3, gross 500.00, refund 35.00 (3 events; including two on one order), net 465.00, AOV 155.00. No real customer records processed.
- Key limitations: only 2/3 bounded files; first visible sheet; exact approved gross/refund financial semantics and currency, not cost/period/tax conversion. Local actor attestation is **not identity verification, authorization proof or legal e-sign**. Duplicate identical refund events lack unique ID. No customer Windows10/11 or full original regression, no ML leak gate, no HTML/PDF/XLSX delivery, no sales rights review.
- Operational state: `[작업중]` retained; original AutoML releases and other product markers unchanged; `RELEASE HOLD`, original code/data unchanged, no Vercel/Production. Next P85 ML+report, P95 physical/rights, P100 final customer/owner acceptance.
