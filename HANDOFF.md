# HANDOFF — AX ZERO 전용 브랜치 생성·최종설계 확정 (2026-11-17 KST)

1. **목표·확정 요구:** 최초 5단계(AI 문제해결→공통규칙 추출→소형 프로그램 생성→합성 반복검증→AI 없는 모듈 승격)와 SKILL.md/판단·변경 대응·호출 제거율·AXNODE 선택 연계를 모두 담은 독립 로컬 엔진; `REQ-01~36` 전수.
2. **이번 완료:** `product/ax-zero-local` 신규 분기; README/AGENTS/REQUIREMENTS/STATUS/HANDOFF/최종설계·ADR·KPI·보안·연동·런북·매트릭스·P1/P2 큐·phase gates 문서. 제품 구현/동작 개발 아님.
3. **검증:** GitHub 문서 쓰기·원격 readback·REQ/큐/분모 정합성 확인 대상. 제품 소스·CI·로컬 Windows/모델/Qwen·브라우저·AI 절감 벤치마크는 `NOT_RUN`, 72%는 가상 예시.
4. **상태:** 구현 0/36 REQ, P1 0/18 task DONE, P2 0/9 P2 RUN; 공식 가중치 검증률 UNASSESSED, RELEASE HOLD, 상용 미등록·Production 미적용.
5. **위험·장애 대안:** LLM 생성 코드 직접 실행 금지; sandbox 없으면 HOLD. AXNODE 미완성/외부 모델 과금/고객 자료 미제공 시 Python IR·합성 데이터·offline read-only 먼저 진행. 원본 수정·브랜치 덮어쓰기 금지.
6. **Repo·branch·SHA:** `hibi89/Freelancer@product/ax-zero-local`; 출발 `main@4982ce06cc0e74cbb45fc161b03051b8e0fe2db7`; **최신 HEAD는 GitHub branch live readback 기준**. AXNODE `product/axnode-sector-runtime@fa30a28aa61c166b519ddb2663c3620537767f4e` 원본 불변.
7. **배포·환경:** Windows 11/Python 3.11/GTX1050Ti/16GB 로컬 우선, cloud/Vercel/Production 미적용, 외부 모델 기본 OFF, 실 PC 검증 NOT_RUN.
8. **원본·백업·인증:** Git branch commit history로 문서 복구. 고객 원본·개인정보·토큰/.env/모델 가중치 전송 0. MLA/EAI/기존 Freelancer main·타 브랜치 변경 없음.
9. **다음 작업:** Instant 첫 READY `AXZ-001`(trace), `AXZ-003`(skill importer), `AXZ-006`(policy/isolation) 동시 진행 가능한 경로로 묶기; P1 완성 후 High SHA gate→P2 독립 검증→P3 감사→P4 인수→사용자 별도 GO.
10. **일시·범위:** 2026-11-17 KST. 이번 단계는 설계/큐 원격 기록만. 최신 SHA·문서 정확 일치는 커밋 및 GitHub 원격 readback으로 확인하고 작업 결과에 보고. GitHub/OS/CI/기능 성공 주장 금지.

**재개 명령:** 이 AX ZERO 고정 채팅의 `ㄱ`/`ㄱㄱ`은 repo HEAD/정본 확인 후 READY 실제 코드 구현. 해총 중앙 자동화 채팅의 단독 `ㄱ` 업무를 바꾸지 않음.
