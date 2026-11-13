# Freelancer 5종 크몽 상품 통합 색인 — 2026-11-13 KST
**Private `hibi89/Freelancer`; 브랜치 5개 생성·원격 파일 SHA/Tree 확인**

| 제품 | branch | 검증된 최종 HEAD | BLUEPRINT 본문 | Git Tree blob |
|---|---|---|---:|---:|
| **AZENTFLOW AX** — HAE + Lightning Azent | `product/hae-la-automation` | `a578aee2300ae053bafe5cdaf1dd8e23385ff47b` | 8,053자 | 10 |
| **CITEVAULT AX** — RAG + SMAX²/PREP | `product/rag-enterprise-knowledge` | `acf4936670bf1205f648d0dff5ca7e48b62fa83a` | 9,229자 | 10 |
| **SITECRAFT AX** — REA + Fable/Astra | `product/rea-website-rebuild` | `6e2346c3b9d50dea1bde8d5ecb47b47f1567f774` | 10,693자 | 10 |
| **PROOFQA AX** | `product/proofqa-ax-delivery-audit` | `54b718f5d5520fae912d1fcc2e70a87ebd8f173c` | **10,490자** | **12** |
| **ONTOINSIGHT AX** | `product/ontoinsight-ax-data-analytics` | `afda6eac0802d50cbcd44eb0b99d3daeffbf0922` | **11,805자** | **12** |

