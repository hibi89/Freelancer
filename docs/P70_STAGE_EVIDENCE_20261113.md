# BID AX — 70-stage local workflow verification

**Date:** 2026-11-13 KST. **User target:** full-blueprint final 70%. **Status:** offline P70 ENGINEERING MILESTONE completed locally, official final completion **UNASSESSED**, `[작업중]` retained, RELEASE HOLD, not listed on Kmong.

## Evidence and controls

- Private product source of truth: `hibi89/Freelancer@product/bid-ax-public-procurement`, `docs/FINAL_BLUEPRINT.md` R01–R21. All previous branches and excluded `hibi89/Bid_Owl` unchanged.
- Original baseline source GitHub commit `d614c08e611ef15d388865034ada215e10c8da6e`; verified matching source blobs for prior core/CLI/tests/README before modification.
- Local test: `python -Werror::ResourceWarning -m unittest discover -s tests -v` → **45 PASS / 0 FAIL / 0 SKIP** after P70 feature work. Python **3.13.5** is the observed runner, not proof of Windows10/11/Python3.11 compatibility.
- GUI headless smoke: `xvfb-run -a python [Tk launch with timed destroy]` → `TK_GUI_SMOKE_PASS`, Tk **8.6**, Linux virtual display. Actual customer Windows GUI acceptance **NOT_RUN**.
- Other local negative cases: DB payload tamper, stale source version review, duplicate review replay, CSV formula, HTML injection, existing DB/report overwrite, unrelated/corrupted backup, invalid JSON and atomic import all checked.
- Source code/commit SHA GitHub readback to be confirmed after commit, CI/real browser/Windows/official API/real bidder/customer acceptance **NOT_RUN**. No developer key, real customer data, payment, external requests or third-party AI.

## 21 full-scope requirements — latest bounded implementation status

| ID | Evidence | Remaining full acceptance |
|---|---|---|
| R01 | Official dataset metadata/7-day restriction; no live key | Current operation rights and business terms / live use |
| R02 | Offline query-plan operation only | Actual authorized listing/detail pagination and reconciliation |
| R03 | API key not accepted/persisted in product | Customer key safe handling, real quota/retry/429 policy |
| R04 | Official-domain HTTPS source link guard | Original official attachments and version/timestamps |
| R05 | Strict normalized notice + profile fixtures | Real response field contract against official sample |
| R06 | SHA256 payload fingerprint + append-only version ledger + changes | Live version semantics/attachments |
| R07 | SQLite integrity check, duplicate-safe atomic import, create-only backup & restore | Customer DB migration, crash/power-off recovery, actual Windows test |
| R08 | Company profile JSON with strict local validation, GUI load | Secure multiple persistent profiles and evidence lifecycle |
| R09 | Region/license/budget preliminary screening | Original legal qualification verified by human |
| R10 | Unknown/missing clause yields explicit manual review | Real original document discrepancy trials |
| R11 | Document-name/expiry checklist by user-provided profile | Actual attachments and license certificate verification |
| R12 | KST/timezone deadline + on-demand due alerts | Local scheduler/after-resume refresh and notification |
| R13 | JSON, BOM-CSV injection-safe, printable CSP HTML report | PDF, customer Korean font/print acceptance |
| R14 | Human append-only review/audit events, UUID idempotency and stale snapshot protection | Authenticated owner/reviewer role separation and acceptance |
| R15 | Per-version field diffs and history | Official amendment polling and durable source checkpoint |
| R16 | Offline Tkinter guided GUI for core workflow | Real Windows10/11 UX and accessibility testing |
| R17 | No Windows installer/EXE yet | Signed/unsigned packaging, install/uninstall |
| R18 | SQLite hash/quick_check, input file size guard, no-overwrite backups/restore | Secure at-rest key vault, filesystem permissions, disaster recovery |
| R19 | 45 synthetic local tests only | 100 authentic notices and 10 independently reviewed qualification cases |
| R20 | Warnings+restricted scope; official terms metadata | Legal and commercial terms/guide/support acceptance |
| R21 | Local host CLI and virtual Xvfb GUI only | Actual Windows customer pilot + owner release approval |

**No approved R01–R21 weights.** Do not convert the P70 technical scope, 45/45 test pass, or number of visible screens into official “70% final completion”. Cannot remove `[작업중]` until weighted entire-blueprint acceptance. Old P50 is historical progress; current internal target P70 does not imply 50% verified previously.

## Architecture comparison (unchanged decision)

- **A. Hosted SaaS/crawler:** always-on ingestion but infra recurring cost, secrets and users' contract documents exposed to server, higher outages and compliance burden.
- **B. Customer PC local Tkinter/SQLite:** zero mandatory hosting costs, deterministic offline audits, backup/restore and no server secrets; PC must be on and records may be stale. **B kept** for P70 to preserve privacy/cost and limit operational risk.
- API plan respects official 2026-11-10 7-day restriction ([data.go.kr dataset 15129394](https://www.data.go.kr/data/15129394/openapi.do)). No live scraping, actual API ingestion, unattended notification or bid submission.

## Operating instructions and recovery

1. `python -m unittest discover -s tests -v` from repo root, then `python -m bidax.cli --db ./customer.db gui` (Tkinter required). On headless Linux, use `xvfb-run -a ...` only for smoke, not a Windows equivalence claim.
2. From GUI: select local company JSON → import normalized authorized notices JSON → click preliminary screening → inspect source/time/warnings → optionally record explicit human review → export a **new** JSON/CSV/HTML path → backup DB to a **new** path. Backend CLI supports same flow.
3. To restore: `python -m bidax.cli --db /new/path/restored.db restore /old/path/backup.db`. **Must use new destination; never overwrite the old DB.** Verify existing DB/backup before migration. Source modification/repo rollback only with owner approval.
4. All `*.db`, `*.db-wal`, `*.db-shm`, secrets and customer profile JSON remain local and are not GitHub assets. `.gitignore` blocks DB and secret paths.
5. If a source record changes after screening, manual review fails and demands re-screen; if payload hash differs, ledger fails closed. Previously published reports are immutable snapshots and may be stale.

## Next 70→85 priority

- Official API 1.3 spec and real authorized JSON/XML mapping, limited retry/backoff and secret handling; 100 live notices and 10 human source checks before any final claim.
- Python 3.11 + Windows10/11 manual GUI, multi-profile persistence and KST reminders with resume checkpoints; installer EXE and Korean report/PDF rendering, customer backup migration.
- Secure role separation/customer pilot, commercial terms & API provenance; independent full-blueprint requirement weights/owner acceptance, then update central Kmong completion registry, not the other 28 sources.
