# ONTOINSIGHT AX 최종상품 50→70→85→95→100 수용 로드맵
**별도 AI AutoML 기존 95% 기록과 다른 신규 결합 제품 기준. 문서 작성만으로 개발점수를 올리지 않는다.**

| 누적 기준 | 신규 기능 합격 조건 |
|---|---|
| 50 | AI AutoML Analyst 실 CSV 1파일 경로 로컬 검증 + 경량 data dictionary/metric/meaning 후보 엔진, source SHA·review hold와 최소 4개 합성 KPI exact 재계산 |
| 70 | XLSX·복수 CSV(지원 2~3개) 검증 intake, 승인형 entity/relationship/cardinality/join policy, 주문·반품·채널 복수 source exact 합계, 기존 원본 불변·감사 |
| 85 | AutoML leak/target/time/group split+dummy baseline/abstain, 오프라인 분석 HTML/Excel/PDF/JSON 결과, 36개 데이터 품질·보안 위협 테스트 중 핵심30 PASS, Linux+Windows CI |
| 95 | 36/36 독립 QA(해당 환경별 SKIP 근거), 실제 고객 승인 자료 2개 업체/업종 또는 동등 허가 자료, 데이터 성능 p95/Windows10/11 실 PC 설치·파일 오픈/zip 재검수, LICENSE/NOTICE/고객 권리/출력 수치감사 |
| 100 | 고객 최종 산식·인수·리뷰/재분석/권리·보관·수정/지원·영수증/세금 정책, 실제 상용 납품 경계·운영비 확인, 사용자 최종 승인 후 RELEASE GO |

## 시작점/기술 증거
- 기존 `AI_AutoML_Analyst` 자체는 pandas/sklearn/FastAPI·CSV 분석 이력 있음, `feature/kmong-p6e50-owner-delivery-20261112` README 주요 한계 한 파일 CSV, target 누수 위험.
- 해총 P95 예전 CI 정확 SHA `458cf43816d3...`: Ubuntu 320 PASS/3 SKIP, Windows 322 PASS/1 SKIP, synthetic delivery Chromium 6/6 PASS. **새 Excel/ontology/관계 모델/고객 데이터 수용 실험이 아니므로 신규 상품 진척률 UNASSESSED.**
- NVIDIA Auto Ontology는 **개념 차용만**: 공식 코드/컨테이너/NIM/GPU·MCP 서비스의 실제 설치/연동 없음.
- 이번 브랜치 코딩 0, CI 0, Windows 실기기 0, 기업 API 비용 0, 고객 실 분석 0.

## 고객 인수·성과 측정
- 누적 목표는 feature checklist/정확 SHA/실행 커맨드/독립 데이터 재계산으로 평가. 필요시 파일 row-by-row reconciliation.
- KPI: source total vs derived summary exact, missing/invalid rows, parse success vs partial, business approval 100%, ML dummy baseline 대비 gain, heldout confidence interval·의미 없을 때 보류.
- 성능: 10MB/50MB 입력의 CPU/memory/time, 1k/100k/1m rows 한도는 실제 테스트 후 지원범위 고정. 임의 1m 지원을 광고 금지.
- 차별화: 일반 AutoML 단독 대비 고객 업무 컬럼 의미 확인 시간/잘못된 JOIN으로 인한 금액 오류 감소/보고서 근거 재현·재사용·지원시간 실측.
- 검증 후 해총 `kmong-productization` 후보 항목에 신규 제품 상태 및 feature SHA/CI 링크만 업데이트. 기존 Analyst 진척률 변경·자동 병합 금지.
