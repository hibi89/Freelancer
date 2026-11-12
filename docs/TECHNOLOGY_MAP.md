# REA_WEB 기술 스택 전체 맵

| 영역 | 정확한 기술/컴포넌트 | 역할 | 상태 |
|---|---|---|---|
| 웹 관찰 정적 | Fable 5.1 pinned static scanner | 허가된 HTML/DOM metadata | 합성 local GET |
| 실제 브라우저 | Playwright Chromium, Chrome/Edge 목표 | 화면/클릭/필터/검색/반응형·상태 캡처 | Chromium 합성 3종 |
| 증거 엔진 | Astra P4 (ObservationBundle/derive_spec) | 관찰/추정 분리, spec/출처 provenance | 합성 partial |
| 스크린샷 | Pillow RGB diff | viewport별 시각 차이 검사 | 차이=동일성 증명 아님 |
| HTML/CSS/JS | HTML, CSS, Vanilla JS / 승인형 UI template | 독립 UI·시각·접근성 | Pro 코어 |
| 백엔드 | Python 3.11+ / FastAPI / Pydantic | 독립 앱 API/검증/생성 | 구현 코어 |
| 로컬 데이터 | SQLite / versioned JSON/CSV | 카탈로그·목록·조회·데이터 검증 | 합성 지원 |
| HTTP/API QA | httpx/TestClient/uvicorn/requests/bs4 | 출처/생성앱 API 수용 | 기존 검증 |
| 품질 | pytest, Playwright, Chromium desktop/mobile, Linux+Windows Actions | 브라우저/보안/회귀 | 합성 CI 검증 |
| 증거/승인 | SHA256, evidence bundle, human workbench | 사실/추정/고객 허가 분리 | 실제 고객 GUI 추가 |
| 납품 | ZIP/manifest/checksum/backup/new-path recovery | 변경/복구/출고 | Pro 코어+출고 gate |
| 서비스 운영 | 고객 서버 or optional Vercel/host, TLS/CI/CD | 실제 배포·접근 정책 | 고객 승인 후 |
| 개인정보·권리 | Data minimization, redaction, license ledger | 안전한 관찰/납품 | 고객별 별도 검증 |
| 데이터 전용 별도 | `hibi89/data2web_studio` | CSV/Excel/JSON/TSV → 데이터 UI | **REA 본상품 아님** |

## Fable / Astra / Pro 역할 구분
- Fable: 지원 범위의 웹사이트 화면/DOM 정적 분석과 향후 **검증된 브라우저 기록 adapter**. 별도 Playwright 관찰을 Fable이 이미 수행했다고 말하지 않는다.
- Astra: 스크린샷·셀렉터·기능 사실/추정/unknown을 데이터 계약으로 검토. 이미지/추정만으로 소스코드를 역생성한 것처럼 표현 금지.
- REA Pro: 표준화된 데이터를 기반으로 독립 FastAPI/SQLite 웹앱을 실제 생성하고 재실행·복구한다.
- Playwright: before/after를 실제 브라우저에서 검증. CSS 픽셀 차이는 정의상 고객 의도된 리디자인일 수도 있으므로 휴먼 판단 유지.

## 정형 데이터와 생성기 통합
고객의 JSON/CSV/XLSX 등은 DATA2WEB 라이브러리를 임의 직접 import하는 게 아니라 별도 **검증/승인 계약**으로만 사용한다. 복수 스키마 JOIN·엑셀 VBA·재무의미 자동 결정은 미지원 또는 별도 개발.

## 환경비용/권리
- 초기 독립 로컬 제품은 Python 3.11+·브라우저·SQLite만으로 데모 가능하지만 실제 고객 사이트 관찰에는 인터넷/사이트 부하·약관/권리·차단 상황이 따름.
- Production/Vercel/도메인·유료 브라우저/AI 모델·호스팅/인증 DB/저작권 사용료는 별도 비용. 외부 사이트 데이터는 권리 있는 범위에서만 요청.
- 크롬/엣지/Playwright·Python 의존성·상업적 재배포 라이선스와 필수 고지/버전 고정, 공급망 CVE 확인.
