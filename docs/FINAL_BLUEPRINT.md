# AX ZERO — 최종설계도 v1.0 (OWNER 기능 범위 고정, High 기술판단)

**설계 기준일:** 2026-11-17 KST · **정본:** `hibi89/Freelancer@product/ax-zero-local` · **범위:** REQ-01~REQ-36 전체 · **구현 상태:** 미착수 · **검증:** NOT_RUN/UNASSESSED · **출시:** RELEASE HOLD.

## 0. 제품 본질·비목표
**AX ZERO = AI가 해결한 작업을 실행 가능한 작은 프로그램으로 컴파일하고, 신뢰 경계 안에서는 AI 없이 실행하며, 조건이 바뀌면 필요한 부분만 AI로 재작성·검증·진화시키는 로컬 엔진.** 단순 RPA, SKILL.md 리더, LLM 답변 캐시, 모델 학습기, AXNODE 파일 생성기만으로 기능 축소하지 않는다.
- 목적은 **정확도/안전을 유지한 상태에서 AI 호출·토큰·작업 총시간·반복 비용 감소**; GPU 학습이나 대형 모델 소유가 목적이 아님.
- 기술 독창성/특허/성능 우위를 보장하지 않음. 프로그램 합성·스킬 컴파일·RPA self-healing·재사용 메모리 등 선행 기술이 존재하며 경쟁 제품 대비 차별화는 벤치마크로 판단.
- 단일 파일 AXNODE의 별도 목표(독자 바이너리 섹터/원격 자원 런타임)는 침범하지 않음.

## 1. 최초 사용자 구상: 절대 유지할 5단계
1. **AI가 처음 보는 문제 해결:** GPT/Qwen/EAI 또는 허가된 AI 워커가 문제를 해결; 작업 요청·입력 계약·성공/실패·실측 실행 경로를 추적. 최초 작업이 이미 결정적/기존 코드로 처리되면 AI를 강제 호출하지 않음.
2. **성공 작업 공통 규칙 추출:** 입력·판단·작업 순서·오류·출력 구조를 비교. *일회 성공*만으로 반복 가능한 법칙을 단정하지 않으며 실패 기록과 반례도 보존.
3. **자동 작은 프로그램 생성:** Python/JS/SQL/워크플로용 제한 IR·템플릿·검증 가능한 생성기. 코드 생성 뒤 정확 의존성·최소권한·결정적 계약 기록. 지원하지 않는 임의 작업은 후보 보류.
4. **합성 데이터 반복 검증:** 정상·실패·예외·권한·복구·변형/경계 테스트, 기존 모델/정확 oracle과 차등 비교. 모델이 자기 만든 테스트만 통과하는 경우 승격 불가.
5. **검증 통과 시 AI 없는 모듈로 승격:** 고정된 계약과 입력 신뢰 경계 안에서만 호출 0, 경계 밖/드리프트/오류/위험 작업은 즉시 HOLD→AI 분석 또는 인간 승인→새 버전 격리 테스트.

## 2. 전체 데이터·제어 흐름
```text
SKILL.md / 작업지침 / 로그 / 기존 스크립트 / EAI·MLA 요청
    ↓ ingest(출처·비밀·신뢰등급) → task trace / baseline
    ↓ 반복 작업 지문·유사성·비용·위험 평가
    ↓ contract extractor (입력/출력/전제조건/부작용/권한)
    ↓ 제한 typed IR → code synthesizer / template compiler
    ↓ policy & isolation preflight → independent verifier
    ↓ shadow + differential + property + regression + security
    ↓ promotion registry (immutable SHA + evidence + owner approval)
    ├─ 입력이 검증 범위 내 → deterministic runtime (AI calls=0)
    └─ 변경/OOD/불확실/오류 → HOLD → local/opt-in AI or human
                                  ↓ 변경 영향 그래프 → 선택적 재컴파일
                                  ↓ 독립 재검증 → 새 버전 승격/롤백
    ↓ receipts + KPI/benchmarks + optional AXNODE export
```
입력 소스·모델 출력·SKILL.md는 모두 untrusted. 검증기·승격 정책·승인은 외부 신뢰 경계에서 소유.

