# STATUS — 2026-11-14 KST 실제 Windows EXE 3차 재실행 기존 거래처 GUI 복원 PASS (최신)

- 사용자 콘솔 `$p3 = [System.Diagnostics.Process]::Start($psi2)` 후 `$p3.WaitForExit()`, **`ExitCode: 0`**, 사용자 육안 보고 “그대로있더라”: 이전 생성한 합성 `WORKNOVA_QA_TEST_01` 거래처가 **세 번째 Windows onedir EXE 프로세스의 Tk GUI에 그대로 표시**. 동일 자식 임시 `LOCALAPPDATA=$qaRoot` 사용. 전회차 2차 EXE에서 GUI 생성·종료 후 SQLite 읽기전용 `SyntheticCustomerCount:1`, `integrity_check:ok`와 연결되어, **생성→저장→종료→재시작 후 기존 목록 복원** 실제 Windows 사용자 검증 PASS. 3차 별도 스크린샷/재SQL은 미수신, 사용자 현장 육안 보고. 증거 `docs/P85_WINDOWS_EXE_BUILD_RESULT_20261114.md`.
- **미검증:** GUI 견적/계약/납품/수금 업무 종단·감사/권한 보안·무Python 타기기·서명/Defender·활성 DB 암호화/OS ACL·Word/PDF 상용권/실고객·법률. WD01/08/09/11/13 부분 검증 보강, 승인 WD01~14 고정 100점 완전 인수 정식 합 **0/100(구현률0 아님), 85 미달, [작업중], RELEASE HOLD, 크몽 미등록**.
- 실고객 장부/OS 정책·원본/타 상품/등록완료/유료 CI 변경 없음. 추가 설치·빌드 반복 불필요. 다음은 **합성 견적 생성/승인→계약→납품/수금**의 독립 실기기 업무 E2E 단계.

---

# STATUS — 2026-11-14 KST 네이티브 EXE 2차 실행·GUI 거래처 저장·종료 후 DB 지속성 PASS (최신)

- 소유자가 처음 실행 후 종료된 같은 `TEMP/worknova-gui-qa-<GUID>` 격리 `LOCALAPPDATA`로 실제 `WORKNOVA-Desk.exe`를 **두 번째 실행**. GUI '새 거래처'에서 `WORKNOVA_QA_TEST_01`을 생성했고 화면에 이름+임의 ID 및 `완료(로컬 기록)` 표시. 이후 X로 종료, PowerShell **`ExitCode: 0`**, 같은 `desk.sqlite` 읽기전용 조회 **`SyntheticCustomerCount: 1`**, **`integrity_check: ok`** 확인. 이는 **실 Windows EXE 재실행·한 건 GUI 입력·디스크 저장·종료 후 지속성·DB 무결성 PASS(사용자 콘솔/화면 증거)**. 원격 증거 `docs/P85_WINDOWS_EXE_BUILD_RESULT_20261114.md`, 원본 스크린샷/SQLite 실파일은 개인정보 방지로 업로드하지 않음.
- **여전히 미검증:** 세 번째 EXE 구동의 거래처 목록 복원 화면, 견적/계약/납품/수금 업무 E2E·감사로그 정확성, Python 없는 타PC에서 onedir 이동·Windows ACL/활성 DB 암호화·서명/Defender·Word/상업 폰트/실고객·법률 수용. 사용자 승인 WD01~14 총100점은 **항목 전체 고객 수용** 기준만 점수 인정, WD01/08/09/11/13 부분 PASS이나 정식 합 **0/100(구현률0 아님)**·85 미달, **[작업중]/RELEASE HOLD/미등록**.
- 실제 고객 장부·OS 보안 설정·원본 repo/타 제품·등록완료·유료 CI 변경 없음. 이전 빌드·해시·MZ·기본 Tk·SQLite v2 PASS 증거 유지.

---

# STATUS — 2026-11-14 KST 실제 Windows 격리 SQLite integrity_check ok / user_version 2 PASS (최신)

