# Freelancer — 크몽 3대 기업형 상품 총괄
**2026-11-13 KST · Private · 기획/검증 문서 전용 · RELEASE HOLD**

기존 Freelancer Upwork/구직 자료는 현행 Git 트리에서 제거하고, 크몽 3개 독립 상품의 **최종설계 기준 저장소**로 전환했다. **소스코드 구현은 각각의 기존 제품 저장소**에서 수행한다.

| 상품별 브랜치 | 기술 조합 | 100% 기준 문서 | 표준형 가설 |
|---|---|---|---:|
| [product/hae-la-automation](https://github.com/hibi89/Freelancer/tree/product/hae-la-automation) | HAE+Lightning Azent+DBVORA+선택 SOVIA | [HAE 최종설계](https://github.com/hibi89/Freelancer/blob/product/hae-la-automation/docs/FINAL_BLUEPRINT.md) | **199만원** |
| [product/rag-enterprise-knowledge](https://github.com/hibi89/Freelancer/tree/product/rag-enterprise-knowledge) | RAG Studio+SMAX²+PREP+SQLite/검색+선택 로컬LLM | [RAG 최종설계](https://github.com/hibi89/Freelancer/blob/product/rag-enterprise-knowledge/docs/FINAL_BLUEPRINT.md) | **299만원** |
| [product/rea-website-rebuild](https://github.com/hibi89/Freelancer/tree/product/rea-website-rebuild) | REA_WEB+Fable5.1+Astra P4+Playwright+REA Pro | [REA 최종설계](https://github.com/hibi89/Freelancer/blob/product/rea-website-rebuild/docs/FINAL_BLUEPRINT.md) | **189만원** |

[3개 상품·검증된 커밋 색인](docs/PRODUCT_INDEX.md) · [이전 구직 파일 복구](docs/REPOSITORY_RECOVERY.md)

각 브랜치의 `docs/FINAL_BLUEPRINT.md`는 **최종상품 100% 완성의 설계 기준**이다. `docs/TECHNOLOGY_MAP.md`, `docs/ACCEPTANCE_AND_ROADMAP.md`, `docs/COMMERCIAL_AND_SECURITY.md`, `REQUIREMENTS.md`, `STATUS.md`, `HANDOFF.md`를 함께 읽는다.

**주의:** 이 저장소는 상용 서비스나 제품 실행기가 아니며 현재 판매/Production `RELEASE HOLD`. 모든 가격은 검증 전 견적 가설, 제품 구현·실 고객 권리·보안·계약/과세형태는 원본 별도 검증 대상이다. 예전 구직 파일은 현재 트리에서 지웠지만 Git 이력은 비강제 이관으로 보존한다.
