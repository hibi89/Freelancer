## [BID_AX_P70_DOC_SYNC_20261113] 새 고객 흐름 — 로컬 전용 P70

```bash
python -Werror::ResourceWarning -m unittest discover -s tests -v
python -m bidax.cli --db ./local.db gui
python -m bidax.cli --db ./local.db import examples/notices.json
python -m bidax.cli --db ./local.db screen examples/profile.json
python -m bidax.cli --db ./local.db alerts --hours 72
python -m bidax.cli --db ./local.db export examples/profile.json ./report.html --format html
python -m bidax.cli --db ./local.db changes R26BK000001
python -m bidax.cli --db ./local.db backup ./backup.db
python -m bidax.cli --db ./restored-new.db restore ./backup.db
```

Tkinter에서 기업 JSON을 열고, 정규화된 **사용 권한 있는** 공고 JSON만 가져온 뒤 사람의 검토/근거/기한을 확인한다. 보고서 JSON·CSV·HTML은 **새 파일**로만 저장, DB 복원은 **새 경로**로만 가능하며 원본은 절대 덮어쓰지 않는다. 알림은 앱 실행 중 확인만, 실 API·자동입찰·법적 적격 보증·유료 AI/서버/배포 없음. 기능 SHA `22d44f5e2fb39024703331903b881bec7bfd6521`, 45 PASS + Linux Xvfb GUI smoke, **공식 최종완성률 UNASSESSED / 70 목표 [작업중]**. [P70 추적](docs/P70_STAGE_EVIDENCE_20261113.md).

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
