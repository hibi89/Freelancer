> **[2026-11-14]** Onbid offline audit: `onbid-field-audit LOCAL_PACKET` prints documented field-presence **counts only**, never identities/values/key. `onbid-detail-queue LOCAL_PACKET --out NEW_LOCAL_FILE --consent` creates **unexecuted private local** result-detail candidate plans (never share queue). Mock regression 235 PASS Linux, actual item field values and customer Windows unverified. [Guide](docs/ONBID_OFFICIAL_FIELD_BRIDGE_20261114.md). Official final 85% NOT verified; release HOLD.

> **[2026-11-14 무료 API 공통 인증키 연결기]** 사용자 공공데이터포털 활용신청 완료 4개(나라장터1+온비드3), 인증키 동일. 로컬 CLI `api-probe`는 기본 무HTTP 계획/키입력 없음, `--live --out 신규파일`만 동의 후 임시 키 입력하여 별도 원문 격리 저장. 각 API 이용권/호출량은 독립. **온비드 공고물건 15157220은 실제 operation 미확인으로 호출 차단**. 실제 키·실 응답·Win/고객 검증 없음; [실행·보안 안내](docs/API_GATEWAY_SHARED_KEY_20261114.md). 공식 최종률 UNASSESSED, 목표85% [작업중]/HOLD.

## 2026-11-14 Optional Korean PDF and court document preview (P85 follow-up, unreleased)

- **Local bid report PDF:** `python -m bidax.cli --db customer.db export examples/profile.json NEW_REPORT.pdf --format pdf`. Requires manually installed optional `reportlab` (tested 4.4.9); CID font mapping `HYSMyeongJo-Medium` uses no bundled font binaries, PDF viewer rendering/Korean glyph acceptance and font rights must be checked before sale. JSON/CSV/HTML exports continue to use standard library only. Never overwrite an existing report.
- **Opt-in court PDF/TXT keyword preview:** `python -m bidax.cli --db customer.db court-preview USER_FILE.pdf --case-id 2026타경12345 --source-note "고객이 적법하게 제공한 원본" --consent`. Requires optional `pypdf` for PDF (tested 5.9.0). Parses up to 12 pages (maximum configurable internal limit 20), refuses encrypted/annotated/active PDF, never stores full extracted text, does not OCR or scan malware, and never interprets court rights as approved. Existing `court-import` remains metadata-only for backward compatibility. Missing text or checked terms do **not** prove absence of risks.
- Both optional libraries may need installation in the customer's local Python environment, and are not included in the source ZIP / current portable `.pyz`; neither performs network activity as part of these functions. Do not enable live APIs or ship an EXE based on the local test alone.

---

# BID AX v2 — 3모듈 소스 스냅샷 (2026-11-14 KST)

이 ZIP은 비출시 코드/테스트 스냅샷입니다. **전체 최종설계는 R01–R29(29개), 공식 최종완성률 UNASSESSED, 85% 미인증, [작업중], RELEASE HOLD**입니다. 나라장터/온비드 정규화 공고/공매와 소유자 동의 법원 자료의 오프라인 처리만 검증됐습니다. 최신 정본 STATUS/HANDOFF/FINAL_BLUEPRINT은 GitHub private hibi89/Freelancer@product/bid-ax-public-procurement HEAD d295a8869689272f14a37864716e69093d5ca351을 참조하십시오. 아래 문서는 이전 단계의 기록입니다.

---

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


## 2026-11-14 최종설계 전체 진행 보강

`portfolio-report`, `onbid-filter`, `onbid-watch`, `onbid-watchlist` 명령이 승인된 로컬 스냅샷에 대해 동작합니다. 온비드 관심/검토보류/해제는 UUID 감사 이력으로 중복·변조·물건 변경을 감지합니다. Tk GUI의 '공매·경매 로컬 관리' 메뉴에도 같은 기능을 추가했습니다. 법적 자격·실시간 시세/낙찰·법원 권리 확정은 제공하지 않습니다. 로컬 전체 167 PASS, 원격 Python CI/실 Windows/실정부 API 미검증. 새 전체 R01–29 감사표: [전수 수용·미승인 가중치](docs/BID_AX_FULL_BLUEPRINT_29_ACCEPTANCE_20261114.md).


## 2026-11-14 local API quarantine audit (nonrelease)

After an authorized one-page `api-probe --live --out` command, inspect saved metadata **without network/key**:

```powershell
python -m bidax.cli --db .\local\bidax.db api-inspect .\local\result_001.json
```

The inspector returns only structural audit metadata. A passing structure is NOT an official API mapping, source signature, allowed bulk import, legal qualification or a finished saleable feature. See `docs/P85_API_RESPONSE_QUARANTINE_AUDIT_20261114.md`.
