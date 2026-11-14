# CITEVAULT AX — STATUS — RAG Studio Enterprise, 2026-11-13 KST

## [2026-11-14 09:10 KST] REQ24 합성 후속대화 + REQ19 Windows ZIP 실제 실행 검증

- 기능 SHA `f2979aa50156b4f5c3d80f4d23a1b2ec336f0040`, [정확 Actions #43531986943](https://github.com/hibi89/Freelancer/actions/runs/43531986943) **8/8 SUCCESS, 447 test executions PASS/0 FAIL/0 SKIP**, 원본 RAG pinned35+CITEVAULT bridge36, Ubuntu/Windows 로컬127씩·백업12씩·native31씩·Korean100 harness1씩, Chrome1, Windows ZIP QA2.
- **REQ24 실제 구현:** `p85-conversation.mjs` 5분 TTL/최대64 대화, SHA256 bearer 소유자 결속·문서 version/source SHA 기억, 매번 현재 ACL+source 재검증, 권한 철회·문서 폐기·교체·변조·만료·재로그인 시 fail-closed; UI 후속 질문 두 버튼 및 POST API, 양 OS 신규12PASS, Chrome 후속 질문 실제 클릭 확인. 답변 생성 없음·외부 통신0.
- **REQ19 실제 진전:** Windows2022에서 12파일 합성 오프라인 패키지(설치된 Node22 exe+JS+NOTICE·SHA manifest) 구성→Python 표준 ZIP 파일목록/CRC/해시 검증→압축해제된 Node.exe로 localhost 운영자 self-test **2PASS**, ZIP 크기33,208,926bytes, 압축 SHA `6dc2c15b...`. ZIP은 CI 내부만, **고객 다운로드/정식 설치기·Node 재배포 라이선스/물리 Win10/11 미검증**.
- **차단·피벗:** PowerShell ZIP 경로 문제로 CI 2번 실패(#43531311927/#43531472046) 후 원인 확인·같은 방식 중단→Python zipfile 로컬 검증 후 CI QA2PASS. 이전 CI #43531831668 Chrome cleanup `ENOTEMPTY`; 최소 종료 대기·rm retry 패치, 최신 8/8 PASS. 상세 `docs/P85_CONVERSATION_PORTABLE_20261114.md`.
- 전체24항 최종완성률 공식 **UNASSESSED / 사용자 목표85% 미인증**, `CITEVAULT AX [작업중]`, SALE NO-GO/RELEASE HOLD. 실제 기업 IdP·자료 권리·승인 AX producer·실 Korean local model·고객 Gold100·물리 Windows/고객 인수 미완. 공유 Freelancer PUBLIC에 다른 제품 노출/전수 비밀감사 미검증, 고객 원본·권한·Production·결제 미변경.



## [2026-11-14 KST] REQ16 실제 Chromium 대시보드·허용 문서 KPI/차트·원문 탐색 7/7 CI PASS

- 기능 SHA `49918ad4d0de23b8bc462830fa0789e93ebd7936`, [정확 Github Actions #43529432977](https://github.com/hibi89/Freelancer/actions/runs/43529432977) **7/7 jobs SUCCESS, 421 test executions PASS/0FAIL/0SKIP**(OS 중복 포함). 신규 ACL library API 테스트8PASS/OS, Chromium 실제 브라우저 렌더 테스트1PASS. Linux/Windows vault+HTTP 각각115PASS.
- 실기능: 서버 측 tenant/group/project/classification/active 사전 필터링 후 `GET /v1/library` 접근 허용된 문서의 metadata만 반환. `p85-ui.mjs` 문서 KPI/컬렉션 막대차트/원문 문서 선택/refresh/logout. 사용자 소스 원문·다른 조직 문서 명칭/개수·절대 파일 경로·토큰 미반출. SQLite 권한 철회·문서 폐기 시 즉시 반영.
- 실제 Chrome CDP Ubuntu 서버에서 로그인→대시보드→문서 검색→390px 모바일 무가로오버플로→스크린샷 SHA `dacfed12...`→로그아웃 및 UI 초기화, 외부 HTTP 요청0·JS runtime exception0. 로컬 환경 Chrome localhost는 관리자 정책 BLOCKED, 정책 우회하지 않고 Hosted 실제 Chrome PASS로 대체. 물리 Windows10/11 Chrome/Edge 미검증.
- 상세 `docs/P85_CHROMIUM_DASHBOARD_ACCEPTANCE_20261114.md`. REQ16 **합성 범위 브라우저 검증**, 실제 기업 IdP·원본 사용권·승인된 PREP/SMAX producer+AX/실 Korean model·Win 설치·고객 Gold100·보안 인수는 미완. 전체24항 **UNASSESSED, 85% 미인증, CITEVAULT AX [작업중], RELEASE HOLD/SALE NO-GO**. 타 제품/고객자료/Production/원본 소스 변경 없음.



## [2026-11-14 KST] P85 SQLite 백업 문서 목록↔원문 일치 보안 보강 — 정확 SHA d32f530e

- **최신 기능 SHA `d32f530e2425da0129a4eb2e9a4a7aef6708dab8`:** [hosted CI #43527372030](https://github.com/hibi89/Freelancer/actions/runs/43527372030) Ubuntu/Windows **6/6 SUCCESS; 404 실행 PASS/0FAIL/0SKIP**(OS 중복·합성100 반복은 스위트 각1개). 기존 pinned 원본 RAG35+CITEVAULT bridge36도 성공.
- **변경:** `p85-offline-backup.mjs` 스냅샷/복구에서 SQLite 정식 header/users/docs/audit 테이블, state generation, 사용자/문서 수·active 문서의 정확 tenant/id/version/native_kind SHA256와 staged 원문 bytes를 교차 검증. 이전에는 manifest SHA 재계산 시 DB 문서 목록↔원문 불일치를 막지 못함. 신규 부정 테스트 3개(원문 변조·SQLite+manifest 합성 위조·header-only DB) 추가, 양 OS backup 12/12 PASS, 합계 404PASS. 상세 `docs/P85_SNAPSHOT_CATALOG_INTEGRITY_20261114.md`.
- **완성률:** 24개 전체 기준 공식 `UNASSESSED`, 사용자 목표85% 아직 미인증, `[작업중]` 유지. 실제 고객 IdP/사용권/승인된 producer·한국어 실제 모델·물리 Win10/11/Gold·운영 보안·가중치 수용 미완. 서비스 중지한 합성 백업만 검증, Production 미적용. 추가 비용/실고객자료/원본 RAG·SMAX·PREP 변경0.
- 공유 Freelancer PUBLIC에 다른 제품/과거 브랜치 포함 공개 위험; 이력 비밀 전수 스캔 미실행.



## [2026-11-14 KST] 사용자 승인 후 P85 백업·복구 및 합성100 질의 성능/권한 CI 완료

- **기능 SHA** `0cf969fb2908cca985f4655d2c713ad7e030d168` (직전 백업 구현 `e1d25c18c3fb0ddaf6957ce91b6d54e15199582f`). 실제 [GitHub Actions #43525453183](https://github.com/hibi89/Freelancer/actions/runs/43525453183) **6/6 SUCCESS, 398 실행 PASS/0FAIL/0SKIP**(Linux/Windows 반복 test 포함): P70 31, RAG pinned 11+24+36, Windows/Linux P85 local 각107+백업 각9+합성100 작업 각1, Windows/Linux native 각31. 신규 정책 gate도 SHA별 별도 확인 필요.
- **실기능:** `p85-offline-backup.mjs` local state SQLite backup API + SHA256 manifest + document bytes, 원본 무변경·동일 경로/덮어쓰기·symlink/hardlink·추가/변조·경로 위조 거부, atomic create-only restore. `p85-offline-ops.mjs` 명령형 수동 실행만. Windows/Linux hosted 각 9PASS, 추가 비용/외부 네트워크 0. **서비스 정지·DB 닫은 상태에서만** 사용하며 생산형 고객 동시 백업/자동복구 아님.
- **합성 QA:** `tests/p85-synthetic100.test.mjs` 합성 한국어 질의 100회/OS, 근거검색20·근거부족20·원문 충돌20·기밀 직접조회 차단20·혼합 권한조회 차단20. CI 각 OS 1 테스트 스위트 PASS; p95 Ubuntu **0.328ms**, Windows **1.001ms** (작은 합성자료/측정 당시 runner, 고객 성능/Gold100 아님). 실 고객 질문/모델·정확도 외삽 불가.
- 24항 최종설계의 **공식 완성률 UNASSESSED / 85% 미검증**, `CITEVAULT AX [작업중]`, `RELEASE HOLD/SALE NO-GO` 유지. Real IdP/원본 사용권/실 signed PREP-SMAX·승인 AX/실 Korean local model/실 Win10/11 설치/고객 Gold100/수용 가중치·법적 검수 미완. Public 공유 repo 전 브랜치/이력 보안 위험 미해결; 고객자료·비밀/타상품/원본 RAG/Production 무수정.
- 증거: `docs/P85_OFFLINE_SNAPSHOT_20261114.md`, `docs/P85_SYNTHETIC100_EVIDENCE_20261114.md`.


## [2026-11-14 KST] CITEVAULT P85 호스티드 Ubuntu+Windows CI 복구 성공 (소스 SHA cea0ec09)

- 실제 [GitHub Actions #43523337142](https://github.com/hibi89/Freelancer/actions/runs/43523337142) **6/6 SUCCESS**, 원본 pin RAG P512 11 + P538/P540/P549 24 + CITEVAULT bridge 36; Ubuntu/Windows 로컬 107×2, native PDF/DOCX 통합 31×2, Linux local-contracts 31. **378 실행 PASS/0FAIL/0SKIP**, OS별 동일 테스트 중복 포함; [최종설계 정책 gate #43523337300](https://github.com/hibi89/Freelancer/actions/runs/43523337300) SUCCESS(정책 검증만).
- 첫 hosted 재실행에서 Windows 한국어 DOCX `NATIVE_HOLD`와 SQLite `EBUSY`가 실제 발생. Python `-I`의 환경변수 무시와 Windows 파이프 코드페이지 차이를 `-X utf8`로 대응; 테스트 저장소 close→임시파일 정리 순서 변경. 코드 source commit `cea0ec09ac4a85a16e369bd302986959fca408b0`에서 모두 실제 CI PASS. 상세 `docs/P85_HOSTED_CI_RECOVERY_20261114.md`.
- **주의:** 사용자 조치로 공유 `hibi89/Freelancer` 전체 저장소 현재 PUBLIC; 여러 제품의 다른 브랜치·커밋도 공개. 과거 파일·민감정보 전수 검사 미실시, 원본 공개 여부 안전 판정 불가. assistant는 공개 설정을 변경하지 않음.
- **최종설계 24항 전체에 대한 공식 완성률 UNASSESSED, 목표 85% 미입증**, `CITEVAULT AX [작업중]`, `RELEASE HOLD/SALE NO-GO` 유지. 실제 고객 IdP/권리/승인 producer, 실제 Korean model+Gold, 실제 Win10/11 설치·보안/고객 수용 없음; Production 미적용. GitHub Actions green은 최종상품 승인 아님.


## [2026-11-14 KST] CITEVAULT AX P85 원본 RAG/Windows CI 장애 수정·실행 계층 차단

- 기능 패치 `88564c860a3da0a8d9a7c3e4dac3c99a6b2e2cbe`: 원본 RAG 통합 테스트 구문 괄호, Windows SQLite 임시파일 정리 순서, Python DOCX 안전한 Windows 환경 변수 전달을 최소 수정. GitHub 정확 blob SHA 3건 조회, 원본/고객자료/타상품 불변.
- 이전 hosted [#43514206340](https://github.com/hibi89/Freelancer/actions/runs/43514206340): pinned RAG 원본 체크아웃 및 원본 35개 테스트는 통과했으나 CITEVAULT 브리지 SyntaxError; Windows DOCX NATIVE_HOLD, Windows SQLite EBUSY 확인. 신규 정확 SHA [#43516278650](https://github.com/hibi89/Freelancer/actions/runs/43516278650) 및 최종설계 gate [#43516279187](https://github.com/hibi89/Freelancer/actions/runs/43516279187) **FAIL before runner allocation** (steps 0/runner 0/로그 없음), 코드 테스트는 실행되지 않음. 계정 할당/쿼터 원인 미확정, 무의미한 재실행/과금 변경 금지.
- 사용자 최종설계 24항 전체 대비 **공식 UNASSESSED, 85% 미검증**, 이전 로컬 합성138PASS는 과거 SHA 증거로만 보존. `CITEVAULT AX [작업중]`, RELEASE HOLD/SALE NO-GO. 85% 확정에는 실기업 IAM·자료 사용권/승인·서명된 원본 PREP/SMAX·실 한국어 모델·Windows/Gold/수용 가중치 증거가 추가로 필요. 정본 `docs/P85_HOSTED_CI_TRIAGE_20261114.md`.


## [2026-11-14 KST] P85 통합 PREP·SMAX 서명 검토 실경로 검증 — 합계 138 PASS

- **기준·판정:** 사용자 최종설계 전체 `docs/FINAL_BLUEPRINT.md` 100% 대비 85% 목표 **UNASSESSED, 아직 미달성/미검증**; `[작업중]`, RELEASE HOLD/SALE NO-GO. `docs/FINAL_BLUEPRINT_85_ACCEPTANCE_MATRIX_20261114.md`의 24개 REQ 정확 수용표만 사용, 합성 테스트 통과율로 85% 조작 금지.
- **이번 실제 기능:** 이전에 단독만 검증됐던 Ed25519 서명 기능을 실제 `POST /v1/assess` 검토 전용 PDF/DOCX/TXT+readonly SQLite 요청에 연결. `p70-local-review.mjs`에서 직접 파일로 읽은 PREP 매핑 원문 bytes SHA·재검증, `p85-review-sql.mjs` SQLite 잠정 매출 결과에 mapping digest 결속, 신규 `p85-signed-review-gate.mjs` host-trusted 공개키·조직·key ID·원본 CSV SHA·PREP mapping SHA·version/expiry 검사, `p85-journey.mjs`서 오류/위조·스키마 변조·재사용·만료 시 데이터/인용 누출 없는 REVIEW_HOLD·answer:null. 유효한 서명도 source_rights_verified false, customer_approval false, ax_package_created false. **실제 고객/SMAX producer/권리 승인 아님**.
- **검증:** Linux Node22.16/Python3.13.5 이번 변경 후 개별 완료 P85 테스트 10파일 **138PASS/0FAIL/0SKIP**(기존 합성 129+신규 signed SQL journey 9), 총합은 **각 파일 별도 실행 결과**, 단일 묶음 테스트 명령은 timeout으로 **미완료**. 새 9건은 실 API HTTP/서명 변조/원본·매핑 SHA/조직 경계/버전·만료 부정까지 PASS. 기존 P85 journey 18, HTTP17, actual native PDF/DOCX13, state14, vault27, operator10, UI6, BM25 6, 서명 단독18 개별 통과. 독립 ZIP 28파일 CRC검증·압축해제 신규 9 PASS/데모 PASS; SHA256 `84a9ea2725fe8391451a6942f5ec4628471c86f0d66bb9bc3d3b8fab3d4aa99e`. 소스/테스트 5파일 GitHub remote blob/local `git hash-object` 정확 SHA 일치. 상세 `docs/P85_SIGNED_REVIEW_INTEGRATION_EVIDENCE_20261114.md`.
- **CI/RAG 구분:** Ubuntu24.04/Windows2022 GitHub Actions P85 job 신규 source/test 확인 및 실행 정의(실 Hosted run ID/CI SHA/Windows PASS **미검증**). 원본 RAG Studio 과거 workflow run ID `43231121679`는 Windows/Ubuntu 성공 확인했지만 CITEVAULT pinned `c5867b3951f51bfa97cadd1aad8fb13e9cf9e604` exact 3SKIP 증거는 아님. 원본 develop과 pin 분기 상태 유지.
- **잔량/승인:** 실제 기업 IAM/신뢰 사용자·고객 source rights/키 관리·실 PREP/SMAX 승인 패키지, pinned 원본 RAG native/SQL/BM25 실제 실행, 한국어 실제 local pretrained model/라이선스+성능, Windows/Linux hosted CI/물리 설치·Gold·인수, 최종설계 owner 승인 가중치 모두 대기. 추가 비용·권한 변경·원본/고객자료·Production/Vercel·타 크몽 상품 변경 0.



## [2026-11-14 KST] CITEVAULT AX 최종설계 85% 목표 실구현 — 로컬 사용자관리·UI·BM25

- **공식 판정:** 최종완성률은 `docs/FINAL_BLUEPRINT.md` 전체 100% 기준. **UNASSESSED · 85% 달성 미검증**, `[작업중]`, `RELEASE HOLD / SALE NO-GO`. 전체 24요구 수용표 `docs/FINAL_BLUEPRINT_85_ACCEPTANCE_MATRIX_20261114.md`; 임의 가중치·합성 PASS 기반 최종점수 산정 금지.
- **실제 구현:** `p85-state-store.mjs` SQLite `createUser/loadAccount/replaceUserAccess` 트랜잭션·audit; `p85-vault.mjs` 관리자 로컬 `provisionUser/changeUserAccess`, 조직·관리자 권한 범위 상속, 모든 로그인·세션 사용 시 최신 SQLite 자격/그룹 재조회, 교차 프로세스 revoke/실시간 축소 반영. `p85-loopback.mjs`에 `POST /v1/admin/provision`, `/v1/admin/access` 및 `GET /`·`/ui.js`·`/ui.css` 정적 localhost UI, CSP/no-store/CORS 미허용. `p85-ui.mjs` 로그인·근거검색·운영자 권한 UI(토큰 메모리, DOM textContent). `p85-bm25.mjs` 실제 BM25+한국어 ngram, 사전 ACL·source SHA 통과한 citations만 rank. 독립 시연 `scripts/p85-operator-demo.mjs --self-test`.
- **실행 검증:** Linux Node22.16/Python3.13 `node --test --test-concurrency=1 tests/*.test.mjs` **129 PASS/0 FAIL/0 SKIP**(현재 P85 standalone synthetic, 원본 RAG 3SKIP 포함 아님). 신규 운영자/계정 테스트 10PASS·UI/API 6PASS·BM25 6PASS. 기존 P85 vault27/HTTP17/SQLite14/native PDF-DOCX13/SQL journey18/Ed25519 18도 회귀 PASS. `node scripts/p85-operator-demo.mjs --self-test` PASS. 정확 GitHub blob/local `git hash-object` 수정/신규 9파일 9/9 동일. 증거/요구 표 `docs/FINAL_BLUEPRINT_85_ACCEPTANCE_MATRIX_20261114.md`.
- **ZIP 독립 검증:** `CITEVAULT_AX_P85_operator_bm25_20261114.zip` 25파일, SHA256 `161bb8bc4069e8e6e51fa3b70d54e77911d9e884155c042517170b3119b2d5ca`. 압축해제 후 operator selftest PASS, BM25+UI 12 PASS/0 FAIL. 기존 파일/원본·고객 데이터 변경 없음. Linux local only.
- **CI/실서비스:** `.github/workflows/citevault-p50.yml` Ubuntu24.04/Windows2022 Node22 행렬에 새 operator/visible UI/BM25 tests+셀프테스트 추가(정의만), **Hosted 실제 workflow job/run SHA/Windows 실행 결과 미확인**. Chromium local 실제 렌더 시도는 조직 정책에서 `127.0.0.1` 차단 `chrome-error://chromewebdata/` → 미검증, 우회 안 함. Vercel/Production/실기업 계정 미적용.
- **중요 잔량:** 원본 RAG Studio 정확 pin `c5867b...` BM25/SQL/native/PREP-SMAX 통합 3SKIP, 실제 고객 신분/IdP·원본 이용권 승인·진짜 signed PREP/SMAX→AX producer, 실제 한국어 모델 체크섬/권리/품질, Windows/Linux Hosted CI·물리 Windows10/11/Gold100/고객 수용 미구현/미검증. 합성 로컬 운영자 ≠ 기업 IdP. 사용자 불필요 개입 중단 조건은 아님, 실제 개인정보/권한/고객 승인은 추후 요청.



## [2026-11-14 KST] CITEVAULT AX P85 서명 검토 경계 — 독립 18 PASS

- **목표와 판정:** 사용자 최종설계 전체 대비 85% 목표. **공식 UNASSESSED / 85% 미달성·미검증**, `[작업중]`, `RELEASE HOLD/SALE NO-GO`. 기존 합성 local Node 통합 기능을 실제 기업 인증이나 고객 승인으로 전용 금지.
- **추가 구현:** `enterprise/p85-signed-provenance.mjs`에서 Ed25519 오프라인 서명 생성/검증. 테넌트·외부 신뢰 공개키 ID·source CSV SHA256·PREP mapping SHA256·정렬된 문서 SHA/types·issue/expiry·생산자 버전 일치 검증. 위조된 `approved`·`rights_verified:true`·타 조직·가짜 키·만료/replay 시 HOLD. 모든 성공 반환도 `REVIEW_HOLD`, `source_rights_verified:false`, `ax_package_created:false`, `answer:null`. 본 기능은 실제 PREP/SMAX producer 통합이 아닌 **합성 메타데이터 전용 검증 계약**.
- **실제 검증:** Linux Node22.16.0 `node --check enterprise/p85-signed-provenance.mjs` PASS, `node --test tests/p85-signed-provenance.test.mjs` **18PASS/0FAIL/0SKIP**, GitHub 원격 2파일 blob SHA `78b777505a4325230ad7f780907bf08538dc7783` / `ef21059e67ce5b2e4c7b5043d6ed0e738c151232` 로컬 `git hash-object`와 동일. 지난 전체 P85 89/89 PASS는 **변경 이전 기록**, 이번 전체 직렬 실행은 HTTP 테스트 이후 native 단계에서 도구 제한시간 초과하여 **미완료**, 신규 전체 107PASS라고 주장하지 않음.
- **CI:** `.github/workflows/citevault-p50.yml` Ubuntu/Windows P85 matrix에 신규 서명 파일 syntax 및 테스트 추가; 실제 Hosted Actions run/log/Windows 실행은 **미검증**.
- **남은 필수:** 정확 pin 원본 RAG SQL/BM25/PDF/DOCX·SMAX 3SKIP, 실제 고객 임직원 IdP/권한과 자료권리 승인·실 PREP/SMAX signed producer 연동, 한국어 실제 로컬모델·라이선스, Windows 물리/CI, 고객 Gold·가중치 수용. 실제 기업 IdP/고객 문서/원본 RAG/PREP/SMAX/외부 API/Prod 변경 없음. 증거 `docs/P85_SIGNATURE_GATE_20261114.md`.



## [2026-11-14 KST] CITEVAULT P85 권한-매출 폴더 바인딩 검수 — 89PASS

- **설계 전체 목표:** 사용자 최종설계 100% 대비 85%. 공식 완성률은 **UNASSESSED**, 85% **검증 미달**, 크몽 `[작업중]`, **RELEASE HOLD/SALE NO-GO**.
- **발견·실제 수정:** `authorizeSyntheticDataset`가 사용자 tenant/group/project 권한만 검증하면서 `salesDirectory`를 인증된 테넌트의 물리 폴더에 결속하지 않는 취약 경계를 발견. `enterprise/p85-vault.mjs`가 고정 `<root>/<tenantId>/sales-only` 절대 경로·조직 폴더/세일즈 폴더의 디렉터리 타입·심볼릭 링크를 **CSV 읽기 전에** 확인하도록 변경, `enterprise/p85-journey.mjs`에서 server-configured 실제 폴더를 인가 함수로 전달. `tests/p85-journey.test.mjs`에 타조직 경로 바꿔치기·매출 폴더 심볼릭 링크 거부 2개 추가. 합성 PDF/DOCX 생성물의 immutable byte template만 재사용하여 각 테스트는 여전히 독립된 파일에서 실제 native parsing 및 승인 HOLD 실행.
- **정확 소스 SHA:** remote GitHub blob/local `git hash-object` 정확 일치 vault `3256d1e52fed8bcf4748060478b381e9c5afe542`, journey `7e194a8def953e851e8413f217212338d033a994`, test `40a171cadb662275f34c62f5f602ae3cdb7ab4d8`. 세 파일 GitHub 반영 완료. 상세 `docs/P85_TENANT_PATH_AND_QA_20261114.md`.
- **실행 테스트:** 이 세 파일 포함 독립 ZIP 로컬 Linux Node22.16/Python3.13.5: P85 journey **18PASS/0FAIL/0SKIP**(기존16+새2), 인증 vault27PASS, loopback17PASS, state-store14PASS, real native PDF/DOCX13PASS. **`node --test --test-concurrency=1 tests/*.test.mjs` = 89PASS/0FAIL/0SKIP**, JSON HTTP demo `--self-test` PASS. Journey 실행시간 이 환경 약 66.7s → 28.0s (fixture 생성 반복 제거). 이전 P50/P70/P85 결합 결과 124total/121PASS/3SKIP은 선행 이력이며, 이번 업데이트를 반영한 확장 결합 126개 명령은 **이번 턴 미실행**.
- **원본 RAG SHA 정책:** 기존 pin `c5867b3951f51bfa97cadd1aad8fb13e9cf9e604` 보존. `develop` 최근 HEAD `bb8529ed689c1e95ccd7bbb722d4d6616eb46130`와 분기가 달라 자동 교체하지 않음. 정확 원본 RAG checkout/SMAX SQL 3SKIP 및 GitHub Hosted Actions job/Windows 실실행 확인 불가. GitHub workflow 정의만 CI PASS로 간주 금지.
- **출시 및 승인:** 실제 기업 IdP/영속 직원 권한·실고객 소스 권리와 서명 승인 PREP/SMAX→AX, 원본 pinned RAG native SQL/문서 검색 연결, 실제 한국어 모델/라이선스/Win10·11/Gold, 취약 입력·TOCTOU 보안 검증 등이 미완. 원본 RAG/PREP/SMAX·고객 계정·타상품·Production/Vercel·환경변수·결제 변경 없음.



## [2026-11-13 KST] CITEVAULT AX 통합 서비스 85% 목표 재추진 — PDF/DOCX·SQLite 리뷰 HTTP 종단 PASS

- **공식 판정:** 전체 최종설계 100% 대비 사용자 **85% 목표**, 현재 **UNASSESSED · 85% 미달/검증 대기**, `[작업중]` 유지, `RELEASE HOLD / SALE NO-GO`. P85 synthetic-only 테스트 수를 전체 고객제품 완성률로 환산 금지.
- **이번 실제 통합 개발:** 기존 P85 합성 account/session+tenant/group/project ACL/SQLite document lifecycle/실 PDF page+DOCX paragraph에 **하나의** `POST /v1/assess` 오프라인 종단 경로 구현. `enterprise/p85-review-sql.mjs`는 `p70-local-review.mjs` 실제 CSV bytes/SMAX/PREP source SHA review HOLD 재확인 후, 좁은 5컬럼 합성 subset을 SQLite `:memory:` 고정 읽기 전용 SQL로 재계산·P70 BigInt totals 대조한다. `enterprise/p85-journey.mjs`는 문서 원문 접근/시스템 고정 매출데이터 범위 인가→선별 PDF/DOCX 검색→CSV 권리 미승인 근거/잠정 매출 명시→**answer null/REVIEW_HOLD**. 임의 SQL/기간별 매출/출처 변경·허위 승인/타조직 누출 거부.
- **실행 가능한 demo:** `scripts/p85-synthetic-demo.mjs --self-test`가 127.0.0.1 임시 HTTP·무작위 합성 자격증명·실 PDF/DOCX+CSV를 생성, 로그인→통합 запрос→REVIEW_HOLD 검증 및 임시파일 삭제. **PASS**, 외부 API/모델 0. 일반 실행은 로컬에서 데모 세션 제공하지만 상용 고객 데이터 입력/배포 금지.
- **실제 테스트:** Linux Node v22.16.0/Python3.11 신규 통합 **16PASS/0FAIL/0SKIP**, 전체 로컬 P50/P70/P85 **124 TOTAL/121 PASS/0FAIL/3SKIP**(3개 pinned 원본 RAG checkout). 신 소스/테스트/스크립트 6개 GitHub blob과 로컬 `git hash-object` exact 일치. 새 ZIP 독립 압축해제: `node scripts/p85-synthetic-demo.mjs --self-test` PASS, `node --test --test-concurrency=1 tests/*.test.mjs` **87 PASS/0 FAIL/0 SKIP**(약 56s). 이전 병렬 zip run 툴 시간 초과, 직렬 재실행 정상 PASS. 증거 `docs/P85_UNIFIED_EVIDENCE_20261113.md`.
- **CI:** Ubuntu24.04/Windows2022 Python3.11/Node22 native job에 16개 통합 테스트와 실제 로컬 데모 self-test 추가. GitHub workflow blob `4e5fe24c4b25cba8bc7054c91d8e2cd4de95c193`; **Hosted CI/Windows 실통과 확인 불가**. 원본 RAG `c5867b3951f51bfa97cadd1aad8fb13e9cf9e604` checkout/SQL/native 연동 3SKIP 미해결.
- **구현 미완과 보존:** 실제 직원 IdP/기업 IAM, 원본 RAG/PREP/SMAX signed approved AX, 한국어 실제 로컬모델·라이선스·악성문서 sandbox, 실제 물리 Windows/customer Gold/권리/완성률 owner 가중치 미확정. 원본·권한/환경변수/고객데이터/타상품 불변. Production/Vercel 미적용.



## [2026-11-13 KST] P85 재진행 — 실제 PDF/DOCX 바이트 파서·권한/인용 통합 검증

- **목표:** 사용자 최종설계 전체 기준 85%, 공식 최종완성률 **UNASSESSED / 85% 미확정**. `[작업중]` 유지, `RELEASE HOLD/SALE NO-GO`. 기준 복구 HEAD `6fb66efd14dd95dd64ebfb1305ef872478ff1524`.
- **이번 실제 개발:** 기존 합성 LocalSyntheticVault에 native_kind=`txt/pdf/docx` 구현. 계정·테넌트·그룹/프로젝트/등급 사전 ACL→원본 링크·바이트 SHA256→최대 2MiB 승인된 **실제 PDF/DOCX 버퍼**→독립 Python `pypdf` 페이지·`python-docx` 문단 추출→고유 페이지/문단 인용. 오프라인 경계, 문서 상충 보류/검색모델 없는 SEARCH_ONLY, SQLite 문서 버전·퇴출 기존 기능 통합. 새 소스 `enterprise/p85-native-extract.py`/`.mjs`, `tests/p85-native-fixture.py`, `tests/p85-native-integration.test.mjs`, `tests/requirements-p85-native.txt`. 원본 RAG/PREP/SMAX 수정 0, 기업 실제 파일 업로드/계정 변경/배포/유료 호출 0.
- **실제 검증:** Linux Node22.16/Python3.11, 실제 2페이지 PDF·한국어 DOCX 2개 등 합성 파일로 P85 신규 테스트 **13 PASS/0 FAIL/0 SKIP**. 전체 P50/P70/P85 로컬 테스트 **108 total/105 PASS/0 FAIL/3 SKIP**. 3 SKIP은 pin `RAG_STUDIO@c5867b3951f51bfa97cadd1aad8fb13e9cf9e604` 원본 체크아웃 필요 SQL/BM25/SMAX 통합, 신규 native PASS와 혼동 금지. 원격 GitHub 6개 파일 SHA와 로컬 검증 파일 `git hash-object` 1:1 일치. 증거 `docs/P85_NATIVE_EVIDENCE_20261113.md`.
- **CI:** `.github/workflows/citevault-p50.yml` 신규 Ubuntu24.04+Windows2022 `p85-native-evidence` Python3.11/Node22 job, PDF/DOCX pinned dependencies 설치·실 테스트. **Hosted 실행 결과 및 Windows PASS 미검증**; 기존 원본 RAG P512/P538/P540/P549 job도 미검증. 실행 정의만으로 최종완성률 상승 주장 금지.
- **한계:** 원본 RAG Studio native parser/SQL 직결이 아닌 별도 합성 증거 경로, 고객 실제 기업 IAM/법적 사용권, signed PREP/SMAX→AX, 한국어 실제 모델·라이선스/정확도, Gold/물리 Windows10/11·상용 샌드박스 보안 미구현·미검증. PDF OCR/복잡한 DOCX 구조/악성 파일 풀샌드박스 미지원. 기존 회귀/원본 보존.



## [2026-11-13 KST] CITEVAULT AX 85% 재추진 — SQLite 영속 상태·철회·감사 원자화

- **공식 목표:** 최종설계 100% 대비 85%. **현재 공식 완성률 UNASSESSED / 85% 미달성·검증 대기**, `[작업중]` 유지, `RELEASE HOLD/SALE NO-GO`.
- **실제 구현:** 신규 `enterprise/p85-state-store.mjs` Node22 내장 SQLite (실험적): 합성 계정/문서 메타데이터를 최초에만 시드하고 재시작 때 재사용, 외부 주입 시드 재등록 거부, 문서 버전/폐기·로그·접근 철회 보존. 원본 `p85-vault.mjs`에 선택적 `stateStore`, 권한검사 후 파일 로딩, cross-process 계정 disable·폐기 반영, stale revision 거부. `p85-loopback.mjs`에 관리자 revoke API 추가. version/reindex/retire/revoke 상태 변경 및 감사 기록은 한 SQLite 트랜잭션. 원본 RAG/PREP/SMAX는 불변.
- **실제 검증:** Linux Node v22.16.0 `node --test tests/p85-vault.test.mjs tests/p85-loopback.test.mjs tests/p85-state-store.test.mjs` **58 PASS/0 FAIL/0 SKIP**, 독립 ZIP 압축해제 후 재실행도 **58 PASS**. P50/P70/P85 Node 전수 로컬 결합 **95 total/92 PASS/0 FAIL/3 SKIP** (3개 RAG 원본 checkout 필요). 신규·수정 코드/테스트 Git blob 6개 `git hash-object` 정확 일치. 근거: `docs/P85_DURABLE_EVIDENCE_20261113.md`.
- **CI/Windows:** `.github/workflows/citevault-p50.yml`에 기존 Ubuntu24.04/Windows2022 P85 매트릭스의 SQLite 영속성 14케이스 추가. 실제 GitHub Actions hosted job/run 및 Windows 실행 결과 **미확인**, GitHub Classic commit status 0개만으로 성공/실패 판단하지 않음.
- **중요 미완:** 진짜 기업 사용자 IdP/영속 운영계정·테넌트별 안전한 index/물리 RAG 데이터계약, 실 승인된 PREP/SMAX→AX, PDF/DOCX 원문 페이지/문단 통합, 한국어 로컬 모델/권리 실험, 실제 고객 Windows/Gold·백업 복구. 합성 로컬 메타데이터는 상용 IAM 인증이 아니며 85% 공식 인정 불가.



## [2026-11-13 KST] CITEVAULT AX P85 사용자 목표 — 조직분리·로그인·문서 수명주기 로컬 검증

- **공식 목표/판정:** 사용자 확정 최종설계도 전체 대비 **85%**. 실제 최종완성률은 **UNASSESSED**, 85% **미달성/검증 대기**, 해총 **[작업중]** 유지, **RELEASE HOLD / SALE NO-GO**.
- **신규 실제 구현:** `enterprise/p85-vault.mjs`: 오프라인 합성 계정 scrypt 로그인·시크릿 없는 난수 Bearer 세션, 15분 만료/로그아웃/잠금, 조직·그룹·프로젝트·등급 ACL 검증 **후**에만 고정 파일 원문 열람, SHA256·링크·경로·사이즈 변조 차단, 조직별 감사 이력, 버전 전환/폐기/관리자 재색인. `enterprise/p85-loopback.mjs`: `127.0.0.1`로만 바인딩되는 합성 HTTP QA, 401/403/404, `no-store`, JSON/4096 bytes 입력 제한. 실제 고객 IAM/Production 서버 아님.
- **실행/검증:** GitHub blob SHA와 Linux Node22.16 로컬 파일 4개가 `git hash-object`로 정확 일치 (vault `378523e03e4d42fe899e702504f8c37b6c23454e`, vault test `5e455611732c067bbcbcd7c5b8ea005e775e3dea`, HTTP `dee33df73c1f677713c11c89156f07fd4de40dfd`, HTTP tests `80a30bccb792a8a37104ec5376c55ce1dce4a4f3`). `node --test tests/p85-vault.test.mjs tests/p85-loopback.test.mjs` **42 PASS/0 FAIL/0 SKIP**, 기존 P50/P70 Node 검증 포함 총 **79 중 76 PASS/0 FAIL/3 SKIP**. 3 SKIP은 실제 원본 RAG Studio checkout에 필요한 통합.
- **보안 결함 처리:** 1차 개발 이후 관리자 감사 조회의 조직 간 이벤트 메타정보 노출 가능성을 확인→tenant별 audit 저장/조회 필터 추가 후 27/27 vault PASS. HTTP text/plain JSON 및 4096 bytes 초과 본문 차단 추가 후 15/15 PASS.
- **CI:** `.github/workflows/citevault-p50.yml`에 `p85-loopback-contracts` Ubuntu24.04/Node22.16 + Windows2022/Node22.23 매트릭스 추가. **Hosted run/job 로그 및 Windows PASS는 확인 불가**. 이전 원본 RAG P512/P538/P540/P549도 CI 정의만 확인.
- **미구현/미검증:** 영속 IAM/계정 데이터 저장, 조직별 실제 데이터/인덱스/세션, 실제 고객 허가된 PDF/DOCX·SMAX Native→서명 승인 AX, 한국어 실제 모델/라이선스, 실 Windows 인수/Gold·백업 복구, 사용자 최종설계 가중치 100% 재산정. `docs/P85_EVIDENCE_MATRIX.md` 필수 추적.
- **보존:** 원본 RAG/PREP/SMAX/고객정보·계정 권한·Vercel/Production/과금 변경 없음. CI 통과를 추정하지 않고 `[작업중]` 유지.


## [2026-11-13 KST] 사용자 70% 목표 2차 구현 — Node 34PASS/0FAIL/3SKIP, 최종완성률 미확정

- **실제 개발:** 원본 RAG 통합 브리지의 근거 없는 `FOUND` 허용 결함 확인·수정. `enterprise/p70-citation-contract.mjs` 엄격 출처 검증을 `enterprise/p70-rag-bridge.mjs`에 실제 연결. `enterprise/p70-local-review.mjs`는 실제 로컬 CSV bytes/원본 SHA-256/5열 역할 매핑/BigInt 금액 일치/보존 확인, SMAX/PREP `REVIEW_HOLD`만 출력. `row_lineage_verified:false` 등 권리·인가 과대주장 금지.
- **정확 검증 범위:** Linux Node **v22.16.0**, 원격 GitHub 코드와 로컬 4개 신규 source/test Git blob SHA 일치: 인용 계약 **14 PASS/0 FAIL**, CSV/매핑 review-only **17 PASS/0 FAIL** → **31 PASS/0 FAIL/0 SKIP**. 기존 P50 standalone 3 PASS/3 SKIP와 동시 명령 실행 기준 **37 total / 34 PASS / 0 FAIL / 3 SKIP**. SKIP 3은 실제 pinned RAG checkout 불가로 SQL/BM25/SMAX 통합 미수행. P70 original-source BM25/충돌/근거 계약 **순수 V8 in-memory 5 PASS**, 로컬 자료/Node native RAG 대신 증명하지 않음. `docs/P70_EVIDENCE_MATRIX.md`의 정확 blob과 실행 근거.
- **CI:** GitHub Actions `.github/workflows/citevault-p50.yml`의 독립 `local-contracts` job으로 31 Node 테스트 구성, `synthetic-evidence`는 원본 RAG pin과 P512/P538/P540/P549 연결. 실제 GitHub Actions run ID/job status **미검증**.
- **남은 목표:** P50 실 원본 RAG package import 통합 3개 SKIP 해결, PDF/DOCX 2+ 실제 source CI/Windows, PREP/SMAX 실제 인증 승인→AX 전환, 기업 서버 Identity 및 ACL-before-load, 사용자 승인 최종설계 100% 가중치 전수 평가. 순수 synthetic 도구를 실 IAM/법적 승인으로 간주 금지.
- **판정:** 공식 최종완성률 **UNASSESSED**, 70% 사용자 목표 **미달성·검증 대기**, `[작업중]` 유지, `RELEASE HOLD / SALE NO-GO`, Production 배포 미적용. 이번 변경은 기존 원본/고객자료/자격증명/기타 상품 무변경.


## [2026-11-13 KST] 사용자 CITEVAULT AX P70 개발 목표 — 오프라인 검색정책 구현, 최종 70% 미검증

- **목표:** 사용자 최종설계 전체 대비 70%(기존 P50 선행 미검증 포함). 현재 **공식 최종완성률 UNASSESSED, 목표 70% 검증 미달**, `[작업중]` 및 `RELEASE HOLD/SALE NO-GO` 유지.
- **이번 구현:** `enterprise/p70-policy.mjs` (synthetic-only 테넌트/부서/프로젝트/등급/유효기간 제약, 무권한 문서 제외, 전체 허가 문서 상충 보류, 로컬 모델 없는 `SEARCH_ONLY`, SMAX `REVIEW_HOLD` 강제) + `enterprise/p70-rag-bridge.mjs` (허가된 synthetic 문서 ID만 원본 RAG `knowledgeSearch` 대상으로 전달, 반환 출처 재검사). PDF 페이지 번호를 테스트용 줄 번호로 잘못 표시하지 않도록 수정.
- **테스트:** `tests/p70.test.mjs` 24개 신규 순수 JS 테스트, **GitHub 정본 JS를 V8에서 동작시켜 24 PASS / 0 FAIL**. Node/Hosted CI가 아닌 별도 테스트 환경. `tests/p70-rag-integration.test.mjs` 6개 원본 연결 테스트 작성, 실제 Node 실행 **미검증**. 기존 P50 테스트는 이전 턴 Node22 단독 **3 PASS / 0 FAIL / 3 SKIP** (3개 RAG 통합 미실행).
- **원본 회귀 CI 설정:** `.github/workflows/citevault-p50.yml`에 기존 RAG 정확 pin `c5867b3951f51bfa97cadd1aad8fb13e9cf9e604`와 P512 PDF/DOCX, P538 전체 상충, P540 다중 native, P549 PREP/SMAX mapping 리뷰, 신규 P70 Node 테스트 추가. **실제 CI run ID/성공 확인 없음**. 구현 근거 및 70 요구 전수 표 `docs/P70_EVIDENCE_MATRIX.md`.
- **핵심 한계:** `SYNTHETIC_ONLY` principal은 실제 IAM이 아니고, 원본 RAG `loadPackage()`는 문서 권한 필터 전 패키지 전체를 로딩하므로 **기업 ACL-before-load 미구현**. 실기업 권한/고객 파일·진짜 승인된 PREP/SMAX→AX 전환, 모델/Windows/라이선스 미검증. 비공개 원본/토큰/고객자료·계정/배포 변경 없음.
- **결론:** 개발 소스 반영은 검증됨. 독립 검수 없는 70% 수치 책정 불가, **[작업중] 유지**. 해총 중앙 후보표/인수인계 최신화 필요.



## [2026-11-13 KST] CITEVAULT AX P50 사용자 목표 — 통합 QA 소스 반영, 50% 미검증

- **작업 목표:** 최종설계 전체 기준 50%. 현재 공식 완성률 **UNASSESSED**, 목표 **미달성/검증 대기**. 목표 달성 전 해총 후보 목록에서 `[작업중]` 유지.
- **제품 브랜치:** `hibi89/Freelancer@product/rag-enterprise-knowledge`. 신규 소스 `enterprise/p50-gate.mjs`, 테스트 `tests/p50.test.mjs`, workflow `.github/workflows/citevault-p50.yml`, 추적 `docs/P50_EVIDENCE_MATRIX.md`. 원본 RAG/PREP/SMAX 수정 없음.
- **실 엔진 정확 참조:** `hibi89/RAG_STUDIO@feature/p550-mapped-cited-journey` pinned `c5867b3951f51bfa97cadd1aad8fb13e9cf9e604` (read-only 외부 checkout). RAG `develop`와 과거 CI SHA `0e88301059c9...`는 diverged, 상용 엔터프라이즈 P50로 점수 승계 금지.
- **구현:** 실 RAG 모듈 동적 로드, 승인된 합성 AX SHA/SQL KRW 157,000 오라클/TXT 출처/BM25 검사, 승인 전 SMAX `REVIEW_REQUIRED` 차단, 합성 파일 스냅샷 전후 digest, symlink/위변조/잘못된 집계 부정 테스트.
- **로컬 정확 소스 테스트(2026-11-13 KST):** GitHub 새 소스 2개 `git hash-object`가 원격 blob SHA와 각각 일치(`5e9080f00fcda6c92ad575e88bc6be35024f7600` / `a26c758cfe9a1a79d5b83f459236a27160712a93`). Node v22.16.0 `node --check` 2/2 통과, `node --test tests/p50.test.mjs` **6개 중 3 PASS, 0 FAIL, 3 SKIP**. SKIP은 pinned RAG checkout 필수 통합 테스트여서 **통합 PASS 아님**.
- **CI·PDF/DOCX:** `.github/workflows/citevault-p50.yml` commit `54cd494e47c27a3dd89846d9d02aeda0c955f8f4`에 기존 RAG 원본 `tests/p512-native-document.test.mjs`(PDF 페이지/DOCX 문단 실제 파싱) 실행 추가. 실제 GitHub Actions run/job 로그와 성공 여부 **미확인**. PREP/SMAX Native→인가 AX 실전환, 기업 IAM/ACL/실 Windows/실고객/라이선스도 미검증. P50 매트릭스 참조.
- **계약/출시:** 고객/기밀 원문, 외부 API 호출, 오토 승인, Production/Vercel 배포/상품 게시 없음. `RELEASE HOLD / SALE NO-GO`. 다음은 정확 CI 실행 증거 후 누락 P50 수용조건 구현.

> **상품명: CITEVAULT AX** · 근거형 기업 AI 지식·데이터 검색. 원래 제품명·저장소는 유지.
- 이 브랜치에는 기업 맞춤형 고가 상품 **최종설계·세부 기술·고객 인수/출고·판매/보안 문서**만 추가. 원본 RAG/SMAX/PREP 코드·배포 0건 수정, 이번 제품 테스트 0회.
- `hibi89/RAG_STUDIO@develop` 조회 HEAD `e63e539ab8ded5834cb85672aa2142eb660d3f23`. Private SMAX/PREP 별도 보존.
- 기존 해총 RAG 일반 제품 **95% 잠정**(2026-11-12 CI SHA `0e88301059c9...` 기록), **기업 다중 사용자 제품** 신규 수용 기준은 미검증/재산정 필요.
- 차단: 실제 고객 자료 권리 승인, PREP/SMAX Native 실 운영 연동, 기업 인증/부서 ACL, 실제 로컬 LLM 라이선스/성능, 고객 Windows 설치 및 데이터 라이프사이클.
- RELEASE HOLD / 상용 승인 없음 / Vercel Production N/A(초기 로컬 우선).