## 3. 내부 모듈 (BE)
- `core.trace`: 동의 기반 이벤트 수집·PII 최소화·run_id/parent·도구 부작용·처리 시간, 모델 통계.
- `core.discovery`: 구조적 fingerprint(작업 유형+입력스키마+환경+효과계약+출력계약), 유사패턴/드리프트 후보와 반례 저장.
- `core.ingest`: SKILL.md/자연어/워크플로/기존 코드 수용; 스킬 속 스크립트를 자동 실행하지 않고 **명세 데이터**로 취급.
- `compiler.ir`: typed DAG; 분기/반복 상한/위험 행동·불확실성 주석/불변 artifact content digest.
- `compiler.codegen`: 템플릿 우선, 필요 시 한정된 모델 도움. Python first, JS/SQL/워크플로 플러그인. 모델 생성 코드는 검증 전 격리.
- `security.policy/isolation`: user-owned 권한 경계, 네트워크 DENY, 파일·실행·RAM·시간·호출 한도, 무승인 외부 설치/호출 차단.
- `verifier`: 신뢰된 독립 oracle, 동일 fixture 차등 평가, property/metamorphic, 부작용 기록, 테스트 커버리지와 시험 공백 표시.
- `runtime.dispatch/boundary`: 모듈 버전 pin, 입력 스키마+분포 밖 입력 검사, 실행 또는 HOLD/FALLBACK. **AI 판단은 도구 실행 권한 아님.**
- `evolve`: 환경·스키마 의존 그래프 역조회, 변화 감지, 영향 최소 후보 생성·shadow·검증·승격·철회.
- `storage.catalog`: 로컬 SQLite 원장, 모듈/검증 SHA·타임라인·캐시·영수증·복구·용량관리. 원본 고객 파일 분리.
- `metrics`: 호출 제거율/절감·정확도/성공률·토큰·시간·자원·비용·불확실성, 분모 변경 경고.
- `adapters`: MLA 첫 실사용, EAI optional, AXNODE optional serializer; 모두 **독립적으로 OFF 가능**.
- `cli/ui`: 로컬 CLI 및 간단한 읽기전용 우선 대시보드, 작업 이력·에러·승격·취소·안전 승인 동선.

## 4. FE/사용자 동선
화면 1 Overview: total/eligible/AI-free-success 작업수 + AI Elimination Rate, 실제 AI 호출 감소, 정확도 변화, 시간/비용, 기간·작업유형별 세그먼트(예시 1000건/720건/72%는 가상).
화면 2 Candidates: 발견된 반복 패턴, 기준작업, 효익가설, 지원 범위, 위험점수, 컴파일 준비.
화면 3 Compile: 계약·IR·코드 diff/trace·의존·권한; sandbox 테스트 결과와 실패 이유.
화면 4 Registry: QUARANTINED→SHADOW→VERIFIED/PINNED→REVOKED 상태와 변경 SHA·롤백.
화면 5 Runs: 실제 모델 호출 0/양수, 입력 fingerprint, 출력 oracle, 경계 이탈 및 사람 승인.
화면 6 Drift: 바뀐 환경, 영향 받는 노드·관련 테스트, 새 버전 비교·선택적 승격.
화면 7 Settings: 네트워크 기본 OFF, 외부 공급자 명시 opt-in, 키는 OS secret store, 기본 비용 0, CPU/GPU/RAM 예산.
P1에서 BE/FE 완전 연결과 최소 smoke 필수; 브라우저/시각/접근성/반응형 전체 검증 P2 이관.

## 5. 실행 계약·판단 설계
```text
Capability {
  id, version, artifact_sha, source_sha, producer, provenance,
  input_schema, output_schema, preconditions, postconditions,
  effects, required_capabilities, resource_limits,
  known_supported_domains, assumptions, validator_sha,
  fixture_set_sha, oracle_evidence, risk_tier, rollout_state,
  dependencies[], rollback_reference, expires_or_revalidate_at
}
RunRequest {run_id, capability_id, expected_sha, input_digest,
  environment_fingerprint, requested_effects, policy_context}
Decision = EXECUTE_NO_AI | NEED_AI_REVIEW | NEED_HUMAN_APPROVAL | BLOCKED
Receipt {run_id, capability_sha, verifier_sha, actual_model_calls,
  input_digest, output_digest, verdict, duration_ms, peak_memory_mb,
  approvals, failures, rollback_ref}
```
- 실행신뢰경계: 스키마 맞춤만으로 충분치 않다. 의미/정책/데이터분포/기저 시스템 버전까지 적합해야 함. 자동 신뢰 점수는 **근거/불확실성의 지표**이지 보안 승인 권한이 아니다.
- 회색 영역에서는 AI가 **제안**하되 실제 실행/승격은 독립 정책+검증을 통과한 경우에만.
- 고위험 변화(세금/매출 규칙/권한/고객 파일 삭제·외부 데이터 전송)는 수동 승인. 독립 검증 불가능하면 QUARANTINED.
- 재컴파일은 immutable previous artifact 유지, dependency blast radius 및 관련 테스트 전수 수행. 다운그레이드하여 이전 버전을 조건 무시 실행하는 '위험 롤백' 금지.

## 6. 런타임과 최적화
- 기본 로컬 Python 3.11 stdlib+경량 의존성, SQLite, deterministic executor; Windows 11/GTX1050Ti/16GB RAM. CPU-first; Qwen3 4B는 optional 모델, 외부 서비스 기본 OFF. 모델 없는 기능 경로에서 Ollama 프로세스를 필수 기동하지 않는다.
- 캐시는 **입력 지문 + 실행 모듈 SHA + 환경/정책 버전 + 허가 범위**로 키를 구성. 비결정적/외부 쓰기·민감 업무는 무조건 캐시하지 않는다. 캐시와 프로그램 생성/실행을 혼동하지 않는다.
- 성능은 hot path에서 fingerprint+schema/policy 검사 후 직접 함수/가벼운 워커를 실행; 독립 프로세스 시작·DB 조회 비용을 계측. 격리 한계가 있는 환경은 안전 범위를 줄이지 않고 실행 차단.
- 결과 동일성, P50/P95 시간, CPU/RAM/저장량, 모델 기동 시간 포함/제외 두 시나리오, AI 호출·토큰 측정.

