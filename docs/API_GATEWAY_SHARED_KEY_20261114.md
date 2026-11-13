# BID AX — 공공데이터포털 공통 인증키 1개 / 4개 승인서비스 로컬 연결기

**2026-11-14 KST · 제품 브랜치 `hibi89/Freelancer@product/bid-ax-public-procurement` · 최종설계 R01–R29 불변.**

## 사용자 확인 및 설계 선택

사용자는 나라장터 입찰공고정보 15129394 + 온비드 공고 물건 15157220, 결과목록 15157252, 결과상세 15157254 **4개 활용신청을 완료했고 키 문자열이 동일하다고 확인했다**. 키 문자열은 **수집/저장/업로드하지 않았다**. 공통 인증키는 *동일 계정의 인증 수단*이며 각 API 접근 권한·사용량·계약은 독립이다. 무료 API와 첨부파일/원문 재판매 권리, 운영계정 승인량을 혼동하지 않는다.

- A: 중앙 SaaS 수집기는 PC 꺼져 있어도 동작하지만 서버 과금·키 공유·개인정보 위탁/운영 문제가 발생한다. **미채택.**
- B: 고객 PC 표준라이브러리 Python의 **수동 1페이지 호출 + raw JSON 격리 보관**, 키는 입력 한 번/메모리만 이용. 서버 비용 0, 고객 PC 실행 필요, API 이용계약/권리는 여전히 확인해야 한다. **선택.**

## 구현 (코드/테스트 구분)

- `bidax/api_gateway.py`의 `create_plan`: G2B `g2b_goods/services/construction/foreign` 및 온비드 `onbid_result_list`, `onbid_result_detail`의 공식 호스트·오퍼레이션·파라미터 유효성 확인. 목적지를 사용자가 임의로 지정할 수 없음.
- 온비드 **공고별 물건 15157220은 필수입력 및 기본 URL을 문서 확인했으나 operation path 원문을 독립 확인하지 못함**. `onbid_announcement_assets` **계획만 생성, 실행 금지**. 모르는 경로를 추측해 요청하거나 성공을 주장하지 않는다.
- `api-probe` CLI: 기본 실행은 **키를 요구하지 않고 오프라인 계획만 출력**. `--live --out 신규경로`를 명시해야만 `getpass`로 키를 잠깐 받아 고정된 공식 호스트에 1페이지를 요청. **이 개발/검증 과정에서 실제 HTTP 0, 키 0.**
- 승인 필수, HTTPS/TLS, 프록시/리다이렉션 차단, 제한된 응답 크기, 중복 JSON 키 거부, 키/전체 URL 오류 미노출, SQLite KST 일자별 **서비스 별도 로컬 일일 호출예산**, 429/5xx 한정 유한 재시도/시도당 예산 차감, 기존 출력파일 덮어쓰기 거부, 소유자 전용 신규 파일(가능한 OS에서 `0600`) 저장.
- 결과는 `OFFICIAL_API_RAW_UNVERIFIED_MAPPING`으로 격리 저장. **데이터·지역·자격/권리·기관 API 실제 스키마 통과는 아직 증명되지 않으며 심사 엔진에 자동 등록하지 않는다.**

## 무료·무키 상태에서 가능한 사용법

프로젝트 폴더에서 시작 (Windows 10/11은 `python` 대신 `py -3.11` 가능):

```powershell
python -m bidax.cli --db .\local\bidax.db api-probe g2b_goods examples\g2b_live_plan_LOCAL_ONLY.json
python -m bidax.cli --db .\local\bidax.db api-probe onbid_result_list examples\onbid_result_list_plan_LOCAL_ONLY.json
python -m bidax.cli --db .\local\bidax.db api-probe onbid_result_detail examples\onbid_result_detail_plan_LOCAL_ONLY.json
```

**본인 PC에서 실제 승인 키로 단일 페이지 시험**할 때에만 다음과 같이 실행한다. CLI가 표시하는 입력창에 *키를 붙여 넣어도 화면·로그에는 출력하지 않으며*, GitHub나 ChatGPT에 보내지 않는다. 출력은 기존 파일이 없는 사용자의 로컬 경로이며, 읽기/재배포권을 별도 확인한다.

```powershell
python -m bidax.cli --db .\local\bidax.db api-probe onbid_result_list examples\onbid_result_list_plan_LOCAL_ONLY.json --live --out .\local\onbid_result_001.json
```

`--live`는 기본값이 아니며 Windows 실제 실행·고객 API 서비스키·raw 응답 미검증. 사용자 PC에서 경로 `local` 폴더를 먼저 만들고 3가지 `.json` 예시는 본인 조회기간/물건번호로 수정해야 한다. **명령 실행은 정부 서버로 개인정보/키가 포함된 인증 요청을 전송한다**. 사용자 명시 허가 없이 자동실행·스케줄/키 저장 금지. 내려받은 JSON 파일이나 키를 채팅/깃허브에 업로드 금지.

## 검증 범위와 최종완성률

- 기존 로컬 167 테스트에 추가된 17건 검증은 **가짜 HTTP 응답**, 환경변수/고객키/공식 원문 없음. 검증 내용: G2B 7일 제한, 고정 호스트/서비스별 예산, 1개 동일 키 2개 서비스 호출 모의, 중복키·인증 오류, 로컬 JSON 격리, 파일 보호, 기본 계획 무HTTP.
- Python3.13.5 Linux 로컬 회귀 테스트 전체 실행 결과는 이 문서의 Git 커밋 이후 실제 출력 별도 기록. Python3.11 실제 런타임/Windows/실 API·100공고/10사람/상업 이용권 및 고객 시연 **미검증**.
- 최종 29개 정본은 `docs/FINAL_BLUEPRINT.md`와 `docs/BID_AX_FULL_BLUEPRINT_29_ACCEPTANCE_20261114.md`; 사용자 지침에 따라 **추가 가중치 승인 요청을 반복하지 않는다.** 요구별 실행 검증이 안 된 기능을 85% 완료로 산정하지 않는다. `[작업중]`, RELEASE HOLD, 크몽 미등록 유지.

## 재현·롤백

- `python -Werror::ResourceWarning -m unittest discover -s tests -q`
- `python -m compileall -q bidax tests`
- 기존 `bidax/transport.py`(선택형 G2B 전송 라이브러리)와 모든 고객 DB/다른 프리랜서 상품/BID OWL **미수정**, 신규 코드 위주로만 변경.
- Git 정상 revert로 이전 HEAD 복구, force push 금지. API `--live` 실행 시 로컬 출력/사용량 테이블이 생성될 수 있으므로 고객 DB를 먼저 백업하고 테스트 DB를 따로 사용.
