# WORKNOVA Desk — P85 Windows installer / missing DB safety regression

Date: 2026-11-13 KST. Canonical full-product blueprint remains `docs/FINAL_BLUEPRINT.md` WD-01..WD-14. Formal whole-product 85% is **UNASSESSED / not accepted**. This is a tested incremental security/packaging patch, not release clearance.

## Precisely reproduced engineering risks and fixes

1. **PowerShell package allowlist failure:** The candidate v2 manifest contains `verify_portable.py` (12 entries), yet `install_local.ps1`'s path allowlist rejected this required verifier. Updated the strictly bounded allowlist to include exactly `verify_portable.py` (arbitrary `.py` files still blocked).
2. **Installed package cannot start:** The earlier PowerShell staging loop copied only manifest-listed 12 files; `FILE_MANIFEST.json` is deliberately *not* one of those files, so the installed app would always fail the `verify_portable.py` preflight. The installer now copies the manifest into staging and verifies its hash, then rechecks each staged file before moving the prior app. The executable previous version is kept in an app-only rollback folder. No owner database is copied or deleted.
3. **Windows launcher argument quoting:** `--root "%~dp0"` ends in a backslash which can be parsed incorrectly by Windows command-line argument processing. Following `pushd "%~dp0"`, the launcher now invokes `--root "."` and verifies before creating/opening data.
4. **Executable cache bypass:** Verifier previously ignored all `__pycache__` files. `-B` prevents cache writing, not necessarily cache loading, so it now rejects any cache/bytecode tree as well as unlisted executable extensions. Signed publisher authentication is still absent.
5. **Missing owner SQLite:** SQLite `connect()` defaults to creating a new empty file, potentially looking like disappeared customers/transactions. `Desk(...,allow_create=False)` now opens existing SQLite with `mode=rw` (fail-closed). CLI operations other than explicit `init` require an existing DB. GUI shows a confirmation dialog before creating a never-before-seen new ledger. Refused confirmation leaves no DB. On POSIX, brand-new DBs get `0600` permissions; existing OS ACLs are never modified. Windows ACL/BitLocker are not independently certified.

## Executed local tests (synthetic data only)

- `CUA_DD_PYTHON_TOOL_WARM_SPREADSHEET_RUNTIME=false CUA_DD_INIT_ARTIFACT_TOOL_V2=false PYTHONPATH=. python -m unittest discover -s tests -q` → **97 tests PASS; FAIL 0; SKIP 0** (81 prior + 8 installer + 8 missing-DB safety).
- `PYTHONPATH=. xvfb-run -a python tests/gui_initialization_xvfb.py` → **PASS** real Linux Tk8.6, refusal/explicit first-run consent/existing DB without prompt.
- `PYTHONPATH=. xvfb-run -a python tests/gui_smoke_xvfb.py` → **PASS** preexisting quote→approved contract→milestone→manual collection UI.
- `PYTHONPATH=. xvfb-run -a python tests/gui_lifecycle_evidence_xvfb.py` → **PASS** preexisting rename/delete protection and read-only delivery evidence.
- Staging-simulator 8/8 checks include real `scripts.verify_portable.verify()` against a model of the Windows staging layout, plus negative corruption and unexpected code checks; **they are not actual PowerShell execution**.
- Source `compileall`, deterministic ZIP extraction/verification and CLI `init` in a fresh isolated directory must be rechecked at exact final source SHA; record results in Git commit and central audit after push.

## Restrictions / risk / reversibility

- Windows10/11, real `install_local.ps1`, actual upgrade/rollback/uninstall, real Word/PDF printing, EXE signing and customer acceptance all **NOT RUN**. Do not translate Linux staging tests into Windows passing QA.
- Existing user SQLite, actual customer files, OS ACLs, original PayPal hackathon code, `Freelancer@main`, and other branches unchanged.
- Local Python-required source archive remains unsigned. An attacker replacing both source and manifest could still forge hashes.
- New source can roll back to pre-patch verified GitHub SHA `6f24ccea44c120391254922f4b0d0801bfbb6e5f` **without** touching customer data. Do not run older v1 DB writers against v2 ledgers.
- GitHub Actions policy-only checks are not Windows application tests. Do not trigger paid CI, deployment, change permissions or mark product KMONG registered without approval.

## Next gates

1. Run real non-admin Windows10/11 staging, install, launch and upgrade/rollback, verifying customer file SHA before/after.
2. Implement explicit owner-only local authorization and OS-protected storage policy without silently changing existing security permissions; have the owner approve any OS permission changes.
3. Test DOCX/TTF PDF on Word/Windows and font distribution license; prove no customer data leakage to a network.
4. Collect 10+ real customer acceptance cases, legal/invoice wording review, and approved requirement weights for the 14-item whole-product design.

**Official final-completion status:** UNASSESSED; P85 not certified; `[작업중]`, RELEASE HOLD.

### Final clean portable artifact check (executed on Linux)

- `python -B scripts/build_portable.py --out /mnt/data/WORKNOVA_Desk_P85_Windows_Portable_InstallerFix_20261113.zip` from the fresh project root **PASS** after fixing the script path import.
- ZIP **13 members (12 validated files + manifest)**, `ZipFile.testzip()==None`, package SHA256 `50d25add8e34735576da6c0dfbd002092943f46d3160573358358e3954505187`.
- Fresh-folder `python -B scripts/verify_portable.py --root EXTRACTED` **PASS 12/12**; synthetic `python -B -m worknova_desk --db TEMP.sqlite init`, `customer`, `list-customers` all PASS. Those create and delete only throwaway records in a disposable temp directory. This is not a real Windows install.
