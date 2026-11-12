# RAG Studio AX Enterprise — FINAL BLUEPRINT v1.0
**2026-11-13 KST · 100% 완성도 판정 정본 · 기업 맞춤 구축용 · 본 설계만으로 구현/판매 인정 불가**

## 0. 고객 문제·제품 경계
- 문제: 사내 정책/매뉴얼/PDF·Word·CSV 보고서가 여러 폴더에 흩어져 있어 탐색이 느리고, 단순 AI 챗봇의 근거 없는 숫자·보안상 외부 데이터 전송이 위험하다.
- 제공: 자료를 고객 허가 범위 안에서 **로컬 표준화 + 근거 검색 + 검증된 SQL 집계 + 출처 표시 + 역할별 접근 제어 + 설치/인수**로 패키지화한다.
- 고객: 5~10인 규모의 소형 제조/유통/기술 서비스팀, 매뉴얼/품질·매출·반품 규정 검색, 민감 문서를 외부 클라우드에 올리고 싶지 않은 조직.
- 아키텍처 키워드: `SMAX² → PREP/approved mapping → AX_DATA_PACKAGE_V0 → RAG Studio → BM25 + optional E5 dense → readonly SQLite → grounded response → optional local LLM → UI/ACLS/audit`.
- **중요한 경계:** 개인 로컬 셀프설치 상품 ≠ 직원 여러 명이 권한 분리해 쓰는 기업형 RAG. 기존 RAG 개발의 가중 95%가 기업형 신규 요구까지 완성했다는 뜻은 아니다.

## 1. 원본 저장소·기술 출처
| 원본 | 역할 | 사용 원칙 |
|---|---|---|
| `hibi89/RAG_STUDIO@develop` (조회 HEAD `e63e539ab8ded5834cb85672aa2142eb660d3f23`) | Node/SQLite/문서 검색/검증·대시보드 | 메인 엔진; 비공개 기업 코드·고객 파일을 Public 원본에 반영 금지 |
| `hibi89/SMAX` (Private) | 데이터 CSV/필드/비즈니스 의미 표준화, Native 데이터 패키지 | 소스 복사 금지, 버전 고정 JSON/manifest producer 계약 |
| `hibi89/prep` (Private) | 사용자/파일 전처리·매핑·품질 절차 | SMAX와 역할 중복 분석, 필수 둘 중첩 실행 강제 금지 |
| `hibi89/SOVIA_sovereign` | 보안/감사/정책 옵션 | 유료 옵션, 독립 검증 후 활성 |
| FAISS/ONNX/E5 등 모델 관련 | 검색 인프라 선택 기술 | 모델/체크섬/라이선스·실측 검증 없으면 미구현으로 표시 |

RAG Studio는 합성 데이터에서 SQLite 집계 + 문서 출처 + 브라우저/Windows CI 성과가 있고, 중앙 해총 기록상 2026-11-12 **95% 내부 엔지니어링 목표**가 보고됐다. 그러나 `develop` 브랜치가 실제로 95% 검증 코드 SHA와 동일하다고 가정하지 않는다. 95% 기록의 정확 CI SHA `0e88301059c9...`, Actions `43231121679`와 현재 분기/반영 상태를 비교할 것. 지금 기업용 신규 범위는 고객 승인·권한·설치 검증이 남아 있다.

## 2. 경쟁 설계안 비교·채택
| 안 | 초기개발/비용 | 성능·검색 | 보안/유지보수 | 결론 |
|---|---|---|---|---|
| A. 기존 RAG 서버 하나에 모든 고객 PDF 업로드 + 외부 SaaS LLM | 빠름, 종량제 비용 발생 | 높은 자연어 편의 | 정보 전송·권한·서비스 의존/비용 불확실 | 고객 허가가 있는 옵션만 |
| B. **로컬 표준화/검증 + Hybrid RAG + read-only SQL + 근거** | 초기 계약·권한 설계 필요, 기본 운영비 낮춤 가능 | 근거 검증·정확 숫자, 모델 부재 fallback | 역할 분리·감사·오프라인 운용 가능 | **주력 채택** |
| C. DB·문서·LLM·권한을 전부 1회 대형 통합 재작성 | 느림, 고정개발비 큼 | 상황에 따라 강력 | 원본 검증 손실·회귀/지원 위험 큼 | 채택 안 함 |

