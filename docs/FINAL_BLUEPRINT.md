# BID AX — final product blueprint v2 (2026-11-13; v1 retained below)

**Purpose:** Public procurement preparation assistant for authorized bidder staff on a customer-owned Windows PC. Reduce manual bid search, evidence checking, deadline loss and version confusion; never autonomously submit bids or guarantee legal eligibility. This blueprint is the product's full 100% denominator, not the short prototype.

## End-to-end flow

Official authorized API+original document with source time/version → seven-day bounded incremental collection and local checkpoints → normalized immutable source-linked notice ledger (dedupes/revisions) → customer-controlled profile/verified licenses, regions, price and documents → deterministic fail-closed three-state preliminary screening + human approval → document checklist/expiry/deadline/reminder → printable Korean/JSON/PDF evidence report + backup/restore → customer acceptance.

## [2026-11-13 KST 사용자 승인] v2 확장 최종설계 — BID AX 3모듈

이 절이 구버전 R01–R21 표보다 우선한다. **기존 R01–R21은 수정/삭제하지 않고 보존**하며 신규 **R22–R29 8개**를 추가한다. 최신 전체 100% 분모는 **R01–R29 29개 최종 요구**. 기존 21개 표와 기술 P85 숫자는 이전 설계 이력이다.

| 상품 모듈 | 공식 소스/입력 | 사용자 기능 | 금지/차단 |
|---|---|---|---|
| A 나라장터 (기본) | 조달청 15129394 고객 승인 무료 API | 7일 범위 입찰 공고·면허·지역·서류·마감·변경·사전 검토 | 실제 자격 확정·무승인 자동입찰 금지 |
| B 온비드 공매 (확장) | 캠코 온비드 무료 공식 API별 고객 승인 신청 | 부동산·동산·차량 물건, 최저가/감정가, 유찰, 낙찰·취소 결과, 관심목록/알림 | '투자 적합' 판정/수익 보장·미허가 원문 재판매 금지 |
| C 법원경매 (프리미엄) | 고객이 적법하게 보유한 문서를 **로컬 직접 업로드** | 문건 연결·누락·권리/점유/비용 위험 체크, 원문 근거, 사람 최종 판단 | 공식 일반 경매 API 무료발급 확약/무허가 크롤링/법률판단 자동 확정 금지 |

**공통 데이터 경계:** source namespace, agency notice/property/case ID, revision, acquisition timestamp, source URL/document SHA256을 분리 보관한다. 나라장터 입찰 자격 엔진을 온비드 투자판단·법원경매 권리분석으로 재활용하지 않는다. 모듈별 고객 키/쿼터·원문 사용권·개인정보 보존정책·human approval·파일 백업/복원을 독립 검증한다. 판매 등급은 미출시 기획이며 크몽 등록을 뜻하지 않는다.

### 신규 필수 요구·수용조건

| ID | 최종 수용조건 | 현재 실제 구현 |
|---|---|---|
| R22 | 온비드 API 메타데이터·권리·상용 조건/약관·참조키 | 메타데이터만 확인, 코드 0 |
| R23 | 온비드 승인된 고객 키로 목록/물건/상세/페이지 증분 수집, quota/429/중단복구 | 미구현, 실호출 0 |
| R24 | 공고관리번호·물건관리번호·공매조건번호 원문 링크, 가격·유찰·SHA 버전 원장 | 미구현 |
| R25 | 온비드 낙찰·유찰·취소와 정정/변경 이력·중복/시점 오류 처리 | 미구현 |
| R26 | 온비드 필터/관심물건·비용/점유/권리/세금/명도 위험 체크리스트; 투자판단은 인간 | 미구현 |
| R27 | 적법하게 확보한 고객 법원경매 문서 동의 기반 로컬 업로드, 출처/해시/악성·민감정보 검증 | 미구현 |
| R28 | 법원경매 문건·물건 연결, 권리/위험 출처 표시·미확인 REVIEW_HOLD; 법률의견 보장 금지 | 미구현 |
| R29 | 3원천 ID/권한/데이터/보고 분리·tier/가이드/Windows·실고객 상업 수용 | 미구현 |

