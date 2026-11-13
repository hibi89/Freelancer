# BID AX P85 후속 보안 감사 — 2026-11-13 KST

**검증 기능 SHA:** `9a895ad6ac6d47941d0cf5c5a3ec908e4a298947`. 사용자 목표는 전체 R01–R21 설계의 85%지만, 이 구현은 로컬 기술 단계 부분 수용일 뿐 **공식 최종완성률 UNASSESSED**, `[작업중]` 유지, 판매/Production RELEASE HOLD 및 크몽 미등록이다.

## 실제 구현
- `bidax/batch.py`: 완료된 공고 수집 배치를 조회·재전송할 때 전체 페이지 수·SHA-256 해시가 유효한지 확인. 사후 변조 데이터가 완료 상태로 표시되지 않도록 중단. 수집 중 과도한 전체 페이지 해시 반복 방지.
- `bidax/transport.py`: 임의 정수·문자열을 요청 승인으로 간주하지 않고 정확한 `True`만 허용. URL에 고객키가 포함된 예기치 못한 urllib 오류는 사용자 메시지에 전파하지 않음. 네트워크 타임아웃/연결 오류는 기존 유한 재시도와 요청예산으로 제한. KST 날짜가 바뀌면 재시도 예산 날짜 갱신. JSON 중복 키 거부는 보존.
- `tests/test_p85_security.py`: 7종 합성 회귀(완료배치 변조2, 승인값 거절, 오류 비밀누출, 타임아웃/예산2, HTTP403). 네트워크는 전부 가짜 opener.

## 결과 및 잔여 게이트
- 로컬 Linux Python3.13.5 `python -Werror::ResourceWarning -m unittest discover -s tests -q`: **90 PASS / 0 FAIL / 0 SKIP** (기존83+신규7). `python -m compileall -q bidax tests packaging run_bidax.py`: PASS. 기존 Tk8.6 Linux Xvfb GUI 기본 스모크는 이전 기록이며 이번 후속 범위의 Windows 증빙은 아니다.
- GitHub 원격 코드·테스트 3파일과 SHA 직접 readback 완료. 신규 GitHub Python Actions는 별도 검증 전 **미검증**.
- 실제 정부 OpenAPI 호출, 실제 원문·첨부, 100공고와 10자격 사례, 운영키/할당량·상업권 확인, Windows10/11·Python3.11·EXE 설치/제거, 고객 승인·PDF 인쇄·역할 인증·암호화·Production 및 최종 점수 가중치 **미검증**.
- SHA-256은 우발적 손상 탐지이지 DB 관리자 공격자를 견디는 전자서명이 아니다. 네트워크 예외 메시지 억제는 OS/프록시의 URL 로깅 방지를 보증하지 않는다. 실제 API 키 운영 전 별도 보안 점검 필수.
- 기존 BID OWL·타 Freelancer 제품·중앙 크몽 29원천/19판매/등록 이력 변경 없음. Git 이전 기능 기준 `a5266b4044cfb4217aa620d555094407beaab71e` 복구 가능. 원본 고객자료·비밀·유료/API 연결 없이 개발.

## 아키텍처 선택
중앙 SaaS(A)는 상시 수집 가능하지만 호스팅 비용과 고객 비밀 집중 위험이 크다. 현재 로컬 Tkinter/SQLite(B)는 서버비 0원 목표·기밀 최소화·작은 변경 위험에 적합하므로 유지한다. PC 종료 중 알림/수집 중단을 고객 고지하고, 실/API/Windows/법무/고객 수락 및 사용자 확정 R01–R21 가중치 이후만 공식 85%를 판정한다.