- 소유자 콘솔 실제 Windows Python3.11에서 앞선 EXE 실행으로 생성된 새 TEMP `desk.sqlite`를 `mode=ro`로 열어 `PRAGMA integrity_check` → **`ok`**, `PRAGMA user_version` → **`2`** 확인. 이번 검사는 데이터 파일 기존 내용 수정하지 않음. 기존 EXE onedir 빌드/7,107,722 bytes·SHA256 `A7CD6B052108E5630E4AD50151841F0B812654F22E87CFE8338E22CB12A5C23E`/MZ PASS → GUI 표시→ExitCode0 → 새 격리 DB 존재까지의 실 Windows 사용자 보고 증거 연장. [자세한 기록](docs/P85_WINDOWS_EXE_BUILD_RESULT_20261114.md).
- **남은 미검증:** 거래처 CRUD/버튼 E2E/DB 재실행 지속성·감사로그, Python 없는 다른 PC·Windows ACL/활성 DB 암호화/서명·Defender/실고객 법무·글꼴 권리. 사용자 승인 WD01~14 전체100 완전 인수 배점 불변, WD08/09/11/13 부분 실증에도 정식 **0/100(구현률 0 아님), 85 미달, [작업중]/RELEASE HOLD/미등록**. 고객 실제 장부·OS 보안·원본 타상품 변경 없고 유료 비용0.

---

# STATUS — 2026-11-14 KST Windows EXE 종료코드 0 / 격리 SQLite 파일 존재 PASS (최신)

- 실제 소유자 Windows PowerShell에서 `ProcessStartInfo.UseShellExecute=false`, EXE 자식 프로세스의 `LOCALAPPDATA`만 새 `TEMP/worknova-gui-qa-<GUID>` 폴더로 분리하여 실행, 새 빈 장부 확인 후 실제 Tk 메인 GUI 표시→X 종료→`WaitForExit()` 완료. 사용자 콘솔 **`ExitCode=0`, `TestDatabaseExists=True`**(`WORKNOVA Desk/Data/desk.sqlite` 경로) 확인. 이것은 실제 Windows **EXE 기본 GUI 실행·정상 종료·격리된 새 SQLite 파일 생성 PASS** 증거이며, 사용자가 제공한 콘솔 결과에 의존. 기존 Win onedir 빌드 PASS·EXE 7,107,722바이트·SHA256 `A7CD6B052108E5630E4AD50151841F0B812654F22E87CFE8338E22CB12A5C23E`·MZ PASS와 연결. [근거](docs/P85_WINDOWS_EXE_BUILD_RESULT_20261114.md).
- **남은 미검증:** SQLite 무결성/업무 테이블·거래처 CRUD·재실행 데이터 보존, onedir 타PC 배포·Python없는PC, OS ACL·상시 DB 암호화·서명·Defender/SmartScreen·상업권/Word/고객·법무 수용. 단순 파일 존재를 기능 전수 PASS로 계산하지 않는다. 고객 원본/OS 정책·타상품 변경 없음.
- 사용자 승인 WD01~14 최종 100점 각 항목 완전수용 채점 불변, WD11/13 부분 검증 진전에도 공식 **0/100(구현률0 의미 아님), 85점 미달, [작업중], RELEASE HOLD, 크몽 미등록**.

---

# STATUS — 2026-11-14 KST 네이티브 Windows EXE 실제 Tk 메인 GUI 표시 증거 (최신)

- 사용자 제공 스크린샷에서 **WORKNOVA Desk — 로컬 계약·납품 장부** 메인 창이 Windows에서 실제 열린 것을 확인. 한글 안내·거래처 검색/새 거래처, 4개 업무 탭, 견적·계약·납품·수금·백업·암호화 복원 등 GUI 컨트롤이 그려짐. 이전 `onedir` EXE 빌드·7,107,722바이트·SHA256 `A7CD6B052108E5630E4AD50151841F0B812654F22E87CFE8338E22CB12A5C23E`·MZ PASS, 첫 장부 생성 팝업을 잇는 실제 GUI 구동 증거. 스크린샷 원본은 개인 UI가 있어 GitHub 업로드하지 않고 텍스트 관찰만 기록: `docs/P85_WINDOWS_EXE_BUILD_RESULT_20261114.md`.
- **검증대기:** 형이 창을 닫은 뒤 PowerShell `ExitCode` 및 `TestDatabaseExists` 출력. 메인 GUI 화면 확인만으로 임시 SQLite DB 생성/존재/재실행, 버튼 전수 기능, Windows ACL/DB 암호화·서명·Defender·Python 없는 PC 이식, 실제 고객/법률/라이선스 수용을 PASS로 처리하지 않는다. 기존 고객 자료/환경설정 변경 증거 없음.
- 사용자 승인 WD-01~14 정식 전체100·완전 구매자 수용 배점만 인정. WD-11/13 GUI 표시 **부분 검증**, 전체 인정 **0/100**(구현률0 뜻 아님), 목표85 미달, **[작업중]/RELEASE HOLD/크몽 미등록** 유지.

