# WORKNOVA Desk — Offline KRW quote-to-collection ledger

**Status (2026-11-13 KST):** independent P50 development prototype; formal final-blueprint completion **UNASSESSED**. Private-source development branch. **RELEASE HOLD / NOT FOR CUSTOMERS.**

WORKNOVA Desk is an offline local-first bookkeeping helper for freelance service delivery. It **does not** transmit payments, confirm a bank transfer, digitally sign a contract, provide tax/legal advice, call PayPal, or use AI. The entered `reference` is a manual receipt note, not independently verified payment evidence.

## Run (Python 3.11+, standard library only)

```bash
PYTHONPATH=. python -m unittest discover -s tests -v
PYTHONPATH=. python -m worknova_desk --db ./desk.sqlite init
PYTHONPATH=. python -m worknova_desk --db ./desk.sqlite customer --name '테스트 고객'
```

Next CLI flow: `quote --customer-id <ID> --items-json '[{"description":"디자인","quantity":1,"unit_krw":100000}]'` → `approve-quote --quote-id <ID> --actor owner` → `contract --quote-id <ID> --scope '시안 1종' --steps-json '[{"title":"1차 납품","amount_krw":110000}]'` → `activate --contract-id <ID> --actor owner` → `deliver --milestone-id <ID> --actor owner --note '납품'` → `accept --milestone-id <ID> --actor client` → `collect --milestone-id <ID> --actor owner --amount-krw 110000 --reference MANUAL-001` → `report --contract-id <ID> --html-out ./report.html` → `verify` → `backup --out ./desk-backup.sqlite`.

Milestone IDs are available in local SQLite query `SELECT id,title FROM milestones WHERE contract_id=?`. CLI customer IDs, quote IDs, and contract IDs are returned as JSON. The current P50 prototype is developer-facing; client GUI and guided milestone selection are P70 scope.

Default report masks customer names; HTML is script-free with restrictive CSP. SQLite data stays on the operator's PC, but **is not encrypted**: protect the database, backup and report files using OS disk permissions/encryption. Only synthetic test data has been exercised. Use an empty throwaway DB for testing. Existing customer DB migrations and Windows EXE/installer have not been validated.

Canonical product scope: [docs/FINAL_BLUEPRINT.md](docs/FINAL_BLUEPRINT.md). Feature trace and acceptance: [docs/P50_TRACE.md](docs/P50_TRACE.md). Original PayPal hackathon `lead/paypal` remains **read-only and unchanged**.
