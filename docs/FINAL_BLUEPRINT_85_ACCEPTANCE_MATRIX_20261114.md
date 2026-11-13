# CITEVAULT AX — 최종설계 100% 기준 85% 수용 증거표 (2026-11-14 KST)

> **판정 규칙:** 본 표의 분모는 `docs/FINAL_BLUEPRINT.md` 전체 확정 요구와 `REQUIREMENTS.md` 1~9 및 `docs/ACCEPTANCE_AND_ROADMAP.md` 수용 단계다. 테스트 PASS/비율이나 기존 RAG Studio 내부 진행률을 CITEVAULT의 최종완성률로 환산하지 않는다. 소유자 승인 가중치와 정확 커밋별 요구-증거 검증이 없어 **공식 최종완성률 UNASSESSED**. 사용자 목표 **85% 미달성/미검증**. `[작업중]`·`RELEASE HOLD`.

## 아키텍처 선택 (성능·비용·보안·유지보수)

| 선택지 | 초기비용·성능 | 보안·유지보수 | 판단 |
|---|---|---|---|
| A. 원본 RAG 전패키지 로드 후 문서 접근 차단 | 저비용·짧은 구현, 원본 BM25 재사용 | `loadPackage` 선로딩으로 허가 전 원문 메모리 유입; 기업 ACL 요구 위반 | 기업용 접근 경계로 불채택 |
| B. **현재 로컬 사전 ACL + SQLite 사용자/원문 버전 + 검증된 버퍼만 native parser + 검토 보류 SQL** | 추가 서비스 비용 0, 오프라인 실행·고객 LAN 분리 가능; 파서/권한 유지보수 발생 | 그룹/프로젝트 제한·불변 원본 SHA 검증. 실제 기업 신분·생산자 승인·전체 샌드박스 미완 | 합성 원본 기반 안전한 독립 검증 경로로 구현, 상용 서비스 아님 |
| C. 기업 IdP+서명 승인 PREP/SMAX+전체 원본 RAG 재연동 | 초기 구축·고객 승인·기기/모델 요구 커짐, 기업 기능 완결 | 신분과 문서 권한·법적 승인·실모델/호스팅 검증 필요 | 최종 설계대로 구현 필요, 현재 미완 |

## [2026-11-14 KST] 마지막 실제 회귀 검증 (제품 변경 SHA 대조)

- 로컬 Node v22.16.0/Python3.13.5 실제 검증: `node --test --test-concurrency=1 tests/*.test.mjs` = **129 PASS / 0 FAIL / 0 SKIP** (7개 P85 중심 테스트 파일 + 이전 suite; 129 카운트는 각 nested case 포함). `node scripts/p85-operator-demo.mjs --self-test` PASS.
- 신규 사용자 계정 10PASS(중첩 포함), 브라우저 UI 계약 6PASS, Korean n-gram 실제 BM25 6PASS. 원본 P85 vault27, HTTP17, SQLite14, native PDF/DOCX13, PDF+SQL journey18, Ed25519 review18 PASS. **총129는 이러한 P85 standalone/synthetic만**, 원본 RAG pin P50/P70 3SKIP과 고객 실 데이터/Win hosted CI를 포함하지 않는다.
- ZIP `CITEVAULT_AX_P85_operator_bm25_20261114.zip` 내부 25파일, 독립 압축해제 운영자 selftest PASS, BM25+UI 계약 **12PASS**, archive SHA256 `161bb8bc4069e8e6e51fa3b70d54e77911d9e884155c042517170b3119b2d5ca`.
- 실제 Chromium 렌더링 시도는 정책상 `chrome-error://chromewebdata/` / `Your organization doesn’t allow you to view this site`를 반환. 브라우저 접근 정책 우회 없이 중단; **브라우저 UI 렌더/Console/Network 미검증**, HTTP/static/js syntax 확인과 혼동 금지.
- 기업형 로컬 사용자·상시 검증 BM25의 **기술 범위는 확대**, 고객 실직원 IAM/IdP, source rights/producer approval, 실제 한국어 모델, 원본 RAG, Windows/고객 인수의 최종 수용 조건은 여전히 대기. **공식 UNASSESSED** 유지.

## 전체 설계 항목별 수용 표

**상태 구분:** `검증-합성` = 특정 합성 시나리오에서 실제 코드 실행 테스트 통과(실고객 완료 아님); `부분` = 일부 기술 검증/미완; `대기` = 실제 수용 증거 없음. 파일·검증 근거는 제품 브랜치 정본.

