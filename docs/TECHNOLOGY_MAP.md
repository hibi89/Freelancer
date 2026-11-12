# CITEVAULT AX — RAG Studio 기업상품 기술 스택 100% 맵

> **상품명: CITEVAULT AX** · 근거형 기업 AI 지식·데이터 검색. 원래 제품명·저장소는 유지.

| 계층 | 기술/프로젝트 | 책임 | 구현·검증 구분 |
|---|---|---|---|
| UI/서버 | Node.js 22 ESM, localhost HTTP | 검색·대시보드/API | 기존 구현 |
| 데이터 SQLite | Node 내장 SQLite/read-only fixed SQL | SKU·매출·주문 합산 | 제한 합성 샘플 |
| PDF parser | pdfjs-dist 6.x | PDF 텍스트/페이지 | 2MiB·미리보기 제한 |
| DOCX parser | mammoth 1.x | 문단 텍스트 | 페이지 보증 불가 |
| Plaintext | UTF-8 TXT/Markdown | 행 기반 원문 인용 | 구현 |
| CSV/Excel intake | PREP, SMAX², 검증된 CSV parser | 열 의미/스키마/표준화 | 교차 상용 인가 미검증 |
| Package | AX_DATA_PACKAGE_V0, SHA256 | 소스/manifest/승인/계보 | 합성 패키지 구현 |
| Keyword | BM25 | 문서 검색 | 구현 |
| Lexical fusion | n-gram, RRF | 오타/한영 보완 실험 | 선택형 |
| Semantic vector | E5 ONNX/로컬 embedding | 검색 의미 유사도 | 실모델/실고객 성능 별도 |
| Vector storage | lightweight dense, FAISS/pgvector 검토 | ANN 검색/대용량 | FAISS 완성이라고 주장 금지 |
| Query routing | fixed intents + readonly SQL | 수치 정확성과 문서 결과 분리 | 제한 문장 지원 |
| Citation | doc SHA/line/PDF page/DOCX paragraph | 출처 재확인 | 합성 검증 |
| Grounded answer | optional local LLM+validator | 근거 기반 자연어 | 범용 LLM 기업용 미완 |
| Security | localhost bearer, ACL/identity future | 파일·세션 접근 제어 | 기업 IAM 신규 |
| Audit | SOVIA option + event ledger | 정책 추적·보관/삭제 | 옵션/교차 검증 필요 |
| Windows | CMD, native picker, portable ZIP | 로컬 파일 선택·실행 | 고객 PC/정식 installer 미검증 |
| QA | Node built-in test, gold100/negative20/heldout24, Playwright/Chrome/Edge | 정확·보안·브라우저 | 내부 합성 CI 존재 |
| DevOps | GitHub Actions, manifest pinned deps/license SBOM | 코드 provenance/배포 | 기업 배포 출고 필요 |

## 엔진 간 책임 경계
- **SMAX²**: 입력 데이터를 정규화하는 producer. 재무/매출 의미 확정은 사용자 승인이 필수.
- **PREP**: 별도 입력·매핑·전처리 UX 및 품질 사전검사. SMAX 기능과 중복되는 부분은 인터페이스로만 연동하고 이중 변환 금지.
- **RAG Studio**: 승인된 패키지 안의 정형 SQL/문서 검색·출처·대시보드 consumer.
- **SOVIA**: 보안 정책과 감사 선택형. RAG 답변 품질 엔진을 대신하지 않음.
- **HAE/LA**: 이후 직원의 승인된 보고서 자동 출력/전송을 위해 연계할 수 있지만 이 기업 RAG 초기 범위에 자동 포함하지 않는다.

## 회사별 설치 대안
A. 개인 PC single-user localhost(저렴, 유지보수 간단; 권한분리 약함) / B. 고객 내부 서버 Windows 또는 Linux + 직원 계정+TLS(권한/운영 필요; 기업형 채택) / C. 멀티테넌트 SaaS(고객정보·공급자 보안·고정 운영비 증가; 초기 배제).
대상 업체의 상시 운영 서버가 없으면 A를 표준형 축소 상품으로 판매하거나 B 장비/운영 비용을 추가 견적해야 한다.

## 모델 비용·권리
- 기본 BM25 + SQLite는 유료 AI API가 없어도 사용 가능; 업로드/대역폭/백업과 PC 비용은 남는다.
- 선택 Dense/LLM은 모델의 라이선스·정확 체크섬·모델 파일 획득 방식·GPU/RAM·CPU latency를 실제 검증해야 한다.
- 외부 LLM 옵션은 고객 동의한 출처만 송신, 토큰 상한/로그 마스킹, 월 예산 hard cap을 수용해야 가능.
- 공개 `RAG_STUDIO` 레포에 비공개 SMAX/PREP 구현·실 고객 문서·모델 토큰을 복제하지 않는다.
