> **최신 우선 해석 — 2026-11-14 KST:** 사용자 `배점안승인`으로 `docs/FINAL_BLUEPRINT_WEIGHT_PROPOSAL.md` WD-01~14 100점은 **이미 승인된 최종 정본**입니다. 이 파일 아래 과거 '미승인' 기록은 승인 이전의 역사적 이력이며 더는 현재 가중치 상태가 아닙니다. 기존 설계/가중치는 변경하지 않습니다. WD-13 추가 개발은 오프라인 Windows PyInstaller onedir 빌드 **준비 코드**만이며 실제 exe·Win/ACL/서명 검증은 별도입니다. 근거 `docs/P85_WINDOWS_EXE_CANDIDATE_20261114.md`; 전체 인정 0/100, [작업중], RELEASE HOLD.

## 2026-11-14 P85 schema and privacy safety follow-up

- WD-01: redacted-by-default local JSON customer portfolio with amounts/status only; requires second explicit flag to include customer name. Out-of-band OS folder privacy remains user's responsibility; no multiuser authorization or retention/legal erasure.
- WD-08/09: treat unrelated SQLite v0, pre-existing blank file, corrupted bytes, incomplete v2 catalog and altered audit as unsafe on open; fail before creating product tables. Existing valid v1 migrates only via explicit backup. Checkpoint is unsigned.
- WD-11/13: GUI button and package manifest add `worknova_desk/privacy.py` (14 source/script entries + manifest); Python-required portable ZIP, no signed EXE or real Windows validation.
- New negative/functional tests: 19, all passing locally along with original 104; four GUI Xvfb scripts and 14-file extracted package proof. No reduction of WD-01–WD-14 or accepted percentage. Formal final rate **UNASSESSED**, P85 not yet certified, `[작업중]` and RELEASE HOLD.

---

## 2026-11-13 P85 customer lifecycle/evidence acceptance follow-up (no scope reduction)

- WD-01 **partial local implementation:** guarded customer rename and delete only when there are no quotes; account roles/authentication and full owner privacy lifecycle still incomplete.
- WD-06 **partial local implementation:** explicit read-only local delivered-file SHA256/size audit and reverify. No external delivery proof, buyer identity verification or binding acceptance.
- WD-08 **partial:** inherited unsigned SHA chain. Tamper-proof external audit remains incomplete.
- WD-13 **partial:** updated Python-required portable ZIP exact 12 file preflight/PowerShell script allowlist. Standalone signed EXE and real Windows still unverified.
- Full WD-01..14 and 100% final blueprint unchanged, with owner-approved requirement weights still missing: official rate **UNASSESSED**, P85 goal not certified, `[작업중]`, RELEASE HOLD.

---

# WORKNOVA Desk — functional and delivery requirements

Canonical whole-product design: `docs/FINAL_BLUEPRINT.md` (WD-01 through WD-14). Local P50 development gate is NOT final product-completion percentage.

- WD-01–05: customers, integer-KRW line items, explicit VAT, immutable approved quote, owner-activated contract, milestone amounts equaling approved quote.
- WD-06–08: delivery, revision, acceptance as separate human events; manual partial collection not before acceptance; no PayPal/AI/network execution; exact reference idempotency and overpayment refusal.
- WD-09–11: local SQLite append-only digest audit, backup integrity, privacy-minimizing script-free HTML/JSON; recovery and failure safety.
- WD-12–14: Korean customer GUI, DOCX/PDF printable documents, signed Windows delivery, sample/real-customer acceptance and legal/licensing checks.
- All requirements must be traced to source and executed tests; no invented final percentage. Private source, RELEASE HOLD until owner approval.


## P70 additions (technical milestone, not full final-completion 70%)
- Immutable v2 quote root + sequential parent links with explicit revision creation; approved original quote/contract protected. Legacy v1 DB auto-upgrade forbidden; explicit backup-before-migrate.
- SHA-256 verified, non-clobbering backup recovery into new destination; integrity and audit check; SQL source/target comparison.
- Korean offline Tkinter local GUI with customer filtering, quote entry/revision, owner approval, contract and milestone actions, manual partial collection and redacted review HTML.
- P70 Linux scoped regression and GUI virtual-display smoke required, plus Windows user acceptance before commercial score.
- Preserve all 14 canonical WD requirements; formal user final percentage remains UNASSESSED pending 100-point weights, exact-SHA acceptance and external gates.

