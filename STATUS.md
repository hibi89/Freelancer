# STATUS — WORKNOVA Desk P85 hardening (latest, 2026-11-13 KST)

- Full WD-01..WD-14 blueprint unchanged; **official final-completion UNASSESSED / target 85 NOT certified**. Candidate remains **[작업중] / RELEASE HOLD / not registered**, no Production.
- Newly implemented: user-triggered independent checkpoint of six table hashes/audit head, offline SHA verification, no plaintext customer rows in checkpoint; portable v2 exact ten-source-file verification before GUI/data directory and stronger installer allowlist. No existing business DB/schema changed, no external payment/AI/network.
- Linux Python3.13.5 unittest **68 PASS/0 FAIL/0 SKIP**, Linux real Tk8.6 Xvfb scripted E2E PASS, compileall PASS. Real Win10/11 PowerShell/installer/Word/Defender/unsigned code rights/customer E2E **NOT RUN**; product Actions not run in this patch. Existing local P85 52 PASS retained within 68.
- This newer source adds integrity checkpoints but does not supply a signed EXE, real OS user authentication, disk encryption, guaranteed payment receipt, or buyer/legal acceptance. A stolen/replaced checkpoint can be rewritten by an attacker with both files; separately archive returned SHA and proof.
- Pre-change exact verified GitHub branch HEAD `7fdea1bf0d031fcd4d500d2f3b31d59a49e99124`; new feature SHA shall be verified after remote commit. Backup/recovery: checkout prior source commit; leave user database unchanged, user-owned external backups preserved. Original PayPal and Freelancer main unchanged.
- Full evidence and commands `docs/P85_HARDENING_20261113.md`; next gate Windows non-admin upgrade/rollback, license and business acceptance, owner-approved weights. No charge/permissions/Production actions.

---

# STATUS — WORKNOVA Desk scoped P85 implementation (2026-11-13 KST)

**Repo:** `hibi89/Freelancer` (Private), branch `product/worknova-desk-local`. **Official final-blueprint completion: UNASSESSED**, user P85 objective **not certified**. KMONG `[작업중]` remains; **RELEASE HOLD / not registered / no Production**.

## Implemented and locally verified

- P50/P70 intact: offline KRW + VAT quote, explicit quote approval, immutable versioned revisions, approved contract, milestone states/acceptance, manual payments/receivables, audit, v1 migration/backup, hash-verified new-path restore and Tk GUI.
- New P85: redacted-by-default Korean standard-library DOCX for quote and contract progress; optional PDF using ReportLab + caller-provided font (no font bundling); GUI export actions; path no-overwrite, explicit dual privacy flags, audit check and SHA256 receipts.
- New P85: deterministic source-only portable ZIP and file SHA256 manifest, candidate per-user Windows `install_local.ps1` and `launch.cmd`, app-data split/rollback/uninstall preserving user data. This **requires Python** and is not a signed EXE/installer. Real Windows action NOT_RUN.
- Local Linux Python3.13.5 52/52 unittest PASS, 0 FAIL, 0 SKIP. Tk8.6 Xvfb scripted user-flow PASS. `compileall` PASS. PDF bytes and Korean text parsed using host-installed NanumGothic fixture (not part of product), DOCX read using python-docx. 10 synthetic industry finance/lifecycle cases PASS; *not* customer acceptances.

## Open official full-design requirements

WD-01 real roles and data lifecycle, WD-06 external delivery evidence, WD-08 tamper-resistant independent proof, WD-09 secure customer recovery, WD-11 native Windows UX, WD-12 actual Windows Word/Print and font license, WD-13 self-contained signed Windows package/ACL/encryption, WD-14 10 actual accepted user cases, legal/license/NOTICE/support/sale approval. Owner-approved whole-product 100-point weight matrix is unavailable; numeric score must not be invented.

## Safety / recovery

- PayPal hackathon source, Freelancer main and other product branches and existing customer DB untouched. P70 predecessor Git commit `16d08b79621a303e190835a74885d58d75d513d9` is the rollback code reference; **do not use older writer against a migrated v2 DB**.
- Backups/new exports are explicitly user-owned and never silently overwritten or transmitted. No font included. Installer scripts have not been executed on Windows. Sensitive SQLite remains unencrypted; user must protect folder with OS permissions/encryption.
- Product SHA to be filled by exact GitHub source commit readback. No Actions Windows/Production run for this SHA, no actual payment or commercial test.

Evidence: `docs/P85_TRACE.md` (full WD-01..WD-14 rows). **RELEASE HOLD**.
