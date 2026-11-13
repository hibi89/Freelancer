## [BID_AX_P70_DOC_SYNC_20261113] 70% 단계 실제 수용·미검증 (최종설계 축소 아님)
- R05–R15 일부 로컬 계약/조회/보고·수동 승인 아닌 검토 감사, R16 GUI 기본 흐름, R18 부분 백업/검증을 추가. 전체 R01–R21 완전 수용으로 간주하지 않는다.
- Linux Python3.13.5 **45 PASS/0 FAIL/0 SKIP**, Tk8.6 Linux Xvfb 실행 PASS, 기능 SHA `22d44f5e2fb39024703331903b881bec7bfd6521`. GitHub blueprint-only CI SUCCESS는 실제 Python 테스트 실행이 아님.
- API 응답/원문/권리, 보안 키/운영quota, 100 실공고·10 실제 자격 대조, 고객 Windows10/11, 설치/실시간 스케줄·PDF·고객 승인 부족. 공식 `UNASSESSED`, 70 목표 `[작업중]`/출시 HOLD.
- [세부 21개 추적](docs/P70_STAGE_EVIDENCE_20261113.md). 과거 REQUIREMENTS 본문은 보존한다.

# BID AX — requirements and acceptance (full product = 100%)

- R01-R04: official original source/permission and change-aware collection; region/kind/period; user-owned key/quotas; failures/retries/rate limiting; original evidence.
- R05-R08: normalized immutable/traceable records, dedupe/version, local SQLite and atomic failure handling, verified offline profile/notice schema.
- R09-R12: profile license/region/budget mapping; mandatory qualification/manual review; required document expiry/missing; time-zone aware deadlines.
- R13-R15: source-backed human-readable/exportable report; manual decision trace; change notices and reminders after PC resumes.
- R16-R18: Windows GUI, offline installer/update/uninstall, backup/restore/security access controls and 100-real-notice/10-qualification-case acceptance.
- R19-R21: bilingual/Korean user guidance; API/attachment commercial rights and policy/fee confirmation; customer pilot, support, sale owner signoff.

## 50-stage input/output contract

- Input: trusted local UTF-8 JSON array with normalized `notice_no`, `revision`, `title`, `category`, `issuer`, `deadline` (timezone offset), `source_url` (allowlisted official HTTPS), `regions`, `license_codes`, `required_documents`, optional `budget_min_krw` nonnegative integer.
- Profile: `company`, `regions`, `license_codes`, `documents` map of `name → YYYY-MM-DD` expiration, optional `max_budget_krw` nonnegative integer. Fields absent from official source must be explicitly represented as empty/unknown, never silently concluded eligible.
- Output: importer counts (`received/added_versions/unchanged`), immutable change event trace, three-state preliminary result (`적합/부적합/추가 확인 필요`), clause reasons, source URL/fingerprint and disclaimer.
- Errors: malformed/unknown JSON field, HTTP nonofficial source, missing timezone, invalid budget/date/schema → reject before transaction. No auto-submission, web scraping, credentials persistence or spending.
- 50-stage evidence: offline library/CLI + relevant unit tests on exact checked SHA, source/API contract verification and no sensitive data transfer. This is a **milestone definition**, not a validated official 50% final-completion score.

## P70/P85/P95/P100 blockers

1. Official response-JSON/XML normalizer and real officially authorized 7-day collection with 429/5xx backoff, TLS, resumable checkpointing, API usage limits and retry tests.
2. Bid attachment original-source clause mapping, document checklist evidence review, human decision record, local scheduled refresh and reminder reliability.
3. GUI/Windows executable with per-user access control, local encrypted secret storage if required, backup restore integrity, uninstall, Korean accessibility, PDF report.
4. At least 100 live notices/change/error reproductions and at least 10 documented human-reviewed qualification cases; real Windows PC and real customer acceptance.
5. Current copyright/commercial-use and API agreements, contract/liability texts, support policy, owner launch approval.

**Completion scoring:** user-approved per-requirement weights are not available. The official final-blueprint completion remains `UNASSESSED`; a unit-test pass or this 50-stage checkpoint is not mathematically 50% of R01-R21.

## 2026-11-13 P70 follow-up
Source 027c4592e7aed1d806a9218269efe534952a8f04. Added offline G2B-format snapshot contract quarantine (never live HTTP), saved/reusable local multi-company SQLite profiles, and duplicate JSON key checks. Local Python3.13.5: 60/60 PASS, Tk Xvfb smoke PASS; six Git blobs match. Actual API response/Win10-11/Python3.11/customer/CI not verified. See docs/P70_HARDENING_EVIDENCE_20261113.md.
Full R01-R21 final completion remains UNASSESSED (approved owner weighting absent), target 70% [작업중] retained and RELEASE HOLD. Local DB profiles are plaintext, keep filesystem access restricted; never put real customer data or credentials into repo.
