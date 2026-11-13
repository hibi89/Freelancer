# WORKNOVA Desk P85 customer lifecycle/evidence follow-up — 2026-11-13 KST

- **Official final design completion UNASSESSED / user P85 target NOT CERTIFIED**, `[작업중]` retained, **RELEASE HOLD**, no actual Kmong listing or Production. Canonical WD-01..WD-14 unchanged; owner-approved percent weights not available.
- New functional WD-01 partial: customer rename with stale-write/explicit confirmation; delete unused customer only and preserve financial history. No customer-name hash or name in event. Single-owner strings are **not authentication**.
- New functional WD-06 partial: explicit local file selection (<=64MiB) in DELIVERED milestone; record only SHA256, bytes, milestone ID; idempotent duplicate; later read-only reverify. No external delivery/receipt proof, no file content or path saved. CLI and Tk GUI integrated.
- Schema v2 and existing P50/P70/P85 code/backup/quote/contract/receipt untouched. Portable Python-required ZIP allowlist updated to 12 source/script files. No EXE, paid CI or Windows install executed.
- **Local Linux Python3.13.5: unittest 81 PASS/0 FAIL/0 SKIP; Tk8.6 Xvfb GUI 2 scripted flows PASS; compileall PASS; extracted ZIP verifier 12/12 PASS and CLI init PASS.** Local scripts do not independently prove Windows product QA. Tests and specifics: `docs/P85_CUSTOMER_EVIDENCE_20261113.md`.
- Blockers: physical Windows10/11 PowerShell+Word/PDF+security, role auth/retention, encryption, legal/font rights, real buyer E2E and owner-approved weight matrix. `P85` remains a bounded engineering milestone, not official 85%.
- Verified predecessor feature SHA `affb062c6251bc5ff253a8d855c7672298afe39d`; new GitHub code SHA to be read from branch after commit. Original PayPal hackathon, Freelancer main/all other branches, user DB and secrets unchanged. No Vercel/Production URL (N/A).

---

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
