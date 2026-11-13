# HANDOFF — 2026-11-14 KST AXNODE × WORKNOVA Desk 분산 배포 사용 사례 (10항)

1. **목표/기술:** 사용자 실기기 WORKNOVA Desk PyInstaller `onedir` EXE 의존 파일 분리 문제를 AXNODE 독자 `.axnode` 분산 참조·지연 조회·검증·복구 설계의 구체적 사용자 사례로 추가. A안 유지.
2. **완료/결정 근거:** `docs/FINAL_BLUEPRINT.md §12`에 동작 원리와 W01~W08 수용 매트릭스 추가; `STATUS.md` 현재 공개 상태/작업 이력 정리. 파일 단독 이동으로 무조건 실행되는 것이 아니라 OS DLL 의존·로컬 서명 스테이징 필요. 데이터는 실행물과 분리. 기존 R01~R29, 가중치 승인 대기 상태, 제품 기능/점수 불변.
3. **테스트·미검증:** GitHub 문서 읽기/쓰기·정확 SHA 확인만 수행. 사용자 WORKNOVA GUI 표시 증거는 실제 `onedir` Windows 창 렌더링 한정. W01~W08 = **0 실행 / NOT_RUN**. 이전 AXNODE POC 19 PASS는 과거 별도 로컬 시제품 증거이고 본 브랜치의 EXE/NAS/HTTPS 실행 검증이 아님.
4. **상태:** 요구 구체화 문서 완료, AXNODE 분산 로더/원격 실행/WORKNOVA 결합 **미구현**; 공식 `UNASSESSED`, `RELEASE HOLD`, 크몽 `미등록`, `[작업중]` 자동 표시/정식 점수 인상 없음.
5. **오류·재시도 금지·대안:** PyInstaller `onedir` EXE만 옮겨 의존 파일 없이 동작한다는 추정 금지. `onefile`도 내부 파일 추출하므로 원격 무설치 실행 보장이 아님. 네트워크 상실·USB/NAS 부재 시 캐시 없는 필수 단계는 PENDING/FAIL로 표시; 네이티브 DLL 검증 없는 원격 실행, SQLite WAL NAS 멀티PC 직공유 금지. 안전한 로컬 비실행 데이터 조회 POC부터 시작.
6. **Repo·branch·SHA:** `hibi89/Freelancer@product/axnode-sector-runtime` (현재 PUBLIC), 문서 전 HEAD `bda856370a00c05f28081581b397e90103e080c7`, 변경 `docs/FINAL_BLUEPRINT.md`, `STATUS.md`, `HANDOFF.md`. 기존 `main`, 타 product 브랜치 및 중앙 원장·WORKNOVA 브랜치 불변.
7. **Production/환경:** AXNODE 서비스·Vercel 미적용, Windows POC GUI/분산 통합 미실행. WORKNOVA 네이티브 Tk GUI 시각 확인은 별개 실제 Windows 로컬 실행 증거; 제품 상용 설치/원격 배포 아님.
8. **원본/백업·비밀:** 이전 SHA로 문서 복구 가능. 고객 SQLite 장부/원본 파일/운영 ACL/패키지·민감정보 변경 0; 원격 전송·권한 승격·유료 서비스 0. GitHub PUBLIC에 비밀/실고객 자료 업로드 금지.
9. **다음 순서·완료 기준:** W01 로컬 폴더·드라이브 합성 자료 E2E→W02 USB/NAS 연결 중단·캐시→W03 안전 HTTPS→W04 부분 오프라인→W05 체크포인트→W06 WORKNOVA 합성 결과동일성→W07 비용·시간/RAM 측정→W08 타 Win10/11 독립 실행. R01~R29 기본 수용과 별도로 점수 올리지 않음. 외부 데이터/비밀/원본·권한/비용 변경 전 승인.
10. **기록 시각·검증 범위:** 2026-11-14 KST. 정확 GitHub HEAD/커밋/파일 readback은 커밋 후 재확인 예정. 문서-only, CI·새 Windows 분산 실증·Production NOT_RUN.

---

# HANDOFF — AXNODE 전용 브랜치 (10항, 2026-11-13 KST)

