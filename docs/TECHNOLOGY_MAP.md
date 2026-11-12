# PROOFQA AX 전체 기술·라이선스/의존성 지도

| 레이어 | 사용 후보·버전 전략 | 책임 | 현재 검증 여부 |
|---|---|---|---|
| Base | Python 3.11+, AI Code Checker offline v2 | ZIP/folder/TXT 안전 읽기, Python AST/제한 generic 검사, 결과 상태 | 코드체커 기존 구현, 판매 EXE 출고 HOLD |
| Report | `offline_report.py`, Tkinter GUI, HTML/Markdown/PDF browser print | 한국어 보고서와 로컬 사용성 | 기존 개발자/CI 후보, 고객 Windows 미검증 |
| Graph | `Graphify-Labs/graphify` (공식 PyPI `graphifyy`) + tree-sitter, SQL/code AST | 노드/엣지/근거·의존성 그래프, change blast radius | 외부 프로젝트 존재 확인. PROOFQA adapter 미개발 |
| Browser | `vercel-labs/agent-browser`, Rust CLI/CDP/Chrome for Testing | 스테이징 사이트 참조 snapshot/작동 검증 | 외부 존재 확인. 통합·계정/Windows 미검증 |
| Browser QA backup | Playwright Chromium/Edge | 브라우저·Console/Network/스크린샷·실 UI E2E | PROOFQA 통합 미검증 |
| Security method | `cloudflare/security-audit-skill` 6 phase / schema validators | 구조·커버리지·탐색·독립 반증·검증 보고 | 실제 full audit 실행/격리 미구현 |
| Finding schema | JSON Schema / SHA256 manifest | 실행 환경·근거/범위/판정 일치 | 신규 계약 |
| Artifact builder | Python/PDF browser, HTML escaping, create-only ZIP | 고객 인수·재검수 결과 | 신규 조합 검증 필요 |
| Sandbox | OS-enforced network/file/process/memory/time isolation | 고객 악성 코드·비밀·권한 보호 | **미구현: 자동 임의 코드 실행 차단** |
| Optional AI | Gemini API (기존 v1) 또는 로컬 LLM | 요약·우선순위 초안 | 고객 데이터/상용 약관/비용 동의 후 옵션 |
| CI | Python unittest/pytest, Windows GitHub Actions, Browser smoke | source SHA ↔ 실행기/보고 일치 | 원본 일부 이력. 제품 통합 CI 없음 |
| Delivery | Windows portable EXE 후보 + source-bound reports | 설치/패킷/SmartScreen·NOTICE | 실 고객 Win10/11 미검증 |

## 외부 기술 공식 근거·정확 명명
1. Graphify: https://github.com/Graphify-Labs/graphify · 공식 패키지 `graphifyy`(오타 주의). tree-sitter 로컬 구조 그래프, optional Cloud/LLM은 기본 OFF. Apache-2.0 및 NOTICE/과거 MIT 문구 확인.
2. agent-browser: https://github.com/vercel-labs/agent-browser · Chrome for Testing install 필요, 페이지 snapshot+ref 기반 CLI. Apache-2.0. 지원 버전·Node/Rust/OS 패키지 런타임을 정확한 릴리스 SHA로 고정.
3. Cloudflare Security Audit Skill: https://github.com/cloudflare/security-audit-skill · MIT, 다단계 검증 프로토콜. 자동 취약점 확정/공식 Cloudflare 인증 아님. OS 강제 샌드박스 필수 요건을 충족할 수 없다면 풀오딧 미실행.
4. 기존 Code Checker: https://github.com/hibi89/ai-code-checker · `feature/retail-private-candidate-20261112@64744eebd109...`. 오프라인 v2와 Gemini v1 기술/개인정보·API 비용 경계를 엄격히 분리.

## 핵심 서비스 분리
- **Core scanner** = 우리가 개발·관리한 기존 정적 검사; **Graph module** = 구조 인지도 확장, 모든 언어 보안 감사가 아님; **Browser module** = 허가된 사이트 기능에 대한 동작 증거; **Security method** = 독립 검증과 불확실성 처리 절차.
- 고객마다 구조만 필요한 경우 Graphify는 optional이고 브라우저 없는 CLI 프로그램은 UI E2E를 강요하지 않는다. 검수 상품에서 미포함 모듈은 명시.
- 중간 CI와 PROOFQA 신규 CI는 서로 다른; 기존 95% CodeChecker ≠ PROOFQA 95% 상용 제품.

## 보안/비용 가정
- 로컬 Code Checker+Graphify에서 별도 AI 호출비 0 가능하나 브라우저/격리 워크스페이스 CPU·OS 디스크·서명/라이선스/지원 비용은 있음.
- agent-browser 자체도 로컬 브라우저 구동 및 약관 준수가 필요하며 테스트 URL·리다이렉트 SSRF/사내망/CI의 민감 로그에 주의.
- 고객 기업 리포지토리는 고객의 명시 허가/암호 처리 합의 없이 외부 Cloud Graphify/외부 LLM으로 전송하지 않는다.
- 공급사 라이선스·NOTICE/전이 의무는 상품 릴리스 시 고정된 **정확한 commit/release SHA**에 대해 최종 다시 검토한다.
