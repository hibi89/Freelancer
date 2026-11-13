# WORKNOVA Desk P85 — private backup and recovery rehearsal (2026-11-13 KST)

## Scope and decision

Goal: make actual backup/restore failure visible without touching owner production data or expanding cloud/payment functionality. Design A: send an encrypted archive to a hosted checkpoint service (ongoing cost and personal-data transmission risk). **Design B selected:** explicit owner-selected offline separate temporary workspace, backup SHA256, new-destination SQLite restore, six-table and audit-head comparison, automatic scratch removal; zero network use. This is not full endpoint encryption, Windows ACL coverage, or disaster recovery certification. Canonical full blueprint WD-01..WD-14 remains unchanged.

## Implementation

- `worknova_desk/core.py`: create fresh SQLite backup with `os.open(...O_CREAT|O_EXCL, 0o600)`; target must be NEW and parent non-symlink. On exception, remove only the just-created backup, never rewrite an owner file. Backup integrity and pre-existing hash-chain check preserved.
- `worknova_desk/recovery.py`: refuses nonexistent, symlink or active-DB-directory scratch; uses fresh private temp folder in explicit owner workspace; backs up, hash-pins, restores into a new file; compares six table row hashes, counts, schema and audit head. `TemporaryDirectory` deletes scratch when complete or on error. Returns aggregate counts only, no customer PII.
- CLI: `--db EXISTING.sqlite rehearse-restore --workspace-dir SEPARATE_EXISTING_PRIVATE_DIRECTORY`. It is opt-in and has no automatic network or background behavior.
- Portable v3 bundle contains the new module; verifier and PowerShell allowlist updated to exactly 13 declared source/script files + `FILE_MANIFEST.json`. v2 archives remain historical, but must not be mixed with the v3 verifier.

## Reproducible evidence (Linux development host only)

- Python 3.13.5 `PYTHONPATH=. python -m unittest discover -s tests -v`: **104 PASS, 0 FAIL, 0 SKIP** (existing 97 + new 7 recovery tests). New cases: exact table round-trip & ephemeral cleanup, refusal of live folder/missing/symlink scratch, POSIX new-backup 0600 despite umask 022, no overwrite, CLI end-to-end and privacy of output.
- Native Tk8.6 under Xvfb scripted GUI tests (original 3 flows) and portable v3 extracted verifier/init smoke separately performed as recorded in final handoff.
- Tests use only synthetic data in disposable temporary directories; no real customer database, license, private token or font read or uploaded.
- No actual Windows Win10/11, PowerShell, BitLocker/ACL, physical disk corruption, signed Python-bundled EXE, commercial Word/PDF rights or customer signoff. `RELEASE HOLD`.

## Stop/recovery/limitations

`os.open(mode=0600)` on POSIX enforces a private new file; it does not retrofit owner files or guarantee Windows NTFS ACLs. Operating-system administrator or compromised profile can still access local data. The rehearsal creates short-lived **plaintext** copies in the explicitly provided local workspace: use only a private non-network folder, not a shared directory; the app cannot enforce that operational decision. The verification checks business rows and audit chain, not independent bank settlement or cryptographic signing. Avoid storing the workspace in synced folders.

Rollback: previous GitHub source commit `85a2a115d32d3378544ae68bb453466499aebcb8` without touching owner DB, existing backups or original PayPal repo. Never downgrade an owner v2 DB to a v1 writer. Official full completion **UNASSESSED, P85 not certified, `[작업중]`, RELEASE HOLD**; proposed WD weight rubric is not user-approved.
