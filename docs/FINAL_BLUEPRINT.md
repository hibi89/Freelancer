# PROOFQA AX — FINAL PRODUCT BLUEPRINT v1.0
**2026-11-13 KST · 향후 상품 100% 완성의 정본 · 기업 개발품 납품 검수 서비스**
**중요: 설계 완료 ≠ 통합 구현 완료/보안 인증/고객 납품 완료. RELEASE HOLD.**

## 0. 고객과 제품의 본질
- 타깃: AI 코딩 도구로 만든 MVP/웹사이트/소규모 백엔드를 납품받는 고객, 개발 외주 종료 단계의 발주자, 작은 개발팀의 PR 릴리스 담당자.
- 고객이 구매하는 것은 자동 취약점 스캐너 실행이 아니라 **기능·구조·의존성·보안·납품 완결성에 대한 재현 가능한 인수 검수**다.
- 고객 문제: AI 생성 프로그램이 외형상 작동해도 클릭 후 실제 저장/조회 실패, 브라우저 흰화면, 숨은 누출, 미구현 API, 소스/빌드 차이, 미검증으로 인한 분쟁이 발생한다.
- 납품 결과: `기준자료+사용권 확인 → 정적·구조·실브라우저 검수 → 증거·독립 판정 → 수정 우선순위/수용 판단 → 수정 후 재검증 → 한국어 보고서/인수패키지`.
- 진실 구분: **CONFIRMED**, **NEEDS_VALIDATION**, **REJECTED**, **NOT_COVERED**. 기술 한계로 미검증한 부분을 통과로 세지 않는다.
- 서비스가 제공하지 않는 것: 무조건적 보안 보증, 국가/국제 인증서, 취약점 0개 보장, 침투테스트 전체 대행, 법적 감리/사람 보안전문가의 서명, 무단 실고객 DB 접근.

## 1. 기술 원본과 저장소 역할
| 기술 | 소스 및 책임 | 통합 방식/경계 |
|---|---|---|
| AI Code Checker | `hibi89/ai-code-checker`, 기존 오프라인 GUI/CLI/리포트; 조사한 개발 브랜치 `feature/retail-private-candidate-20261112` HEAD `64744eebd109ebbdfd6dafca23ec23329cc3ee77` | 소스 정본; 안전 입력/정적 검사 엔진·한국어 보고 재사용. 소스 미변경 |
| Graphify | `https://github.com/Graphify-Labs/graphify` | 로컬 코드·SQL AST 관계 그래프, 노드/엣지/근거; 버전·라이선스 고정. Cloud 옵션 기본 금지 |
| agent-browser | `https://github.com/vercel-labs/agent-browser` | 허가 스테이징 웹 UI의 실제 탐색/클릭/스크린샷/결과. 재현 가능한 세션으로 격리 |
| Cloudflare security-audit-skill | `https://github.com/cloudflare/security-audit-skill` | coverage-led 감사/독립 반증·machine-readable finding **방법론**. 도구 자동 실행/Cloudflare 제휴/보안 인증 의미 아님 |
| Playwright/Chromium | 실 브라우저 2차 백엔드 | 재현 가능한 E2E 테스트와 콘솔/네트워크 증거; agent-browser 버전·호환 실패 시 범위 공개 |
| PDF/HTML/ZIP/JSON | 기존 code checker + 별도 verifier | 납품 패키지, manifest/SHA, 고객 검수/재검수 계약 |
- 고객용 제품 개발은 원본 `ai-code-checker`에 신규 독립 상업 기능 브랜치를 열어 진행(사용자 승인 후). 여기 `Freelancer` 브랜치는 최종설계·상태·상용 납품 정책만 관리한다.
- 제3자 오픈소스는 **상용 재배포 허용/NOTICE/버전 취약점/라이선스 양립**을 실제 소스 태그 기준으로 검증해야 한다. 현재 조사한 라이선스 정보: Graphify Apache-2.0(+ 과거 MIT 고지 가능), agent-browser Apache-2.0, Cloudflare Skill MIT. 실제 bundling 전 재확인.
- 공급사 도구를 쓰는 것이 고객 데이터 업로드/원격 코드 실행의 권한이 되지는 않는다.

