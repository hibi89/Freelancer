
# WORKNOVA Desk — P85 authenticated backup engineering evidence (2026-11-14 KST)

**Whole-product denominator WD-01..WD-14 unchanged; the owner-requested FINAL 85% is NOT certified.** Proposed scoring rubric is not approved; **[작업중]**, **RELEASE HOLD**.

## Alternatives and reason

Cloud-managed keys require accounts, recurring costs, customer transmission and extra security exposure. Chosen free offline alternative uses optional AES-256-GCM (locally installed `cryptography`) and scrypt-derived passphrases, random per-backup salt/nonce, and authenticated backup-only encryption.

## Implemented

`worknova_desk/secure_backup.py` makes a consistent SQLite memory snapshot, refuses oversized data (>128MiB), writes an exclusive private encrypted blob, and supports password-only, new-path, SHA-pinned recovery. Authentication precedes plaintext file creation; invalid passwords, ciphertext corruption, foreign format, corrupt SQLite, unsupported schema and audit-chain errors fail closed. Tk and CLI require explicit user action, passwords are prompted without argv or storage. SQLite source and user files are not silently overwritten or transmitted.

**Limitations:** active database remains unencrypted; recovered DB is plaintext; no authorized multi-role login, no live Windows10/11 PowerShell/ACL/Defender/Word QA, no signed standalone EXE, no actual customer acceptance or external bank proof. A strong remembered passphrase and separately retained SHA are necessary. Dependency is optional and NOT bundled; license and Windows binary delivery must be reviewed before sale.

## Actual executed scope

- Local Linux Python3.13.5 unittest **141/141 PASS, 0 FAIL, 0 SKIP** (125 prior + 16 new), `cryptography 46.0.4`.
- Linux Tk8.6/Xvfb scripted GUI **5/5 PASS** including backup password prompt, new restore and overwrite refusal.
- Complete source compilation PASS; portable archive 15/15 source/script hashes verified, extraction init/verify PASS, tampered source rejected.
- Native Windows test **NOT RUN**: script explicitly fails on Linux. Existing test suite emits SQLite connection ResourceWarning; quality issue remains open.

## Reproduce

`PYTHONPATH=. python -m unittest discover -s tests -q`

`PYTHONPATH=. xvfb-run -a python tests/gui_secure_backup_xvfb.py`

`python scripts/build_portable.py --out NEW.zip` then extract and `python verify_portable.py --root .`

No sale, external data change, paid workflow or owner-score approval performed.
