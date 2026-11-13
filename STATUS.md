# CITEVAULT AX — STATUS — RAG Studio Enterprise, 2026-11-13 KST

## [2026-11-13 KST] CITEVAULT AX 85% 재추진 — SQLite 영속 상태·철회·감사 원자화

- **공식 목표:** 최종설계 100% 대비 85%. **현재 공식 완성률 UNASSESSED / 85% 미달성·검증 대기**, `[작업중]` 유지, `RELEASE HOLD/SALE NO-GO`.
- **실제 구현:** 신규 `enterprise/p85-state-store.mjs` Node22 내장 SQLite (실험적): 합성 계정/문서 메타데이터를 최초에만 시드하고 재시작 때 재사용, 외부 주입 시드 재등록 거부, 문서 버전/폐기·로그·접근 철회 보존. 원본 `p85-vault.mjs`에 선택적 `stateStore`, 권한검사 후 파일 로딩, cross-process 계정 disable·폐기 반영, stale revision 거부. `p85-loopback.mjs`에 관리자 revoke API 추가. version/reindex/retire/revoke 상태 변경 및 감사 기록은 한 SQLite 트랜잭션. 원본 RAG/PREP/SMAX는 불변.
- **실제 검증:** Linux Node v22.16.0 `node --test tests/p85-vault.test.mjs tests/p85-loopback.test.mjs tests/p85-state-store.test.mjs` **58 PASS/0 FAIL/0 SKIP**, 독립 ZIP 압축해제 후 재실행도 **58 PASS**. P50/P70/P85 Node 전수 로컬 결합 **95 total/92 PASS/0 FAIL/3 SKIP** (3개 RAG 원본 checkout 필요). 신규·수정 코드/테스트 Git blob 6개 `git hash-object` 정확 일치. 근거: `docs/P85_DURABLE_EVIDENCE_20261113.md`.
- **CI/Windows:** `.github/workflows/citevault-p50.yml`에 기존 Ubuntu24.04/Windows2022 P85 매트릭스의 SQLite 영속성 14케이스 추가. 실제 GitHub Actions hosted job/run 및 Windows 실행 결과 **미확인**, GitHub Classic commit status 0개만으로 성공/실패 판단하지 않음.
- **중요 미완:** 진짜 기업 사용자 IdP/영속 운영계정·테넌트별 안전한 index/물리 RAG 데이터계약, 실 승인된 PREP/SMAX→AX, PDF/DOCX 원문 페이지/문단 통합, 한국어 로컬 모델/권리 실험, 실제 고객 Windows/Gold·백업 복구. 합성 로컬 메타데이터는 상용 IAM 인증이 아니며 85% 공식 인정 불가.



## [2026-11-13 KST] CITEVAULT AX P85 사용자 목표 — 조직분리·로그인·문서 수명주기 로컬 검증

- **공식 목표/판정:** 사용자 확정 최종설계도 전체 대비 **85%**. 실제 최종완성률은 **UNASSESSED**, 85% **미달성/검증 대기**, 해총 **[작업중]** 유지, **RELEASE HOLD / SALE NO-GO**.
- **신규 실제 구현:** `enterprise/p85-vault.mjs`: 오프라인 합성 계정 scrypt 로그인·시크릿 없는 난수 Bearer 세션, 15분 만료/로그아웃/잠금, 조직·그룹·프로젝트·등급 ACL 검증 **후**에만 고정 파일 원문 열람, SHA256·링크·경로·사이즈 변조 차단, 조직별 감사 이력, 버전 전환/폐기/관리자 재색인. `enterprise/p85-loopback.mjs`: `127.0.0.1`로만 바인딩되는 합성 HTTP QA, 401/403/404, `no-store`, JSON/4096 bytes 입력 제한. 실제 고객 IAM/Production 서버 아님.
- **실행/검증:** GitHub blob SHA와 Linux Node22.16 로컬 파일 4개가 `git hash-object`로 정확 일치 (vault `378523e03e4d42fe899e702504f8c37b6c23454e`, vault test `5e455611732c067bbcbcd7c5b8ea005e775e3dea`, HTTP `dee33df73c1f677713c11c89156f07fd4de40dfd`, HTTP tests `80a30bccb792a8a37104ec5376c55ce1dce4a4f3`). `node --test tests/p85-vault.test.mjs tests/p85-loopback.test.mjs` **42 PASS/0 FAIL/0 SKIP**, 기존 P50/P70 Node 검증 포함 총 **79 중 76 PASS/0 FAIL/3 SKIP**. 3 SKIP은 실제 원본 RAG Studio checkout에 필요한 통합.
- **보안 결함 처리:** 1차 개발 이후 관리자 감사 조회의 조직 간 이벤트 메타정보 노출 가능성을 확인→tenant별 audit 저장/조회 필터 추가 후 27/27 vault PASS. HTTP text/plain JSON 및 4096 bytes 초과 본문 차단 추가 후 15/15 PASS.
- **CI:** `.github/workflows/citevault-p50.yml`에 `p85-loopback-contracts` Ubuntu24.04/Node22.16 + Windows2022/Node22.23 매트릭스 추가. **Hosted run/job 로그 및 Windows PASS는 확인 불가**. 이전 원본 RAG P512/P538/P540/P549도 CI 정의만 확인.
- **미구현/미검증:** 영속 IAM/계정 데이터 저장, 조직별 실제 데이터/인덱스/세션, 실제 고객 허가된 PDF/DOCX·SMAX Native→서명 승인 AX, 한국어 실제 모델/라이선스, 실 Windows 인수/Gold·백업 복구, 사용자 최종설계 가중치 100% 재산정. `docs/P85_EVIDENCE_MATRIX.md` 필수 추적.
- **보존:** 원본 RAG/PREP/SMAX/고객정보·계정 권한·Vercel/Production/과금 변경 없음. CI 통과를 추정하지 않고 `[작업중]` 유지.


