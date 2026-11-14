# WORKNOVA Desk — 2026-11-14 KST 무인 테스트 전환 및 검증 경계

## 사용자 요청 / 운영 변경

사용자가 수차례 실제 Windows EXE를 설치·검증·실행·클릭하여 EXE 빌드/GUI/SQLite 증거를 제공한 뒤, **반복 수동 테스트를 왜 사용자가 계속해야 하는지** 문제를 제기하였다. 앞으로 **형의 PC에서 일일이 클릭하도록 요청하는 방식을 기본 경로로 쓰지 않는다.** 서버에서 실행할 수 있는 기능/회귀 테스트는 개발 담당자가 자동화하고, 사용자 기기는 원격에서 재현 불가한 하드웨어·실사용자 승인·서명/보안 정책 등 실제 현장 필요 검증에만 사용한다.

## 대안 비교 (기존 최종설계/100점 가중치 불변)

| 경로 | 시간·성능 | 비용·권한 | 제약 / 권고 |
|---|---|---|---|
| A. 로컬 격리 Python unittest | 빠른 독립 실행, 합성 SQLite DB/업무 E2E·거부/중복·데이터 보존 검증 자동화 | 이미 존재하는 Python으로 비용0, 오프라인, 비공개 고객 DB 접근 없음 | EXE 본체 GUI/실 Windows 서명·보안 증거는 별개. **우선 선택** |
| B. 비공개 GitHub Actions Windows/Linux runner | 정확 Git SHA의 다중 OS 자동 실행 가능, 로그 보관 | Actions 할당량/결제·수동 dispatch 권한 미확인, 비용 위험 | Actions 실행 가능·무료 잔량 확인과 사전 승인 전 새 유료 잡 실행하지 않음 |
| C. 소유자 Windows 수동 UI 검증 | 정확 사용자의 EXE·OS·UI 증거 확보 | 비용0이나 사용자의 반복 조작 부담이 큼 | 정말 필요한 *최종 고객/보안·실환경* 게이트로만 제한 |

## 이번 커밋

`tests/test_unattended_business_lifecycle.py` 신규 2개 unittest (실제 상품 코드의 `worknova_desk.core.Desk` API 사용). 각 테스트는 독립 `tempfile.TemporaryDirectory`에서만 합성 DB를 생성하고 종료 후 지움.

- **테스트1:** 가짜 고객 생성→1,000원 VAT 비포함 견적→미승인 계약 금지→견적 승인→계약/단계 생성→계약 활성화→납품 전/미승인 수금 금지→납품·검수→수금→같은 참조번호 중복 수금 무증식→감사 체인 검사→DB 종료/기존 파일로 재열기→고객·견적·계약·단계·영수증·SQLite 무결성/버전 확인.
- **테스트2:** 가짜 견적/계약/납품 승인 이후 2,000원 단계에 1,500원 부분 수금→추가 600원 초과 수금 거절→영수증 합계·감사 이벤트 무증식/무결성 유지.
- PayPal 결제 호출, 인터넷/API, 실고객 데이터, 비밀, 관리자 권한, 외부 전송, 유료 Actions 없음. Windows GUI/Tk를 자동 조작한 테스트로 혼동하지 말 것.

## 검증 및 엄격한 판정

- GitHub 파일 읽기 재검증 완료; 신규 파일 **Git blob SHA `4df97d19a5bcacc203babff5136dc2fc48b40fac`**. 동일 내용을 이 환경의 임시 Python 파일로 재구성하여 로컬 Git blob SHA1이 동일함을 확인. 따라서 코드 동일성 증거가 있다.
- 정확 소스 `ast.parse` **PASS**, 139줄 / UTF-8 6,182 bytes. 이 검증은 *문법* 검사이다.
- **`python -m unittest discover -s tests -v` 전체 프로젝트 실제 실행 NOT_RUN**: 비공개 GitHub 전체 원본이 현재 격리 실행기 파일시스템에 제공되지 않았고, GitHub 연결에 새 Actions workflow dispatch 권한이 없음. 이번 commit에 연결된 combined status도 비어 있어 CI PASS라 주장하지 않는다.
- 사용자가 이번 대화에서 `$p4 = [Diagnostics.Process]::Start($psi2)` 후 `$p4.WaitForExit()`→`ExitCode:0`을 보고함. 사용자는 그 전에 요청한 **가짜 1,000원 견적 작업을 수행했다고 진술**했지만, GUI 견적 테이블/SQLite 정확 신규 견적 행 조회가 없어 **실제 견적 결과 PASS 판정은 보류**.
- 이전 현장 Windows3회 GUI 실행, 1건 고객 저장/재시작·실 DB 무결성은 독립 근거로 그대로 보존.

## 다음 단계

- 소스 기반 무인 테스트를 **GitHub 비용/권한 문제가 해결된 자동 환경 또는 정본 소스를 받은 격리 Python 환경에서 실행**하여 test2/2 PASS/FAIL 확보하는 것이 우선. 사용자의 Windows 수동 조작은 이 단계에서 불필요.
- 자동 테스트가 PASS해도 Windows GUI/EXE 전체 E2E가 자동 검증됐다는 의미는 아님. Windows EXE 자동화가 필요할 때는 별도 격리 사용자 데이터 폴더·Win GUI runner와 실패 복구/오탐까지 설계.
- WD-01~14 총100점 사용자 승인 배점 및 구매자 **항목 전체** 검증 시 배점 인정 원칙 불변. 현재 정식 완전 수용 인정0/100(코드 구현률0 뜻 아님), 85 미달. **[작업중]/RELEASE HOLD/크몽 미등록** 유지.
