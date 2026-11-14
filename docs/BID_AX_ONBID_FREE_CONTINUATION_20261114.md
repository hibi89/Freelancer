# BID AX — 안전한 무료 온비드 후속 페이지 수집 (2026-11-14)

## 적용 범위·현재 증거
최종설계 R01~R29 29개 전체를 유지하며 최종완성률은 **UNASSESSED / 목표85% 미입증**입니다. 온비드 15157252 실 첫 페이지 10/10 확인, 서버 보고 186건(19페이지)은 **수집된 186건이 아닙니다**. 나머지 18페이지는 실제 키를 가진 소유자 PC에서만 수집할 수 있습니다.

## 설계
A) 클라우드 일괄 수집/원문 자동 반영: 계정 권리·원문 필드·개인정보·비용 위험으로 불채택.
B) 이미 저장한 첫 페이지 격리 JSON을 고객 PC에서 검증 → 동일 조회조건의 누락 페이지만 명시 승인·일일 호출 예산 안에서 수집 → 신규 파일에 원문 격리 → 기존 로컬 SQLite UUID 배치로 검증/재개. **선택**. 자동 입찰·법률 자격/투자 판정/원장 승격은 없습니다.

## Windows 사용자 실행 예시

반드시 최신 소스 `product/bid-ax-public-procurement`에서 실행하세요. 아래 `$first`는 고객 PC에 이미 저장한 원본 격리 JSON의 실제 경로로 바꿉니다. 키를 채팅/커맨드 인자/파일에 쓰지 마세요.

```powershell
$first = 'C:\\PATH\\TO\\result_001.json'
$batch = [guid]::NewGuid().ToString()
New-Item -ItemType Directory -Path '.\\local-onbid-pages' -Force | Out-Null

# 1. 호출 0회, DB 생성 0회, 키 입력 없음
py -3.11 -m bidax.cli --db '.\\local-onbid-pages\\stage.db' onbid-continue $batch $first --out-dir '.\\local-onbid-pages' --consent

# 2. 소유자가 직접 승인한 경우만 실행. 매 실행 키를 메모리에 1회 입력
py -3.11 -m bidax.cli --db '.\\local-onbid-pages\\stage.db' onbid-continue $batch $first --out-dir '.\\local-onbid-pages' --consent --live --max-new-pages 4 --daily-limit 24

# 3. 한 번에 18페이지가 필요하고 실제 제공자 잔여할당이 확인되면
# 위 명령의 --max-new-pages 4를 18로 변경; 같은 UUID를 반드시 보존
# 4. 중단 후 같은 배치 상태 조회
py -3.11 -m bidax.cli --db '.\\local-onbid-pages\\stage.db' onbid-stage-status $batch
```

- `--live` 없이는 외부 HTTP 없음. `--consent` 없으면 저장/HTTP 차단. `--max-new-pages` 1~25 범위, 기본4. `--daily-limit`은 사용자 PC에서 서비스별·KST 날짜별 요청 **시도** 수를 SQLite에 영구 기록해 제한(기본24).
- 응답은 기존 파일을 덮어쓰지 않고 새 JSON에만 저장. 전원이 꺼져 JSON만 남은 페이지는 다음 실행 때 해시/요청조건을 확인 후 무HTTP 재사용. 기존 페이지는 재호출하지 않음. 이상한/수정된 파일·다른 총건수는 안전 중단.
- 공식 15157220 endpoint의 **오퍼레이션**은 아직 독립 검증이 안 되어 호출 차단. 무료 표시/개발계정 트래픽과 고객의 상업적 원문 재판매 권한은 별도입니다.

## 검증과 미검증
신규 `bidax/onbid_capture.py`, CLI `onbid-continue`, 테스트 10종. [GitHub Actions #43540224552](https://github.com/hibi89/Freelancer/actions/runs/43540224552) **5/5 SUCCESS**: Ubuntu3.11/3.13 각276 PASS, Windows3.11 276 tests/0FAIL/1 POSIX SKIP, CLI/GUI EXE 비출시 스모크 성공. 첫 합성 테스트 샘플 totalCount 불일치 1 ERROR 수정 후 최종 SHA `3008bfd440aafe57e264ad4a0485d517f8819634` 성공.

**실 고객 Windows에서 후속18 페이지 API 호출은 아직 미실행**. 실공고 100건·독립 인간10명 검토·타 API3종·상업 권리·고객 설치/인수 미검증. 출시 `HOLD`, 크몽 미등록, `[작업중]`.