## [2026-11-13 KST] 사용자 70% 목표 2차 구현 — Node 34PASS/0FAIL/3SKIP, 최종완성률 미확정

- **실제 개발:** 원본 RAG 통합 브리지의 근거 없는 `FOUND` 허용 결함 확인·수정. `enterprise/p70-citation-contract.mjs` 엄격 출처 검증을 `enterprise/p70-rag-bridge.mjs`에 실제 연결. `enterprise/p70-local-review.mjs`는 실제 로컬 CSV bytes/원본 SHA-256/5열 역할 매핑/BigInt 금액 일치/보존 확인, SMAX/PREP `REVIEW_HOLD`만 출력. `row_lineage_verified:false` 등 권리·인가 과대주장 금지.
- **정확 검증 범위:** Linux Node **v22.16.0**, 원격 GitHub 코드와 로컬 4개 신규 source/test Git blob SHA 일치: 인용 계약 **14 PASS/0 FAIL**, CSV/매핑 review-only **17 PASS/0 FAIL** → **31 PASS/0 FAIL/0 SKIP**. 기존 P50 standalone 3 PASS/3 SKIP와 동시 명령 실행 기준 **37 total / 34 PASS / 0 FAIL / 3 SKIP**. SKIP 3은 실제 pinned RAG checkout 불가로 SQL/BM25/SMAX 통합 미수행. P70 original-source BM25/충돌/근거 계약 **순수 V8 in-memory 5 PASS**, 로컬 자료/Node native RAG 대신 증명하지 않음. `docs/P70_EVIDENCE_MATRIX.md`의 정확 blob과 실행 근거.
- **CI:** GitHub Actions `.github/workflows/citevault-p50.yml`의 독립 `local-contracts` job으로 31 Node 테스트 구성, `synthetic-evidence`는 원본 RAG pin과 P512/P538/P540/P549 연결. 실제 GitHub Actions run ID/job status **미검증**.
- **남은 목표:** P50 실 원본 RAG package import 통합 3개 SKIP 해결, PDF/DOCX 2+ 실제 source CI/Windows, PREP/SMAX 실제 인증 승인→AX 전환, 기업 서버 Identity 및 ACL-before-load, 사용자 승인 최종설계 100% 가중치 전수 평가. 순수 synthetic 도구를 실 IAM/법적 승인으로 간주 금지.
- **판정:** 공식 최종완성률 **UNASSESSED**, 70% 사용자 목표 **미달성·검증 대기**, `[작업중]` 유지, `RELEASE HOLD / SALE NO-GO`, Production 배포 미적용. 이번 변경은 기존 원본/고객자료/자격증명/기타 상품 무변경.


## [2026-11-13 KST] 사용자 CITEVAULT AX P70 개발 목표 — 오프라인 검색정책 구현, 최종 70% 미검증

- **목표:** 사용자 최종설계 전체 대비 70%(기존 P50 선행 미검증 포함). 현재 **공식 최종완성률 UNASSESSED, 목표 70% 검증 미달**, `[작업중]` 및 `RELEASE HOLD/SALE NO-GO` 유지.
- **이번 구현:** `enterprise/p70-policy.mjs` (synthetic-only 테넌트/부서/프로젝트/등급/유효기간 제약, 무권한 문서 제외, 전체 허가 문서 상충 보류, 로컬 모델 없는 `SEARCH_ONLY`, SMAX `REVIEW_HOLD` 강제) + `enterprise/p70-rag-bridge.mjs` (허가된 synthetic 문서 ID만 원본 RAG `knowledgeSearch` 대상으로 전달, 반환 출처 재검사). PDF 페이지 번호를 테스트용 줄 번호로 잘못 표시하지 않도록 수정.
- **테스트:** `tests/p70.test.mjs` 24개 신규 순수 JS 테스트, **GitHub 정본 JS를 V8에서 동작시켜 24 PASS / 0 FAIL**. Node/Hosted CI가 아닌 별도 테스트 환경. `tests/p70-rag-integration.test.mjs` 6개 원본 연결 테스트 작성, 실제 Node 실행 **미검증**. 기존 P50 테스트는 이전 턴 Node22 단독 **3 PASS / 0 FAIL / 3 SKIP** (3개 RAG 통합 미실행).
- **원본 회귀 CI 설정:** `.github/workflows/citevault-p50.yml`에 기존 RAG 정확 pin `c5867b3951f51bfa97cadd1aad8fb13e9cf9e604`와 P512 PDF/DOCX, P538 전체 상충, P540 다중 native, P549 PREP/SMAX mapping 리뷰, 신규 P70 Node 테스트 추가. **실제 CI run ID/성공 확인 없음**. 구현 근거 및 70 요구 전수 표 `docs/P70_EVIDENCE_MATRIX.md`.
- **핵심 한계:** `SYNTHETIC_ONLY` principal은 실제 IAM이 아니고, 원본 RAG `loadPackage()`는 문서 권한 필터 전 패키지 전체를 로딩하므로 **기업 ACL-before-load 미구현**. 실기업 권한/고객 파일·진짜 승인된 PREP/SMAX→AX 전환, 모델/Windows/라이선스 미검증. 비공개 원본/토큰/고객자료·계정/배포 변경 없음.
- **결론:** 개발 소스 반영은 검증됨. 독립 검수 없는 70% 수치 책정 불가, **[작업중] 유지**. 해총 중앙 후보표/인수인계 최신화 필요.



