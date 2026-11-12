# REA_WEB — WEBSITE ANALYSIS & INDEPENDENT REBUILD / FINAL BLUEPRINT v1.0
**기준 2026-11-13 KST · 고객용 100% 완료 정본 · 디자인/기능 저작권·실서비스 검증 전 RELEASE HOLD**

## 0. 정체성·고객 결과
- 판매 목적: 성능이 느리거나 모바일 UX가 불편하거나 기능이 낡은 기존 웹서비스를 **허가된 범위에서 분석**하고, **계약한 페이지/기능 범위 안에 새 웹앱**을 구축·검증한다.
- REA_WEB = **웹사이트를 관찰→증거화→명세 승인→독립 재구축**하는 플랫폼. 단순 "CSV 넣으면 사이트 생성"은 `data2web_studio` 소유; 동일 제품으로 합쳐선 안 된다.
- 고객 산출물: ①기존 사이트 진단 리포트 ②관찰 증거/기능 매트릭스 ③고객 승인 화면·기능 명세 ④독립 소스/DB·배포 ZIP ⑤UI/행동·반응형/접근성 전후 비교 ⑥테스트 결과/인수·복구 안내.
- 정확한 시각적 복제/감춰진 서버 구현 자동 복원, 제3자 디자인·콘텐츠 무단 재사용은 **불가/보증 금지**. 고객이 가진 원본 소스 제공 시에만 정당한 수정/재사용 범위 확정.

## 1. 기술 출처·보존 대상
| 기술/구성 | 원본·브랜치 | 원칙 |
|---|---|---|
| REA_WEB 전체 | `hibi89/REA_Web@feature/website-analysis-rebuild` 조사 HEAD `467ec1cf875db75623c41860659a6faec64bb834` | 신규 코드는 원본 저장소에서만 |
| Fable 5.1 | `hibi89/REA_Web@import/fable51-bbe72c0`, pinned `7e6f273b359b207fad8f92016226e3058cbcb839` | 원본 정적 scanner 기능과 확장 관찰 계약 구분 |
| Astra P4 | `hibi89/REA_Web@import/astra-p4-b3166b6`, pinned `f044b66e799289a5a353fdb9cbfdb324e683ffa3` | 관찰/추정/미확인 근거 provenance |
| REA Pro builder | `hibi89/REA_Web@feature/d27-windows-python-discovery`, 검토 기준 `97b6e5cab7b8ffb4e1ee7f5e593021f4dac2598d` | FastAPI/SQLite 독립 앱 생성·ZIP·보안/복구 자산 보존 |
| REA 기존 오케스트레이터 | `feature/orchestrator` 과거 pinned `46060b4...` | 증거 adapter 및 기존 테스트 |
| DATA2WEB | Private `hibi89/data2web_studio` | CSV/Excel→오프라인 HTML 전용, 업무 정체성 혼합 금지 |
| Playwright/Chromium + Pillow | 웹 동작/화면 시각차이 | 실제 브라우저로 관찰, 정적 Fable GET과 구별 |

## 2. 설계 대안과 채택 근거
| 방식 | 성능/개발비 | 운영/유지보수 | 법적·품질 위험 | 판단 |
|---|---|---|---|---|
| A. URL 입력 즉시 HTML/CSS 스크레이핑→원본 동일 복제 | 빠른 저품질 데모 | 런타임 변경에 취약 | 저작권/사용권·숨겨진 동작 추정·약관 위반 위험 | 배제 |
| B. 수작업 웹 에이전시 전면 신규 개발 | 중간~고비용 | 사람 실무에 의존 | 고객 요구가 늘면 납기·원가 불안정 | 고객별 예외 |
| C. **허가형 관찰 Fable/Playwright + Astra 증거 + 사람 승인 + Pro 독립 구축 + E2E 수용** | 초기 모듈/계약 검증 필요 | 반복되는 승인형 표준 템플릿·테스트 유지 가능 | 확인된 사실/추정 구분·원본 보존 유리 | **채택** |
| D. 데이터 전용 DATA2WEB로 제품 정체성 대체 | 최저 | 쉬움 | 기존 웹사이트 기능 분석·재구축 요구 불충족 | 별도 상품으로만 |

