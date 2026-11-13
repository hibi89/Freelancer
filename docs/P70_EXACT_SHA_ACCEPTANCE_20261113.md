# PROOFQA AX — P70 실제 도구 수용 증거 (2026-11-13 KST)

> **판정:** 원래 최종설계 `docs/FINAL_BLUEPRINT.md`의 **P70 내부 기술 단계 핵심 항목 검증 완료**. 공식 최종상품 완성률은 `UNASSESSED`(사용자 승인 전체 100점 가중치·독립 실제 제품 인수 없음). `RELEASE HOLD/SALE NO-GO`, `[작업중]` 유지.

## 1. 정확 GitHub 증거

- 설계 정본: `hibi89/Freelancer@product/proofqa-ax-delivery-audit`, `docs/ACCEPTANCE_AND_ROADMAP.md`의 **P50/70/85/95/100 원본**. P70 범위 축소/변경 없음.
- 이전 P50 구현 정본: `hibi89/ai-code-checker@feature/proofqa-ax-p50-evidence-intake`, SHA `e2b79f6c242d3d501cc2195732196abe5d0bba91`; 기존 Code Checker 원본/상업 브랜치 및 main 무변경.
- 새 P70 기능 SHA: `hibi89/ai-code-checker@feature/proofqa-ax-p70-graph-browser` **`1c4e9b629476ac9ac76b40a207f25408b2002a18`**.
- [P70 실제 제3자 CLI/Chromium CI #43378766440](https://github.com/hibi89/ai-code-checker/actions/runs/43378766440): `completed/success`, exact code SHA 동일.
- [기존 전체 회귀 #43378766391](https://github.com/hibi89/ai-code-checker/actions/runs/43378766391): **16/16 job SUCCESS** (Ubuntu24/26 + Windows2025, Python3.11~3.15 테스트15 + dependency audit1), Linux/Win Python3.11 각 **520 tests PASS/0 FAIL** (PROOFQA P50 9 + P70 8 포함).
- [전체 최종설계 증거 정책 gate #43378766710](https://github.com/hibi89/ai-code-checker/actions/runs/43378766710): SUCCESS. 이는 최종설계 기능 100점 수용을 의미하지 않음.
- [검토용 Draft PR #84](https://github.com/hibi89/ai-code-checker/pull/84): P50 브랜치 대상으로 미병합. 원본/고객 프로젝트/권한·Production 설정 변경 없음.

## 2. P70 확인항목/미확인

| 원래 P70 수용 조건 | 실검증 결과 | 근거/해석 |
|---|---|---|
| Graphify 실제 pinned CLI 및 Python AST | **PASS** | `graphifyy[sql]==0.9.108` CI 설치; `graphify extract --code-only --no-cluster` 실제 실행. Python L위치 AST 노드 3개 |
| JS 및 SQL AST 및 file:line | **PASS(합성)** | JS L위치 노드 3개, SQL 노드 2개; 실제 `--no-cluster` 출력 `edges` 스키마를 맞춰 검사 |
| 기존 CodeChecker 정적 finding 2건↔Graphify 구조 영향 | **PASS(파일·함수 범위)** | 기존 `offline_core` 실제 분석 2건 → 그래프 소스 SHA/노드/EXTRACTED contains edge 연결 2/2. **`FILE_SCOPE_APPROXIMATE`**이며 런타임 영향/취약점 확인 아님; 확인된 보안 결함 0건 |
| agent-browser 실제 synthetic staging | **PASS** | `agent-browser@0.43.0` Chrome 설치/실 브라우저 snapshot·버튼 클릭·state 변경 |
| HTTP 200/500 및 저장→재조회 | **PASS** | 127.0.0.1 서버 실제 `GET /api/ok 200`, `GET /api/fail 500`, `POST /api/save 200`, 재시작 DOM 후 `GET /api/reopen 200`; 서버 관찰 결과와 화면 결과 교차 검증 |
| source / network security gates | **합성 범위 PASS / 고객 범위 미검증** | P50 ZIP 경로/압축폭탄/중복/링크·전후 SHA 확인. 합성 서버 127.0.0.1/허용된 경로만, CSP/Host 제한. **OS 강제 egress sandbox는 없음**, 고객 자료/실 URL 미실행 |

Graphify 그래프 SHA256 `63cf4e3370542ef352ea4edec365189c1f9dfcb01c9f09169103744cc3898f26`, 합성 ZIP SHA256 `84d6993f54906df72b1451d2f23e5906b0d4047067213da43c4b901f18e2ab93`; 해당 값은 CI ephemeral 합성 fixture 한정. `Graphify EXTRACTED` edge는 구조상 관계를 의미하며 실제 보안 사고/동적 호출 사실이 아님. CodeChecker의 JS/SQL 정적 scan은 부분 범위(`partial`)임을 숨기지 않음.

## 3. 설계 비교·비용/유지보수

- A안: 외부 Graphify/브라우저를 고객 ZIP·실사이트에 바로 결합해 자동 실행. 겉보기 처리량은 높으나 OS 격리·권한·공급망/실사이트 부작용/법적 비용 위험 높음. **P70에서는 기각**.
- B안(**채택**): 원본 Code Checker/P50 분리 유지 + 버전 고정 CLI를 일회성 합성 프로젝트에서만 실제 실행 + 정적 후보를 그래프에 근거/불확실성 명시해 연결 + localhost 전용 실제 브라우저 검증. GitHub Actions 무료 범위 내 검사, 실 외부 AI API 0, 모듈 교체·회귀 비교 용이.
- C안: AST/DOM을 Mock만으로 시험. 설치/속도는 유리하지만 `실제 Graphify + 실브라우저` 수용 기준 위반으로 기각.

## 4. 소스 위치·재실행

- 구조/상관관계 `proofqa_p70.py`; Graphify 실제 `scripts/proofqa_p70_graph_acceptance.py`; 브라우저 실제 `scripts/proofqa_p70_browser_acceptance.py`; 합성 단위 `tests/test_proofqa_p70.py`; 신규 Actions `.github/workflows/proofqa-p70-live.yml`.
- 테스트: `python -m unittest tests.test_proofqa_p70 tests.test_proofqa_p50 -v` → 17건. 실제 호스팅 CI는 Python3.13에 `graphifyy[sql]==0.9.108`, `agent-browser@0.43.0` 설치 후 두 `python -m scripts.proofqa_p70_*_acceptance` 호출.
- CLI는 사용자 소스 스캔/브라우저 실제 고객 URL 자동 전송을 **하지 않으며**, 제3자 프로그램/소스 자체를 GitHub에 복사하지 않음.
- 실험 실패와 수정: 첫 CI Python 모듈 경로 오류 → `python -m` 실행으로 수정. 다음 CI Graphify의 `--no-cluster`가 `links`가 아닌 `edges`를 제공함을 발견 → **기존 `links`와 실제 `edges` 양쪽 검증**으로 보강. 최종 exact SHA CI에서 Graphify·브라우저·기존 회귀 성공.

## 5. P85 이후 우선순위·판매 보류

- P85 Cloudflare 방식 6단계 coverage-led 감사, 독립 반증 검증, CONFIRMED/NEEDS_VALIDATION/REJECTED/NOT_COVERED 별도 상태, PDF/HTML/JSON 일관성, 총 15개 공격 회귀(실 모델/독립 evaluator 필요).
- P95 실제 고객 권리 확보 작은 repo+사이트 2개, OS 강제 격리와 network deny, Windows10/11 실 PC/Chrome·Edge, 30 위협 모델 전체와 라이선스·NOTICE/진짜 고객 QA.
- P100 고객 서명 인수·완전한 납품 ZIP 독립 검사·상용 권리/가격/지원/승인. 위 증거 전까지 **공식 최종상품률 UNASSESSED 및 PROOFQA [작업중], RELEASE HOLD 유지**.
