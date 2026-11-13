# STATUS — WORKNOVA Desk P85 offline recovery checkpoint

Updated 2026-11-13 KST · Private `hibi89/Freelancer@product/worknova-desk-local`.

**Official whole-final-blueprint completion UNASSESSED; user requested P85 NOT CERTIFIED. `[작업중]` remains. RELEASE HOLD / no actual product registration / no Production.** The WD-01..WD-14 blueprint and unapproved 100-point proposal remain unchanged.

## Verified in local Linux Python 3.13.5

- Existing offline customer/quote/revisions/contracts/milestones/receipts, controlled deletion, file evidence hashes, audit checkpoint, redacted DOCX/PDF, Tk GUI and portable prelaunch verification preserved.
- Newly implemented recovery drill: opt-in separate existing private scratch workspace; consistent online backup, SHA-pinned new-path restoration, six business/audit tables exact comparison, automatic scratch cleanup. Backup creation POSIX owner-only 0600 even under umask 022; no existing user files overwritten or permissions changed.
- Python regression **104/104 PASS, 0 FAIL, 0 SKIP**, original 97 + 7 recovery unit/CLI scenarios. See `docs/P85_RECOVERY_DRILL_20261113.md`.
- Portable v3 strict 13 source/script entries plus manifest; Linux extraction + preflight + throwaway CLI (and existing Tk8.6 Xvfb GUI flows) require final-source-SHA evidence in HANDOFF.

## Unverified / blockers

- Real Windows10/11 per-user PowerShell install, upgrade, launch, rollback, removal, data/ACL preservation, signed bundled EXE, Defender; actual Windows Word/PDF and rights; true OS authentication/ACL/disk encryption and administrator-compromise resistance; real buyer cases and legal/tax acceptance; approved complete 100-point WD rubric. No actual bank payment/provider API. These prevent official P85 certification and sales.
- No Vercel or public service planned; Production status **N/A**. Policy-only Actions do NOT count as product Windows CI.

## Rollback

Previous verified code `85a2a115d32d3378544ae68bb453466499aebcb8` in Git history. Do not touch owner databases, backups, main branch, PayPal source, other product statuses or licenses. Package v3 requires its paired v3 integrity verifier, do not mix with v2. Preserve source/test evidence exact SHA in central KMONG registry and `HANDOFF.md`.