## 신규 2개와 해총 원안 연결
- 원안: [해총 KMONG_PRODUCTIZATION.md — GitHub 기술 협업 신규 상품화 2건](https://github.com/hibi89/hackathon-command-center-2026/blob/kmong-productization/KMONG_PRODUCTIZATION.md).
- PROOFQA: Code Checker 원본 `hibi89/ai-code-checker@feature/retail-private-candidate-20261112` (조회 SHA `64744eebd109...`), [Graphify](https://github.com/Graphify-Labs/graphify), [agent-browser](https://github.com/vercel-labs/agent-browser), [Cloudflare security-audit-skill](https://github.com/cloudflare/security-audit-skill).
- ONTOINSIGHT: AutoML 원본 `hibi89/AI_AutoML_Analyst@feature/kmong-p6e50-owner-delivery-20261112` (조회 SHA `d56b1b48...`), [NVIDIA Auto Ontology](https://github.com/NVIDIA/auto-ontology) **아이디어/메타데이터 계약만**, optional Private `hibi89/SMAX`/`hibi89/prep`.
- 두 상품 각각 `README.md`, `REQUIREMENTS.md`, `AGENTS.md`, `STATUS.md`, `HANDOFF.md`, `docs/FINAL_BLUEPRINT.md`, `docs/TECHNOLOGY_MAP.md`, `docs/ACCEPTANCE_AND_ROADMAP.md`, `docs/COMMERCIAL_AND_SECURITY.md`, `docs/REPOSITORY_RECOVERY.md` 및 별도 `docs/THREAT_MODEL_AND_TESTS.md` 또는 `docs/DATA_CONTRACT_AND_TESTS.md`.
- 기존 제품 3개는 동일 SHA·파일 및 100% 설계 기준 그대로 둠.

## 실 검증과 미검증 구분
- 새 branch Git Trees(정확 SHA) 각 12 blob, `FINAL_BLUEPRINT.md` 원격 내용과 branch head 확인, old Upwork/INCOME/LOOM/APPLICATION 파일 각 0개.
- 새 PRODUCT 브랜치 문서 변경은 기존 Code Checker·AutoML 코드/데이터/배포를 변경하지 않음. 실제 신규 adapter/Excel/온톨로지/브라우저·샌드박스 구현/통합 테스트/고객 수용·상용 판매는 모두 **NOT_RUN/UNASSESSED**.
- 과거 원본 Upwork 기록은 Git history SHA `d47239f961fc895592147c2afa969ecf64f2bd00`로 조회/선택적 복구 가능; 영구 삭제 미실시.
- 상용 가격/상품명/고객 비용·수요/OSS_NOTICE/법적 데이터 처리/세금 증빙 미검증, **RELEASE HOLD**. 새 기획 진척률을 기존 제품 퍼센트에서 복사하지 않는다.

## 3개 기존 기업형 상품의 공식 내부 브랜드 (2026-11-13 KST)
- **AZENTFLOW AX**: HAE + Lightning Azent + DBVORA, `product/hae-la-automation/docs/BRAND_POSITIONING.md` (브랜치 내 실제 경로 참조).
- **CITEVAULT AX**: RAG Studio + SMAX²/PREP, `product/rag-enterprise-knowledge/docs/BRAND_POSITIONING.md`.
- **SITECRAFT AX**: REA_WEB + Fable 5.1 + Astra P4 + REA Pro, `product/rea-website-rebuild/docs/BRAND_POSITIONING.md`.
- 새 명칭은 내부에서 사용하며 상표 검색/서비스명 충돌·도메인 확보 미검증. 명칭 변경은 소프트웨어 개발률·출시율에 영향을 주지 않는다. 기존 `product/*` 브랜치는 모두 유지한다.

## 2026-11-13 추가 — 개인용 로컬 AI 신상품 (기존 5개 상품 불변)

기존 AZENTFLOW/CITEVAULT/SITECRAFT/PROOFQA/ONTOINSIGHT 5개 독립 브랜치와 SHA·최종설계는 **수정하지 않음**. 기존 헤더의 '5종'은 과거 기업형 카탈로그 구분이다. 다음 소비자형 2개 개발 브랜치는 별도로 추가되었다.

| 상품 | 개발 브랜치 | 확인 HEAD | 공식 최종완성률 | 상용/크몽 |
|---|---|---|---|---|
| ECHOHOME + PAWTALK (가족 음성/반려동물 캐릭터 대화 2 SKU) | product/echohome-pawtalk-local-ai | 603be91d278f4cef1e8e0fe0994bfdb21ca23740 | UNASSESSED (기획만) | HOLD/미등록 |
| **MYRADIO AI (개인 AI 라디오)** | **product/myradio-ai-dj** | **5885b2b22f8e4ee7692c08ba96ddd536d2c82e26** | **UNASSESSED** (Python 7 PASS 초기 오프라인 시제품) | **HOLD/미등록** |

MYRADIO 최종설계 정본: https://github.com/hibi89/Freelancer/blob/product/myradio-ai-dj/docs/FINAL_BLUEPRINT.md
MYRADIO 구현: 오프라인 WAV 카탈로그 권한필터/장르·기분 선곡/5개 DJ **대사 스타일**/Windows 기본 TTS 시연 코드 + tkinter 원형. 온라인 음악 API, 실제 자연스러운 여러 DJ 목소리, Windows 실행·라이선스 검증·배포는 미검증/미구현. 기존 상품/등록 이력 삭제·진척률 전용 금지.


## 2026-11-13 추가 — AXNODE 독자 섹터형 실행 파일 기술

| 제품 | 개발 브랜치 | 설계 정본 | 공식 최종완성률 | 출시/크몽 |
|---|---|---|---|---|
| **AXNODE** | `product/axnode-sector-runtime` | [최종설계 R01~R29](https://github.com/hibi89/Freelancer/blob/product/axnode-sector-runtime/docs/FINAL_BLUEPRINT.md) | **UNASSESSED** | **HOLD / 미등록** |

- 사용자 확정: 신규 파일 확장자 `.axnode`의 **A안 자체 바이너리 섹터/주소표와 중앙 실행 그래프**. 여러 GitHub 저장소/브랜치로 프로그램을 나누는 기술이 아님. 실 저장/연산 자원은 로컬·NAS·승인된 원격 실행기에 존재할 수 있음.
- 제품 브랜치 최종설계 등록·정책/요구/STATUS/HANDOFF 완료. 로컬 POC `19 PASS/0 FAIL/0 SKIP` (샘플 5섹터/852 bytes)와 GitHub 코드 통합/CI·Windows/3GB/원격 실행은 **명확히 별개**. 본 branch는 현재 설계 자료이며 POC 소스는 별도 ZIP 다운로드 산출물.
- 해총 `kmong-productization/docs/audits/FREELANCER_BRANCH_COMPLETION_REGISTRY_20261113.md`에 신규 제품 등록. 이전 기업형 5종+소비자형 3종 그대로. 총 **8 product 브랜치 / 9 Freelancer 제품**. 기존 29종·19개 서비스에는 중복 합산하지 않음.

## 2026-11-13 BID AX 별도 공공입찰 준비상품 신규 구현

- 기존 크몽 원천29종 중 **BID AX**를 Private `product/bid-ax-public-procurement`에 신규 독립 구현(기존 제외 BID OWL과 별개). 확정 소스 커밋 [`d614c08e611e`](https://github.com/hibi89/Freelancer/commit/d614c08e611ef15d388865034ada215e10c8da6e), 원격 12/12 파일 내용 일치.
- `docs/FINAL_BLUEPRINT.md` R01~R21 전체 100% 기준. Python 3.11+ stdlib 로컬 JSON+SQLite+CLI: 공식 HTTPS 근거 확인, 버전/중복, 기업 지역·면허·예산·서류 만료·마감 검토, 보고·백업, 순수 7일 API 요청계획(실 전송 없음). 합성 로컬 단위 19 PASS, CLI import/screen/history/backup PASS; GitHub CI/실공고/실 Windows/법무·상용 고객 미검증.
- **사용자 목표: 최종완성률 50%, [작업중]**. 승인 가중치/전수 실제 요구 검증 부족으로 **공식 UNASSESSED** 유지, 상품 RELEASE HOLD/미등록. 기존 29원천→19판매+내부CUBE 및 각 기존 상품의 공식률·등록완료 이력·마커 변경 없음.
- 현재 Freelancer 브랜치 **9 product 브랜치/10종 제품**(기존 8/9 + BID AX 1/1). 해총 [중앙 추가등록부](https://github.com/hibi89/hackathon-command-center-2026/blob/kmong-productization/docs/audits/FREELANCER_BRANCH_COMPLETION_REGISTRY_20261113.md), [BID AX 전체 설계](https://github.com/hibi89/Freelancer/blob/product/bid-ax-public-procurement/docs/FINAL_BLUEPRINT.md).



## 2026-11-13 WORKNOVA Desk 독립 상품 P50 오프라인 엔진

- 비공개 제품 구현 브랜치 [`product/worknova-desk-local`](https://github.com/hibi89/Freelancer/tree/product/worknova-desk-local). 전체 WD-01~14 정본은 해당 브랜치의 `docs/FINAL_BLUEPRINT.md`; 코드 검증 기준 커밋 [`6b7f86738fb6`](https://github.com/hibi89/Freelancer/commit/6b7f86738fb6ed6c7b965523955efcae3285d1f7), 최신 제품 문서 `5c7f3478ccf06b0ee037a23456c541951ff39fa4`.
- 한국 프리랜서 로컬 **KRW/VAT 견적→계약/마일스톤→납품/수정·승인→수동 수금 기록**과 감사·SQLite 백업·CLI. 원본 PayPal 해커톤은 참조만 사용, 신규 구현은 Python3.11+ stdlib·비공개. 코드/테스트/문서 11/11 로컬 ↔ 원격 Git blob SHA 일치, Linux Python3.13.5 18 PASS/0 FAIL/0 SKIP.
- GitHub [Final blueprint gate #43377108605](https://github.com/hibi89/Freelancer/actions/runs/43377108605) SUCCESS는 메타/근거 감사이며 해당 Python 단위 테스트 자동 실행 결과가 **아니다**. 실제 Windows/고객/은행 확인/GUI/문서·설치/라이선스/출시 **NOT_RUN**.
- 사용자가 요구한 최종설계 기준 50%는 승인 가중치/전체 고객 수락·범위 미충족으로 **공식 UNASSESSED**. 별도 P50 기술 엔진 실증 완료; **[작업중] 유지·RELEASE HOLD·크몽 미등록**. 기존 29개 원천제품 및 19개 게시 후보를 중복 추가하지 않는다.
- 이 신규 상품을 포함 현재 원격 확인: `product/*` **10개 브랜치 / 11개 상품** (ECHOHOME·PAWTALK 동일 브랜치). 이 숫자는 기존 8/9·9/10의 역사적 증빙을 덮어쓰지 않는다. 해총 [후보 등록부](https://github.com/hibi89/hackathon-command-center-2026/blob/kmong-productization/docs/audits/FREELANCER_BRANCH_COMPLETION_REGISTRY_20261113.md) 동기화.
