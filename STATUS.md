# STATUS — WORKNOVA Desk P85 continuation, installer + lost-ledger safety (2026-11-13 KST)

**Repo:** Private `hibi89/Freelancer@product/worknova-desk-local`.
**Owner objective:** 85% of COMPLETE WD-01..WD-14 final blueprint; **official percentage UNASSESSED / NOT CERTIFIED**. Unapproved candidate rubric `docs/FINAL_BLUEPRINT_WEIGHT_PROPOSAL.md` is explicitly NOT an accepted denominator. Keep central KMONG **[작업중]** and **RELEASE HOLD**. No KMONG registered product or production deployment.

## Newly implemented, verified locally

- Fixed two demonstrable Windows installer logic defects: `verify_portable.py` was erroneously rejected by an overrestrictive PowerShell allowlist, and `FILE_MANIFEST.json` was omitted when copying the installed application. Installer stages manifest and checks all hashes before replacing prior app; retains app rollback and untouched Data directory.
- Corrected Windows launcher verifier root from quoted trailing-backslash `%~dp0` to `.` after pushd; the new package verifier refuses injected `__pycache__` / bytecode / unexpected executables.
- Prevented silent empty customer ledger creation: all CLI commands except `init` use SQLite `mode=rw`; GUI asks explicit first-run confirmation if DB is missing; no file is created on refusal. New POSIX DB created with `0600`; existing DB permissions untouched. Windows OS ACL/security settings remain unverified and unchanged.
- **97/97 Linux Python3.13.5 unit tests PASS**, 0 FAIL/0 SKIP (previous 81 + 16 new).
- **3 real Linux Tk8.6 Xvfb GUI smoke flows PASS** (existing sales workflow, customer delivery evidence, new first-run DB guard).
- `python -m compileall -q worknova_desk scripts` PASS; stage simulation `verify_portable()` and corruption negatives included in 97 tests. A Linux staging simulation is **not** a Windows PowerShell test.
- Detailed evidence: `docs/P85_INSTALL_DB_SAFETY_20261113.md`. Exact remote commit SHA and package extraction tests to be recorded at final GitHub write verification.

## Remaining blockers

- Native Windows10/11 non-admin PowerShell install/upgrade/rollback/uninstall/GUI/Word/PDF/Defender, tested standalone code-signed EXE, verified OS access controls and encryption, offline customer privacy and authorized user, legal/font rights, 10+ REAL buyer acceptances, approved 100-point rubric — **NOT RUN/NOT APPROVED**.
- Local `actor` names are labels, not user authentication. SHA/manifest protect against accidental corruption only; not signature/independent proof. SQLite disk remains unencrypted. No bank/PayPal/API settlement.

## Safety and recovery

- Previous verified feature commit `6f24ccea44c120391254922f4b0d0801bfbb6e5f` remains an application-code rollback reference. Never overwrite customer SQLite, migrated schema, backups, or secrets. Existing PayPal hackathon source, `Freelancer@main`, and all other branches untouched.
- No API/paid CI/Production, permissions changes, real customer data processing or actual KMONG registration.
- **Official completion UNASSESSED, P85 NOT CERTIFIED; [작업중], RELEASE HOLD.**

## Final Linux portable evidence

`python -B scripts/build_portable.py` from source root PASS after dependency path repair. Produced unsigned Python-required 13-member ZIP SHA256 `50d25add8e34735576da6c0dfbd002092943f46d3160573358358e3954505187`; extracted `verify_portable` **12/12 PASS**, CLI synthetic init/customer/list PASS. Actual Windows installer NOT RUN.
