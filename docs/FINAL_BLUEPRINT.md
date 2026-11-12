# AZENTFLOW AX — HAE + Lightning Azent 기업 업무 자동화 / FINAL BLUEPRINT v1.0

> **상품명: AZENTFLOW AX** · 승인형 기업 업무 자동화 · 기술 원본은 HAE + Lightning Azent + DBVORA; 기존 기술 이름/저장소는 변경하지 않는다.
**2026-11-13 KST · 상품 완료 100% 판정 정본 · 설계 문서, 코드 구현 보고서 아님**

## 0. 제품 정의와 고객 가치
- 제품 이름: **AZENTFLOW AX (HAE Enterprise Workflow Automation)**. HAE = Humanized Automation Ecosystem; LA = Lightning Azent.
- 고객: 반복 엑셀 정리, 파일 집계, DB/Sheets 보고, 승인형 메일 전달을 반복하는 1인 사업자·소규모 팀. 통화 최소화, 지원 템플릿과 고객이 승인한 범위만 납품.
- 구매 결과물: 설치 가능한 로컬 관리 화면·실행기, 정확히 계약한 워크플로, 실행/실패/재시도 보고서, 원본 보존·백업 방법, 인수테스트 결과.
- 목표 지표: 재현 가능한 업무 단계, 실패 시 복구 가능성, 중복 실행 시 비즈니스 쓰기 중복 없음(지원된 로컬 SQLite에 한정), 무승인 실행 0건, 비밀/고객행 로그 유출 0건, 계약한 처리시간/데이터 정합성. 생산성 개선 수치는 고객 실측 전 가설.

## 1. 소유권과 원본 기술 계보
| 구성 | 원본/책임 | 변경 원칙 |
|---|---|---|
| HAE 운영자 UI·계획·정책·커넥터·승인 | `hibi89/HAE@feature/axflow-mvp` (검토 기준 HEAD `1de81c2fc1fb671fd20603b64e1be76b6d36aad5`) | 원본 repo에서만 개발, 이 저장소는 설계 |
| Lightning Azent LA 실행기 | `hibi89/HAE@feature/lightning-azent` (검토 기준 HEAD `9fce9e2f13fdfd9e0768fa8ad4675a3762863201`) | 독립 LA 패키지/계약 유지, 일괄 무검증 교체 금지 |
| HAE legacy `axflow` | `apps/ax-flow/axflow` | 검증 후 점진적 LA adapter 전환, 이전 기능 보존 |
| DBVORA 데이터 관제 | 비공개 `hibi89/DBVORA` | 별도 API/권한 및 소스/백업 소유권 |
| REA_APP | HAE 내부 소스 분석 도구 | 고객 업무 실행 엔진과 분리 |
| SOVIA | `hibi89/SOVIA_sovereign` | 유료 옵션용 감사·정책, 출시 의존성 아님 |
| 참고 n8n | 독립적 동작 비교 도구 | 코드/노드/UI 불법 이식·라이선스 침해 금지 |

## 2. 100% 고객 시나리오
1. 비개발자 고객이 오프라인 실행 프로그램 설치 및 샘플 워크플로 확인. 설치 실패 시 원본 시스템/파일 무영향으로 취소.
2. 고객이 **지원되는** 한국어 설명 또는 템플릿 선택: 예) '매일 거래 CSV의 중복을 검사해 안전한 SQLite로 저장하고, 승인 후 집계표 저장'.
3. HAE가 입력 파일 형식/매핑·작업 주기/대상·변경 범위·예상 로컬 소요·API 사용량을 계산하고 `PLAN_DRAFT` 생성.
4. 정책/스키마 검증: 파일 SHA·경로·크기·허용 작업·버전·권한·소비 예산. 불명확한 열 의미, 결제, 외부 전송은 `REVIEW_REQUIRED`.
5. 고객이 드라이런 화면에서 입력/출력의 비밀값 제외 샘플과 영향 범위를 확인. `plan_hash` + `input_hash`에 묶인 승인을 서명/세션 인증과 함께 별도 기록.
6. LA가 검증된 IR에 정의된 단계를 로컬에서 실행; 런타임 원장과 업무 DB는 격리. 재시도와 체크포인트는 단계별 실제 결과를 재검증.
7. 외부 API는 각 커넥터 범위 내에서만 사용; 응답 모호 시 실제 조회로 중복 여부 확인 가능한 경우에만 재실행. 불가능하면 `HOLD`.
8. 로컬 DBVORA가 사용자 선택 DB의 자산 ID·스키마·백업 상태를 조회; DBVORA가 없어도 독립 실행 가능한 구간은 명시된 DEGRADED 모드.
9. 오류 발생 시 자동 롤백 가능한 범위만 보상; 외부메일/메시지 전송처럼 취소 불가능한 단계는 재전송 전 반드시 판단 요청.
10. 화면에서 완료/실패/보류 증거, 누가 언제 승인했는지, 재시도 횟수·고객 업무 결과의 정합성을 확인하고 읽기 전용 결과물을 납품.

