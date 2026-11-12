# HANDOFF — 크몽 3대 상품 설계 저장소 (10항)
1. **목표/확정 기술:** Private `hibi89/Freelancer`를 HAE+Lightning Azent+DBVORA, RAG Studio+SMAX²/PREP, REA_WEB+Fable5.1/Astra P4 3개 기업형 상품 설계 허브로 전환.
2. **완료/근거:** 기존 Upwork/구직 문서를 현재 트리에서 없애고 3개 `product/*` 브랜치 생성, 상세 BLUEPRINT/TECHNOLOGY/ACCEPTANCE/COMMERCIAL 및 README/REQUIREMENTS/STATUS/HANDOFF 작성. 독립 제품 코드 무수정.
3. **테스트:** GitHub Tree/파일/author SHA 읽기 검증 PASS(3 branch, 각각10파일; legacy 0). 실제 소프트웨어 테스트 0회·CI 0회·고객/브라우저 실서비스 0회.
4. **진행/대기/차단:** 설계 문서 완료, 실제 판매/고객 설치/보안·권리 승인 미검증, `RELEASE HOLD`.
5. **오류/시도/대안:** slash가 포함된 branch를 Git Trees URL ref로 직접 넘긴 첫 재조회는 400. **commit SHA로 Git Tree 조회하여 개선·재검증 성공**. 반복 금지. 강제 이력 정리는 고객 자료/복구권 위험이 있어 미실시.
6. **저장소/브랜치/SHA:** `hibi89/Freelancer` Private / `main` 이전 `d47239f`→새 정리 커밋 `2f0528b`; `product/hae-la-automation@58f810ec`, `product/rag-enterprise-knowledge@8da3e43`, `product/rea-website-rebuild@ba3ee24`. 세부: `docs/PRODUCT_INDEX.md`.
7. **Production/실행:** 이 저장소는 문서 전용이므로 Vercel/배포/실행 명령 없음. 코드 실행은 각 원본 프로젝트 HAE/RAG_STUDIO/REA_Web에서 별도 수행.
8. **원본/백업/권한:** 이전 소스 트리 Git commit `d47239f...` 복구 가능(강제 push 없음). HAE·LA·DBVORA/SMAX/PREP/RAG/Fable/Astra/REA 소스·시크릿·고객자료·Vercel 계정/결제 불변. `docs/REPOSITORY_RECOVERY.md` 확인.
9. **다음 작업/완료 기준/승인:** 사용자가 각 상품 개발을 명시 지시할 때 해당 product branch의 HANDOFF→STATUS→AGENTS→REQUIREMENTS→BLUEPRINT→실제 원본 repo 최신 순으로 읽고 현재 소스·테스트·CI 비교 후 승인 범위 내 구현/검증. 가격·상용권·사용자 자료/실계정·고객 납품은 별도 승인.
10. **갱신/기준:** 2026-11-13 KST. 문서 GitHub 원격 Tree 및 BLUEPRINT 직접 재조회, Author/Committer hibi89 확인. 허브 최종 HEAD는 이번 인수인계 문서 갱신 직후 재조회값 사용.