---

# STATUS — 2026-11-14 KST EXE 파일 해시/크기/MZ 사용자 실기기 증거 확보 (최신)

- 사용자 제공 같은 실제 Windows `WORKNOVA-Desk.exe` 파일에서 **Length 7,107,722 bytes**, **SHA256 `A7CD6B052108E5630E4AD50151841F0B812654F22E87CFE8338E22CB12A5C23E`**, 최초 두 바이트 `MZ header: PASS` 확인. 앞선 PyInstaller6.22.3 onedir EXE/COLLECT `Build complete!` 및 파일 존재의 후속 검증. 증거 `docs/P85_WINDOWS_EXE_BUILD_RESULT_20261114.md`. 사용자 콘솔 로그 기반이며 바이너리 파일 본문 직접 수신·별도 재해시 아님.
- **아직 미검증:** 실행/WORKNOVA Tk GUI 표시·첫 빈 장부/거래처 저장·재실행 데이터 유지, Python 없는 타PC 이식, 전체 PE/코드서명·Defender, Windows 폴더 ACL·활성DB 암호화·상용권/고객법률 수용. 다음은 자식 프로세스의 `LOCALAPPDATA`만 새 TEMP 디렉터리로 격리한 GUI 실행; 실제 고객 장부·운영 환경 변수 미변경.
- 승인 WD01~14 고정100점 중 항목 전체 수용 PASS 조건 유지, WD13 빌드+파일 기본 무결성은 **부분 수용/0점**, 정식 **0/100(구현률0 의미 아님), 목표85 미달, [작업중]/RELEASE HOLD/크몽 미등록**. 별도 유료 배포/OS 보안 수정/원본·타상품 변경 없음.

---

# STATUS — 2026-11-14 KST 사용자 Windows onedir EXE 실제 빌드 성공(최신)

- 사용자 제공 Windows 10.0.26200 / Python3.11.9 / PyInstaller6.22.3 PowerShell 로그: 기존 `--plan`으로 생성된 PyInstaller 인자를 직접 실행, `Building EXE completed successfully`, `Building COLLECT completed successfully`, `Build complete!` 및 `WORKNOVA-Desk.exe` 파일 존재 확인. 이전 사용자 사이트 차단 문제를 우회한 **최초 실 Windows EXE 빌드 PASS(사용자 로그 기준)**.
- EXE 파일 `Length` 출력은 열 폭으로 `22...` 잘림, SHA256 출력은 제공되지 않음. **정확 크기·SHA256/MZ 헤더·EXE 실제 GUI 실행·무Python 환경·기능·Defender/SmartScreen/서명/라이선스/Windows ACL·활성 DB 암호화는 NOT_VERIFIED**. 빌드는 기존 ZIP의 인자로 진행했으며 빌드 소스의 exact Git SHA도 미수집. 사용자 합성 Windows 소스형 11PASS×2 이전 증거 유지. 새 증거 `docs/P85_WINDOWS_EXE_BUILD_RESULT_20261114.md`.
- 승인 WD-01~14 배점 총100점 및 항목 전체 고객 수용 PASS만 인정하는 규칙 유지. WD-13 **PARTIAL/0점**, 최종 인정 **0/100**(구현률 0 아님), **목표85 미달, [작업중], RELEASE HOLD, 미등록**. 실제 사용자 DB/설정/원본/타상품 수정·유료 실행 없음.