## 3. 고객 최종 사용자 경험 (100%)
1. 고객이 로컬 서버/허용된 Windows PC에 프로그램 설치하고 조직 관리자 계정을 생성. 데이터는 기본적으로 고객 지정 디스크에 저장, 외부 전송 0이 기본값.
2. 고객이 처리권한을 가진 PDF/DOCX/TXT/MD/CSV/지원 XLSX 파일/업무 DB를 선택한다. 원본을 직접 수정하지 않으며 문서와 자료별 출처·소유권·기밀 레벨·사용기간·정책을 확인한다.
3. PREP/SMAX²가 파일 타입·헤더·표준 필드·누락·환불/세금 의미·인코딩·부호·중복·행수를 검증하고 매핑 초안을 제시한다. 책임자가 필드 의미를 승인하기 전 `REVIEW_HOLD`.
4. 승인 후, 해시 고정 `AX_DATA_PACKAGE_V0` 또는 검증된 다음 버전 패키지를 발급한다. 문서·CSV·manifest·행 계보를 기록; 원본 ZIP을 무조건 신뢰하거나 유효하지 않은 `ACCEPTED` 표기를 승인으로 오인하지 않는다.
5. RAG가 고객별 권한으로 허용된 문서만 인덱싱한다. 기본 BM25, 선택 Dense/embedding/RRF 검색은 모델/PC 요구조건/실측 품질 통과시 활성.
6. 질문 예: '지난달 N-02 상품 매출과 반품 규정은?'. **매출은 SQLite SELECT 읽기 전용 집계**, 문서 근거는 원문 기반 검색. SQL 숫자와 문서 설명을 독립 출처로 결합한다.
7. 서로 모순되는 규정·기간/근거 없는 매출/권한 제한·검색 품질 부족이면 `ABSTAIN/REVIEW_REQUIRED`로 반환. 모델이 허위 출처를 만들지 못하게 검증한다.
8. 선택형 로컬 LLM은 '허용된 근거 요약'만 생성하며 시스템 정책/원문 역할 구분, 근거 문장 일치 검증, 메모리·모델 용량·출력 길이·비용 상한. 모델이 없으면 검색·SQL 근거 UI로 정확하게 fallback.
9. UI는 원문 PDF 페이지, DOCX 문단, TXT/MD 행, CSV 근거 행과 질문 시점 패키지 버전을 표시한다. 직원은 접근 가능한 컬렉션만 검색한다.
10. 관리자 기능: 사용자/그룹 권한, 문서 교체·폐기·재색인, 보존기간/감사·백업·복구, 업데이트/검수 결과·다운로드 데이터 경계와 권리 보고.
11. 최종 납품: 실제 고객이 승인한 자료 1세트, 고객 질문 Gold 세트, 정확성/권한 음성검증, Windows 실행 및 복구 테스트, 인수서/설치·재색인 안내. 고객 동의 없는 학습/외부 전송은 하지 않는다.

## 4. 전체 아키텍처
```text
Customer-provided sources (PDF DOCX TXT MD / CSV XLSX / approved SQL)
     │ explicit rights+consent+classification, antivirus/path/zip bounds
     ▼
PREP (owner field mapping, rule preflight) / SMAX² (typed normalization)
     │ provenance, semantic meanings, validation, plan review
     ▼
Approval Service / Reviewer identity & revocable audit
     │ approval tied to exact source+schema+version; else REVIEW_HOLD
     ▼
AX_DATA_PACKAGE_V0  [manifest, digests, row lineage, source doc map]
     ├── CSV → fixed readonly SQLite (numeric truth, SKU/orders/totals)
     └── TXT/MD + parsed PDF/DOCX → chunker, language normalization
               ↓
         IndexBuilder (BM25 base / optional ngram RRF / E5 ONNX dense)
               │ ACL materialized *before* retrieval and ranking
               ▼
     QueryRouter: typed intention + authorized scope + budget
       ├─ fixed-parameter readonly SQL route (no arbitrary LLM SQL)
       ├─ document retrieval/citation route
       └─ SQL + document combined route
               ↓
     Source verifier [row/page/paragraph hash, conflict/insufficient check]
               ↓
     Optional Local LLM [bounded grounded summary with citation verifier]
               ↓
     RAG Studio localhost/authorized LAN dashboard
       ├─ question + evidence cards + KPI/chart + source explorer
       ├─ admin roles/audit/document version & removal requests
       └─ diagnostic / backup / offline update / install report
               └─ optional SOVIA event audit (separate)
```

