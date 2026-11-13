# BID AX v2 — three-module remote source sync, credential-free Onbid API planning

**As of 2026-11-14 KST.** User goal: full R01–R29 **85%**. **Official completion: UNASSESSED; not proven 85%.** `[작업중]`, RELEASE HOLD and no Kmong listing remain.

## New verifiable functionality

- The previously local-only Onbid (`bidax/onbid.py`) and court (`bidax/court.py`) evidence ledgers, matching CLI/GUI and 3-module tests were promoted into the private GitHub product branch; 8/8 exact remote content matches against local tested files.
- Onbid snapshot import consumes **authorized, manually normalized local JSON**, not raw API responses or unsolicited scraped data. It independently fingerprints announcement/property/condition and results and conservatively labels decisions `추가 확인 필요`.
- Court analysis requires explicit `--consent` and documented lawful possession; it records local PDF/TXT metadata and SHA256, not the PDF text, and does not make legal conclusions.
- `bidax/onbid_plan.py` adds three credential-free **nonexecutable** request plans: announcement assets dataset 15157220 with `pbancMngNo`, result list dataset 15157252 with `cltrTypeCd/prptDivCd/opbdDtStart/opbdDtEnd`, and result detail dataset 15157254 with `cltrMngNo` and optional `pbctCdtnNo`. Rejects unknown parameters and service keys, invalid dates/types, noninteger page counts and unsafe IDs. `operation_path=None`, `network_ready=False` until live specification and rights approval. No API secrets, calls, quota usage or external transfer.
- The documented *G2B-specific* seven-day query limit is **not** silently imposed on Onbid; Onbid currently has a distinct documented parameter contract.

## Evidence

- Local Linux Python 3.13.5 from the source ZIP: `python -Werror::ResourceWarning -m unittest discover -s tests -q` = **136 PASS, 0 FAIL, 0 SKIP** (prior 130 plus six Onbid planner tests); `python -m compileall -q bidax tests` PASS.
- `ast.parse(feature_version=(3,11))` on 22 `.py` files PASS; this is **syntax** verification, not actual Python 3.11 runtime or Windows 10/11.
- Deterministic `packaging/build_portable.py` Python zipapp built with all 15 files, SHA256 `2fe1de178782e3b3e6698630ca4ffc243503dc0a863953f3d6d223d13f61e0f1`; actual portable CLI `onbid-plan result_detail` emitted a safe nonexecutable plan without creating customer DB; Python required, **not an EXE/installer**.
- New code/docs GitHub commit and test CI must be read back independently after write. Blueprint metadata GitHub Actions SUCCESS does not mean Python/Windows suite PASS. Manual-only private Actions matrix not executed without cost/permission check.

## Full R01–R29 blockers / no official 85% claim

1. No owner-approved 100-point requirement weights; default arbitrary equal weighting prohibited. Existing R01–R21 work is partly verified with synthetic data but live original document rights/eligibility and customer acceptance are not complete.
2. Onbid real free OpenAPI key, user permission, response fields, pagination and official result reconciliation remain untested. R22–R26 **partial offline implementation only**.
3. Court PDF is fingerprinted only and not legally interpreted. Actual user-owned legal documents, document security, personal data retention and professional review not independently accepted. R27–R29 **partial offline implementation only**.
4. Real G2B/Onbid source 100 notices and 10 human decision cases, Windows10/11 executable/installer/SmartScreen/ACL, real PDF report, customer pilot, third-party attachment redistribution/licensing and final sale owner approval are still pending.
5. Do not move `[작업중]`/RELEASE HOLD/official `UNASSESSED` until 29 weighted acceptance and exact source-SHA real verifications are completed.

## Official source references

- https://www.data.go.kr/data/15157220/openapi.do (Onbid announcement assets)
- https://www.data.go.kr/data/15157252/openapi.do (Onbid result list)
- https://www.data.go.kr/data/15157254/openapi.do (Onbid result detail)
- https://www.data.go.kr/data/15129394/openapi.do (G2B)
- https://openapi.scourt.go.kr/kgso202m01.do (Court open API generally planned; partner integration via separate inquiry)
