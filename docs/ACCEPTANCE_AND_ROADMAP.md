# HAE 50/70/85/95/100 최종완성률 가중 기준 + 테스트
**100% = 아래 점검 통과 + 구매자 실제 승인. 내부 엔지니어링 단계 비율은 판매 가능도와 무관.**

| 구간 | 누적 가중 | 반드시 통과할 체크 (검증 자료 확보) |
|---|---:|---|
| 0→50 | 50 | HAE·LA 계약 목록/버전·synthetic CSV→승인 SQLite e2e, split state/business DB, 1개 시나리오 실패안전, 코드 SHA와 CI |
| 50→70 | 70 | LA 독립 실행/재시작·중복/digest 차단·로컬 UI preview, 2개 서로 다른 업무 워크플로, 무승인 write 0, 경합·속도 한계 |
| 70→85 | 85 | 3개 **합성** 업무 경로와 DBVORA 계약 모의 검증, audit·영수증, 스케줄 제한형, Windows+Linux CI 및 정확한 PASS/FAIL 구분 |
| 85→95 | 95 | **전체 CI 0 FAIL**, source↔zipapp/ZIP parity, 실 DBVORA 프로세스, 지원된 실제 Gmail/Sheets OAuth 1개씩(판매 범위에 포함 시), 고객 승인형 작업 UI, Win10/11 크롬/엣지 install/backup/restore/upgrade |
| 95→100 | 100 | 실제 비밀/데이터 처리 동의, 3개 고객형 워크플로, 재실행·유지보수·최종 인수서·라이선스/환불/가격·사업자/증빙 정책, 고객 배포 승인 |

### 상세 테스트 분류
1. **Unit**: IR schema version, node dependencies/DAG cycle, safe file inputs, bad encodings/cells, unknown command refusal, run ID uniqueness, amount numeric overflow, redacted logs.
2. **State**: crash before/after business commit, kill during receipt, concurrent run ID, recovery after reboot, tampered SQLite, migration to new schema, repeated schedule tick.
3. **API/Provider**: 401/403/429/500/timeouts, token revoked, quota exhausted, provider duplicate response, ambiguous mail outcome; external API assertions must use real sandbox/permitted account separately.
4. **DBVORA**: real localhost process selected database schema hash/size/relations + read-only assurance; corrupted DB backup & independent new-path restore; raw data not leaked in inventory.
5. **Security**: loopback/origin/CSRF, malicious file/link path, prompt injection into source CSV, oversized payload, log-redaction, secret lifecycle, outbound network deny.
6. **UI**: click review→approval→run→refresh→status, stale response race, manual edit invalidates stored plan, accessible keyboard, Chrome/Edge Windows actual.
7. **Commercial**: nondeveloper Windows install, instructions, opt-out/abort/uninstall no residue beyond expressly user-kept data, onboarding time/one revision contract, license notices.

### 입증된 원본 기록과 현재 미해결
- HAE `feature/axflow-mvp` 문서 기록 85% 잠정; historical Actions `42990527614`: 양OS Python **264 PASS/2 FAIL/7 SKIP**, Node UI **24 PASS**. 2 FAIL은 오래된 출고 ZIP/pyz↔소스 parity; **full CI FAILURE**.
- 실 DBVORA 서비스/Google OAuth·Sheets/Gmail/고객 Win10·installer·real customer acceptance 미검증.
- LA 브랜치 기능 및 추가 HAE bridge의 일부 격리 테스트 존재하나 최종 GUI 전환·통합·상품 출고 증거가 아님.
- **이번 이 저장소 작업에서 제품 테스트 실행 0건**. 위 기록은 원본 repo 문서/기존 CI의 과거 증빙이며 실제 배포 재검증이 아니다.

### 단계별 후속 수행 순서
P1 상태/계약/배포물 mismatch 파악→P2 LA adapter 고정/회귀→P3 DBVORA 실제 독립 프로세스/두 DB 검증→P4 지원된 커넥터 1개씩 옵트인→P5 Windows 고객형 인수→P6 출고 보안/라이선스/지원→최종 사용자 승인. 매 단계 원본 GitHub source SHA·검증 명령·결과·복구 계획 기록.
