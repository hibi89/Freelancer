## 2026-11-14 KST — Windows EXE 실제 메인 GUI 화면 표시(시각 증거)

사용자가 `onedir` EXE의 신규 빈 장부 확인 대화상자에 이어 메인 **WORKNOVA Desk — 로컬 계약·납품 장부** 창을 보여주는 Windows 스크린샷을 전달. 한글 안내·거래처 검색·거래처/견적·버전/계약/납품·수금 4탭·업무와 백업 버튼 UI 렌더링 확인. **EXE GUI 시작 화면 표시 PASS**(사용자 화면 증거). **ExitCode, 임시 TEST SQLite 파일 존재, 실제 버튼 실행/데이터 보존·무Python PC/서명·Defender/ACL/고객수용 미검증**. 원본 스크린샷은 개인정보/브라우저 UI가 있어 GitHub에 업로드하지 않고 내용만 기록. [증거 기록](docs/P85_WINDOWS_EXE_BUILD_RESULT_20261114.md).

WD-11/13 일부 GUI 검증 강화, 완전 수용 불충족으로 각 PARTIAL/0. 전체 승인 WD01~14/100 **정식 0/100, 목표85 미달, [작업중]/RELEASE HOLD/미등록** 유지.

## 2026-11-14 KST — EXE 파일 크기·SHA256·MZ 기본 헤더 PASS (사용자 로그)

Windows onedir 산출물 `WORKNOVA-Desk.exe` **7,107,722 bytes**, `SHA256=A7CD6B052108E5630E4AD50151841F0B812654F22E87CFE8338E22CB12A5C23E`, `MZ header: PASS`. 사용자 실제 PowerShell 검증 결과를 전달받아 기록. 바이너리 파일 원본은 수신하지 않아 파일 전체 직접 검증·PE 전체 유효성/서명은 주장하지 않는다. [증거](docs/P85_WINDOWS_EXE_BUILD_RESULT_20261114.md). **EXE GUI 런타임·실거래처/DB 지속성·무Python PC·Defender·ACL/활성 DB 암호화·실고객/법무 수용은 NOT_RUN.**

WD13(10점) 빌드 및 기본 파일 확인 **PARTIAL/0점**, 고정 전체 WD01~14 100점 중 정식 수용 PASS 합 **0/100**, 목표85 미달. **[작업중]/RELEASE HOLD/미등록** 유지.

## 2026-11-14 KST — 실제 Windows onedir EXE 빌드 증거 추가 (WD-13 PARTIAL)

사용자 전달 PowerShell에서 Windows10.0.26200, Python3.11.9, PyInstaller6.22.3을 확인. `--plan` JSON의 PyInstaller 인자를 직접 호출한 결과 EXE·COLLECT 완료 및 `Build complete!`, `WORKNOVA-Desk.exe` 파일 존재 확인. **빌드 PASS**는 EXE 실제 실행·서명·Defender·GUI 또는 제품 전체 수용과 다름. 길이 표가 잘려 정확 파일 크기·SHA256 출력 없음, PE MZ/원격 정확 소스 SHA·실 GUI/ACL/무Python 환경·라이선스 미확인. 상세 `docs/P85_WINDOWS_EXE_BUILD_RESULT_20261114.md`.

WD-13(10점)은 Windows 패키지 생성 부분 진전이지만 설치·데이터 보호·암호화·서명/고객 수용 조건 전부 충족하지 못해 **PARTIAL/0점**, WD01~12/14 판정 유지. 전체 사용자 승인100점에 대한 완전 검증 인정 **0/100**, 목표85 미달, **[작업중], RELEASE HOLD**, 판매 미등록.

## 2026-11-14 KST Windows EXE 빌드 진입 오류 및 수정 결과 — WD-13 점수 불변

실 Windows에서 PyInstaller6.22.3은 사용자 계정 설치로 정상(`py -3 -m PyInstaller --version`), `--plan`도 PASS였으나 실제 `build.log`: `No module named PyInstaller`. 빌드 래퍼가 자식 `PYTHONNOUSERSITE=1`로 사용자 사이트를 비활성화한 결함을 수정하고 재발 방지 테스트 추가. 수정 파일 blob `10d60c3789fb2f8c654479845ec9296dbb0c890b` 정확 소스의 **Linux 5 mock/경로 테스트 PASS**·컴파일 PASS·GitHub readback. 실제 수정한 Windows EXE 빌드·실행/서명은 여전히 **NOT_RUN**. 상세 `docs/P85_PYINSTALLER_USER_SITE_FIX_20261114.md`.

