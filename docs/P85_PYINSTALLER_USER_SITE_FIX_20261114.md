# WORKNOVA Desk — 2026-11-14 KST Windows PyInstaller user-site 설치 인식 오류 수정

## 실제 사용자 증거 / 원인

사용자가 Windows 10.0.26200.9974, Python 3.11에서 `py -3 -m pip install --user pyinstaller` 후 `py -3 -m PyInstaller --version` → **6.22.3**임을 보고했다. 이후 기존 ZIP 내 `tools/windows_build_exe.py --plan`은 정상 JSON(`network:false`, `signed:false`, `production_ready:false`)을 출력했으나 실제 `build()`가 실패했다. 해당 사용자 로컬 `build.log` 마지막 출력은 다음과 같다.

```
python.exe: No module named PyInstaller
```

실패 원인은 PyInstaller 미설치나 PC의 PATH 오류가 아니다. **부모 Python은 사용자 계정의 PyInstaller를 인식했지만, 기존 빌드 스크립트가 자식 프로세스 환경에 `PYTHONNOUSERSITE=1`을 설정해 `pip --user` 설치 경로를 감췄다.** `--plan`은 실행 전 검증이므로 이 문제를 검출하지 못했다. 이 문제는 빌드 준비 코드의 결함이며 실제 EXE는 생성되지 않았다.

## 대안 비교와 최소 수정

A) PyInstaller를 시스템 Python 위치에 재설치: OS Python 패키지 환경 변경, 사용자 시간·충돌 위험 증가. 거부.

B) 기존 Python 인터프리터와 사용자가 설치한 PyInstaller를 그대로 사용하되 빌드 자식 프로세스에서 `PYTHONNOUSERSITE` 차단을 제거: 비용0·기존 PATH/고객 데이터 불변. **B 선택.**

`tools/windows_build_exe.py`에서 `env['PYTHONNOUSERSITE'] = '1'` 제거하고 `env.pop('PYTHONNOUSERSITE', None)`로 변경. 기존 `PYTHONDONTWRITEBYTECODE=1`, 새 출력 디렉터리, 원본/고객 DB 중첩 거부, 서명 없음, 실패 시 HOLD 등은 유지. `tests/test_windows_exe_build.py`에 사용자 사이트 차단을 재발하지 않게 하는 mock 회귀 테스트 추가. 형 PC의 실행 설정이나 설치본을 변경하지 않는다.

## 이번 검증과 남은 한계

- GitHub 수정 코드 blob **`10d60c3789fb2f8c654479845ec9296dbb0c890b`**와 별도 Linux Python3.13.5 실험 복제 텍스트의 **Git blob SHA1 정확 일치** 확인.
- 해당 정확 소스에서 Linux 단위 mock/경로 테스트 **5/5 PASS**, `py_compile` PASS. 기존 Windows 프로젝트 전체 테스트 153개 + 신규 저장소 테스트 파일의 전체 13개를 이번 회차 통합 재실행한 것이 아니다. GitHub 신규 테스트 파일은 코드 readback 확인했으나 별도 전체 자동 실행은 미확인.
- **수정 후 실제 Windows PyInstaller 재빌드와 EXE 실행·Defender/SmartScreen/서명/GUI·DB ACL은 NOT_RUN**. 사용자 제공 앞선 Windows `windows_acceptance.py` 11개×2 PASS는 Python 필수 포터블 합성 범위로만 유효.

## Windows 재검증 경로

사용자가 기존 압축 해제 폴더를 유지하는 경우, **기존 코드의 `--plan`만 재사용해 검증한 인자 목록을 직접 PyInstaller로 실행하면** 결함 있는 `build()` 래퍼를 우회할 수 있다. 출력은 기존 실패 폴더를 덮어쓰지 말고 새 UUID 폴더를 사용한다.

```powershell
$out = Join-Path $env:TEMP ("worknova-exe-" + [guid]::NewGuid().ToString("N"))
$plan = py -3 -B $script --out $out --plan | ConvertFrom-Json
if ($LASTEXITCODE -eq 0) {
    $python = [string]$plan.argv[0]
    $argsForPython = @($plan.argv | Select-Object -Skip 1)
    & $python @argsForPython
    if ($LASTEXITCODE -eq 0) {
        $candidate = Join-Path $out 'dist\WORKNOVA-Desk\WORKNOVA-Desk.exe'
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            Get-Item -LiteralPath $candidate | Select-Object FullName, Length
            Get-FileHash -LiteralPath $candidate -Algorithm SHA256
        }
    }
}
```

이는 기존 `--plan`의 네트워크 없는 빌드 인자 사용이며 **빌드 성공 확인 후에도 EXE를 임의 실행하지 않음**. 출력이 실패하면 오류를 확인하고 무작정 반복하지 않는다. 또는 수정된 최신 GitHub ZIP을 새 폴더에 받아 `windows_build_exe.py`를 실행할 수 있다. 두 방식 다 실 고객 장부/기존 설치를 건드리지 않으며, 실제 Windows 결과가 오기 전에는 EXE PASS 선언 금지.

## 최종설계 및 운영 상태

WD-01~14 사용자가 승인한 100점 배점·전체 수용 단위 채점은 불변. 현재 **정식 인정 0/100**(기능 구현률 0 아님), 목표85 미달, **[작업중] / RELEASE HOLD / 크몽 미등록**. 기존 코드 rollback 기준은 **`d8ab09beae722607a180390dcc3807801fc569cb`**. 제품 코드/테스트 수정 SHA는 최신 GitHub commit에서 재확인. 중앙 크몽 원장 동기화 후 실제 SHA 기록.
