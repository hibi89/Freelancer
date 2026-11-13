# WORKNOVA Desk P85 — independent engineering evidence (2026-11-13 KST)

**Scope / policy:** Private `hibi89/Freelancer@product/worknova-desk-local`, owner-defined complete blueprint WD-01..WD-14. The user requested a P85 milestone. This note records *bounded engineering completion only*. **Official final-blueprint completion remains UNASSESSED**, since there is no owner-approved 100-point per-requirement weighting or complete WD-01..14 acceptance. Never translate 52 tests or the P85 goal into a formal 85% of the final product. **RELEASE HOLD / no authorized sale / no registered KMONG SKU.**

## Preserved baseline

- Previous exact source `16d08b79621a303e190835a74885d58d75d513d9` at start, Git blob parity of `core.py` (`046781410776d6d79a7ddb790c09f5f9bf1707b5`) and `gui.py` (`2570deb257d464e23b3c8ff9ff928d79e763166b`) verified locally before edits.
- Existing P50/P70 source, schema v2, SHA audit/backup, versioned approved quotes, explicit activation/acceptance/manual collection, UI and all 37 tests preserved; no automatic PayPal CREATE/CAPTURE, bank lookup, AI call, cloud upload or customer data.
- All new work in the standalone private product branch; `Freelancer@main`, other product branches, public PayPal source, and production URL untouched.

## Architecture and cost comparison (P85 additions)

| Implementation | Cost, interoperability, maintenance | Decision |
|---|---|---|
| A: Electron/embedded browser + SaaS PDF | Node/Electron installer, package size, third-party license obligations, potentially external font/cloud data; greater maintenance | Not selected |
| B: existing Tk GUI + offline OOXML (Python stdlib) + optional ReportLab with user-owned Korean TTF + checksum-verified per-user Windows Python portable package | Local CPU/disk; no mandatory server fee, no bundled fonts, minimal new dependencies; Windows Python required and no EXE/signature yet | Selected, implemented/tested as specified |

## WD-01..WD-14 trace status (exact source refs)

| ID | Feature/evidence | Remaining / not certified |
|---|---|---|
| WD-01 | Preserved customer create/search/list `core.py`, GUI | Customer update/archive/role authorization absent |
| WD-02 | Preserved integer KRW, explicit VAT and round-half-up tests; 10 synthetic categories in `test_p85_documents.py` | Actual tax counsel and cases not checked |
| WD-03 | Preserved v2 immutable quote revision/approval chain; DOCX/PDF exact quote ID/revision | Human buyer approval legally valid not claimed |
| WD-04 | Preserved manual contract activation; internal contract status report DOCX | Legal contract document/customer countersignature not provided |
| WD-05 | Preserved contract milestone sum & state transitions | Multi-actor authorization missing |
| WD-06 | Preserved delivery/revision/acceptance, visible in DOCX progress snapshot | External delivery evidence provenance and richer revision log incomplete |
| WD-07 | Manual partial collection and outstanding included in DOCX; no actual bank/PayPal query | Actual money reconciliation not implemented |
| WD-08 | `export_document` verifies stored audit chain before writing; export does not overwrite | Not immutable against someone rewriting entire local database |
| WD-09 | Preserved v1 backup/migration and hash-checked new-only restore, real SQLite smoke | Windows OneDrive/ransomware/power-cut restore drill not run; raw SQLite unencrypted |
| WD-10 | Redacted-by-default DOCX/PDF, explicit double-confirmation for customer name, no network, restrictive HTML | User may voluntarily share generated documents; no external attestation |
| WD-11 | Tk user-initiated DOCX/PDF buttons + existing full local actions; Xvfb GUI smoke PASS | Native Windows/keyboard/screen-reader/real customer QA not run |
| WD-12 | `documents.py` standard library OOXML DOCX verified by `python-docx` readback; PDF optional ReportLab uses user-provided Korean TTF, generated PDF text parsed with PyMuPDF; Korean text / A4 / prices checked | Commercial font permission/Windows print/Word/Edge compatibility and real customer templates NOT verified; **no fonts bundled** |
| WD-13 | `scripts/build_portable.py` deterministic ZIP with per-file SHA256 manifest; Windows `install_local.ps1` (user-scope, dry-run, old app retained, data outside app) and `launch.cmd` (requires preinstalled Python). ZIP read-back, duplicate/existing target refusal and no customer/secret/font payload checked | **Not an EXE, unsigned**, PS1 not executed on actual Windows, Python installer not bundled, ACL/Defender/upgrade/uninstall/codesign Windows tests pending; role/storage encryption not implemented |
| WD-14 | Synthetic 10 industry scenario end-to-end DB transaction tests | **0 actual customers**, 0 real tax/legal review, license/NOTICE/support/refunds/owner sale approval absent |

