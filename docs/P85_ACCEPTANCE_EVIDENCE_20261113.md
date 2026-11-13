# AZENTFLOW AX — 70→85 합성 기술 수용 기록 (2026-11-13 KST)

## 판정 기준
- **70→85 내부 기술 수용 게이트**: 합성 업무 3개 실 실행 + 독립 DBVORA HTTP 계약 mock + 감사·승인 영수증 + 제한형 LA 스케줄러 + 실제 Windows/Linux CI 결과.
- **공식 사용자 최종설계 100% 분모:** 변경 없음. **공식 최종완성률 UNASSESSED**; 85% 기술 단계 충족은 상용 완성률 85%·출시 승인·실 고객 3업무 통합을 뜻하지 않는다.
- **크몽 상태:** `AZENTFLOW AX [작업중]`, `RELEASE HOLD`, 미등록 계속 유지.

## GitHub 기능 근거와 소스 경계
| 항목 | 확인 |
|---|---|
| HAE 기능/시험 실제 commit | `hibi89/HAE@feature/axflow-mvp`, `a640666db7a1bf2011c5d2abc944f13199ce455f` |
| 독립 Lightning Azent | `hibi89/HAE@feature/lightning-azent` 조회 SHA `36f9882eb50e0de9e85eedb320a5778c8321cda5`. GitHub CI에서는 이동 가능한 branch checkout; 해당 개별 CI 작업 checkout SHA를 고정 assert한 것은 아님 |
| 신규 테스트 | `apps/ax-flow/tests/test_azentflow_p85_acceptance.py`, unittest 7개 |
| 실 CI | [GitHub Actions #43382552489](https://github.com/hibi89/HAE/actions/runs/43382552489), 기능 SHA `a640666d...` |
| Ubuntu | **신규 P85 7/7 PASS**. Python 총 290건: 281 PASS / 2 FAIL / 7 SKIP. 전체 CI FAILURE(기존 배송물 정합성) |
| Windows | **신규 P85 7/7 PASS**. Python 총 290건: 281 PASS / 2 FAIL / 7 SKIP. 전체 CI FAILURE(기존 배송물 정합성) |
| 구간 P50/P70 | 기존 두 단계 3 + 7 시험은 별도로 유지. P85의 추가 7 시험은 고객형/물리 환경 출시 검증을 대신하지 않는다 |
| Node UI | 기존 모의 DOM race 회귀 Ubuntu·Windows 각 24 PASS. 실제 Chrome/Edge 고객 UAT는 별도 미검증 |

## 구현/수용 항목별 실제 경로
1. **세 업무:** 합성 고객 CSV 2행 전체 가져오기(`csv_to_sqlite`), 합성 매출 CSV 3행 중 2행 금액 기준 조건부 저장(`csv_conditional_import`), 고객 ID 조회 1행만 반환하는 읽기 전용 검색(`csv_lookup`)을 같은 localhost HAE UI→독립 LA 실행 경로에서 분리된 run_id로 완료. 저장 DB의 고객·매출 각 2건, 조회는 비즈니스 DB 쓰기 0건. 계획 미리보기 전 DB 생성 0.
2. **DBVORA 모의 계약:** 테스트 자체 localhost mock HTTP 서버에 `GET /health`, `GET /api/inventory`만 허용, HAE `DbvoraClient`의 `p0-01.v1` SQLite metadata/provenance 검증. 응답은 경로/CSV 원문·고객행 제외. 계약 버전 불일치 `UNSUPPORTED_CONTRACT`, 모의 서버 중단 `UNAVAILABLE`; HAE 실제 LA의 완료 SQLite/감사 기록은 보존하며 연동 상태는 partial. **독립 DBVORA 실제 프로세스 또는 실제 고객 DB 검증 아님.**
3. **감사·영수증:** 승인 scope에 따른 LA runtime `/api/la-audit`의 계획 SHA256·승인 카운트·이벤트 검증, 런타임/사업 DB는 독립, `LAExecutor.verify_receipts` read-only 영수증 검증, 동일 승인 재실행 row 중복 0, audit response에 CSV 행/경로 비노출, advisory DBVORA 정상 시 workflow status completed.
4. **제한 스케줄:** 승인 없이 `LAExecutor.schedule`은 `ApprovalRequired`; 1001회 요청은 `PlanError`로 거부, 양 상태 DB 파일 0. 독립 `python -m lightning_azent schedule` 호출은 `--synthetic --approve-writes --max-runs 2` + interval 1초로 0,1 tick/4행. 별도 새로운 프로세스에서 1회 재개하면 tick2/6행, 기록의 `next_tick=3`. 실제 OS 재부팅/Windows Task Scheduler나 외부 cron 설치 시험은 미실시.
5. **위험 거부:** Gmail 전송·원격 DB 삭제 등 미지원 요청 HTTP422/실행 DB 0, 모의 공급자 POST/WRITE 0. 승인 없이 조건부 업로드는 HTTP403/양 DB 미생성.

## CI 오류/재시도
- 신규 P85 첫 commit `39d9b4f6d01350a3adb1e4b68336e969130984a2`에서 테스트 코드가 HTTP 결과 최상위 `workflow_status/dbvora/audit_persisted`를 중첩 `integration`으로 잘못 참조하여 **1 ERROR**. 원인 확인 후 **테스트만** 수정한 `a640666db7a1bf2011c5d2abc944f13199ce455f`에서 Ubuntu·Windows 각 P85 7 PASS. 스케줄 오류 유형도 `ApprovalRequired`·`PlanError`로 좁혀 유효 거부를 검증.
- 기존 Python full-suite 배송 2 FAIL: `test_checked_in_zipapp_matches_current_hae_and_staged_la_sources`, `test_release_zip_matches_shipped_sources_and_executes_real_la_e2e`. 오래된 원본 `hae-integrated.pyz` / `HAE-Windows-offline.zip`와 current source 불일치. **배송물 덮어쓰기·회귀 검사 건너뛰기·CI 전체 성공 주장 금지.**
- 사용한 데이터는 전부 합성·임시 로컬 CSV/SQLite. 실제 OAuth/고객자료/LLM/유료 API/외부 네트워크·프로덕션/사용자 계정 권한 변경 0. 테스트만 원본 HAE branch에 추가했고 LA 실행 모듈·출고 ZIP·pyz·원본 DB는 그대로이다.

## 설계 선택·복원
- A: Freelancer 상품 repo에 HAE/LA/DBVORA 엔진을 복제하여 단일 번들 시뮬레이션 — 독립 프로세스/업데이트 추적 불능 및 소스 drift, 보안 수정 중복, 유지보수비 증가.
- B(**채택**): 기존 HAE 서버/LA runner를 실제 실행하고 DBVORA protocol만 분리된 localhost mock으로 수용 — 엔진 기능 원본 유지, 네트워크/권한 최소화, 개별 오작동 시 경계 확인. 단점은 실 DBVORA 서버·바이너리 통합을 95 구간에서 독립 검증해야 한다는 점.
- 복구: 최초 HAE branch HEAD `980faee4e6163a5cd7126b6ac6be10b5ace4e012`; 새 시험 commit은 `39d9b4f6...`, 수정본 `a640666d...`. Git 이전 commit으로 새 시험만 revert 가능; 기존 고객/출고 바이너리 원본 불변.

## 다음 85→95 · 사용자 승인
- 전체 CI **0 FAIL**, 원본 ZIP/pyz SHA 정합성 회복 + 백업 후 안전 재생성 검증, 실 DBVORA 독립 프로세스와 schema/backup/restore, 지원 범위에 포함할 때만 실제 Google OAuth, 실제 Win10/11 Chrome·Edge 고객형 설치/업데이트·백업 복구, 실제 승인 UI.
- 최종 100점 전수 항목·가중치 독립검수와 고객 승인 전까지 **공식 최종완성률 UNASSESSED**, `[작업중]`·`RELEASE HOLD` 유지. 외부 비용/권한/실 데이터/출고 ZIP 원본 덮어쓰기는 사전 별도 승인.
- 재현: `cd apps/ax-flow && python -m unittest discover -s tests -p test_azentflow_p85_acceptance.py -v` (독립 LA package `packages/lightning-azent` staging 필수). 전체 회귀: `python -m unittest discover -s tests -v`; Node: `node tests/test_ui_races.cjs`.
- 기록 기준: 2026-11-13 KST. 대상 정확 기능 SHA `a640666d...`, Actions #43382552489. **Windows + Ubuntu 결과 확인 완료, 제품/해총 STATUS·HANDOFF 갱신 대상.** Vercel Production 미적용.
