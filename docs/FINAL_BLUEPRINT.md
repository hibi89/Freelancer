# ONTOINSIGHT AX — BUSINESS DATA INTELLIGENCE / FINAL BLUEPRINT v1.0
**2026-11-13 KST · 최종 상품 100% 기준 · 설계 문서이며 실제 AI AutoML+온톨로지 통합 구현/수익화 완료가 아님**

## 0. 왜 만드는가
- 목표 고객: 매출/주문/환불/재고 Excel·CSV가 누적됐지만 정확한 정제·품질 분석·사업 설명과 의사결정 자료를 만들기 어려운 개인사업자·온라인 판매자·작은 영업팀.
- 현재 문제: Excel 파일별 날짜·금액 형식과 고객 ID가 다르고 '매출'이 순매출/총매출/결제금액으로 혼용된다. CSV를 AutoML에 바로 넣으면 열 의미를 오판하고 target leakage로 과대평가할 수 있다.
- 우리가 판매하는 것은 'AI가 엑셀을 읽어 돈을 벌어 준다'가 아닌 **원본 보존→데이터 정의/수식 검증→시각화/통계→적합하면 ML 평가→근거 설명→고객 재현 가능한 납품**.
- 산출물: Data Dictionary/semantic map, 품질·행 증감 보고서, KPI 공식과 수치 감사표, 정규화 파생 데이터, HTML/Excel/PDF 경영리포트, 선택형 ML 모델 평가, 개선 가설/한계, 결정적 검증 manifest.
- 검증 구분: `OBSERVED`(파일·실측), `DERIVED`(수식/관계), `HYPOTHESIS`(검증 필요), `NOT_ENOUGH_DATA`, `REVIEW_HOLD`. 모델 수치와 매출 성장 제안을 확정 사실로 묘사하지 않는다.

## 1. 원본 엔진·외부 연구 기술 계보
| 구성 | 원본·범위 | 제품화 조합 |
|---|---|---|
| AI AutoML Analyst | `hibi89/AI_AutoML_Analyst`; `feature/kmong-p6e50-owner-delivery-20261112` 조회 HEAD `d56b1b48fef372f0923b5f9543b9c0e4a738a412` | Python/pandas/sklearn/FastAPI 분석·평가/보고, 기존 구현 보존 |
| NVIDIA Auto Ontology | https://github.com/NVIDIA/auto-ontology · Apache-2.0 | *개념/설계 참고*: 의미 메타데이터→entity/relationship→검증 가능한 지표 계약→출처/SQL 맥락; **라이브러리 자체 통합 미실시** |
| PREP / SMAX² | `hibi89/prep`, `hibi89/SMAX` (Private) | 확장형 매핑/정규화 검토. native 원본·고객자료의 외부 repo 전송 금지 |
| DBVORA | `hibi89/DBVORA` (Private) | 기업형 DB 자산/스키마·백업 관제 옵션(현재 Standard 납품 포함 아님) |
| Python analytics | pandas/numpy/scikit-learn/matplotlib, 필요 시 openpyxl | source-bound numeric analysis, plots, validated workbook |
| Output | 기존 FastAPI/HTML/Markdown + HTML→PDF + Excel/ZIP | 장표·보고서·source lineage·독립 verify 단계 |
- 기존 AI AutoML Analyzer의 제품 P95 개발 기록은 **일부 기존 코드 범위**. 이번 '데이터 의미/온톨로지/다중 소스/기업용 보고'가 완성됐다고 승계하지 않는다.
- NVIDIA 구현 스택은 실제 설치 시 PostgreSQL/pgvector/NIM/Next.js 등 복합 의존성이 있으나, 우리는 **경량 로컬 의미 계층**을 우선 채택하며 NVIDIA 제품 전체를 복제/내장하지 않는다.

