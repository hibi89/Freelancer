# AX ZERO — 신뢰·보안·실패·복구 최종설계

## 신뢰 경계
유저/외부 SKILL.md/소스 문서/AI 생성 코드/LLM 자기 테스트/도구 결과는 **불신**. 별도 policy authority + deterministic verifier + human approval outside model이 유일한 자동 승격 경로. 모델 결과는 후보이며 절대 실행 권한/인증 근거가 아니다.

## 위험 목록과 강제 통제
| 위험 | 필수 대응 |
|---|---|
| SKILL.md 간접 prompt injection | 지침을 데이터로만 수집, trusted instruction과 분리, 허용된 입력 스키마·도구별 인자 검증 |
| 생성 코드 RCE·shell injection | 임의 eval/exec/무조건 subprocess/shell 금지, 정해진 IR 및 adapter allowlist |
| sandbox escape | 지원 OS에서 실효 격리 부재 시 실행 불가; 경계 밖 권한/마운트/네트워크 접근 차단 |
| 고객자료·비밀 유출 | 기본 network DENY, OS credential store, 로그 redaction, 공개 저장소에 비밀 0 |
| 고위험 실행 | 삭제·결제·권한·고객 원본·원격 업로드는 action+arguments 단위 사전 승인; 서면 승인 없으면 BLOCKED |
| 모델 셀프검증 부정 | verifier SHA·fixture SHA 분리, 생성자가 시험 기준 임의 축소 불가 |
| 검증 데이터 과적합 | unseen holdout·negative/delta/independent oracle, 실패 케이스 상시 축적 |
| 포맷/의존성 공격 | hash/version/size/path/symlink/zip bomb/SSRF·redirect 검증 |
| 비용 폭주 | 모델 호출/CPU/RAM/실행시간/반복횟수 상한, 무료 기본·유료 opt-in |
| 캐시 오염·TOCTOU | content-addressed verified artifact, 환경·정책 버전 포함한 캐시 키 |
| 드리프트 오판 | 불확실·중요 규칙 변경 시 HOLD; 이해하지 못하는 환경 변화는 기존 코드 무조건 실행 금지 |
| 자동 복구 중 중복 결제/삭제 | idempotency token, checkpoint, compensation 한계 명시, 재승인 |
| Windows 노트북 구동 | 프로세스 경계·Defender/SmartScreen/ACL·경로 테스트, 실제 OS 실행 증거 전 미검증 |

실제 독립 환경에서 격리될 때만 Python/JS 코드 실행 허용. 문서에 'sandbox'라고 썼다는 사실만으로 실행 안전성을 인정하지 않는다. SKILL.md embedded script는 읽기전용 정적 검사까지 P1 허용 가능하나 자동 실행은 gate.

## 버전·승격 프로토콜
`OBSERVED → CANDIDATE → COMPILED_QUARANTINED → SHADOW_PASS → VERIFIED_PINNED → REVOKED`; 모든 전이는 승인된 정책 엔진과 증거 SHA 필요. `VERIFIED_PINNED`도 해당 입력·환경 신뢰 범위의 보증이며 보편적 정답 아님.
- 자동 실행 중 실패: 새로운 고위험 효과 금지; 실패 영수증 기록 → 이전 pinned 버전의 계약을 다시 검사 → 안전할 경우만 rollback → AI/human escalation.
- 모델의 '성공' 텍스트로 수용 판정 금지. oracle이 없으면 `UNASSESSED`.
- 수집 자료 정해진 retention, 백업 확인, 사용자 삭제·암호화·OS 권한. 실제 사용자 자료 GitHub와 외부 워커 업로드 승인 전 차단.

## P1 즉시 안전검사 / P2 전체검증
- P1: policy deny-by-default, 경로탈출/권한, 비밀 redaction, 외부 HTTP 기본 OFF, 로컬 syntax/unit/국소 smoke. 위험 수정이 포함되면 즉시 focused regression 실행.
- P2: 전체 적대적 입력·공급망/샌드박스 탈출/권한상승, 장시간 복구, stale-cache, 브라우저/윈도우/통합+부하, false PASS 분석.
- 외부 문헌 참고 (정책 근거, 구현 검증 아님): OWASP GenAI Prompt Injection Prevention Cheat Sheet https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html ; Python subprocess security https://docs.python.org/3.11/library/subprocess.html
