# WORKNOVA Desk P85 Windows acceptance and owner-only blockers — 2026-11-14 KST

**Status: official whole-product completion UNASSESSED; P85 not certified.** Preserve [작업중], RELEASE HOLD, existing full WD-01..14 scope and unapproved 100-point proposal.

## Why P85 has not been reached

- The source is tested locally (125 Python tests and four Linux Tk/Xvfb user flows), but engineering-stage labels and test counts are not percentages of the final blueprint.
- Physical Win10/11 Python/Tk, native non-admin PowerShell install/upgrade/rollback/uninstall, app-data persistence and document print still lack native results. Linux tests cannot certify them.
- Independent signed EXE, OS authentication/encryption, legitimate fonts and legal/NOTICE/support reviews, ten genuine buyer acceptance cases and approved WD-01..14 weights remain outstanding.

## One zero-cloud-cost owner step

On an owned Windows 10/11 computer with Python 3.11+ and Tk, inside a checkout of this private branch:

    py -3 -B tools\windows_acceptance.py

The tool creates only synthetic data below a new temporary LOCALAPPDATA for child processes; it runs the unmodified PowerShell script without administrator privilege or policy bypass, checks local package integrity, install/upgrade/uninstall and offline recovery, and cleans the temporary workspace. No existing customer data or ordinary app data is selected. Only share the final JSON summary. FAIL means Windows NOT VERIFIED; do not disable Windows protections to force PASS.

A PASS is narrow Windows synthetic acceptance, **not** evidence of signed EXE, real buyer UX, legal rights, genuine real-money settlement or completed 85%.

Alternative: a windows-latest GitHub Actions runner may consume private repository minutes or cost. No such paid/hosted run is authorized or initiated here.

## Local evidence

Linux Python 3.13.5: 125/125 unit tests PASS, 0 FAIL, 0 SKIP; four Tk8.6 Xvfb GUI flows PASS; portable ZIP rebuild PASS. New Windows runner deliberately refuses Linux with exit 3. **Native Windows execution NOT RUN.**

Next: review Windows JSON, approve/change 100-point weight proposal, complete OS auth/encryption, independent EXE and real buyer/license/legal gates; continue [작업중] and RELEASE HOLD until verified.
