# WORKNOVA Desk — functional and delivery requirements

Canonical whole-product design: `docs/FINAL_BLUEPRINT.md` (WD-01 through WD-14). Local P50 development gate is NOT final product-completion percentage.

- WD-01–05: customers, integer-KRW line items, explicit VAT, immutable approved quote, owner-activated contract, milestone amounts equaling approved quote.
- WD-06–08: delivery, revision, acceptance as separate human events; manual partial collection not before acceptance; no PayPal/AI/network execution; exact reference idempotency and overpayment refusal.
- WD-09–11: local SQLite append-only digest audit, backup integrity, privacy-minimizing script-free HTML/JSON; recovery and failure safety.
- WD-12–14: Korean customer GUI, DOCX/PDF printable documents, signed Windows delivery, sample/real-customer acceptance and legal/licensing checks.
- All requirements must be traced to source and executed tests; no invented final percentage. Private source, RELEASE HOLD until owner approval.