---

# STATUS — 2026-11-14 KST Windows PyInstaller pip --user 빌드 차단 오류 수정 (최신)

- **실제 실패:** Windows Python3.11 `PyInstaller --version` 6.22.3 정상. 빌드 `--plan` PASS였으나 실행시 `build.log`에 `No module named PyInstaller`. 기존 `tools/windows_build_exe.py`가 하위 Python에 `PYTHONNOUSERSITE=1`을 강제해 사용자 설치형 모듈을 숨긴 **빌드 스크립트 결함**으로 확인. 사용자 PATH/설치·고객 데이터의 문제 아님.
- **최소 수정:** 자식 환경의 `PYTHONNOUSERSITE`를 제거하여 부모 Python의 `pip --user` 설치를 인식하도록 함. 기존 보호(새 폴더만 출력·고객 장부와 교차 거부·비서명 HOLD) 보존. 회귀 테스트 신규1개 추가; GitHub 원격 코드 readback 일치, 정확 코드 blob `10d60c3789fb2f8c654479845ec9296dbb0c890b`. 해당 정확 소스를 별도 Linux 환경으로 재구성해 **5/5 단위 mock/경로 테스트 PASS**, py_compile PASS. 전체 제품 회귀/새 저장소 테스트 전체 실행 **미검증**.
- **상태:** 오류 정정 코드는 GitHub 반영. **수정된 Windows EXE 빌드·실행은 아직 NOT_RUN**, 앞선 네이티브 Windows 11종×2 PASS는 Python필수 합성 검증으로만 남음. 전체 WD-01~14 사용자 승인 가중치 불변, 엄격한 최종 수용 **0/100**, 목표85 미달, **[작업중]/RELEASE HOLD/미등록**. 제품 문서 `docs/P85_PYINSTALLER_USER_SITE_FIX_20261114.md`. 비용 추가0·OS 권한/패키지 설치 변경0·데이터 변경0. 다음: 새 UUID 경로로 원래 --plan의 인자를 직접 실행하거나 최신 GitHub ZIP으로 재시도, 출력 확인 후 단계별 EXE/GUI 보안 검증.

---

# STATUS — 2026-11-14 KST Windows owner synthetic acceptance 2회 PASS (최신)

- 사용자 제공 PowerShell Windows 10.0.26200.9974 / Python3.11 실기기 출력: `tools/windows_acceptance.py` **11/11 PASS, 0FAIL/0SKIP × 독립 호출 2회**(총 22PASS), `platform=win32`, `ok=true`. 기본 Tk 창, 포터블15무결성, PowerShell dry-run/사용자 폴더 설치/업그레이드·이전 버전 보존/삭제 후 합성 DB 보존/암호화 백업·복구/임시 파일 정리 통과. **GitHub CI 아님**; 사용자 제공 로그만 확인했고 로컬 ZIP 정확 SHA는 미수집.
- 첫 시도 경로 누락 오류는 이중 압축 해제 경로 수정으로 해소. `bidax.cli` 오류는 별개 상품 명령이며 WORKNOVA Desk 검사 무관. 사용자 증거 요약 `docs/P85_WINDOWS_OWNER_CONSOLE_20261114.md`, 수집 전 제품 코드 HEAD `8455b2950b1d59d3f2167b3b4d7652262573c7c1`.
- **여전히 미검증:** Python 없는 독립 EXE 생성·실행, 실제 본제품 전체 Tk UI/접근성, Win ACL·활성 장부 암호화/서명·Defender, Word 한글 출력·글꼴 상업권, 실제 고객 수용/법률·지원. WD-09/11/13 **부분 실증 강화**이나 사용자 승인 WD-01~14 엄격한 완전 수용 기준 정식 인정점수 **0/100**, 목표85 미달. **[작업중] / RELEASE HOLD / 미등록** 그대로. 사용자는 비용 없는 `py -3 -m PyInstaller --version`만 확인하도록 요청, 실제 빌드 전 보안·고객자료 변경 없음.

---

# STATUS — 2026-11-14 KST WD-13 독립 Windows EXE 빌드 준비 (최신)