## 5. 기술 세부 모듈과 불변 계약
### 5.1 FileIntake + Review
- ZIP bomb, symlink/hardlink, path traversal, duplicate archive entry, oversized PDF, Unicode invalid, CSV formula injection, hidden metadata, time-of-check/use 교체 탐지.
- 파일 원본 SHA-256, 크기, inode/mtime 가능한 범위, parsing errors, source permission, reviewer identity, retention window 저장; 내용은 접근 허가된 로컬 볼륨에만.
- 원본에 판매·업무 사용권이 있다는 단순 체크박스만으로 법적 승인 확정 금지. 기업 책임자·용도·기밀범위·취소 정책 구체화.
- PREP: 입력 스키마 인식, 열 후보 의미, 사용자 매핑 draft, rejected row reports.
- SMAX²: typed normalized data, 데이터 계보, 검증된 producer contract.
- 입력 승인 전 `SMAX_REVIEW_HOLD_V1`; `AX_DATA_PACKAGE_V0`는 **서명/승인 확인 후만** RAG의 정식 지식 컬렉션으로 승격.

### 5.2 Packaging contract 예시 (설계용)
```json
{
  "contract":"ax.enterprise.package.v1",
  "source_digest":"<sha256>",
  "producer":{"name":"SMAX","contract":"SMAX_PREPROCESS_GENERIC_CSV_V1","version":"pinned"},
  "review":{"state":"REVIEW_HOLD","actor_id":null,"decision_id":null},
  "dataset":{"schema_id":"sales-v1","row_count":0,"columns":[]},
  "documents":[{"id":"doc-id","media_type":"application/pdf","sha256":"<hash>","access_class":"team-policy"}],
  "policy":{"network":"deny","retention_days":30},
  "status":"UNAPPROVED"
}
```
실제 `AX_DATA_PACKAGE_V0` production manifest schema는 소스 계약 테스트로 별도 고정한다. 이 JSON은 목표 인터페이스 설명이며 이미 배포된 공용 계약이라고 주장하면 안 된다.

### 5.3 IndexBuilder
- 기본 BM25: 언어별 정규화, 정확 토큰/문자 검색, 문서별 chunk/page/line provenance, threshold·dedup.
- n-gram RRF: 오타·띄어쓰기 보완 후보. 합성 benchmark에서 우월했다고 일반화하지 않음.
- Dense: E5 ONNX/임베딩 모델을 정확 SHA/라이선스/플랫폼/CPU/GPU 검사 후 optional load. 미존재시 BM25로 fallback.
- 인덱스 변경: 원본 수정 금지, 새 version의 shadow index 생성 후 승인/검증 성공 시 원자적 pointer swap. 검색 중 이전 인덱스와 출처 혼동 방지.
- 고객별 검색 권한: document ACL + team/department + clearance, chunk-level security. 필터는 vector DB 반환 결과 후만 걸지 말고 **검색 전후** 모두 검증한다.
- 대규모 문서에서 FTS5, FAISS 또는 pgvector는 실측 후 선택; 초기 고객 범위에서 PostgreSQL/클라우드 강제 금지.

### 5.4 SQL + Document Router
- SQL은 read-only credential/connection, parameterized exact queries, tables allowlist, max rows/time/cost, no attach/pragma writes, no direct SQL from untrusted LLM.
- 금액: KRW rounding, tax(VAT), net/gross, 환불, 취소일·주문일을 명시적으로 확인. 단순 CSV 합산을 회계 결론으로 마케팅 금지.
- 결합질의: 독립 집계 출처 `dataset_id+query_version+input_digest`와 문서 출처 `doc_id+version+page/paragraph/line`을 모두 표시하고 제어.
- 더 넓은 SQL 자유질문은 정책+쿼리 AST 파서+읽기 전용 별도 안전 샌드박스 검증 전 선택 범위 제외.

