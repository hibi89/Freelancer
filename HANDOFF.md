# BID AX 공식 API 수집 격리검증 인수인계 — 2026-11-14 KST (필수 10항)
1. 목표/용도/기술: 최종설계 R01~R29 전체 100% 고정(가중치 추가 요구 없음), 목표85%, Python/SQLite/Tk, 나라장터1+온비드3 공통 본인인증키와 합법 법원 자료 로컬 분석.
2. 완료/결정: 오프라인 격리 응답 구조·페이지/총건수/본문 형식·SHA 변경·인증키 JSON/URL 반사 안전검증과 CLI 추가; raw를 심사 엔진에 자동 승격하지 않음. 고객 PC 로컬 방식/서버비0 목표 유지.
3. 테스트: Linux Python3.13.5 기존188+신규13=201 PASS/0FAIL/0SKIP, compileall/pyz 계획 스모크 PASS. 실제 정부 HTTP·본인 키·공고100·인간 검토10·Win10/11 고객 시험 0/미검증.
4. 상태: 로컬 응답 계약 감사 기능 구현 완료, 공식 85% 미입증/UNASSESSED, [작업중], RELEASE HOLD, 미등록.
5. 실패/근거·피벗: 미확인 온비드 15157220 세부 operation 경로 임의 추정 금지, ready=false. 기관 JSON 형식·이용권/원문 정밀 확인은 실 사용자/키 없이 미검증. 테스트 증가만으로 최종률 계산하지 않음.
6. 저장소·브랜치/SHA: private hibi89/Freelancer@product/bid-ax-public-procurement, 전 HEAD e3ffb4fa1a6c20f640746f990cef5f0f9e88f8b3; bidax/{api_gateway,response_audit,cli}.py, tests/test_api_response_audit.py, docs/P85_API_RESPONSE_QUARANTINE_AUDIT_20261114.md. 최신 HEAD는 커밋 후 조회.
7. Production/실행·환경: `python -Werror::ResourceWarning -m unittest discover -s tests -q`; `python -m bidax.cli --db local/bidax.db api-inspect local/result_001.json` 은 오프라인; api-probe --live 는 사용자 PC 명시동의/키 입력 필요. Vercel/Production N/A, Windows EXE 미검증.
8. 원본/백업·보안: 원본코드/고객 DB·원문 키/기존 BID OWL 타제품 비수정, Git normal revert. Gitignore local/격리파일 추가; 실 키/실 자료 GitHub 업로드 금지. 저장된 canonical hash는 전자서명 아님.
9. 다음 우선순위·완료기준/승인: 사용자 PC에서 4개 승인 API의 1페이지 실 요청(키 노출 없이), 15157220 공식 operation 명세·실 항목 매핑, 실공고100/인간 자격검토10, Windows3.11/EXE/PDF·고객/권리·지원, R01–29 전체 독립 수용 후 85% 판정. 유료 CI/실고객 전송/출시/권한변경 승인 전 금지.
10. KST 시점/검증 범위: 2026-11-14, 공식 data.go.kr 15129394/15157220/15157252/15157254 메타데이터와 로컬 mock 201 PASS에 한정. GitHub source SHA·중앙 동기화 사후 readback 별도.

---

