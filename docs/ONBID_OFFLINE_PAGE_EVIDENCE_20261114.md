# BID AX — 온비드 결과목록 멀티페이지 오프라인 증빙 체크포인트

2026-11-14 KST | 최종설계 R01–R29 불변 | 목표 최종 85%, 현재 공식 수용률 미산정

## 실제 근거와 범위

사용자 Windows/Python 3.11에서 본인 명시 동의·개인 키로 온비드 결과목록 API 15157252를 한 번 호출하고, 첫 페이지 응답을 로컬에 보관했다. 직접 보고된 안전한 메타데이터는 `resultCode` 성공코드 후보, `pageNo=1`, `numOfRows=10`, `totalCount=186`, `body.items.item` 길이 10(예상 10), 로컬 canonical JSON SHA-256 일치이다. **186건을 모두 수집하거나 원문 값/상업적 권리/법적 적합성을 검증하지 않았다.** 개인 인증키와 실제 결과 파일은 어시스턴트·GitHub로 전송되지 않았다.

## 설계 비교와 선택

A. 외부 API 페이지를 받고 즉시 정규화·영구 원장에 투입: 개발 단순하지만 실제 공식 항목 필드 계약·권리·경매결과 세부 의미가 독립 검증되지 않아 고객 오판·자료변조 위험이 큼. **미채택**.

B. 기존 고객 PC의 검증된 격리 JSON 파일들을 **오프라인·페이지 단위로 점진적 등록**: 서로 다른 페이지순서·중단복구 지원, 해시·조회조건·페이지 수 일치 검증, 원본 변경/분실 감지, DB에 원문 대신 로컬 경로·다이제스트·페이지 건수만 기록, 자동 법적 자격/입찰/영구 원장 승격 금지. 서버비·추가 API 요금·키 공유가 없고 오프라인 재현 가능. **채택**.

## 구현 사항

- 신규 `bidax/onbid_batch.py`: `stage_page`·`batch_status`, UUID 기반 불변 배치, 쿼리 필터(페이지 번호 제외) SHA, 서비스/자료셋 검증, 보고 전체 건수와 page size 일치, 동일 페이지 멱등, 다른 조회조건·다른 전체건수·대체된 패킷·원본 변경의 안전한 거부, SQLite 트랜잭션/재시작 후 재검증.
- 데이터베이스는 `onbid_stage_batches`, `onbid_stage_pages` 두 테이블로 분리. DB에 사용자의 **파일 절대경로와 SHA·건수만** 보관하며 API 서비스키·경매 물건명·개별 응답 원문·원본 JSON은 저장하지 않는다. 경로 자체는 개인정보가 될 수 있으므로 고객 PC 내부 보관이 원칙이다.
- `onbid-stage-page BATCH_UUID LOCAL_PACKET --consent`: **명시적 로컬 파일경로 기록 동의**가 있을 때만 페이지 등록. `onbid-stage-status BATCH_UUID`: 기존 DB만 **읽기 전용** 확인하고 원본 파일을 하나씩 다시 검사. 페이지 일부만 모이면 누락 번호 반환. 전수 재검증 뒤에만 `OFFLINE_COMPLETE_NOT_IMPORTED` 기록. 완성 후 원본 훼손 시 오류로 중단. 자료값·서비스키·원본 경로를 콘솔로 출력하지 않는다.
- `body.items.item` 각 항목을 실제 온비드 필드로 확정하거나 `OnbidStore`의 `assets`/`results`로 자동 매핑하지 않는다. 공식 필드 계약·실사용권 검토가 필요하다. 단일 실수집 페이지를 가지고 **19페이지 모두 수집했다고 주장하지 않음**.

## 고객 PC 오프라인 예시 (새 코드/기존 원본 경로)

```powershell
# 파워셸 변수 $files에 기존 원본 파일 경로가 있는 환경에서:
$batch = [guid]::NewGuid().ToString()
py -3.11 -m bidax.cli --db .\local\stage.db onbid-stage-page $batch $files[0].FullName --consent
py -3.11 -m bidax.cli --db .\local\stage.db onbid-stage-status $batch
```

**위 예시는 키를 받거나 API 요청을 하지 않는다.** 새 코드가 포함된 BID_AX 폴더에서만 동작한다. `local` 디렉터리와 기존 격리 원본을 보존한다. 이 실행은 사용자가 요청하기 전까지 필요하지 않다.

## 검증 및 한계

- Linux Python3.13.5 로컬 `python -Werror::ResourceWarning -m unittest discover -s tests -q`: **255/255 PASS**, 0 FAIL/0 SKIP. `compileall` PASS. 기존 237개 회귀 + 신규 18개.
- 신규 테스트: 186건 보고/첫 10개/미검증18페이지 표기, 역순 페이지·봉인·재시작·멱등, 필터/전체건수/페이지사이즈 충돌, 동일 페이지 바뀜, 저장 JSON 수정·삭제, DB에 고객 원문 미저장, 동의/UUID/심볼릭 링크/미확인 응답 거부, 빈 결과, CLI 무네트워크, 별도 배치 구분.
- 사용자 실제 Windows 파일의 **새 온비드 배치 명령 실행은 미검증**, 공식 타 3개 API 및 후속 페이지 실조회 없음. Windows/Python 3.11 GitHub CI는 커밋 후 실행 여부·결과 별도 확인.
- 현지 금융/법률·상용/원문 사용권·실공고100/자격 검토10/설치·고객 인수 등 **R01–R29 전체 수용 미완료**. 목표 85% 유지, 공식 완성률 `UNASSESSED`, `[작업중]`, RELEASE HOLD, 크몽 미등록.

## 백업·복구/보안

기존 원본과 DB를 덮어쓰지 않으며, 고객이 원본 파일을 이동하거나 잃으면 상태 검사에서 안전하게 오류 처리한다. 기존 배치 DB는 SQLite 정상 백업·로컬 통제하에 보존한다. Git 정상 revert로 전 코드 복원 가능. API 서비스키·고객 원본·개인정보를 GitHub·채팅으로 업로드하지 않는다.