### 5.5 Response Validator / LLM
- `RETRIEVED/CONFLICT/INSUFFICIENT/FORBIDDEN/STALE` 분류, 출처 없는 문장에 대해 생성 요약 제한.
- 답변 근거 형태: `answer_summary, confidence_class, sql_evidence[], document_evidence[], missing_requirements[], status`; 정확 model confidence %를 근거 없이 만들지 않음.
- LLM 프롬프트는 고객 파일을 신뢰하지 않음: 업로드 문서 내 '지침 무시' 문구는 자료 데이터. SQL/도구 실행 지시로 승격 금지.
- 로그/모델 프롬프트 내 개인정보·비밀문구, 재현 테스트 시 synthetic substitution; 로컬 모델의 외부 호출 차단 실측.
- 동일 질문도 문서 업데이트 후 근거 버전이 바뀌면 새 답변 생성; 답변 캐시 키에 사용자/권한·dataset+document SHA 포함.

### 5.6 Access, Audit, Ops
- **개발자용 임시 localhost Bearer ≠ 기업 인증**. Enterprise는 신뢰 가능한 계정 생성·초대·비밀번호 저장·세션 회수·권한분리·최소 역할·관리자 행위 기록.
- 네트워크: 기본 localhost, 기업 LAN/서버는 TLS/방화벽/인증/업데이트/로그 회수/보안 검사를 별도 수용.
- 기록: 문서 수·해시/질의 시각·정책/접근 결과·검색 성능; 원문 본문·토큰은 기본 기록하지 않음.
- 삭제: 고객 요청 시 원문/파생 텍스트/임베딩/SQLite/캐시/backup retention·감사 필수 보존의 경계를 구분; 즉각 전부 삭제를 무조건 보장하지 않음.
- Windows 서비스/최소 사용자 설치기/비정상 종료 후 재시작/오프라인 보안 업데이트·모델 배포 권리를 검토한다.

## 6. 5개 사용 유형
1. **Document RAG:** 단일 PDF/DOCX/TXT/MD 검색과 원문 근거 클릭.
2. **Knowledge Base RAG:** 부서별 정책·FAQ·내규 컬렉션과 버전·상충 규정 경고.
3. **Multi-document RAG:** 여러 문서의 비교와 출처별 날짜/페이지·상태 표시.
4. **Conversational RAG:** 지원된 후속 질문 범위, 원문과 유효기간/권한 변경 시 맥락 무효화.
5. **SQL+Document RAG:** 검증된 정형 KPI와 텍스트 정책/근거를 결합. **차별화 가능성의 핵심.**

5개 유형 모두 동일 모델 5개가 아니라 **공통 ingest/index/search/DB를 용도별로 조합**한다. 전체 범용 Agent/임의 SQL/고객 문서로 모델 재학습은 필수 범위 아니다.

## 7. 고객 수준의 정확성·성능·한계
- 실제 고객 Gold 질문 최소 100문항(정형/문서/혼합·부정/상충/권한 없는 항목을 균형 포함), 정답/근거 원본·판정 기준 고객 서명.
- 각 케이스마다 retrieval Recall@K, exact SQL numeric, citation precision, refusal/abstain, role leakage, answer groundedness, avg/p95 latency/memory를 측정.
- 목표치는 사전 정의하고 실 측정/환경에 따라 계약(예시: 승인된 정확 집계 오류 0; 비인가 문서 검색 유출 0; 실패시 안전 보류 100%; 정확한 문서 검색 목표는 고객 Gold 합의).
- scanned PDF, 복잡 표/수식, 암호화 파일, 실시간 ERP 조회, 모델 언어/도메인 성능은 계약 전 샘플로 별도 검증, 디폴트 지원 보장 아님.

## 8. 범위 외 및 법적 제한
- 원본 문서 저작권/사용권, 기업 내부 비공개 정보, 데이터 처리 위탁/전송, 모델 상업 재배포 권리 필수 확인.
- 고객 내부 보안 등급/규정·기밀문서 외부 AI 업로드, 제3자 지식 데이터 모델 훈련 허락 없이 수행 금지.
- 고객 지원 범위를 벗어난 365일 SLA, 무제한 수정, 임의 고객 ERP CRUD, 회계·법률·의료 전문가의 확정 판단 등은 기본 상품에 포함되지 않음.
- 비용이 드는 모델/GPU/서버/OAuth/스토리지/자동 백업은 고객 동의/견적 분리.
- 최종 100%는 [수용표](ACCEPTANCE_AND_ROADMAP.md) + 상용 권한/라이선스/실기기/기업 사용자 검증까지 완료해야만 인정한다.
