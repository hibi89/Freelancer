# Freelancer — 크몽 3대 기업형 상품 총괄
**기준: 2026-11-13 KST · 저장소 Private · 문서 전용 · RELEASE HOLD**

기존 Upwork/프리랜서 구직 보좌관 자료를 현재 트리에서 전면 제거하고, **3개 고객 납품 상품의 독립 최종설계 본부**로 전환한다. 본 저장소는 통합 배포 소스가 아니다. 실제 개발 기준 코드는 아래 원본 제품 저장소에 둔다.

| 제품 전용 브랜치 | 상품 | 원본 개발 코드 | 표준형 가설 |
|---|---|---|---:|
| `product/hae-la-automation` | HAE + Lightning Azent 기업 업무 자동화 | `hibi89/HAE`, `hibi89/DBVORA` | 1,990,000원 |
| `product/rag-enterprise-knowledge` | RAG Studio + SMAX²/PREP 사내 지식·데이터 AI | `hibi89/RAG_STUDIO`, `hibi89/SMAX`, `hibi89/prep` | 2,990,000원 |
| `product/rea-website-rebuild` | REA_WEB + Fable 5.1 + Astra P4 웹사이트 분석·재구축 | `hibi89/REA_Web` | 1,890,000원 |

각 브랜치의 `docs/FINAL_BLUEPRINT.md`가 **최종상품 100%의 정본**이다. `docs/TECHNOLOGY_MAP.md`, `docs/ACCEPTANCE_AND_ROADMAP.md`, `docs/COMMERCIAL_AND_SECURITY.md`가 세부 기술·단계별 수용·견적/보안을 정의한다. `STATUS.md`, `HANDOFF.md`는 확인된 상태와 다음 작업만 기록한다.

**작업 경계:** 본 저장소는 기획·계약·상품 설계 전용. 원본 제품 코드 복제, 자동 병합, 외부 API 사용, 고객 데이터 반입, 유료 결제, 출시·배포는 하지 않는다. 기존 상용화 전 `RELEASE HOLD`를 유지한다. 과거 기록의 파일 삭제가 Git 이력 영구삭제를 의미하지 않으며 복구 방법은 [docs/REPOSITORY_RECOVERY.md](docs/REPOSITORY_RECOVERY.md)에 있다.
