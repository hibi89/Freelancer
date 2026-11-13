# WORKNOVA Desk — 2026-11-14 KST 무료 Windows EXE 빌드 후보 증거

## 승인된 최종설계·범위

사용자 승인 WD-01~14 100점 배점 [8,7,6,6,6,7,7,8,10,5,8,6,10,6] 그대로. **정식 완전 수용점수 0/100, 85점 미달, [작업중], RELEASE HOLD, 판매 미등록.** 이는 기능 구현률 0%라는 뜻이 아니다.

## 0원 두 설계 비교와 선택

| 방법 | 기능·성능 | 추가 지출 가능성 | 검증 한계/유지보수 |
|---|---|---|---|
| A. 소유자 Windows PC의 PyInstaller **--onedir --windowed** (선택) | Python 설치가 없는 PC에서도 앱 디렉터리 내 EXE 실행 가능. 사용자 데이터는 LOCALAPPDATA 별도 폴더 | PyInstaller 자체 오픈소스, 이미 설치된 경우 추가 비용 0원. 설치가 없다면 외부 패키지 확보는 별도 승인/검토 | Windows에서만 빌드 가능. 미서명·SmartScreen·Defender·실 PC 동작은 별도 실검증 |
| B. private GitHub Windows Actions와 --onefile | 자동 반복 테스트 및 단일 파일 후보 가능하나 임시 추출·AV 오탐 관리 추가 | 비공개 저장소는 포함 compute 사용량을 차감하고 초과 시 과금 가능 | 사용자 0원 조건상 잔여 무료 할당 확인 없이 **실행 금지** |

**선택: A의 오프라인 onedir 준비 코드만**. 제품 소스형 ZIP/기존 GUI/SQLite 스키마/고객 데이터/정본 배점은 수정하지 않았다. 본 회차에서 PyInstaller 설치/실행, Windows EXE 생성, API 호출, Actions/유료 빌드는 **0건**.

## 추가한 실제 코드

- `tools/windows_gui_entry.py`: 사용자 LOCALAPPDATA의 기존 `WORKNOVA Desk/Data/desk.sqlite`를 기존 GUI로 연결. 소유자 확인 없는 DB 자동 초기화/교체를 하지 않으며, 기존 GUI의 명시적 신규 DB 생성 확인을 유지한다. 링크/재파스 경로 사전 차단(Windows ACL 전체 정책 인증을 의미하지 않음).
- `tools/windows_build_exe.py`: 소유자 지정 **새 출력폴더**를 강제하며 기존 폴더 덮어쓰기, 저장소 내부 출력, 고객 DB 경로와 교차, symlink/junction을 거부. 네트워크/패키지 설치 없음. PyInstaller --onedir --windowed, SHA256 및 MZ 헤더 확인, 로그 로컬 저장. 무서명 `RELEASE HOLD` 표시.
- `tests/test_windows_exe_build.py`: 격리된 Python 테스트 12개. 쓰지 않는 --plan, 경로·덮어쓰기·고객정보 경로 격리, Linux에서 Windows 빌드 거부, 가짜 PE 거부를 확인.

## 실행한 검증 vs 미검증

**실제 이번 회차:** Linux Python 3.13.5, 위 3개 신규 파일 대상으로 `python -B -m unittest discover -s tests -v` **12 PASS/0 FAIL/0 SKIP**, `compileall` PASS, `--plan` 읽기 전용 결과 확인. Github 신규 파일 3개 전체 텍스트 readback 일치. **이것은 전체 제품 회귀 153개와 통합하여 실행한 결과가 아니다.** 이전 회차 153 PASS, Tk Xvfb 5 PASS, source ZIP15 PASS는 *과거 SHA 증거*로만 남긴다.

**NOT RUN:** Windows PyInstaller 빌드/실 EXE 시작/한글 GUI/PowerShell 설치·복구/권한 ACL·암호화/Defender·SmartScreen/서명/Word 인쇄/실고객·법률·폰트 권리. 호스트 Windows가 현재 도구 환경에 없고 PyInstaller가 cross-compiler가 아니므로 합성 mock은 EXE PASS가 아니다.

### 나중에 소유자 Windows PC에서 할 수 있는 무료 실제 확인 (별도 승인 없이 개인정보 사용하지 않음)

기존 private 브랜치 checkout과 Windows Python 3.11+, **이미 설치된** PyInstaller가 있을 때, 저장소 밖에 새로운 출력 폴더를 지정한다. `<NEW_OUTPUT>`는 실제 존재하지 않는 폴더이고 그 **상위 폴더만 존재**해야 한다.

```powershell
py -3 -B tools\windows_build_exe.py --out "$env:TEMP\worknova-exe-candidate" --plan
py -3 -B tools\windows_build_exe.py --out "$env:TEMP\worknova-exe-candidate"
```

첫 명령은 검토만 수행하며, 실제 빌드명령은 기존 대상이 있으면 실패한다. 빌드가 끝나도 다음 경로를 **고객 원본 DB 없이 별도 합성 환경에서** 실행 확인해야 한다: `dist/WORKNOVA-Desk/WORKNOVA-Desk.exe`. 실제 계정 LOCALAPPDATA를 사용하는 EXE를 무조건 실행하라는 뜻은 아니다. 테스트 계정 또는 임시 환경변수를 통해 기존 데이터가 없는 환경에서만 검증한다. PyInstaller 미설치라면 설치를 임의로 수행하지 않는다.

## 다음 독립개발/소유자 승인 게이트

1. 실제 Windows에서 빌드·실행·EXE 패키지 전체 폴더 전송/검증, GUI/복구 회귀 및 uninstall 검증.
2. Windows ACL/암호화·명시적 OS 사용자 통제, 위변조에 강한 서명/진본성 검사. OS 보안 정책 변경이나 유료 디지털 서명은 사전 승인.
3. DOCX/Word·폰트 재배포권/지원·환불/실구매자 10건 검수; 전체 WD별 완전 수용 증거 확보 후 정식 점수 재산정.

**복구 기준:** 새 코드 작성 전 HEAD `a1517ad41c26a9d8de374c29c44f98ca1b07971c`. 사용자 데이터·원본 PayPal/Freelancer main/타 제품·라이선스·외부 계정 변경 없음. Python 기존 소스 ZIP은 그대로 배포 후보로 보존한다.
