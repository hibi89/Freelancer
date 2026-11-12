# PROOFQA AX — AI 개발품 납품 검수 서비스
**2026-11-13 KST · 작업명 확정(대외 상표 확인 전 내부명) · 설계 저장소 · RELEASE HOLD**

> 해총의 「AI 개발품 납품 검수 서비스」에 대응하는 독립 상품 브랜치다. 기존 `ai-code-checker` **기반 엔진** + **Graphify** 코드/SQL 관계 그래프 + **vercel-labs/agent-browser** 허가된 실제 웹 행동 검증 + **Cloudflare security-audit-skill**의 검증 중심 보안 감사 방법론을 **조합하는 목표**다. **실제 통합 개발은 아직 수행하지 않았다.**

**최종 판매물:** AI 제작 웹앱/자동화 소프트웨어/소스 저장소의 검수 결과를 기능/구조/보안/납품 적합성으로 나누어, 재현 가능한 증거(파일·줄, 실행 환경·SHA, Playwright/agent-browser 행동·스크린샷, 재현 절차), 확인된 결함·미검증과 고객 승인·수정 우선순위가 포함된 한국어 HTML/PDF/JSON/ZIP 납품 패키지.

- 소스 정본: [ai-code-checker](https://github.com/hibi89/ai-code-checker), 실제품 개발 브랜치 `feature/retail-private-candidate-20261112`; 이 브랜치는 기획/검수·상용 기준만 소유. 외부 오픈소스 소스 자동 import나 무단 배포 없음.
- 상세: [최종 100% 설계](docs/FINAL_BLUEPRINT.md) / [전체 기술](docs/TECHNOLOGY_MAP.md) / [50·70·85·95·100 수용](docs/ACCEPTANCE_AND_ROADMAP.md) / [검수·보안 위협모델](docs/THREAT_MODEL_AND_TESTS.md) / [가격·권리](docs/COMMERCIAL_AND_SECURITY.md).
- 가격표는 **판매 실적 없는 견적 가설**이며 수주 전 작업 시간·프로젝트 크기·고객 지원 범위로 다시 산정한다.
- 안전: 의뢰인 프로젝트 무단 실행/권한 없는 침투/취약점 확정·보안인증 주장 금지. 안전한 샌드박스 없는 경우 `NEEDS_VALIDATION`로 보고한다.
