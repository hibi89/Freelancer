# BID AX v2 — 2026-11-14 KST 최신 인수인계 (필수 10항)
1. 목표·확정 요구·기술: 고객 PC 오프라인 BID AX; 나라장터+온비드 공매+사용자 적법 확보 법원경매 원문. Python3.11+ SQLite/Tk, R01–R29 전체 최종설계, 사용자 목표 85%.
2. 완료·결정: 온비드 자료/결과 독립 원장, 법원 TXT/PDF 해시/동의, GUI/CLI, 키 없는 공식 API 3종 요청 검증계획. 개인정보·인증키 외부 유출 방지/고정 서버비 0 목표로 로컬형 유지.
3. 테스트: Linux Python3.13.5 **136/136 PASS**, compileall PASS, Python3.11 AST 22 PASS (실런타임 아님), 비출시 pyz 실제 onbid-plan PASS. GitHub 기능 8/8+4/4 정확 원격 일치. GitHub Python OS CI/Win실기/실 API/실고객 미실행.
4. 완료/진행/차단: 오프라인 3모듈 기술 기능 구현·반영 성공. 공식 최종 85% **미입증**, 공식 UNASSESSED, [작업중] 유지/RELEASE HOLD/크몽 미등록. R01–29 승인 가중치 없음.
5. 실패/원인·회피: 예전 로컬 3모듈 기능 GitHub에 미반영되어 진척을 과장할 위험 → 원격에 반영·본문 12/12 대조로 해소. 여전히 실API 키·권리/고객 Windows 불가·Private Actions 과금 위험으로 무승인 실행 금지. 합성 데이터를 실제 정부 입찰로 보고하지 않음.
6. 저장소/브랜치/SHA·경로: 비공개 hibi89/Freelancer@product/bid-ax-public-procurement. 기능 SHA `2a9852bcb47a271a4119f67dfcaf8ec35ae2a632`, 코드 bidax/{onbid,court,onbid_plan,cli,desktop}.py, 테스트 test_p85_expansion.py/test_onbid_plan.py, 상세 docs/P85_V2_CURRENT_ACCEPTANCE_20261114.md. 문서 HEAD는 원격 readback으로 확인.
7. Production/URL/실행·환경: `python -Werror::ResourceWarning -m unittest discover -s tests -q`; `python -m bidax.cli --db ./local.db gui`, `onbid-import`, `court-import --consent`, `onbid-plan`. 기존 Python pyz 비출시. Vercel/웹 Production 미적용, 실제 Windows EXE 미생성.
8. 원본·백업·보안: 과거 정상 HEAD `1b7b2ef0c00162905b4d0f4116933f682311fb0f`, Git 일반 revert; 사용자 원본DB·타 Freelancer 제품·BID OWL 수정 없음, 로컬 백업/복원 create-only, 비밀/고객자료/원본 API 키 GitHub 전송 0.
9. 다음 우선순위·완료기준·승인: 무료 API 본인 활용신청/권리/서비스키와 실 응답 확인→실 공고100·인간 자격검토10→정확 파서·취소수정/첨부·역할권한·Windows10/11·서명/설치·PDF/고객 수용→R01–29 승인 가중치 전수 검증→85%/판매 판정. 유료 CI·실 데이터/키 전송·출시·권한 변경 사전 승인.
10. 갱신 시점/검증 범위: 2026-11-14 KST, local Linux Python3.13.5·합성/mocked data; API 메타 출처 data.go.kr 15129394/15157220/15157252/15157254와 법원 이용안내. 실 고객/OS/API/권리/CI 미확인, docs 기준 커밋은 원격 확인 후 기록.

---

