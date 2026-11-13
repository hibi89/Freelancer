# ONTOINSIGHT AX P85 acceptance evidence — 2026-11-13 KST

**Technical milestone P85: synthetic/Linux+Windows CI verified. OFFICIAL user whole-final-design completion: UNASSESSED. [작업중] and RELEASE HOLD retained.**

## Exact remote evidence
- Product source: `hibi89/AI_AutoML_Analyst@feature/ontoinsight-ax-p85-20261113` executable SHA `8d1bdc80ed345485591f739aace632e91112a604`, documentation/handoff SHA `d027481b886bd86b75f5e44b73250e4e3c0948b3`.
- [Actions #43383793303](https://github.com/hibi89/AI_AutoML_Analyst/actions/runs/43383793303) **2/2 SUCCESS**. Ubuntu24.04 93 PASS / 0 FAIL / 0 SKIP / one expected malicious-ZIP duplicate warning; Windows Server2025 93 PASS / 0 FAIL / 0 SKIP / same warning. `compileall` PASS both. Separately rerun source-defined 30 distinct test selectors **30/30 PASS each OS**; 30 cases are a subset of the 93, not an additional 30 distinct tests.
- Legacy P50/P70 retained. First P85 SHA `d8ac0644` Linux 90 PASS/3 FAIL caused two expected-error/fixture mismatch and real duplicate-timestamp CV risk; fixed at `8d1bdc80ed345485591f739aace632e91112a604` by fail-closed duplicate timestamp policy. Unfixed approach must not be reused.

## Approved P85 stage acceptance crosswalk
| Roadmap item | P85 source/tests | Observed scope |
|---|---|---|
| ML target/type/feature availability & leakage guard | ontoinsight_p85_ml.py + test_ontoinsight_p85_ml.py | explicit plan attestation, forbidden ID/future columns, small/bad classes abstain: synthetic PASS |
| Time/group holdout and fold local training/CV | sklearn pipeline, GroupShuffleSplit/GroupKFold, TimeSeriesSplit, KFold/StratifiedKFold | models and Dummy evaluated within train only, separate heldout; duplicate times HOLD: synthetic PASS |
| Dummy baseline comparison & ML_NOT_SUITABLE | 22 ML tests + 8 edge tests | 1 bounded challenger vs Dummy, no business/causal guarantee, no model download: PASS |
| Offline HTML/Excel/PDF/JSON report | ontoinsight_p85_report.py + test_ontoinsight_p85_report.py | static CSP HTML, XLSX aggregated chart, text PDF, source-bound JSON, ZIP manifest and tamper/reconciliation check: PASS |
| Core 30 of original 36-threat quality/security test list | scripts/ontoinsight_p85_core30_gate.py | 30 distinct **selected test selectors** each OS PASS; not complete customer acceptance for each scenario |
| Linux/Windows CI | exact SHA Actions #43383793303 | both hosts 93/93 PASS + selected 30/30 PASS; no physical client OS |

## Quality and limitations
- Selected 36-catalog case IDs: 01,02,03,04,05,06,07,09,11,12,13,15,16,17,19,20,21,22,24,25,26,27,28,29,30,31,32,33,34,35. See original repo core30_gate.py for 1:1 test selector audit and detailed QA docs/qa/ONTOINSIGHT_AX_P85_20261113.md.
- Not in core gate: 08 actual Unicode/space filesystem path; 10 symlink; 14 real Excel serial-date/timezone; 18 same-customer multi-order and privacy; 23 canceled/refunded event de-dup with true event ID; 36 actual client Windows10/11 with independent amounts. Case 12 tests malformed XLSX blocking, not actual password-protected workbook; true encrypted XLSX gate not verified.
- Customer permissions, actor real identity, explicit signed business definitions, multi-user isolation, retention/erasure, privacy threat review, third party licenses/NOTICE, customer Windows10/11 and all PDF pages/fonts, full old AutoML regression, external factual/causal/financial output validity and actual customer source usage **NOT VERIFIED**. PDF uses technical English text, Korean customer PDF typography remains future.
- ML is optional and requires separately approved local ML CSV plan. A reported baseline difference is not business profit, calibrated confidence or causal impact. Time duplicate conservatively abstains. No network/external LLM/paid API.
- P70 exact synthetic order sample 500 gross/35 refund/465 net/3 orders/155 net AOV, output built exclusively from validated source/receipt then independent ZIP verification; originals never overwritten.

## Full design and remaining gates
- This P85 phase uses the existing engineering roadmap; it **does not** make the entire user final blueprint 85% complete. The approved 100-point requirement weights are absent; official progress is **UNASSESSED**, not 85%. Historic AutoML independent engineering 95% is not inherited.
- P95: genuinely encrypted XLSX, complete 36/36 independent QA, actual owner Windows10/11, real authorized source/rights, full original regression and performance, report visual/fonts/NOTICE. P100: end-user formula agreement, acceptance/redo/retention/support/tax policy and explicit commercial GO.
- `hibi89/Freelancer@product/ontoinsight-ax-data-analytics` is a design/ownership branch; live code remains in separate `hibi89/AI_AutoML_Analyst` feature branch; originals/main unaffected; no Vercel/Production. Keep central kmong `[작업중]`, HOLD, registration history untouched.