| 번호 | 사용자 확정 100% 설계 요구 | 현재 근거/실행 사실 | 상태 / 완료를 막는 것 |
|---:|---|---|---|
| 01 | 파일/데이터 소유권·사용권·개인정보·컬럼 검수 | `p70-local-review.mjs`·`p85-review-sql.mjs` 합성 CSV SHA/매핑 검토 HOLD | **부분**: 실제 고객 사용권·검토자 승인 없음 |
| 02 | PREP 실 파일 매핑/결측/반려 행 | P70 좁은 합성 5컬럼 mapping·review 검증 | **부분**: 실제 PREP 원본/고객 데이터 매핑 승인 없음 |
| 03 | SMAX² 정형 producer/typed normalization/행 계보 | 합성 원본 SHA와 P70 잠정 매출 교차 검증, 실제 typed producer 미연동 | **부분**: 원본 SMAX typed 직렬화 미검증 |
| 04 | 서명/권리 승인된 AX_DATA_PACKAGE_V0 발급 | `p85-signed-provenance.mjs` Ed25519 metadata 검증 18PASS, 항상 REVIEW_HOLD | **대기**: 진짜 producer/외부 신뢰키·법적 승인·정식 패키지 없음 |
| 05 | PDF 페이지·DOCX 문단·TXT/MD 행 | 실제 합성 2페이지 PDF 및 한국어 DOCX 문단 검증, TXT line 해시 검증 | **검증-합성**: 복잡 문서·OCR·XLSX는 별도 |
| 06 | 문서 2건 이상 동시 검색·인용·전용 범위 | P85 real PDF+DOCX 단일 /assess 종단·documentIds 사전 ACL, native13PASS | **검증-합성**: 고객 문서·코퍼스 검증 필요 |
| 07 | 원본 RAG BM25 검색/IndexBuilder | **신규:** 별도 P85 실 BM25 + 한국어 n-gram 검색을 읽기 전 ACL·SHA 검증을 통과한 인용 구간에만 적용, 단위 6PASS | **부분**: 정확 원본 RAG pin BM25·대규모 인덱스 연결/CI 3SKIP 미검증 |
| 08 | 원본 RAG fixed readonly SQLite SQL/typed KPI | P85 별도 `node:sqlite :memory:` 5컬럼 고정 집계, tamper 검증/HOLD | **부분**: 원본 RAG SQL/실 매출 VAT·환불 의미 승인 없음 |
| 09 | SQL+문서 혼합 라우터·출처 두 가지 | `p85-journey.mjs` localhost /v1/assess 실 PDF/DOCX+잠정 SQL 단일 요청 | **검증-합성**: 승인자료 기준 고객 조회 불가 |
| 10 | 정형 숫자 세금·환불·취소·SKU·기간 의미 통제 | 미지원 범위 `REVIEW_HOLD` 회피·비생성 검증 | **부분**: 고객 데이터 의미 확정·확장 쿼리 미구현 |
| 11 | 풀코퍼스 정책 상충·거절/insufficient | 특정 7/14일 반품 상충 `POSSIBLE_CONFLICT`, 무권한 문서 차단 | **부분**: 전체 도메인/한국어 정책 Gold 불충분 |
| 12 | 권한 있는 문서만 읽고 인덱싱 (tenant/group/project/classification) | vault는 ACL before byte read, SHA/inode/mtime/symlink/hardlink, 타조직 sales path 결속, 개별 테스트 | **검증-합성**: 생산형 multi-tenant index/TLS/파일 race 보안 미검증 |
| 13 | 실제 사용자·그룹·프로젝트·컬렉션 인증 | **신규:** 운영자 로컬 계정 발급, scrypt derived 저장, SQLite 재기동·다른 프로세스 로그인, scoped permission, admin만 발급·상속 권한 한도 | **부분**: 실제 고객 IdP/현장 관리자 승인·MFA/계정 초대 미검증 |
| 14 | 권한 변경·세션 철회·감사 | **신규:** `provisionUser/changeUserAccess` + SQLite transaction/audit, 기존 세션 권한 즉시 반영, 교차 프로세스 revoke | **검증-합성**: 생산 운영 복구·장기간 계정 정책 필요 |
| 15 | 문서 버전 교체·폐기·재색인 | `p85-state-store.mjs` durable revision/retire/reindex, SHA·gen·audit 테스트 | **검증-합성**: shadow index 원자 swap·백업/검색 동시성 추가 |
| 16 | 오프라인 사용자 UI/KPI/차트/출처 탐색 | **신규:** `p85-ui.mjs` localhost 로그인·문서 인용·매출 REVIEW_HOLD·계정 관리, strict CSP/no-store, JS 구문/HTTP/API 6PASS, local operator demo PASS | **부분**: Chromium 실렌더링은 검사 환경 조직 정책에서 localhost 차단; KPI/chart/Windows 미구현 |
| 17 | 한국어 실제 로컬 모델·선택 dense | 모델 미설치 fallback `SEARCH_ONLY`, 출처 없는 생성 차단 | **대기**: 실제 model weights·라이선스·Korean mini benchmark 없음 |
| 18 | 프롬프트 인젝션·ZIP·악성 파일·권한/데이터 유출 | bytes budgets, source SHA/inode/symlink, fail-closed, no network, XSS-safe UI textContent | **부분**: 문서 파서 OS 샌드박스/TOCTOU/침투 테스트·공식 보안점검 미완 |
| 19 | Windows10/11 오프라인 설치·백업/복구·라이선스 | Node/Python Linux localhost 셀프테스트, SQLite 재기동/문서 version 지속 | **대기**: 실제 Windows 패키지/물리 설치·백업/복구 인수 증거 없음 |
| 20 | Win/Linux GitHub-hosted CI 0FAIL | `.github/workflows/citevault-p50.yml` Linux/Windows native/identity/signed test job 설정 | **대기**: 실제 hosted job/run·Windows 성공 상태 미확인 |
| 21 | 고객 Gold100 + negative/heldout, retrieval/latency/메모리 수용 | 합성 보안 부정 테스트 및 단위 PASS, 모델/Gold100 없음 | **대기**: 고객 실제 100문제·성과 지표 미검증 |
| 22 | 백업/복구·삭제/보존기간·운영 정책 | 합성 SQLite account/doc/audit 저장·재시작 검증, 임시 데모 자동 삭제 | **부분**: 실 고객 보존/백업/삭제 요청·증거 이력/운영 가이드 미구현 |
| 23 | 고객/법적·가격·지원·운영 인수 | 합성 SOURCE_RIGHTS=false/RELEASE HOLD 강제 | **대기**: 고객/소유자 승인·라이선스·실기기·지원 수용 불가 |
| 24 | 5개 RAG 유형/대시보드/후속 질문 | 단일 문서·다중 문서·narrow SQL+문서 합성, 간단 UI | **부분**: conversational context, 실제 RAG 원본 end-to-end 미검증 |