## [2026-11-13 KST] CITEVAULT AX P50 사용자 목표 — 통합 QA 소스 반영, 50% 미검증

- **작업 목표:** 최종설계 전체 기준 50%. 현재 공식 완성률 **UNASSESSED**, 목표 **미달성/검증 대기**. 목표 달성 전 해총 후보 목록에서 `[작업중]` 유지.
- **제품 브랜치:** `hibi89/Freelancer@product/rag-enterprise-knowledge`. 신규 소스 `enterprise/p50-gate.mjs`, 테스트 `tests/p50.test.mjs`, workflow `.github/workflows/citevault-p50.yml`, 추적 `docs/P50_EVIDENCE_MATRIX.md`. 원본 RAG/PREP/SMAX 수정 없음.
- **실 엔진 정확 참조:** `hibi89/RAG_STUDIO@feature/p550-mapped-cited-journey` pinned `c5867b3951f51bfa97cadd1aad8fb13e9cf9e604` (read-only 외부 checkout). RAG `develop`와 과거 CI SHA `0e88301059c9...`는 diverged, 상용 엔터프라이즈 P50로 점수 승계 금지.
- **구현:** 실 RAG 모듈 동적 로드, 승인된 합성 AX SHA/SQL KRW 157,000 오라클/TXT 출처/BM25 검사, 승인 전 SMAX `REVIEW_REQUIRED` 차단, 합성 파일 스냅샷 전후 digest, symlink/위변조/잘못된 집계 부정 테스트.
- **로컬 정확 소스 테스트(2026-11-13 KST):** GitHub 새 소스 2개 `git hash-object`가 원격 blob SHA와 각각 일치(`5e9080f00fcda6c92ad575e88bc6be35024f7600` / `a26c758cfe9a1a79d5b83f459236a27160712a93`). Node v22.16.0 `node --check` 2/2 통과, `node --test tests/p50.test.mjs` **6개 중 3 PASS, 0 FAIL, 3 SKIP**. SKIP은 pinned RAG checkout 필수 통합 테스트여서 **통합 PASS 아님**.
- **CI·PDF/DOCX:** `.github/workflows/citevault-p50.yml` commit `54cd494e47c27a3dd89846d9d02aeda0c955f8f4`에 기존 RAG 원본 `tests/p512-native-document.test.mjs`(PDF 페이지/DOCX 문단 실제 파싱) 실행 추가. 실제 GitHub Actions run/job 로그와 성공 여부 **미확인**. PREP/SMAX Native→인가 AX 실전환, 기업 IAM/ACL/실 Windows/실고객/라이선스도 미검증. P50 매트릭스 참조.
- **계약/출시:** 고객/기밀 원문, 외부 API 호출, 오토 승인, Production/Vercel 배포/상품 게시 없음. `RELEASE HOLD / SALE NO-GO`. 다음은 정확 CI 실행 증거 후 누락 P50 수용조건 구현.

> **상품명: CITEVAULT AX** · 근거형 기업 AI 지식·데이터 검색. 원래 제품명·저장소는 유지.
- 이 브랜치에는 기업 맞춤형 고가 상품 **최종설계·세부 기술·고객 인수/출고·판매/보안 문서**만 추가. 원본 RAG/SMAX/PREP 코드·배포 0건 수정, 이번 제품 테스트 0회.
- `hibi89/RAG_STUDIO@develop` 조회 HEAD `e63e539ab8ded5834cb85672aa2142eb660d3f23`. Private SMAX/PREP 별도 보존.
- 기존 해총 RAG 일반 제품 **95% 잠정**(2026-11-12 CI SHA `0e88301059c9...` 기록), **기업 다중 사용자 제품** 신규 수용 기준은 미검증/재산정 필요.
- 차단: 실제 고객 자료 권리 승인, PREP/SMAX Native 실 운영 연동, 기업 인증/부서 ACL, 실제 로컬 LLM 라이선스/성능, 고객 Windows 설치 및 데이터 라이프사이클.
- RELEASE HOLD / 상용 승인 없음 / Vercel Production N/A(초기 로컬 우선).
