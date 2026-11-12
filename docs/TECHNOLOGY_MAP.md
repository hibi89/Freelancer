# ONTOINSIGHT AX 기술 맵 — 우리 엔진 + Trending 개념

| 계층 | 확정/검토 기술 | 책임 | 검증 상태 |
|---|---|---|---|
| 기반 분석 엔진 | `hibi89/AI_AutoML_Analyst`, Python3.11+, FastAPI, Uvicorn | 기존 folder scan/schema group/CSV 선택/AutoML/report | 개발·CI 이력 존재 |
| DataFrame | pandas/numpy, Python decimal | dtype/정제/통계/수치/KPI | 기존 일부, 새 수식검증 필요 |
| Model | scikit-learn Pipeline/CV, Dummy, 분류·회귀 | 예측 실험 비교 | 기존 코어, 새 누수/시간 split gate 추가 |
| UI | HTML/CSS/JS, 기존 FastAPI 앱 | 업로드/매핑 승인/결과/다운로드 | 기존 기본 프론트, 승인 화면 추가 |
| Excel | openpyxl 또는 검증된 parser, XLSX | 시트/날짜/통화/셀/외부 링크 안전 intake | 기존 분석은 CSV 한정, **신규 개발** |
| Business ontology | NVIDIA Auto Ontology **개념 참고** | 엔터티/속성/관계·KPI 공식/라인리지·사용자 확정 | 연구 단계, 원본 NVIDIA 도구 미통합 |
| Optional mapping | SMAX²/PREP Private native | 컬럼 매핑·정형화/고객 확인 계약 | 교차 실 고객 통합 미검증 |
| Optional DB audit | DBVORA | 스키마·재고·백업/기업 DB 정보 | 초기 상품 제외 |
| Data store | SQLite 또는 로컬 parquet/CSV cache | run/metric/manifest metadata | 정식 저장/삭제 설계 필요 |
| Display | matplotlib/plotly 검증된 도표 + HTML | KPI/차트/상관·코호트 | 기존 별도 제품과 호환 검증 |
| Reporting | Markdown/HTML/PDF/openpyxl XLSX/ZIP + SHA256 | 한국어 문서·재분석·수치감사 | 기존 일부 보고서/ZIP, 신규 정형화 |
| Model registry | JSON metadata: config/seed/split/metrics | 재현성·작업취소·모델 버전 | 고객형 신규 |
| CI | pytest, Python Windows/Linux, Chrome/Edge optional | 정형데이터·ML/repro/report 회귀 | 정확 신규 CI 미개발 |
| Security | file allowlist/size/time/PII mask, consent ledger | 원본·고객정보·외부 전송 제한 | 고객형 신규 |

### 외부 NVIDIA Auto Ontology 범위
- 공식 GitHub: https://github.com/NVIDIA/auto-ontology · 라이선스 Apache-2.0, 추가 제3자 NOTICE. 원본 전체 스택은 PostgreSQL/pgvector, Next.js, FastAPI, NVIDIA NIM 등 선택 모델·자원 요구. **우리 제품은 온톨로지 기반 데이터 의미/관계/근거 검증 아이디어**를 채택하고 로컬 pandas/sklearn로 독립 구현을 우선한다.
- 상업 라이선스 문서는 라이브러리/모델/연동 서비스별로 다르게 적용. 본 이름이 NVIDIA 상표/로고 사용권을 의미하지 않는다.
- 온톨로지가 없는 고객 데이터에 없는 관계를 확정하지 않는다. 모델이 뜻을 추정하더라도 사용자 승인/유효성 검사가 필요하다.

### 선택 아키텍처 비교
- 가벼운 로컬 DataFrame+분류/회귀+BISemantic JSON → 소규모 파일 분석에 적합, 운영비 낮음.
- PostgreSQL + pgvector + NIM/Graph DB → 수십~수백 테이블, 기업 사용자·고성능 추론 요구 시만 별도 견적, API/GPU/DB 운영비 증가.
- 단순 Excel 대시보드 → 빠르고 가격 낮지만 누수·join·비즈니스 의미·AI 분석 여부를 엄밀히 분리하지 못함.

### 현재 원본 CI 한계
- 해총 기록의 AI AutoML Analyst `feature/kmong-p6e50-owner-delivery-20261112` 기능 SHA `458cf43816d3...`에서 Ubuntu 320PASS/3SKIP·Windows 322PASS/1SKIP·3SKU 합성 브라우저 전달 PASS. **새 ONTOINSIGHT AX의 Excel/관계/온톨로지·ML 누수게이트 검증이 아님.**
- 기존 README의 정확한 한계: 한 번에 CSV 1개, schema group 자동 병합 미지원, XLSX/JSON 기본 미지원, 예측 leakage 위험; 이 빈틈을 새 상품 설계의 최초 핵심 과제로 설정한다.
