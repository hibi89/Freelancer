# BID AX Windows frozen GUI 실기동 CI — 266테스트

**2026-11-14 KST** | 기능 SHA `1ec540634671ff85b080e034cd37564e54fc8e1e` | [GitHub Actions #43538851029](https://github.com/hibi89/Freelancer/actions/runs/43538851029) **5/5 SUCCESS**.

## 왜 보강했는가

- 기존 [GUI/온비드 체크포인트](BID_AX_GUI_ONBID_CHECKPOINT_CI_20261114.md)는 Windows Tk 기본 창 생성 및 PyInstaller **PE 파일 빌드까지만** 검증했다. 실제 frozen GUI EXE를 시작하지 않았기 때문에 PyInstaller 수집 누락, GUI 진입점 오류를 검증할 수 없었다.
- 네트워크/고객DB 없는 로컬 셀프테스트 **A**: `--selftest-gui` 전용 진입점이 `TemporaryDirectory`를 만들고 Tk 전체 화면을 구성/700ms 후 정상 파괴. Windows CI에서 EXE 프로세스를 직접 실행해 30초 시간 제한 및 ExitCode0 확인. 비용은 기존 공개 리포지터리 표준 Actions 범위, 별도 고객 인증키/유료 서비스 불필요. **채택**.
- 고객 데이터로 실행하거나 무조건 30초 기다렸다 강제 종료하는 **B**는 실제 사용자 DB 접근 위험/종료 정상성 검증 불량으로 불채택.

## 구현/증거

- `bidax/entrypoint.py`: `--selftest-gui` 외 비정상 GUI 인자 거부, 시험 시 고객 기본 DB 경로 함수 사용하지 않고 임시 테스트 경로 전달. 일반 무인자 GUI 경로 보존.
- `bidax/desktop.py`: 유효한 `auto_close_ms` 100~5000ms만 인정, 700ms 후 Tk `root.destroy`; 자동 종료 옵션 없으면 기존 `mainloop` 그대로.
- `tests/test_gui_entrypoint.py`: 임시 경로/소유자 DB 미접근, 일반 진입점 회귀, 비정상 인자 거부 **3종**. 이전 263→**266**.
- GitHub Actions Ubuntu3.11 **266 PASS**, Ubuntu3.13 **266 PASS**, Windows3.11 **266 tests/0 FAIL/1 POSIX-only SKIP**, Windows CLI EXE PASS, Windows Tk 기본 창 초기화 PASS, unsigned GUI onedir PE 생성 PASS, **실 frozen Windows GUI 셀프테스트 시작·정상 종료 PASS**. 원격 로그 출력: `Frozen GUI launched and exited; customer installation NOT tested`.
- 이 자동 테스트는 실제 고객 Win10/11 설치, 권한, 한국어 UI 육안검수, 실제 보고서/원문, 운영 API 호출, 서명·SmartScreen 인수까지 증명하지 않는다.

## R01–R29 완성률·권리·재개

공식 최종완성률 **UNASSESSED**, 목표 85% **미입증**; `[작업중]`, RELEASE HOLD, 크몽 미등록. 온비드 실 첫 10건·기관 보고 총186만 존재, 나머지18페이지/다른 API·100 실공고·10 독립 사람 검토·상업적 이용권/고객 파일럿 미확인. 사용자 API 키, 고객 격리 JSON·DB, 타상품/BID OWL 미수정. 다음 작업은 실제 소유자 승인 현장 수용과 운영 API 계약 검증이며 새 유료/외부 전송은 사전승인.
