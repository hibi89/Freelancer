# AZENTFLOW AX — HANDOFF — HAE+LA 크몽 상품 (10항, 2026-11-13 KST)

> **상품명: AZENTFLOW AX** · 승인형 기업 업무 자동화 · 기술 원본은 HAE + Lightning Azent + DBVORA; 기존 기술 이름/저장소는 변경하지 않는다.
1. 목표: HAE UI/정책 + Lightning Azent 독립 실행 + SQLite 원장/비즈니스 DB + DBVORA 읽기/복구·선택 SOVIA. 한국어 지원 업무 자동화 기업용 표준 납품.
2. 완료: FINAL_BLUEPRINT/TECHNOLOGY_MAP/ACCEPTANCE_AND_ROADMAP/COMMERCIAL_AND_SECURITY 설계 문서만 구성. 기존 원본 제품은 무수정.
3. 테스트: 이 브랜치 제품 테스트 0/0/0; 기존 HAE 역사적 CI #42990527614 양OS Python 264PASS 2FAIL 7SKIP, Node UI24PASS. 전체 FAIL; 상세 검증 docs 참조.
4. 상태: 계획 문서 등록, 기존 HAE 엔지니어링 85% 잠정(범위 다름), 판매 RELEASE HOLD.
5. 장애: 원본 배포 ZIP/pyz와 신규 소스 패리티 두 건 실패; 고객의 외부 SaaS/OAuth 실연동·Windows 설치 미검증. 기능추가보다 parity/contract 우선.
6. 원본: `hibi89/HAE@feature/axflow-mvp 1de81c2`, `hibi89/HAE@feature/lightning-azent 9fce9e2`; 제품 기획 `hibi89/Freelancer@product/hae-la-automation`. 파일 `docs/*`.
7. 배포: 제품은 로컬 우선; Vercel/Production 해당 없음. 실행은 원본 HAE 개발 문서의 Python3.11+ 명령에 따름.
8. 보호: 원본 Repo·Private 소스·고객 DB·OAuth·키·실 사업 자료·기존 branch 전부 불변; 복구는 원본 Git SHA와 이 저장소 제품 브랜치 commit 이력.
9. 다음: 원본 최신 README/HANDOFF/STATUS→기능 코드·테스트→패키지 parity 원인→LA adapter 실제 계약→DBVORA 및 지원 API→Windows 실고객형 수용, 사용자 승인 후 실행.
10. 일시/검증: 2026-11-13 KST GitHub 문서·metadata·기존 기록 조회. 이 설계 문서 최종 commit SHA는 별도 원격 readback 확인값을 사용. CI/고객 실증 미수행.
