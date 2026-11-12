# ONTOINSIGHT AX — AI Excel·CSV 데이터 인텔리전스
**2026-11-13 KST · 내부 상품명(상표 조사 전) · 설계 전용 · RELEASE HOLD**

> 해총에 기록된 「AI 엑셀·CSV 매출·고객 데이터 분석 서비스」를 독립 상품화한 브랜치. **AI AutoML Analyst** 기반 로컬 분석 엔진에 **NVIDIA Auto Ontology의 의미/관계/출처 검증 개념**을 참고하고, 고객이 승인한 표준화·컬럼 의미/업무지표 정의·통계·ML 평가·설명 가능한 실행 결과를 결합한다. Auto Ontology 원본 코드를 실제로 이식했다고 주장하지 않는다.

**목표 납품물:** 승인된 고객 Excel/CSV 파일 → 열/금액/날짜/고객 ID 의미 매핑 → 정제·품질 리포트 → KPI/통계/차트 → 적합한 경우에만 누수방지 ML 예측 → 원본 연결 근거·오류/보류 표시 → 재실행 가능한 HTML/PDF/Excel/JSON/ZIP 인수 패키지.

- 실제 코드 원본: [hibi89/AI_AutoML_Analyst](https://github.com/hibi89/AI_AutoML_Analyst) / 개발 기능 브랜치 `feature/kmong-p6e50-owner-delivery-20261112`.
- 선택적 사내 기술: `SMAX²/PREP`(검증된 데이터 매핑/정규화 계약)·`DBVORA`(향후 고객 DB 자산 관제). 공개 분석 서비스에서는 **비공개 소스 무단 복제 금지**.
- 제3자 연구 기준: [NVIDIA/auto-ontology](https://github.com/NVIDIA/auto-ontology), Apache-2.0; '온톨로지/비즈니스 의미 계약'을 참조하며 회사의 NVIDIA 공식 파트너·인증 상품이 아님.
- 문서: [최종설계](docs/FINAL_BLUEPRINT.md), [전체 기술](docs/TECHNOLOGY_MAP.md), [품질·ML 검수 시나리오](docs/DATA_CONTRACT_AND_TESTS.md), [50→100](docs/ACCEPTANCE_AND_ROADMAP.md), [크몽·권리/가격](docs/COMMERCIAL_AND_SECURITY.md).
- 모든 가격·성능·정확성/고객 매출 증가의 효과는 실측 전 가설. 확정 계약/판매 전 고객·Windows/라이선스·정산·출고 검증 필요.