- **현재 HEAD 변경 근거:** 사용자 승인 WD-01~WD-14 100점 배점 고정, 85점 목표 변동 없음. `tools/windows_gui_entry.py`, `tools/windows_build_exe.py`, `tests/test_windows_exe_build.py` 신규 생성, 코드/테스트 커밋 `59513923fa36c26da980080123cd0f7897755fe1`. 자세한 문서 `docs/P85_WINDOWS_EXE_CANDIDATE_20261114.md`.
- **실행 범위:** Linux Python3.13.5에서 신규 파일 3개 대상 12/12 단위 테스트 PASS(0FAIL/0SKIP), compileall PASS, 읽기전용 --plan PASS. GitHub 신규 파일 3개 readback 내용 일치. 기존 **153개 제품 회귀·5 Xvfb GUI·15 source ZIP PASS는 전 회차 기록**이며 새 전체 소스로 재실행한 것이 아님.
- **남은 핵심 게이트:** PyInstaller 자체 미설치·현재 Linux 호스트. 실제 Win10/11 onedir EXE 빌드·실행·PowerShell/Word·OS ACL/암호화·Defender·상용권/실고객/서명은 **NOT_RUN**. private Actions 과금 가능해 실행하지 않음. Python 필요 기존 ZIP은 변경·삭제하지 않음, 고객 DB/복구본/타 브랜치/원본 미변경.
- **공식 인정점수:** 전 14항목 구매자 전체 수용 미완, 승인 기준 **0/100(제품 구현률 0 아님)**. **85 미달 · [작업중] · RELEASE HOLD · 실제 상품 미등록** 유지. Production/Vercel N/A, 유료 사용 0원. 향후 Windows 로컬 실검증 및 실고객·권리 승인 후 요구 항목별 재채점.

---

# STATUS — 2026-11-14 KST WD-08 감사 로그 말단 누락 검증 추가(최신)

- 사용자 승인한 WD-01~14 전체 100점 및 85점 목표 변경 없음. 마지막 감사 이벤트 삭제 미검출 결함을 실제 재현해 seq 연속번호/high-water 검증 보강. 체크포인트 POSIX mode0600과 한글 PDF 글꼴 상용권 별도 명시 동의.
- 직접 실행: Linux Python3.13.5 unittest 153 PASS/0 FAIL/0 SKIP, Linux Xvfb Tk GUI5 PASS, compileall PASS, ZIP 추출·15개 파일 무결성·합성 CLI init/verify PASS.
- GitHub 코드/테스트 커밋 5f43ff0ad1f0e3ff6b90f169c4350ec4f0d8684f, source 패치 커밋 91c31ad055829f0f4cc3b20e3a68e66dc6156442. SHA가 로컬 테스트 코드와 일치함.
- 실제 Win10/11/Word/서명 EXE/OS ACL/실고객·폰트 권리·법률은 미검증, ResourceWarning 미정리.
- 사용자 승인 100점 기준 엄격한 완전 구매자 수용 항목 점수 0/100(개발률 아님). 목표85 미달, [작업중], RELEASE HOLD, 판매미등록. 원본/다른 제품 수정 없음.

---

# STATUS — 2026-11-14 KST: 최종설계 배점안 사용자 승인(최신)

- 사용자 명시적 `배점안승인`: WD-01~WD-14의 기존 100점 배점을 **최종 승인**. 상세 `docs/FINAL_BLUEPRINT_WEIGHT_PROPOSAL.md`(파일명은 기존 참조를 위해 유지). 설계 범위 축소나 점수 임의 조정 없음.
- 승인된 엄격한 *항목 전체 완료만 PASS* 기준 현재 **최종 검증 인정점수 0/100**, **85점 목표 미달**. 이는 기능 구현률 0%가 아니라 구매자 수용까지 완전 종료된 항목이 아직 없다는 뜻. **14개 항목 부분 구현·기능 검증 증거**는 `docs/FINAL_SCORE_EVIDENCE_20261114.md`에서 구분.
- 이전 회차 증거: Linux Python 141/141 PASS, Tk Xvfb GUI 5종 PASS, 포터블 15개 파일 검사 PASS(기능 SHA `fb71ca9a65f8d1a067a2b53eb18fbdac0580054b`). **이번 승인 작업에는 제품 코드 수정·신규 실행 테스트 없음**.
- Windows10/11 실기기, 보안·서명 EXE, Word 인쇄·폰트 권리, 실고객·법률/지원 수용 **미검증**. 무료 검증 우선; 유료 CI·보안 설정 변경·실고객 전송·판매GO는 승인 대상 외.
- `hibi89/Freelancer@product/worknova-desk-local` `[작업중]`·`RELEASE HOLD`·실등록 미완료. Production N/A. 기존 데이터·타브랜치·PayPal 원본 변경 없음.

