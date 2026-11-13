## 2026-11-14 KST 사용자 제공 실제 Windows EXE 메인 GUI 스크린샷

사용자가 같은 PowerShell 격리 실행 절차의 후속 화면을 전달했으며, **WORKNOVA Desk — 로컬 계약·납품 장부**라는 제목의 실제 Tk 창이 열린 것을 시각적으로 확인했다. 화면에 다음 구성요소가 표시된다.

- 오프라인·수기 장부 고지 문구가 한글로 출력.
- 거래처 검색/새 거래처/새로고침.
- `거래처`, `견적·버전`, `계약`, `납품·수금` 탭.
- 견적 생성·버전 수정·승인, 계약 생성/활성화, 납품·검수·수금 수기 기록, 보고서·백업/암호화 백업/복원·증빙 해시 관련 버튼.
- 최초 열람시 거래처 표는 비어 있으며 GUI 오류 경고 또는 충돌창은 스크린샷에 보이지 않는다.

이 화면은 앞서 확인한 `onedir` EXE 빌드/해시/MZ 및 새 빈 장부 생성 확인창 뒤 단계에서 제공된 결과다. **Windows EXE 프로세스의 Tk 메인 GUI가 표시되는 실제 실행 증거**로 분류한다. 다만 **스크린샷만으로 모든 버튼·작업 로직·사용성/접근성 통과, 파일 I/O, 데이터 지속성, 프로세스 ExitCode=0, 실제 LOCALAPPDATA 경로 검증, 악성코드/코드서명/타 PC 이식은 증명되지 않는다.** 사용자는 화면의 프로그램을 종료한 다음 PowerShell에서 `ExitCode`, `TestDatabaseExists`가 출력되는 결과를 보내기로 함; 이 기록 작성 시점 결과 미수신이다.

출처는 사용자 채팅에 제공한 화면 이미지이며 해당 이미지에는 브라우저·개인 UI 등이 함께 포함되어 **원본 스크린샷을 GitHub에 업로드하지 않는다**. 텍스트 관찰 사실만 기록. 기존 고객 장부·고객자료/OS 설정에는 접근하지 않는 새로운 TEMP `LOCALAPPDATA` 값이 자식 EXE 실행 과정에 전달되도록 구성되었으나 **실제 경로 기록을 눈으로 확인하지 않은 상태**.

**평가:** WD-11/13 GUI의 네이티브 Windows 초기 표시 일부 PASS; WD별 완전 고객 수용 PASS 요건은 미달, WD-11/13 여전히 PARTIAL/0. 승인 WD-01~14 총100 중 정식 완전 수용 0/100, 목표85 미달. **[작업중] / RELEASE HOLD / 판매 미등록** 유지.

## 2026-11-14 KST 후속 사용자 콘솔 — EXE 크기/SHA256/MZ 확인

같은 네이티브 Windows 생성 후보 파일에 대해 사용자가 PowerShell `Get-Item ... | Format-List`, `Get-FileHash ... -Algorithm SHA256`, `[System.IO.File]::OpenRead`로 첫 두 바이트를 직접 검사한 결과:

- **바이트 크기:** `7107722` bytes.
- **SHA256:** `A7CD6B052108E5630E4AD50151841F0B812654F22E87CFE8338E22CB12A5C23E`.
- **MZ 헤더:** `PASS` (첫 두 바이트 77/90).
- **경로:** 사용자 로컬 TEMP의 `worknova-exe-3561dc8e2946484a8af0d09b00c7c58a/dist/WORKNOVA-Desk/WORKNOVA-Desk.exe`. 로컬 경로는 공개 고객 자료가 아니며, 정확 경로를 GitHub에 기록할 필요 없으므로 UUID와 계정 이름은 본 기록의 경로에 포함하지 않는다.

**추가로 확인된 항목:** 산출물 EXE 파일 존재와 크기/SHA256 계산, 기본 Windows MZ 헤더가 사용자 제공 로그로 검증됨. **검증되지 않은 사항:** 외부에서 바이너리 직접 재해시(파일 본문 미수신), PE 전체 구조·서명·SmartScreen/Defender, 런타임 GUI 및 거래처 데이터 저장, PyInstaller onedir 전체 폴더 필수 DLL/자산 이식성과 Python 미설치 PC 실행, 고객 정보 및 권리·고객 수용. 이 결과는 사용자 제공 콘솔을 근거로 한 해시 기록일 뿐, 바이너리 무해성이나 EXE 정상 작동을 보증하지 않는다.

### 다음 안전 GUI 런타임 테스트의 격리 원칙

실 EXE는 처음 구동 시 `windows_gui_entry.py`에서 `LOCALAPPDATA/WORKNOVA Desk/Data/desk.sqlite` 경로를 정하며, `gui.main()`은 해당 DB가 없을 때 새 빈 장부를 만들지 명시적으로 확인한다. 실제 고객 데이터를 건드리지 않도록, PowerShell `System.Diagnostics.ProcessStartInfo.UseShellExecute=false` 및 자식 **프로세스 전용** `EnvironmentVariables['LOCALAPPDATA']`에 새 `TEMP/worknova-gui-qa-<GUID>`을 설정하고 EXE를 실행한다. 팝업에 표시되는 빈 장부 생성은 격리 경로에서만 `예`를 선택. 고객 실명·실수금·외부 데이터는 사용하지 않으며, 실행 프로세스와 새 SQLite 테스트 파일 경로를 별도로 확인. 사용자가 결과 제공 전 이 후속 시험은 **NOT_RUN**.

