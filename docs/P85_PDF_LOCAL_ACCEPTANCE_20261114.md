**2026-11-14 원격 사후검증:** source SHA `2de90f3e1231d945b8fcec322f02194003b37098`, 11/11 source/docs content readback, Author·Committer GitHub hibi89. Blueprint evidence Actions #43504668031 SUCCESS **not** Python CI; 151/151 local Python3.13.5 only. No live API, Windows, customer or 85% approval.

# BID AX P85 follow-up — local PDF export and consented court preview

**2026-11-14 KST, FULL blueprint R01–R29 maintained.** User final 85% target **not yet met or verified**; official score `UNASSESSED`, `[작업중]`, RELEASE HOLD, not listed on Kmong.

## Concrete changes

- R13 local PDF export: `bidax/pdf_report.py` + existing `workflow.write_new_report` + CLI `export --format pdf` + desktop export. Uses optional ReportLab and its Korean CID mapping without bundling OS font binaries. Generates source-linked preliminary screening, with Korean title, timestamps, statuses, reasons, source fingerprint, and explicit nonlegal disclaimer. Create-only path and rollback on error. PDF viewer/Korean rendering/third-party font use require final customer acceptance.
- R27/R28 consented PDF/TXT preview: `bidax/court.preview_document` + `court-preview --consent` CLI. Uses optional pypdf for PDF max 5MiB / 12 pages (configurable <=20), rejects encrypted/active/annotated PDFs and large text, returns *category keyword mentions only*, records no full original text or legal findings. Does not OCR scanned documents, certify virus absence, validate title, identify owners, decide priority rights, or infer eligibility. Existing metadata-only court import unchanged; PDF data never sent to remote service.
- Optional packages were available locally: ReportLab 4.4.9 and pypdf 5.9.0. Neither is vendored, no font binaries bundled. Missing optional dependencies allow standard-library core to continue; relevant tests skip with explicit reason.

## Actual verification

- Isolated previous-sources ZIP extracted; prechange regression `python -Werror::ResourceWarning -m unittest discover -s tests -q` **136 PASS / 0 FAIL / 0 SKIP** (Linux Python3.13.5).
- After changes `python -Werror::ResourceWarning -m unittest discover -s tests -v`: **151 PASS / 0 FAIL / 0 SKIP** locally when optional packages present; compileall PASS. New 15 tests cover PDF creation/CLI/no overwrite, invalid prelim report, consent gate, malformed/active/encrypted PDF rejection and absence of full text in output.
- No authorized API key/real agency call/official 100 notices/human 10 legal checks/Windows10–11 physical run/Windows EXE or installer/customer acceptance/legal rights/production executed. GitHub exact SHA/readback to be recorded after upload, do not extrapolate local 151 PASS into remote CI.

## Remaining blockers and user boundary

1. User-owned free API approval & verified real response/rights; human independent evidence for actual cases, no unapproved customer data transfer.
2. Real Win10/11 Python runtime, GUI, PDF Korean fonts, installer/signature/SmartScreen, customer backup and security trials.
3. Full R01–R29 owner-approved weights/specific acceptance and independent SHA evidence. **Cannot claim final 85% without these.**

## Safe recovery

Existing `hibi89/Freelancer@product/bid-ax-public-procurement` verified prior HEAD `d295a8869689272f14a37864716e69093d5ca351`. No force update to prior commits; code changes restricted to PDF optional module and integration. The original `hibi89/Bid_Owl` and unrelated product branches are untouched.
