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
