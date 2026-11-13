# WORKNOVA Desk — 2026-11-14 KST Windows 10/11 실기기 합성 인수검증 사용자 콘솔 증거

## 원본 증거 유형과 한계

사용자가 본 채팅에 **Windows PowerShell 원본 JSON 출력 2회**를 직접 제공하였다. 본 기록은 사용자 보고 콘솔 캡처의 보존 요약이며 GitHub-hosted Windows CI, 제3자 서명된 재현 로그, 로컬 실행파일의 정확 SHA를 독립 확인한 것으로 취급하지 않는다. 실제 장치의 표시는 `Microsoft Windows [Version 10.0.26200.9974]`, 로컬 Python 3.11, PowerShell 5.1; 콘솔 결과 `platform: "win32"`, `ok: true`, `scope: "native Windows synthetic offline QA only"`.

사용자 ZIP 압축 해제 위치가 한 단계 깊어 최초 상대경로에 `[Errno 2] No such file or directory`가 발생하였다. `Get-ChildItem -Recurse -Filter windows_acceptance.py`로 실제 경로를 찾은 뒤 다음과 같이 정상 실행했다. 중간에 입력된 `bidax.cli`은 다른 제품 명령이고 작업 중 파일이 없는 상태여서 실패했으며 WORKNOVA Desk 기능 실패와 무관하다.

```powershell
py -3 -B .\Freelancer-product-worknova-desk-local\tools\windows_acceptance.py
```

## 사용자 제공 두 번의 독립 호출 결과

두 번 모두 **11개 검사 PASS, 0 FAIL, 0 SKIP**. 합산 **22 PASS/0 FAIL**, 같은 11개 검사의 *반복 실행*으로 신규 22종 시나리오가 아니라는 점에 유의한다.

| Windows 합성 검사 | 1회 | 2회 |
|---|---|---|
| Windows Python + Tk window | PASS | PASS |
| Portable ZIP extraction and allowlist (15 files) | PASS | PASS |
| Portable command preflight | PASS | PASS |
| PowerShell no-change dry run | PASS | PASS |
| PowerShell per-user install in disposable profile | PASS | PASS |
| Synthetic ledger and audit verification | PASS | PASS |
| AES-GCM encrypted backup/restore, temporary fixture only | PASS | PASS |
| Synthetic backup/restore preserves original | PASS | PASS |
| PowerShell upgrade/rollback app and data preservation | PASS | PASS |
| PowerShell app-only uninstall retains synthetic DB | PASS | PASS |
| Disposable profile and synthetic files cleaned | PASS | PASS |

최초 파일 위치 문제는 환경 경로 문제로 해소됐다. 관리 권한, API 연결, 개인정보/실고객 장부 접근, 강제 PowerShell 보안 정책 변경, PayPal/유료 API 사용은 증거에 없음.

## 승인된 최종평가에 미치는 영향

- WD-09 Windows **합성 데이터** 기준 백업/복원·업그레이드·삭제 후 보존의 현장 운영체제 검증 증거가 추가되었다.
- WD-11 Windows의 기본 Tk 창 생성이 확인되었다. 실제 WORKNOVA GUI 전체 흐름·접근성, 사람 조작/글꼴·업무 수용은 여전히 미검증.
- WD-13 Python 필수 포터블 PowerShell 사용자 설치/갱신/제거 합성 경로가 실제 Windows에서 확인되었다. 실제 **Python 없는 독립 EXE 빌드/실행·코드서명·Defender·ACL·상시 SQLite 암호화**는 미검증.
- 사용자 승인 배점 WD-01~14 총100 고정, 해당 항목 **전체 수용 조건**을 모두 충족한 항목은 확인되지 않았으므로 엄격한 공식 확정점수 **0/100**, 목표 **85 미달**. 이는 코드 구현률 0% 의미가 아님. `[작업중]`, `RELEASE HOLD`, 크몽 미등록 유지.

## 다음 의존성

무료 조건에서 사용자는 `py -3 -m PyInstaller --version`으로 Windows Python3.11의 PyInstaller 설치 상태만 확인한다. 버전 출력이라면 기존 `tools/windows_build_exe.py --plan`과 별도 신규 임시 폴더의 onedir 후보 빌드·합성 계정 GUI 실제 실행을 우선 검토한다. 미설치면 **무단 pip 설치·새 유료 Windows Actions 작업 실행하지 않는다**. 원래 고객 장부/계정·자료 보안·폰트/서명·실구매자·법률/환불 승인 별도. 이 문서는 사용자 전달 결과 기반이며 정확 설치 ZIP/git SHA 미수집으로 완전 원본 SHA 재현으로 간주하지 않는다.

**문서 기준 제품 소스 HEAD(사용자에게 알려진 최신):** `8455b2950b1d59d3f2167b3b4d7652262573c7c1`. 검증된 사용자 ZIP 내부 소스가 해당 SHA와 정확히 동일하다고 주장하지 않는다.