## 3. 최종 전체 아키텍처
```text
User/Owner
  ├─ Korean NL request + curated templates + files
  └─ Configured OAuth scopes / consent (never raw tokens to LLM)
        ↓
HAE UI/API (localhost by default; origin/session/CSRF)
  ├─ file intake & field-semantic review
  ├─ planner: deterministic templates / optional bounded LLM proposal
  ├─ IR validation + risk / cost / permission gate
  ├─ plan approval: actor + planHash + inputDigest + scopes + expiry
  ├─ workflow catalog/versioning & manual schedule controls
  └─ capability negotiation: HAE↔LA adapter contract
        ↓ only approved typed plan
Lightning Azent independent runtime
  ├─ deterministic graph/DAG execution
  ├─ bounded per-step timeout/retry/backoff/circuit breaker
  ├─ durable checkpoints & status receipts
  ├─ idempotency + ambiguous result HOLD / operator review
  └─ local isolated runtime SQLite (jobs/steps/checkpoints/approvals)
        ├────────────────────────────────────┐
        ↓                                    ↓
Supported business adapter                 Connector broker
  ├─ local CSV/XLSX validated               ├─ Gmail (optional, real OAuth gate)
  ├─ business SQLite separate DB            ├─ Google Sheets (optional)
  └─ future PostgreSQL adapter              └─ signed/allowlisted REST APIs
        ↓                                    ↓
DBVORA local API (optional)              Provider status & quotas
  ├─ selected asset schema snapshot          └─ never assume external exactly-once
  ├─ readonly inventory
  └─ verified independent backup/restore
        ↓
SOVIA audit option → redacted operator report / receipts → delivery package
```
불가: '전 세계 모든 앱 자동화', 'PC 꺼져도 실행', '무제한 웹 크롤링', '외부 결제 권한 자체 발급', '언제나 정확히 한 번' 보증.

## 4. 단계별 모듈과 독립 계약
### 4.1 입력/정규화
- `intake`: 로컬 업로드 허용 목록, UTF-8/BOM·CSV injection·정확한 스키마, 파일 상한, 비밀컬럼/개인정보 분류. 파일 경로는 사용자 지정 루트 상대경로만 허용하고 링크·디렉터리 순회·경합/파일 교체 검사. XLSX/대형 PDF는 표준형에 기본 보장하지 않음.
- `semantic_mapper`: '주문 금액=세전/세후?', '환불은 음수?' 등 의미에 관한 확정 입력. AI 추정값은 `UNAPPROVED`.
- `normalizer`: 원본 유지한 파생 결과, 오염 행 HOLD, SHA-256 provenance와 변경 리포트.

### 4.2 계획 / 실행 분리
- `planner`: 자연어를 바로 임의 실행하지 않으며 지원된 작업 vocabulary로만 표준 JSON IR 생성. 불명확/미지원 요청은 검토.
- `schema_registry`: `axflow.ir.v0` 및 LA 전환 `azent.api.v0` 지원 버전·capabilities, 최소 backward compatibility 기간.
- `policy`: read/write/external/disclosure/risk classifier, user allowed destinations, rate/budget, revocation policy.
- `approval`: 미리보기별 단일 plan digest 승인, 수정되면 모든 승인 무효화; 소유자 인증/권한 없는 self-assertion 불가.
- `la_adapter`: 내부 계획을 LA 외부 계약으로 변환, SHA 및 step count 일치·결과 status 검증·구형 HAE와 리플레이 상호운용.
- `executor`: LA의 가용 작업만 실행, plugin allowlist, 디폴트 인터넷 차단, shell/system command 불허.
- `state`: run/step/job/receipts/idempotency/schedule/retry 원장, business database와 물리적·권한적 격리.
- `business_db`: 사용자가 지정한 SQLite 로컬 데이터만 명시된 쓰기 트랜잭션으로 반영; 임의 SQL 실행 API 미제공.
- `connector_broker`: 실 고객 승인된 OAuth만, OS secure storage, 최소 scope, token rotation/expiry, provider-specific read-after-write/receipts.
- `dbvora_bridge`: localhost DBVORA `p0-01.v1` 같은 명시 계약으로 자산 ID/SHA/크기/테이블/FK 조회, 원시 행·계정 토큰 불노출.
- `sovia_bridge`(옵션): 감사 이벤트를 비식별 표준 스키마로 넘기고 보호 정책 판단. 응답 실패가 무단 실행 권한으로 상승하지 않음.
- `ops_ui`: 작업 목록·승인·보류·재시도·실행증거·파일 해시·복구/내보내기/삭제 요구.

