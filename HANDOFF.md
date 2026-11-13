# HANDOFF — ONTOINSIGHT AX (2026-11-13 KST / 10항)

1. **목표·용도·기술:** `docs/FINAL_BLUEPRINT.md` 전체가 100% 분모. 소상공인 CSV/XLSX 의미 확인→원본 검증→명시적 승인→정확 KPI→적합할 때만 ML→재현 보고. 원본 AutoML pandas/scikit-learn/FastAPI/Decimal 경로 + 로컬 ontology-lite.
2. **완료 기능·결정:** P50 단일 CSV/metadata/SHA/review-hold 기반 P70 2~3 파일 CSV·XLSX, 로컬 승인 attestation·맵/파일 버전 묶기, 주문/환불/채널 관계키 검증 및 1:N 중복 매출 차단, 정확 Decimal 합계/CLI. 외부 LLM 업로드 대신 로컬 방식 선택(비용/개인정보), naive join 배제(중복합산 위험).
3. **테스트:** 원본 실행 SHA `34e7b16a2fef5e1b0d21f4e6d097c6faaaaf9012` [Actions #43378733016](https://github.com/hibi89/AI_AutoML_Analyst/actions/runs/43378733016) 2/2 SUCCESS. Ubuntu 44/44 PASS, Windows Server2025 44/44 PASS, 양쪽 0 FAIL·0 SKIP, compileall PASS. 원본 전체 회귀/실 고객·Windows10/11·브라우저 검증은 별도.
4. **현재 상태:** P70 엔지니어링 수용조건 합성 검증 PASS. 공식 최종설계 전체 완성률 `UNASSESSED`(사용자 승인 요구별 가중치 미등록). 크몽 `[작업중]` 유지, `RELEASE HOLD`/판매 미등록.
5. **오류·원인·재시도 금지:** 이번 CI 실패 없음. 취약 입력: 승인 없음/변조·중복 order/channel·고아 refund·환불 초과·미확인 금액·수식/외부 링크/숨은 XLSX/민감 컬럼은 HOLD/거부. 동일한 환불 이벤트 중복과 법적 고객 동의는 코드만으로 보증할 수 없음. 최종률 임의 70% 확정 금지.
6. **저장소·브랜치·SHA·경로:** 기획 `hibi89/Freelancer@product/ontoinsight-ax-data-analytics`; 구현 `hibi89/AI_AutoML_Analyst@feature/ontoinsight-ax-p70-20261113` 실행 SHA 위, 문서 SHA `0e831106c03efb5ba6cba4d840dcfecf73ec235f`. 주요 경로 `backend/app/services/ontoinsight_p70.py`, `scripts/ontoinsight_p70_cli.py`, `tests/test_ontoinsight_p70.py`, `tests/test_ontoinsight_p70_cli.py`.
7. **배포·환경:** Python3.11 GitHub Actions Ubuntu24.04/Windows Server2025 2/2 성공. 로컬 CLI 경로 GitHub 테스트로 확인. Vercel/Production 미적용, 실제 고객 Windows10/11 데스크톱 구동·파일 리뷰 미검증.
8. **원본·백업·인증:** 기존 AutoML/P50/main 무수정, P70 독립 브랜치 기준 복구 SHA `8defbec4a943e081a12a6aaff1ae59f135ef05d0`. 고객 원본·토큰·비밀·유료 API 송신 없음. 승인 문자열은 법적/암호학적 서명이 아니므로 실제 고객 사용권·보유기간 합의 필요.
9. **다음 작업·승인:** P85 = ML 대상/시간/고객군 누수 차단 + dummy baseline/abstain + HTML/Excel/PDF 검증 보고 및 핵심 30개 위협 테스트+CI. P95 실 고객/Windows10·11/성능·LICENSE/NOTICE, P100 실제 인수/지원/세금 정책/승인. 공식 70% 산정을 위해 설계 전체 가중치/수용 증빙 승인 필요.
10. **갱신:** 2026-11-13 KST. 정확 실행 SHA/Actions 로그 확인, 코드와 문서 변경 분리, 설계 브랜치/해총 원장 동기화 별도 원격 SHA 확인. 사용자용 인수 보고 `docs/P70_ACCEPTANCE_EVIDENCE_20261113.md`.
