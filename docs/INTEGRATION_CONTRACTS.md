# AX ZERO — 타 시스템 연결 계약

## AX ZERO 독립 실행 원칙
`axzero inspect | observe | compile | verify | run | drift | metrics | rollback` (명령은 **목표 API**, 현 코드 없음).
기본 원장 `~/.axzero` 는 OS의 사용자 전용 폴더로 배치할 목표이며 실제 경로는 구현 시 OS profile API로 결정; 샌드박스 밖 사용자 원본을 탐색·쓰기하지 않는다.
입력/출력은 버전화 JSON/Protobuf 중 JSON v1 첫 채택. 주요 필드:
- `request_id,task_type,input_contract,env_digest,allowed_effects,approval_id_or_null`
- `decision=EXECUTE_NO_AI|REQUEST_MODEL|REQUIRE_APPROVAL|BLOCK`
- `receipt_id,artifact_sha,verifier_sha,status,actual_model_calls,latency_ms`
경계: 취소 가능·timeout/재시도·idempotency, 모든 failure typed error; 모델 응답은 결정권 없음.

## My Local AI — 첫 소비자
- MLA Controller owns planning, approval, phase gates and Git worktree; AX ZERO는 **반복업무 후보 발견/모듈 컴파일/검증 후보/선택 실행**만 반환.
- MLA의 F18 independent trust verifier에 대한 역할 우회 금지; AX ZERO 자체 verifier와 MLA F18은 별도 책임. MLA authoritative VERIFIED는 MLA 독립 수용에서만.
- 입력: 합성/사용자 허가된 읽기전용 작업 메타데이터. 출력: immutable artifact ref, proposed execution, evidence, forbidden effects.
- 최초 실사용: 코드/타입 검사 리포트·safe CSV transform·read-only SQL. MLA `dev/instant-implementation-v1` 및 기존 기능 SHA 변경은 별도 작업/승인.

## EAI — 두 번째 소비자
- EAI는 독립 범용 설계·판단 실행 시스템으로 유지. AX ZERO optional port는 EAI에 최종 의사결정 권한을 요구하지 않는다.
- EAI의 기존 정책/모델 역할(예: 입력-only) 변경 금지; EAI 자체의 승인/검증 흐름 우선. 어댑터 OFF이면 EAI 독립 정상 동작.

## AXNODE — 선택적 출력/이동
- AXNODE 독자 섹터 파일 규격 `product/axnode-sector-runtime` 원본 변경 금지.
- AX ZERO 내부 검증 능력은 우선 JSON/코드 아티팩트+실행 계약으로 저장; AXNODE가 안정화되면 **명시 버전 핀의 serializer**에서 검증된 capability/IR/의존/서명/영수증 참조를 `.axnode` 포맷으로 export.
- AXNODE 파일 생성=검증 완료/윈도우 배포 성공/원격 실행 가능을 의미하지 않음. AXNODE runtime verifier와 연동계약/호환성 E2E 별도 P2.

## 해총/DBVORA/FFAX/고객 상품
초기 개발에는 미연결. 기존 GitHub Actions·웹훅·DB 원본·서비스 상태·고객 자격 변경하지 않는다. 미래 추가는 opt-in adapter+제품별 별도 승인/검증; 어떤 고객 코드도 공개 repo로 업로드하지 않는다.
