# CITEVAULT AX — 실제 Chromium 사용자 화면·권한별 대시보드 수용 증거 (2026-11-14 KST)

## 기능·원본
- 저장소 `hibi89/Freelancer@product/rag-enterprise-knowledge`, 기능 SHA `49918ad4d0de23b8bc462830fa0789e93ebd7936`, 이전 백업 무결성 SHA `d32f530e2425da0129a4eb2e9a4a7aef6708dab8` 보존.
- 구성: `enterprise/p85-vault.mjs`의 새 `library(token)` 권한 제한 metadata-only 목록/컬렉션 KPI, `enterprise/p85-loopback.mjs` `GET /v1/library` bearer 검증, `enterprise/p85-ui.mjs` 허용 문서수 KPI·컬렉션 막대차트·원문 ID 선택·로그아웃 초기화.
- 보안: 매번 주체 인증·테넌트/그룹/프로젝트/등급/active 문서 상태를 검색 **전에** 확인. 원문 읽지 않고 ID/version/type/collection/clearance만, source path/hash/금지 문서 수/타조직 계정 원본 노출 0; 기존 API와 적대적 서명/SQL REVIEW_HOLD 보존.
- 아키텍처 A) 브라우저에서 전체 카탈로그 가져온 후 숨기기(원문/메타 유출 위험, 불채택), B) **서버 권한 필터링 후 제한된 메타만 전송**(선택, 네트워크0, 기존 metadata API 재사용) 비교. 실제 기업 IdP/고객 데이터는 별도.

## 실제 실행
- [정확 SHA GitHub Actions #43529432977](https://github.com/hibi89/Freelancer/actions/runs/43529432977): **7/7 jobs SUCCESS, 421 test executions PASS/0FAIL/0SKIP** (OS간 중복 포함).
- Ubuntu24.04/Windows2022 vault+loopback job: 이전107+신규 library8 = **115 PASS** 각 OS. synthetic100 harness1 각 OS, offline backup12 각 OS. Linux contracts31, pinned upstream RAG11+24 +CITEVAULT bridge36, native Linux/Windows each31.
- 신규 **실제 Chrome CDP browser job 1 PASS/0FAIL/0SKIP**: Ubuntu runner 설치 Chrome에서 HTML 실제 렌더링 → 합성 사용자 로그인 → 허용 문서/컬렉션 KPI·차트 확인 → 무권한 `foreign` 문서 미노출 → 문서 선택→검색 결과 `SEARCH_ONLY` → 390px 모바일 가로 오버플로 없음 → PNG 스크린샷 생성 → 로그아웃 후 목록 비움. 테스트 런타임 JavaScript 예외 0, 원격 HTTP 요청 0. screenshot SHA256 `dacfed126a5c6763bd6117e0645ac0b4f3cb532b1bbb573d163151570fa46a65`. Screenshot bytes는 CI 세션 안에서 검증했고 고객 UI 공식 확인용 파일/배포 아님.
- 로컬 이 검증 환경에서는 Chromium loopback 화면이 `net::ERR_BLOCKED_BY_ADMINISTRATOR`로 차단(정책 우회 안 함). **GitHub Hosted Ubuntu 실제 Chromium은 PASS**, 원격 런너 차이 명확히 구분. 브라우저 Windows 실제 렌더/사용자 물리 Win10/11 미검증.
- 정확 기능 SHA CI 브라우저는 Node22/CDP를 사용하며 외부 브라우저 npm 패키지/모델 API 다운로드 0, 단 GitHub-hosted runner 자체 운영 인프라는 사용.

## 24항 전체 설계 수용 판정
- **REQ16 (오프라인 브라우저 UI/KPI/컬렉션 차트·문서 탐색) 합성 범위 실제 Chromium 검증으로 강화**, REQ12/13/14 ACL·현역 세션/문서 폐기 메타 계약 신규 8PASS 추가. 이들 요소를 실제 고객 IdP/운영 인증이라고 주장하지 않음.
- 여전히 기업 직원 실제 신분·계정/자료 사용권 승인, authoritative PREP/SMAX signed AX package, 실제 Korean local model + weights/checksum/license/heldout, 물리 Win10/11 설치·복구·고객 Gold100·운영 및 법적 검수 없음. 원본 RAG pinned bridge는 합성, 고객 통합 아님.
- 공유 `Freelancer` 저장소 사용자에 의해 PUBLIC이며 다른 상품 브랜치/과거 커밋 노출 가능, 전체 비밀 이력 검사 미완. assistant는 공개/권한·결제·Production 변경0.
- 전체 최종설계 공식 완성률 **UNASSESSED**, 사용자 목표 85% **미인증**, `CITEVAULT AX [작업중]`, `RELEASE HOLD/SALE NO-GO`; 최종 85%를 CI 421 PASS로 임의 확정 금지.
