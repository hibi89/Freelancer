# HANDOFF — ONTOINSIGHT AX (2026-11-13 KST / 필수 10항)

1. **목표·용도·확정 요구·기술:** `docs/FINAL_BLUEPRINT.md` 전체를 사용자 승인된 100% 분모로 사용. 고객 권한 있는 CSV/XLSX 의미/관계 승인→KPI/선택형 ML→근거 오프라인 보고. Python/pandas/Decimal/sklearn/reportlab/openpyxl; 외부 유료 AI 0.
2. **완료·변경·결정 근거:** P50/P70 기존 기능 유지, P85 ML source/target/feature/time/group 승인·time duplicate abstain, fold-safe CV, Dummy baseline/holdout, 원본 재검산 HTML/Excel/PDF/JSON·manifest ZIP 검증 및 신규 출력 CLI. 외부 LLM/단순 원본 DataFrame 1:N merge 대신 로컬 결정론적 분리 채택(비용/개인정보/중복매출 위험).
3. **테스트 명령·성공/실패/미검증:** 정확 코드 `8d1bdc80ed345485591f739aace632e91112a604` [Actions #43383793303](https://github.com/hibi89/AI_AutoML_Analyst/actions/runs/43383793303) Linux **93 PASS/0 FAIL/0 SKIP**, Windows Server2025 **93 PASS/0 FAIL/0 SKIP**, 둘 다 별도 30-core PASS·compileall PASS. 테스트 `pytest -q tests/test_ontoinsight_p50.py tests/test_ontoinsight_p70.py tests/test_ontoinsight_p70_cli.py tests/test_ontoinsight_p85_*.py` + `python -m scripts.ontoinsight_p85_core30_gate`. 전체 원본 회귀/구매자 Windows10/11/실 고객은 미실행.
4. **진행 상태:** P85 개발 단계 검증 완료; 사용자 전체 최종설계 공식 퍼센트 **UNASSESSED**; `[작업중]` 유지, `RELEASE HOLD`·크몽 미등록, 배포 대상 아님.
5. **실패 근거·원인·시도·재시도 금지:** 초기 P85 `d8ac0644` 90 PASS/3 FAIL—두 test expectation/fixture 문제, 반복 timestamp 무결성 위험 → 보수적 HOLD로 수정; 현재 기능 `8d1bdc80ed345485591f739aace632e91112a604` 93/93 PASS. 부실 시간 split 및 허위 완성률 반복 금지. 실제 암호화 XLSX, 환불 이벤트 식별/중복, 법적 고객 동의, 실시간/외부 API 기능 미검증.
6. **저장소·브랜치·SHA·주요 경로:** 설계 `hibi89/Freelancer@product/ontoinsight-ax-data-analytics`; 구현 `hibi89/AI_AutoML_Analyst@feature/ontoinsight-ax-p85-20261113`, 코드 SHA `8d1bdc80ed345485591f739aace632e91112a604`, 운영 문서 SHA `d027481b886bd86b75f5e44b73250e4e3c0948b3`; `backend/app/services/ontoinsight_p85_ml.py`, `ontoinsight_p85_report.py`, `scripts/ontoinsight_p85_delivery_cli.py`, `scripts/ontoinsight_p85_core30_gate.py`, `docs/qa/ONTOINSIGHT_AX_P85_20261113.md`.
7. **Production URL·환경·실행:** Production/Vercel **N/A**. Actions Python3.11 Ubuntu24.04/Windows Server2025. 제한형 CLI: `python -m scripts.ontoinsight_p85_delivery_cli --orders orders.csv --refunds refunds.csv --receipt receipt.json --out fresh.zip`. 원본 P70 review→attest 선행; 고객 Windows10/11 직접 설치/시각검증 NOT VERIFIED.
8. **원본·백업·인증 관리:** 기존 AutoML main/P50/P70 브랜치, 고객 원본/모델·토큰 보존. P85 분기 기초 SHA `0e831106c03efb5ba6cba4d840dcfecf73ec235f` 복구점(별도 브랜치 이용, 강제 push 금지). 로컬 attestation은 법적/암호학적 고객 인증이 아니며 고객자료 GitHub/외부 송신 금지.
9. **다음 우선순위·완료 기준·승인:** P95 독립 36/36 통과(실 password XLSX), 데이터 provenance/법적 사용권·반품/취소 이벤트ID, 원본 전체 회귀, Windows10/11 실파일·PDF fonts/NOTICE/성능/업종2종, P100 계약·보관·지원·영수증·GO. 공식 85% 판정은 모든 최종요구 가중치와 정확 SHA의 승인된 검증 증거가 선행돼야 함.
10. **최신화 일시(KST)·확인 범위:** 2026-11-13 KST. 코드 SHA `8d1bdc80ed345485591f739aace632e91112a604`, CI #43383793303를 원격 확인. 세 저장소 문서 동기화 이후 각각 HEAD를 별도 확인하며, 문서 갱신만으로 원본 기능·최종률 변동 없음. P85 상세 기록 `docs/P85_ACCEPTANCE_EVIDENCE_20261113.md`.

---

## 이전 P70 인수 상태 (역사 보존)
기존 P70 설계·기능 SHA 및 감사문서는 Git 이력과 `docs/P70_ACCEPTANCE_EVIDENCE_20261113.md`에 유지되며 공식 전체 완성률 미산정.