## 2. 아키텍처 설계 비교·최종 선택
| 대안 | 개발 속도·비용 | 정확도/성능 | 보안·유지보수 | 결론 |
|---|---|---|---|---|
| A. 고객 Excel을 그대로 외부 LLM에 업로드해 요약 | 빠르나 API 종량/개인정보 위험 | 금액·단위/관계 추론 오류 위험 | 모델/약관 의존, 재현성 부족 | 기본 배제 |
| B. 기존 AI AutoML 단일 CSV 분석만 제공 | 빠르고 테스트 활용 | KPI·업무 용어, 다중 파일 관계 설명 부족 | 간단한 BASIC엔 유리 | 제한형 |
| C. **로컬 입력 검증 → 경량 ontology/schema map → 고객 승인 → deterministic KPI/통계 → 선택 AutoML → 근거 보고** | 구현 중간·API 무상 운영 가능 | 의미 검증·수치 재현 가능, 모델 게이트 | 모듈별 재사용·감사 가능 | **채택** |
| D. NVIDIA Auto Ontology 전체 Stack+NIM/pgvector 구축 | 초기 설치·GPU/API/DB 비용 큼 | 대규모 관계 표현 강력 | 소기업 표준 판매에 과한 운영 부담 | 기업 커스텀 옵션만 |

## 3. 고객 100% 사용자 동선
1. 고객은 자신이 분석·가공·납품할 권리를 가진 CSV/XLSX와 목표를 제출(예: '재구매 고객 특징과 채널별 순매출/반품 추세'). 데이터 수집 목적/PII·계정 식별자 저장 범위·외부 AI 사용 여부를 서면 확인.
2. 로컬/고객 승인 저장 위치의 원본을 읽기 전용 취급하고, SHA256/크기/인코딩/시트/헤더/정확한 데이터 행수/열/통화·날짜 파싱 상태를 수집. 엑셀 수식·외부링크·매크로·Pandas formula injection에 안전 중단.
3. **Data profiler**가 데이터 종류(주문·고객·상품·광고·재고), 타입/결측/중복/열 cardinality·이상치·날짜 누락·환불/세금 여부를 표로 보여준다. 잘못된 형식을 고쳐 쓰기 전에 고객과 의미를 확정한다.
4. **Schema mapper/경량 Ontology layer**가 entity `Customer/Order/OrderLine/Product/Channel/Date/Refund` 후보를 만들고 key/foreign-key/aggregation grain/metric definitions `gross_sales/net_sales/refunds/AOV`와 관계 증거(컬럼·샘플 건수/중복/연결 불일치율)를 제시한다.
5. 원본에서 자동 추론한 관계는 모두 `INFERRED/REVIEW_HOLD`. 사용자가 주문번호·고객ID·비용 기준·부가세/환불 의미를 수정·승인하면 `approved_mapping_digest`를 발급한다. 승인 전 여러 CSV를 자동 JOIN하거나 예측하지 않는다.
6. 지원된 단일/복수 파일을 승인된 키·카디널리티로 로컬 정규화. 1:N 반복 JOIN에서 매출이 중복 합산되지 않도록 키 uniqueness·행 보존/증감·중복 건수·유실 행을 검증.
7. **KPI 계산기**는 순매출/주문수/고객수/객단가/환불율/판매채널별 기간 추세 등 고객이 승인한 산식만 실행. 소수점·금액/통화·쿠폰·세금·취소를 직접 검증. 원본 표와 derived/row counts를 교차 연결.
8. **탐색형 분석**: 매출 추세·상품별 분포, 세그먼트/코호트, 이상치/시즌성·상관관계, 원인 확인이 안 되면 '가능한 설명/추가 확인'으로 표기.
9. **AutoML gate**: 고객이 목표를 명시한 경우만 ML. 미래 결과 예측/분류가 합리적인지 label/누락/변수 누수·예측 시점에 이용 불가한 feature·표본수·클래스 불균형·시계열 순서를 검사한다. 부적합 시 예측 대신 통계·요약만 납품.
10. **모델 실험**: 고객/시간/주문군 leakage 방지 split, 훈련집합 내부 CV+preprocessing, dummy baseline, 적합한 간단 모델과 하이퍼파라미터 상한, heldout 최종 1회 평가. 결과는 accuracy 하나가 아니라 목적에 맞는 MAE/RMSE, ROC-AUC/PR-AUC/F1 및 불확실성을 함께 표시.
11. **설명/추천**: observed data fact ↔ KPI 수식 ↔ model performance ↔ business hypothesis 구분. 예: '채널 A 반품율이 높음'은 관찰, '상품설명 개선이 원인 해결'은 실험 전 가설. 추천은 우선순위와 검증 방법(A/B 또는 추가 로그)을 함께 제시.
12. **고객 보고서**: 한국어 1페이지 executive summary, 데이터 품질/제외행/한계, KPI 표·차트, 관계 맵, ML 실행/미실행 이유, 결과 수치 근거·시나리오별 제안, 정확한 source digest·환경·버전.
13. **납품**: 수정 불가능한 원본은 고객이 보관, 파생 CSV/XLSX·HTML/PDF·JSON/manifest·검증 스크립트·재실행/데이터 삭제/업데이트 가이드 포함. 고객 승인된 결과 범위만 내보내기.
14. **재분석**: 고객이 새 기간 자료를 주면 원본·매핑·수식 버전·train/holdout 시점을 확인, 스키마 drift 발생 시 `HOLD` 후 새 승인. 이전 결과와 비교하되 과거 모델 성능을 복사해 새로운 파일에서 그대로 주장하지 않는다.

