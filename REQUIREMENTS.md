# AX ZERO — 고정 전체 요구사항 REQ-01~REQ-36 (2026-11-17)

**총 분모: 36개 기능·기술 요구사항**. 사용자 최초 5단계, 이후 모든 논의(판단·변경 대응·성능·통계·대시보드·AXNODE)를 누락 없이 포함한다. 수용 조건은 개발 완료 선언이 아니라 실제 검사할 계약이다. 임의 요구 삭제·가중치 변형 금지; 구조 변경은 High 설계심사와 사용자 범위 승인.

| ID | 영역 | 필수 요구 | 최소 수용 조건 | 위험 |
|---|---|---|---|---|
| REQ-01 | TRACE | 작업 실행 수집 | 합성 실행 입력/출력/도구 호출/상태를 run_id와 시각으로 수집; 빠진 필드와 중복 ID 거부 | MEDIUM |
| REQ-02 | TRACE | 데이터 최소화·비밀 제거 | 원본 개인정보·키·프롬프트 유출 없이 허가된 특징/해시/익명화 결과만 저장; 원본은 로컬 보관 | HIGH |
| REQ-03 | DISCOVERY | 작업 동등성 지문 | 구조화 입력·환경·효과·권한·출력 계약으로 fingerprint 생성; 데이터 변경/유사 오탐 검증 | HIGH |
| REQ-04 | DISCOVERY | 반복 패턴·후보 발견 | 반복 횟수·결과 안정성·효익·위험 점수로 후보 분류; 의미가 다른 작업을 동일시하지 않음 | MEDIUM |
| REQ-05 | INGEST | SKILL.md/자연어/워크플로 수용 | 스킬 지침과 선택적 스크립트·사례·기존 코드 import; 입력을 신뢰된 실행 명령으로 해석하지 않음 | HIGH |
| REQ-06 | INGEST | 실행 계약·규칙 추출 | 입출력 스키마/전제조건/후조건/부작용/에러·권한을 구조화; 미명시 계약은 HOLD | HIGH |
| REQ-07 | COMPILER | 결정적 작업 IR·계획 | 유형화 DAG와 제한된 연산 IR; 의존성/분기/반복 상한/결정성 검사 | HIGH |
| REQ-08 | COMPILER | 컴파일·코드 생성 | 검증 가능한 템플릿/IR 기반 Python 등 생성, immutable artifact digest, source map/생성 이유 기록 | HIGH |
| REQ-09 | COMPILER | Python 로컬 어댑터 | Python 3.11의 허용 연산만 구동; 임의 exec/eval·검증되지 않은 패키지 설치 금지 | HIGH |
| REQ-10 | COMPILER | JS/SQL/워크플로 확장 어댑터 | 추가 백엔드는 opt-in; SQL 기본 읽기전용·파라미터화, JS 별도 격리, 지원 불가 시 HOLD | HIGH |
| REQ-11 | TRUST | 정책·도구 권한 중재 | 권한을 모델 출력과 분리한 정책 엔진에서 검사; read-only 기본, 위험 행동 사전 승인 | CRITICAL |
| REQ-12 | TRUST | 격리·실행 자원 한도 | 파일/프로세스/네트워크/CPU/RAM/시간/재시도 한도; 미확립 격리는 실행 불허 | CRITICAL |
| REQ-13 | VERIFY | 독립 검증기 | 생성 모델과 분리된 deterministic oracle 및 fixture 검사, 셀프 PASS 불인정 | HIGH |
| REQ-14 | VERIFY | 차등·속성·예외·보안 테스트 | 동일 입력의 기준결과 비교, 경계/변형/실패/권한/복구 시험, 테스트 편향 기록 | HIGH |
| REQ-15 | VERIFY | 섀도 실행·격리 비교 | 실데이터 원본 변경 없이 dry-run/shadow 결과 비교; 테스트 원본 재현성 기록 | HIGH |
| REQ-16 | VERIFY | 승격 게이트·등급 | UNASSESSED/QUARANTINED/SHADOW/VERIFIED/PINNED/REVOKED 구분, 근거 없는 자동 승격 차단 | CRITICAL |
| REQ-17 | EXECUTE | AI 없는 디스패처 | 검증 범위 내 캐시된 모듈만 호출; 버전·환경·입력 동일성/출력 계약 검사 | HIGH |
| REQ-18 | EXECUTE | 실행 신뢰 경계 | 분포 밖 입력/OOD·규칙 불확실·결과 검증 실패 시 중단 및 AI/인간 폴백 | CRITICAL |
| REQ-19 | EXECUTE | AI 재호출·판단 경로 | AI는 미해결 예외에 한해 선택 호출, 0원·오프라인 모드에서 외부 전송 없음; 결정권 없음 | HIGH |
| REQ-20 | EXECUTE | 고위험 인간 승인 | 삭제/결제/권한/외부전송/고객 원본 수정·출시 등은 구체적 대상·효과 승인 전 영구 HOLD | CRITICAL |
| REQ-21 | EVOLVE | 능력·자원 의존성 그래프 | 스키마/파일/외부 API/환경/모듈 version digest 의존성 명시, 역방향 영향 계산 | HIGH |
| REQ-22 | EVOLVE | 환경 변화 감지 | 스키마 드리프트/규칙·파일·도구 버전 변경과 실제 실행 실패 분리 탐지 | HIGH |
| REQ-23 | EVOLVE | 영향 최소 재컴파일 | 영향 받은 후보만 새 버전 생성, 기존 버전 고정·국소 테스트; 전역 무검증 자동 수정 금지 | HIGH |
| REQ-24 | EVOLVE | 롤백·비교·폐기 | shadow 평가 후 승격/폐기, 실패 시 이전 검증 버전으로 복귀하되 조건 변경 시 구버전 무조건 실행 금지 | CRITICAL |
| REQ-25 | RECOVERY | 멱등 작업·체크포인트 | 중복 트리거·취소·강제종료·부분완료 복구; 쓰기 작업 보상불가면 재승인 | HIGH |
| REQ-26 | RECOVERY | 영수증·감사 계보 | 입력 지문/모듈 SHA/검증기 SHA/승인/결과/AI 호출/시간/비용/오류 기록; 민감 로그 비저장 | HIGH |
| REQ-27 | STORE | 로컬 카탈로그·캐시 | SQLite WAL·원자적 기록·락·백업/복원·용량 제한; 원본/프로그램 분리 | HIGH |
| REQ-28 | STORE | AXNODE 선택형 출력 | 독립 로컬 형식으로 먼저 동작; AXNODE 어댑터는 버전 핀·타입/권한 검증 후 선택, 의존성 필수화 금지 | MEDIUM |
| REQ-29 | ADAPTER | My Local AI 1차 연동 | Controller의 소유권·F18 독립 검증 훼손 없이 명시 계약에 따라 호출; 실 저장소 변경은 별도 승인 | HIGH |
| REQ-30 | ADAPTER | EAI 2차 연동 | EAI 고유 설계/역할 보존, 선택적 API/CLI만 연결, 끄면 기존 EAI 동작 보존 | MEDIUM |
| REQ-31 | UX | CLI 및 로컬 대시보드 | 작업 후보/검증 상태/호출 제거율/승격·복구/승인 UI, CLI와 동일 진실 원장 조회 | MEDIUM |
| REQ-32 | METRIC | AI 호출 제거율 포함 KPI | task-based elimination·실호출 절감·토큰/원가/지연/정확도/안전/신뢰구간/분모 누락을 구분 표시 | HIGH |
| REQ-33 | PERF | 저사양·오프라인 최적화 | GTX1050Ti/16GB/Windows11 CPU 우선, 모델 optional, cold/warm latency·메모리 예산 실측 | MEDIUM |
| REQ-34 | PERF | 재현 가능한 벤치마크 | CSV·DB 읽기·코드 검증 합성 fixture, 짝지은 baseline, drift/편향/부트스트랩 비교 재현 | HIGH |
| REQ-35 | OPS | 모델/공급자 탈부착 | 기본 OFF/로컬 0원, 외부 API·Hydrogen·Codex 연동은 opt-in+별도 GO, 과금/전송 무승인 금지 | HIGH |
| REQ-36 | OPS | 설치·SDK·문서·권리 | 로컬 패키지, 버전 마이그레이션, 데이터 삭제/백업, 라이선스/NOTICE, Win10/11 실기기 단계 구분 | MEDIUM |