1. **목표·용도·확정 기술:** 사용자 승인 **A안**, 독자 `.axnode` 바이너리(64-byte header/섹터 주소표의 POC에서 출발), 중앙 제어 그래프·기능 섹터·외부 로컬/NAS/원격 참조·지연 실행·복구. 사용자는 GitHub 저장소/브랜치를 여러 개 만드는 것이 아니라 단일 파일이 여러 섹터 역할을 가지는 개념을 확정.
2. **완료·변경·결정 근거:** Private `Freelancer` 전용 `product/axnode-sector-runtime` 생성, `docs/FINAL_BLUEPRINT.md` R01~R29·A/B 비교 및 안전·AX 상품화 방향 정리, README/REQUIREMENTS/AGENTS/STATUS/HANDOFF 분기별 전용 문서화. 기존 main/다른 product 브랜치/기존32 기술 원본 수정 금지.
3. **테스트/검증:** 원격 **설계 문서 fetch readback** 별도 확인. 로컬 이전 POC `python -m unittest discover -s tests -v` **19 PASS/0 FAIL/0 SKIP** (2026-11-13 KST), 5섹터 852바이트 CSV·합계 350.00·평균 116.6666666666666666666666667, CLI inspect/run 실행. 이번 브랜치 GitHub에 POC 소스/테스트 없음, CI 0, Windows/3GB/고객/Production 미검증.
4. **완료/진행/대기/차단:** 설계 브랜치·최종설계 등록 완료; 상세 점수 가중치/실제품 실행기는 개발 대기; 공식 완성률 UNASSESSED, 출시 HOLD·크몽 미등록. 원격 보안·신뢰 계층 없이 외부 실행은 차단.
5. **오류·원인·시도·재시도 금지·대안:** 3GB 로직 '소멸'·GitHub 무제한 무료 클라우드 가정은 비현실적. v0.1의 단순 SHA는 서명이 아님. 파일로 허가 없는 임의 Python/쉘 자동 실행 금지; B안 ZIP 재포장으로 승인 없는 설계 변경 금지. 실패 2회 무진전이면 보안/범위 재설계, 안전 로컬 POC 우선.
6. **저장소·브랜치·SHA·경로:** `hibi89/Freelancer` (private) / `product/axnode-sector-runtime`; 본 상품 기준 `docs/FINAL_BLUEPRINT.md`, `REQUIREMENTS.md`, `STATUS.md`, `AGENTS.md`, `HANDOFF.md`. 블루프린트 첫 커밋 `bc479afee9a456c4c454f948669b103c474c1233`; 최종 HEAD는 GitHub 브랜치 readback 기준. 중앙 해총 `kmong-productization/docs/audits/FREELANCER_BRANCH_COMPLETION_REGISTRY_20261113.md`.
7. **Production/Vercel/실행환경:** Vercel/Production 미적용. POC는 로컬 Python 3.11+ 표준 라이브러리 CLI `python -m axnode pack-demo/inspect/run`; GitHub Actions 트리거·원격 모듈 실행기 미구현.
8. **원본·백업·인증 관리:** 로컬 POC `/mnt/data/axnode_poc`, zip `/mnt/data/AXNODE_A_Prototype_20261113.zip`(대화의 임시 산출물, 영구 저장 아님). 원본/코드·바이너리 및 고객 비밀은 중앙 공개 저장소로 복사 금지. GitHub 브랜치/commit 이력으로 현재 문서 복구, main·다른 product 이력 보존.
9. **다음 작업·절차·승인:** 사용자 R01~R29 중요도/가중치 및 원격 권한·비용 승인→테스트된 POC 소스 영구 반영·정확 SHA 검증→포맷 fuzz/타입 그래프→safe resolver+cache→서명·sandbox→checkpoint/receipts→허가된 event runner→HAE/LA/SOVIA/DBVORA 통합→Windows/실고객/OSS·크몽 심사. 목표 전부 검증되어야 출시.
10. **갱신 일시/확인 범위/문서 기준:** 2026-11-13 KST. GitHub private 제품 브랜치 설계·중앙 원장 확인 및 로컬 POC 19 PASS. 문서 최종 커밋 SHA는 자기 참조 오류 방지를 위해 각 파일 update 응답/원격 비교로 확인. 코드 CI·Production·고객 수용 검증 0건.

**상태 변경 원칙:** 사용자 직접 확정 설계 전체를 100%로 보고, 가중치·정확 SHA 테스트 부족이면 UNASSESSED. 기존 제품 완료률과 상품 등록 이력 보존.