## 2. 비교 설계와 선택
| 안 | 시간·비용 | 성능/품질 | 유지보수·리스크 | 결론 |
|---|---|---|---|---|
| A. AI에게 ZIP과 URL을 주고 한 번에 보안·품질 판단 | 빠름/LLM 종량 비용 | 거짓 양성·누락, 재현/실환경 증거 부재 | 고객 분쟁·민감정보 외부전송 위험 | **기각** |
| B. 기존 정적 Code Checker 단독 결과 PDF | 저렴·오프라인 안정 | 브라우저 행동·전체 구조/변경영향 미검사 | 저가형 보조 옵션 | BASIC 제한 |
| C. **증거 지향 오케스트레이터: 정적 Checker + Graphify + 허가된 브라우저 + 다단계 감사 + 독립 인수 검증** | 중간·테스트 비용 예측 가능 | 구조·실행·보안 진단을 교차 설명 가능 | 모듈별 교체/미지원 구분, 출시/납품 장기 유리 | **최종 채택** |
- 초기엔 사용자 승인형 테스트 플랜과 사람 리뷰 게이트를 중심에 두고, 자동 코드 실행은 독립 샌드박스가 갖춰지기 전 기본 `DENY`.

## 3. 사용자 동선 — 완제품 100% 시나리오
1. 고객이 저장소/ZIP/허가된 staging URL·스크린샷·명세/수용조건·계정/데이터 권한·비밀정보 처리 금지영역·요청 테스트 범위를 제출한다. 제3자 소스 무단 감사 금지.
2. 프로젝트 사전 평가: 저장소 크기, 언어·패키지/CI 구성, 컴파일/실행 의존성, 결제·개인정보 위험. **현재 검사 가능한 범위**와 **제외될 경로**를 견적 전에 확정한다.
3. 고객이 테스트 플랜을 승인: `subject_digest`, repo commit SHA, authorized domain/path/action, 최대 파일/요청·최대시간/비용, 역할·테스트 계정 권한, 데이터 마스킹.
4. 원본을 RO 상태로 로컬 격리 workspace에 사본 수집; 민감 파일 패턴과 secret 탐지·redaction; ZIP 폭탄/경로탈출/심볼릭링크·하드링크/대용량·파일 교체를 거부한다.
5. **정적 검사**: Code Checker의 실제 지원된 Python AST/제한된 generic 룰, 구문·예외·입력검증·프론트 정적 위험. Unsupported 언어 또는 제외 파일 `PARTIAL`.
6. **구조 분석**: 별도 Graphify 격리 설치/실행 후 import/call/SQL 관계 그래프·source line provenance. 코드 가시성 없는 node는 unknown. 변경으로 영향받는 호출 경로/중요 모듈 목록 제시.
7. **브라우저 동작 검증**: 승인된 staging에 agent-browser/Playwright를 쓰되 읽기/허가된 synthetic 쓰기만. 홈→폼→리스트→상세→저장/다시 열기→실제 backend GET/POST 결과까지 검증; UI에 뜬다고 DB에 저장된 것으로 단정 금지.
8. **보안 감사**: Cloudflare 방식의 architecture→coverage ledger→candidate findings→fresh verifier→confirmed/needs_validation/rejected→report schema 검증. 소스 근거가 없으면 위험도를 매기지 않는 `needs_validation`.
9. 교차 연결: Graphify 호출 그래프의 코드 위치와 Code Checker 의심 줄·브라우저 실제 오류를 동일 trace ID로 잇는다. 단순 정적 경고와 실제 영향이 증명된 결함을 분리한다.
10. 고객의 승인된 테스트 범위에 대한 **컴포넌트별 Coverage**를 계산: 적용/미지원/건너뜀/검증된/실패, 언어·파일·라우트·기능별. 퍼센트가 미검증 영역을 숨기지 않게 명시한다.
11. Findings 분류·우선순위: `severity = 영향 × 전제조건/가능성`을 검증된 위협모델에만 부여; 비즈니스 손실 추정은 시나리오 가설과 실측 분리. 각 항목에 최소 수정안·재검증 자동/수동 항목 포함.
12. 보고서 작성: 고객용 요약·우선 수정 TOP10·기능/보안/구조 구획·스크린샷/콘솔·파일 줄 근거·테스트 결과와 증거 해시/미검증, 마크다운/HTML/PDF·고정 ZIP.
13. 고객이 패치한 **새 SHA**를 제공하면 원본/패치본의 동작·그래프·finding 재검증. 기존 결함이 개선됐는지 실측하지 않으면 `FIX_UNVERIFIED`; 자동 변경/원본 덮어쓰기 금지.
14. 최종 인수: 프로젝트/시나리오/보고서 SHA 및 timestamp 일치, 고객 서면 인수·보유기간/삭제, 빌드·배포형태/소스 권리 확인, 지원 종료일·재검수 조건 고정.

