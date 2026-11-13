# BID AX v2 — 3모듈 오프라인 기술 검증 (2026-11-13 KST)

## 범위 및 정확한 판정

- 기준: `hibi89/Freelancer@product/bid-ax-public-procurement`; 최종설계 기존 R01–R21 + 사용자 승인 R22–R29 = 총 29개. 기존 소스/SQLite 스키마/이전 테스트 결과 보존.
- **추가된 실 동작:** `bidax/onbid.py` 온비드 **사용자가 적법하게 확보한 정규화된 로컬 JSON 스냅샷**의 검증/원자적 저장/수정이력/중복방지/공고+물건 식별자 연결/결과 상태의 별도 provenance·CHECK_REQUIRED 및 공매 인수조건 체크리스트. `bidax/court.py` 사용자 명시 동의 뒤 로컬 TXT/PDF의 해시·메타데이터 증거를 SQLite에 보관, TXT는 키워드 언급만 표시, PDF 내용은 파싱하지 않음. 기존 입찰 원장과 테이블 namespace 별도.
- `bidax/cli.py` 네 새 명령 `onbid-import`, `onbid-report`, `court-import`, `court-report`. 기존 GUI에 4개 새 동작을 추가하고 Tk 컨트롤러도 오프라인으로 재사용. 합성 예시 `examples/onbid_*_synthetic.json`, `examples/court_synthetic.txt` 추가.
- **정직한 제한:** 온비드는 공식 REST JSON을 자동 수집·직접 파싱하는 어댑터가 아니라 수동으로 정규화된 파일을 수용한다. 수집대상별 실제 API 오퍼레이션/응답계약 및 고객 계정·원본 라이선스/첨부 재배포 권리 미검증. 법원경매 일반 무료 API/무허가 크롤링 없음. TXT 단어 존재는 법적 권리 판정이 아님. PDF는 해시만, OCR/멀웨어 검사/권리 추출 기능 없음. 실 고객문서·실 법원자료 0건.

## R22–R29 적용 후 상태

| ID | 구현·검증된 범위 | 차단된 전체 수용 |
|---|---|---|
| R22 | 온비드 공식 API 목록·결과 상세의 무료/기본 트래픽 메타데이터 조사 | 고객 실제 상업·첨부 재배포/서비스별 승인·원본 계약 |
| R23 | 로컬 정규화 JSON 유효성·출처/상태 확인·원자적 import | 실 온비드 API 키·원문 응답 매핑·실 페이지/429/쿼터/자동 중단복구 |
| R24 | 공고·물건·공매조건 키 분리, 독립 SQLite fingerprint·중복/변조·오래된 변경 차단 | 실 원문 URL/가격·유찰 상태 독립 대조 |
| R25 | 로컬 정규화 낙찰/유찰/취소 결과와 물건 연결, 다른 공매조건은 조인 금지 | 실제 결과 API 원문·취소/정정/갱신 확증 |
| R26 | 가격·기간·유찰항목 및 등기/점유/세금·명도 보수적 체크리스트 | 시세·세금/인수권리 검증·투자결정·상담 |
| R27 | 소유자 동의 CLI/GUI+로컬 TXT/PDF 파일 해시/중복·사건 키/5MiB/확장자/심볼릭링크 차단 | 실 PDF 원문 파싱·악성코드 검사·고객 파일권리/개인정보 정책 |
| R28 | TXT 키워드 언급과 필수 사람 검토 체크리스트; PDF 미추출 표기 | 실제 매각물건명세서·현황조사서/등기 문서 추출 및 전문 권리 검토 |
| R29 | 세 출처 DB 테이블/ID 분리, GUI/CLI, 합성 3모듈 공존 | 각 계층 접근권한/상용 배포/고객 PC·보안·사용자 수용 |

**출시/최종 판정:** R01–R29의 사용자 승인 100점 가중치 및 실제 최종 수용 근거가 불완전하다. 공식 전체 **85% 미입증 → 최종완성률 UNASSESSED**, `[작업중]`·`RELEASE HOLD`·크몽 미등록 유지. 내부 기술 단계 이름의 P85는 최종 제품 85% 공식률 아님.

## 로컬 재현 명령

```bash
python -Werror::ResourceWarning -m unittest discover -s tests -q
python -m compileall -q bidax packaging tests run_bidax.py
python -m bidax.cli --db ./local.db onbid-import examples/onbid_assets_synthetic.json
python -m bidax.cli --db ./local.db onbid-import examples/onbid_results_synthetic.json
python -m bidax.cli --db ./local.db onbid-report
python -m bidax.cli --db ./local.db court-import examples/court_synthetic.txt --case-id 2026타경999 --source-note "본인 합성문서" --consent
python -m bidax.cli --db ./local.db court-report 2026타경999
```

검증: Linux Python3.13.5 로컬 **130 PASS/0 FAIL/0 SKIP**, compileall PASS, Linux Xvfb Tk8.6 + 3모듈 controller smoke PASS, Python zipapp CLI onbid/court-import/report 실행 PASS. 테스트는 합성/mock·고객자료 없는 환경이며 실제 Windows 10/11 Python3.11·Windows EXE·온비드/나라장터 실 API/권리/법원 문서분석/고객 승인 **NOT_RUN**. GitHub CI는 별도로 확인해야 한다.

## 로컬 보안·장애 원칙

- 기존 고객 DB 덮어쓰기 금지. 감사 이벤트 SHA는 우발적 변조 검사용이고 외부 공격자에 대한 디지털 서명·법적 증명은 아님. 백업/복구는 기존 create-only 경로 사용.
- PDF는 **바이너리 해시만** 내고 외부 라이브러리의 PDF parser/render/JS/macro 실행 전혀 없음. 5MiB 이내 정규파일만, 원문 DB에 저장 안 함. TXT 추출 문장은 저장하지 않고 키워드 분류명만. `--consent` 없으면 거부.
- 출처 상이한 공고번호·동일 물건번호는 서로 다른 namespace로 분리하고 최신 결과를 공식 입찰 자격으로 전환하지 않는다.
- Windows 실기에 배포된 파일이 아님; `.pyz`는 Python3.11+ 별도 설치가 필요한 비출시 검증 패키지.

## 공식 출처 (메타데이터만 확인)

- 나라장터: https://www.data.go.kr/data/15129394/openapi.do
- 온비드 물건: https://www.data.go.kr/data/15157220/openapi.do
- 온비드 낙찰/유찰/취소 결과: https://www.data.go.kr/data/15157254/openapi.do
- 법원 API: https://openapi.scourt.go.kr/kgso202m01.do (일반 공개 API 추후 제공 예정, 별도 협의 필요)
