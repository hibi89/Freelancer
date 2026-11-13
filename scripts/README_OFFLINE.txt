WORKNOVA Desk P85 Portable (engineering candidate; not commercially released)

This is an offline Python/Tk application, NOT a standalone EXE and NOT code-signed.
Windows 10/11 user must first install Python 3.11+ with Tkinter; installation
requires no administrator privileges. Launch launch.cmd from extracted folder.

To install per-user: Windows PowerShell from an EXTRACTED, owner-reviewed package:
  .\install_local.ps1 -DryRun
  .\install_local.ps1
To uninstall application files ONLY (customer SQLite kept):
  .\install_local.ps1 -Uninstall -ConfirmRemoveApp

DATA: %LOCALAPPDATA%\WORKNOVA Desk\Data\desk.sqlite (UNENCRYPTED).
Application updates preserve customer Data; keep verified offline backups in an
OS-protected directory, preferably full-disk encryption. Manual receipt status
is NOT bank/PayPal settlement. No network, tax filing, digital signing or AI.

DOCX: Python standard library, references Windows Korean font (no fonts shipped).
PDF: optional reportlab installation, plus user-supplied licensed Korean TTF.
No fonts or customer records are included in this package. Existing customer
DOCX/PDF must be handled as sensitive files; output is redacted by default.

No real Windows/Defender/SmartScreen/installer test has been run at source.
PRODUCT RELEASE HOLD; not an authorized legal contract or tax invoice generator.

P85 hardening update: manifest format v2, pre-launch verify_portable.py fails closed
on missing/tampered source before creating the Data folder. Installer also verifies
exactly ten named application files. Unsigned hashes are corruption checks, NOT
proof of authenticity; a malicious party could alter manifest and verifier.
Optional independent ledger checkpoint:
  py -3 -m worknova_desk --db PATH checkpoint-new --out NEW.json
  py -3 -m worknova_desk --db PATH checkpoint-verify --file NEW.json --expected-file-sha256 SHA
Store JSON and its SHA away from the unencrypted customer DB.

2026-11-13 safety continuation: repaired the PowerShell allowlist to admit
verify_portable.py, and copied FILE_MANIFEST.json into staging for launch-time
verification. Staged hashes are checked BEFORE any app swap. The launcher uses
--root "." after pushd to avoid trailing-backslash quoting. Unexpected Python
bytecode caches/executable files block startup. Missing owner DB prompts for
explicit first-run confirmation in GUI; CLI existing ledger commands fail
closed unless explicit init was first run. This was tested on Linux only;
Windows OS execution remains NOT RUN and product is RELEASE HOLD.

P85 OFFLINE BACKUP RECOVERY REHEARSAL (no cloud, explicit opt-in)
- Choose a separate private existing local workspace directory. It must not be the
  active database folder. Temporary copies of sensitive data will be created and
  automatically removed when the rehearsal finishes.
- Use Python installed on your computer. Example:
    python -B -m worknova_desk --db FULL_PATH_TO_EXISTING_DB rehearse-restore --workspace-dir FULL_PATH_TO_PRIVATE_SCRATCH
- This verifies a SHA-pinned backup, a new-path restore and 6 business/audit
  tables. A successful rehearsal is NOT proof of physical Windows power-failure
  recovery, encryption, cloud backup, banking receipts or legal acceptance.
- Backups contain sensitive customer data; protect via OS account encryption and
  owner-controlled offline storage. On POSIX, newly created backups use mode 0600.


OPTIONAL OFFLINE ENCRYPTED BACKUP (not live-database encryption):
  Requires locally installed optional cryptography package (not bundled).
  python -m worknova_desk --db PATH backup-encrypted --out NEW_BACKUP.wndesk
  python -m worknova_desk --db PATH restore-encrypted-new --encrypted-file FILE.wndesk --new-db NEW.sqlite --sha256 SAVED_SHA256
  Passphrase entered privately, never through argv; keep separate owner-protected copy. Restored SQLite is plaintext. Native Windows/Word/ACL NOT RUN.
