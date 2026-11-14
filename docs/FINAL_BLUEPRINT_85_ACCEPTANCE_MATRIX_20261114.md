# CITEVAULT AX — 최종설계 100% 기준 85% 수용 증거표 (2026-11-14 KST)

## [2026-11-14 10:25 KST] Real Korean E5 ONNX hosted inference verified

- Exact tested code SHA a3ffc4ba5a05e0b140ba08d8f248b6b0bc44e64e; [actual Actions run #43540387093](https://github.com/hibi89/Freelancer/actions/runs/43540387093) Ubuntu24.04 1/1 SUCCESS. Python 3.11 4/4 unit contracts PASS; SHA-matched ephemeral downloaded ONNX 118,054,593 bytes; real CPU inference 384 dimensions; fixed synthetic Korean query/positive/negative retrieval 3/3 correct, cosine margins [0.09215, 0.12037, 0.05195], 1,145ms measured for 9 synthetic embedding inputs on runner.
- Initial run #43540283742 at SHA 44e3e8a0 had 0-job YAML parse FAIL because pip --only-binary=:all: bare scalar colon+space; corrected workflow with run folded scalar at SHA a3ffc4ba. No repeated failed workflow needed.
- Only public model downloaded into GitHub hosted ephemeral environment; no weights/customer files/secrets checked into repository, no paid service. Original ACL/BM25 SEARCH_ONLY path, RAG, PREP/SMAX and production untouched.
- Existing CITEVAULT core CI #43537747863 still 8/8 SUCCESS 469 executed tests PASS on exact earlier source f4f5f088; THIS latest documentation change did not rerun core tests. No real customer Gold100, authorized PREP/SMAX production AX import, employee IdP, real Windows10/11 installer, security/legal/model redistribution licensing acceptance.
- OFFICIAL FULL-24-REQ FINAL COMPLETION UNASSESSED / 85% NOT CERTIFIED / [작업중] / RELEASE HOLD / SALE NO-GO. Public shared Freelancer historical branches still need secrets/IP audit.


## [2026-11-14 KST] REQ17 실 Korean ONNX 모델 후보 SHA 사전검사

- `f4f5f088b9fb2d89937c825445c035d1a4da0ca2` [hosted #43537747863](https://github.com/hibi89/Freelancer/actions/runs/43537747863) **8/8 SUCCESS, 469PASS/0FAIL/0SKIP**(OS반복), 신규 offline model file preflight 7PASS×2OS, real inference는 미실시.
- SHA `4d24e2bc01a447951524466ef533e52944bf48509e6552810bcee1a2711cb02c` 고정 `multilingual-e5-small` ONNX 파일 검사, 허위 파일/경로/누락 metadata 실패 확인. 원본 모델 카드 MIT 표시/변환 모델 상용 재배포 license 미확정, ONNX 가중치 118MB **미다운로드**, 실제 Korean retrieval/LLM 평가 미완.
- **공식 전체 완성률 UNASSESSED, 사용자 목표85% 미인증, [작업중]·RELEASE HOLD** 유지. 상세 `docs/P85_KOREAN_MODEL_PREFLIGHT_20261114.md`.


## [2026-11-14 KST] REQ16 사용자 실제 Windows 부분 증거 + 쉬운 검색 화면 CI PASS

- 사용자 직접 Windows PC에서 이전 정본 SHA `62663721...` synthetic localhost QA `PASS` 및 synthetic operator 로그인/문서1건/컬렉션1개/SEARCH_ONLY 출처 policy line1 화면을 대화 스크린샷으로 확인. OS 버전, 정식 설치기, 고객 인증/실자료, 현재 신규 UI 실기기 실행은 미검증; 스크린샷 파일은 GitHub에 올리지 않음(임시 비밀번호 포함).
- 이번 실 UI 기능 SHA `62fe69bd9f78f5a9a2c49f53b5f227053503a4f1`, [#43536006934](https://github.com/hibi89/Freelancer/actions/runs/43536006934) **8/8 SUCCESS, 455 PASS/0FAIL/0SKIP**(OS 중복), 신규4×2OS simple UI + 실제 Chromium collapsed/advanced/한국어 검색/후속 질문/권한/390px 검사.
- 전체24항 **UNASSESSED / 85% 미인증 / [작업중] / RELEASE HOLD**. 고객형 IAM, 권리, 원본 signed producer AX, 실제 Korean model, customer Gold/물리 OS-version-specific installer/legal signoff 미해결.


## [2026-11-14 KST] P85 REQ24 bounded 후속대화 + REQ19 Windows portable 기능 증거

- 기능 `f2979aa50156b4f5c3d80f4d23a1b2ec336f0040`, [실제 Actions #43531986943](https://github.com/hibi89/Freelancer/actions/runs/43531986943) **8/8 SUCCESS, 447 executed PASS/0FAIL/0SKIP**(OS별 중복 포함).
- REQ24: 근거 문서+세션에 결속한 후속 질문(5분 TTL, ACL·해시/version 검사, revoke/retire/change/expire 맥락 무효화), Windows/Linux 각12PASS, Chrome UI 클릭 E2E; 실제 기업 신원/한국어 생성형 모델·고객 RAG 통합 미완.
- REQ19: Windows2022 Node22 실행 파일 포함 **합성** offline 폴더+SHA manifest→Python zipfile CRC/sha roundtrip→실제 압축 해제 Node 실행 2PASS. Node 라이선스/물리 Windows10/11 설치기·고객 품질 미검증; ZIP은 CI 임시 파일, 배포하지 않음.
- 기존 문제 PowerShell ZIP 두 번 오류 후 방법 중단·Python pivot, Chrome profile teardown ENOTEMPTY 보강 후 이번 정확 SHA CI 전체 성공. 공식 `UNASSESSED`/목표85 미인증·`[작업중]`·RELEASE HOLD. 상세 `docs/P85_CONVERSATION_PORTABLE_20261114.md`.


## [2026-11-14 KST] REQ16 실제 Chromium UI·ACL 제한 KPI/차트 검증

- 기능 `49918ad4d0de23b8bc462830fa0789e93ebd7936`, [CI #43529432977](https://github.com/hibi89/Freelancer/actions/runs/43529432977) **7/7 SUCCESS, 421 PASS/0FAIL/0SKIP**(중복 OS 포함), 신규 scope library8PASS/OS·actual Chrome desktop/mobile 1PASS.
- REQ16: 서버 ACL 사전 필터 `GET /v1/library`; 사용자별 허용 문서 수/KPI, 컬렉션별 차트, 문서 선택, 로그아웃 클리어. Hosted Ubuntu actual Chrome 렌더·390px 모바일·스크린샷 생성·검색·로그아웃·JS exception0·외부 HTTP0 검증. 실 고객 Win10/11 브라우저/E2E는 여전히 별도.
- 실제 기업 IAM·승인된 고객 문서·AI Korean model/성능·Windows 실물 설치·고객 Gold100/라이선스/법무·24항 owner weighted acceptance 미충족. **공식 UNASSESSED, 85% 미인증, [작업중]·RELEASE HOLD**.


## [2026-11-14 KST] REQ22 실코드 보강: SQLite active catalog↔백업 원문 SHA 정확 일치

- 기능 `d32f530e2425da0129a4eb2e9a4a7aef6708dab8`, [CI #43527372030](https://github.com/hibi89/Freelancer/actions/runs/43527372030) Win/Ubuntu **6/6 SUCCESS, 404 PASS/0FAIL/0SKIP**(반복 포함).
- REQ22 실제 추가 검증: SQLite 4개 스키마 + format/gen + live active metadata `tenant/id/version/kind/SHA`와 snapshot 원문 bytes 교차 검증, 카탈로그 변조+manifest 재해시/HDR-only DB 거부. 로컬12PASS, 양 OS 각각12PASS. `docs/P85_SNAPSHOT_CATALOG_INTEGRITY_20261114.md`.
- **유효 백업 제품·실 고객 데이터 사용권·소유자 서명 승인·운영중 서비스 복구 보장은 아직 아님.** 공식 UNASSESSED, 85% 미입증, [작업중]/RELEASE HOLD.


## [2026-11-14 KST] 수동 SQLite 백업·복구, 합성100 질의 양 OS 실검증 추가

- 정확 기능 `0cf969fb2908cca985f4655d2c713ad7e030d168`, [GitHub hosted #43525453183](https://github.com/hibi89/Freelancer/actions/runs/43525453183) **Ubuntu+Windows 6/6 SUCCESS, 398 PASS/0FAIL/0SKIP**(중복 OS 횟수 포함); 기존 pinned RAG 35 upstream + CITEVAULT bridge36도 PASS.
- REQ22: 오프라인 **합성** SQLite+문서 수동 snapshot/복구를 SHA256 manifest+원자적 create-only 방식으로 구현, Windows/Linux 각9PASS. 실제 고객 자료·장시간 보존정책/무중단 복구·복구 운영자 권한 미완.
- REQ21: **합성** 한국어 100 질의(문서검색20/근거부족20/충돌20/비인가 직접조회20/혼합권한20) 양 OS 각1개 harness PASS, p95 Ubuntu0.328ms / Windows1.001ms. **실 고객 Gold100, retrieval recall/heldout, model 정확도 및 계약 성능 미검증**.
- REQ19: Win2022 hosted 기능 검증 ≠ 실제 Windows10/11 고객 프로그램 설치/복구 완료; REQ17 실 한국어 로컬 모델 미확보. 공식 `UNASSESSED`, 사용자 목표 85% 미검증, `[작업중]` 및 `RELEASE HOLD` 유지.


## [2026-11-14 KST] 최신 정확 SHA Hosted CI 6/6 성공 — 최종 설계 분모는 불변

- 기능 SHA `cea0ec09ac4a85a16e369bd302986959fca408b0`, [CITEVAULT hosted #43523337142](https://github.com/hibi89/Freelancer/actions/runs/43523337142) Ubuntu/Windows 6개 작업 **모두 SUCCESS**, 원본 RAG pin source-bound P50/P70 bridge **36 PASS/0SKIP** 및 pinned upstream35PASS. Ubuntu/Windows P85 로컬 권한·SQLite·UI/서명/검색 각각107PASS, native PDF/DOCX/SQL journey 각각31PASS, local-contracts31PASS. 플랫폼 간 중복 포함 **378회 실행 PASS/0FAIL/0SKIP**. [정책 gate](https://github.com/hibi89/Freelancer/actions/runs/43523337300) SUCCESS.
- 기존 불확실했던 호스티드 runner, 정확 원본 RAG CI 브리지 3 SKIP, Windows 한국어 DOCX, SQLite cleanup 오류는 **이번 SHA에서 실제 검증 해결**. 단, 고정 원본 RAG synthetic bridge 통과가 고객 권리 승인된 기업 제품 종단 완료라는 의미는 아님.
- 공유 `Freelancer` 저장소 현재 PUBLIC(소유자 조치), 다른 브랜치/과거 이력 공개 위험; 전체 비밀스캔 미실시, 운영 보안 이슈 별도.
- REQ20 CI 작업 실행 자체는 **검증-합성**, 원래 최종 24개 요구 중 IdP·고객 권리/producer·실 모델·Win10/11 물리 설치/Gold/사용자 수용은 여전히 미충족. 공식 최종완성률 **UNASSESSED**, 목표 85% **미검증**, `[작업중]/RELEASE HOLD`.


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

## [2026-11-14 KST] PREP/SMAX Ed25519 실 경로 통합 추가 (추가 증거)

- **실제 개발:** 합성 검토 `p70-local-review.mjs`의 PREP 매핑 파일 bytes SHA256 검증, `p85-review-sql.mjs` 정확 SQLite 결과로 매핑 digest 전달, `p85-journey.mjs` / `p85-signed-review-gate.mjs`가 host-trusted Ed25519 key·source SHA·mapping SHA·tenant·key ID·version/expiry 검사. `POST /v1/assess`에서 서명 실패 시 수치/인용 불반환. 유효한 서명에도 **answer null/REVIEW_HOLD**, 사용권·권한 승인 기능 없음.
- **검증:** Linux Node22/Python3.13 이번 변경 후 **10개 P85 독립 테스트 파일 합산 138PASS/0FAIL/0SKIP**, HTTP 서명 통합 신규9PASS, 기존 doc+SQL journey18PASS·HTTP17PASS 등. **단일 전체 runner invocation은 timeout**이므로 hosted CI/one-shot PASS라고 주장하지 않음. ZIP CRC+압축해제 신규9PASS/운영자 E2E PASS. 소스5파일 local Git/GitHub remote blob exact. 근거 `docs/P85_SIGNED_REVIEW_INTEGRATION_EVIDENCE_20261114.md`.
- **원본 RAG CI:** RAG Studio 과거 run 43231121679 Windows+Ubuntu SUCCESS를 확인했으나 **CITEVAULT pinned SHA 연동이나 이 제품의 CI 결과가 아니다**. 원본 3SKIP·고객 IdP/권리·실 한국어 모델·Win 실제 hosted/물리 인수·Gold 여전히 미검증.

## 전체 설계 항목별 수용 표

**상태 구분:** `검증-합성` = 특정 합성 시나리오에서 실제 코드 실행 테스트 통과(실고객 완료 아님); `부분` = 일부 기술 검증/미완; `대기` = 실제 수용 증거 없음. 파일·검증 근거는 제품 브랜치 정본.

| 번호 | 사용자 확정 100% 설계 요구 | 현재 근거/실행 사실 | 상태 / 완료를 막는 것 |
|---:|---|---|---|
| 01 | 파일/데이터 소유권·사용권·개인정보·컬럼 검수 | `p70-local-review.mjs`·`p85-review-sql.mjs` 합성 CSV SHA/매핑 검토 HOLD | **부분**: 실제 고객 사용권·검토자 승인 없음 |
| 02 | PREP 실 파일 매핑/결측/반려 행 | **신규 통합:** 검증된 `prep-mapping.json` 실제 파일 바이트 SHA256 + 원본 CSV SHA 바인딩, 서명 없는 수정/단순 공백 재직렬화도 거부(실 테스트) | **부분**: 실제 PREP 원본 생산자/승인된 고객 필드 매핑·의미 검증 미완 |
| 03 | SMAX² 정형 producer/typed normalization/행 계보 | **신규 통합:** 실제 합성 SMAX review + PREP 매핑 + Ed25519 원본·매핑 해시를 SQLite 검산과 HTTP 조회에 연결, 신규 9PASS | **부분**: 실제 원본 SMAX typed producer/서명키·고객 검토자 미연동 |
| 04 | 서명/권리 승인된 AX_DATA_PACKAGE_V0 발급 | **신규:** `p85-signed-review-gate.mjs` 서명 검증을 단독 계약에서 `POST /v1/assess` 실검증 경로로 연동, 위조·만료·replay/변조·타조직 차단, 성공에도 항상 REVIEW_HOLD | **부분**: 정식 signed producer + 법적/신분 승인·approved AX package 생성 미구현, 고객 권리 false |
| 05 | PDF 페이지·DOCX 문단·TXT/MD 행 | 실제 합성 2페이지 PDF 및 한국어 DOCX 문단 검증, TXT line 해시 검증 | **검증-합성**: 복잡 문서·OCR·XLSX는 별도 |
| 06 | 문서 2건 이상 동시 검색·인용·전용 범위 | P85 real PDF+DOCX 단일 /assess 종단·documentIds 사전 ACL, native13PASS | **검증-합성**: 고객 문서·코퍼스 검증 필요 |
| 07 | 원본 RAG BM25 검색/IndexBuilder | **신규:** 별도 P85 실 BM25 + 한국어 n-gram 검색을 읽기 전 ACL·SHA 검증을 통과한 인용 구간에만 적용, 단위 6PASS | **부분**: 정확 원본 RAG pin BM25 소스 결속 CI 36PASS(합성) 확인; 고객용 대규모 인덱스·승인된 전체 RAG 종단 미검증 |
| 08 | 원본 RAG fixed readonly SQLite SQL/typed KPI | P85 별도 `node:sqlite :memory:` 5컬럼 고정 집계, tamper 검증/HOLD | **부분**: 원본 RAG SQL/실 매출 VAT·환불 의미 승인 없음 |
| 09 | SQL+문서 혼합 라우터·출처 두 가지 | `p85-journey.mjs` 단일 HTTP에서 PDF/DOCX/TXT 인용·SQLite 매출 잠정 수치와 `signed_review` Ed25519 결과를 결합, 서명 불일치 시 숫자·인용 제거 | **검증-합성**: 실사용 승인 자료 조회·원본 RAG 종단 미검증 |
| 10 | 정형 숫자 세금·환불·취소·SKU·기간 의미 통제 | 미지원 범위 `REVIEW_HOLD` 회피·비생성 검증 | **부분**: 고객 데이터 의미 확정·확장 쿼리 미구현 |
| 11 | 풀코퍼스 정책 상충·거절/insufficient | 특정 7/14일 반품 상충 `POSSIBLE_CONFLICT`, 무권한 문서 차단 | **부분**: 전체 도메인/한국어 정책 Gold 불충분 |
| 12 | 권한 있는 문서만 읽고 인덱싱 (tenant/group/project/classification) | vault는 ACL before byte read, SHA/inode/mtime/symlink/hardlink, 타조직 sales path 결속, 개별 테스트 | **검증-합성**: 생산형 multi-tenant index/TLS/파일 race 보안 미검증 |
| 13 | 실제 사용자·그룹·프로젝트·컬렉션 인증 | **신규:** 운영자 로컬 계정 발급, scrypt derived 저장, SQLite 재기동·다른 프로세스 로그인, scoped permission, admin만 발급·상속 권한 한도 | **부분**: 실제 고객 IdP/현장 관리자 승인·MFA/계정 초대 미검증 |
| 14 | 권한 변경·세션 철회·감사 | **신규:** `provisionUser/changeUserAccess` + SQLite transaction/audit, 기존 세션 권한 즉시 반영, 교차 프로세스 revoke | **검증-합성**: 생산 운영 복구·장기간 계정 정책 필요 |
| 15 | 문서 버전 교체·폐기·재색인 | `p85-state-store.mjs` durable revision/retire/reindex, SHA·gen·audit 테스트 | **검증-합성**: shadow index 원자 swap·백업/검색 동시성 추가 |
| 16 | 오프라인 사용자 UI/KPI/차트/출처 탐색 | **실기능 추가:** 기본 화면 로그인→질문→근거 우선, 범위·SQL·관리자 관리 `details`로 접고 모든 기존 API·ACL 유지. Real Chrome (desktop/mobile 390px) 기본/고급 패널 접힘·로그인/검색/후속/로그아웃 성공; `tests/p85-simple-ui` 4PASS×2OS. 사용자 이전 PC에서 로그인/근거 검색/1문서 KPI 시각 확인 | **검증-합성/부분-현장:** 새 간소 UI의 고객 PC 실재현·전문 UX 인수, 고객 실기업 IdP/실데이터/금융·법무 인수 미검증 |
| 17 | 한국어 실제 로컬 모델·선택 dense | **신규 사전단계:** MIT 기반 `multilingual-e5-small` 후보/118MB ONNX SHA 확인 및 offline model hash/local path/metadata 선검증, Win/Linux 각각 7PASS. 기존 미설치 fallback `SEARCH_ONLY` 유지 | **부분-준비:** 실제 weights·tokenizer 다운로드, local ONNX inference, dense index/품질·heldout·OS 라이선스/상업적 배포는 미검증, 모델 구동 완료 판정 금지 |
| 18 | 프롬프트 인젝션·ZIP·악성 파일·권한/데이터 유출 | bytes budgets, source SHA/inode/symlink, fail-closed, no network, XSS-safe UI textContent | **부분**: 문서 파서 OS 샌드박스/TOCTOU/침투 테스트·공식 보안점검 미완 |
| 19 | Windows10/11 오프라인 설치·백업/복구·라이선스 | Windows2022 hosted portable ZIP CRC/SHA·unpacked Node 실행 2PASS + offline backup 12PASS/OS. **사용자 실제 Windows PC에서 별도 QA 스크립트 PASS 및 synthetic 브라우저 로그인/검색 화면 관찰(이전 정본 SHA)** | **부분:** 고객용 정식 설치기/Node 라이선스·구체 Win10/11 버전 확인·새 간소UI 현장 재검증·실고객 데이터/백업복구·운영 인수 미완; 사용자 스크린샷은 영업 릴리스 승인 증거 아님 |
| 20 | Win/Linux GitHub-hosted CI 0FAIL | 정확 기능 SHA `f4f5f088` [#43537747863](https://github.com/hibi89/Freelancer/actions/runs/43537747863) **8/8 SUCCESS, 469 test executions PASS/0 FAIL/0 SKIP**; Ubuntu actual Chrome+Windows ZIP/native+온디바이스 ONNX preflight | **검증-합성:** hosted regression verified, Korean 실제 inference/enterprise customer authentication/Win10/11 commercial delivery excluded |
| 21 | 고객 Gold100 + negative/heldout, retrieval/latency/메모리 수용 | 신규 한국어 합성100건(20×5 유형) Windows/Linux 모두 PASS, p95 Ubuntu0.328ms/Win1.001ms | **부분**: 합성 반복 계약 테스트이며 고객의 Gold100·진짜 heldout·모델 성능/고객 합격 기준 미검증 |
| 22 | 백업/복구·삭제/보존기간·운영 정책 | Node22 SQLite backup API, 합성 문서 SHA manifest, create-only offline restore; **신규 SQLite 4개 테이블·실 active doc source SHA 바인딩**, 양 OS 각12PASS(기존9+신규3), 원본 불변·변조·링크·중복·덮어쓰기 거부 | **부분**: 실 고객 운용 중 무중단 백업/보존·삭제·물리 Windows10/11 복구/권한·개인정보 미검증 |
| 23 | 고객/법적·가격·지원·운영 인수 | 합성 SOURCE_RIGHTS=false/RELEASE HOLD 강제 | **대기**: 고객/소유자 승인·라이선스·실기기·지원 수용 불가 |
| 24 | 5개 RAG 유형/대시보드/후속 질문 | **신규:** `ScopedConversation` (5분·64스레드·세션해시/출처 SHA 결속·후속 질문 근거 재검사/로그아웃 삭제), `POST /v1/conversation/ask`, UI 후속 클릭 actual Chrome, 합성12PASS/OS. 기존 단일/다중/SQL+문서/컬렉션 합성 기능 유지 | **부분**: 5종 합성 기능 일부 실제 수행, real Korean model·authorized 고객 RAG 원본/IdP/권리/장기 대화 테스트 미검증 |

## 85% 목표 필수 차단 항목

- 원본 `hibi89/RAG_STUDIO@c5867b3951f51bfa97cadd1aad8fb13e9cf9e604` pinned upstream35PASS 및 CITEVAULT synthetic bridge36PASS로 이전 3 SKIP은 hosted에서 해소. **실 고객 권리 승인된 전체 기업용 SQL/BM25/PDF/DOCX/SMAX 종단은 미검증**.
- 실제 고객형 IDP/신뢰 주체·직원·그룹·문서 권리의 고객/운영자 승인, signed PREP/SMAX→AX authoritative import 미구현. 로컬 합성 운영자 기능은 대체 증거가 될 수 없다.
- 실제 한국어 로컬 모델(아티팩트 SHA/라이선스/질문 세트) 없음, Win/Linux Hosted CI/실 Windows 설치/Gold 수용 미확인.
- 전체 요구의 소유자 확정 가중치 없음. 24행에서 PASS 수를 나눠 최종완성률을 임의로 추정하지 않는다.

**다음 우선순위:** (1) 정확 original RAG pin/Actions 로그 또는 검증 가능한 원본 패키지 확보 → 3SKIP 해소, (2) 고객 IdP/데이터 사용권·서명 producer 승인 조건 확정(민감 권한·자료 외부송신은 사전 승인), (3) licensed 실제 Korean model 미니 품질/보안 검수, (4) Win/Linux CI 실제 결과와 물리 Windows 환경 테스트, (5) 원본 최종설계 전체 REQ-by-REQ signed 검수 및 소유자 승인 가중치.

**공식 상태: UNASSESSED / 사용자 목표 85% 미달성·미검증 / [작업중] / RELEASE HOLD / SALE NO-GO.**