## Local test receipt (not hosted CI)

- Runtime: Linux Python 3.13.5, Tk 8.6 under Xvfb; not physical Windows.
- `PYTHONPATH=. python -m unittest discover -s tests -q` -> **52 PASS / 0 FAIL / 0 SKIP**, including existing 37 P50+P70 and 15 new P85 tests. Uses only synthetic customer records and local temporary SQLite.
- `PYTHONPATH=. xvfb-run -a python tests/gui_smoke_xvfb.py` -> **PASS**, actual Tk widgets from customer selection through quote approval, contract activation, delivery, acceptance and partial collection; no real human user.
- `python -m compileall -q worknova_desk scripts` -> **PASS**.
- `PYTHONPATH=. python scripts/build_portable.py --out NEW_FILE.zip` produces deterministic ZIP; verify unpacked manifest and check source-only CLI/GUI import before Windows acceptance. Hash and exact SHA to be frozen after final package build.
- PDF test installed packages `reportlab 4.4.9`, `python-docx 1.2.0` (test-only parser), `PyMuPDF 1.26.7` (test-only parser). Korean font `/usr/share/fonts/truetype/nanum/NanumGothic.ttf` is **host's installed test fixture only**; never copied to product/ZIP or shared. Windows PDF requires separate rights-cleared local `.ttf` and optional `reportlab` install.
- Local hosted GitHub Actions: **NOT_RUN for new source SHA**, no Windows jobs started, no CI result claimed.

## Safeguards and remaining gates

1. A generated DOCX/PDF has the explicit "오프라인 수기 기록 / not tax invoice or bank confirmation" disclaimer. Customer name is redacted unless the caller supplies *both* privacy options; Tk GUI always exports redacted.
2. Export refuses document-path overwrite; verifies audit; emits SHA256. Draft and already-approved quotes are separate versions. PDF font path must be an existing local `.ttf` under 25 MiB, with use rights confirmed by owner; no font licensing assertion.
3. Windows portable package uses a source-only allowlist and individual SHA256 checks, stage copy/rollback; existing customer SQLite stored outside the program folder; uninstall deliberately retains customer data and program backup. Source scripts are unsigned, user must review them. Windows PowerShell execution policy should not be silently changed.
4. Data are **not encrypted**, there's no login/role enforcement or cryptographic 3rd-party audit anchor. Do **not** sell/claim secure multiuser release.
5. Next: real Windows10/11 Python3.11+ Tk smoke and actual Word/DOCX/PDF printing, install/upgrade/uninstall/rollback, explicit buyer-safe data privacy/role policy, optional signed EXE after cost/permission approval, at least ten *realistic customer-accepted* cases, third-party rights/NOTICE and legal/owner approval. Full final-weight consensus before official 85% claim.

**CI/Production:** Vercel N/A; no public production. **RELEASE HOLD**. When pushed, record exact product commit SHA, Central KMONG sync SHA and updated KST below; P85 scoped functional outputs are not the final-product rate.

## Verified GitHub source checkpoint

- **Feature commit:** [`106e6a8f3c0b2b547344b8ef40dcf15c22b0529a`](https://github.com/hibi89/Freelancer/commit/106e6a8f3c0b2b547344b8ef40dcf15c22b0529a), product branch `product/worknova-desk-local`; GitHub tree source files match locally hashed `documents.py 83fccf11`, `gui.py db96b28c`, `__main__.py 550af134`, `install_local.ps1 fa6b8035`, P85 tests `bff26539`.
- **GitHub workflow** [`#43383886013`](https://github.com/hibi89/Freelancer/actions/runs/43383886013) SUCCESS at feature commit. This workflow verifies the repository blueprint/policy content; it does **not** run Python 52-test product suite or Windows installer tests.
- **Local package** Python-dependent source ZIP `WORKNOVA_Desk_P85_Windows_Python_Portable.zip`: 22,485 bytes SHA256 `ebaf31a3b087d6fed4418a8c2c522d5a515da1c65769a78ee4dd95785cb5b352`; ZIP CRC/content verified and extracted source CLI `init` succeeded. No signed EXE, no physical Windows tests, no customer data/fonts.
