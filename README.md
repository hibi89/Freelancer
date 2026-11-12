# AZENTFLOW AX — HAE + Lightning Azent 기업 업무 자동화

**공식 내부 상품명: AZENTFLOW AX | 고객 설명: 승인형 기업 업무 자동화 | 핵심 조합: HAE + Lightning Azent + DBVORA**
**판매 채널: 크몽 · 설계 기준 2026-11-13 KST · Private · RELEASE HOLD**

- **최종 목표:** 비개발자가 한국어로 업무를 설명하고 데이터/연동 대상을 선택하면 HAE가 실행 가능한 계획과 위험·비용을 제시한다. 고객이 승인하면 **Lightning Azent(LA)**가 실행·재시도·중복 방지·복구·감사를 담당한다. 지원 업무 DB는 **SQLite** 우선, DB 구조·백업 관제는 별도 **DBVORA**가 책임진다.
- **기술 조합:** `HAE (UI + planner + policy + approval)` + `Lightning Azent (typed IR + deterministic runner)` + `SQLite runtime/business DB` + `DBVORA (inventory/backup/restore)` + `SOVIA(선택적 감사)` + `허가된 API OAuth 커넥터`.
- **판매 표준형 타당가 가설:** 1,990,000원. 기본 990,000원, 고급 3,990,000원. 외부 서비스 월 비용·특수 시스템 연동 별도.
- **중요:** 원본 개발은 `hibi89/HAE@feature/axflow-mvp`, LA는 같은 저장소 `feature/lightning-azent`, DBVORA는 별도 `hibi89/DBVORA`이다. 이 브랜치는 **설계/납품/진척 문서**만 보유한다.
- **정본:** [최종설계](docs/FINAL_BLUEPRINT.md) → [기술 전부](docs/TECHNOLOGY_MAP.md) → [수용·로드맵](docs/ACCEPTANCE_AND_ROADMAP.md) → [상품·보안](docs/COMMERCIAL_AND_SECURITY.md).
- **현재 사실:** HAE 내부 85% 잠정 기록이나 Python 원본 전체 CI에 패키지 parity 2 FAIL, 실 Google OAuth·고객 인수 미검증. LA 별도 엔진도 완전 상용 서비스가 아니다. `RELEASE HOLD`.
