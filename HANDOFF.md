# CITEVAULT AX — HANDOFF — RAG Studio 기업형 (10항, 2026-11-13 KST)

## [2026-11-13 KST] CITEVAULT AX P70 후속 작업 — 10항 최신 인수인계

1. **목표·용도·확정 설계/기술:** 기업용 로컬 RAG, PREP/SMAX 데이터 검토·승인, 문서/SQL 근거, 사용자별 권한 및 모델 fallback. 이번 명시 목표 **최종설계 전체 대비 70%**, 이전 P50 검증 조건 포함. 사용자 승인 100점 가중치 부재로 공식 **UNASSESSED**, 70% 달성 미확정.
2. **완료·변경·결정근거:** 기존 RAG 재작성 대신 기존 `RAG_STUDIO` pinned source와 CITEVAULT synthetic-only policy를 분리. 신규 `enterprise/p70-policy.mjs`/ `enterprise/p70-rag-bridge.mjs`, `tests/p70.test.mjs` 24개, `tests/p70-rag-integration.test.mjs` 6개, CI P512/P538/P540/P549 연계 설정, `docs/P70_EVIDENCE_MATRIX.md`. 원본 RAG/PREP/SMAX 변경 0. 다른 외부 연결/유료 API 0.
3. **테스트·명령·결과:** 코드 원격 GitHub 원문과 동일한 순수 JS `enterprise/p70-policy.mjs`+`tests/p70.test.mjs`를 V8 eval 기반으로 실제 실행해 **24 PASS/0 FAIL**(최종 policy blob `de75419d049b488ea4475a560f86fb99250d7d19`, test blob `b3f741963a1f5314d2fbaf8e504c9ff7b5ae60c9`). Node22 host `node --test tests/p50.test.mjs tests/p70.test.mjs tests/p70-rag-integration.test.mjs` 및 원본 RAG `tests/p512...`, `p538...`, `p540...`, `p549...` **실행 미확인**. 과거 P50 Node standalone 3PASS/0FAIL/3SKIP는 별개.
4. **단계·중단 지점:** P70 정책/오류거부/검색 출처 래퍼는 개발 완료. 실제 RAG 연결·기업 identity server·ACL storage-before-load·인가된 PREP/SMAX→AX 단일 end-to-end 및 다중 native 문서 Hosted 검증은 미완/미검증. **공식 UNASSESSED / 70 목표 미달성/검증 대기 / [작업중] 유지 / RELEASE HOLD**.
5. **오류·근거·시도·재시도 금지:** container GitHub DNS 미해결(로컬 git clone 불가). GitHub connector로 원본 source/commit 확인, V8 순수 계약 검증 및 Actions workflow 코드 구성으로 전환. Hosted push run ID는 GitHub connector의 PR-only run 검색으론 확인되지 않음. **CI 실패라고 추정하지 않음**, 같은 확인법 반복 금지. 원본 native tests를 성공으로 가정하지 않는다.
6. **저장소·브랜치·SHA·경로:** `hibi89/Freelancer@product/rag-enterprise-knowledge`; 시작 P70 HEAD `6c36d02e71a751c8473b0bb36c9dc8b2c5ed460c`, 원본 RAG `hibi89/RAG_STUDIO@c5867b3951f51bfa97cadd1aad8fb13e9cf9e604`. 신규 policy/test blob 위, CI 설정 `64b85e992877a453732ee88aceec78c83f5695ff`, P70 문서 `0a7adfbe57e31cba6b9507e92c2cbff60d348300`; 본 HANDOFF 이후 정확 HEAD 재조회.
7. **실행/환경/Production:** Node 22.16+ 원본 node:sqlite 및 pdfjs/mammoth 의존, GitHub Ubuntu Actions read-only pinned checkout. 로컬 dummy principal only, 신뢰 ID 제공자 없음. 외부 서비스/LLM 과금 0, Vercel·Production 배포 미적용.
8. **원본/백업/권리/금지:** P70 작업 직전 제품 SHA `6c36d02e71a751c8473b0bb36c9dc8b2c5ed460c`를 Git 복구 기준으로 보존. Private SMAX/PREP, Public RAG 원본, 고객데이터, 키/권한/도메인/배포 불변. `SYNTHETIC_ONLY`는 권한 없는 사용자를 인증한 증거가 아니며 실제 직원 서비스 노출 금지.
9. **다음 우선순위·절차·승인:** P50/P70 original pinned RAG GitHub Actions 실 run 검증→실 PDF/DOCX 다중 검색과 상충/SMAX signed approval end-to-end→사용자 승인 후 실제 직원 서버 인증·역할 정책, 승인 철회, 기업별 저장/색인 분리→실 Windows/골드/성능→가중치 승인·최종완성률 재계산. 계정 권한/실고객자료/원본 보안 변경은 사전 승인.
10. **갱신 일시·확인 시점·검증 범위:** 2026-11-13 KST; GitHub 정본 file/blob/CI yaml 조회, V8 순수 JS 24/24 PASS. Node full, GitHub hosted CI, Win10/11, 고객 실환경, 실제 인증·SMAX 서명, Production/상품 등록 및 최종 70 점수 **미검증**. 중앙 해총 인수인계 동기화 확인 필요.