## P85 engineering gate additions, 2026-11-13

- Must preserve baseline P50/P70 and schema v2, use no network and do not change PayPal original.
- WD-10/12: export redacted Korean quote/contract review DOCX without external dependencies; optional user-rights-cleared Korean TTF PDF, reportlab optional. No PDF claims if font missing. All document paths must be new, user-initiated; emit hash.
- WD-11: GUI user action triggers local quote/contract DOCX / PDF; customer disclosure remains opt-in and is disabled by default.
- WD-13: verify deterministic ZIP source allowlist + SHA manifest and provide unsigned Windows per-user Python portable install candidate with app/data split, dry-run and rollback. A Python prerequisite/unsigned PowerShell **must not be advertised as a native EXE or signed installer**.
- WD-14: record 10 synthetic industry cases separately from actual customer legal and accounting signoff.
- Official final 85% not claimable without owner-approved weights/full WD-01..14 evidence; `[작업중]` and RELEASE HOLD unchanged.

## Current P85 hardening gate (not completion certification)
- WD-08: add user-controlled independent hash checkpoint (six table fingerprints + audit-head; new-only JSON; separately retained SHA). Does not defend against malicious rewrite of both DB and saved checkpoint.
- WD-13: v2 portable exact-file hash preflight in launcher; no EXE/signature, PowerShell not Windows-tested.
- Exact local tests and outstanding acceptance: `docs/P85_HARDENING_20261113.md`. All WD-01..WD-14 remain the final denominator; their approved weights are unavailable; **official final completeness UNASSESSED / P85 objective not certified**.

## 2026-11-13 further P85 safety acceptance (no scope change)

- WD-09: no silent empty-DB recreation for CLI existing-ledger operations; GUI first-run confirmation; explicit CLI `init`; no automatic customer backup restoration or overwrite.
- WD-13: Windows installation must ship its own `FILE_MANIFEST.json` and permit every required verifier file, checksum the stage before swapping app, fail on unexpected executables and `__pycache__`. Linux staging model tests are **not** physical Win10/11 validation.
- New POSIX SQLite files should be `0600` with existing permissions unchanged; Windows ACL, encryption, signed standalone EXE and real owner access controls remain **NOT RUN / incomplete**.
- Weighted final-score proposal `docs/FINAL_BLUEPRINT_WEIGHT_PROPOSAL.md` is explicitly **NOT OWNER APPROVED**, not permission to declare 85%. Keep central `[작업중]`, RELEASE HOLD.

## P85 owner-safe recovery validation, 2026-11-13
- WD-09: explicit `rehearse-restore` using an operator-selected *separate* existing private workspace; SHA256-pinned new-path restore and six-table snapshot check, temporary files deleted, source database not changed; Python Linux regression executed. New POSIX backups use owner-only 0600. No real Win10/11 ACL/power-loss proof.
- WD-13: offline source manifest format v3 includes `worknova_desk/recovery.py` in its strict 13-file allowlist. Older v2 packages remain separate rollback artifacts; a v3 package must only be checked with its paired v3 verifier. No signed standalone EXE.
- The WD-01..WD-14 full final blueprint, unapproved 100-point rubric, UNASSESSED official score, `[작업중]` and RELEASE HOLD remain unchanged.


## P85 follow-up — offline optional encrypted backup (no final scope change)

- WD-09/WD-13 partial: authenticated backup using AES-256-GCM, scrypt, random salt/nonce, non-overwriting restore into a NEW SQLite file, wrong-password/tamper/bad-format failure isolation.
- Encrypt **backup only**; the live ledger remains plaintext, optional cryptography is NOT distributed, OS permissions and multi-role authentication remain required for release.
- Never transmit secrets or customer files, put password in CLI argv, overwrite backups, or infer native Windows success from Linux tests. Final WD-01..14 weighting remains unapproved and formal rate UNASSESSED.
