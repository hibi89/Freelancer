## P85 customer safety/evidence follow-up (2026-11-13)

New **local-only** customer rename (stale-write + confirm), deletion of **unused** customers only, and user-selected delivery-file SHA256 capture/reverification during DELIVERED state. CLI: `customer-rename`, `customer-delete-unused`, `evidence-attach --confirm-local-read`, `evidence-list`, `evidence-verify`. GUI exposes guarded actions. Evidence hashes are not buyer signatures or actual delivery proof.

Verified scoped Linux Python **81/81 tests**, Xvfb Tk **2 scripted GUI flows**, extracted portable **12-file preflight**, CLI init, Python compile. Real Win10/11, PowerShell, Word/PDF printing, signed EXE, customer rights and formal owner-approved final % all **unverified**; official `UNASSESSED`, `[작업중]`, RELEASE HOLD. Details [`docs/P85_CUSTOMER_EVIDENCE_20261113.md`](docs/P85_CUSTOMER_EVIDENCE_20261113.md).

---

# WORKNOVA Desk — offline local-first freelancer operations

**2026-11-13 KST.** Independent Korean local customer/quote/contract/delivery/collection desk. Python 3.11+ stdlib (`sqlite3`, `tkinter`), no mandatory cloud subscription or live PayPal/AI. **Private development, not released**, official whole-product final-completion rate **UNASSESSED**; user P70 is a bounded **engineering gate** only.

## Demo without external requests

Work in an existing private local folder; do not use customer data for tests.

```sh
PYTHONPATH=. python -m unittest discover -s tests -v
PYTHONPATH=. python -m worknova_desk --db ./demo.sqlite init
PYTHONPATH=. python -m worknova_desk --db ./demo.sqlite customer --name '가상 고객'
PYTHONPATH=. python -m worknova_desk.gui --db ./demo.sqlite
```

For Windows (Python 3.11+ with Tcl/Tk installed) use `py -3 -m worknova_desk.gui --db "C:\\YOUR_PRIVATE_FOLDER\\desk.sqlite"` from the checkout folder; **not verified on actual Windows yet**. Offline GUI supports selecting/searching customers, new/revised tax-aware integer-KRW quote, explicit quote/contract actions, milestone delivery/revision/acceptance, manually noting collections, script-free HTML quote preview, offline backup. No file is overwritten by export or restore.

## User data / versioning / recovery

- New SQLite DB initializes schema **v2**; quote revisions have an immutable lineage and cannot approve a superseded draft. A pre-existing approved quote/contract remains unchanged after a proposed revision.
- Existing schema v1 requires explicit owner-controlled `migrate-v1 --backup-out FRESH_BACKUP.sqlite` before `revise-quote`/GUI. The migration **first** writes a consistent SHA256 backup; the previous v1 backup remains available. Do not delete it until recovered data is verified.
- Recovery is **explicit**, only into an unused new filename: `python -m worknova_desk --db ./current.sqlite restore-new --backup-file ./backup.sqlite --new-db ./restored.sqlite --sha256 ACTUAL_SHA_FROM_BACKUP`. Source SHA is required; original and backup preserved.
- `quote-history --quote-id ID`, `revise-quote --quote-id ID --items-json '[{"description":"...","quantity":1,"unit_krw":50000}]' --actor owner`, `quote-preview --quote-id ID --out NEW_PREVIEW.html` require selecting actual IDs. Outgoing documents default to redacted names.
- No automatic funds movement, bank check, e-signature or tax filing. Manual records are **not** bank-confirmed. Local databases and backup files are **not encrypted**; protect using OS permissions/disk encryption.

## Tests and boundaries

`PYTHONPATH=. python -m unittest discover -s tests -q` locally **37/37 PASS** (18 P50 regressions plus 19 P70); `PYTHONPATH=. xvfb-run -a python tests/gui_smoke_xvfb.py` **PASS** on Linux virtual Tk 8.6. No Windows end-user acceptance/CI, real-client VAT/legal signoff, DOCX/PDF final output, signed installer, customer onboarding, commercial IP/legal approval. All releases **HOLD**.

[Final whole-product blueprint](docs/FINAL_BLUEPRINT.md) · [P70 scoped evidence](docs/P70_TRACE.md) · [P50 baseline](docs/P50_TRACE.md).

## P85 scoped upgrade — offline Korean DOCX/PDF + portable source package (2026-11-13)

Original P50/P70 functions and DB v2 remain unchanged. From the private checkout:

```sh
PYTHONPATH=. python -m unittest discover -s tests -q
PYTHONPATH=. xvfb-run -a python tests/gui_smoke_xvfb.py  # Linux GUI test only
python -m worknova_desk --db ./demo.sqlite export-document --type quote --id QUOTE_ID --out ./NEW_QUOTE.docx --format docx
python -m worknova_desk --db ./demo.sqlite export-document --type contract --id CONTRACT_ID --out ./NEW_REPORT.docx --format docx
# Optional Korean PDF requires local reportlab and a licensed Korean TTF file:
python -m worknova_desk --db ./demo.sqlite export-document --type quote --id QUOTE_ID --out ./NEW_QUOTE.pdf --format pdf --pdf-font /PATH/TO/YOUR_LICENSED_KOREAN.ttf
python scripts/build_portable.py --out ./NEW_WORKNOVA_PORTABLE.zip
```

The generated documents exclude customer names by default, show quote version and recorded KRW/VAT, and disclaim legal, payment and tax certification. CLI inclusion of a customer name requires **both** `--include-customer` and `--confirm-disclosure`; the GUI does not offer unredacted export. Documents and SQLite backups are sensitive, unencrypted local data and are never automatically uploaded.

The Windows portable ZIP includes Python source, explicit checksums, `launch.cmd`, and a candidate `install_local.ps1` for user-scoped install/upgrade/remove preserving `LOCALAPPDATA\\WORKNOVA Desk\\Data`. **Windows Python 3.11+ and Tk are prerequisites. No standalone EXE, signed MSI, font files or customer database are bundled.** Native Windows install/rollback/Defender/SmartScreen **NOT_RUN**. The PowerShell script must be reviewed and never silently bypass policy.

Engineering proof: [P85 trace](docs/P85_TRACE.md) (Linux 52/52 tests and virtual-display UI smoke; **official final % UNASSESSED and RELEASE HOLD**). The previous P70 test statement above is historical rather than the current test total.

## P85 independent ledger checkpoint and portable preflight (2026-11-13)

Run `python -m worknova_desk --db ./demo.sqlite checkpoint-new --out ./checkpoint-001.json` only with owner-owned synthetic/private data. Save returned `file_sha256` somewhere **outside** the database folder. Verify later: `python -m worknova_desk --db ./demo.sqlite checkpoint-verify --file ./checkpoint-001.json --expected-file-sha256 SHA`. The checkpoint includes only aggregate table counts/hashes and local audit-head; it is **not a signature or substitute for encrypted offsite backup**. A new legitimate transaction requires a new checkpoint (old checkpoint should fail, by design).

`python scripts/build_portable.py --out NEW.zip` generates an unsigned Python-required ZIP. `python verify_portable.py --root EXTRACTED_DIR` checks exact source and manifest before first launch; on Windows `launch.cmd` now performs this preflight before GUI. Do not use with real customers until Windows install/rollback/Defender/Word/font rights pass. [Hardening evidence](docs/P85_HARDENING_20261113.md).
