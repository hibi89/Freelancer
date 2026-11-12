> **[OWNER-FINAL-BLUEPRINT-100 | 2026-11-13 KST | 사용자 확정·전체 저장소 최우선]** 제품 공식 **최종완성률은 사용자 확정 최종설계도 전체 100%**를 분모로 한다. 총괄·작업자는 임의로 설계를 축소하거나, 해커톤용 MVP·합성 테스트·CI PASS·85/95% 내부 마일스톤을 최종완성률로 혼용할 수 없다. 최종설계 요구사항 ID→코드→정확 SHA 실제 검증→미구현/미검증 및 사용자 승인 가중치를 추적해 계산한다. 근거·가중치가 미비하면 **최종설계 기준 UNASSESSED(재산정 대기)**로 표시하고 종전 수치는 **과거 내부 마일스톤**으로 보존한다. 크몽 관련 완성률은 해총 `kmong-productization` 원장에 동기화한다. [작업중]/등록완료/RELEASE HOLD 등 기존 별도 상태는 보존한다. 상충하는 구형 진척률 산정 지시보다 우선. [공통 전체 규칙](https://github.com/hibi89/hackathon-command-center-2026/blob/kmong-productization/docs/strategy/FINAL_BLUEPRINT_COMPLETION_STANDARD_20261113.md). 정책 커밋은 코드 수정·성공 테스트·제품 출시·재산정 완료를 의미하지 않는다.

# AGENTS — 5대 크몽 상품 설계 저장소
- GitHub 비공개 `hibi89/Freelancer`의 `main`은 5개 상품 인덱스이며 `product/*` 5개 브랜치가 각 최종설계·수용 기준의 소유자다. 실제 제품 소스/CI/배포는 해당 독립 원본 GitHub 저장소에 존재한다.
- 새 채팅 또는 사용자 `ㄱ`: 해당 상품 branch의 `HANDOFF.md → STATUS.md → AGENTS.md → REQUIREMENTS.md → docs/FINAL_BLUEPRINT.md → 원본 제품 최신 HANDOFF/STATUS/AGENTS/REQUIREMENTS/코드` 순으로 확인한다.
- 제품 최종완성률 `50→70→85→95→100`은 **문서에 확정한 전체 제품 설계의 검증 단계**. 설계 파일만 작성하고 신규 코드를 구현하지 않은 경우 진행률을 임의로 부여하지 않는다.
- 아키텍처는 최소 2개 안을 성능·비용·유지보수·법적 권리·데이터 보안으로 비교해 채택 근거를 기록한다.
- 원본 코드/실 고객 정보/비밀번호·API 키·비공개 SMAX/PREP·회사 자료를 이 저장소/외부 AI/Public Repo로 무단 복사/업로드하지 않는다.
- 계정, 외부 통신, 유료 비용, CI 분 사용, 보안/권한, 원본 변경, 신규 배포/도메인/사업자/계약 범위는 사전 승인 대상. AI의 추정/고객 실증/CI PASS/미검증을 분리한다.
- 사용자가 제품 실제 개발을 지시할 때 해총 `hibi89/hackathon-command-center-2026@kmong-productization`의 해당 제품 `[작업중]` 지침 확인 후 정확 SHA·목표/검증 기준을 기록한다. 목표 미달 표시 임의 삭제 금지.
- 문서·기능 변경 후 `STATUS.md`, `HANDOFF.md` 10항과 Git SHA·CI PASS/FAIL/SKIP·미검증 및 복구 방법 최신화. 의미 없는 CI·재배포·빈 커밋·force push 금지.
- 고객에게는 지원된 기능·언어/파일·페이지·수정횟수·검수 기준·모델/브라우저/서버 비용·라이선스/영수증 정책을 명시. 광고 문구에 미구현 Graphify/agent-browser/Auto Ontology 통합을 구현 완료처럼 표기하지 않는다.
- 원본 `Freelancer` 업워크 자료는 현행 트리에서만 제거, 과거 Git 이력으로 복구 가능. 다른 3개 제품 브랜치의 기존 작업/기록 유지.