## 4. 전체 시스템 아키텍처
```text
Authorized customer CSV/XLSX + data purpose + privacy/rights agreement
     │
     ▼
Intake & Source Integrity
  ├─ validated format/canonical column types, SHA, sheet/rows
  ├─ PII/secret check, formula/macro/links, max size/rows
  └─ local original READ ONLY / output to new folder
     │
     ▼
PREP/SMAX optional typed normalization adapter (no source copy)
  ├─ profiler: missing/duplicate/outlier/drift type
  └─ mapping candidates, key/cardinality validation
     │
     ▼
Ontology-lite Semantic Catalog (inspired by NVIDIA Auto Ontology)
  ├─ entity/attribute/relationship candidate & lineage
  ├─ business metric: definition+units+grain+time scope+SQL formula
  └─ confidence: observed/inferred/reviewed/approved
     │  customer approve (mapping+source SHA+scope+expiry)
     ▼
Deterministic Analyzer
  ├─ pandas/numpy exact numeric and reconciliation
  ├─ optional DuckDB/SQLite read-only local analytic query
  ├─ KPI engine and chart renderer
  └─ data-quality flag/row lineage source ids
     │
     ├── [No suitable target] → descriptive stats + no ML report
     │
     └── [Suitable approved target] → AutoML Analyst
           ├─ sklearn Pipeline+CV with time/group-aware split
           ├─ dummy baseline + bounded models
           ├─ leakage/imbalance/calibration checks
           └─ heldout metrics / limitations / reproducible seed
     │
     ▼
Report & Insight Engine
  ├─ observed / derived / hypothesis / needs-review separation
  ├─ HTML charts/KPI + PDF + Excel/CSV + source line/row refs
  ├─ package SHA+manifest+independent data reconciliation
  └─ customer review / delivery / purge / support
```

## 5. 엔터티/온톨로지 세부 계약
### 5.1 Data semantics catalog
- `source_registry`: 파일 ID/SHA, format, source timestamp, detection confidence, permission/retention/PII class, schema version.
- `entity_catalog`: `Customer, Order, OrderLine, Product, Channel, Refund, Period`; 모두 업무별 선택된 vocabulary, 실제 데이터 없으면 자동 확정 금지.
- `attribute`: column token, dtype, currency, timezone, nullable, source lineage and transform, `sensitivity`.
- `relationship`: candidate join key, parent cardinality (1:1/1:N/N:M), actual unmatched/duplicate rates, source row keys, exact mutation risk, `status=INFERRED|APPROVED|REJECTED`.
- `metric_contract`: ID, description, dimension/measure/grain, unit/rounding, net/gross, refunds, tax, date basis, business owner identity, `formula_version`.
- 모델 입력의 *금액*이 순매출인지 총매출인지 승인 안 되면 요약 문구에 경제적 해석 금지.