---

# STATUS — WORKNOVA Desk Windows acceptance readiness (2026-11-14 KST)

- Owner objective: verified **85% of full WD-01..14**. **UNASSESSED / NOT CERTIFIED**, [작업중], RELEASE HOLD. Proposed 100-point rubric still unapproved; never equate local engineering stage with final percent.
- New: no-fee, isolated, disposable Windows acceptance helper `tools/windows_acceptance.py` and two regression checks. Linux 125 Python PASS / 0 FAIL / 0 SKIP, four Linux Xvfb Tk GUI flows PASS. On Linux Windows helper explicitly exits with status 3; native Windows10/11 PowerShell/Word/Defender/user acceptance **NOT RUN**.
- Owner-only later: run one local Windows command, return sanitized JSON; approve/change WD weights and customer/legal signoff. Still missing signed standalone EXE, validated OS access protection, commercial rights. Exact evidence: `docs/P85_WINDOWS_GAP_20261114.md`.
- No original customer DB, PayPal hackathon, Freelancer main or other products modified. GitHub SHA is the commit containing this update; no Vercel/Production.

---

# STATUS — WORKNOVA Desk P85 schema/privacy safety (2026-11-14 KST)

**Official final design completion UNASSESSED / owner 85% goal NOT CERTIFIED.** Product remains `[작업중]`, RELEASE HOLD, no Kmong sale and no production service. WD-01–WD-14 remains authoritative; proposed weights in `docs/FINAL_BLUEPRINT_WEIGHT_PROPOSAL.md` are unapproved.

## Implemented and verified this turn

- New/open path schema fail-closed: refuse unrelated SQLite v0/empty/corrupt; refuse incomplete v2 structure; validate audit and SQLite integrity on reopen. Protect unchanged original files and preserve v1 explicit migration.
- User-controlled, minimal customer financial/contract-state JSON export, redacted name by default, explicit disclosure flags, no free text/bank references/file paths, new-file-only private output on POSIX, GUI button, consistent read snapshot. Output financial figures and opaque IDs are still confidential.
- Offline portable manifest 14 source/script files + JSON, no remote service or paid usage. Python prerequisite unchanged.
- Linux Python3.13.5 `PYTHONPATH=. python -m unittest discover -s tests -q`: **123 PASS / 0 FAIL / 0 SKIP**. Four Tk8.6 Xvfb scripted actual-widget GUI flows PASS. `compileall` PASS. ZIP extraction/preflight 14/14 + isolated CLI init/verify PASS. See `docs/P85_SCHEMA_PRIVACY_20261114.md`.

## Gaps / stop conditions

Windows10/11 native PowerShell/installer/upgrade/uninstall, true signed standalone EXE, login/auth and disk encryption, real Word/PDF licenses and print, 10+ actual customer acceptance, legal/NOTICE/support/sales signoff, approved weighted WD-01–WD-14 acceptance: **NOT VERIFIED**. No owner-data/credentials/font sent, no paid CI run, no actual bank settlement. Product Actions policy-only status is not functional QA. No Vercel/Production (N/A).

## GitHub/rollback

Feature branch `hibi89/Freelancer@product/worknova-desk-local`, prior exact head `4e8adf0f61281006bcb570aa2f6282925168b0f7`; source commit SHA `4d116918cc096d0a87605d07a4dd80da3ce35959`, GitHub 18/18 blob parity checked; documentation head advanced by this metadata commit. Restore previous feature code only, do not revert owner SQLite v2 with old v1 writer. No changes to Freelancer main, original PayPal hackathon, other product branches. Central Kmong `[작업중]` synchronization after code confirmation. **RELEASE HOLD**.