### 4.3 예시 도메인 계약 (설계용, 구현 완료 아님)
```json
{
  "contract": "hae.workflow.v1",
  "workflow_id": "wf-demo",
  "version": 3,
  "source": {"kind": "csv", "path_token": "source-id", "sha256": "<hash>"},
  "plan": {"ir_version": "axflow.ir.v0", "hash": "<hash>",
            "steps": [{"id":"parse","op":"csv_read"},
                      {"id":"stage","op":"sqlite_import_csv","requires_write_approval":true}]},
  "approval": {"state": "PENDING", "actor_id": null, "expires_at": null},
  "policy": {"network":"deny", "max_retries_per_step":2, "max_runtime_sec":300},
  "execution": {"run_id": "run-demo", "state":"NOT_STARTED"}
}
```
이 예시는 API 계약 설계를 위한 가상값; 실제 스키마·엔진 필드와 다른 부분은 adapter 계약 테스트에서 고정하고 호환 이전 전환 금지.

## 5. 상태 기계·반복 실행·복구
- `DRAFT→VALIDATED→PREVIEWED→WAITING_APPROVAL→APPROVED→RUNNING→COMPLETED`; `HOLD|FAILED|CANCELED|RECOVERABLE`을 별도 분기.
- 승인에는 actor/session identity, workflow/version, plan hash, source hash, 수신인/송신 범위, 정책, 만료 시각을 묶는다. 중간 변경·재시작 후 이전 승인 자동 재사용 금지.
- SQLite 트랜잭션 경계 내에서 business write+local receipt를 묶을 수 있을 때만 원자성 주장; 외부 API는 provider idempotency key 또는 확인 조회가 없으면 불확실 결과를 보류.
- 스케줄 tick은 `schedule_id+interval_anchor+sequence+plan_hash`로 안정된 중복 키 생성. PC 오프라인이면 놓친 tick 처리 정책 선택, 무제한 적체 실행 금지.
- 장애 분류 `BAD_INPUT`, `NEEDS_SEMANTIC_REVIEW`, `AUTH_EXPIRED`, `PROVIDER_LIMIT`, `NETWORK_UNKNOWN`, `STATE_TAMPERED`, `NEEDS_OWNER_APPROVAL`, `NON_RETRYABLE`, `DEPENDENCY_UNAVAILABLE`. 정확한 사용자 행동·단일 재시도 가능 여부 기록.
- 복구: 실행중 프로세스 크래시·Windows 재부팅·DB 롤백·부분 업로드·API 429/5xx·비밀정보 폐기·계획 변경·검토 도중 데이터 교체·동시 시작을 독립적으로 시험.

## 6. 보안·데이터 흐름
- **데이터 저장과 조회 분리:** 입력 원본 읽기 전용, runtime ledger 메타데이터만, business DB 승인된 행만, audit ledger 민감 payload 없음.
- 로컬 서버 127.0.0.1 바인딩, 세션·Origin·CSRF·Host/포트·경로 검증, JSON 크기 상한. 브라우저 로컬 프리뷰가 일반 인터넷 서비스를 뜻하지 않음.
- 고객별 비밀정보는 OS credential manager 또는 적합한 암호 저장에만. GitHub/AI 프롬프트/스크린샷/에러로그 노출 불가.
- 프롬프트 인젝션/CSV 수식/링크/디렉터리 순회/세션 재사용/다운로드 공급망/의존성 CVE·라이선스 점검.
- GDPR/PIPA 등 적용 법과 위탁·보유 정책은 거래별 확인. 기본값 외부 자료 전송 0, 실 고객 동의 없는 테스트 0.

## 7. 원본 코드 보존·납품 구조
- 원본 HAE/LA/DBVORA는 별도 Git 브랜치·검증 SHA로 취급, this repo는 합쳐진 flatten 코드나 진짜 설치 파일이 아님.
- 제품 빌드: 버전 고정 소스→테스트→빌드→내부 ZIP/EXE→새 임시 설치 폴더→Windows 10/11 크롬/엣지→실작업→백업/복구→삭제/재설치.
- 고객 납품물: 버전 태그, LICENSE/NOTICE, 실행기, 사용자 가이드(한국어), 승인 기록, 지원 업무 2개 recipe, 데이터 보관/삭제 안내, 테스트 CSV, 검수 결과, 복구/업데이트 절차.
- 어떤 단계도 기존 사용자의 원본/운영 DB를 무단 덮어쓰지 않는다.

## 8. 범위 외·고객별 승인 사항
- 외부 SaaS의 데이터·계정 권한 무제한, 민감 메일/재무자료 임의 클라우드 전송, Google OAuth 자동 대신 인증, 결제 대행, 사이트 보호 우회, ERP 전사 통합.
- 로컬만 사용 시 PC가 꺼져 있으면 실행되지 않는다. 항상 실행하려면 고객 허가한 상시 서버/작업 스케줄러 별도 구축.
- 업종별 규정, 전자서명/실사업자 증빙, 예상 업무 절감액의 실측과 서버·API 운영비는 계약 후 확정.

## 9. 핵심 출시 판정
[수용·로드맵](ACCEPTANCE_AND_ROADMAP.md)의 100점 전부 충족 + 고객/자격/라이선스/영수증/정보처리/실제 Windows 설치·3개 지원 워크플로 PASS + **전체 CI GREEN** 없으면 `RELEASE HOLD`. 중간 85%는 고객에게 '완성'이라고 광고하지 않는다.
