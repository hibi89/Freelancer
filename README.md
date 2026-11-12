# CITEVAULT AX — RAG Studio + SMAX²/PREP 기업 AI 지식검색

**상품명: CITEVAULT AX · 근거형 기업 AI 지식·데이터 검색 · 기술: RAG Studio + SMAX²/PREP + SQL/BM25**
**크몽 기업 맞춤형 · 2026-11-13 KST · Private · 설계 전용 · RELEASE HOLD**

- **완성 목표:** 고객 PDF/DOCX/TXT/MD 및 승인된 Excel/CSV/업무 DB를 로컬에서 **SMAX²/PREP로 정형화→RAG Studio로 검색·정확한 SQL 집계→문서 원문 근거 표시→필요 시 로컬 LLM으로 답변**한다. 근거가 없거나 충돌하면 보류한다. 고객/역할별 접근 통제와 설치·복구까지 납품.
- **기술 조합:** `SMAX² (데이터 표준화)` + `PREP (사용자 매핑/품질)` + `AX_DATA_PACKAGE_V0 (검증/권리 패키지)` + `RAG Studio Node.js + SQLite + BM25/RRF + 선택 Dense/E5 ONNX` + `PDF.js/Mammoth` + `승인형 로컬 LLM(선택)` + `SOVIA(선택적 감사)`.
- **소스 정본:** `hibi89/RAG_STUDIO`, Private `hibi89/SMAX`, Private `hibi89/prep`. 이 상품 브랜치는 코드 복제/전사 고객자료가 아닌 상업용 요구·아키텍처·검증 기준을 관리한다.
- **가격 가설:** BASIC 1,490,000원 / STANDARD **2,990,000원** / PREMIUM 5,990,000원, 계정·모델/서버·자료량 별도.
- **주의:** 기존 RAG Studio의 셀프설치 개인용 계획(149,000원대)과 이 상품의 **기업 맞춤 구축/설치·검수 서비스**는 별도 상품이며 동일 범위가 아니다. 현재 사용권 승인·실 고객 권한분리·실 Windows 설치 미검증. `RELEASE HOLD`.
- 문서: [100% 최종 설계](docs/FINAL_BLUEPRINT.md), [모든 기술](docs/TECHNOLOGY_MAP.md), [50→100 수용](docs/ACCEPTANCE_AND_ROADMAP.md), [패키지/보안](docs/COMMERCIAL_AND_SECURITY.md).
