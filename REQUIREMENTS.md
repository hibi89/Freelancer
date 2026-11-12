# REQUIREMENTS — Freelancer 5대 상품의 최종설계 기준
1. 총 **5개** 제품 전용 브랜치: AZENTFLOW AX(HAE+LA), CITEVAULT AX(RAG+SMAX/PREP), SITECRAFT AX(REA+Fable/Astra), PROOFQA AX, ONTOINSIGHT AX. 각 브랜치에 FINAL_BLUEPRINT/TECHNOLOGY_MAP/ACCEPTANCE_AND_ROADMAP/COMMERCIAL_AND_SECURITY와 STATUS/HANDOFF 저장.
2. 공통: 개발 기능과 계획을 분리, 전체 100% 기준·50/70/85/95 단계, 고객 자료 권리/라이선스/개인정보/실 Windows 설치·검수, 원본 불변·장애/재시도/재현/데이터 정합성, 구독·API비 별도 표시.
3. HAE: HAE 정책/승인 + LA 결정적 실행 + SQLite 분리 + DBVORA 자산/복구 + 선택 SOVIA; Google OAuth 고객형 미검증.
4. RAG: RAG Studio 문서·SQL 근거 + PREP/SMAX 데이터 정형화 + 기업 권한/생성 답변 보류, 로컬 모델 선택형.
5. REA: 고객 허가 사이트 Fable/Playwright 관찰→Astra 증거→고객 승인→Pro 독립 웹앱 생성→브라우저 비교; DATA2WEB와 별도.
6. **PROOFQA AX**: AI Code Checker 정적 검사 + Graphify code/SQL graph + agent-browser 실 사이트 E2E + Cloudflare security-audit-skill의 독립 검증 방법론. 코드를 무단 실행하지 않고 확인/미검증/기각 결론에 정확 증거 연결.
7. **ONTOINSIGHT AX**: AI AutoML Analyst + NVIDIA Auto Ontology **개념 참고**의 의미·관계/KPI 계약 + Excel/CSV 안전 ingest+SMAX/PREP 선택형, leakage-safe AutoML + 수치 재검증·근거형 보고서.
8. 상품명 PROOFQA/ONTOINSIGHT는 상표 검토 전 내부명. 제3자 GitHub OSS는 정확한 버전/라이선스/NOTICE/상용 배포 조건 검토 전 내장·판매 금지. 외부 기업 제휴/보안 인증 주장 금지.
9. 해총 기존 16종 진척과 신규 결합 상품 진척률은 독립. 신규 2개는 현재 `UNASSESSED`, 코딩/통합 미착수, `RELEASE HOLD`.

10. 기존 세 기업형 판매 상품의 내부 브랜드는 `AZENTFLOW AX`, `CITEVAULT AX`, `SITECRAFT AX`이며, 고객 약속 기능과 기술이 보존되는 이름표다. 원본 HAE/RAG/REA 저장소/기술명 및 구 브랜치명을 강제 변경하지 않는다. `docs/BRAND_POSITIONING.md`와 각 branch `FINAL_BLUEPRINT.md`에서 명칭 확인.
