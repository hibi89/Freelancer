# BID AX: 온비드 결과목록 첫 페이지 실제 10건 검증 및 오프라인 수집 계획

2026-11-14 KST. 최종설계 R01~R29 고정, 최종 85% 미인증.

## 실제 사용자 Windows 검증 (민감정보 미수신)
- 사용자 로컬에서 API 15157252 실제 단일 페이지 응답을 저장하고 안전한 구조와 건수만 출력.
- `STATUS_CLASS=SUCCESS_CODE_CANDIDATE`, `pageNo=1`, `numOfRows=10`, `totalCount=186`, `items.item` 자료형은 `list`, 실제 길이 **10**, 기대 **10**.
- 로컬 JSON canonical SHA-256 검사 일치. 저장한 10개 항목은 채팅/깃허브로 전송하지 않았으며, 보고된 총 186건의 실제 전체 수집은 수행하지 않음.
- 데이터 내용·필드 매핑·정부 디지털 서명·상업 이용권·자격판정·실고객 검증은 미확인.

## 추가 구현
- `bidax/api_gateway.py`에서 G2B 중첩 `response.header.resultCode`와 온비드 최상위 `header.resultCode`의 비성공 코드를 **저장 전 차단**. 미확인 구조는 여전히 격리만 허용.
- `bidax/response_audit.py`의 `plan_remaining_pages`는 인증키/네트워크 없이 **기존에 저장된 격리 파일**을 구조·건수·해시 검사한 후 메타데이터만 반환.
- `bidax/cli.py`에 **오프라인 전용** `api-page-plan LOCAL_FILE` 추가.
- 이번 186건 보고값과 페이지당 10건이면 **19페이지 예상**. 첫 페이지 10건만 증거가 있으며 2페이지 이후 **18페이지는 호출·검증되지 않음**. 이후 API 응답에 따라 전체 건수는 바뀔 수 있음.
- 실패 응답/페이지 불일치/개수 불일치 시 페이지 계획을 거부하며 `auto_fetch_allowed=false`, `source_field_mapping_verified=false` 유지.

## 검증 및 제한
- 로컬 Linux Python3.13.5 `python -Werror::ResourceWarning -m unittest discover -s tests -q`: **220 PASS / 0 FAIL** (이전 215 + 신규5). Python3.11 AST 파싱 PASS, compileall PASS.
- 코드 변경 4개 파일의 원격 Git blob SHA가 로컬 검증본과 **4/4 일치**. 인증키 제공/재입력/정부 API 추가호출 0건.
- 사용자의 실제 저장 파일을 **새 CLI에서 Windows 재검증하지는 않음**. 이전 구형 프로그램에서 `api-page-plan` 실행 불가.
- 최종완성률 **UNASSESSED**, 85% 미입증, `[작업중]`, RELEASE HOLD, 크몽 미등록.

## 최신 코드 사용법 (기존 원본 파일 유지)
새 버전 소스의 `BID_AX` 폴더 PowerShell에서 다음 명령. 별도 작업 폴더에 보존된 기존 JSON 파일은 **절대경로**로 지정한다.

```powershell
py -3.11 -m bidax.cli --db .\local\test.db api-inspect '기존_파일_절대경로'
py -3.11 -m bidax.cli --db .\local\test.db api-page-plan '기존_파일_절대경로'
```

API키를 ChatGPT/GitHub로 전송하거나 데이터 원본을 업로드하지 말 것. 실제 후속 페이지 조회/대량 수집/키 외부 저장은 별도 명시 승인.
