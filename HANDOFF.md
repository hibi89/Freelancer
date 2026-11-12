# HANDOFF — Freelancer 5상품 크몽 설계 허브 (10항, 2026-11-13 KST)
1. **목표·용도·확정기술:** Private Freelancer 문서 저장소에서 기존 3종 AZENTFLOW AX(HAE+LA)/CITEVAULT AX(RAG+SMAX)/SITECRAFT AX(REA+Fable-Astra)와 신규 **PROOFQA AX**(CodeChecker+Graphify+agent-browser+Cloudflare 보안 검증 방법), **ONTOINSIGHT AX**(AutoML+NVIDIA Auto Ontology 개념+데이터/KPI/ML) 5개 독립 최종상품 기준을 유지.
2. **완료/변경/결정 근거:** 기존 3 branch의 상세 기술 설계는 보존하되 내부 상품명·브랜드 소개·문서 표제만 갱신. 신규 product 브랜치 2개 생성, 각 FINAL_BLUEPRINT/기술/30 또는 36 테스트/50→100/상품·보안 문서 작성. PROOFQA는 구조·동작·근거 교차검증, ONTOINSIGHT는 경량 ontology-lite/수치 검증·누수방지 선택. 전체 NVIDIA Stack/자동 고객 소스 실행은 초기에 배제.
3. **테스트/성공·실패:** 새 GitHub branch 두 HEAD·Git Trees 각각12 blob·문서 원격 재읽기 확인 PASS. 실제 제품 기능/CI·Windows/고객 보안·판매 0회 NOT_RUN. 기존 CodeChecker/AutoML 역사 CI는 신규 상품 검증과 구분.
4. **상태:** 두 신규 패키지 **기획 완료, 기능 통합 미착수/완성률 UNASSESSED/RELEASE HOLD**, 기존 3개 제품도 상용출시 HOLD. 등록/판매가·고객 인수 전 기술 라이선스·증빙 별도 검증.
5. **오류·원인·시도·재시도 금지:** 신규 브랜치 큰 통합 서비스는 정적 탐지만으로 웹·보안 결론을 확정할 수 없고, 매출 의미·join·target leakage 위험. 외부 Graphify/skill의 패키지/버전·비밀정보 전송 옵션과 NVIDIA NIM 비용은 검토/사전 승인. 무한 CI/force push·무단 원본 수정 금지.
6. **저장소/브랜치/정확 SHA:** `hibi89/Freelancer` Private, `main` 기존 `b80423da5...`, 새 `product/proofqa-ax-delivery-audit@54b718f5d5520fae912d1fcc2e70a87ebd8f173c`, `product/ontoinsight-ax-data-analytics@afda6eac0802d50cbcd44eb0b99d3daeffbf0922`, 기존 세 상품의 최신 브랜드 갱신 SHA는 `docs/PRODUCT_INDEX.md`에 기재.
7. **Production/프로젝트/환경:** 이 저장소는 실행 불필요한 기획 Repo; Vercel Production 미적용. 실제 Python3.11+ CodeChecker·AutoML 소스/브라우저/OSS 종속성은 각각 원본 repo에서 검증 후 제품화.
8. **원본/백업/인증 관리/금지:** 구직 원본 SHA `d47239f...` Git history 복구 가능, 기존 3 브랜치/코드 및 해총 기존16종 완성률 불변. 고객 코드/PII/키/업무자료/원본 DB는 GitHub·외부 모델로 무단 송신 금지.
9. **다음 우선순위·절차/승인:** 신규 상품 각 `HANDOFF→STATUS→AGENTS→REQUIREMENTS→FINAL_BLUEPRINT→원본 CodeChecker/AutoML source·tests`→실행 가능 범위 설계 재확인→사용자 제품 개발 승인→최소 adapter/semantic contract 구현→CI/OS/실고객/라이선스→크몽 판매 승인. 해총 `[작업중]`는 기능 착수 시 사용자 규칙에 따라.
10. **갱신 KST·확인 범위·커밋 기준:** 2026-11-13 KST, GitHub READ/CREATE/UPDATE/검증. 이번 문서 최신 hub SHA는 수정 후 GitHub main 원격 ref 확인값 사용, 제품 코드 TEST/Production 미실행.

### 2026-11-13 브랜드 갱신 후속 기록
- AZENTFLOW AX `product/hae-la-automation@a578aee2300ae053bafe5cdaf1dd8e23385ff47b`
- CITEVAULT AX `product/rag-enterprise-knowledge@acf4936670bf1205f648d0dff5ca7e48b62fa83a`
- SITECRAFT AX `product/rea-website-rebuild@6e2346c3b9d50dea1bde8d5ecb47b47f1567f774`
- 각 브랜치 `docs/BRAND_POSITIONING.md` 추가. 명칭만 수정; 이 작업에서 제품 기능 코드/CI/Production 변경 및 상표·도메인 조사 없음. 기존 PROOFQA AX/ONTOINSIGHT AX SHA·문서 변경 없음.