기존 실 Windows 합성 11 PASS×2는 포터블 Python 경로 증거이며 독립 EXE 증거가 아님. 원본 WD-01~14 사용자 승인 총100점, 항목별 완전 수용 기준 **0/100**, 85 미달, [작업중], RELEASE HOLD 유지. 기능/성능/제품 scope·가중치 변경 없음.

## 2026-11-14 KST — WD-09/11/13 Windows 합성 QA 사용자 콘솔 11/11×2 PASS

사용자가 실제 Windows 콘솔에서 `tools/windows_acceptance.py` 실행 결과 `platform=win32`, `ok=true`, 각 11 PASS / 0 FAIL / 0 SKIP을 **두 번** 제공. 기본 Tk 창·Python 필수 포터블 ZIP 15파일·PowerShell 합성 설치/업그레이드/삭제·합성 SQLite·선택 AES 암호화 백업/복원·원본 데이터 보존과 임시 정리가 확인됐다. GitHub-hosted CI가 아니라 **사용자 제공 콘솔 출력**으로만 확인; 다운로드된 로컬 ZIP 정확 SHA 미수집. 실행 로그 평가 `docs/P85_WINDOWS_OWNER_CONSOLE_20261114.md`.

변경: WD-09/WD-11/WD-13의 일부 Windows 미검증 게이트를 **실기기 합성 시나리오 PASS**로 세분화. 실제 전체 GUI·Python 독립 Windows EXE·OS ACL/상시 DB 암호화·서명/Defender·Word 한글 인쇄·실고객/법률·글꼴 상용권은 아직 NOT_RUN. 승인 WD-01~14 가중치/범위 불변, 전체 구매자 수용완료된 항목이 아직 없으므로 **전항목 PARTIAL/정식 인정 0/100, 목표85 미달** (개발률 0% 뜻 아님). `[작업중]`, `RELEASE HOLD`, 크몽 미등록 유지.

## 2026-11-14 KST WD-13 무료 onedir EXE 빌드 **준비 코드** 추가 — 정식 점수 불변

승인 WD-01~WD-14 전체 100점과 항목별 완전 수용 PASS 원칙은 불변. WD-13(10점)은 Windows Python 없는 EXE를 만들 수 있는 선택적 PyInstaller **오프라인 빌드 경로 코드** 및 로컬 데이터 경로 기본 차단을 추가했다. 신규 단위 테스트 **12/12 PASS**(Linux Python3.13.5, mock 포함), compileall PASS, GitHub 3 신규 파일 readback 동일; 기능/테스트 SHA `59513923fa36c26da980080123cd0f7897755fe1`. **PyInstaller/Win EXE 실제 빌드·GUI 실행·서명·OS ACL/암호화/Win 설치 복구/실고객 수용은 NOT_RUN.** 이는 WD-13 **PARTIAL/0점**을 계속 의미한다. 나머지 WD-01~12,14는 이전 판정 유지. 승인 기준 합계 **0/100**, 목표85 미달, [작업중], RELEASE HOLD, 판매 미등록. 기존 Python153/Tk5/ZIP15 PASS는 과거 SHA 증거이며 이번 통합 재실행 아니다. 자세히 `docs/P85_WINDOWS_EXE_CANDIDATE_20261114.md`.

# WORKNOVA Desk — 승인 배점 기준의 전체 최종설계 검증 원장

**2026-11-14 KST:** 사용자가 WD-01~WD-14의 **100점 배점안을 승인**. 기준점수 합계 100, 목표 85. 원본 설계/범위는 변경하지 않음. 이번 변경은 **평가기준 승인·증거 재분류**이며 소스 구현이나 Windows 실기기 검증이 아님.

