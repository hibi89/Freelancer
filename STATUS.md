# BID AX 2026-11-13 P85 independent test preparation (latest)
- User target: final 85% of full R01-R21 blueprint. **NOT VERIFIED**; official **UNASSESSED**, **[작업중] retained**, RELEASE HOLD, no Kmong listing.
- Locally Python3.13.5 Linux **94 PASS / 0 FAIL / 0 SKIP**, compileall PASS, Python3.11 AST syntax for 20 files PASS, Python .pyz --help PASS. Added 100 SYNTHETIC notices in 5 out-of-order pages with restart and 10 FAKE review records + backup/restore. These are **NOT** 100 real official notices / 10 independent human qualification checks.
- Created manual-only .github/workflows/bid-ax-manual-acceptance.yml 3 matrix legs (Windows3.11, Ubuntu3.11/3.13). **NOT DISPATCHED** due private Actions possible billing; no independent OS CI result, actual Windows installer or customer run yet. Existing blueprint-only workflow success is not Python CI.
- Evidence docs/P85_CROSS_PLATFORM_ACCEPTANCE_PLAN_20261113.md. Prior baseline HEAD 78247ce6132fc1af2b05cd7fb65729711355caf6; latest HEAD to verify after docs commit. API contracts, real data/rights, Windows/EXE, real Korean PDF and customer acceptance unverified. Other branches and user data preserved.
---

# BID AX P85 보안 후속 — 2026-11-13 KST

- 사용자 목표: 최종설계 전체 **85%**. 공식 최종완성률 **UNASSESSED / 목표 미검증 / [작업중] 유지 / RELEASE HOLD / 크몽 미등록**.
- 새 기능 SHA `9a895ad6ac6d47941d0cf5c5a3ec908e4a298947`: 완료된 수집 배치 사후변조 거부, API 승인 bool 엄격화, 오류문구 내 서비스키 노출 방어, 타임아웃 유한 재시도·KST 일일 호출예산.
- Linux Python3.13.5에서 전체 로컬 회귀 **90 PASS/0 FAIL/0 SKIP**, compileall PASS (기존83 + 신규7); 실제 정부 API 호출·고객자료 전송 없음. [증거](docs/P85_SECURITY_FOLLOWUP_20261113.md).
- 이번 기능 코드/테스트 3개 GitHub readback 완료; 새 커밋 Python CI 결과, Python3.11, 실 Windows10/11, 실제 공고100건·자격10건·권리/고객 인수 미검증. 기존 BID OWL과 다른 제품 보존.

---

# BID AX P85 engineering checkpoint — 2026-11-13 KST

- **목표:** 사용자 확정 최종설계 전체 **85%**. **공식 최종완성률 `UNASSESSED` / 85% 미입증 / `[작업중]` 유지 / RELEASE HOLD / 미등록**.
- P85 로컬 기능: UUID/7일/page/전체건수 일치 스냅샷 체크포인트·재시작 복구, 변조·중복 거부, 저장된 기한 알림 중복 방지, *호출 불가 기본 상태* 의 선택형 공식 API 전송 라이브러리(메모리 키/고정 URL/단일 요청의 유한 재시도·로컬 사용량 기록), Windows 수동 패키징 스크립트·검증용 Python `.pyz`와 manifest 소스 ZIP. 기존 P70 GUI/원장/3상태 사전검토 보존.
- 로컬 Python3.13.5 Linux `python -Werror::ResourceWarning -m unittest discover -s tests -q`: **83 PASS/0 FAIL/0 SKIP**; `compileall` PASS; Tk8.6 Linux Xvfb 기본 초기화 PASS. Windows/Python3.11/실 API·고객/EXE/원격 Python CI **NOT_RUN**.
- [P85 세부 검증/잔여 요구](docs/P85_STAGE_EVIDENCE_20261113.md); 전체 21개 요구 R01–R21 변경/축소 없음, 승인 가중치 부재. 국내 조달 운영 자격/실 공고100건·10사례·PDF·서명/실 설치·보안/실사용 승인 없음.
- 기능 이전 Git SHA `766032d6256d634469366b1125639f9aa9a6ef1c`. 이번 원격 commit/SHA는 GitHub 반영 후 readback으로 확인해야 함. 비밀/고객DB·BID OWL·기타 Freelancer 상품·크몽 29/19 이력 무수정.

---

# BID AX — status (2026-11-13 KST, P70 continuation)

- **Product:** private `hibi89/Freelancer@product/bid-ax-public-procurement`; BID OWL unchanged and excluded. Final 21-requirement blueprint unchanged.
- **User target: 70% full design**, work marker `[작업중]` preserved; **official final completion UNASSESSED**, owner-approved requirements weights lacking, explicit release/registration HOLD.
- **Local P70 engineering additions:** Tkinter GUI (profile → import → screen → history / manual review → export / backup / restore), append-only idempotent review with stale fingerprint check; KST on-demand alerts, diff, SQLite hash/quick-check, create-only database backup and restore; report JSON/CSV/HTML with CSV formula and HTML injection guards, max-10MiB local JSON bound.
- **Testing:** baseline 19 PASS; total **45 PASS / 0 FAIL / 0 SKIP** in Python 3.13.5 on Linux; warnings-as-error check clean. Tk8.6 GUI launches/closes under Linux Xvfb. Exact source SHA/readback to confirm after GitHub commit. No live API/real 100 notices/10 human eligibility cases/Windows10 or 11/installer/PDF/long-running scheduling/production/customer pilot.
- **No external transfer:** No official API key or HTTP request in product; no user document uploaded; raw notice input is already authorized normalized local JSON, not live official response mapping.
- **Reference:** [P70 requirement by requirement evidence](docs/P70_STAGE_EVIDENCE_20261113.md), `REQUIREMENTS.md`, `docs/FINAL_BLUEPRINT.md`; official portal is `https://www.data.go.kr/data/15129394/openapi.do` with 7-day limit effective 2026-11-10.
- **Next 70→85:** live authorized API mapping/quota/backoff/attachments/credentials, actual Windows GUI+installer, safe scheduling and migration, PDF/report acceptance, real 100/10 cases, customer rights, role model and approved full-score weights.
