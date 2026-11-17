# AX ZERO — 검증된 AI 작업을 실행 소프트웨어로 전환하는 로컬 엔진

**제품 식별자:** AX-ZERO · **전용 브랜치:** `hibi89/Freelancer@product/ax-zero-local` · **기준:** 2026-11-17 KST · **단계:** 최종설계 확정 / 구현 미착수 / RELEASE HOLD.

> 한 줄 정의: AI를 사용할수록 반복 업무에 AI가 필요 없어지게 하는 **경험→프로그램 컴파일·검증·변화 적응 엔진**.

## 사용자 최초 구상 — 절대 삭제하거나 약화하지 말 것
1. **AI가 처음 보는 문제를 해결**: GPT/Qwen/EAI/호환 모델 또는 기존 검증된 수행기
2. **성공한 작업의 공통 규칙 추출**: 입력·판단·작업순서·오류·출력·부작용 분석
3. **자동으로 작은 프로그램 생성**: Python·JS·SQL·워크플로, 허용 어댑터/안전한 제한 IR
4. **합성 데이터로 반복 검증**: 성공·실패·예외·권한·복구·기준결과 차등 검증
5. **검증 통과 시 AI 호출 없는 실행 모듈 승격**: 신뢰 경계 안에서만 실행, 범위 밖은 AI/인간 판단으로 복귀

## 최종 완전판
- SKILL.md/자연어 명령/기존 워크플로/실제 작업기록을 입력으로 허용
- 반복 패턴 발견 → **검증 가능한 코드**로 컴파일 → 독립 검증 → 버전 승격
- 입력·업무규칙 변화 감지 → 의존성 영향분석 → **필요 부분만** 재컴파일 → 검증·롤백
- 에이전트의 조건부 판단, 인간 승인, 실행영수증, 자원제한, 오프라인 캐시
- **AI 호출 제거율(AI Elimination Rate)**, 모델 실제 호출 감소, 토큰·비용·시간 절감, 정확도·안전도·성공률 대시보드
- My Local AI 첫 소비자, EAI 선택적 소비자, **AXNODE는 선택적 내보내기 포맷**, 의존성 아님
- 로컬 Windows 11 / Python 3.11 / GTX 1050 Ti / 16GB 우선, 모델 재학습 필수 아님

## 정본·작업
- [최종설계](docs/FINAL_BLUEPRINT.md)
- [36개 전체 요구사항](REQUIREMENTS.md)
- [설계 대안·선정](docs/ARCHITECTURE_DECISIONS.md)
- [KPI·측정·벤치마크](docs/KPI_SPEC.md)
- [안전·복구·위협](docs/SECURITY_AND_FAILURES.md)
- [My Local AI/EAI/AXNODE 계약](docs/INTEGRATION_CONTRACTS.md)
- [REQ 수용 매트릭스](docs/ACCEPTANCE_MATRIX.md)
- [Instant 구현 지침](docs/INSTANT_RUNBOOK.md)
- [P1 구현 큐](INSTANT_TASK_QUEUE.json) / [P2 검증 큐](VERIFICATION_TASK_QUEUE.json) / [단계 게이트](WORK_PHASE_GATES.json)
- [현재 상태](STATUS.md) / [인수인계](HANDOFF.md) / [작업 정책](AGENTS.md)

**표시 기준:** 구현완료율=P1 코드 구현 / 검증완료율=P2 독립 수용. 현재 P1 0/36 REQ의 새 코드 구현, P2 0/36 REQ 검증. 사용자 승인 가중치 부재로 공식 가중치 검증률은 UNASSESSED. 문서 완료는 제품 구현 완료가 아니다. AI 절감률 72%는 최초 설명용 가상 예시이지 실측값 아님.

**보안:** 미검증 모델 생성 코드가 사용자 PC를 임의로 실행/변경하지 못한다. 기본 네트워크 차단; 외부 API, 유료비용, 고객원본·권한, 배포/판매는 별도 사전 승인.