---

# STATUS — WORKNOVA Desk P85 offline recovery checkpoint

Updated 2026-11-13 KST · Private `hibi89/Freelancer@product/worknova-desk-local`.

**Official whole-final-blueprint completion UNASSESSED; user requested P85 NOT CERTIFIED. `[작업중]` remains. RELEASE HOLD / no actual product registration / no Production.** The WD-01..WD-14 blueprint and unapproved 100-point proposal remain unchanged.

## Verified in local Linux Python 3.13.5

- Existing offline customer/quote/revisions/contracts/milestones/receipts, controlled deletion, file evidence hashes, audit checkpoint, redacted DOCX/PDF, Tk GUI and portable prelaunch verification preserved.
- Newly implemented recovery drill: opt-in separate existing private scratch workspace; consistent online backup, SHA-pinned new-path restoration, six business/audit tables exact comparison, automatic scratch cleanup. Backup creation POSIX owner-only 0600 even under umask 022; no existing user files overwritten or permissions changed.
- Python regression **104/104 PASS, 0 FAIL, 0 SKIP**, original 97 + 7 recovery unit/CLI scenarios. See `docs/P85_RECOVERY_DRILL_20261113.md`.
- Portable v3 strict 13 source/script entries plus manifest; Linux extraction + preflight + throwaway CLI (and existing Tk8.6 Xvfb GUI flows) require final-source-SHA evidence in HANDOFF.

## Unverified / blockers

- Real Windows10/11 per-user PowerShell install, upgrade, launch, rollback, removal, data/ACL preservation, signed bundled EXE, Defender; actual Windows Word/PDF and rights; true OS authentication/ACL/disk encryption and administrator-compromise resistance; real buyer cases and legal/tax acceptance; approved complete 100-point WD rubric. No actual bank payment/provider API. These prevent official P85 certification and sales.
- No Vercel or public service planned; Production status **N/A**. Policy-only Actions do NOT count as product Windows CI.

## Rollback

Previous verified code `85a2a115d32d3378544ae68bb453466499aebcb8` in Git history. Do not touch owner databases, backups, main branch, PayPal source, other product statuses or licenses. Package v3 requires its paired v3 integrity verifier, do not mix with v2. Preserve source/test evidence exact SHA in central KMONG registry and `HANDOFF.md`.


---

## 2026-11-14 P85 optional encrypted-backup development evidence

- User target is verified 85% of **the full WD-01..WD-14 final product**, **NOT** an engineering milestone. Formal weighted rate remains **UNASSESSED / P85 NOT CERTIFIED**. Keep KMONG **[작업중]** and **RELEASE HOLD**, no sale/deployment.
- New source `worknova_desk/secure_backup.py`, CLI concealed backup/recovery password prompts, Tk GUI backup/restore controls, optional `cryptography` AES-256-GCM+scrypt, non-overwrite restoration, SHA pin, integrity/audit checks, strict portable allowlist. Active DB remains **unencrypted**.
- **Actual Linux Python3.13.5 full unittest 141/141 PASS, 0 FAIL, 0 SKIP** (previous 125 + new 16), actual Linux Tk8.6 Xvfb **5/5 GUI scripts PASS**. Compileall PASS. New disposable portable ZIP: 15 hash-verified files, extracted CLI init+verify PASS, tampered file fail-closed. Existing suite still emits `ResourceWarning` for unclosed SQLite connections; a clean resource-leak audit has NOT passed.
- Native Windows acceptance runner intentionally exits code3 on Linux, thus Win10/11 installer/PowerShell/Defender/Word/PDF/unsigned EXE/OS ACL/real customer/legal acceptance **NOT RUN**. Private GitHub runner included-usage balance could not be verified; no fee-risk workflow invoked.
- Previous code parent `0b5354c20b1eaf1b3354432ee92f24aedbce03a4`; new exact source SHA and verification need GitHub readback. No existing customer DB, main branch, PayPal code, external security control, secrets or pricing modified.