## [2026-11-13 KST] P50 통합 QA 코드 신규 작업 — 10항 인수인계 (최신)

1. **목표/기술/범위:** CITEVAULT AX 최종설계 전체 100% 중 사용자 요청 50% 개발 목표. Node22 순수 로컬, 별도 RAG 원본 체크아웃의 고정 SQL·BM25·인용·SMAX 리뷰 게이트를 기업상품 브랜치에서 통합 확인. 내부 P50 gate와 공식 점수 분리.
2. **완료/변경/선택 근거:** 제품 브랜치 신규 `enterprise/p50-gate.mjs`, `tests/p50.test.mjs`, `.github/workflows/citevault-p50.yml`, `docs/P50_EVIDENCE_MATRIX.md`, STATUS 갱신. 기존 RAG 엔진 복사·전면 재작성 대신 pinned 원본 read-only 참조(비용 0/회귀 위험 낮음). RAG/SMAX/PREP 기존 코드/원본 데이터 변경 0.
3. **테스트/성공 실패/미검증:** 실제 Linux Node v22.16.0 동일 원격 코드 blob(소스 `5e9080f00f...`, 테스트 `a26c758cfe9a...`; `git hash-object` exact MATCH)에서 `node --check` 2/2 PASS, `node --test tests/p50.test.mjs` **6 total / 3 PASS / 0 FAIL / 3 SKIP**. SKIP 3개는 RAG 원본 pinned checkout 통합에 해당하며, 실제 SQL/BM25/SMAX 연결 **미실행**. GitHub Actions push run/job log 및 원본 PDF/DOCX source test **미확인**. 실행명령 `RAG_STUDIO_ROOT=/absolute/path/to/pinned/RAG_STUDIO node --test tests/p50.test.mjs`.
4. **완료/진행/대기/차단:** 코드+테스트+Actions 정의 GitHub 반영 완료. Workflow `54cd494e47c27a3dd89846d9d02aeda0c955f8f4`에서 **기존 RAG 원본** `tests/p512-native-document.test.mjs`(PDF 페이지/DOCX 문단)도 실행하도록 보강했으나 CI PASS 미확인. 6-test 중 RAG 연결 3개 SKIP, SMAX→인가 AX 전환 미구현 또는 미검증. 사용자 확정 가중치/전체 REQ 추적 미완. **공식 최종완성률 UNASSESSED, 목표 50% 미달성/검증 대기, [작업중] 유지, RELEASE HOLD**.
5. **오류/원인/시도/재시도 금지/대안:** 컨테이너 `git ls-remote`는 `github.com` DNS 해석 실패, 원본 git checkout 불가하여 GitHub 커넥터로 파일/커밋 확인·쓰기 수행. GitHub connector `fetch_commit_workflow_runs`는 PR 트리거만 조회하므로 push 작업 결과 없음으로 성공/실패 판단 불가. 기존 P50 실제 CI 실패 근거는 아직 없음. 우회 토큰/수동 가짜 PASS/중복 재배포 금지; 다음 수단은 GitHub Actions job/run 로그 혹은 허가된 로컬 2-repo checkout.
6. **저장소/브랜치/SHA/복구:** `hibi89/Freelancer@product/rag-enterprise-knowledge`, 작업 전 `1195f767c7ebc6b1965936cc2166db53853c6e53`; 신규 코드 `72a300fbb7901c3459c3411b1b2ebc2527fc0e8c`, 테스트 `111de7b65c76a78be826c8e30ae3c41a6f7637cd`, workflow `087b567c5e0d7615531b49c9e5cb413ea2218839`, 매트릭스 `5c6aa7882f13a03990469745a1dd84e6dc73354d`, STATUS `63806b8a11b40aa0179b65a7c620ac0e976a03e5`; 최신 HEAD는 HANDOFF commit 이후 원격 재조회. 외부 RAG pin `c5867b3951f51bfa97cadd1aad8fb13e9cf9e604`.
7. **실행환경/배포:** Node 22.16.0 local standalone unit 3 PASS / 0 FAIL / 3 SKIP, 정확 pinned GitHub Actions Ubuntu 24.04 test command (PDF/DOCX npm ci deps), 유료 API/LLM 의존 없음. 실제 Production/Vercel 배포 **미적용**, 고객형 설치·인증 기능 미구현. 워크플로는 read-only 두 checkout으로 정의.
8. **원본/백업/보안:** Git 이력 작업 전 SHA가 복구지점. RAG_STUDIO 공개 fixture만 사용, private PREP/SMAX 소스 및 고객정보 업로드/복제 없음. 개발용 RAG localhost Bearer를 기업 IAM으로 혼동하지 않음. 원문·토큰·권한/계정/결제/배포 수정 금지.
9. **다음 작업 순서/완료 조건/승인:** GitHub Actions push run 실제 로그/Node assertion 확인 → 실패시 정확 원인 1회 개선 → 실제 PDF/DOCX 인용 gate → SMAX producer→인증된 reviewer 승인 서명·revocation + 승인된 AX export (보안/권한 영향 변경 전 사용자 승인) → 정확 SHA 전체 수용·가중치 검토 → 그때만 50% 평가. `[작업중]`은 기준 충족 전 유지.
10. **최신화 시점/근거 범위:** 2026-11-13 KST, GitHub repository/branch/원본 code·fixture/커밋과 P50 gate source 반영 확인 + **exact Git blob 대비 로컬 3 PASS/0 FAIL/3 SKIP**. Hosted CI pass, full RAG producer, Windows/Chrome, 사용자 고객형 E2E, 보안 전문 감사, 판매 승인 **미확인**. 중앙 해총 후보 목록 동기화/원격 readback은 본 HANDOFF와 별도 수행.

