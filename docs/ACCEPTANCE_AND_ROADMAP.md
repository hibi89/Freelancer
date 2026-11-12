# CITEVAULT AX — RAG Studio 기업형 50/70/85/95/100 단계별 수용

> **상품명: CITEVAULT AX** · 근거형 기업 AI 지식·데이터 검색. 원래 제품명·저장소는 유지.
**이 표는 기존 개인용 RAG Studio 내부 95%와 구분되는 신규 기업형 상품 100% 설계 기준.**

| 누적 단계 | 합격 조건 |
|---|---|
| 50 | 실제 RAG 코드의 문서 파싱·BM25/SQL fixed query·인용·원본 무변경/오프라인 synthetic E2E; SMAX→AX 단일 샘플 계약 및 반품/매출 두 출처 검증 |
| 70 | PREP/SMAX 실 파일 매핑 리뷰/승인 격리, PDF/DOCX 2+ 동시 검색, 전체 코퍼스 충돌 보류, 모델 미설치 fallback, 역할별 권한 모델/테스트 |
| 85 | 고객형 사용자·그룹/컬렉션 실제 인증·ACL, 문서 버전/폐기·재색인, 무단 문서 누출 0, 한국어 실제 모델 소규모 수용, Windows/Linux CI |
| 95 | 실제 고객 동의 파일 1+ 세트, 골드100·부정/상충/권한 음성 세트·성능/메모리/검색 재현, 물리 Windows 10/11 설치·배포물 해시, 재설치·백업복구/라이선스 합격, CI 0FAIL |
| 100 | 고객관리자 수용서·모든 포함기능 종단 테스트/운영정책·가격/수수료/고객 자료권리/개인정보 법적 검수·실고객 사용자 권한·지원 범위·최종 승인 |

## 필수 테스트 실행 계획
- **Accuracy:** fixed SKU SQL exact value, 세전/세후·환불·총매출 의미 지도; Gold100 실제 소스 추적, 문서 상충 시 `ABSTAIN`.
- **Retrieval:** BM25 vs lexical vs Dense 동등한 질문세트/환경 비교, Recall@3/5, MRR/NDCG, p50/p95 latency, 언어 간 검색 한계.
- **Security:** 문서 A를 user B가 문서ID URL로 조회하려 할 때 403; 색인/캐시/벡터/제목으로 권한 우회 불가; 모든 파일 SHA/경로/ZIP 공격/공백·한글 파일명, 악성 프롬프트 거절.
- **Data lifecycle:** source update during parse, cancel import, missing rights, selected doc deletion, stale citations, orphan embeddings, backup restore post-index.
- **UI:** source highlight 정확 행/페이지, 문서 선택·검색/질문, API401/403/422 상태, 작은 화면/키보드, Chrome/Edge rendered E2E.
- **Ops:** 모델 없는 PC, RAM 부족, 장비 sleep, 100문서/1000문서 스케일 각 계약 환경, source-only/portable 설치 및 clean upgrade, 정상 복구.
- **License:** PDF.js/Mammoth 및 배포되는 ONNX/model weights 라이선스/NOTICE/상업 배포 요건·버전 고정; 모델 없으면 해당 기능 판매 제외.

## 확인된 선행 증거 (실행 재검증 아님)
- 사용자 중앙 관리 문서에는 RAG 일반 엔지니어링 **95%**(2026-11-12, `0e88301059c9...`, Actions `43231121679`)가 기록: Linux 635건 중 633PASS/2SKIP, Windows 635 중 634PASS/1SKIP; Gold100/Negative20/Heldout24. 이 CI는 synthetic/internal gate이며 기업 운영 승인 아님.
- `develop` GitHub ref는 `e63e539ab8ded5834cb85672aa2142eb660d3f23`(2026-11-13 조사). 95% 코드와 `develop`의 정확한 포함 관계는 추가 diff/branch 확인 필요.
- Windows 22.16/특정 filesystem API 문제 기록; Node22.23 이상에서 hosted Windows 합성 PASS. 판매용 설치 최소 환경을 실제 PC로 검증 필요.
- 실제 고객 문서 권리 검토→진짜 `ACCEPTED` 승격·기업 ACL/인증·정식 모델·물리 사용자 PC 설치·금액 결제/구독은 **미검증**.

## 작업 우선순위
1. **코드 SHA/브랜치 합류 확인**: 95% 테스트된 정확 feature source와 develop, customer packaging의 차이 정리.
2. 실제 PREP→SMAX 단일 계약·승인 서명/폐기 설계 확정. 합성 negative tests와 로컬 오류 방어.
3. 기업 문서/사용자 ACL 구현과 index filter, 테스트 사용자 A/B 데이터 격리.
4. 로컬 모델 E5/생성 LLM 실하드웨어와 규칙 기반 fallback, 검색 품질 객관 평가.
5. 개인정보 동의가 완료된 고객형 Gold·설치/보안·백업/원복 수용 및 상품 정식 출고 승인.
