## P85 후속 PDF 출력/문건 미리보기 — 수용 한계 (2026-11-14)
- **R13 부분 보강:** 한국어 CID font mapping으로 로컬 임시 PDF 생성·기존 파일 덮어쓰기 금지. ReportLab 선택 의존성, PDF 글꼴/출력/고객 Win10·11 미검증; 정식 보고서 수용 미완.
- **R27–R28 부분 보강:** 명시적 고객 동의+적법 보유 근거가 있는 로컬 PDF/TXT 텍스트 언급 목록/체크리스트; pypdf 선택 의존성, 악성파일·스캔 PDF OCR·권리진위·법률검증 미지원. 원문 전문/개인정보는 DB에 미저장, 미확인 REVIEW_HOLD 유지.
- R01–R29 최종설계 축소 없음. 전체 공식 완성률은 승인 가중치·실정부/Windows/실고객 수용 전 **UNASSESSED**, 사용자 85% 목표 [작업중]·RELEASE HOLD.

---

# BID AX v2 현재 최종 요구 안내

R01–R21 기존 요구 보존 + R22–R26 온비드 공매 + R27–R29 법원경매 동의 로컬 문서/3원천 격리. 총 29개, 공식 최종완성률 UNASSESSED, 85% 목표 [작업중], RELEASE HOLD. 이 ZIP 안 아래 요구 문구는 역사적으로 보존한 v1/P85 단계입니다. 최신 전체 설계/검증 표는 GitHub product/bid-ax-public-procurement/docs/FINAL_BLUEPRINT.md 및 docs/P85_V2_CURRENT_ACCEPTANCE_20261114.md.

---

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


## 2026-11-13 added implementation acceptance evidence (no reduced scope)

- P70 goal = real Windows GUI + evidence-linked customer journey, report exports and local failure recovery; current **bounded offline implementation only**.
- Keep `R01–R21` full 100% denominator unchanged, and require owner-approved weights + exact-SHA evidence before any official final % number.
- Tested local Python 3.13.5 45 PASS/0 FAIL/0 SKIP, Tk 8.6 Xvfb smoke PASS. No official API call, Windows10/11 test, real G2B qualification, customer or legal acceptance.
- Separate human preliminary review log from actual legal qualification and authorized submission. No API keys saved, no original BID OWL copied.
- Read [P70 evidence and outstanding gates](docs/P70_STAGE_EVIDENCE_20261113.md) before advancing to EXE/scheduling or making a progress claim.


## P85 attempted milestone — no change of R01–R21 final denominator

Verified locally: page-staged partial imports, restart recovery, replay dedupe, durable reminders, mocked and capped explicit transport, safe source package. 80 synthetic/mock tests and Linux Tk smoke. **Not tested:** official data collection/rights and 100/10 evidence, Win10/11+Py3.11, EXE/signature/installation, user identity/ACL, PDF, customer/legal acceptance. Official completion `UNASSESSED`; 85% goal `[작업중]` remains. See `docs/P85_STAGE_EVIDENCE_20261113.md`.
