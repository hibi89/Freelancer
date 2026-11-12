> **[KMONG_WORK_TARGET_GATE_20261112 | 사용자 최신 확정 | 필수 작업 규칙]** 이 저장소에서 크몽 상품·육성 후보를 작업하는 모든 AI 담당자는 새 채팅·`ㄱ` 시작 시 이 문구를 읽고 적용한다.
> - 실제 개발/수정/테스트 착수 즉시 [해총 크몽 최종완성률·후보 상태표](https://github.com/hibi89/hackathon-command-center-2026/blob/kmong-productization/docs/audits/KMONG_16_CURRENT_20261111.md)의 **해당 상품명 옆에 `**[작업중]**`을 표시하고 GitHub 커밋**한다. 확정 단계 목표(예: 95%)와 검증 기준을 제품 STATUS/HANDOFF에 남긴다.
> - **목표 완성률 달성 전에는 [작업중]을 삭제하지 않는다.** 일시중단·종료·보류·다른 제품 전환·담당 채팅 변경도 삭제 사유가 아니다. 예전 '전환·중단 시 삭제' 지시는 폐기한다.
> - **검증된 목표치에 도달한 뒤에만** 기능 SHA·PASS/FAIL/SKIP·미검증을 기록하고 자기 표시를 제거·커밋한다. 목표 하향/변경으로 표식 제거 시 사용자 명시 승인 필요. 다른 담당자 표시·기존 수치·RELEASE HOLD 보존.
> - 표식은 목표 미달 상태를 의미하며 **실시간 실행 증명은 아니다**. 허브 최신 HEAD 확인 후 안전하게 반영, 실패 시 `KMONG_HUB_SYNC_PENDING` 기록. 자동 동기화 없음. 크몽 외 작업에는 표시 불필요.

> **2026-10-28 해총 전 저장소 최상위 공통 운영 공지 (소유자 승인):** [전 프로젝트 최종 개발 가속·검증 정본](https://github.com/hibi89/hackathon-command-center-2026/blob/main/docs/DEV_ACCELERATION_AND_VERIFICATION_20261028.md)을 먼저 적용한다. 현재 활성 개발은 **KIC(+DL)·PayPal·UGREEN·LA의 4개 슬롯**만이며, 본 프로젝트는 **일시 대기(폐기 아님)**다. 재개 지시 전 `ㄱ`만으로 개발·CI·배포하지 않는다. 활성 총괄의 일반 구현은 GPT-6 Instant, 최초 설계·고위험 쟁점·해총 검수는 높은 추론. 파일별 커밋/조회, 중복 문서 갱신과 무의미한 CI 반복을 줄이고 실제 기능/테스트 실행 PASS·FAIL·SKIP와 SHA를 우선 보고한다. 기존 설계·안전·권한/외부 서비스·개인정보 보호 및 소유자 승인 규칙 유지. 운영 공지이지 제품 변경/완료 선언이 아니다.

# AGENTS — operating rules

## Mission
Earn verified money from **ethical AI-assisted digital work**, minimize unsolicited calls/meetings and travel, preserve development time. Preferred jobs: Python, pandas, Excel/Sheets, KPI reporting, n8n, REST APIs, SQL, testing, document processing, small automation contracts.

## Evidence and truth
- State **verified / owner-reported / planned / unknown** separately.
- Never claim paid client experience, delivered commercial products, completed training, hackathon awards, verified model accuracy or production deployments without proof.
- A customer's specification outranks AI convenience; if external AI tools are restricted, do not use them. Ask permission as needed and disclose usage when appropriate.
- Check feasibility, task hours, cost, fees, client history, budget and terms before recommending an application.
- Use secure handling of data: do not paste client secrets, private assets or personal data into AI tools without permission; create sanitized test data.
- No fake accounts, fake reviews, mass spam applications, false qualifications, or circumventing platform restrictions.
- **Never** submit a job proposal, contact clients, accept a contract, authorize paid Connects, buy subscriptions, charge APIs, or publish a public portfolio without direct user authorization. Drafts and read-only research are allowed.
- No arbitrary force push, deletion, repo/publicity changes or cross-repo work without a clear need and authorization.

## Decision order
1. A realistically payable task > a decorative portfolio addition.
2. Jobs allowing approved AI tools, remote and async text communication.
3. Quick small delivery if math works; prioritize 1st completed, paid client.
4. Build case-study demos only in support of identifiable applications.
5. Use reusable modules from other repos within rights and security boundaries.

## Continuity
Make changes that include STATUS and HANDOFF updates as appropriate, document exact source links and next owner's action. GitHub is the durable source, ChatGPT memory is not the authoritative log.

## Privacy
Avoid storing name, home address, DOB, phone, official ID, banking, screenshots of verified accounts, token/API keys or sensitive client files in this repo. Private means not public; it is **not** a secure vault.
