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