### 공식 API 근거·남은 권리 확인

- 나라장터 https://www.data.go.kr/data/15129394/openapi.do — 무료/이용허락 제한 없음 표시, 2026-11-10 조회기간 최대 7일. 실제 가입/운영 이용조건·실 응답·재배포 권리 미검증.
- 온비드 공고물건 https://www.data.go.kr/data/15157220/openapi.do — 무료 REST JSON/XML, 공고관리번호 pbancMngNo로 공고 내 물건 조회. 낙찰결과상세 https://www.data.go.kr/data/15157254/openapi.do — 물건관리번호 cltrMngNo 등으로 상태 상세 조회. **두 API는 별도 신청/별도 조회대상**; 전체 목록·검색용 관련 API 추가 조사 필요. 개발계정 1,000 트래픽 표기가 실제 모든 운영 계정의 무제한 사용을 의미하지 않음.
- 법원 사법정보공유포털 https://openapi.scourt.go.kr/kgso202m01.do — 일반 오픈API는 추후 제공 예정이고 연계 API는 publicapi@scourt.go.kr 별도 협의. 무료 일반 경매 API 키 발급·자동수집·상용 재판매 가능하다고 단정 금지.
- 각 API 무료와 유료 소프트웨어 상용이용 및 파일/이미지/등기 관련 제3자 저작권 재배포 허용은 독립적으로 심사한다. 고객 인증키·공고 원문·고객 파일을 GitHub에 업로드하지 않는다.

### 최종완성률 재산정

**R01–R29 29개, 신규 요구 8개 중 구현/실행 수용 0/8. 공식 최종완성률 = UNASSESSED (재산정 대기).** 최종설계 산정 규칙 OWNER-FINAL-BLUEPRINT-100상 사용자 승인 요구별 총 100점 가중치와 정확 Git SHA·실행·원문/권리/고객 수용 증거가 없으므로 임의 85%, 0%, 기타 점수를 계산하지 않는다. 이전 Linux 합성/mock 94 PASS는 과거 P85 내부 검증이며 신규 설계에 대한 실행이 아니다. 목표 85% **[작업중]**, RELEASE HOLD, 크몽 미등록 유지.

정밀 전수 상태는 [BID AX v2 29개 추적표](BID_AX_EXPANSION_REASSESSMENT_20261113.md)를 참조.

---

## Requirement trace (historic R01–R21 only; v2 now R01–R29)

| ID | Outcome / acceptance evidence | 2026-11-13 offline prototype |
|---|---|---|
| R01 | Official data.go.kr API current terms/operations, rights and provenance record | metadata checked; no live authorization |
| R02 | Authorized incremental listing/detail collection, all bid types, pagination | pure seven-day query plan only |
| R03 | Customer-owned API key, quota, throttle, retries and 429/5xx | unimplemented |
| R04 | Official source original attachments with timestamp and source version | official-domain URL guard only |
| R05 | Normalized notice field contract and validation | implemented + unit tested |
| R06 | Per-notice version history/immutable fingerprint/idempotent import | implemented + unit tested |
| R07 | Transactional local SQLite, dedupe, failure recovery | core implemented, restore unimplemented |
| R08 | Profile input validation, offline read/export | implemented input path; no profile persistence |
| R09 | Region/license/budget-based rules with explanations | prototype tested; real qualification unverified |
| R10 | Missing/unknown info never construed as legal qualification | review/fail-closed warnings tested |
| R11 | Required supporting documents with expiry and missing checks | prototype tested; no file inspection |
| R12 | Correct timezone deadlines and reminder scheduling | deadlines tested; reminders unimplemented |
| R13 | Audit/source-linked report + JSON/CSV/PDF export | JSON CLI only |
| R14 | Human final review/acceptance record and role separation | unimplemented |
| R15 | Update diff, deadline monitoring/checkpoint after PC resume | event history only |
| R16 | Korean interactive Windows GUI and guided setup | unimplemented |
| R17 | Windows installer/EXE, migration/uninstall/SmartScreen tests | unimplemented |
| R18 | Encryption/access hygiene, secure key handling, backup+restore | no key kept, backup created; restore unimplemented |
| R19 | 100 live notice cases and 10 qualification reviews incl. failure | unimplemented |
| R20 | Licensing/rights/terms, disclaimers, user guide and support | metadata checked; legal/customer acceptance unimplemented |
| R21 | Actual Windows10/11/customer pilot and owner release approval | unimplemented / RELEASE HOLD |

