# Freelancer — 크몽 브랜드 5종 최종설계 허브
**2026-11-13 KST · Private · 설계/검증 문서 전용 · RELEASE HOLD**

과거 업워크·구직 운영 문서는 현행 트리에서 제외되고 Git 이력으로 복구 가능하다. 이 저장소에는 **각 상품 최종완성률 100%의 정본 설계**를 `product/*`의 **독립 5개 브랜치**로 보관한다. **실제 제품 코드는 원래의 GitHub 저장소에서만 수정·검증·출시한다.**

| 상품 | 전용 브랜치 | 기술 조합 | 표준형 견적 가설 |
|---|---|---|---:|
| **AZENTFLOW AX** — HAE 기업 자동화 | [product/hae-la-automation](https://github.com/hibi89/Freelancer/tree/product/hae-la-automation) | HAE + Lightning Azent + DBVORA + 선택 SOVIA | 199만원 |
| **CITEVAULT AX** — RAG 기업 AI 검색 | [product/rag-enterprise-knowledge](https://github.com/hibi89/Freelancer/tree/product/rag-enterprise-knowledge) | RAG Studio + SMAX²/PREP + SQL/BM25 + 선택 로컬 LLM | 299만원 |
| **SITECRAFT AX** — REA_WEB 웹사이트 재구축 | [product/rea-website-rebuild](https://github.com/hibi89/Freelancer/tree/product/rea-website-rebuild) | REA_WEB + Fable5.1 + Astra P4 + Playwright + REA Pro | 189만원 |
| **PROOFQA AX** 개발품 납품 검수 | [product/proofqa-ax-delivery-audit](https://github.com/hibi89/Freelancer/tree/product/proofqa-ax-delivery-audit) | AI Code Checker + Graphify + agent-browser + Cloudflare 보안 감사 방법론 | **39만원** |
| **ONTOINSIGHT AX** Excel/CSV 인텔리전스 | [product/ontoinsight-ax-data-analytics](https://github.com/hibi89/Freelancer/tree/product/ontoinsight-ax-data-analytics) | AI AutoML Analyst + NVIDIA Auto Ontology 개념 + 선택 SMAX²/PREP | **34.9만원** |

[상품별 정확 SHA·문서/검증 범위 통합 색인](docs/PRODUCT_INDEX.md) · [과거 구직 자료 복구](docs/REPOSITORY_RECOVERY.md)

각 브랜치는 `docs/FINAL_BLUEPRINT.md`에 상세 시스템 구조·100% 고객 사용자 동선·모듈/데이터 계약·보안/원본/장애 처리·최종 인수 기준을 기록한다. `docs/TECHNOLOGY_MAP.md`는 전체 기술, `docs/ACCEPTANCE_AND_ROADMAP.md`는 **50→70→85→95→100** 단계, `docs/COMMERCIAL_AND_SECURITY.md`는 판매·라이선스·견적/고객 정보 보호를 정의한다. 각 상품은 별도 `README/REQUIREMENTS/STATUS/HANDOFF`가 있다.

**사실 경계:** PROOFQA AX·ONTOINSIGHT AX는 2026-11-13 기준 **신규 조합의 통합 구현·고객 검수·판매는 미착수**. 기존 Code Checker/AutoML의 역사적 엔지니어링 진행률을 신규 상품에 합산하지 않는다. 가격/브랜드/경쟁성능은 검증 전 가설이며 판매·배포는 HOLD.
