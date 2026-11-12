# ONTOINSIGHT AX 최종 요구사항
1. 사용권과 업무 의미가 검증된 CSV/XLSX(지원 시)만 입력. 인코딩·서식·숫자 단위·통화·날짜/시간대·세전/세후·환불/취소·중복·결측을 자동 탐색하되 불확실한 의미는 고객이 결정.
2. `AI_AutoML_Analyst`의 CSV schema grouping/분류·회귀 CV·분석보고 코어를 보존하고, 데이터 전처리·업무 메타데이터·온톨로지식 관계 기술 계약을 **별도 서비스**로 구축.
3. 데이터별 `customer_id`, `order_id`, `sku`, `date`, `sales`, `refund` 등 컬럼 role 초안과 통계 근거·confidence `observed/inferred/approved` 표시, APPROVED 이전 BI 지표 확정 금지.
4. 고객 개인정보·고유식별정보·민감속성을 기본 제외하거나 승인된 목적에 한해 가명 처리; 소스 변경·해시/원본 provenance·관계 모델 revision/undo·삭제/보유 정책.
5. KPI 계산을 검증된 수식으로 보존(기간, 건수/순매출/객단가/환불율/고객별 집계); 단순 집계와 모델 예측/인과분석을 완전히 분리.
6. ML은 선택 목표/레이블·표본·누수/시간정보·train/test 조건을 검사하고, 부적절하면 `ML_NOT_SUITABLE`로 안전 보류. baseline/CV/heldout/불균형/편향·과적합을 보고.
7. AI가 데이터에 없는 개선 기회/예측 가능 수익을 확답하지 않고 `observed insight/hypothesis/recommendation` 3단계, 고객 확인 필요 항목을 따로 기록.
8. 표준형은 작은 스키마 단일/몇 파일의 제한형 분석; 대용량 DB/실시간 API/민감 고객정보/시계열 산업별 예측은 별도 견적·검증.
9. 납품: 고객이 직접 검증 가능한 원본 무변경·행/합계 재계산·테스트/환경·보고서/차트·사용 권한·재분석 가이드, Windows10/11 실기기 인수.
