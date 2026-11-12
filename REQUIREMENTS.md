# HAE 기업 자동화 제품 확정 요구사항
제품 완료의 유일한 기준은 [docs/FINAL_BLUEPRINT.md](docs/FINAL_BLUEPRINT.md)의 계약과 [수용표](docs/ACCEPTANCE_AND_ROADMAP.md)다.
1. 한국어 작업 설명·프리셋/고객 파일→버전 고정 계획(IR)→위험·비용·대상 시스템 파악→미리보기/승인→실행→감사/복구.
2. HAE의 UI/정책/비밀정보/연동 어댑터와 LA의 결정적 실행·원장·중복 제어 분리, 버전 명시 `HAE→LA` 계약.
3. 실행 원장 SQLite와 고객 업무 데이터 SQLite 분리; 삭제/덮어쓰기 기본 거부; 승인·run_id·idempotency key·plan/source digest.
4. 기본 지원 범위는 CSV→SQLite·읽기 전용 집계·승인 쓰기/조건·스케줄; Gmail/Sheets는 정식 OAuth·최소권한·실 API 검증 후 옵션으로 활성화.
5. DBVORA는 원본 DB 직접 변경하지 않는 스키마/자산 조회 및 독립 백업·복구 정책을 소유; 장애 시 HAE는 관제 기능 `UNAVAILABLE`을 보고한다.
6. LLM은 계획 초안/설명만 담당; 자유 셸 명령, 임의 SQL, 미승인 원격 쓰기는 불허. 고위험 단계는 인간 승인.
7. 전송/비용/호출 횟수 제한·타임아웃/백오프·정지·재개·인증 만료·중복 외부 API 모호 응답 처리 필수.
8. 로컬 우선 Windows 10/11 인수, 실제 고객 업종별 사용성, 보안·라이선스·NOTICE·지원 정책 검증 전 출고 금지.
9. Basic/Standard/Premium은 지원되는 명시 기능만 판매하며 미구현 커넥터와 임의 기업 통합을 포함하지 않는다.