# WORKNOVA Desk — 2026-11-14 KST 실제 Windows 독립 EXE 빌드 사용자 로그 증거

## 사실(사용자가 전달한 PowerShell 로그에 근거)

- Windows `10.0.26200`, Python `3.11.9`, PyInstaller `6.22.3` 및 hooks `2026.10`.
- `windows_build_exe.py --plan`에서 제공한 인자를 PowerShell이 `python -m PyInstaller --onedir --windowed ...`로 **직접 호출**하여, 빌더 자식 환경의 `PYTHONNOUSERSITE=1` 버그를 우회했다.
- 로그에서 `Building EXE from EXE-00.toc completed successfully.`, `Building COLLECT COLLECT-00.toc completed successfully.`, `Build complete! The results are available in: .../dist`를 확인.
- 이후 `Test-Path -LiteralPath .../dist/WORKNOVA-Desk/WORKNOVA-Desk.exe -PathType Leaf` 분기에서 `Get-Item`이 `FullName`을 출력했으므로 **실제 EXE 파일이 디스크에 생성된 것**은 사용자 전달 로그로 확인된다.
- PowerShell 결과 표에서 `Length`는 열 폭 제한으로 `22`까지만 노출. SHA256은 해당 첨부에서 확인되지 않는다. **정확한 파일 크기·SHA256 미검증**.
- 빌드에 사용자 시스템의 reportlab, PIL, numpy, cryptography 등 hook 탐색이 포함됨. 이는 해당 패키지 전체의 상업적 재배포 라이선스 확인이나 런타임 정상 동작을 뜻하지 않는다.

## 분류

- **PASS(사용자 콘솔)**: PyInstaller Windows `onedir` 독립 EXE 후보 빌드, COLLECT 완료, EXE 파일 존재.
- **NOT_RUN / 증거 부족**: PE의 MZ/파일 전체 SHA256, 산출물 폴더 전체 해시 및 디렉터리 이식, EXE 단독 실제 실행, Tk 프로그램 GUI 표시/업무기능, 무Python PC, 보안 제품/SmartScreen, 서명·라이선스, OS ACL·활성 SQLite 데이터 암호화/실고객 수용.
- 사용자가 가지고 있는 **구형 ZIP의 소스에서 직접 빌드**한 결과로, 최신 GitHub HEAD 소스와 빌드에 사용된 원본의 해시가 동일함을 독립 증명하지 못함.
- 기존 Windows `windows_acceptance.py` 11/11 PASS ×2는 **Python 필수 소스형 포터블** 합성 검증이다. 이번 exe 빌드는 별개의 처음 성공한 빌드 증거.

## 권고되는 다음 사용자 안전 검사(읽기 전용)

기존 PowerShell 세션에서 `$out`이 유지돼 있다면 아래 명령으로 EXE 경로, 정확 크기, SHA256 및 Windows PE MZ 바이트를 검사. 어떤 EXE도 실행하지 않고, 민감 데이터/설정도 건드리지 않는다.

```powershell
$candidate = Join-Path $out 'dist\WORKNOVA-Desk\WORKNOVA-Desk.exe'
if (!(Test-Path -LiteralPath $candidate -PathType Leaf)) { throw 'EXE file missing' }
Get-Item -LiteralPath $candidate | Select-Object FullName,Length | Format-List
Get-FileHash -LiteralPath $candidate -Algorithm SHA256 | Select-Object Algorithm,Hash | Format-List
$stream=[System.IO.File]::OpenRead($candidate)
try { $header=New-Object byte[] 2; $read=$stream.Read($header,0,2); if($read -ne 2 -or $header[0] -ne 77 -or $header[1] -ne 90) { throw 'PE header MZ missing' }; 'MZ header: PASS' }
finally { $stream.Dispose() }
```

이후 EXE 기능 자체를 테스트할 때는 반드시 새 임시 `LOCALAPPDATA`와 합성 빈 DB/사용자 동의 UI를 통해 기존 고객 장부와 분리해야 함. 정식 릴리스로 쓰지 않고 배포/업로드 금지.

## WD 정본 점수

사용자 승인 WD-01~14 전체 총100점 고정, 요구별 최종 구매자 완전 수용만 PASS/배점 인정. WD-13의 **EXE 빌드만 부분 증빙**, 설치·서명·보안·실실행 수용 미완료로 WD-13 **PARTIAL / 0점**. 전체 정식 수용 **0/100**(구현률 0 의미 아님), 85점 목표 미달. **[작업중] / RELEASE HOLD / 판매 미등록** 유지.

**원본 보호/비용:** 기존 고객 DB·백업·인증/OS 정책·PayPal 원본/타 상품/등록완료 변경 없음. 추가 과금 없이 기존 PyInstaller 사용. 이전 패치 전 코드 rollback SHA `d8ab09beae722607a180390dcc3807801fc569cb`; 빌드 준비 수정 코드 HEAD는 현재 제품 GitHub에서 별도 재확인.