## Two designs and approved execution path

A — Hosted crawler/SaaS: stronger always-on, weaker infrastructure/PII/key security and recurring fees, larger ops burden. B — local Python/SQLite customer-owned key: zero required server fees, offline evidence security, cheap testability, but relies on on-PC refresh and user API quota. **B selected for the explicitly requested backend-first prototype**. The selected option does not erase any final R01-R21 acceptance gates.

## Official API context verified 2026-11-13

Official portal https://www.data.go.kr/data/15129394/openapi.do shows update **2026-11-10** and the max query period changed from one month to **seven days**, with JSON/XML, free use, license shown as unrestricted and developer baseline **1,000** requests. Service type-specific operations must be used; only the request-plan helper is implemented. No user key acquired, no remote call, no access to real notice, attachments, or business records. Full commercial conditions will be reconfirmed before sale.

## Progress and independent scoring

The 50-stage prototype target is an independent offline engine, input/output contract, API/rights metadata review and tests. The complete 100% blueprint has 21 requirements, many still absent. User-approved requirement weights remain **NOT_APPROVED**; therefore official final completion **UNASSESSED**, independent of the stage label. Never overwrite previous final completion records or release status based on a milestone pass alone.


## 2026-11-13 P70 engineering follow-up (not a change of final scope)

[Offline P70 acceptance and R01–R21 actual status](P70_STAGE_EVIDENCE_20261113.md). Local customer GUI, local version-diff + human review ledger, on-demand deadlines, JSON/CSV/HTML report and create-only backup/restore are tested in Python3.13.5 (45/45 PASS); Tkinter GUI Linux Xvfb smoke passed. Live official procurement, actual Windows, customer pilot, role separation, installation, PDF and seller/legal rights remain unverified. Official final completion `UNASSESSED`; approved weighted R01–R21 rubric missing; P70 is only a local engineering milestone and must not be marketed as final 70%.

## 2026-11-13 P70 follow-up
Source 027c4592e7aed1d806a9218269efe534952a8f04. Added offline G2B-format snapshot contract quarantine (never live HTTP), saved/reusable local multi-company SQLite profiles, and duplicate JSON key checks. Local Python3.13.5: 60/60 PASS, Tk Xvfb smoke PASS; six Git blobs match. Actual API response/Win10-11/Python3.11/customer/CI not verified. See docs/P70_HARDENING_EVIDENCE_20261113.md.
Full R01-R21 final completion remains UNASSESSED (approved owner weighting absent), target 70% [작업중] retained and RELEASE HOLD. Local DB profiles are plaintext, keep filesystem access restricted; never put real customer data or credentials into repo.


## 2026-11-14 최종설계 전체 진행 보강

`portfolio-report`, `onbid-filter`, `onbid-watch`, `onbid-watchlist` 명령이 승인된 로컬 스냅샷에 대해 동작합니다. 온비드 관심/검토보류/해제는 UUID 감사 이력으로 중복·변조·물건 변경을 감지합니다. Tk GUI의 '공매·경매 로컬 관리' 메뉴에도 같은 기능을 추가했습니다. 법적 자격·실시간 시세/낙찰·법원 권리 확정은 제공하지 않습니다. 로컬 전체 167 PASS, 원격 Python CI/실 Windows/실정부 API 미검증. 새 전체 R01–29 감사표: [전수 수용·미승인 가중치](docs/BID_AX_FULL_BLUEPRINT_29_ACCEPTANCE_20261114.md).