## 종단 간 성공 조건
1. 동일한 합성 작업을 기존 모델 방식으로 먼저 수행한 **정확한 기준결과**가 있다.
2. 반복 패턴을 감지·계약화하고 격리된 실행 코드/IR을 생성한다.
3. 생성 모델과 별개인 검사자가 차등·예외·권한·회귀를 수행한다.
4. 검증된 범위의 입력은 실제 호출 0으로 실행하되 위험/범위 이탈 시 AI 또는 사람에게 제어를 넘긴다.
5. 입력·환경 변화 발생 시 영향 그래프로 영향을 받은 능력만 재생성하고 재검증한다.
6. 모든 단계의 출처, 버전, 검증 SHA, 리스크, 실제 AI 호출 수·시간·비용을 기록한다.
7. GUI/CLI에서 작업별 AI 호출 제거율·실제 호출 절감·품질 저하 여부를 확인할 수 있다.
8. My Local AI가 일차적으로 이 엔진을 선택 호출하고 EAI 및 AXNODE 없이도 독립 기동한다.

## 분모와 승인
- P1 코드 구현 후보: 각 REQ 구현 + 최소 국소 근거 갖춘 경우만 완료 카운트. 설계/목업/테스트 정의만으로 완료 처리 금지.
- P2 공식 검증: 승인 가중치와 전체 수용 조건 검증 전 `UNASSESSED`. P1=100%라도 P2=100% 아님.
- RELEASE HOLD/상용 미등록 유지. 모든 금액·속도·정확도는 실측 전 가설.