# BID AX API 공통키 게이트 개발 인수인계 — 2026-11-14 KST (필수 10항)
1. 목표·최종설계·스택: BID AX R01–R29 사용자 고정 100% 기준, 목표85%; 나라장터+온비드 API와 합법 법원 로컬자료. Python/SQLite/Tk, 고객 PC 월서버비0.
2. 변경·근거: 공공데이터포털 4개 각각 승인, 동일 키 확인. 키는 호출 때 단 1회 임시 입력·저장 안 함. G2B/온비드 결과목록/상세 host/operation 고정; 불확실 15157220 path 차단. SaaS보다 고객 PC 수동 조회 선택(개인정보/비용 감소).
3. 테스트: Python3.13.5 Linux 오프라인 가짜 HTTP 총188/188 PASS(기존167+신규21), compileall 및 Python zipapp api-probe dry-run PASS. GitHub SHA·Actions는 새 커밋 뒤 확인. 실정부 HTTP 0, 고객키0, Windows/고객 미검증.
4. 상태: 오프라인 API 연결기·CLI 완성, 실 응답 연동/공식 스키마·원문/납품 권리는 미검증. **전체 공식률 UNASSESSED / 85% 미입증 / [작업중] / RELEASE HOLD / 미등록**.
5. 장애·대안: SQLite 자원경고는 테스트 connection 누락 및 새 예산 커넥션 정리 후 188 PASS. 15157220의 operation 이름 미확인→임의 추측 대신 차단. 실키/실 API·사용자 외부 전송 전 별도 승인/PC 수동 테스트만.
6. repo/branch/SHA: private hibi89/Freelancer@product/bid-ax-public-procurement, 변경 전 HEAD 04d5b5e563be70ff32b08e49ea46c6e3f37693e9; 새 bidax/api_gateway.py, cli.py, tests/test_api_gateway_shared_key.py, examples 3개, docs/API_GATEWAY_SHARED_KEY_20261114.md, STATUS/HANDOFF/README. 새 SHA는 readback 확인.
7. 실행·환경·Production: python -Werror::ResourceWarning -m unittest discover -s tests -q; python -m bidax.cli --db LOCAL_DB api-probe onbid_result_list examples/onbid_result_list_plan_LOCAL_ONLY.json(무HTTP); --live --out NEW_PATH는 고객 동의 키 입력. Windows/EXE 미실행, Vercel/배포 N/A.
8. 원본·백업·인증: 기존 transport.py/G2B/온비드/법원 원장·BID OWL/다른 제품/고객 DB 불변. 키/실데이터 GitHub 업로드 금지. Git normal revert from 04d5b5e563be70ff32b08e49ea46c6e3f37693e9; force push 금지.
9. 다음 우선순위: 15157220 공식 오퍼레이션 확인, 승인된 로컬 키로 각 서비스의 소량 실 응답을 사용자 PC에서 별도 허가 후 확인, pagination/실원문 정규화·100건/10인간, Win10/11/설치/상용권리/고객인수. 사용자 고정 최종완성률 기준 유지, 가중치 승인 재요구 금지.
10. 갱신 기준: 2026-11-14 KST, Python3.13.5 Linux fake HTTP 검증만. 서비스 명세 data.go.kr 15129394,15157220,15157252,15157254; 188/188 테스트·원격 브랜치 HEAD는 각각 별개 근거.

---

# BID AX 2026-11-14 최종설계 85% 목표 후속 인수인계 (필수 10항)
1. 목표/용도/확정설계/스택: R01–R29 29개 완제품 100% 기준, 나라장터+온비드 공식API+동의 받은 법원자료 분석, 로컬 Python/SQLite/Tk; 최종 85% 사용자 목표.
2. 변경/설계: 온비드 관심목록·감사 이벤트·UUID 멱등·변조/버전 경고·필터, 3원천 통합 현황 GUI/CLI/pyz. 기존 로컬형을 유지(서버비 0 목표, 비밀/개인자료 불송신). 다른 원본 기능·BID OWL 무변경.
3. 테스트/실증: Linux Python3.13.5 167/167 PASS, compileall/Tk smoke PASS, 비출시 zipapp CLI subprocess PASS, 소스 코드 Git blob 3/3 일치. Python GitHub CI/Windows10/11·실정부 API/고객 NOT_RUN.
4. 상태: 기능 추가 및 원격 코드 동기화 완료, 전체 공식 완성률 UNASSESSED(85% 미입증), [작업중] 유지/RELEASE HOLD/크몽 미등록.
5. 장애/근거·Pivot: 통합 현황에서 미등록 SQLite DB에 테이블 자동 생성 위험을 사전 검출→출처별 스키마 게이트, 없는 원장은 빈 항목. 초기 regression 1 FAIL을 재설계/복구해 167 PASS, 동일 실패 방식 반복 금지.
6. 저장소·브랜치·SHA·경로: hibi89/Freelancer@product/bid-ax-public-procurement, 기능 SHA `8aa19f3aa4873ff17ecc188a097bd1c59f146a7b`, 포트폴리오 소스/CLI/GUI, tests/test_portfolio_watchlist.py/tests/test_portable.py, docs/BID_AX_FULL_BLUEPRINT_29_ACCEPTANCE_20261114.md; 최종 HEAD 재확인.
7. Production·실행/환경: python -Werror::ResourceWarning -m unittest discover -s tests -q; python -m bidax.cli --db DB portfolio-report 및 onbid-filter/watch/watchlist. Vercel N/A, Windows EXE/실배포 없음.
8. 백업/원본·보안: 기존 정상 코드는 parent SHA 및 git 정상 revert로 복구, 고객 SQLite 삭제/이관·API키/개인정보 전송 없음. 감사 이력은 append-only, 파일 해시 검증 및 데이터 출처 분리.
9. 다음/승인·완료기준: 29개 요구별 배점 제안 사용자 승인 전 공식 숫자 금지; 나라장터/온비드 무료 API 발급 및 권리·실응답 100건/사람 검토10건, 실제 Win10/11 EXE/보안·고객 인수, 상용약관; 유료 Actions/외부전송 사전승인.
10. KST·확인시점/범위: 2026-11-14, 합성 로컬 테스트와 원격 3개 코드 Blob, 사용자 최종설계 29개 증거표만 확인. 실 OS/원문/권리 미검증, 이번 기준 커밋은 최신 브랜치 조회 필요.

