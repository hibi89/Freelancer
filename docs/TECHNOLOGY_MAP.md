# HAE 상품 전체 기술 스택·재사용/신규 개발 분류

## A. 반드시 쓰는 기술
| 레이어 | 기술/컴포넌트 | 책임 | 준비 수준/의존 |
|---|---|---|---|
| 런타임 | Python 3.11+, stdlib | 로컬 백엔드·입력검증·자동화 | 기존 HAE/LA |
| 운영 웹 UI | HTML/CSS/JS (localhost) | 설정·승인·작업 진행/관리 | 합성 UI 일부 |
| 기존 백엔드 | `apps/ax-flow/axflow` | 구형 기능/계약 및 단계 마이그레이션 | 제거 금지 |
| 독립 실행 엔진 | `packages/lightning-azent` / LA | 결정적 실행/상태/복구/중복방지 | 실제 customer cutover 미완 |
| 명세 | `axflow.ir.v0`, `azent.api.v0` adapter | planner/executor 경계 | 버전·contract 회귀 필수 |
| 원장 | SQLite(Audit/Run) | 계획·상태·영수증·스케줄 | 로컬 구현 |
| 사업 저장소 | 별도 SQLite, 승인된 data adapter | 업무 행·집계 | 합성 검증 |
| DB 관제 | DBVORA | 읽기 전용 자산목록·관계·백업/복구 | 실 서비스 interop 미검증 |
| 표준화 | CSV / 지원 Excel 파서 | 스키마·행 검증 | XLSX 공식 지원 추가 검증 |
| 승인/감사 | hash-bound review, run receipts | 사람 통제 | 합성 승인 일부 구현 |
| 테스트 | unittest/pytest, Node UI tests, CI, Chromium | 회귀/Windows/보안 | HAE 2 parity FAIL 잔존 |
| 배포 | Python zipapp + Windows 패키지 후보 | 셀프 설치·독립 점검 | signed installer 미완 |

## B. 조건부 / 고급형 / 아직 미검증
- Google Sheets/Gmail: OAuth2 PKCE/Provider consent, least privilege, Google Sheets incremental rows/changes, Gmail thread/labels/发送의 중복 정책. 실제 동작/쿼터 비용 확인 전 비활성.
- PostgreSQL: psycopg, TLS, read-only schema, 승인된 쓰기; 무차별 SQL 금지, 대규모 고객용 별도 계약.
- 외부 webhook/REST: TLS/allowlist, bounded timeout, schema validation, idempotency, explicit outbound approval.
- LLM: 선택형 원격/로컬, 자연어 '초안' 생성; 토큰/개인정보·비용 한도, fallback to deterministic template. 모델 미지원 환경 정상 거부.
- SOVIA: 정책/감사 보고 옵션, 필수 launch blocker 아님.
- DBVORA 복구: 원본 DB 작업 위험에 따라 별도 명시적 승인; HAE가 곧장 delete/restore하지 않음.
- Schedule service: Windows Task Scheduler/foreground runner; host-down handling, permission check, restart semantics. Hosted cloud는 고객 별도 계약.
- Password/secret store: Windows DPAPI Credential Manager 대안 검증, token rotation/revocation. 소스코드 암호 하드코딩 금지.
- Installer: 유효한 EXE/MSIX/ZIP packaging, NOTICE+SBOM, SmartScreen/서명 정책 검토.

## C. 데이터·통합 원칙
- Runtime SQLite `workflow_id/run_id/step_id/state/retry_count/approval_digest` / Business SQLite `approved rows/transaction IDs` / DBVORA metadata `asset ID/schema hash/size` 분리.
- HAE는 LA state 처리를 맡기고 LA는 UI/고객 OAuth 토큰을 소유하지 않는다.
- DBVORA가 닫혀도 기존 고정 계약의 독립 CSV→SQLite 실행은 가능, 자산 검증 의존 작업은 `HOLD`.
- 기존 n8n의 Sustainable Use License 등 최신 약관 검토 전 인앱 embed/재판매 금지. UI/코드 cloning 불허, 자체 엔진 개발 유지.
- 라이선스 등록부 필수 열: 패키지/버전/출처/라이선스/수정·재배포/NOTICE/상용검토 SHA.
- 실시간 Gmail/Sheets 데이터와 local sample을 구별하고 로그/테스트에서 고객 데이터 식별자·시크릿 제거.

## D. 경쟁 차별화 *목표* (검증 전 우위 주장 금지)
1. 입력→계획→승인→실행→증거의 단일 로컬 경로.
2. 실행 엔진(LA)과 운영 UI(HAE), 데이터 관제(DBVORA) 분리.
3. 불확실 원격 결과/원본 드리프트/재시작 시 안전 HOLD·증거 재검증.
4. 외부 종량제 비용이 없는 지원된 로컬 워크플로 기본형.
5. 고객별 사전 정의된 **인수 시나리오**와 실행·변경 보고 납품.