> **상품명: CITEVAULT AX** · 근거형 기업 AI 지식·데이터 검색. 원래 제품명·저장소는 유지.
1. 목표: Private PREP/SMAX²→승인된 AX패키지→RAG Studio BM25/dense/SQL+문서→근거 검증→선택형 로컬 모델+기업 ACL.
2. 완료: 상세 FINAL_BLUEPRINT, TECHNOLOGY_MAP, ACCEPTANCE_AND_ROADMAP, COMMERCIAL_AND_SECURITY 문서 작성. 원본 저장소 기능 변경 없음.
3. 테스트: 이번 브랜치 제품 테스트 NOT_RUN; 기존 해총 역사적 CI #43231121679(Linux 633PASS 2SKIP; Windows 634PASS 1SKIP) 별도 기록. 정확 develop/feature 포함 관계 미검증.
4. 상태: 설계 전용; 기업 사용권/계정/실물 Windows·로컬 모델/상용 출고 미검증, RELEASE HOLD.
5. 오류/장애: 개발용 localhost 인증을 기업 IAM으로 혼동하면 안 됨, unapproved `REVIEW_HOLD` 패키지 자동 승인 금지, 모델 없는 fallback 필요.
6. 원본: `hibi89/RAG_STUDIO@develop e63e539`, `hibi89/SMAX` Private, `hibi89/prep` Private, 상품문서 `hibi89/Freelancer@product/rag-enterprise-knowledge`.
7. 실행: Node 22 계열; 기존 RAG 원본 `npm test`, synthetic demo/Windows doc picker. Production/Vercel N/A. 외부 업로드 기본 불허.
8. 보존/권한: 고객 문서·키/모델 권리/Private SMAX 코드 외부 복제 금지, 원본 소스 모두 그대로. 승인 후 별도 기업 수용 파일 사용.
9. 다음: 최신 RAG 정확 CI source→develop diff, PREP/SMAX 계약→기업 권한/문서 수명주기→모델 벤치→실 PC/고객형 인수→최종 승인.
10. 시점/검증: 2026-11-13 KST GitHub ref/기존 문서 읽기. 실제 고객 실증/판매/소프트웨어 테스트 이 브랜치에서 미수행; 최종 commit SHA는 이후 readback.
