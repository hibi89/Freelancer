# CITEVAULT AX — HANDOFF — RAG Studio 기업형 (10항, 2026-11-13 KST)

> **상품명: CITEVAULT AX** · 근거형 기업 AI 지식·데이터 검색. 원래 제품명·저장소는 유지.
1. 목표: Private PREP/SMAX²→승인된 AX패키지→RAG Studio BM25/dense/SQL+문서→근거 검증→선택형 로컬 모델+기업 ACL.
2. 완료: 상세 FINAL_BLUEPRINT, TECHNOLOGY_MAP, ACCEPTANCE_AND_ROADMAP, COMMERCIAL_AND_SECURITY 문서 작성. 원본 저장소 기능 변경 없음.
3. 테스트: 이번 브랜치 제품 테스트 NOT_RUN; 기존 해총 역사적 CI #43231121679(Linux 633PASS 2SKIP; Windows 634PASS 1SKIP) 별도 기록. 정확 develop/feature 포함 관계 미검증.
4. 상태: 설계 전용; 기업 사용권/계정/실물 Windows·로컬 모델/상용 출고 미검증, RELEASE HOLD.
5. 오류/장애: 개발용 localhost 인증을 기업 IAM으로 혼동하면 안 됨, unapproved `REVIEW_HOLD` 패키지 자동 승인 금지, 모델 없는 fallback 필요.
6. 원본: `hibi89/RAG_STUDIO@develop e63e539`, `hibi89/SMAX` Private, `hibi89/prep` Private, 상품문서 `hibi89/Freelancer@product/rag-enterprise-knowledge`.
7. 실행: Node 22 계열; 기존 RAG 원본 `npm test`, synthetic demo/Windows doc picker. Production/Vercel N/A. 외부 업로드 기본 불허.
8. 보존/권한: 고객 문서·키/모델 권리/Private SMAX 코드 외부 복제 금지, 원본 소스 모두 그대로. 승인 후 별도 기업 수용 파일 사용.
9. 다음: 최신 RAG 정확 CI source→develop diff, PREP/SMAX 계약→기업 권한/문서 수명주기→모델 벤치→실 PC/고객형 인수→최종 승인.
10. 시점/검증: 2026-11-13 KST GitHub ref/기존 문서 읽기. 실제 고객 실증/판매/소프트웨어 테스트 이 브랜치에서 미수행; 최종 commit SHA는 이후 readback.
