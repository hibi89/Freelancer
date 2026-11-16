> **[OWNER-DEV-EXECUTION-V2 | ACTIVE]** [2026-11-16 사용자 확정 최신 실행·복원 정본](https://github.com/hibi89/hackathon-command-center-2026/blob/kmong-productization/docs/strategy/OWNER_DEV_EXECUTION_CANONICAL_20261116.md): **웹 GPT-6 Sol High 최초 전체 설계/Instant 작업큐 → 웹 GPT-6 Sol Instant BE/FE 구현 후보100%까지 묶음 코딩 → 최종 전체 CI·수정(고위험 최소검사 즉시) → Codex GPT-6.1 Sol Max 기술·Astra Max 디자인 독립검수 → 웹 Sol High 최종 인수 → 형 승인 후 Codex Luna Extra High 크몽 등록.** 구형 '4개 작업슬롯만', High 단독 코딩, 매 작업 전체 CI, 중간 검수·디자인 순서는 효력상 대체; 최종설계·보안/원본/외부비용/법적권리/상품 HOLD는 유지. 이 정책 기록 자체는 제품 재개·CI·출시 허가가 아니다. **새 채팅은 역할/브랜치 HEAD와 최신 AGENTS를 우선 확인하고 HANDOFF→STATUS→REQUIREMENTS→최종설계→실코드·큐 순으로 대조**한다. HANDOFF 오래된 지시가 정책을 덮어쓰지 못하며 `ㄱ`은 해당 제품만 재개한다. 구현률/공식 검증률 구분, 허위 1%p 금지.

> **[OWNER-FINAL-BLUEPRINT-100 | 2026-11-13 KST · 사용자 확정]** 최종완성률은 **사용자 최종설계도 전체 100%**를 기준으로만 계산한다. AI 총괄/담당자의 임의 축소·가중치 조정·MVP/합성 CI/내부 기술 85·95%를 최종완성률로 전용 금지. REQ별 구현 경로·정확 SHA 실행 검증·미구현·미검증·사용자 승인 가중치 추적표를 갖춰 산정하고, 미비하면 공식 `UNASSESSED(재산정 대기)`. 기존 내부 점수/마커·등록이력·판매 HOLD 보존. 크몽 상품 원장은 해총 `kmong-productization`에 증빙과 함께 최신화. [공통 정본](https://github.com/hibi89/hackathon-command-center-2026/blob/kmong-productization/docs/strategy/FINAL_BLUEPRINT_COMPLETION_STANDARD_20261113.md). 문서 갱신 자체는 제품 완료나 배포가 아님.

# AGENTS — 3대 크몽 상품 설계 저장소
- GitHub 비공개 저장소 `hibi89/Freelancer` 의 `main`은 전체 색인, `product/*` 3개 브랜치는 각 상품 설계의 소유자다. 실제 제품 구현/테스트/배포의 정본은 독립 원본 저장소다.
- 사용자 `ㄱ` 지시 시 담당 브랜치의 `HANDOFF.md → STATUS.md → AGENTS.md → REQUIREMENTS.md → docs/FINAL_BLUEPRINT.md → 원본 제품의 최신 문서/코드`를 확인하고 다음 안전한 단위를 수행한다.
- 제품의 100%는 확정된 상세 설계의 수용 기준이 전부 검증됐을 때만 인정한다. 50/70/85/95/100은 내부 단계이며 매출·출시·완성 보장이 아니다.
- 착수 전 두 개 이상 아키텍처를 성능·비용·유지보수·권리·보안으로 비교하고 채택 이유를 문서화한다. 설계 승인 없는 제품 코드 변경·외부 시스템 연동은 수행하지 않는다.
- 원본 소스/데이터·브랜치·CI·환경변수·고객자료·비공개 SMAX 전략을 보호한다. 고객 계정·개인정보·토큰·원본 기밀은 이 저장소에도 저장하지 않는다.
- 위험/돈/외부 송신/계정 권한/프로덕션/고객 계약·개인 자료는 사용자 승인 필요. 실행 관찰 결과와 문서상의 목표/추정/미검증을 구분한다.
- 제품 구현 시작 시 해총 `hibi89/hackathon-command-center-2026@kmong-productization` 작업 표시 규칙을 확인하고, 목표 미달의 `[작업중]` 임의 제거 금지. 단순 설계 갱신은 구현 완료율 올리지 않는다.
- 변경 후 STATUS/HANDOFF 10항, 검증 SHA, PASS/FAIL/SKIP, RELESE HOLD/미적용을 최신화한다. 불필요한 커밋·강제 push·빈 커밋·원본 파괴 금지.
- 고객 맞춤 판매 견적에는 포함/제외/수정횟수/인수테스트/운영비/라이선스/영수증 조건을 명시한다. 업계 시세·차별화·가격은 실측 없는 가설로 표시한다.