## 7. 변경·오류·복구 시나리오
- 열 순서만 바뀌어 이름기반 계약이 유지되면 동일 능력 실행.
- `매출액`→`총매출`의 의미가 확인된 alias는 테스트 후 매핑 변경; 이름만 비슷하면 AI 없이 실행하지 않음.
- 세금/통화/환율 규칙 변화는 정책·검증 및 사람 승인 없이는 변경 거부.
- 데이터베이스 스키마 변경: 영향 DAG의 capability를 선택 검증/재생성, 관련 없는 능력만 그대로 유지.
- 네트워크 끊김: cached offline safe task만, 원격 required 는 PENDING/BLOCKED, 무한 재시도 금지.
- 컴파일 오류·생성 모델 착각·독립 검증 실패: QUARANTINED, 기존 verified digest 보존.
- 쓰기 중 crash: SQLite 트랜잭션/체크포인트와 idempotency key, compensation 불가능 시 반드시 human review.

## 8. 메트릭 필수 (세부 정본 docs/KPI_SPEC.md)
- **AI Elimination Rate (업무 기반) = 100 × AI 호출 0건으로 성공하고 독립 수용된 eligible 작업 수 / 전체 eligible 작업 수.**
- 별도 관측: 실제 모델 호출 횟수/1천 작업, 짝지은 기존모델 baseline 대비 call reduction %, 토큰·금액·P50/P95 latency, CPU/RAM, AI fallback 비율, OOD 거부, 재컴파일 성공·오탐, 회귀율.
- eligible 분모는 실행 *전에* 동결하며 단순 어렵거나 실패한 일을 임의 제외해 비율을 부풀릴 수 없다. 평가 기간, 제외 이유, baseline SHA, 실제 vs 추정 명시.
- 가상 데모: 1,000건 중 AI 없는 독립 검증 성공 720건이면 72%. 실제 달성 주장 금지.

## 9. 첫 사용 사례와 개발 순서
U1 코드 검사·타입/구조 검증(파일 읽기전용, 위험 낮음) → U2 CSV/JSON 변환(합성 데이터, 안전 출력) → U3 read-only SQL 보고서 → U4 My Local AI Controller 계약형 호출 → U5 EAI opt-in → U6 AXNODE export opt-in.
코어 기능이 안정화되기 전 제품 범위를 일부로 감축하거나 상용 출시는 금지. AXNODE 미완성은 U1~U5 차단조건 아님.

## 10. 구현/검증/출시 단계 분리
- **P0** 본 최종설계, REQ/큐/수용조건 확정. 사용자 최초 사상 변경 금지.
- **P1** Instant 주력: REQ-01~36 BE/FE 코드 및 국소 안전 스모크로 구현 후보 100%; 전체 CI·브라우저 E2E는 P2 후행, 단 고위험 즉시 검사 불가면 해당 작업 HOLD.
- **P2** 전체 독립 CI/통합/보안/Windows/실사용/브라우저/성능/회귀 및 수정; 9개 검증 큐.
- **P3** Codex Sol Max 기술·보안 + Astra Max UI/UX 독립 검수; 실제 실행한 경우만 인정.
- **P4** High 전체 36요구 인수; 실환경·비용·보안·원본 보호 판단. **P5** 사용자 GO 전 배포/크몽 등록 금지.
- 최종 안전 수용: 고객원본/키 유출 0, 비승인 고위험 실행 0, 결정적 기준 작업 결과 차등 불일치 0(필수 fixture), 누락 테스트는 NOT_RUN, 기존 프로그램 대비 정확도 저하를 숨기지 않음. 목표 속도 향상은 **실측 판단**이며 숫자 자동 PASS 아님.

## 11. 설계·소스·실증 상태
현재 생성 파일은 설계/큐 문서뿐. 제품 코드 0, 자동 워크플로/실 Windows/실 브라우저/AI 호출 절감 실측 0. 구현 0/36 REQ, 공식 P2 검증률 UNASSESSED, 출시 HOLD. 새로운 설계 이외 다른 제품 브랜치·원장/설치 환경 변경 금지.

## 12. 권리/선행연구/승인
'세계 최초', 특허성, SkillCompiler/SkillGen 등의 완전한 재구현/라이선스 적합성 주장은 검증 전 금지. SKILL.md의 포함 스크립트는 외부 소스 라이선스 및 사용자 허가 별도 확인. API·고객 정보·모델 코드/모델 가중치의 GitHub 공개 금지. 중요 정책은 docs/SECURITY_AND_FAILURES.md.
