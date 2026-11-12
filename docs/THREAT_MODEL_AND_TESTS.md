# PROOFQA AX 위협 모델·감사 테스트 카탈로그

## 위협 경계
| 자산·신뢰 경계 | 공격/실패 | 기본 대응/허용 행위 |
|---|---|---|
| ZIP / Repo 입력 | symlink/hardlink/ZIP slip/bomb/비밀키/유니코드 경로 혼동 | 읽기/크기/총량/파일수 상한, 링크 거부, SHA·원본 보호, 시크릿 마스킹 |
| Sandbox 실행 | 빌드 postinstall/pytest가 고객파일/네트워크에 접근, exfiltration | OS 강제 egress deny, filesystem allowlist, nonprivilege, process/time/memory bounds; 없으면 실행 불가 |
| Graphify/외부 도구 | CLI 종속성 해킹, 파서 무한루프/AST coverage 과장 | lockfile·SHA/서명·운영체제 테스트, parse fail NOT_COVERED |
| Staging browser | CSRF/결제/삭제/실계정 PII/비인가 auth | 사이트·경로·행동 허용목록, dev 계정, 결제/계정 변경/삭제 금지, 리다이렉트 재검증 |
| Findings | hallucinated file:line, 기존 source와 불일치, 중복 경고 | exact source SHA/line/quote verifier, independent contradiction, false positive REJECTED |
| Severity | 방어층 존재하지만 심각 취약점으로 오인 | 실제 principal/resource/impact 증거 없으면 severity 부여 금지 |
| Reports | 보고서 XSS, 스크린샷 PII, HTML-PDF 불일치 | text escaping/CSP, redaction, PDF 독립 렌더·시각 검수, manifest |
| Client data | 외부 AI/Cloud 전송, 보유기간 초과, URL 접근 노출 | 권한 문서, 데이터 최소화/암호/삭제·수취인 제한, 비허가 전송 0 |

## 반증 중심 검증 시나리오 30개
1. 정상 Python AST 1파일, 함수 2개 연결. 2. 잘못된 Python 구문. 3. JS generic 탐지=보안 전체 PASS 오해 차단. 4. 규칙 미지원 언어 partial. 5. ZIP ../ 경로. 6. ZIP 중복 entry. 7. archive 압축폭탄. 8. 심볼릭링크. 9. 하드링크/디바이스. 10. `.env`/키 탐지 마스킹.
11. 원본 파일 변조/동시 교체. 12. Graphify 미설치. 13. Graphify 지원되지 않는 문법/파서 런타임 오류. 14. Graph inferred edge를 observed로 오표기 금지. 15. 그래프 장기 실행 CPU 한도. 16. 브라우저 사이트 진입 실패. 17. stale DOM ref 클릭 실패. 18. 클릭 전 화면과 클릭 후 변화 없음. 19. UI 성공 메시지 있으나 backend GET 저장 누락. 20. Network 401/403/500.
21. 고객 계정/비밀번호 누출. 22. 내부 IP redirect 차단. 23. 파괴적 Delete 버튼 발견→실행 거부. 24. 보안 후보의 독립 verifier가 반증하여 rejected. 25. 증거 부족 severity null. 26. 보고서 HTML escape의 악성 소스명. 27. PDF 시각 결과와 JSON finding 수치 일치. 28. 수정 후 SHA 다름→이전 CONFIRMED 상태 자동 재사용 금지. 29. 중복 run case/고유 output dir 충돌. 30. 물리 Windows 환경 압축 해제/경로·SmartScreen 및 설치/삭제.
- 테스트는 단순 계획이다. **이번 브랜치에서 실행한 30개 테스트는 없음**.
- 결과 보고: each test `test_id, source_sha, environment, command, expected, observed, PASS/FAIL/SKIP/NOT_RUN, evidence_hash`. CI exit 0이 모든 finding 검증 통과는 아니다.
- 패키지 테스트: 고객용 `report.zip`을 새 경로로 직접 추출→독립 CLI로 hash+schema+HTML/Markdown/PDF 교차 확인, 오류 시 RELEASE HOLD.
