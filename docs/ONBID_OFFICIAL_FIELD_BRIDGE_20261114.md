# BID AX — 온비드 공식 결과목록 10건 기반 필드 감사·상세 후보 (오프라인)

2026-11-14 KST. 최종설계 R01–R29 고정, 목표 85% 아직 미입증.

## 확인된 실제 사용자 Windows 증거
- 온비드 15157252 실응답 첫 페이지 10건 요청/10건 확인, 성공 코드 후보, API 보고 전체 186건, 저장본 canonical SHA256 일치.
- 실제 186건 전수 수집은 아님. 고객 API 키/원문 JSON/개별 물건정보는 개발자에게 전달되지 않음.
- 공공데이터포털 15157252·15157254 공식 자료에서 결과상세 조회 식별자로 cltrMngNo(필수), pbctCdtnNo(선택)를 명시하지만 실제 10개 행에서 이 필드가 확인된 것은 아직 아님.
- 출처: https://www.data.go.kr/data/15157252/openapi.do / https://www.data.go.kr/data/15157254/openapi.do

## A/B 설계 비교
- A. 원본을 바로 정규화·자동 적재하면 처리 속도가 빠르나 실제 필드/권리 확인이 안 된 상태에서 잘못된 자격판정이 발생할 위험이 있다. 미채택.
- B. 격리본의 서비스·해시·페이지·건수를 먼저 검사한 뒤 공개 필드의 존재 건수만 노출하고 실행되지 않은 상세조회 후보만 고객 PC에 별도 저장한다. 서버비 0, 보안과 유지보수에 유리하다. 채택.

## 실제 구현
- bidax/onbid_official_bridge.py: 이미 저장된 15157252 격리 패킷을 오프라인으로 검사, 공개 필드의 존재 건수만 출력. 알 수 없는 실제 필드 이름과 데이터 값은 표시하지 않음.
- onbid-field-audit LOCAL_PACKET: 원본 패킷에 대한 공개 필드별 존재 건수·식별자 형식 검사. 네트워크, 서비스키, 자동 DB 임포트 없음.
- onbid-detail-queue LOCAL_PACKET --out NEW_FILE --consent: 모든 항목의 식별자가 올바르고 중복되지 않을 때만 15157254 조회 후보를 사용자 PC의 새 JSON에 기록. 필요한 식별자가 누락되거나 변조·중복되면 실패, 부분 저장·기존 파일 덮어쓰기 금지.
- 상세 후보에는 실제 물건관리번호가 포함될 수 있으므로 이 로컬 파일은 ChatGPT/GitHub에 보내지 말 것. 실제 API 호출은 0회, 실행 권한 자동 위임 없음.

## 검증 / 미검증
- Linux Python3.13.5 전체 unittest **235 PASS/0 FAIL** (기존220+신규15); compileall PASS, Python3.11 AST 35개 PASS.
- GitHub 제품 코드/CLI/신규 테스트 원격 Git blob 3/3 일치. 사용자 실제 파일에서 개별 ID 필드 존재 및 최신 Windows 실행은 NOT_RUN.
- 본 업데이트는 Python/Windows CI 신규 실행 전 상태임. 나머지 3개 실제 API, 18개 후속 페이지, 100실공고·10인간검토, 설치/상용권/고객 수용 미완료.
- 최종 공식 UNASSESSED, 85% 미입증, [작업중], RELEASE HOLD, 크몽 미등록.

## 사용자 Windows 오프라인 명령 (업데이트된 소스에 한함)
py -3.11 -m bidax.cli --db .\local\test.db onbid-field-audit C:\PATH\TO\result_001.json
py -3.11 -m bidax.cli --db .\local\test.db onbid-detail-queue C:\PATH\TO\result_001.json --out .\local\detail_candidates.json --consent
