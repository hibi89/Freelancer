# WORKNOVA Desk — 감사기록 말단 삭제 감지·PDF 폰트 권리 검수

기준일: 2026-11-14 KST. 승인된 최종설계 WD-01~14 100점 그대로 유지.

## 재현된 결함·수정
- 기존 소스에서는 고객 생성 뒤 감사 이벤트의 마지막 행 DELETE 후에도 SHA 체인 확인이 성공하는 오류를 실제 재현.
- 감사 이벤트 순번 연속성과 SQLite AUTOINCREMENT high-water 대조를 추가. 말단/중간/전체 삭제 및 high-water 행 삭제를 탐지하고 재개장 실패 처리. 관리자가 DB와 메타데이터 모두 위조하는 경우 방어하지 못함.
- 독립 체크포인트 파일을 POSIX에서 0600 개인 파일로 신규 생성하고, 기존 파일 덮어쓰기 거부.
- 한글 PDF TTF 선택 이후 상업용 PDF 임베딩 권리에 대한 별도 GUI 명시 확인. 거부 시 문서 생성 호출 차단. 실제 권리를 검증하거나 보증하는 것은 아님.
- 고객 SQLite 원본·DB 스키마·기존 PayPal 코드·다른 제품 변경 없음.

## 실행한 검증
- Linux Python3.13.5 unittest 153/153 PASS(기존 141+신규 12), 실패0, 건너뜀0.
- Linux Tk8.6 Xvfb GUI 5종 PASS, compileall PASS.
- 포터블 ZIP 새 폴더 압축 해제, 15개 소스 SHA 검증 및 합성 SQLite init/verify PASS.
- 변경한 3개 소스 + 신규 2 테스트 GitHub Blob SHA가 실제 로컬 검증 코드와 일치.
- ResourceWarning(미종료 SQLite 연결)은 남아 있고 정밀 추적은 제한 시간 초과; 해결했다고 주장하지 않음.
- Windows10/11 네이티브/Word 출력/ACL/독립 서명 EXE/실고객 수용/법률·폰트 권리 NOT RUN.

## 정식 점수
승인 100점 기준 WD-08/10/12 부분 구현 진전. 완전한 구매자 수용 조건을 충족한 항목이 없으므로 엄격한 완료 인정점수 0/100 유지(기능 개발률 0% 의미 아님). 85점 미달, [작업중], RELEASE HOLD, 실제 판매 미등록.
