# CITEVAULT AX — HANDOFF — RAG Studio 기업형 (10항, 2026-11-13 KST)


## [2026-11-13 KST] P50 통합 QA 코드 신규 작업 — 10항 인수인계 (최신)

1. **목표/기술/범위:** CITEVAULT AX 최종설계 전체 100% 중 사용자 요청 50% 개발 목표. Node22 순수 로컬, 별도 RAG 원본 체크아웃의 고정 SQL·BM25·인용·SMAX 리뷰 게이트를 기업상품 브랜치에서 통합 확인. 내부 P50 gate와 공식 점수 분리.
2. **완료/변경/선택 근거:** 제품 브랜치 신규 `enterprise/p50-gate.mjs`, `tests/p50.test.mjs`, `.github/workflows/citevault-p50.yml`, `docs/P50_EVIDENCE_MATRIX.md`, STATUS 갱신. 기존 RAG 엔진 복사·전면 재작성 대신 pinned 원본 read-only 참조(비용 0/회귀 위험 낮음). RAG/SMAX/PREP 기존 코드/원본 데이터 변경 0.
3. **테스트/성공 실패/미검증:** 테스트 **6개 작성**, 로컬 실행 **NOT_RUN**, GitHub Actions push run log **미확인** (확인 가능한 PASS 0/FAIL 0, 실행이 0건이라는 주장 아님). 코드 검토 및 기존 RAG 원본 module/fixture blob 조회 완료; 그 조회는 새 모듈 실행 증거가 아님. 실행명령 `RAG_STUDIO_ROOT=/absolute/path/to/pinned/RAG_STUDIO node --test tests/p50.test.mjs`.
4. **완료/진행/대기/차단:** 코드+테스트+Actions 정의 GitHub 반영 완료. P50 6-test 실제 통과 미확인, PDF/DOCX 소스 실행 gate·SMAX→인가 AX 전환 미구현 또는 미검증. 사용자 확정 가중치/전체 REQ 추적 미완. **공식 최종완성률 UNASSESSED, 목표 50% 미달성/검증 대기, [작업중] 유지, RELEASE HOLD**.
5. **오류/원인/시도/재시도 금지/대안:** 컨테이너 `git ls-remote`는 `github.com` DNS 해석 실패, 원본 git checkout 불가하여 GitHub 커넥터로 파일/커밋 확인·쓰기 수행. GitHub connector `fetch_commit_workflow_runs`는 PR 트리거만 조회하므로 push 작업 결과 없음으로 성공/실패 판단 불가. 기존 P50 실제 CI 실패 근거는 아직 없음. 우회 토큰/수동 가짜 PASS/중복 재배포 금지; 다음 수단은 GitHub Actions job/run 로그 혹은 허가된 로컬 2-repo checkout.
6. **저장소/브랜치/SHA/복구:** `hibi89/Freelancer@product/rag-enterprise-knowledge`, 작업 전 `1195f767c7ebc6b1965936cc2166db53853c6e53`; 신규 코드 `72a300fbb7901c3459c3411b1b2ebc2527fc0e8c`, 테스트 `111de7b65c76a78be826c8e30ae3c41a6f7637cd`, workflow `087b567c5e0d7615531b49c9e5cb413ea2218839`, 매트릭스 `5c6aa7882f13a03990469745a1dd84e6dc73354d`, STATUS `63806b8a11b40aa0179b65a7c620ac0e976a03e5`; 최신 HEAD는 HANDOFF commit 이후 원격 재조회. 외부 RAG pin `c5867b3951f51bfa97cadd1aad8fb13e9cf9e604`.
7. **실행환경/배포:** Node 22.16.0, 정확 pinned GitHub Actions Ubuntu 24.04 test command, 추가 API/유료 모델 의존 없음. 실제 Production/Vercel 배포 **미적용**, 고객형 설치·인증 기능 미구현. 워크플로는 read-only 두 checkout으로 정의.
8. **원본/백업/보안:** Git 이력 작업 전 SHA가 복구지점. RAG_STUDIO 공개 fixture만 사용, private PREP/SMAX 소스 및 고객정보 업로드/복제 없음. 개발용 RAG localhost Bearer를 기업 IAM으로 혼동하지 않음. 원문·토큰·권한/계정/결제/배포 수정 금지.
9. **다음 작업 순서/완료 조건/승인:** GitHub Actions push run 실제 로그/Node assertion 확인 → 실패시 정확 원인 1회 개선 → 실제 PDF/DOCX 인용 gate → SMAX producer→인증된 reviewer 승인 서명·revocation + 승인된 AX export (보안/권한 영향 변경 전 사용자 승인) → 정확 SHA 전체 수용·가중치 검토 → 그때만 50% 평가. `[작업중]`은 기준 충족 전 유지.
10. **최신화 시점/근거 범위:** 2026-11-13 KST, GitHub repository/branch/원본 code·fixture/커밋과 P50 gate source 반영 확인. CI pass, real producer, Windows/Chrome, 사용자 고객형 E2E, 보안 전문 감사, 판매 승인 **미확인**. 중앙 해총 후보 목록 동기화/원격 readback은 본 HANDOFF와 별도 수행.

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
