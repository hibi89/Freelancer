# AZENTFLOW AX — 50→70 기술 수용 증빙 (2026-11-13 KST)

**상태: 70% 단계의 합성 기술 수용시험 PASS / 공식 최종완성률 UNASSESSED / RELEASE HOLD / 크몽 미등록.** 이 문서는 최종 100% 기준의 분모나 승인 가중치를 변경하지 않는다. 고객 설치, 보안감사 및 상용 제품 70% 완료를 보장하지 않는다.

## 1. 기준·정확 코드·CI
- 정본: [최종설계](FINAL_BLUEPRINT.md), [누적 50/70/85/95/100 수용 조건](ACCEPTANCE_AND_ROADMAP.md). 70 기준: LA 독립 실행·재시작, 중복 및 digest 차단, 로컬 UI preview, 서로 다른 2개 업무 workflow, 무승인 write 0, 경합·속도 한계.
- HAE 원본 / **실제 테스트된 기능 SHA**: `hibi89/HAE@feature/axflow-mvp` `12987055802c1e2e3dbf7eb5c5820382a52daef4`.
- LA 독립 코드 ref: `hibi89/HAE@feature/lightning-azent`, 2026-11-13 확인 HEAD `36f9882eb50e0de9e85eedb320a5778c8321cda5`. 워크플로의 checkout은 `ref: feature/lightning-azent`이며 SHA를 CI에서 assert하지 않았으므로 불변 pin된 패키지 검증이라고 주장하지 않는다.
- 신규 수용시험 `apps/ax-flow/tests/test_azentflow_p70_acceptance.py` (7개). P50 `test_azentflow_p50_acceptance.py` (3개) 보존.
- [GitHub Actions run #43377368138](https://github.com/hibi89/HAE/actions/runs/43377368138), GitHub-hosted Python3.11 + Node22, Windows/Ubuntu 모두 완료. **P70 신규 각 OS 7/7 PASS, 0 FAIL/0 SKIP. P50 각 3/3 PASS.**
- OS별 기존 HTTP smoke 6/6 PASS, 독립 HAE↔LA adapter 5/5 PASS, Node UI race 24 PASS. Python full suite **각 283 실행 = 274 PASS / 2 FAIL / 7 SKIP**, workflow 결론은 **FAILURE**. 기존 배송 아티팩트 두 건 불일치만 FAIL; 신규 P70/P50 테스트 실패 없음.
- 첫 P70 테스트 커밋 `4d7c824a6a528ff0be44e02234f81503b1c13d60`에서 1개 테스트가 지원되지 않는 유효하지 않은 변경 요청으로 HTTP 422를 받아 의도한 해시 충돌 409에 도달하지 못함. **테스트 입력만** 유효한 read-only 변경 계획으로 조정한 `12987055...`에서 양 OS P70 7/7 PASS. 운영 소스 변경 없음.

## 2. 사용자 70 기술 수용 항목별 실증

| 요구 | 실제 검사 | 판정 및 범위 |
|---|---|---|
| 독립 LA 실행 | HAE가 만든 `axflow.ir.v0`를 별도 Python **자식 프로세스**의 `python -m lightning_azent run`으로 실행; 무승인 return 2, 승인 실행 2행, 다시 `status`, `resume`, 최종 행 2건 유지 | **PASS**, 동일 머신 별도 프로세스; GUI와 LA 서비스 물리 분리 상용 패키지 아님 |
| LA 재시작과 이력 | HAE localhost UI 서버 종료·신규 서버 기동 후 LA durable SQLite `/api/status`, `/api/la-audit`로 완료/해시/승인 증거 확인, 실제 행 유지 | **PASS**, 실제 OS reboot/kill -9 장애 복구는 미검증 |
| 중복과 소스/계획 digest | 동일 승인 token 동시 HTTP 요청 2개 → 같은 `run_id`, 두 결과 완료, 사업 DB 2행 유지; 다른 작업/변경 CSV는 409와 DB 무생성 | **PASS**, 로컬 SQLite idempotence만, 원격 API exactly-once 불보장 |
| 로컬 UI preview | 127.0.0.1에 실제 HTML 및 JS 자산 배포, preview/run 버튼과 API 경로 확인, preview 2회/명시 승인 후 쓰기 | **PASS**, Python HTTP + Node24 모의 DOM 검증. 실제 Chrome/Edge 사용자 클릭은 아직 미검증 |
| 지원된 서로 다른 업무 2개 | ① 고객 CSV 2행 전체 import; ② 한국어 조건부 매출 threshold CSV(3행 중 2행만 import)로 LA 별도 multi-step/branch 계획 수행; 각 run_id 독립, 총 4행 | **PASS** (합성), Google/ERP 고객 실제 업무 미검증 |
| 승인 없는 쓰기 0 | preview 시 두 SQLite 없음, 미승인 import=HTTP403, 다른 plan/stale input=HTTP409, SQLite 계속 미생성 | **PASS**, 고객 계정·서명·권한 경계 실검증 아님 |
| 경합·속도/입력 상한 | 동시 2요청을 ThreadPool로 시험해 행 중복 0, 요청 pair 20초 상한; 과대 CSV(~280KiB) preview 안전 거부 및 20초 상한·DB 미생성 | **PASS** 호스티드 CI 기능 회귀·상한, TPS/latency/SLA·부하 테스트 아님 |
| 실패 복구 승인 | fixture에서 **상태만 failed로 주입**한 뒤 UI 서버 재기동, 변경된 계획 409, 승인 없는 재개 403, 명시 승인 재개 200 및 사업 데이터 중복 0 | **PASS** *합성 상태주입*; 프로세스 강제중단 복구는 별도 필요 |

## 3. 원본·CI 차단·비용·보안
- HAE 기존 실행 모듈, LA 엔진, 고객 원본·DB·키·권한·Vercel 설정, 출고 ZIP/pyz 변경 **0**. 오직 신규 테스트 파일 + 수정 테스트 입력 + STATUS/HANDOFF/본 근거 문서.
- 현재 full-suite 2 FAIL: `test_shipped_package.test_checked_in_zipapp_matches_current_hae_and_staged_la_sources`, `test_release_zip_matches_shipped_sources_and_executes_real_la_e2e`. `hae-integrated.pyz` 및 `HAE-Windows-offline.zip`의 내용과 현행 원본 소스가 불일치하며, 이전 P50에서 기록된 동일한 차단이다. 원본 백업 후 rebuild/비교/실 OS 설치 검증 전 CI GREEN·출시 성공 주장 금지. **현재의 70기술 구간은 전체 CI GREEN이 수용 조건이 아니며 95 구간에서 필수.**
- 비용: 외부 LLM·Google API·SaaS 호출 0, 합성 로컬 임시 SQLite만 사용. 테스트는 GitHub Actions hosted runner에서 수행했으며, 조직 CI 비용/할당 청구 상태는 별도 미조회.

## 4. 아키텍처 선택
- A: Freelancer 브랜치에 HAE/LA를 복사하여 독립 배포 — 초기 실행은 단순해도 원본과 CVE/패키지 drift 및 관리 비용 2중화.
- B(**채택**): 원본 HAE 개발 브랜치에 독립 LA를 stage하고 HAE preview 승인 계약/LA CLI·SQLite E2E에 전용 증빙만 추가 — 공개 SaaS 비용 0, 실제 공통 코드 회귀, 원본 기존 기능 유지. LA SHA pin과 배포물 parity는 후속.

## 5. 판정·인수·다음 작업
- **검증된 사실:** 50→70 기술 수용 요건 중 합성 업무/재시작 상태조회/동시성/로컬 UI 자산/제한·승인 흐름이 Windows + Ubuntu에서 실 통과. 이는 단계 게이트 결과이며 최종 전체 제품 70% 공식 점수와 다르다.
- **공식 최종완성률:** `UNASSESSED` (사용자 확정 100% 최종설계 항목 전체 구현/가중치 및 독립 인수 검증 미완). 중앙 `[작업중]` 유지, `RELEASE HOLD` 유지.
- **70→85:** 3개 합성 업무 경로와 실 DBVORA 프로토콜 mock, 감사/영수증, 스케줄 제한형, 양 OS CI 증거 확대. **85→95:** full suite 0 FAIL/ZIP parity/실 DBVORA·OAuth 조건부/실 Win10/11 설치·복구·고객 UI.
- **다음 선택:** 원본 배송물은 기존 ZIP/pyz 원본 백업+hash 검수 후 별도 승인에 따라 안전하게 재생성. LA를 정확 Git SHA pin 검증. 외부 자료·실 고객·요금·권한 변경은 재승인.
- **재현 명령:** `cd apps/ax-flow && python -m unittest discover -s tests -p test_azentflow_p70_acceptance.py -v` (별도 LA package를 repo `packages/lightning-azent`에 staged). 모든 테스트: `python -m unittest discover -s tests -v`.
- **갱신:** 2026-11-13 약 15:19 KST. 증빙 대상 GitHub Actions #43377368138, 기능 SHA `12987055...`; 고객 Production/Vercel **미적용**.