---

## [2026-11-14 KST] P85 PDF 원격 SHA 및 최종 인수인계 보정
- 소스 기능 SHA **2de90f3e1231d945b8fcec322f02194003b37098**, remote **11/11 exact matches**, Author/Committer 연결 hibi89. GitHub blueprint-only CI #43504668031 SUCCESS; Python CI 미실행(비용·승인), 고객 Windows/API/100원문/10전문가 미검증.
- Linux Python3.13.5 **151 PASS 0 FAIL 0 SKIP**, ReportLab4.4.9/pypdf5.9.0 선택 패키지에서 PDF 생성·동의·암호화/주석/손상 거절. 실제 라이선스/폰트/고객 PDF 수용 미검증. R01–R29 공식 UNASSESSED, 85 목표 [작업중] 유지, RELEASE HOLD.
- 소스 복구 기준 이전 d295a8869689272f14a37864716e69093d5ca351, 새 문서 HEAD는 GitHub branch 조회. 비밀/고객 파일/타 브랜치·BID OWL 변경 없음.

---

# BID AX P85 PDF 후속 인수인계 — 2026-11-14 KST (10항)
1. 목표/용도/최종설계: 나라장터+온비드+법원경매 고객 로컬 문서, R01–R29 전체 기준 최종85% 목표, Python/Tk/SQLite.
2. 완료/설계: 로컬 한국어 PDF 근거 보고서(ReportLab 선택), 법원경매 PDF/TXT 동의 기반 범주형 단어 미리보기(pypdf 선택), 기존 메타 원장 보존. SaaS 비용/비밀전송 리스크보다 로컬 기능 우선.
3. 테스트: 이전 136 PASS + 신규15 PASS = Python3.13.5 Linux 151/151 PASS, compileall PASS. ReportLab4.4.9/pypdf5.9.0 선택패키지 로컬 설치에서만 PDF 테스트 동작. GitHub SHA/CI는 후속 확인.
4. 상태: R13/R27–28 보강, 전체 R01–R29 공식률 UNASSESSED(가중치 미승인), 85% 목표 [작업중]·RELEASE HOLD·미등록.
5. 오류/원인/전환: 로컬 합성·선택 패키지 검증만으로 실제 고객 Windows 폰트/법원 문서 적법성/공공 API 권리를 입증 못함. 실패/누락 문서 및 스캔 PDF는 REVIEW_HOLD, 자동 법률판정 금지.
6. 저장소/브랜치/SHA: hibi89/Freelancer@product/bid-ax-public-procurement, 이전 HEAD d295a8869689272f14a37864716e69093d5ca351. 경로 bidax/{pdf_report,court,cli,desktop,workflow}.py, tests/test_pdf_court_preview.py, docs/P85_PDF_LOCAL_ACCEPTANCE_20261114.md. 새 SHA는 원격 확인 후 적용.
7. Production/환경: Python3.13.5 Linux 테스트, 추가 선택 ReportLab/pypdf; OS 폰트 파일 번들 미포함; Vercel N/A, Windows EXE/서명/고객 납품 미실시.
8. 원본/백업/인증: 기존 DB·고객자료·API 키·원본 BID OWL·타 브랜치 불변. Git 기존 HEAD와 새 경로 SQLite 복구 유지. 제3자 폰트 라이선스/개인정보/고객 동의 사전 확인.
9. 다음 작업/승인: 고객 키/공식 API 무료 활용신청·상업권, 실제 공식 응답·100공고·10인간 대조, Win10/11 GUI/PDF/EXE/복구, 사용자 승인 R01–29 가중치 및 출시승인. 임의 유료 CI·외부전송·고객 파일 공유 금지.
10. 갱신일/검증범위: 2026-11-14 KST; 개발자 로컬 151 테스트와 PDF parser dry run, 외부/고객/실OS/법률 검증 미실시, 신규 GitHub/중앙 커밋 확인 후 확정 보고.

---

# BID AX 2026-11-14 소스 ZIP 참고 안내

