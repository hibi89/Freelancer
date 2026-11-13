# CITEVAULT AX — STATUS — RAG Studio Enterprise, 2026-11-13 KST

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
