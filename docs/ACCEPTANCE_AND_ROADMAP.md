# PROOFQA AX 최종 개발 기준(50→70→85→95→100)
**가중 단계는 신규 '4기술 조합' 제품 기준. 현재 실제 코드 구현률을 인위적으로 0이라고 재기록하지 않으며, 설계 완료를 상용 100%라고 하지 않는다.**

| 누적 단계 | 제품 기능과 통과 검증 |
|---|---|
| 50 | Code Checker existing offline v2 adapter + 안전 ZIP/README/import + 한 프로젝트 static HTML/JSON source provenance; 합성 3종 부정 케이스; 개발용 isolated runner와 input digest |
| 70 | Graphify 진짜 pinned binary/CLI 실행으로 최소 Python/JS/SQL sample AST 그래프·file:line 검증; 2개 checker finding과 graph impact 연결; agent-browser 실제 로컬 합성 사이트 탐색/클릭/상태·HTTP 200/500; source+network security gates |
| 85 | Cloudflare 방식 architecture+coverage+candidate+independent verifier+schema; confirmed/needs_validation/rejected/NOT_COVERED; structured HTML/PDF/JSON 일치, 단일 Windows/Linux 내부 CI; 15개 adversarial 회귀 |
| 95 | CI 0 FAIL/0 unexplained SKIP, 모든 30개 위협모델 항목, 샌드박스에 실제 고객 **허가된** 작은 repo+스테이징 사이트 2종, Windows10/11 Chrome/Edge, 소스/EXE parity·보안/권리/NOTICE·임시 데이터 삭제·보고서 시각검수 |
| 100 | 완전 합의된 고객 검수서, 납품 ZIP 독립 검증, 고객 동의/리포트 발송·실제 지원/수정·가격·신고/증빙, 현장 사용자 인수, 상용 release 승인 |

## 필수 QA: 언어·환경·주장 구분
- 최소: Python AST 정적 지원, JavaScript 제한 패턴, Graphify 공식 지원언어의 샘플, SQL/프로젝트 문서 구조; 추가 언어는 지원근거 및 실제 fixture.
- 실제 브라우저: synthetic staging 3개+고객 허가 staging 2개, desktop/mobile·form/list/search/save/reopen, Console+Network, 1회 refresh, original site untouched.
- 결과 정합성: `n_findings = confirmed+needs_validation+rejected`, coverage planned/completed/not-covered, evidence IDs all resolvable, source commit exact.
- 비즈니스: 실패 보고→설정·원인·개선 한번만 재시도/stop-and-pivot, 고객 실 데이터 비용·고정 support.
- 차별성 지표(가설 검증): 기존 Code Checker alone vs combined 제품의 발견된 **확인된** 결함 수, false positive, 검수자 시간, 재현률, 고객 승인 성공률, 비용/프로젝트.
- 수용 기준 문서화: scan 결과에 `WARNING`이나 `PARTIAL`이 있는 경우 완전 검수 PASS 금지.

## 기존 기술·현재 시작점
- 해총 기존 Code Checker `95% 엔지니어링 잠정`, 실제 제품 판매 HOLD/원본 EXE 라이선스·고객 Windows/SmartScreen 미검증 기록.
- 외부 Graphify/agent-browser/Cloudflare skill 레포와 기능·공개 라이선스 확인. **PROOFQA 자체 adapter/통합 CI 0**, 상품 완성률 현재 `UNASSESSED`.
- HAE/REA의 Playwright 또는 보안모듈 코드 무단 복사·수익화 범위 합산 금지.
- 기본 제품 GitHub `ai-code-checker@feature/retail-private-candidate-20261112` 현재 조회 SHA `64744eebd109...`, 정확 후속 개발 시 HANDOFF→STATUS→원본 소스 확인.
