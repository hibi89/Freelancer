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
