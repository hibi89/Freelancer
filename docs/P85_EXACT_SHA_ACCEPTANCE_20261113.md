# PROOFQA AX P85 — 정확 SHA·실도구·독립 코드 검증 증거

**기준일:** 2026-11-13 KST  
**원본 정본:** `hibi89/Freelancer@product/proofqa-ax-delivery-audit/docs/FINAL_BLUEPRINT.md`, `docs/ACCEPTANCE_AND_ROADMAP.md`  
**판정:** 최종설계에서 정한 **P85 내부 합성/개발 기술 게이트 검증 성공**. 전체 100점 대비 공식 최종상품 완성률 **`UNASSESSED`**. 고객 실사·보안 인증·독립 인간/에이전트 검증·상용 출시 아님. `RELEASE HOLD / SALE NO-GO / [작업중] 유지`.

## 증거 표 (기능 정확 SHA 기준)

| 항목 | 사실 |
|---|---|
| 원본/백업 | `hibi89/ai-code-checker@feature/proofqa-ax-p70-graph-browser`, SHA `1c4e9b629476ac9ac76b40a207f25408b2002a18` |
| P85 구현 | `hibi89/ai-code-checker@feature/proofqa-ax-p85-independent-audit`, **`5bce80a870d46702eb1ef5a51faa7cae54755691`** |
| [P85 전용 Actions #43383627492](https://github.com/hibi89/ai-code-checker/actions/runs/43383627492) | **3/3 jobs completed/success**: Ubuntu 24·Windows2025 Python3.13 각각 **31/31 PASS, 0 SKIP**; 별도 Ubuntu Real Graphify+agent-browser+PDF/HTML/JSON 독립 프로세스·PDF raster 실제 검증 성공 |
| [Code Checker 전체 Actions #43383627563](https://github.com/hibi89/ai-code-checker/actions/runs/43383627563) | **16/16 jobs completed/success**, Ubuntu24/26·Windows2025 × Py3.11~3.15 + 의존성 감사. P85 전용 31개는 기존 `test_*.py` 검색에서 별도 분리하여 전용 Actions에서 **실제로** 검증함 |
| [전체 최종설계 정책 게이트 #43383627881](https://github.com/hibi89/ai-code-checker/actions/runs/43383627881) | completed/success. 100% 완성 인증이 아니라 정책·형식 게이트 |
| [Draft PR #85](https://github.com/hibi89/ai-code-checker/pull/85) | P70 기준, 미병합, 기존 상업 main/Code Checker 엔진 변경 없음 |

## P85 추가 소스

- `proofqa_p85.py`: Cloudflare security-audit-skill의 **6단계 방법론만** 참조. `reconnaissance` → `coverage_led_hunting` → `candidate_validation` → `structured_output` → `independent_record_verification` → `target_neutral_reporting` 각 상태 추적 및 누락 구분. P70 실제 Graphify AST/브라우저 합성 증거만을 입력으로 받아 `audit.json`, `coverage-ledger.json`, `findings.json`, `report.json`, `report.html`, `report.pdf`, `manifest.json`을 로컬 create-only로 생성. PDF는 `reportlab==4.4.5` 이용.
- `proofqa_p85_verify.py`: 생성기 **미임포트** 별도 읽기전용 구현. 독립 OS 프로세스로 실행하여 매니페스트 SHA256, 동일 source digest, finding fingerprint+증거참조, `planned=completed+not_covered`, `CONFIRMED/NEEDS_VALIDATION/REJECTED/NOT_COVERED` 및 severity 제약, HTML CSP/escaping, 실제 PDF `pypdf==6.2.0` 본문 추출과 report JSON 동일 canonical text, `jsonschema==4.25.1` schema 검증. 계약 불일치면 배포 불가.
- `schemas/proofqa_p85_report.schema.json`: `run_status=incomplete`, `release_state=HOLD`, `customer_accepted=false`, `security_certification=false`와 허용 필드의 엄격 JSON Schema.
- `tests/p85_adversarial_cases.py`: **31건** (정상 수용 1 + 서로 다른 변조/허위 확정/원본 SHA 위장/결과 불일치/추가 파일·심볼릭 링크 등 fail-closed 부정 30). 이 30건은 **실고객 위협모델 30항 전체 실증이 아님**, 별개로 P95에서 30항 검수 필요.
- `scripts/proofqa_p85_acceptance.py`: P70 원래 실 Graphify/Chromium 합성 fixture를 **실제로 재실행** → P85 보고서 → 외부 프로세스 `python -m proofqa_p85_verify` → read-only 동등 결과 확인 → `pymupdf==1.26.3` 실제 PDF 893×1263 raster 생성. 사용자·고객 원본 입력 금지.
- `.github/workflows/proofqa-p85-audit.yml`: exact 도구 고정, 3개 job, GitHub 권한 `contents:read`, CI 실행결과만 출력, 고객·비밀 파일 업로드 없음.

## 실제 CI 확인 내용

- Graphify `graphifyy[sql]==0.9.108`: Python AST 3 · JS AST 3 · SQL AST 2개의 합성 위치 노드.
- Code Checker 정적 후보 2건 → Graphify 구조 관계 2건 (실제 source file 범위 `FILE_SCOPE_APPROXIMATE`, 보안 취약점/동적 코드 호출 확정 아님).
- 실제 Chromium via `agent-browser@0.43.0`: `127.0.0.1`의 합성 사이트 snapshot/버튼/폼/저장/새로고침/조회. 서버 관찰 `GET /api/ok:200`, `GET /api/fail:500`, `POST /api/save:200`, `GET /api/reopen:200` 일치.
- 14개 합성 범위 검수 ledger: **8 `COMPLETED`, 6 `NOT_COVERED`**. 코드 보안 후보 **2 `NEEDS_VALIDATION`, 0 `CONFIRMED`**, 심각도 모두 `null`. `run_status=incomplete`, `release_state=HOLD`.
- 1쪽 PDF 실제 pypdf parser+source-report canonical lines 일치, 별도 PyMuPDF 893×1263 픽셀 렌더 성공. **인간 시각검수는 NOT_RUN**. 한글 PDF 글꼴 사용자 기기 완벽 렌더링은 보장하지 않음.
- Ubuntu/Windows Python3.13 각각 P85 전용 **31/31 PASS/0 FAIL/0 SKIP**, 기존 P50+P70의 **17/17 PASS**. `pip check` PASS.
- 기존 16매트릭스 CI **16/16 SUCCESS**. 기존 Code Checker core/원본 상업 브랜치 및 main 무변경.

## Cloudflare 방법론 반영과 실제 미실행의 경계

참고: [cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill), 공개 README와 6단계. **Skill 실행/클론·Cloudflare 운영 인프라/보안 인증/실 독립 감사 수행이 아님**. P85의 `independent`는 **별도 코드·별도 프로세스가 동일 기록의 기계적 정합성을 재검증**한다는 뜻. 코드와 데이터 둘 다 허위인 경우 실제 고객 소스·Graphify 원본·네트워크를 완전히 독립 재실측한 것이 아니며, 위협 탐지·허위양성에 대한 **fresh independent human/agent verifier는 NOT_RUN**. 따라서 계약은 `incomplete`로 지속.

## 오류·원인·수정 및 재실행 경계

- 첫 P85 CI에서 Unix `list(tuple)`와 Python 실제 P70 브라우저 원시 `tuple` HTTP 이벤트의 표기 차이로 검증기 차단; 숫자·주소 자체 오류는 없었음. P85 수신단에서 각각 명시적으로 3항 tuple/list인지 확인한 뒤 **동일한 list 표현으로 정규화**, 나머지 allowlist/HTTP 값의 정확 매칭 유지. 최초 실패 이력 보존. 수정 SHA `5bce80a870d46702eb1ef5a51faa7cae54755691`의 실제 P85 + 전체 CI + 정책 게이트 전부 SUCCESS.
- 운영코드 고객 입력 불허·OS 수준 sandbox 미구현. Cloudflare 방법론 독립 에이전트실행/고객-실서비스/Windows10·11/실브라우저 Chrome·Edge/인수 법률/라이선스·NOTICE/외부 네트워크 차단·PDF 사람 렌더 검수는 미검증. P95 또는 상용 출하 승인 이전에 제공되었다고 주장 금지.
- P85 디렉터리는 create-only·SHA 검증. 크래시 발생 시 부분 폴더를 남길 수 있으며 자동 롤백·atomic publish를 보장하지 않음. 분리된 상용 delivery ZIP 및 고객 서면 인수는 P95~P100에서 구현/검증해야 함.

## P95 / P100 다음 절차

1. 대상 30위협 항목의 실제 실행/차단 증거·권한/고객 범위·Graphify 원시 그래프 포함한 독립 source replay 및 OS enforced egress/filesystem sandbox 설계·검증; 허가 없는 고객 코드 실행/네트워크 접근 없음.
2. 고객의 소규모 실제 repo+staging 두 사례 이상 사용권/테스트 범위 승인 후 점검; Windows10·11 Chrome·Edge 설치/폴더/SmartScreen/접근 통제, 외부 라이선스·NOTICE 및 원본 대조. **승인 전 중단**.
3. P100은 사용자/고객 서면인수, 원본·수정본 재검증, 완전 납품 ZIP과 독립 고객 검증/지원/판매 GO. 현재 `UNASSESSED`·`[작업중]`·`RELEASE HOLD` 유지. 변경 없는 기존 28개 제품 완성률·판매원장·작업중 마커 보존.

## 검증 재현

```bash
python -m unittest tests.p85_adversarial_cases -v
python -m unittest tests.test_proofqa_p50 tests.test_proofqa_p70 -v
python -m scripts.proofqa_p85_acceptance
```

첫 명령은 `reportlab==4.4.5` · `pypdf==6.2.0` · `jsonschema==4.25.1`을 요구; 마지막은 추가로 `graphifyy[sql]==0.9.108`, `agent-browser@0.43.0` 및 설치된 Chromium, `pymupdf==1.26.3` 필요. **반드시 합성 fixture만 사용**하며 원본/고객 소스 실행 금지.
