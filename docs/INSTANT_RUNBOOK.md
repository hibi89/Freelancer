# AX ZERO — Instant P1 구현 Runbook

## 시작 순서
1. 이번 채팅 대상 `hibi89/Freelancer@product/ax-zero-local` 확정, 최신 HEAD/AGENTS/HANDOFF/STATUS/REQUIREMENTS/FINAL_BLUEPRINT 실제 내용 확인.
2. `WORK_PHASE_GATES.json` 및 `INSTANT_TASK_QUEUE.json` 읽고 depends_on 만족하는 READY 중 **독립 가능한 3~10개를 배치**. 최신 HEAD와 allowed_paths 충돌 없는지 확인.
3. P1은 코어·FE/대시보드 포함 전체 구현 후보 우선. P2 전체 브라우저·CI·E2E 검증을 구현완료율 분자에 넣지 않는다. 단 기존 필수 CI 비활성 금지, 고위험 즉시 검사.
4. 작업이 차단되면 실패 2회 무진전 중단, 다른 READY로 전환, 정확 오류·시도·대안 기록.

## 최초 READY
- `AXZ-001` REQ01~02: trace 스키마/비밀 제거·로컬 테스트.
- `AXZ-003` REQ05~06: SKILL.md 등 import 정적 파서/실행계약·무신뢰 차단.
- `AXZ-006` REQ11~12: policy deny-by-default와 worker 격리 경계·안전성 국소 테스트.
위 세 가지는 코드 경로가 겹치지 않는 방향으로 개발. risk HIGH/CRITICAL path는 다른 기능보다 안전 우선.

## 구현 배치별 수용
- 생산 코드와 국소 테스트·입출력 계약·위협 케이스·로그/README를 함께 커밋.
- 테스트 증거 SHA, PASS/FAIL/SKIP/NOT_RUN, 구현한 REQ 수(예: 2/36) 기록. `IMPLEMENTED_UNVERIFIED` 명확히 표시.
- 실 모델 호출 없는 로컬 반복 루트는 실제 계측으로 검증; 로컬 HTTP/socket/브라우저 GUI를 상시 띄우는 구조를 기본 강요하지 않는다.
- source and generated tests written by same model cannot self-certify. P2 independent verification required.

## 다음 의존성·순서
`AXZ-001/003/006` → `AXZ-002/004/007/011` → `AXZ-005/008` → `AXZ-009/012` → `AXZ-010/013` → `AXZ-014/015/016` → `AXZ-017/018` (가용 READY는 실제 큐 우선, 순서 예시).
모든 `REQ-01~36` P1 후보가 완료되고 High exact SHA 승인되면 P2 큐 해제. 거짓 구현률 100%/실 Windows 검증 주장 금지.

## 인수인계
각 주요 변경 후 STATUS/HANDOFF 10항: 목표, 변경/근거, PASS-FAIL-SKIP-NOT_RUN, 진행/차단, 오류/대안, repo/branch/SHA, Product/Production 적용 여부, 원본/백업/비밀, 다음 READY/승인, KST/검증 범위. 해총 중앙 상품/기술 원장 구분 보존.
