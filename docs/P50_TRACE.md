# WORKNOVA Desk P50 evidence — 2026-11-13 KST

- Code: `worknova_desk/core.py`, `worknova_desk/__main__.py`, `tests/test_core.py`.
- Local Linux/container Python3.13.5: `PYTHONPATH=. python -m unittest discover -s tests -v`: **18 PASS, 0 FAIL, 0 SKIP**, with synthetic data and actual SQLite files/CLI subprocess.
- Verified: taxable and tax-exempt integer-KRW; half-up rounding; explicit quote/contract human approval; milestone sum; delivery/revision/acceptance; partial manual receipts and replay/overpay rejection; redacted HTML/JSON; event tamper rejection; consistent SQLite backup; safe failures and CLI.
- **Verified source parity:** GitHub commit `6b7f86738fb6ed6c7b965523955efcae3285d1f7` exact 11/11 Git blob SHA equals locally tested and documented UTF-8 files. Generic [blueprint evidence workflow #43377108605](https://github.com/hibi89/Freelancer/actions/runs/43377108605) SUCCESS on code SHA, but **it did not run these Python tests**.
- NOT VERIFIED: GitHub-hosted WORKNOVA test suite, Windows3.11/Win10, actual customer, DOCX/PDF, signed installer, complete quote revision history, role authentication, encrypted DB, restore/migration, payment provider, tax/legal clearance, actual commercial release.
- Score: user requested final 50%; P50 standalone engine is a *bounded engineering target*. Official final blueprint WD-01..WD-14 **UNASSESSED** (no approved weighted trace, real-world gates untested); central `[작업중]` remains until accepted threshold.
