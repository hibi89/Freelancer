### 2026-11-13 — SITECRAFT AX 독립 P85 합성 기술 수용 (공식 UNASSESSED)

정확 기능·테스트 SHA `a3f31c4c676fb28c2ddded052f9cd0a0942370ad` at `hibi89/REA_Web@feature/sitecraft-ax-p85-20261113`; [Windows + Ubuntu P85 GitHub Actions](https://github.com/hibi89/REA_Web/actions/runs/43382914205) **2/2 SUCCESS**, Ubuntu24.04 **116PASS/0FAIL/1WARN**, Windows2025 **116PASS/0FAIL/1WARN**. P50/P70+원형 P85+orchestrator 회귀 포함. 서로 다른 3개 승인 합성 로컬 HTML 사이트를 desktop 1280×720/mobile 390×844 실제 Chromium 조작: 각 검색→카테고리→상세 3연속 상태, 전체 18전이, Astra P4 observed six/site, 참조 PNG24 + 생성 PNG24 + Pillow RGB difference 24, frozen Fable5.1 static GET→승인 합성 CSV 기반 독립 Pro FastAPI/SQLite→실 생성 앱 브라우저 동작 일치. 3사이트 atomic no-overwrite, 위조 digest/원본 SHA/외부 URL/iframe, 합성 XSS 문자열 textContent 검증. 시각적 동등성은 자동 승인하지 않고 `VISUAL_DIFFERENCE_REQUIRES_HUMAN_REVIEW`로 보존.

**P85 숫자는 합성 엔지니어링 단계 수용이며 최종설계 100%를 분모로 한 공식 85%가 아님.** 전체 공식률 `UNASSESSED`(승인 배점+요구별 추적 미완), 중앙 `SITECRAFT AX [작업중]` 유지·RELEASE HOLD. 실 고객·실 URL·법적 권리·Fable 실제 --record·Windows10/11 실기기 Chrome/Edge·GUI 승인·상용/Production은 미검증. 기존 원본 기능과 DATA2WEB 보존.
### 2026-11-13 SITECRAFT AX P70 independent stage acceptance — official UNASSESSED

Actual P70 source `hibi89/REA_Web@feature/sitecraft-ax-p70-20261113` exact CI SHA `cf2c1171d92408af20bae1d4d037583f900e6e4f`; [Actions P70](https://github.com/hibi89/REA_Web/actions/runs/43377441817) Ubuntu24.04 and Windows2025 each **82PASS/0FAIL/1WARN**, **2/2 SUCCESS**. Three distinct synthetic references (catalog/search, inventory/filter, directory/detail) are SHA-pinned local inputs, observed via real Chromium before/after; Astra P4 observed evidence is reviewed with three synthetic digest receipts, original frozen Fable static GET + Pro FastAPI/SQLite builds three independent apps and runs actual generated-browser action parity. Atomic new-folder-only publication and forged rights/path/hash/duplicate/partial delivery rejects are tested. P50 & original P70 regressions are included.

**This verifies the design's P70 synthetic engineering acceptance stage, not an official 70 percent of the entire final design.** Final-design score remains UNASSESSED pending owner-approved 100point weighting+requirements trace. SITECRAFT [작업중] remains and RELEASE HOLD. No live customer sites/real Fable headed Record/Win10-11 physical customer UAT or Vercel/Production.
### 2026-11-13 — SITECRAFT 독립 P50 합성 기술 CI 검증

검증 기능 SHA a5c5a718dc33778fb1df59c601feee57944603db, https://github.com/hibi89/REA_Web/actions/runs/43375663779 Ubuntu+Windows 각 50PASS/0FAIL/1WARN, 2/2 SUCCESS. Strict local contract→실 frozen Fable static GET→Astra REVIEW_REQUIRED→허가된 합성 CSV 기반 REA Pro FastAPI/SQLite 새 앱 API 수용. 원본 보존 및 경로·URL·해시 거부 확인. 공식 100점 최종설계 수치 UNASSESSED(합성 P50 단계 점수 승계 금지), 중앙 [작업중]·RELEASE HOLD 유지. 실제 고객/실 사이트·동적 Fable --record·운영 배포 미검증.
# SITECRAFT AX — REA_WEB 50/70/85/95/100 수용 게이트 및 로드맵

> **상품명: SITECRAFT AX** · 허가형 웹사이트 진단·독립 재구축. 원래 기술명·원본 저장소는 유지.

| 단계 | 누적 비율 | 합격 요건 |
|---|---:|---|
| P50 | 50 | pinned Fable5.1 local static GET 1개 + Astra 검토 draft + 고객 승인 합성 CSV→REA Pro FastAPI/SQLite 새앱 API/동작 경로 |
| P70 | 70 | 허가된 **합성 로컬 사이트 3개**의 Chromium 검색/필터/상세 before/after 관찰 및 원문 기반 spec/Pro 앱 브라우저 기능 결과 비교 |
| P85 | 85 | desktop/mobile 각 3상호작용·증거/스크린샷/DOM·Pillow 차이, owner 검토 digest, XSS/외부URL/변조 부정 검사, Windows+Linux CI |
| P95 | 95 | 실제 허가 받은 URL/고객 입력 데이터로 Fable 기록/관찰 adapter + 승인 GUI + 디자인·반응형 세부 spec → 신규 독립 앱, Windows 10/11 Chrome/Edge E2E·파일/ZIP/라이선스/복구·실 배포 사전 검증 |
| P100 | 100 | 실제 고객 권리/최종 spec/디자인 승인, 전 범위 수용/보안·접근 정책/회귀·인수 및 운영 배포 검증, 고객 납품/거래 증빙/지원정책 확정 |

### 최신 증거 범위
- 원본 `feature/website-analysis-rebuild` P85 합성 CI **#43273324679** 정확 검증 source SHA `1c3390fa3da933c5d0513196f0dcfc97b18b5e14`: Ubuntu/Windows 각 **52 PASS/0 FAIL/1 WARN, 2/2 SUCCESS**.
- 이 CI는 합성 HTML 3종×desktop/mobile 관찰+Astra observed provenance+승인 합성 CSV→Pro 행동 비교. **원본 Fable --record 전체와 실제 외부 사이트/고객 디자인 복제/실 고객 권리/Win10 실기기·배포는 미검증**.
- 2026-11-13 해총에 REA 원형 P95 **개발 중** 표시 기록. 정확한 P95 추가 검증 결과는 원본 최신 HEAD/actions를 별도 확인 전까지 달성 주장하지 않는다.
- 이번 `Freelancer` 문서 브랜치 제품 코드는 0건 수정/제품 테스트 0건 실행. 이 최종설계 자체는 코드가 아니다.

### 테스트 표준 세트
1. Source scope: 허가 URL·DNS/redirect SSRF·IP/network allowlist·rate-budget, source changed mid-scan, private routes refusal, robots/ToS user consent.
2. Observer: real desktop/mobile visual states, dynamic/filter/search/detail states, click causes actual UI change, Chrome/Edge, user screenshot vs live observation provenance.
3. Astra: observed/inferred/unknown never silently promoted, screenshot hash/source/current time, selector evidence, missing action/invalid P4 contract HOLD.
4. Workbench: actor review/edit/reject→spec SHA; stale/forged/edited after-approval; duplicate 'Approve' click; expired consent blocks builder.
5. Builder: independent customer data, 5/7/10 page templates, list/search/filter/detail/basic forms, HTML escaping/XSS/CSRF, SQLite schema/data integrity, newly created output only.
6. Comparator: action by action parity of approved scope, screenshot dimension/RGB difference/DOM, accessiblity labels/keyboard, no false 100% pixels.
7. Delivery: source SHA/ZIP manifest, fresh new folder extraction, real localhost HTTP, Chrome/Edge main flows, corrupted ZIP refusal, customer hosting TLS/secret/backup, original site unchanged.
8. Contracts/rights: user content/images/logo ownership, fonts/sources/third-party license, privacy, revisions and support, tax/receipts and deployment sign-off.

### 개발 순서
- P85 기준 원본/CI 보존 → P95 목표·기능 gap 확인 → 실제 Fable observer contract 통합 → 승인 GUI/고객 데이터권리 → 생성 UI/보안/경합/복구 → 실 PC·호스팅 테스트 → 사용권·계약·판매 승인.
- 원본 서비스에 적법한 테스트 권한이 없다면 합성 사이트만 반복 검증하고 **외부 URL 대상 미검증** 표시. 허가 없이는 실데이터를 임의 수집하지 않는다.
