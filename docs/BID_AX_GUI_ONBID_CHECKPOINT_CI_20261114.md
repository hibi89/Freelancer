# BID AX — GUI 오프라인 온비드 멀티페이지·Windows CI 검증

**2026-11-14 KST** · 최종설계 R01–R29 고정 · 목표 최종85%(공식 미입증) · 소스 SHA `1ae85fcb4cc58d3bdd3f52d37c243b99f1f4e4f4`.

## 변경 및 비용/안전 비교

- **불채택 A:** 확인되지 않은 Onbid 원문을 바로 정규화·자동 수집 후 법적/투자 판정. 잘못된 필드 해석·권리·사용자 키 전송 위험이 높음.
- **채택 B:** 고객 PC에 이미 존재하는, 검증된 공식 응답 격리 JSON만 Tk GUI에서 다중 선택. 사용자가 UUID 배치를 만들거나 기존 것을 붙여넣고, 파일 경로·SHA/건수의 로컬 SQLite 저장에 명시 동의할 때만 오프라인 증빙 기록. 원본·키·고객 자료 업로드, 추가 정부 HTTP 호출, 낙찰·입찰 자격 자동 확정 없음.
- 기존 `bidax/onbid_batch.py`의 페이지·쿼리 SHA·중복/변조·누락/재시작 봉인 계약을 재사용. GUI `LocalController.onbid_stage_pages`로 다중 선택, 이전 파일이 유효하면 나중 파일 실패 때도 기존 페이지 유지(사용자 재개 가능). 완성 상태는 `OFFLINE_COMPLETE_NOT_IMPORTED`이며 원문 필드 계약/상용권 검증 아님.
- 기존 15버튼 Tk 툴바의 가로 화면 이탈을 줄이기 위해 5열 그리드로 재배치. 이는 Tk 정적 코드/컨트롤러/Windows Tk 기본 창 스모크 근거이고 사용자 UI 육안 검수 완료를 의미하지 않음.

## 원격 검증 표

| 대상 | SHA/근거 | 결과 | 한계 |
|---|---|---|---|
| Ubuntu Python3.11 | Actions #43538216227 | 263 PASS | 합성/Mock |
| Ubuntu Python3.13 | 동일 | 263 PASS | 합성/Mock |
| Windows Python3.11 | 동일 | 263 tests, 0 FAIL, 1 POSIX SKIP | 고객 Win10/11 아님 |
| Windows console onedir EXE | 동일 | CLI 실행/무 HTTP 계획 PASS | 출시 미승인 |
| Windows GUI 시험 EXE | 동일 | Tk init + unsigned PE onedir build PASS | EXE 실제 GUI 조작/설치/SmartScreen 미검증 |
| 최종 R01–R29 종단 수용 | 기존 29 요구 감사 | UNASSESSED/85% 미입증 | 실 100공고/10인간·운영API·권리/고객 |

- 최초 코어 변경 `a2e93a2c89daecb1d003eb6a2e35109dc0e40c20`의 [CI 실패 #43537874647](https://github.com/hibi89/Freelancer/actions/runs/43537874647)는 **Windows 테스트 임시 DB 연결 미종료**, 260개 중 1 오류(WinError32). `5447f2e21a50e359e0c3f680d6238cd3c57b74c8`에서 다중 파일 선택·3 테스트 추가 후 마지막 `1ae85fcb4cc58d3bdd3f52d37c243b99f1f4e4f4`에서 명시적 SQLite closing 적용. [최종 성공 CI](https://github.com/hibi89/Freelancer/actions/runs/43538216227) 5/5. 수동 빈커밋·강제 재배포 없음.
- 기존 첫 실제 15157252 응답은 페이지1 **10/10**, 기관 보고 `totalCount=186`이므로 **18개 후속 페이지 미수집**. 이번 새 공식 API 호출 0; 제품 개인정보·API 키 원문 GitHub 업로드 0.

## 인수/다음

- GUI에서 새 배치 UUID 제안 또는 기존 UUID 입력 → 원래 격리 JSON 다중 선택 → 고객 경로 보관 동의 → 진행/누락 페이지 확인. 마지막 응답까지 로컬 복구 가능. **실사용자 Windows 원본 실행 미검증**.
- 다음: 실제 API 필드/권리 확인, 소유자 PC 후속18페이지 및 G2B/온비드 2종 샘플, 100 실제 공고·인간10 사례, Windows 설치/GUI 검수·고객 인수·상업적 API/문서 권리/사용 정책. 필요한 유료·외부 전송·원본/보안 변경은 별도 승인.
- 상태: `UNASSESSED` / `[작업중]` / `RELEASE HOLD` / 크몽 미등록. **기존 CANDIDATE-10/KMONG-SVC-18·BID OWL/타상품/고객 DB 보존**.
