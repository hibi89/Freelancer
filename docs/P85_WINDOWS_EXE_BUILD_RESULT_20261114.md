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
