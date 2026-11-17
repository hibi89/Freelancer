# AX ZERO — AI 호출 제거율·정확도·비용 KPI 정본

## 1. 헤드라인 AI Elimination Rate (최초 사용자 구상)
**분모** `eligible_task_count` = 평가 시작 시 고정된 업무 모집단에서 명시된 정책·정답 판정 기준을 만족하는 작업 개수. 간단한 작업만 골라 분모를 사후 수정 금지.
**분자** `ai_free_accepted_count` = 그 업무 중 실행 경로 전체(라우터·재시도·숨겨진 공급자 포함)에서 **모델 호출 0**, 독립 결과 검증 PASS, 권한 위반 없음, 시간·환경 조건 만족 건수.
`AI_ELIMINATION_RATE_TASK = ai_free_accepted_count / eligible_task_count * 100`.
- 예시 **가상 1000건 중 720건=72%**. 현재 실측값 없음.
- 무조건 결과 산출/캐시 hit를 성공으로 계산하지 않는다. 작업 실패·대기·판정 불명은 **분모에는 남고 분자에서 제외**. 입력 분류 시 제외된 작업은 원인/수량 별도 보고.
- 부분 외부 AI 호출이 있거나 에이전트가 분류에서 모델 호출했다면 그 작업은 AI-free 아님.

## 2. 따로 표시할 지표
- `AI_CALL_REDUCTION_RATE` = (paired-baseline model calls - new-path actual model calls) / paired-baseline calls. **0 denominator이면 N/A**, 샘플/환경 고정, 재시도 포함, 가상 '절약 추정'과 실제 분리.
- `TOKEN_REDUCTION`과 `COST_DELTA`: 동일 작업군, 모델/단가/지역·시간/입출력 토큰/로컬 전력·PC 감가(옵션) 기록. 로컬 모델 'API 비용 0'과 '컴퓨트 비용 0'은 다르다.
- `END_TO_END_LATENCY_P50_P95`: 입력 대기·로컬 모델 warm/cold·런타임 생성·디스크 IO·검증·fallback 포함/제외 각각 보고.
- `AI_FREE_SUCCESS_RATE` eligible 중 모델0/독립검증 PASS 비율 = 헤드라인과 동일; `EXECUTION_ACCURACY` 독립 oracle 결과 일치; `SAFETY_REJECTION_RATE` 부적절 요청 차단.
- `COMPILE_SUCCESS_RATE`, `PROMOTION_RATE`, `DRIFT_DETECTION_PRECISION_RECALL`, `FALLBACK_RATE`, `ROLLBACK_SUCCESS_RATE`, `COLD_START_MS`, `PEAK_RSS_MB`, `MODEL_CALLS_PER_1000_JOBS`.
- **신뢰도/샘플 수:** 작업 유형별 N, bootstrap 95% CI(가능하면), invalid/missing/timeout/ODD 분리. 편향 및 측정한계 설명.

## 3. 실제 측정 실험
U1 코드검사, U2 합성 CSV 변환, U3 합성 read-only DB 보고서 각각 미리 고정한 쉬움/중간/경계/실패/드리프트 테스트. 같은 입력·동일 하드웨어·정확 baseline 소스 SHA·모델 버전과 테스트 세트 SHA를 기록. 매 실행마다: `run_id/task_type/input_digest/baseline_sha/capability_sha/verifier_sha/eligible/model_calls/input_tokens/output_tokens/cost_or_unknown/duration_ms/peak_rss/verdict/reason`.
- A: 기존 모델 처리, B: AX ZERO AI-free 실행, C: 변경 발생 시 fallback/recompile. 부작용은 synthetic scratch only.
- 목표: 정확도와 안전을 감소시키지 않고 실제 AI-call·시간·비용이 줄어드는지 검증. **임의 절감 목표 72%를 통과 기준으로 설정하지 않는다.**
- 기준 성능이 없거나 모델 호출 카운트가 불완전하면 절감률은 `UNASSESSED`; 0원은 무호출이 아닐 수 있음.
- 최초/재사용/변경/실패/롤백 시나리오를 분리, 최악 사례를 평균으로 숨기지 않음.

## 4. 대시보드 필수
기간·업무유형·모델·버전 필터, eligible/total/unknown 분모, AI-free 성공, AI 없는 실행 성공률, 모델 실제 호출, 절감 추정/실측 구분, 정확도·안전 PASS, fallback, drift, 비용, 지연 P50/P95, memory.
모든 카드에는 `source_sha, sample_count, measured_at, verifier_status` 표시, 실측 없으면 `NOT_MEASURED`. 가상 1000/720/72% 예시는 demo badge와 생산 데이터 분리.
