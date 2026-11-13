# BID AX — P85 목표 3모듈 GitHub 기능 검증 최신 근거
**기준 2026-11-14 KST; 기능 커밋 2a9852bcb47a271a4119f67dfcaf8ec35ae2a632.** 사용자 목표: 최종설계 R01–R29 기준 85%. **공식 최종완성률: UNASSESSED, 목표 달성 미검증. [작업중]·RELEASE HOLD·크몽 미등록.**

## 이번 실제 완성/코드 출처
- 기존 오프라인 3모듈 로컬 prototype: 온비드 공매 물건·결과 SHA256/이력/중복·오래된 변경 차단 `bidax/onbid.py`, 적법한 고객 소유 PDF/TXT 로컬 사건 문서 해시·보수적 위험 체크리스트 `bidax/court.py`, `bidax/cli.py`와 `bidax/desktop.py`의 네 명령/GUI 제어, 기존 나라장터 DB 스키마 보호.
- 기능 커밋 `0b407a9edc363bf7be565356f4e9f64190b3c5f3`의 8개 파일은 로컬 검증 파일과 **원격 8/8 내용 일치**. `tests/test_p85_expansion.py`는 합성(mock)이며 정부 실 데이터가 아니다.
- `bidax/onbid_plan.py`는 공공데이터포털이 명시한 3개 공식 메타데이터 서비스의 **실행 불가 요청 계획**: 15157220 공고 물건(pbancMngNo), 15157252 결과목록(cltrTypeCd/prptDivCd/opbdDtStart/end), 15157254 결과상세(cltrMngNo, 선택 pbctCdtnNo). `onbid-plan` CLI 명령과 6개 테스트를 추가.
- 최신 기능 커밋 `2a9852bcb47a271a4119f67dfcaf8ec35ae2a632`의 4개 파일 `bidax/onbid_plan.py`, `bidax/cli.py`, `tests/test_onbid_plan.py`, `docs/P85_3MODULE_GITHUB_SYNC_AND_ONBID_API_PLAN_20261114.md`도 **원격 내용 4/4 일치**.
- 상품 3모듈 데이터 namespace 분리. 온비드 원문은 **공식 실 HTTP 응답 파서가 아니라 승인된 정규화 로컬 JSON**. PDF는 원문 추출/멀웨어 검사/법적 권리분석 미구현. `network_ready=false` 계획만 생성하므로 사용자 키 없이 API·크롤링 호출 없음.

## 재현 가능한 검증
- 로컬 Linux Python3.13.5: `python -Werror::ResourceWarning -m unittest discover -s tests -q` **136 PASS / 0 FAIL / 0 SKIP** (이전 130 + 공식형 API 입력 계획 테스트 6).
- `python -m compileall -q bidax tests` PASS; `ast.parse(feature_version=(3,11))` 22 파일 PASS (**문법만**, 실제 Python3.11 런타임 미검증).
- 표준 라이브러리 `packaging/build_portable.py` 출력 Python zipapp `BID_AX_V2_PORTABLE_20261114.pyz` SHA256 `2fe1de178782e3b3e6698630ca4ffc243503dc0a863953f3d6d223d13f61e0f1`, **15개 파일 포함**; 실제 `onbid-plan result_detail` CLI 출력 PASS; Windows EXE가 아니며 Python 설치 필요.
- **원격 Python/GitHub Actions OS 매트릭스는 미실행**. private Actions의 과금 가능성 때문에 사용자 비용 승인 전 수동 workflow_dispatch 금지. 기존 blueprint gate SUCCESS는 Python 테스트 CI 성공과 다름.

## 공식 최종설계 29개 — 기능·수용 상태
| ID | 부분 구현 | 빠진 최종 수용 |
|---|---|---|
| R01–R04 | G2B 오프라인 7일 계획, mock 전송/유한 재시도, 원본 URL 검증 | 실 API/면허/첨부/운영권 |
| R05–R11 | 기존 SQLite·기업 프로필·증거/규칙 엔진 합성 테스트 | 실제 조달 공고 원문·자격 법률 검토 |
| R12–R15 | 오프라인 알림/보고 JSON·CSV·HTML/검토 이력/변경 체크포인트 | 상시 스케줄, 인쇄 PDF, 역할 분리, 실제 변경 자동수집 |
| R16–R18 | Tk GUI Linux Xvfb, 소스 ZIP/pyz, DB 백업/복원 | 실제 Win10/11 설치·암호화 키/ACL·고객 장애복구 |
| R19–R21 | 합성 100공고/모의 10사례·면책 안내 | 실제 공고 100건, 인간 10건, 권리·고객 수용, 판매 승인 |
| R22–R26 | 온비드 정규화 로컬 원장·결과·보수적 체크리스트, 3종 **키 없는 요청계획** | 고객 무료 API 발급·실응답/페이지·실권리·가격/낙찰 확인 |
| R27–R29 | 동의 기반 로컬 PDF/TXT 해시·사건 메타·3모듈 CLI/GUI 격리 | 실제 문서 추출·위협/개인정보 통제·전문 권리심사·상용 tier 인수 |

**재산정:** 공식 100점 가중치가 사용자 승인되지 않아 공식 비율 산출 불가. 테스트 수(136)나 엔지니어링 P85 명칭을 85%로 환산하면 정책 OWNER-FINAL-BLUEPRINT-100 위반이다. 85% 목표 [작업중], RELEASE HOLD, 미등록 이력 유지. 원천 29개/판매 19개 전체 크몽 원장과 제외 BID OWL 변경 금지.

## 다음 작업 우선순위 / 승인
1. 본인 보유 API 활용신청·상업적 이용 범위, 최신 응답/상세·공고목록 실제 원문/첨부 계약, 공식 조회량 확인. **실 API 호출·고객 데이터 전송은 별도 사용자 사전 승인**.
2. 실제 100건/사람 10사례 근거 검증, 한국어 PDF/Windows10·11/Python3.11·EXE/SmartScreen/보안 ACL·고객 지원 수용.
3. 최종설계 R01–R29 사용자 승인 가중치/세부 합격 조건 후 정확 SHA 전수 테스트로 공식 85% 판정. 승인 전 RELEASE HOLD.
4. 기존 Git 복구: 변경 전 `1b7b2ef0c00162905b4d0f4116933f682311fb0f` 또는 직전 정상 SHA를 정상 revert commit으로 적용하며 force push/고객 DB 덮어쓰기 금지.

## 공식 API 메타데이터 출처
- https://www.data.go.kr/data/15157220/openapi.do
- https://www.data.go.kr/data/15157252/openapi.do
- https://www.data.go.kr/data/15157254/openapi.do
- https://www.data.go.kr/data/15129394/openapi.do
- https://openapi.scourt.go.kr/kgso202m01.do
