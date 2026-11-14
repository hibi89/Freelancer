# WORKNOVA Desk — 2026-11-14 frozen Windows EXE synthetic full lifecycle evidence

## 목표와 선택

기존 Windows EXE GUI/가상 고객 1건만 PASS하는 스모크보다, 실제 배포 대상 **동일 EXE 바이너리에서** 가상 견적·계약·수금/복원 로직을 직접 호출하는 CI 전용 오프라인 합성 QA를 우선. 외부 고객 PC·은행 API·실고객 기록을 가져오는 방안은 개인정보/유료/승인 리스크로 배제. 승인 WD01~14 최종100점 배점은 그대로 유지.

## 구현 및 안전 경계

- `worknova_desk/synthetic_acceptance.py`: 오직 임시 SQLite에 테스트용 거래처/견적 1000원+VAT100원, 미승인 계약 거부, 1100원 승인/계약/납품/검수, 부분수금700+400원, 영수증 중복 멱등/초과 거부, 해시감사→SHA-pinned 백업/새 DB 복원 검증 후 임시 파일 삭제.
- `tools/windows_gui_entry.py`: 임의 인자 거부, `--synthetic-qa-report <NEW .json>`는 `WORKNOVA_TEST_OFFLINE_ONLY=1`에서만 활성화. 정상 GUI 실행경로와 실 사용 `LOCALAPPDATA`는 unchanged.
- `tools/windows_exe_smoke.py`: 실제 frozen EXE 생성→GUI 기동·종료·합성 고객 영속→EXE 실행 모드에서 위 라이프사이클 수행/파일 결과 검사, 실패 시 stage를 보고하고 합성 프로필 삭제. 이 기능은 보안 검사/실 고객 수용을 대체하지 않음.
- `worknova_desk/gui.py`: Treeview의 영어 필드 제목 8개를 한국어 제목으로 대체, 내부 SQLite 데이터키/행 식별자/저장 포맷 변경 없음. 신규 `tests/test_frozen_synthetic_acceptance.py` 4개, `tests/test_gui_korean_headers.py` 2개.

## 원격 실검증

- 소스 SHA: `50ecb87b13a343c4b8428ea6c204afec57f6cd1a`.
- [Windows/Linux/EXE CI #43540390516](https://github.com/hibi89/Freelancer/actions/runs/43540390516): **3/3 SUCCESS**; Linux 174 (173 PASS/1 SKIP), Windows 174 (165 PASS/9 SKIP), Windows native 설치/백업/복원/갱신/삭제 11/11 PASS. Windows unsigned EXE 실제 창 표시·종료0/가상 고객1·SQLite integrity ok·frozen quote/contract/collection2/backup/restore PASS.
- PyInstaller Windows temp onedir EXE 2,300,758 bytes, SHA256 `9bc55621d0c1f67cf363cc1e056412978cc79080d9e8770e268fe20bade69e6f`, **미서명·미배포**. [원장 정책 게이트 #43540391034](https://github.com/hibi89/Freelancer/actions/runs/43540391034) SUCCESS(증거 검사만).

## 남은 구매자/판매 수용 범위

- 원본 최종 WD01~14 **100점·완전 수용한 항목만 배점 인정**. 공식 인정 **0/100**, 목표85 미달. 기술/자동화가 0%인 뜻은 아님. WD13/14 미승인일 때 이론상 점수 최대84점.
- **미검증:** 고객 실기기의 NTFS ACL/상시 장부 암호화, 공인 서명/SmartScreen·백신, Word/PDF 인쇄와 PDF 글꼴 상업권, 실제 고객의 납품·입금·법무/지원·구매 수용. CI 가상 행위로 이를 PASS 처리할 수 없음.
- 원본 DB/백업/Windows OS/타 상품·등록완료 원장 불변. `[작업중]`, RELEASE HOLD, 크몽 미등록. Vercel/Production은 오프라인 제품에 적용되지 않음.
