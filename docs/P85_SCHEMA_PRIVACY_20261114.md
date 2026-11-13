# WORKNOVA Desk — P85 schema/recovery & customer privacy follow-up

Date: 2026-11-14 KST. Existing feature branch: `hibi89/Freelancer@product/worknova-desk-local`. Owner goal is formal 85% of full WD-01–WD-14 design; **that whole-product percentage remains UNASSESSED; target NOT CERTIFIED**. `[작업중]` and RELEASE HOLD remain. This report documents additive implementation, not a reduction or revision of agreed acceptance.

## Why this change was prioritized

Two strategies were considered: (A) redesign storage and permissions around a hosted encrypted account service (new costs, external PII, stronger maintenance/auth burden), or (B) retain the offline SQLite model and enforce strict schema admission, recovery failure, and explicit minimal client summaries (zero cloud fees, fewer modifications, but does NOT establish disk encryption/user auth). **B selected** to preserve source/data and avoid unsupported third-party integration.

## Reproducible implementation

- `worknova_desk/core.py`: Existing foreign `PRAGMA user_version=0` databases, blank pre-existing files, corrupt raw bytes, and incomplete v2 table catalog or quote version columns are refused **before** creating WORKNOVA tables. New ledgers created via the existing explicit `Desk(...allow_create=True)` path still receive v2 schema. For a valid reopened ledger, audit-chain + SQLite integrity/foreign key checks run before use; a corrupted audit cannot be silently loaded as a normal ledger. No legacy v1 auto-migration is introduced; explicit backup migration is retained. This protection is against accidental schema confusion and detectable local changes, not administrator-level forgery or external signature absence.
- `worknova_desk/privacy.py`: User-initiated customer portfolio summary to new `.json`, default customer-name redaction; only opaque IDs, version/amount/state, manual collection and remaining balance. Scope, item description, stage titles, delivery notes, references, evidence paths and file contents excluded. Customer name requires **both** `--include-name` and `--confirm-disclosure`; GUI offers redacted export with explicit confirmation. Never overwrites an existing file, uses exclusive file creation and 0600 on POSIX, takes one database read transaction for a consistent snapshot. No network access. **Even the redacted financial/ID summary is confidential**, not anonymous and not bank/tax certified.
- `worknova_desk/__main__.py`, `gui.py`: `export-customer-summary` CLI and GUI selected-customer button.
- `scripts/build_portable.py`, `verify_portable.py`, `install_local.ps1`: Increment strict package allowlist to 14 source/script files + manifest; no credential/font/data upload or hosting; Python remains prerequisite.

## Local tests (evidence, not Windows success)

- Linux Python 3.13.5 `PYTHONPATH=. python -m unittest discover -s tests -q`: **123 PASS / 0 FAIL / 0 SKIP** (previous 104 + schema 9 + privacy 10). `compileall -q worknova_desk scripts` PASS.
- `PYTHONPATH=. xvfb-run -a python tests/gui_smoke_xvfb.py` PASS; `gui_lifecycle_evidence_xvfb.py` PASS; `gui_initialization_xvfb.py` PASS; **new** `gui_customer_summary_xvfb.py` PASS. Linux real Tk widgets using virtual Xvfb display, not Windows UX.
- `python scripts/build_portable.py --out NEW.zip`, extract NEW folder, `python verify_portable.py --root .`: **14/14** source/script manifest entries verified; `python -m worknova_desk --db ./new.sqlite init` and `verify` PASS on extracted ZIP; deterministic candidate source-only ZIP 15 members including manifest. No self-contained EXE; PowerShell script NOT EXECUTED on Windows.
- Negative evidence: unrelated v0 SQLite and 0-byte file preserved/no silent convert; corrupt bytes refused; incomplete v2 and missing quote version columns refused; corrupted audit rejects reopen; foreign SHA-pinned SQLite restore rejected without destination; CLI error has no traceback; customer sensitive text absent from default JSON; path overwrite/symlink/unknown IDs/incorrect disclosure flags blocked; POSIX file 0600. Only synthetic test records.

## Full blueprint remaining and formal status

- WD-01: offline user-controlled minimal customer summary added; still no multi-user authentication, encrypted local profile, full customer retention/legal deletion.
- WD-08/09: existing-ledger preflight and audit start checks added; no Windows full-system recovery/independent signed tamper proof.
- WD-11/13: GUI + packaging expanded and Linux tested; actual Windows10/11 GUI, PowerShell install/upgrade/rollback/uninstall, Defender, Word/PDF/TTF license, signed bundled EXE, ACL/BitLocker verification remain NOT RUN.
- WD-14: ten synthetic service cases from prior P85; no paying customers/real end-user acceptance, legal/tax approval, commercial support/release approval.

No credentials, PII, user SQLite, customer backup or PDF font entered source control. No PayPal/original PayPal hackathon, Freelancer main or unrelated KMONG product was modified. Rollback code through preceding verified source SHA `4e8adf0f61281006bcb570aa2f6282925168b0f7`; leave the user's database/backup untouched, never run a v1 writer on an existing v2 DB. Signed Windows installer and final scoring require separate evidence/owner approval. **RELEASE HOLD / `[작업중]`**.