## 3. 완성품의 상세 사용자 동선 (100%)
1. 고객이 소유/관리하거나 명시 허가한 사이트 목록, URL/페이지 수, 접근 권한, **관찰 범위/속도/기간**과 고객 요청 기능/브랜드/문구를 제출. 민감정보·로그인 쿠키/토큰의 처리 방식 사전 합의.
2. 관찰 계획 수립: 페이지 allowlist, 클릭/조회 허용 행동, 세션별 max requests/스크린샷/바이트·시간, 금지된 기능(실결제·파괴적 폼 전송), viewport 목록과 사용자 흐름. `PLAN_PENDING_APPROVAL`.
3. 고객이 계획 승인. DNS resolve 및 redirect chain을 포함해 SSRF/내부 네트워크/localhost/cloud metadata 차단; 대상 사이트의 robots/약관·상표/저작권 범위 확인.
4. **Playwright Chromium** 실제 화면에서 홈·목록·검색·필터·상세·네비게이션·폼(안전한 synthetic input만)의 상태 전이 관찰. PC 1280×720, 모바일 390×844 같은 대표 뷰포트와 접근성/키보드 측정.
5. **Fable 5.1 정적 스캐너**가 지원되는 HTML/DOM/자산 metadata 범위를 추출하고, 별도 Playwright 관찰 기록과 **동일 실행기로 가장하지 않고** 버전·출처·측정 시각을 분리한다. 실제 Fable `--record` 연계는 지원 포맷 확인 후 활성.
6. **Astra P4**는 screenshot, selector, path/action, observed/inferred/unknown, DOM/API 사실의 수준, SHA, missing/conflict를 증거 원장에 기록하고 `FUNCTIONAL_SPEC_DRAFT` 생성.
7. 요구명세 화면: 사이트맵, UI 컴포넌트, 반응형 breakpoints, 디자인 토큰/글꼴/이미지 사용권, 페이지별 화면, 기능/데이터/권한/API 계약과 **확인 불가** 항목을 구분하여 표시.
8. 고객이 보류·수정·승인. `spec_hash + evidence_digest + customer_data_digest + reviewer_identity`로 묶은 승인 기록만 유효. 스펙 변경/원본 drift 발생 시 재승인.
9. **REA Pro 독립 앱 builder**가 자체 코드/템플릿 + 고객이 소유하고 승인한 데이터로 새 FastAPI/SQLite 서비스를 생성. 목록/검색/필터/상세·폼 등 계약된 기능만; 원본 사이트 HTML/CSS/JS/상표/이미지 무단 이식 금지.
10. 생성 앱의 정보 구조/화면/핵심 인터랙션을 원래 사이트에서 관찰한 범위와 **행동 동등성의 합의된 기준**으로 비교: 네비게이션/검색 결과·폼 검증·모바일·API response/데이터 수치·스크린샷 차이/사용성.
11. 차이는 `EXPECTED_CHANGE`, `DEFECT`, `NOT_OBSERVED`, `LEGAL/ASSET_HOLD`로 분리하고, 자동 재수정은 승인된 범위·횟수/시간/비용 한도 내에서만. `VISUAL_DIFFERENCE_REQUIRES_HUMAN_REVIEW`는 성공을 의미하지 않음.
12. 고객이 납품 범위·디자인·성능·접근성·자료권리를 검수하고 최종 서면 승인. 승인 전 Production/Vercel·DNS·실결제·실사용자 계정 전환 금지.
13. 고객에게 소스/ZIP, 배포 가이드, SSL/TLS/환경/보안 설정, DB 백업/복구, 사용된 폰트/이미지/템플릿 권리/NOTICE, 실제 E2E QA와 미지원 목록 전달. 버전·해시/복구 지점 기록.

## 4. 전체 시스템 구조
```text
Customer intake (authorized URL + access rights + screenshots/videos
                 + branding, approved data and functional requirements)
      │
      ▼
Permission & Scope Gate
  - owner/legal scope, path/viewport/action allowlist, rate/time quotas
  - robots/ToS/PII, origin redirect DNS recheck, anti-SSRF
      │ owner APPROVE
      ▼
Source Observer Layer
  ├─ Fable5.1 STATIC: supported HTML/DOM/metadata inspection
  ├─ Playwright Chromium: real nav/search/filter/details/multi-step/screenshot
  ├─ optional Fable --record adapter: only after actual format + rights proof
  └─ supplied recordings/screenshots: user-origin evidence, never 'live observed'
      │    observed/inferred/unknown kept distinct
      ▼
Astra P4 Evidence/Requirements Mapper
  - evidence provenance, selectors/path/time/sha, confidence limits
  - UI components, screens, states, data and behavior spec draft
      │
      ▼
Human Approval Workbench
  - HOLD/EDIT/APPROVE/REJECT, actor + spec/evidence/data digest + expiry
      │ only verified approved spec
      ▼
REA Pro Independent App Builder
  - FastAPI / SQLite / Python 3.11 / HTML/CSS/JS templates
  - approved customer-owned content, no source cloning
  - generated source + dependency manifest + tests
      │
      ▼
QA Harness: source observation ↔ approved spec ↔ generated behavior
  ├─ Playwright real Chromium/Edge (desktop/mobile)
  ├─ API TestClient, SQLite source totals/queries
  ├─ visual diff Pillow + DOM structural differences
  ├─ accessibility keyboard/labels + mobile overflow
  └─ XSS/CSRF/SSRF/credentials/headers + regression
      │
      ▼
Delivery (source ZIP + manifest SHA + backup/restore + QA acceptance)
      └─ customer release consent → optional Production/Vercel/hosting
```

