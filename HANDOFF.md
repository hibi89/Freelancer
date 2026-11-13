# HANDOFF — ONTOINSIGHT AX (2026-11-13 KST / 10항)

1. **목표·기술·설계:** 본 브랜치 `docs/FINAL_BLUEPRINT.md` 전체가 100% 분모. Excel/CSV 업무 의미 검증→승인→정확한 KPI→안전한 ML→재현 납품. 기존 AutoML Python/pandas/Decimal + 오프라인 ontology-lite; 외부 NVIDIA 스택 직접 설치/의존성 없음.
2. **완료·결정 근거:** 로컬 처리+기존 bounded CSV parser 재사용 방식 C 채택(외부 LLM 데이터 업로드의 개인정보·종량비용 및 단일 CSV-only 방식의 의미누락 문제 회피). 단일 CSV 메타데이터·역할 후보·SHA·승인 전 보류·합성 KPI 5종 원본 재계산 구현.
3. **테스트:** 원본 소스 기능 SHA `8da6ae98e308f68b52af159a662fe58c20f5bc74`. [Actions #43375766099](https://github.com/hibi89/AI_AutoML_Analyst/actions/runs/43375766099) Ubuntu11/11 Windows Server2025 11/11 PASS, 0 FAIL/0 SKIP, compileall PASS. 전체 과거 AutoML 회귀, 실제 고객/오너 Windows10/11 검증은 이번 SHA에서 미실행.
4. **현재 단계:** **P50 엔지니어링 수용조건 검증 통과**, 최종설계 공식 전체 완성률 **UNASSESSED**(요구별 승인 가중치·전체 증거 추적 미완성). 해총 **[작업중]**, 판매·출시 `RELEASE HOLD`.
5. **장애·원인·재시도 금지:** 제품 신규 CI 실패 없음. 입력 해시 변조, 중복 헤더, 모호 금액, 결측 금액, 환불액 초과, 없는 주문ID는 테스트에서 거절. 승인되지 않은 실 고객 지표는 계산하지 않음. 품질 검증 없이 50% 공식 표시 금지.
6. **GitHub·코드:** 기획 저장소 `hibi89/Freelancer@product/ontoinsight-ax-data-analytics`, 실행 저장소 `hibi89/AI_AutoML_Analyst@feature/ontoinsight-ax-p50-20261113`. 코드 `backend/app/services/ontoinsight_p50.py`, CLI `scripts/ontoinsight_p50_review.py`, 테스트 `tests/test_ontoinsight_p50.py`, 근거 `docs/qa/ONTOINSIGHT_AX_P50_20261113.md`.
7. **운영·환경:** Ubuntu24.04/Windows Server2025 Python3.11 Actions에서 합성 테스트. 로컬 CLI 메타데이터 JSON 사용 가능 설계지만 고객 PC에서 독립 동작 미검증. Vercel/Production **미적용**. 유료 API 0.
8. **원본·백업·비밀:** 원본 AutoML main 및 기존 분석 기능 보존, 독립 신규 기능 브랜치로 변경 격리; 분기 전 SHA `a3ddd8b9d20fee591ad246becab2b4adc89b56d8` 복구점. 고객 데이터·토큰·NVIDIA 코드 복사/공개/송신 없음. 민감 CSV 미수집.
9. **다음 작업·승인:** P70 다중 CSV/XLSX 안전 입력+source/mapping 서명 승인+cardinality-safe JOIN/원본-합계 검산 → P85 ML leakage/time/group/보고 → P95 Windows10/11 실기·고객·권리/검수 → P100 판매 승인. 공식 최종 50% 판정은 전체 요구 가중치 사전 승인 및 실행 증거 필요.
10. **최신화:** 2026-11-13 KST, 원격 기능 SHA/CI 결과 직접 확인; 본 문서 기준 실행 SHA `8da6ae98e308f68b52af159a662fe58c20f5bc74`이고 이후 문서 커밋은 기능 변경 아님. 해총 동기화 여부는 중앙 원장 최신 SHA로 별도 확인.
