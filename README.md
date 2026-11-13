# BID AX — offline public procurement preparation (prototype)

**Private candidate; not for sale.** Separate from the excluded BID OWL project. Standalone Python 3.11+ standard-library engine; SQLite file stays on the customer's PC. No background daemon, HTTP traffic, account, embedded API key, ML, or subscription. This is **preliminary screening**, never a substitute for original bid documents or a licensed professional.

## Local commands

```bash
python -m unittest discover -s tests -v
python -m bidax.cli --db ./bidax.sqlite import examples/notices.json
python -m bidax.cli --db ./bidax.sqlite screen examples/profile.json
python -m bidax.cli --db ./bidax.sqlite history R26BK000001
python -m bidax.cli --db ./bidax.sqlite backup ./bidax-backup.sqlite
```

`import` accepts **normalized, previously authorized JSON fixtures**, not arbitrary downloaded HTML or official raw responses. A version is uniquely identified by `notice_no+revision+SHA256(normalized JSON)`; identical repeated imports do not duplicate events. Changed content is retained as an immutable additional event and the most recently ingested event is current. `backup` never overwrites an existing file. `screen` returns the three labels `적합/부적합/추가 확인 필요`, the clause-level reason, source URL/fingerprint, and an explicit human-verification warning; these are deterministic user-supplied inputs, not the legal status of a real bid.

The pure `official_query()` helper creates a **request plan only** (no key, network, log, or secret persistence) and rejects ranges over seven days. The actual authenticated API client, throttling/retry, official schema adapter, original notice attachment parsing, updated API 7-day behavior live test and commercial terms/country eligibility verification remain open. No external API calls were executed.

## Two architecture options

| Option | Strength | Cost / risk | Decision |
|---|---|---|---|
| A: hosted SaaS crawler | always-on scheduling and centralized support | hosting/secret custody, exposure, traffic and compliance | rejected for the 50-stage |
| **B: local standard-library engine + optional official user-key adapter** | local evidence ledger, no recurring infrastructure fees, easy support/testing | PC must run for refresh; customer API access and schema changes | **chosen for incremental development** |

## Data contracts and guardrails

See `docs/FINAL_BLUEPRINT.md` and `REQUIREMENTS.md`. There are no secrets in this repository. API documentation: https://www.data.go.kr/data/15129394/openapi.do (modified 2026-11-10: max 7-day query window, developer 1,000 requests, free entry, license displayed as no restrictions). This metadata is **not** an end-to-end legal authorization for every customer's commercial scenario and related data/attachments. Do not ship the product or promise eligibility without formal acceptance and current source verification.


## P70 extension (2026-11-13, offline only)

From the repository root with Python3.11+ and standard-library Tkinter installed:

```bash
python -m unittest discover -s tests -v
python -m bidax.cli --db ./bid_ax_local.db gui
python -m bidax.cli --db ./bid_ax_local.db import examples/notices.json
python -m bidax.cli --db ./bid_ax_local.db screen examples/profile.json
python -m bidax.cli --db ./bid_ax_local.db alerts --hours 72
python -m bidax.cli --db ./bid_ax_local.db export examples/profile.json ./bid_report.html --format html
python -m bidax.cli --db ./bid_ax_local.db changes R26BK000001
python -m bidax.cli --db ./bid_ax_local.db backup ./bid_ax_backup.db
python -m bidax.cli --db ./bid_ax_restored.db restore ./bid_ax_backup.db
```

Supported **new-file** exports: HTML (offline CSP, printable), CSV (BOM and formula-injection neutralization), JSON. No output file overwrite. UI actions: choose company profile, import normalized authorized notices, inspect preliminary decisions, source links and changes, record human review explicitly, check due/expired reminders when app is open, export, backup and restore into NEW paths. To record a review from CLI, use `review NOTICE_NO FINGERPRINT REVIEWER 확인|보류|반려 NOTE [--request-id UUID]`. Review does **not** legalize a bid or submit it.

No network client or authorized real API key is bundled: all examples are synthetic, and updates/reminders only reflect local files/PC sessions. **2026-11-10 official API query window is 7 days.** Python 3.13/Linux/Xvfb 45 PASS including GUI smoke; actual Windows10/11 GUI/installer and real G2B data NOT_RUN. [P70 evidence and full R01–R21 trace](docs/P70_STAGE_EVIDENCE_20261113.md). Official final blueprint completion **UNASSESSED**, RELEASE HOLD, `[작업중]` target 70.


## P85 local-only stage (2026-11-13)

```bash
python -Werror::ResourceWarning -m unittest discover -s tests -q
python -m bidax.cli --db ./local.db stage-page ./authorized-page1.json --batch-id 1d8ff697-e0ac-42e4-96ed-642176c0633f --category goods --start 2026-11-07T09:00:00+09:00 --end 2026-11-13T09:00:00+09:00 --obtained-at 2026-11-13T09:30:00+09:00
python -m bidax.cli --db ./local.db stage-status 1d8ff697-e0ac-42e4-96ed-642176c0633f
python -m bidax.cli --db ./local.db poll-alerts --hours 72
python packaging/build_source_zip.py ./BID_AX_SOURCE_ONLY.zip
```

`stage-page` reads a **local, authorized** API-shaped JSON file; it never performs HTTP. All expected pages must be staged before promotion, incomplete batches do not modify the current notice ledger. The `bidax.transport` opt-in helper is **not enabled** in CLI/GUI. For any real request, explicit customer permission, their own government key, license/source contract verification and quota planning are mandatory. Reminders require explicit user action while PC is on. `packaging/build_windows.ps1` is a **manual, unsigned build procedure only**, not a tested installer. See [P85 evidence](docs/P85_STAGE_EVIDENCE_20261113.md).

**Official final completion: UNASSESSED**, not 85%; `[작업중]`/RELEASE HOLD until weighted full-design independent acceptance.


### Portable Python package (P85 follow-up; not Windows EXE)

```bash
python packaging/build_portable.py ./BID_AX.pyz
python ./BID_AX.pyz --db ./local.db import examples/notices.json
python ./BID_AX.pyz --db ./local.db screen examples/profile.json
```

This deterministic `.pyz` runs with Python 3.11+ on a PC that has Python installed. It is **not an installer**, is unsigned, does not schedule or automatically call the government API, and was only executed under Linux Python3.13.5 with synthetic data. No claim of Windows customer readiness. See `tests/test_portable.py`.
