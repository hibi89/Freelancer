# WORKNOVA Desk P70 engineering evidence — 2026-11-13 KST

**Canonical whole-product scope:** `docs/FINAL_BLUEPRINT.md` WD-01..WD-14. **Formal final completion: UNASSESSED** until owner-approved 100-point requirement weights and exact-SHA acceptance. **P70 is a scoped engineering gate, NOT formally earned 70%.** No SKU posting, remote APIs, payment or deployment. RELEASE HOLD.

## New offline implementation (in addition to P50 18 regressions)

| Target | Source | Actual local verification | Remaining |
|---|---|---|---|
| WD-03 quotation immutability/revisions | `core.py`: v2 `root_quote_id/parent_quote_id`, `revise_quote`, `quote_history`, latest-draft approval rejection | chain revision 1→2→3, reject stale edits, original approved quote and contract amount unchanged | full buyer approvals/legal scope, customer acceptance |
| WD-09 safe recovery / migration | `core.py`: explicit `migrate_v1(backup_out)`, SHA-pinned `restore_new(backup,out,sha256)` writes only **new path**, audit+SQLite integrity+FK | v1 fixture preservation + unmodified backup; restored v2 rows and event chain; wrong hash/existing target/bad db rejection | crash/powerfail, customer Win10/11/OneDrive, disk encryption, large DB |
| WD-10 private HTML preview | `core.py:export_quote_html`, CLI `quote-preview` | escapes markup, blocks script/CSP, excludes customer name, output never overwrite | actual Korean printing/PDF/font |
| WD-11 guided local UI proof | `gui.py` Tkinter local UI; customers→quotes→contracts→milestones, manual approvals/receipts, search & price rows | GUI parser tests, real Tk 8.6 Xvfb widget synthetic E2E customer→quote→approval→contract→activate→delivery→acceptance→partial collection and amount/audit checks **PASS** | physical Windows GUI usability, 100% keyboard access, assistive tech |
| WD-01 basic customer lookup | `core.py:list_customers/list_quotes/list_contracts/list_milestones` | search by name, row mapping and output | permissions, customer update/delete/suppression |

## Exact local test commands/observed results

- `PYTHONPATH=. python -m unittest discover -s tests -q` on Linux Python **3.13.5**: **37 PASS, 0 FAIL, 0 SKIP** (18 original + 19 new). Synthetic customers; real temp SQLite DB/backup and CLI subprocess; no customer data.
- `PYTHONPATH=. xvfb-run -a python tests/gui_smoke_xvfb.py`: **PASS**, real Tk 8.6 widgets exercised a synthetic full GUI flow: customer → quote → owner approval → contract activation → delivery → buyer acceptance → 50 KRW manual collection (60 KRW remains), audit rechecked, window destroyed. Virtual X server **not Windows/browser proof**.
- `python -m compileall -q worknova_desk`: PASS. No external calls, authentication, PayPal sandbox transactions or remote CI executed.

## Safety and operational notes

- **Never** run `restore-new` on an existing path: this API rejects overwrite. Restore source SHA256 must match a consistent backup; the output is created atomically as a new DB. Original and backup preserved.
- **Legacy v1**: migrations are NOT automatic. Use explicit CLI `migrate-v1 --backup-out NEW_NAME.sqlite` only after confirming folder, storage & local owner control; backup is created and SHA returned before schema changes. No automatic deletion. Aborted migration retains backup.
- SQLite backups are **unencrypted** and need OS-protected owner folder. Audit chain is an integrity *indicator*, not a tamper-proof third-party timestamp or bank/payment verification.
- An approved quote is still available after new revision and its existing contract remains bound to the old exact total; revisions do not implicitly amend signed/accepted scope. New version requires its **own** owner approval and new contract if chosen.
- Live payment, registered e-signature, tax certification, invoice delivery, data sharing, scheduled tasks or AI-generated quotes **not implemented**.

## Target remains blocked for formal 70%

Owner-approved weights and final WD-01..14 coverage map are missing. Missing/partial: WD-01 safe multi-user roles/customer CRUD, WD-06 richer lifecycle evidencing, WD-08 external integrity anchoring, WD-09 customer-grade recovery, WD-11 Windows GUI, WD-12 DOCX/PDF, WD-13 installer/protection, WD-14 ≥10 customer-shape samples/legal/license, owner acceptance. P70 local engineering scope is now **implemented/tested on Linux** but cannot be marked official 70%.

**Source control:** Private `hibi89/Freelancer@product/worknova-desk-local`, exact code SHA to be recorded after final source/tree commit. Central `kmong-productization` `[작업중]` must stay until formally verified target; all prior P50 evidence preserved.
