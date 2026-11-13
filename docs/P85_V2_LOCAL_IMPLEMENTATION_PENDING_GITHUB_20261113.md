# BID AX v2 — R22–R29 로컬 시제품 증거 및 원격 동기화 대기
**2026-11-13 KST.** 사용자 지시: 제품 최종설계 R01–R29 전체 85%. 요구 29개는 변경하지 않음. 현행 원격 코드 v2 확장 설계 후, **로컬 시제품**만 추가됨.

## 로컬 구현·검증
- `bidax/onbid.py`: 온비드 사용자 보유·정규화 로컬 JSON 스냅샷. 공식 서류·API 응답으로 오인하지 않게 `ONBID_LOCAL_AUTHORIZED_SNAPSHOT` 계약 및 문서 URL·KST 시간 확인. 공고번호/물건/공매조건 원장 분리·SHA256 이벤트·동일 파일 재실행 중복 제거·옛 데이터/변조 차단, 낙찰/유찰/취소 결과 참조. 모든 물건은 `추가 확인 필요`.
- `bidax/court.py`: 법원경매 PDF/TXT 로컬 동의 필수, 5MiB 상한·링크·확장자·서명 검증, 소스 해시/문서 메타데이터 및 체크리스트만 저장. TXT는 키워드 분류명만, PDF는 **파싱·OCR·법률판단하지 않음**. 법원 오픈API·웹수집 0.
- CLI `onbid-import`, `onbid-report`, `court-import --consent`, `court-report`, GUI 4동작, 합성 예시. 기존 나라장터 공고 원장과 테이블 namespace 완전 분리.
- Python3.13.5 Linux `python -Werror::ResourceWarning -m unittest discover -s tests -q`: **130 PASS/0 FAIL/0 SKIP** (기존 94+신규36), compileall PASS, Tk8.6 Xvfb/controller smoke PASS, 신규 pyz 합성 온비드·법원 CLI 실 실행 PASS.
- `source ZIP`와 `PYTHON_ZIPAPP_NOT_EXE` 독립 로컬 생성·내부 SHA/파일목록 확인. 파일은 비출시 로컬 검증 산출물이며 원격 GitHub에 소스 미반영.

## 명시적으로 미검증/차단
- 실제 온비드/나라장터 0 API 호출, 인증키 0, 실 공식 응답 필드매핑·운영한도·권리/재배포 승인 미검증; 실제 법원경매 문서 파싱·등기 권리검토 0.
- Windows10/11 Python3.11/EXE, 실제 고객, 코드 동일 SHA 원격 CI, R01–R29의 사용자 승인 점수 가중치 없음.
- **최종완성률 공식 UNASSESSED / 85% 미달성·검증대기 / [작업중] 유지 / RELEASE HOLD / 미등록.** 구현 진행을 제품 최종률로 환산하지 않는다.

## 복구/동기화
- 기존 `hibi89/Freelancer@product/bid-ax-public-procurement` 기준 ab0d92a333a18e01a585a99d6a6b5812ab0c6305; 원본/다른 브랜치/BID OWL 변경 0.
- 동기화 시 최신 브랜치 확인, 원본 보존, 9개 변경 파일·로컬 130 테스트 재현, 코드 Git blob readback, Python CI 별도 실행 후 STATUS/HANDOFF와 중앙 크몽 원장 재갱신. 기존 자동/유료 CI는 승인 전 미실행.