## 5. 모듈·데이터/계약 설계
### 5.1 Intake & scope
- `customer_authorization`: 고객이 보유한 권리의 유형(관찰/참고/재사용/소스 수령/실제 배포)을 별도 체크. '인터넷 공개'는 코드/디자인 복제권이 아니다.
- `scope_policy`: URL origin/path/vhost allowlist, rate limit, max pages, actions, scrape budget, PII masked capture, no login without approval.
- `source_catalog`: 관찰 대상별 user-provided screenshot vs live browser vs Fable-static을 별도 `source_kind`로 태깅, 동일 증거 SHA를 교차 검증.
- `observer`: request/redirect/DNS allowlist, document state ready·ajax wait, screenshots/DOM, selectors, page navigation traces, viewport dimensions, JS errors. 미허용 network calls 차단.
- `fable_bridge`: 정적/동적 지원 capabilities handshake; `--record` 미지원/불일치 시 `HOLD` 또는 별도 Playwright 관찰 경로를 명시, 결과 하나로 합치지 않음.

### 5.2 Evidence/Astra
- `evidence_store`: append-only observation IDs, image/DOM artifact checksums, metadata timestamp, retention, PII scrub; artifact file 변경 시 invalidated.
- `astra_bridge`: `ObservationBundle`/실제 검증된 `derive_spec`와 계약 버전; source attribution + observed/inferred/unknown; unknown을 자동 확인 사실로 승격시키지 않음.
- `requirements_mapper`: 페이지/네비게이션/데이터/권한/API/폼·분기 스펙; 화면 차이와 기능 차이를 독립하여 관리.
- `cost_estimator`: 페이지 수/기능/수정회차/모델 토큰/브라우저 requests/정적 자산/배포비 소요; 사전 상한 초과 시 자동 종료/고객 승인 요구.

### 5.3 Approval workbench
- `spec_workbench`: 시각·행동·데이터/브랜드 요구 시각화, '관찰된 사실/추정/필요 고객확인' 라벨, 변경 이력/기능 우선순위.
- `review_ledger`: trusted actor identity, role, evidence digest, spec version, input data SHA, approve time/expiration. HTML checkbox 또는 forged JSON `approved:true`를 승인 증명으로 사용 금지.
- `edition_contract`: 수정 1회·7개 페이지·2개 기능 등 계약 범위 초과 시 change request / 가격·납기 재승인.

### 5.4 Independent app builder
- `rea/orchestrator.py`, `rea/mvp.py`, `rea/templates` 기술 재사용. 데이터 mapping은 고정·검증된 CSV/JSON/SQLite 범위.
- 화면: 현대적 컴포넌트 구조, 재사용 가능한 레이아웃/디자인 토큰, 반응형 navigation, text contrast/keyboard focus, 고객 브랜드 합법 사용.
- 백엔드: FastAPI typed routes, 입력 검증, static asset/version hashing, SQLite schema migration/backup, read-only 조회와 admin write 분리. auth/admin/결제는 개발·검증 범위 확인 전 기본 제외.
- 생성 파일: create-only unique output dir, Atomic write/rename, 기존 고객 사이트 파일 덮어쓰기 금지. 로그에 secret/reused session cookie를 기록하지 않음.
- 기존 서비스 DB를 무단 수정하거나 기존 고객 세션을 이관하지 않는다. 운영 DB migration은 별도 승인된 검수·롤백/중단계획 뒤 진행.

