## [2026-11-14] R01–R29 v2 실제 3모듈 수용 범위 (최신)
- R22–R26 일부: 온비드 로컬 JSON 원장(물건/결과/변경/출처/변조), 공식 API 15157220/15157252/15157254 **키 없는 비실행 조회계획**, 온비드 실 API 사용/원문·페이지/권리·고객 수용 아직 0.
- R27–R29 일부: 고객 동의 기반 로컬 PDF/TXT 문서해시, TXT 키워드·체크리스트(법적 판정 금지), 3모듈 GUI/DB 분리. 법원 일반 API, 원문 PDF 추출/악성검사/고객 법률자격 수용 없음.
- 기존 R01–R21 보존, 최종설계 29개 요구. Linux Python3.13.5 합성·mock **136 PASS**와 기능 SHA `2a9852bcb47a271a4119f67dfcaf8ec35ae2a632` 원격 12개 파일 동일성. 실제 Win10/11/파이썬3.11 런타임/실 API·100건·인간10건/독립 상용권 미확인.
- 공식 `UNASSESSED`, 85% `[작업중]`, `RELEASE HOLD` 보존. [상세](docs/P85_V2_CURRENT_ACCEPTANCE_20261114.md).

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

Verified locally: page-staged partial imports, restart recovery, replay dedupe, durable reminders, mocked and capped explicit transport, safe source package. 83 synthetic/mock/portable tests and Linux Tk smoke. **Not tested:** official data collection/rights and 100/10 evidence, Win10/11+Py3.11, EXE/signature/installation, user identity/ACL, PDF, customer/legal acceptance. Official completion `UNASSESSED`; 85% goal `[작업중]` remains. See `docs/P85_STAGE_EVIDENCE_20261113.md`.


## [2026-11-13] 사용자 확정 BID AX v2 신규 필수 요구 (최신 우선)

기존 R01–R21 유지, R22–R29 추가, **전체 R01–R29 29개**가 최신 최종설계 100%. 나라장터 기본/온비드 공식 무료 API 확장/법원경매 적법한 로컬 문서 분석 프리미엄. 무허가 크롤링·법률 확정·자동입찰 금지. 사용료 무료는 이용/재배포권 전체 승인이 아님.

- **R22** 온비드 API 메타데이터·권리·상용 조건/약관·참조키 — 메타데이터만 확인, 코드 0
- **R23** 온비드 승인된 고객 키로 목록/물건/상세/페이지 증분 수집, quota/429/중단복구 — 미구현, 실호출 0
- **R24** 공고관리번호·물건관리번호·공매조건번호 원문 링크, 가격·유찰·SHA 버전 원장 — 미구현
- **R25** 온비드 낙찰·유찰·취소와 정정/변경 이력·중복/시점 오류 처리 — 미구현
- **R26** 온비드 필터/관심물건·비용/점유/권리/세금/명도 위험 체크리스트; 투자판단은 인간 — 미구현
- **R27** 적법하게 확보한 고객 법원경매 문서 동의 기반 로컬 업로드, 출처/해시/악성·민감정보 검증 — 미구현
- **R28** 법원경매 문건·물건 연결, 권리/위험 출처 표시·미확인 REVIEW_HOLD; 법률의견 보장 금지 — 미구현
- **R29** 3원천 ID/권한/데이터/보고 분리·tier/가이드/Windows·실고객 상업 수용 — 미구현

실 API/Windows/권리/고객 수용과 요구별 승인 가중치 미확보 → 공식 **UNASSESSED**, 사용자 목표 85% [작업중], 출시 HOLD·미등록. 정본 docs/FINAL_BLUEPRINT.md, 29개 전수 docs/BID_AX_EXPANSION_REASSESSMENT_20261113.md.
