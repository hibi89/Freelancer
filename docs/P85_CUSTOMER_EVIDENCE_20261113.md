# WORKNOVA Desk P85 follow-up — customer lifecycle and read-only delivery fingerprints

Date: 2026-11-13 KST · target full design WD-01..WD-14 unchanged · offline private product `hibi89/Freelancer@product/worknova-desk-local`.

## User request and architecture decisions
- User requested *final design 85%*. This work does **not** certify it. The only formal denominator remains the approved full WD-01..WD-14 blueprint, and no owner-approved 100-point requirement weights exist. The official completion therefore remains `UNASSESSED`, target P85 unmet, `[작업중]` remains, RELEASE HOLD.
- Choice A: upload delivery files/identities to cloud/SaaS and rely on remote audit. Cost, privacy, internet and payment authority barriers; rejected.
- Choice B: user-selected local file SHA256 fingerprint, immutable existing `audit_events` chain, lightweight customer lifecycle on current v2 SQLite. Does not transmit files, change schema, require subscriptions or new provider permissions. **Chosen**.

## Implemented, exact routes and limits
- WD-01 (partial): `worknova_desk/lifecycle.py` provides customer rename with explicit confirmation and expected-current-name compare (stale-write guard), idempotent no-op, no PII/name hash in audit; deletion only of *unused* customers after separate explicit confirmation. Existing quotes/contracts/receipts make deletion fail closed. CLI `customer-rename`, `customer-delete-unused`; Tk buttons. **Not** multi-user authentication, erase-all, automatic compliance retention or true role-based OS security.
- WD-06 (partial): `worknova_desk/delivery_evidence.py` accepts an explicit user-selected regular file **after** the milestone enters DELIVERED; streams <=64 MiB read-only, checks symlink/hardlink, FD metadata and before/after path identity, records only SHA256 + byte count + milestone ID in local audit, deduplicates the same bytes, verifies a later local file without copying/storing original file or file path. CLI `evidence-attach --confirm-local-read`, `evidence-verify`, `evidence-list`; Tk attach/verify buttons. No Dropbox/email/NAS transfer, buyer signature or external delivery receipt.
- WD-08 (partial): new events reuse existing SHA256 chained audit. **Not cryptographically signed**; a privileged attacker may rewrite the DB/hash chain. Previous standalone checkpoint remains available. No claim of fraud-proof nonrepudiation.
- WD-09/WD-13: existing SQLite schema v2, backups and restore unchanged; unsigned Python-required portable ZIP manifest updated for two new strictly allowlisted source files and PowerShell validation list. No independent EXE or signed Windows installer.

## Executed verification
- **Linux Python3.13.5:** `PYTHONPATH=. python -m unittest discover -s tests -q` **81 PASS / 0 FAIL / 0 SKIP** (previous 68 + new 13, with prior portable manifest expectation 10→12 reflecting added files).
- **Actual Tk8.6 widgets under Linux Xvfb:** `PYTHONPATH=. xvfb-run -a python tests/gui_smoke_xvfb.py` PASS for full quote→approval→contract→delivery→acceptance→manual collection. `PYTHONPATH=. xvfb-run -a python tests/gui_lifecycle_evidence_xvfb.py` PASS for rename, deletion protection, local evidence attach/reverify. No external network used by these fixtures.
- `PYTHONPATH=. python -m compileall -q worknova_desk scripts` PASS. Deterministic ZIP created/rehydrated, `verify_portable.py` **12/12 SHA** and independent extracted CLI `init` PASS. No customer DB used; no customer file contents or credentials added to the ZIP.
- One scripted Tk test initially blocked on expected warning modal; mocked only the warning-display callback and reran PASS. Original product error path remains exercised. No other known failing regressions in scoped tests.
- GitHub committed source hashes / hosted CI outcome must be recorded after push; local verification is **not** Windows verification.

## Security, data and further P85 blockers
- This is a single-owner UI/CLI. The `actor` string is user-entered, **not authenticated**. A hash of a local file does not prove delivery to a buyer or legal assent. Existing customer SQLite is **not encrypted**, and physical disk/OS permissions are external.
- Real physical Windows 10/11, PowerShell install/upgrade/uninstall/rollback/Defender, Windows Word/PDF print and Korean commercial font rights, signed standalone EXE, customer/role retention policy, >=10 actual buyer-accepted cases and independent legal/licensing/sale approval are all **NOT RUN / PENDING**.
- No PayPal/Gemini order/payment API, new hosting, paid Actions, external transmissions or original hackathon edits. No fee/API claims changed.

## Reproduction / rollback / source of truth
- Source `hibi89/Freelancer`, branch `product/worknova-desk-local`. Pre-change feature HEAD `affb062c6251bc5ff253a8d855c7672298afe39d`. For *code* rollback restore the prior commit; do **not** roll back user database using an older writer after migration. User database and any backups not accessed or modified during this work.
- Production/Vercel: **not applicable**. Central kmong audit must remain `[작업중] / UNASSESSED / RELEASE HOLD`. Package has no bundled fonts, user records, API keys or third-party dependencies.