## 4. 최종 전체 아키텍처
```text
Client-owned project ZIP/repo snapshot + authorized staging URL + test account
  │ contract/rights, scope, auth, budget, no external upload default
  ▼
Evidence Intake Gate
  ├─ Safe Reader: bound files/bytes, ZIP bomb/link/path deny, secret filter
  ├─ SHA256 source snapshot + client approved test plan + consent receipt
  └─ Immutable Case Workspace ID (separate input/evidence/output)
       │
       ├────> AI Code Checker static analyzer
       │         AST Python + limited generic rules + local report metadata
       │
       ├────> Graphify isolated CLI (optional) 
       │         verified AST/code/SQL graph, line-linked edges, impact paths
       │
       ├────> agent-browser isolated session / Playwright fallback
       │         approved actions ONLY; DOM/UI + Console+Network+API snapshot
       │
       └────> Cloudflare security-audit method workflow
                 architecture ledger → coverage → candidate → independent verifier
       │
       ▼
Evidence Normalizer / Correlation
  ├─ finding fingerprint, true source line, screenshot/trace refs, SHA
  ├─ statuses CONFIRMED / NEEDS_VALIDATION / REJECTED / NOT_COVERED
  ├─ independent contradiction / spoofed evidence / coverage validation
  └─ risk priority, customer acceptance checklist
       │
       ▼
Report Composer + Independent Delivery Verifier
  ├─ HTML + JSON + PDF via tested browser + Markdown
  ├─ scope/coverage/findings/reproductions/fix priority/missing proof
  └─ deterministic ZIP/manifest/SHA + separate read-only verifier
       │
       ▼
Human reviewer + customer acceptance/repair recheck → RELEASE/RELEASE HOLD
```

## 5. 도메인 모듈 정의
### 5.1 `case_intake` · `scope_policy` · `subject_integrity`
- 재현 가능한 `case_id`, customer consent hash, input source ID, accepted languages/files, targets and auth method, resource budgets, PII class, allowed export destinations.
- 파일 이중 해시/크기·manifest 확인, Git checkout/ZIP 외부 파이프·symlink·숨은 자격증명/대용량·서브모듈/심볼릭 링크 처리. 원본에 execute permission이 있어도 기본 실행하지 않음.
- repo clone/외부 URL 요청도 허가된 소유권과 allowlist/보안 승인 없으면 거부.

### 5.2 `static_adapter`
- 기존 `offline_core.py`, `offline_report.py`, `desktop_ui.py`를 별도 subprocess/lib adapter로 감싸 입력 오류·부분 성공·한도/특정 언어 빈 rule 탐지.
- findings JSON은 `rule_id, source_path_token, line, detector, confidence_kind, raw_impact, redacted_excerpt_sha`. 파일 경로/코드 발췌를 고객/이 저장소로 무단 복제하지 않음.
- 기존 Gemini v1 CLI는 optional remote: 고객 명시 권리·유료 API 약관/저장·PII 검토, 월 budget 승인 전 기본 OFF.

### 5.3 `graph_adapter`
- Graphify 공식 배포 버전/pinned SHA, CLI capability handshake, local-only/no cloud/no optional LLM by default; parser 지원 언어/사용한 데이터 종류/AST 추출 vs inferred 엣지 구분.
- 관계 목록 `node_kind, symbol, file_path_token, line_span, edge_kind, evidence_ref, extractor_version`. 임의 그래프를 실제 보안취약점/런타임 호출 보장으로 해석하지 않음.
- code-checker finding에서 함수/모듈 호출 경로를 추적해 **변경 영향·납품 리스크 보고**로 활용. Graphify 미설치면 static+browser 독립 경로로 degraded.

### 5.4 `browser_runner`
- 사이트 관찰은 `https://` staging/test origin으로 제한, local synthetic fixture는 별도 허용. private IP·internal admin/metadata·redirect chain 검증, 브라우저 요청/폼 송신/파일 다운로드 금지/허용 분리.
- agent-browser의 snapshot → ref 클릭 → snapshot diff에서 실제 보이는 활성/비활성·미인증 화면 검증. 동적 DOM 이후 ref 재사용 금지.
- 실제 browser Console/Network 기록, API 응답 읽기/오류/성능, 시각 screenshot/dimensions, headed Windows smoke. OTP/결제/삭제는 자동화하지 않음.
- 로그에서 session cookies/Authorization/header/HTML 내 PII redaction, 테스트 종료 후 임시 프로필 삭제.

### 5.5 `audit_engine` · `finding_validator`
- Cloudflare Skill의 6단계 구조: architecture/coverage-led hunt/candidate validation/structured output/independent verification/target-neutral report. 실제 Skill 별도 실행은 OS sandbox/다중 독립 reviewer 자원 확보와 라이선스 검토 후만.
- 독립 verifier에게 탐지기 결론이 아닌 immutable evidence + 재현 절차를 제공하여 **반증**. 재현 안 되면 `NEEDS_VALIDATION`, 설명만 허술하면 `REJECTED`.
- coverage 분모는 **검수 계획에 포함된 로직/테스트 케이스**를 사용; 검사 지원 제외된 모듈을 커버됐다고 허위 체크하지 않음.