### 5.2 Ontology-lite JSON 스키마 예시 (가상)
```json
{
  "contract":"ontoinsight.semantic.v1",
  "source":{"source_id":"orders","sha256":"<sha256>","rows":1000,"format":"csv"},
  "entities":[{"id":"Order","grain":"order_id","key_columns":["order_id"],"status":"INFERRED"}],
  "relationships":[{"from":"Order","to":"Customer","keys":["customer_id"],"join":"many_to_one","unmatched_rate":0.0,"status":"REVIEW_HOLD"}],
  "metrics":[{"name":"net_sales","unit":"KRW","period_basis":"payment_date","definition":"approved_formula_v1","status":"PENDING"}],
  "approval":{"actor_id":null,"source_digest":"<sha256>","mapping_digest":"<sha256>","state":"PENDING"},
  "run":{"ml_status":"NOT_EVALUATED","report_state":"HOLD"}
}
```
- 본 JSON은 **미구현 신규 의미 계약의 목표형**. NVIDIA/auto-ontology의 실제 공식 API/스키마와 동일하다고 주장하지 않는다. 데이터/계약 버전 호환 테스트 필요.

### 5.3 원본 ↔ 파생 데이터 일치
- 합산 불변: customer approved aggregation grain에 따라 derived net/gross/refund equals independently recomputed source events. 중복키·조인 폭발·결측 금액은 성공으로 취급 금지.
- 컬럼 의미·날짜 범위가 다른 CSV 파일 병합 전 정규화 스키마/중복/시간대 변환; 변환 전후 행 차이 리포트와 승인/삭제 이유 기록.
- 금액형은 가능한 decimal/정확 integer minimal units 또는 검증된 rounding policy 사용; floating point 임의 round로 금액 리포트 생성 금지.
- CSV formula injection/Excel external link/매크로/VBA/숨은 시트/압축 폭탄·메타데이터 위험 확인. 원본 파일을 고객 요청 없이 overwrite하지 않음.

## 6. ML 정확성·검증 정책 (경영 의사결정 오해 방지)
- 모델의 목적: 고객이 승인한 검증 가능한 분류/회귀 예측만, 미래 매출·고객 이탈·반품 위험 등을 데이터 충분 시 평가.
- 입력 target missing/정확한 prediction horizon/feature availability at decision time/검증 기간/리벨링 품질을 먼저 확인.
- **Time split**: 날짜가 있는 미래 예측은 시간 순 검증, 날짜가 다른 판매 기간의 random split로 leakage 낙관 평가 금지.
- **Group split**: 동일 고객/매장/상품의 여러 행이 train과 test에 겹치면 현실 배포 단위에 맞게 GroupKFold/GroupShuffleSplit 등.
- 모든 preprocessing(표준화/결측·범주 인코딩/선택)은 훈련 fold **내부 fit**, 전체 데이터를 미리 보고 target 기반 선택하는 누수 차단.
- DummyRegressor / DummyClassifier 대비 실익 제시, 학습/평가 데이터 크기 및 class prevalence 명시. 모델이 못 이기면 '예측 성능 확인 안 됨'.
- 회귀 MAE/RMSE/R²·편향, 분류 Precision/Recall/F1/ROC-AUC 또는 PR-AUC와 confusion matrix, threshold/캘리브레이션, heldout confidence intervals(적절 시).
- Feature importance는 모델의 조건부 관계 설명이지 매출 원인 증명 아님. 인과관계 제안은 별도 실험 설계 후 가설.
- 개인정보/민감속성 대리 변수(PHI, 국가·법정 고유식별 등) 발견/사용 시 승인·법률·공정성 검토 없이 자동 학습 제외.

