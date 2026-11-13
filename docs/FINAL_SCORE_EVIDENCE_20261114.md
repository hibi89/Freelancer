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