최신 완전한 인수인계는 GitHub product/bid-ax-public-procurement/HANDOFF.md 정본 사용. 코드 SHA 2a9852bcb47a271a4119f67dfcaf8ec35ae2a632; 136 PASS는 Linux 모의 테스트이며 실 제품 완성률은 UNASSESSED, 목표 85% 미인증. 3모듈 R01–R29 전체 설계, 고객 데이터/키/실 Windows/무료 API 연동 검증은 별도 승인/자료 필요. 아래 본문은 이전 단계의 이력입니다.

---

# BID AX P85 보안 후속 인수인계 (2026-11-13 KST, 10항)

1. **목표/기준/기술:** 사용자 지정 공식 최종 85% 목표; `docs/FINAL_BLUEPRINT.md` R01–R21 전체 분모, Python3.11+ 목표/SQLite/Tkinter.
2. **완료/선택:** 로컬 P85 83건 베이스 유지, 완료 배치 전체 페이지 SHA 재검증과 opt-in API 전송 승인값·에러 비밀 보호·KST 날짜 전환 재시도 예산 보강. 고객PC 로컬형 유지(서버형 대비 비용·보안 우위, PC 중단 제한).
3. **테스트:** 로컬 Linux Python3.13.5 unittest **90 PASS/0 FAIL/0 SKIP**, compileall PASS, 이번 추가 7/7. GitHub 원격 SHA/CI는 별도 readback, Windows/실 API/실 고객 **미검증**.
4. **상태:** 오프라인 P85 엔지니어링 부분 수용. 공식 최종 85% 미입증 → **UNASSESSED**, `[작업중]` 유지, RELEASE HOLD/미등록.
5. **오류/원인/수정:** 예상밖 urllib opener 예외에서 URL/키 노출 가능성 → 일반 오류로 치환, 기존 중복 JSON 키 진단 테스트와 충돌 1회 → 안전한 해당 메시지만 명시 유지한 뒤 전체 90 PASS. 최초 실패 상태는 반복 성공 주장 금지.
6. **저장소/SHA/경로:** Private `hibi89/Freelancer@product/bid-ax-public-procurement`, 수정 전 HEAD `a5266b4044cfb4217aa620d555094407beaab71e`; `bidax/batch.py`, `bidax/transport.py`, `tests/test_p85_security.py`, `docs/P85_SECURITY_FOLLOWUP_20261113.md`, STATUS/HANDOFF. 새 커밋은 원격 확인값 참조.
7. **배포/환경:** `python -Werror::ResourceWarning -m unittest discover -s tests -q`, GUI `python -m bidax.cli --db PATH gui`; Windows EXE/설치/Production/Vercel **미적용/미검증**.
8. **원본/보안/백업:** 기존 배치·공고 이력/새 DB 복구·BID OWL·타 제품/중앙 원장 보존, Git 이전 SHA로 소스 복원. 실 키·고객DB·비밀·실 API 요청은 하지 않음.
9. **우선순위/승인:** 실 API/권리/운영키, 100원문·10자격, Windows10/11+Python3.11 실기기·EXE·한글PDF/설치, 고객 인수와 R01–R21 가중치 독립승인. 확인 전 공식률 변경/판매/배포 금지.
10. **일시/검증범위:** 2026-11-13 KST, 로컬 합성·mock 90 PASS. 새 GitHub 기능커밋·중앙 동기화는 각각 원격 readback 후 확인해야 한다.

---

# BID AX P85 latest HANDOFF — 2026-11-13 KST (10 items)

1. **목표·용도·최종설계·스택:** 공공입찰 준비 로컬 고객용 BID AX, 고객확정 R01~R21 전체 100% 기준/이번 목표 85%; Python3.11+·SQLite·Tkinter, 고객 보유 API 키의 선택형 호출(현재 실행 안 함).
2. **완료·변경·선택 근거:** 오프라인 정규화·공고 이력·기업 프로필·서류/마감·보고서·GUI·백업 유지하면서 UUID/page/7일/총건수 스테이징·재시작 복구, SQLite 중복 알림, 공식 호스트 고정 mock 전송·일일 요청예산·신중한 재시도, 수동 Windows 패키징·화이트리스트 소스 ZIP 추가. 서버형 대비 로컬형 비용/보안 우선.
3. **테스트·검증 범위:** Linux Python3.13.5 synthetic+mock `python -Werror::ResourceWarning -m unittest discover -s tests -q` **80 PASS/0 FAIL/0 SKIP**, compileall PASS, Tk8.6 Xvfb 기본 실행 PASS. 원격 CI/Windows3.11/EXE/실API/고객/법적 실확인 NOT_RUN. 커밋 이후 Git blob/SHA 확인.
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
