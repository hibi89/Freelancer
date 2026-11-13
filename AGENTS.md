# WORKNOVA Desk — product branch operating instructions

- This is a private independent customer-product branch. Source and specifications live in `hibi89/Freelancer@product/worknova-desk-local`; public PayPal hackathon source is a reference, not a deployment target or editable dependency.
- Before editing, read HANDOFF → STATUS → AGENTS → REQUIREMENTS → docs/FINAL_BLUEPRINT → source/tests; compare remote HEAD and avoid modifying main or other branches.
- Owner's full final blueprint is the only denominator for formal completion; until requirement weights are approved and each acceptance is verified at exact SHA, report **UNASSESSED**. P50 refers to a bounded engineering gate, not audited formal 50% of the full product.
- Keep WORKNOVA Desk **[작업중]** in the central kmong audit until confirmed final-blueprint P50 and owner-approved weights; retain RELEASE HOLD, separate product history, registered products, and existing marks.
- Do not read/write customer files outside paths explicitly supplied by user. Avoid symlinks, unapproved external services, PayPal CREATE/CAPTURE, AI/model APIs, auto email, invoicing authority, data-sharing, security changes, or paid workflow minutes.
- Store no secrets, customer records, identifiable evidence, or real payment credentials in GitHub. Local SQLite data and backups are outside GitHub; code/tests/docs only.
- Any change: run `PYTHONPATH=. python -m unittest discover -s tests -v`, inspect ledger/backup/privacy behavior, note exact code SHA and missing Windows/GUI/document acceptance, update STATUS/HANDOFF and central kmong audit as a unit. No false success claims.