### 5.6 `report_assembler` · `delivery_gate`
- 보고서에는 정확 test SHA, source digest, 브라우저/OS/버전, 검사 항목·검사 제외, findings evidence ID, 임팩트·수정 우선순위·근거와 고객 검수 결과.
- 고객 제공 소스는 납품 ZIP 안에 자동 동봉하지 않음. 민감 screenshot/trace는 별도 고객 보안 보관처에 두고 보고서엔 승인된 참조/요약만.
- ZIP은 새 폴더 create-only/atomic publish, 독립 verifier로 manifest/SHA/JSON schema/HTML escape/출처 서술 일치 검증; overwrite/복구 실패 시 HOLD.

## 6. 계약의 구조 (예시이며 실제 코드 스키마 미구현)
```json
{
 "contract":"proofqa.case.v1", "case_id":"case-example",
 "subject":{"repo_commit":"<sha40>","source_sha256":"<sha256>","classification":"confidential"},
 "approval":{"scope_digest":"<sha256>","actor_id":null,"state":"PENDING"},
 "tools":{"code_checker":"pinned","graphify":"OPTIONAL","agent_browser":"OPTIONAL"},
 "coverage":{"planned":12,"completed":0,"not_covered":0},
 "findings":[{"id":"PQ-001","status":"NEEDS_VALIDATION","category":"functional",
    "evidence_refs":[],"severity":null,"reproduction":null}],
 "delivery":{"verified":false,"release_state":"HOLD"}
}
```
- 실제 json schema를 `schema_version`과 함께 테스트·이행. 임의 승인 필드를 외부 파일이 추가해도 승인 권한을 획득하지 않도록 프로세스 외부 신뢰된 ledger 필요.

## 7. 실패·재시도·비용 관리
- 스테이징 불가/로그인 만료 → retry policy bounded 1회, 여전히 실패면 해당 케이스 `NOT_RUN`; 웹사이트 장애로 단정 금지.
- Graphify 파서 충돌/메모리 폭주 → 실행 격리 및 timeout/CPU/RAM 한도, 실패 evidence 로그; 그래프 누락 영역을 위험 없음으로 간주 금지.
- Browser 클릭 재시도 → 액션이 데이터 쓰기/주문/결제를 유발할 가능성이 있으면 자동 재클릭 금지; 실행 전후 상태 확인.
- AI 호출 429/비용 초과 → 중단/로컬 정적 분석 유지, 외부 종량제 상한 준수.
- 중복 `case_id` 또는 같은 파일/다른 버전 병렬 결과 → 고유 case+SHA 분리, 파일 경합/쓰기 원자성, 이전 보고서 덮어쓰기 금지.
- 이미지/PDF 표 등 산출물 생성 실패 → 보고서 배포 차단하고 원본 검사 기록 보존; HTML 생성 SUCCESS가 PDF 검증 SUCCESS를 의미하지 않음.

## 8. 보안·정책·고객 개인정보
- 기본 로컬·오프라인 소스 분석, 고객 계정/비밀번호/토큰 입력은 공급사 외부 전송하지 않고 테스트 계정은 고객이 직접 제공/관리.
- 샌드박스 없는 상태에서 임의 고객 바이너리/빌드 스크립트/테스트코드 실행 절대 금지. 디폴트 읽기 전용 스캔. 컨테이너 격리만으로 충분하다는 보장 금지; 호스트 네트워크·파일시스템 강제 격리 필요.
- 스크린샷에서 주문자 정보/개인정보 보이면 차단·가림·즉시 처리, 고객 비밀값을 GitHub issue/PR/LLM으로 전송 금지.
- 민감 소스·패턴/보안 결함 보고는 고객 승인된 수신자에게만, 내부 공유 링크 ACL 확인. 사건대응/SOC·침해사고 직접 조사 기본 제외.

## 9. 100% 출시/납품 수용
- 기존 Code Checker 전체 CI/원본 EXE 권리 검수, Graphify+browser actual pinned adapter, 승인형 샌드박스, 독립 finding verifier, 대상 언어/사이트 실제 인수와 **Win10/11 실 PC 설치**, 고객형 납품·재검수/원복, LICENSE/NOTICE, 결제증빙 지원 범위 전부 PASS.
- 판매 가능한 기능은 실제 `supported_features.json`으로 고정, 미완 통합 Graphify/보안/브라우저를 상세페이지에 기구현이라고 광고 금지.
- 100점 수용표는 [ACCEPTANCE_AND_ROADMAP](ACCEPTANCE_AND_ROADMAP.md) 우선. 현재 0점 '개발 미착수'는 신규 조합의 상태이며 기존 Code Checker 완성률을 0으로 바꾸는 뜻이 아니다.