| 항목 | 승인배점 | 현재 기존 검증 증거 | 누락된 최종 구매자 수용 조건 | 판정 | 확정 인정점수 |
|---|---:|---|---|---|---:|
| WD-01 | 8 | 고객 등록·변경·미사용 고객 삭제, 비공개 JSON | 실제 권한·보존·삭제 정책 미검증 | PARTIAL | 0 |
| WD-02 | 7 | 정수 KRW/VAT 계산과 예외 테스트 | 실제 세무·표시 적정성 검토 미완 | PARTIAL | 0 |
| WD-03 | 6 | 불변 견적 버전·승인 및 테스트 | 구매자 실제 승인 절차 검수 미완 | PARTIAL | 0 |
| WD-04 | 6 | 견적 연결 계약·별도 활성화 테스트 | 계약 문구 및 실제 법적 수용 미완 | PARTIAL | 0 |
| WD-05 | 6 | 마일스톤 합계와 상태 전환 테스트 | 실사용 업종 수용 사례 미완 | PARTIAL | 0 |
| WD-06 | 7 | 납품·수정·수용 및 파일 해시 | 실제 구매자의 수령·신원 증명 미완 | PARTIAL | 0 |
| WD-07 | 7 | 수동 부분 수금·미수금·중복 방지 | 실제 외부 입금 증빙·대사 미검증 | PARTIAL | 0 |
| WD-08 | 8 | SHA 감사 체인·독립 보관 가능한 미서명 체크포인트 | 독립 서명 기반 변조방지 미검증 | PARTIAL | 0 |
| WD-09 | 10 | v1/v2 백업·복원 리허설·선택적 AES-GCM 암호화 백업 | Windows ACL·전원차단 복구·실사용 복원 미검증 | PARTIAL | 0 |
| WD-10 | 5 | 비공개 JSON/HTML 출력·외부 전송 없는 로컬 작동 | 독립 개인정보 처리·보존 검토 미완 | PARTIAL | 0 |
| WD-11 | 8 | Linux Tk Xvfb GUI 합성 시나리오 5종 PASS | 실제 Windows10/11 UI·접근성 미검증 | PARTIAL | 0 |
| WD-12 | 6 | 한국어 DOCX·사용자 폰트 PDF의 Linux 생성·파싱 | Windows Word 인쇄·한글 폰트 상업권리 미검증 | PARTIAL | 0 |
| WD-13 | 10 | 15개 소스 무결성 확인, Python 필요 포터블 ZIP | Windows 설치·복구·독립 서명 EXE·DB 보호 미검증 | PARTIAL | 0 |
| WD-14 | 6 | 10개 업종 합성 업무 테스트 | 실제 고객 검수·법률/NOTICE·판매/지원 승인 미완 | PARTIAL | 0 |
| **합계** | **100** | 기존 기능 개발·회귀 증거 보유 | 실 Windows·구매자·법률·판매 검증 남음 | **최종85 미달** | **0/100** |

**해석 주의:** `0/100`은 **완전한 구매자 수용까지 최종 검증된 항목만 인정하는 엄격한 점수**일 뿐, 제품 구현률이 0%라는 의미가 아님. 14개 항목에 부분 구현/테스트 증거가 존재하지만, 각 항목의 승인된 전체 배점을 부분 구현만으로 계산하거나 85%로 올려서는 안 됨. 기존 개발 진행정도는 이 점수와 구분해 설명한다.

**기존 실행 근거(이전 회차):** Linux Python 3.13.5 unittest 141/141 PASS, Tk Xvfb 5/5 PASS, Python이 필요한 포터블 15개 파일 검증 PASS, 제품 기능 SHA `fb71ca9a65f8d1a067a2b53eb18fbdac0580054b`. 이 문서 승인 회차에서 제품 기능을 다시 테스트한 것은 아님. Windows 설치/GUI/Word/ACL/서명EXE, 실구매자 검수·라이선스·지원은 미검증. 

**다음 우선순위:** ① 무료 Windows runner 실제 실행과 복구 ② Windows 독립 EXE·원본 권한·장부 보호 ③ 최종 사용자/법적 권리 검토 ④ WD 항목 단위 재증빙 후 정식 배점 반영. `[작업중]`, `RELEASE HOLD`, 크몽 실제 판매 미등록 유지.


## 2026-11-14 KST WD-08/10/12 추가 검증 증거

사용자 승인 전체 100점 그대로 유지. GitHub 실제 코드/테스트 SHA 5f43ff0ad1f0e3ff6b90f169c4350ec4f0d8684f. 감사 로그 마지막 행 삭제시 체인만 검사해 통과하던 오류 재현 후 seq+AUTOINCREMENT high-water 검출 구현. 체크포인트 POSIX0600, PDF 한글 TTF 상업적 사용권 GUI 추가 확인. Linux Python153 PASS/0FAIL/0SKIP, 실제 Tk Xvfb GUI5 PASS, ZIP 추출 후 15개 파일 SHA+합성 CLI PASS. Windows/법무/실고객/서명 실행은 미검증. 전체 고객 수용 점수 0/100 유지(개발률 아님), 목표85 미달·[작업중]·RELEASE HOLD.