## 85% 목표 필수 차단 항목

- 원본 `hibi89/RAG_STUDIO@c5867b3951f51bfa97cadd1aad8fb13e9cf9e604` 정확 pin 3 SKIP 통합 실행 및 original SQL/BM25/PDF/DOCX/SMAX 연결 미확인.
- 실제 고객형 IDP/신뢰 주체·직원·그룹·문서 권리의 고객/운영자 승인, signed PREP/SMAX→AX authoritative import 미구현. 로컬 합성 운영자 기능은 대체 증거가 될 수 없다.
- 실제 한국어 로컬 모델(아티팩트 SHA/라이선스/질문 세트) 없음, Win/Linux Hosted CI/실 Windows 설치/Gold 수용 미확인.
- 전체 요구의 소유자 확정 가중치 없음. 24행에서 PASS 수를 나눠 최종완성률을 임의로 추정하지 않는다.

**다음 우선순위:** (1) 정확 original RAG pin/Actions 로그 또는 검증 가능한 원본 패키지 확보 → 3SKIP 해소, (2) 고객 IdP/데이터 사용권·서명 producer 승인 조건 확정(민감 권한·자료 외부송신은 사전 승인), (3) licensed 실제 Korean model 미니 품질/보안 검수, (4) Win/Linux CI 실제 결과와 물리 Windows 환경 테스트, (5) 원본 최종설계 전체 REQ-by-REQ signed 검수 및 소유자 승인 가중치.

**공식 상태: UNASSESSED / 사용자 목표 85% 미달성·미검증 / [작업중] / RELEASE HOLD / SALE NO-GO.**