## 7. 분석 기능 모듈 설계
- `file_intake`: 선택 파일/시트/인코딩/크기/허용 경로, SHA, read-only, safe output.
- `profile_engine`: dtype, missing/duplicate/outliers/cardinality, row count, string/numeric anomalies, quality baseline report.
- `ontology_lite`: entity + attribute + relation + metric catalog, proposed mappings and approval ledger (owner signed).
- `prep_adapter`: optional SMAX²/PREP tested source-bound mapping contract; native source private and separate.
- `quality_gate`: no unsafe join or unresolved business meaning, no silent dropping; stop/review.
- `kpi_engine`: approved formula library deterministic aggregations, period/cohort/channel/SKU breakdown; independently audited sums.
- `automl_bridge`: existing AI AutoML Analyst runner on validated derived dataset with bounded resource/job cancel semantics.
- `ml_gate`: data sufficiency/target leakage/time/group split/heldout/retraining drift; STOP/HOLD when not suitable.
- `insight_writer`: human understandable source- and formula-linked observations; optional LLM uses only approved aggregate features, default offline/no cost.
- `reporter`: HTML dashboards, PDF/Excel, JSON manifests, SHA bound source lineage and re-run instructions.
- `delivery_verifier`: independent schema/metric/recomputed expected totals, no deleted original, ZIP extract clean + version pinned. 
- `ops`: retry/abort, job status/error classification, customer file TTL purge and safe backup restore.

## 8. 에러·재실행·API 비용/데이터 보관
- 지원되지 않는 XLSX 수식/매크로/암호화, 큰 파일/결측/유니코드/손상: 분류 `INPUT_BLOCKED`, `FORMAT_PARTIAL`, `REVIEW_REQUIRED`. 조용히 누락행을 성공으로 카운트하지 않음.
- 실패 후 재실행: 입력 `SHA + 승인 매핑 SHA + 공식 버전 + 모델 config + seed`를 하나의 run key로 기록, 동일 실험 재시도는 새 run attempt/인수 기록. 고객의 신규 입력이 이전 보고서를 덮어쓰지 않음.
- CPU/RAM/time/job 주기 한도, 모델 후보/데이터 규모 상한, 중단 요청의 실제 worker lifecycle 종료 여부 확인. 브라우저 Cancel만으로 서버 학습 취소 주장 금지.
- API 비용: offline pandas/sklearn 기본 외부 AI 호출 0, optional LLM/NIM/MCP/외부 데이터는 고객 explicit consent + token/month cap/전송 데이터 목록; 수익 가설이 비용을 정당화하지 못하면 사용하지 않음.
- 클라우드 서버/다중 사용자/대량 산업 데이터/라이브 DB는 별도 고객 계약/보안·성능 시험; 초기 Standard는 로컬 승인 파일로 한정.
- 보유기간·파기: 원본/정형화 사본·실험 데이터·임베딩/모델가중치·보고 ZIP·백업/로그 각각 분리해 고객 합의 기간 후 안전 삭제·증빙. 파일 경로·개인정보를 GitHub에 저장하지 않음.

## 9. 판매 납품 기준과 경쟁 개선 가설
- 다른 Excel 분석과 구별할 목표: **고객 용어 승인·JOIN 의미 검증→정확한 KPI 재현→ML 누수 방지/보류→출처별 경영 설명**.
- NVIDIA 모델/속도를 모사하는 게 아니라 경량 매핑 계약에 정확성/권리/변경증거를 결합한다. 공급사가 NVIDIA와 제휴/인증한 것처럼 홍보 금지.
- 고객이 "데이터 표/선형 차트"만 원하면 BASIC, "온톨로지/다중 파일 합계·고객 분석"은 STANDARD, "정당화되는 ML"은 PREMIUM을 제안. 업종별 지표는 고객 승인 없이 독자 확정 금지.
- 출시 최소: 고객 승인된 테스트 파일·경영 정의, 정확한 원본/파생 합계, 재생 가능한 분석 환경/모델 평가, Windows10/11 실행·파일 저장/삭제, 라이선스/NOTICE·작업시간/가격/수정 횟수 검증.
- 자세한 정량 합격은 [ACCEPTANCE_AND_ROADMAP.md](ACCEPTANCE_AND_ROADMAP.md). **이번 브랜치 제품 개발·CI·실고객 검증 0**.