### 5.5 비교/검증
- 입력 3종 합성 사이트: catalog/search, inventory/filter, directory/detail. 이 합성 범위를 초과한 예약/결제/인증 기능은 별도 명세·테스트 필요.
- Fable static getter vs Playwright UI observer를 별도 provenance로 비교하고, Astra observed vs inferred로 각 단위에 근거 태그.
- Visual: identical pixel claim 금지; 이미지 RGB diff·전후 화면 크기/viewport·레이아웃/DOM/상호작용 증거, 원본 사이트의 변동이나 애니메이션을 고려한 수동 검수.
- Functional: search/filter/detail 결과·query/page state·키보드·mobile orientation·API status/mime·Console/Network/404·form validation·XSS/reflection.
- Security: original HTML includes injections, page capture SSRF via redirect, malicious image URLs, local/private IP/metadata blocked, app emitted HTML escape, CSP, safe headers.
- Recovery: browser/pipeline kill mid-build, partial artifact, customer revision after approval, data file changed, duplicate build same ID, conflicting output path, old installer. Old working build always recoverable.
- Tester must run on exact SHA and extracted deliverable, not source-only. Generated app HTTP+browser with independent clean environment acceptance.

### 5.6 Evidence contract 예시 (설계 스키마; 구현 확정 아님)
```json
{
  "contract": "rea.site.evidence.v1",
  "site_ref": "customer-approved-source",
  "scope_digest": "<sha256>",
  "observation": {
    "id": "<sha256>",
    "source_kind": "playwright_browser|fable_static|user_screenshot",
    "page_path": "/catalog",
    "viewport": {"width":1280,"height":720},
    "observed_actions": [{"action":"search","state_before":"A","state_after":"B"}],
    "claim_level": "observed|inferred|unknown",
    "source_sha256": "<sha256>"
  },
  "requirements": {"status":"REVIEW_REQUIRED","spec_digest":"<sha256>"},
  "approval": {"state":"HOLD","trusted_actor_id":null},
  "rebuild": {"release_allowed":false}
}
```
데이터의 `claim_level`은 각 개별 finding 단위로 다뤄야 하며, 이 예시는 구조 설명만 한다. 실제 Astra P4 원본 `ObservationBundle` 호환 여부는 contract test로 확인.

## 6. 보안/저작권/권한
- 보호된 사이트/로그인·유료 컨텐츠/타인 고객 개인정보·CAPTCHA 우회·무단 scraping 및 IP/robots/ToS 위반 금지. 고객이 제공한 소스에 대한 권리도 계약상 확인한다.
- 고객 제공 영상/스크린샷은 **관찰 사실**과 다른 출처; 스크린샷만으로 숨겨진 서버/기능 재현 불가.
- 스크린샷/DOM/HTML에 보이는 고객 개인 정보 마스킹 및 보존기간 상한, 사용권 기록; 공유 GitHub는 고객 자료 보관 장소가 아님.
- 전체 앱 생성 시 Open Source template/라이브러리의 LICENSE/NOTICE, 외부 사진·아이콘·폰트 상용 사용권 확인.
- 구현 후 고객 운영 서버 배포는 TLS, 도메인, 비밀번호/계정/DB 비밀, cookie/session, 백업/접근정책, 모니터링까지 실제 검증해야 한다.

## 7. 견적과 납품 한계
- STANDARD는 계약한 **반응형 페이지 7개**(템플릿 기준)와 정의된 기본 사용자 흐름 1~2종, 읽기 전용 목록/검색/필터/상세를 주력. 실제 원사이트 데이터/권리/디자인 사용 여부 고객 서명.
- 고객 요구가 로그인·결제·복합 예약·API/ERP 연동·대량 데이터 이관·복잡 멀티테넌트 관리자라면 Premium 또는 별도 견적, 검증 완료되지 않은 기능은 제외.
- '웹사이트 전체를 반값으로 다 복제' 아님. 기존 웹 디자이너/프론트엔드 업무·고객 피드백이 남기 때문에 무제한 수정을 약속하지 않는다.
- 생산성 지표: 분석/명세 작성 비용, 페이지/컴포넌트당 수정 시간, 중복 버그, 고객 검수 횟수, QA 결함 발견/복구. 현재까지 **실고객 데이터 미검증**.

## 8. 최종 100% 출고 게이트
- 원래 사이트 분석 명세→고객 승인→새 독립 앱→비교·보안·Windows/Edge/Chrome 및 실제 hosting까지 고객 계약 범위에서 검증.
- 고객이 참조/컨텐츠 권리와 납품/수정 권한을 확보하고 서명/검수·운영 비용·환불/지원·사업자 거래증빙을 확인.
- [수용표](ACCEPTANCE_AND_ROADMAP.md) 전부 통과. `RELEASE HOLD` 해제는 실제 제품 원본 repo의 결론과 고객 승인에 따라야 하며 문서 작성만으로 95/100 달성 주장 금지.