# BID AX v2 85% 목표 — 오프라인 엔진 로컬 개발 후 원격 코드 동기화 대기 (2026-11-13 KST)
1. 목표·용도·확정 요구: 나라장터+온비드 무료 공식 API + 고객 동의 법원경매 오프라인 자료 분석, R01–R29/29개 최종설계 85% 목표, Python/SQLite/Tkinter.
2. 개발 내용·이유: 오프라인 온비드 원장·증분 이력·물건/결과 조인, 법원 TXT 키워드/해시·PDF 비추출·동의 CLI/GUI 및 합성 예시 구현. 로컬 방식은 서버 비용·기밀 위험이 낮으며, API 실연동/실문서 OCR을 완료한 것은 아님.
3. 테스트·성공/실패: 로컬 Python3.13.5 Linux 총130 PASS/0 FAIL/0 SKIP, compileall·Xvfb Tk/controller·비출시 pyz CLI smoke PASS. 신규 코드 원격 GH/Windows/Python3.11/실 API·고객·법률 수용 NOT_RUN.
4. 상태: 이번 GitHub 문서 변경만. **로컬 소스 ZIP 생성·검증은 완료, GitHub 기능 코드 미반영·동기화 대기.** 공식 최종완성률 UNASSESSED, 85% 미입증, [작업중] 유지, RELEASE HOLD/미등록.
5. 오류/근거/대안: 이 환경의 로컬 산출물과 GitHub connector 사이 파일바이트 전달 단계가 제공되지 않아 신규 코드 원격 커밋 미실행. 검증되지 않은 SHA/CI 성공 주장 금지. 대안: 원본 ZIP을 안전한 개발환경에 가져와 기존 해당 브랜치에 최소 diff로 commit/CI 또는 지원되는 커넥터 파일전송 경로 확보 후 readback.
6. 저장소/브랜치/SHA: hibi89/Freelancer@product/bid-ax-public-procurement, 원격 기능 baseline ab0d92a333a18e01a585a99d6a6b5812ab0c6305; 이전 최종설계 v2 commit ab0d92a333a18e01a585a99d6a6b5812ab0c6305. 로컬 신규 경로 bidax/onbid.py,bidax/court.py,bidax/cli.py,bidax/desktop.py,tests/test_p85_expansion.py,examples/*synthetic.json/TXT. 문서 신규 SHA는 재조회.
7. Production/실행/환경: 로컬 전용, Vercel N/A; python -Werror::ResourceWarning -m unittest discover -s tests -q. 비출시 Python pyz, Windows EXE 미생성·미검증. API 키 없음/외부 전송 없음.
8. 원본·백업·인증관리: 기존 29개 요구 R01–R29 보존, DB와 고객 파일 비수정, ZIP은 민감정보/실고객/인증키 포함하지 않은 소스 증거. Git 변경 전 SHA에서 normal revert 가능; force push·원본 덮어쓰기 금지.
9. 다음 우선순위·완료조건/승인: 로컬 9개 신규/수정 소스·테스트 파일을 GitHub 원격 코드로 동기화 후 정확 blob SHA 검증 → 독립 Linux/Windows Python CI 예산 승인 시 실행 → 온비드 고객 키·실 API 응답과 상용권리 확인, 법원 실 PDF 파서 보안, 실 Windows/고객 인수, R01–R29 100점 승인 가중치.
10. 갱신일·확인범위: 2026-11-13 KST. 본 문서가 증명하는 것은 로컬 합성 테스트와 문서 최신화뿐, 원격 코드/서비스 납품/실 법적 적합 인증이 아님.

---

# BID AX v2 3모듈 최종설계 갱신 — 2026-11-13 KST 인수인계 (10항)
1. 목표/용도/최종기술: 고객 PC 로컬 BID AX 기본 나라장터/확장 온비드 공식 API/프리미엄 법원경매 합법 자료 분석; Python SQLite Tk, 기존 R01–R21 + 신규 R22–R29 (총29), 최종85% 사용자 목표.
2. 변경·결정: 3모듈 최종설계·전수 추적/권리·거래 경계 문서만 추가. 호스팅형은 고객키/원문 관리 부담, 로컬형은 저비용·기밀보호를 우선하되 PC 부재시 자동 알림 불가.
3. 테스트: 기존 Linux Python3.13.5 94 PASS는 역사적 오프라인 모의 수용, 이번 docs-only 변경으로 새 코드/테스트 미실행. API/물리 Windows·고객/저작권 정식 수용 0.
4. 상태: 신규 R22–29 구현0/8; 확장 설계 반영은 완료, 전체 최종 85%는 미입증. 공식 UNASSESSED, [작업중]/RELEASE HOLD/미등록 유지.
5. 오류/전환: 승인된 R01–29 가중치와 실 원문·권리 검증이 없으므로 최종% 계산 불가. 법원 공개 사이트를 무료 API나 허가된 상용 크롤링으로 단정 금지.
6. 저장소·브랜치·SHA·경로: hibi89/Freelancer@product/bid-ax-public-procurement; 변경 전 HEAD 42fa2aaa3e7077721ebfeb10f9bacc09ad109a8b; 최종설계 docs/FINAL_BLUEPRINT.md · docs/BID_AX_EXPANSION_REASSESSMENT_20261113.md, STATUS/HANDOFF/REQUIREMENTS/AGENTS. 신규 HEAD는 커밋 후 조회.
7. Production·환경: 기존 오프라인 CLI/Tk GUI, Vercel N/A. 새 API/유료 서비스/실 고객 전송 없음, Python OS CI는 수동 workflow만 존재(실행 미확인).
8. 원본·백업·보안: 코드/DB·고객키·기존 Bid_Owl/타 Freelancer 상품·중앙 29/19 등록 보존, 원본 수정/강제 푸시 없음. Git 원커밋 SHA로 복구.
9. 다음 우선순위/승인: R01–29 가중치 승인 → 온비드 API별 실제 이용권 및 목록·상세 데이터 확인 → 물건/결과 독립 원장 → 법원 동의 로컬 문서분석 → 실 Windows/고객 권리·상품 인수→판매 승인.
10. 확인일·범위: 2026-11-13 KST; 공식 data.go.kr 15129394,15157220,15157254와 법원 API 안내 페이지 확인; docs-only 정합 검증, 별도 코드 실행 없음.

---
# BID AX P85 acceptance readiness HANDOFF — 2026-11-13 KST (10 required items)
1. **Goal/use/stack:** Local public tender preparation assistant, Python3.11+ SQLite/Tkinter, full R01–R21 design. User target final 85%; approved scoring weights not available.
2. **Implemented/decision:** Existing offline P85 ledger/transport/GUI unchanged; new synthetic 100 tender/5 page interrupted resume and 10 fake review audit/backup tests, manually gated Ubuntu/Windows cross-platform CI blueprint. Local B vs hosted A retained for privacy/cost; no paid workflow automatically triggered.
3. **Tests:** Linux Python3.13.5 94/94 PASS; compileall, Python3.11 syntax AST parse on 20 files, standalone .pyz CLI help PASS. Windows+Ubuntu Python CI three jobs **NOT RUN** (manual-only), actual Python3.11 runtime NOT RUN; real government API/100 notices/10 human cases NOT RUN.
4. **State:** Engineering P85 regression coverage improved; official full final 85% **NOT PROVEN**, official UNASSESSED, [작업중] stays, RELEASE HOLD, unpublished Kmong.
5. **Errors/pivot:** Initial local test incorrectly provided keyword-only request_id as positional; fixed immediately, re-ran entire suite 94 PASS. Mock tests do not validate real legal qualification or official API contract; do not repeat invented successes.
6. **Repository/branch/SHA:** Private hibi89/Freelancer product/bid-ax-public-procurement, prior stable baseline 78247ce6132fc1af2b05cd7fb65729711355caf6. Changed tests/test_p85_offline_volume.py, .github/workflows/bid-ax-manual-acceptance.yml, docs/P85_CROSS_PLATFORM_ACCEPTANCE_PLAN_20261113.md, STATUS/HANDOFF. Read live remote HEAD for final SHA.
7. **Production/commands/environment:** python -Werror::ResourceWarning -m unittest discover -s tests -q. Offline CLI/GUI and unreleased Python .pyz; no Windows EXE, installer, signed delivery or Vercel Production. Manual workflow may consume private Github Actions billable minutes; not executed pending approval.
8. **Originals/backup/security:** Existing customer SQLite DB, secrets/keys, other Freelancer product branches, excluded BID OWL and central catalogue unchanged. Use create-only SQLite restore; Git normal revert from baseline, no force push.
9. **Next priorities/approval:** With approval review Actions budget then manually dispatch workflow on product branch and inspect 3 independent job results. Independently validate official current API terms/raw response, 100 real notices, 10 human qualification reviews, Win10/11 UI/EXE and security, Korean PDF and customer pilot, approved R01-R21 weights before official 85 or launch.
10. **KST/verification scope:** 2026-11-13 KST; Linux mock/synthetic only. Real Python3.11/Windows, live external procurement, independent customer, legal terms and sale remain UNVERIFIED. Updated GitHub source + docs SHA separately confirm.
---

# BID AX P85 보안 후속 인수인계 — 2026-11-13 KST (10항)

1. 목표/최종설계: 사용자 목표 최종 85%; 독립 R01–R21 전체 설계, Python3.11+·SQLite·Tkinter 로컬형.
2. 완료/설계 결정: 완료 배치 사후변조 거부, API 승인값 bool 강제, 오류문의 비밀 URL 차단, 타임아웃 유한 재시도; 호스팅형보다 비용·기밀·지원 범위를 통제하는 로컬형 유지.
3. 테스트: Linux Python3.13.5 로컬 **90 PASS/0 FAIL/0 SKIP**, compileall PASS; 원격 신규 3개 파일 readback, GitHub Python CI/Windows/실 API/고객 검증 NOT_RUN.
4. 완료/진행/차단: P85 오프라인 기술 단계 보강, **공식 최종85% 미입증 → UNASSESSED**, [작업중] 유지, RELEASE HOLD, 미등록.
5. 오류/원인/시도: 네트워크 예외에 고객 인증키 포함 URL 노출 위험 발견; 예외 차단 후 구형 중복 JSON 진단 테스트 1건 충돌 수정, 전체 회귀 90 PASS. 동일 실패 방식 반복 금지.
6. 저장소/브랜치/SHA: Private `hibi89/Freelancer@product/bid-ax-public-procurement`, 이전 HEAD `a5266b4044cfb4217aa620d555094407beaab71e`, 기능 SHA `9a895ad6ac6d47941d0cf5c5a3ec908e4a298947`; `bidax/batch.py`, `bidax/transport.py`, `tests/test_p85_security.py`, `docs/P85_SECURITY_FOLLOWUP_20261113.md`.
7. 배포/환경: Python CLI/로컬 Tk GUI, 실행 `python -m unittest discover -s tests -q`; Windows EXE/실 설치/Vercel Production 없음; .pyz는 Python 필수 비출시용.
8. 원본/백업/비밀: 제외 BID OWL·타 Freelancer 브랜치·중앙29/19 상품·공고DB 변경 없음; Git 이력으로 복원. 고객 API 키/PII/고객원본 업로드·외부 호출 금지.
9. 다음 작업/완료조건/승인: 사용자 본인 실 API 키·현재 API 운영권리/원문·첨부 확인, 실공고100·자격10 대조, Win10/11+3.11/EXE·한글 PDF/암호화·실고객 검증, R01–R21 승인 가중치 독립 수용. 확인 전 공식률/출시 변경 금지.
10. 갱신/증거 범위: 2026-11-13 KST; 신규 SHA 원격 확인, 90건은 로컬 mock/합성 기준이며 GitHub CI·실정부 API·Windows·고객·계약권은 미검증.

---

# BID AX P85 latest HANDOFF — 2026-11-13 KST (10 items)

1. **목표·용도·최종설계·스택:** 공공입찰 준비 로컬 고객용 BID AX, 고객확정 R01~R21 전체 100% 기준/이번 목표 85%; Python3.11+·SQLite·Tkinter, 고객 보유 API 키의 선택형 호출(현재 실행 안 함).
2. **완료·변경·선택 근거:** 오프라인 정규화·공고 이력·기업 프로필·서류/마감·보고서·GUI·백업 유지하면서 UUID/page/7일/총건수 스테이징·재시작 복구, SQLite 중복 알림, 공식 호스트 고정 mock 전송·일일 요청예산·신중한 재시도, 수동 Windows 패키징·화이트리스트 소스 ZIP 추가. 서버형 대비 로컬형 비용/보안 우선.
3. **테스트·검증 범위:** Linux Python3.13.5 synthetic+mock `python -Werror::ResourceWarning -m unittest discover -s tests -q` **83 PASS/0 FAIL/0 SKIP**, compileall PASS, Tk8.6 Xvfb 기본 실행 PASS. 원격 CI/Windows3.11/EXE/실API/고객/법적 실확인 NOT_RUN. 커밋 이후 Git blob/SHA 확인.
4. **완료/진행/대기/차단:** P85 로컬 기술 준비 일부 수용, 공식 최종 **85% 미입증→UNASSESSED**, `[작업중]`·RELEASE HOLD·미등록 계속. 실제 나라장터 100건/자격 10건·Windows·승인 가중치 필요.
5. **실패·근거·Pivot:** 최초 소스 ZIP 테스트는 설치된 `packaging` 패키지와 동일 이름 import 충돌 → importlib 지정 경로로 교정 후 80 PASS. 국가 API 실키·실원문 매핑·운영 한도/저작권 재검증 없음; 고객 자격 자동 적합/자동 입찰 주장 금지. 반복 실API 접속은 키·승인 전 금지.
6. **저장소·브랜치·SHA·경로:** Private `hibi89/Freelancer@product/bid-ax-public-procurement`, 직전 HEAD `766032d6256d634469366b1125639f9aa9a6ef1c`, 새 코드 `bidax/{batch,reminders,transport,entrypoint,cli,desktop}.py`, `tests/test_p85.py`, `packaging/*`, `docs/P85_STAGE_EVIDENCE_20261113.md`, 각 STATUS/HANDOFF. 최신 SHA 원격 readback값 사용.
7. **Production/환경:** 로컬 CLI `python -m bidax.cli --db PATH ...`, GUI `gui`; Windows EXE 빌드는 **수동 스크립트만** 제공, PyInstaller 별도 설치 필요. Vercel Production/도메인 미적용; 운영 중 무인 수집 없음.
8. **원본·백업·인증/금지:** 제외 BID OWL·기타 Freelancer product 브랜치 및 29개 원천/19개 서비스·고객 DB/키 무수정. SQLite 원본 보존·새 경로로만 복구, Git 전 버전 SHA로 코드 복원. 민감정보 소스 ZIP/GitHub 제출 금지. 실제 API 키는 앱에 기록하지 않음.
9. **다음 작업·승인·완료기준:** 공식 응답과 권리/고객 키 확인 → 100건/10건 출처 독립 검토 → Python3.11 Windows10/11 GUI/EXE/복구/문서/서명·접근제어 → R01~R21 승인 가중치 전수 독립 수용 → 공식률 확정. 출시/배포/고객 데이터 전송/유료 CI 별도 승인.
10. **KST·확인시점·검증:** 2026-11-13 KST; 로컬 Python3.13.5 합성+mock 80/80, compileall, Tk Xvfb. 외부 API 호출/Windows/실고객/패키징 0건, GitHub 소스 및 중앙 반영은 각 commit 후 정확 SHA를 별도 검증.

---

# BID AX — handoff for next chat (10 required sections; 2026-11-13 KST)

1. **Goal/scope/requirements/stack:** BID AX public procurement preparation, separate from excluded BID OWL; 21 full-scope requirements R01–R21 (`docs/FINAL_BLUEPRINT.md`), strict source/human provenance, preliminary 3-state output, local Windows Tkinter GUI + Python3.11+ SQLite. Owner task: **final completion 70% goal**, not approved realized percentage.
2. **Completed/decision rationale:** Existing offline 50-stage normalized notice, immutable source fingerprint, company validation, 7-day API plan, SQLite/JSON/backup preserved. Added on-demand deadline reminders, field-level change diff, append-only human review with UUID idempotency and stale-source checks, create-only backup/restore, JSON/CSV/HTML reports (formula/injection defense), bounded local JSON and Tkinter GUI. Hosted A vs local B compared; B retained for zero mandatory server cost, privacy, maintainability; PC must run to notify.
3. **Testing/evidence:** Linux Python 3.13.5 `python -Werror::ResourceWarning -m unittest discover -s tests -v` **45 PASS / 0 FAIL / 0 SKIP**, GUI Tk8.6 `xvfb-run` launch/close smoke `TK_GUI_SMOKE_PASS`, CLI import→screen→report→review→history→backup→restore E2E PASS; previous 19 still pass. GitHub remote blob readback/CI to verify separately. Actual Windows10/11, real source/customer/authorization/PDF & EXE/Production NOT_RUN.
4. **State and stop point:** Current **P70 offline engineering milestone locally reached**, not full product 70%; official final completion `UNASSESSED` due no approved 21-requirement weights and major full-scope gaps. `[작업중]` **retain until user goal proven**, RELEASE HOLD, no Kmong listing, no production deployment.
5. **Errors and alternatives:** Earlier SQLite resource warnings resolved by explicit closing; 45-suite with warnings-as-errors clean. No current API credentials or verified live response contract, so next pivot is controlled authorized fixture mapping/real user API after approval, never unauthorized scrape or infer legal eligibility. Tests exercise synthetic data and fail closed on missing proof.
6. **Repository/branch/SHA/paths:** PRIVATE `hibi89/Freelancer@product/bid-ax-public-procurement`; old P50 source commit `d614c08e611ef15d388865034ada215e10c8da6e`. New exact commit verify after GitHub write. `bidax/{core,cli,workflow,desktop}.py`, `tests/test_{core,stage70}.py`, `docs/{FINAL_BLUEPRINT,P70_STAGE_EVIDENCE_20261113}.md`, STATUS/HANDOFF/AGENTS/REQUIREMENTS/README, `.gitignore`.
7. **Production/URL/environment:** Local Windows-targeted Python/Tkinter/SQLite only; run `python -m bidax.cli --db ./local.db gui`, test with `python -m unittest discover -s tests -v`; no Vercel/production endpoint. Linux Tk smoke is not Windows acceptance. Python 3.11 declared target but 3.13.5 tested locally; CI no verification yet.
8. **Backups/originals/security:** Existing product branches, central 29/19 catalog, official registration history, old BID OWL and original hackathon sources must remain unchanged. Git previous SHA for rollback. SQLite backups/restores always to new paths, no database overwrites, source fingerprints validated before review. No secrets/keys/PII uploaded, no authorized third-party data fetched.
9. **Priority/next acceptance and approvals:** Need exact GitHub source readback→hub record update (separate concurrency-safe ref); then obtain owner-approved R01–R21 weights and independent trace. Technical next: authorized official API response, quota/retry, actual 100 notices + 10 human cases, multi-profile/security migration, scheduler resume, Windows installer GUI/PDF/rights/customer test before release. Never remove work marker on P70 synthetic milestones.
10. **Timestamp and verification coverage:** 2026-11-13 KST, local Python 3.13.5/SQLite/Tk8.6 under Linux Xvfb. Updated GitHub SHA and hub status only to be claimed after exact remote verification. Detailed checklist [`docs/P70_STAGE_EVIDENCE_20261113.md`](docs/P70_STAGE_EVIDENCE_20261113.md).
