# AXNODE — 초경량 섹터형 단일 파일 실행 기술
`.axnode` 파일 하나에 **중앙 제어 로직, 섹터 주소표, 기능/자원 참조, 실행 순서 및 외부 자원 연결 규칙**을 표현하고 전용 런타임에서 실행하는 독자 형식. GitHub 저장소를 여러 개 만드는 아이디어가 아니라 원래 프로그램의 실행 구조를 섹터화한 하나의 파일이다.

**아키텍처 선택: A안 — ZIP/OCI 이름 바꾸기가 아닌 독자 바이트 규격.**

- 전체 [최종설계](docs/FINAL_BLUEPRINT.md) · [요구사항](REQUIREMENTS.md)
- 현재 근거: 별도 로컬 POC, Python unittest 19 PASS, 5섹터·852바이트 CSV 샘플. 원격 로딩·무료 GitHub Actions 실행·3GB 실험·Windows 고객 검증·HAE/LA 통합은 **미구현/미검증**.
- 로컬 시제품 코드/테스트 원본은 `AXNODE_A_Prototype_20261113.zip` 다운로드 산출물. **현재 이 기획 브랜치에 코드가 저장됐다고 추정하거나 CI PASS를 주장 금지**.
- 공식 최종설계 완성률 `UNASSESSED`; RELEASE HOLD; 크몽 미등록. 판매 가격은 사후 공수/실고객 검증 대상으로만 기획.

채팅 작업 순서: HANDOFF → STATUS → AGENTS → REQUIREMENTS → FINAL_BLUEPRINT → 실제 소스/테스트. 기존 상품 코드/브랜치/등록 이력 보존.
