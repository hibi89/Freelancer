# AZENTFLOW AX — 0→50 기술 수용 검증 기록 (2026-11-13 KST)

## 판정
- **설계상 0→50 구간 기술 게이트: PASS (synthetic HAE→LA→SQLite)**. 사용자 지정 50% 중간단계의 기술 항목은 실 실행 근거를 확보했다.
- **공식 최종완성률: UNASSESSED (100점 전범위 요구별 가중치/독립 검수 미완)**. P50의 통과를 상품 전체 공식 최종률 50% 확정, 상용 50%, 출시 승인, CI GREEN으로 전용하지 않는다.
- **판매: RELEASE HOLD / 미등록**. 중앙 크몽 원장의 `[작업중]`은 공식 목표치 검증 완료 전 유지.

## 출처·정확 SHA·실증
| 항목 | 확인 |
|---|---|
| HAE 코드·신규 수용시험 | `hibi89/HAE@feature/axflow-mvp` 정확 실행 SHA `91963ae3ba656b384c2c5db092c9bc6cdcdc1e39` |
| LA 독립 엔진 | `hibi89/HAE@feature/lightning-azent` 사후 조회 HEAD `36f9882eb50e0de9e85eedb320a5778c8321cda5`; CI는 움직이는 branch ref 체크아웃(별도 pinned ref 체크는 후속 필요) |
| 신규 검증 코드 | `apps/ax-flow/tests/test_azentflow_p50_acceptance.py` |
| 실제 CI | [GitHub Actions #43375517050](https://github.com/hibi89/HAE/actions/runs/43375517050); 2026-11-13 약 15:03 KST 종료 |
| CI 시스템 | GitHub-hosted Ubuntu, Windows, Python 3.11, Node 22 |
| 새 게이트 | Ubuntu 3 PASS, Windows 3 PASS, 0 FAIL / 0 SKIP |
| 기존 smoke / adapter | HAE→LA→SQLite HTTP 6/6 PASS, LA adapter 5/5 PASS 두 OS |
| 전체 Python 회귀 (OS 각각) | 276 테스트 = 267 PASS, 2 FAIL, 7 SKIP |
| UI Node 회귀 | 24 PASS |
| 전체 workflow | FAIL (2개 기존 출고 아티팩트 parity); 별도 final-blueprint 검증 workflow는 SUCCESS이나 제품 품질 수용으로 치환 불가 |

## 최종설계 0→50 기술 기준 대조
| 50구간 기준 | 실증 경로 / 결과 | 증빙 경계 |
|---|---|---|
| HAE↔LA 계약 목록·버전 | `axflow.ir.v0` ↔ `azent.api.v0`, capability fingerprint/version/preflight 계약: **PASS** | 독립 LA 브랜치 Git 객체 고정 검증은 향후 강화 |
| synthetic CSV→미리보기/승인→SQLite E2E | 합성 CSV 두 행→localhost preview→명시적 승인→LA 실행→SQLite 2행: **PASS** | 실제 고객/외부 공급자/LLM 미실행 |
| runtime/state와 business 데이터 저장 분리 | `runtime.db`의 runs/steps와 별도 `business.db`의 csv_records, SQLite integrity: **PASS** | 고객 민감정보를 사용한 실 보안감사 미실행 |
| 최소 실패 안전 시나리오 | 미승인 write **403/두 DB 미생성**, 입력 SHA 변경 **409/두 DB 미생성**, 같은 run 재호출 행 중복 0: **PASS** | 임의 운영DB·제3자 API exactly-once 미보증 |
| 코드 SHA와 실제 CI | 두 OS 각 신규 3/3, 기존 smoke 6/6: **PASS** | 전체 CI failure 2는 별도 출시 차단 |

## 오류·재시도·원본 보호
- 첫 test-only SHA `1d1523f8b00e3cb1cf54a9bc6b7a846c93cb303d`에서 `unittest.TestCase.run` 메서드 재정의 충돌로 전체 Python suite 실패. 정확 원인을 확인한 뒤 `execute_preview`로 변경했고 기능 SHA `91963ae3...`에서 양 OS 신규 게이트가 통과했다. 실패를 숨기거나 무한 재시도하지 않았다.
- 기존 2 FAIL은 `test_shipped_package`의 보존된 `hae-integrated.pyz`, `HAE-Windows-offline.zip` vs 현재 소스 불일치. Ubuntu는 `run-bundled.cmd` line endings 차이, Windows는 `launch_integrated.py` 내용 차이 등. **원본 ZIP·pyz를 덮어쓰지 않았으며** source parity 문제 해결·서명/Windows 인수 전 RELEASE HOLD다.
- 기존 고객/비밀/운영 DB·OAuth/외부 계정·실 데이터·원본 HAE/LA 실행 코드·워크플로 설정·배포 모두 변경하지 않았다. 제품 검증은 합성 로컬 임시 데이터만 활용. Git 이력으로 테스트 코드 롤백 가능.

## 아키텍처 대안 비교
| 대안 | 성능 | 비용 | 유지보수·보안 | 선택 |
|---|---|---|---|---|
| A. AZENTFLOW 상품 브랜치에 HAE/LA 엔진 복제 | 복제 후 로컬 실행 가능, 버전 분기 시 불일치 | 초기 무상·코드 중복/검증 비용 상승 | 보안 패치 2중 관리, 원본 드리프트 증가 | 미채택 |
| B. HAE 원본 adapter + 독립 LA 소스 계약/CI·product branch 문서 | 기존 실제 로컬 HAE 실행 경로 유지 | 새 유료 서비스/외부 API 0 | 공통 코어 보존, 계약 불일치 fail-closed, provenance 개선 필요 | **채택** |

## 다음 작업
1. `50→70`: LA 독립 재시작·실행 원장/해시, 두 개 고객형 합성 워크플로, UI Preview/승인, 중복/동시성·재개·속도 상한을 정확 SHA로 수용.
2. LA CI 체크아웃의 동적 branch ref → 검증된 commit pin 또는 SHA 기록/비교 계약으로 개선하고 소스 패리티 증빙.
3. 기존 출고 ZIP/pyz는 원본 백업·차이 확인 후 별도 승인과 재빌드/검증. 우회성 skip/강제이력 수정 금지.
4. 최종설계 전체 요구·사용자 승인 가중치를 추적하고, 합성 단계의 PASS와 제품 공식률·판매 승인을 엄격히 분리.

**기록 기준:** 2026-11-13 KST, GitHub 원격 코드 SHA·Actions Ubuntu/Windows 로그 확인. Vercel/Production 미적용.
