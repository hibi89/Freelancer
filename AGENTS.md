> [BID AX 2026-11-14 최신 사용자 지시] 최종설계 R01–R29 **전체 고정**; 별도 배점/가중치 승인 요청 금지. 과거 이 문서의 R01–R21 및 '가중치 필수' 문구는 역사적 이력만 해당. 소스·실정부 데이터·Windows·법률/고객 수용 증거로 검증하고 85% 미입증 시 UNASSESSED/[작업중]/RELEASE HOLD 유지. [응답 격리 감사](docs/P85_API_RESPONSE_QUARANTINE_AUDIT_20261114.md).

> [2026-11-14 BID AX v2 최신] 사용자 확정 최종설계 R01–R29 29개, 목표 85%. 3모듈 오프라인 소스 GitHub 반영 후 local 136 PASS / 신규 API 계획기는 인증키 없이 네트워크 0. **공식 최종완성률 UNASSESSED**, 목표 미인증 [작업중], RELEASE HOLD. 새 기능 SHA `2a9852bcb47a271a4119f67dfcaf8ec35ae2a632`; 실 정부 API·Windows·승인된 100점 가중치 없음. docs/P85_V2_CURRENT_ACCEPTANCE_20261114.md 및 HANDOFF/STATUS를 먼저 확인.

> [2026-11-13 BID AX v2 사용자 확정 변경] 최신 최종설계는 R01–R29 총29개(기존21 보존 + 온비드/법원8 추가); docs/FINAL_BLUEPRINT.md 및 docs/BID_AX_EXPANSION_REASSESSMENT_20261113.md 정본. 아래 R01–R21 표기는 역사 이력. 공식 UNASSESSED, 목표85% [작업중], 출시 HOLD.

> [BID_AX_P85_SECURITY_FOLLOWUP_20261113] R01–R21 전체 최종설계 85% 목표는 **미달성/미산정**; [작업중]·RELEASE HOLD 유지. 기능 SHA `9a895ad6ac6d47941d0cf5c5a3ec908e4a298947`는 완료배치 사후변조 차단·네트워크 인증키 오류 방어, 로컬 90 PASS/0 FAIL. 실제 고객/Windows/공식 API 미검증. [후속 근거](docs/P85_SECURITY_FOLLOWUP_20261113.md).

> [BID_AX_P85_20261113] 사용자 최종설계 R01~R21 전체 85% 목표. 검증 가능한 오프라인 P85 범위와 최종완성률을 혼동하지 않는다. 공식 `UNASSESSED`·`[작업중]`·`RELEASE HOLD` 유지. [이번 기술 범위](docs/P85_STAGE_EVIDENCE_20261113.md). 원본 `Bid_Owl`·타 브랜치/고객 DB 미수정. 유료 CI·실 API 전송·배포·원본/보안 권한 변경 사전승인.

# BID AX branch operating rules

Source of truth: `docs/FINAL_BLUEPRINT.md` + `REQUIREMENTS.md`. User's OWNER-FINAL-BLUEPRINT-100 policy from the central `hibi89/hackathon-command-center-2026@kmong-productization` applies. This private branch is separate from historical excluded `hibi89/Bid_Owl`; no Bid_Owl source or customer data is transferred.

Workflow: HANDOFF → STATUS → AGENTS → REQUIREMENTS → FINAL_BLUEPRINT → code/tests; protect original evidence; no data/credential/network calls or paid/cloud deployment without separate approval; maintain exact SHA/test counts and blockers; mark `[작업중]` until final blueprint 50% is provably met. Official score uses only approved weights + exact source/real test evidence; otherwise UNASSESSED. Keep sale RELEASE HOLD and central 29→19 classification untouched.


## P70 continuation instructions (2026-11-13)

`[작업중]` target **70% of owner-defined full blueprint**; evidence file `docs/P70_STAGE_EVIDENCE_20261113.md`. The local P70 engineering workflow was tested (45/45), but do **not** mark official 70%, remove the marker or release product until owner weights and full acceptance are proven. Do not copy or mutate `Bid_Owl`, create a SaaS, call G2B with unspecified user key, access private external documents, or overwrite user DB. Record exact source SHA and readback; CI and Windows marked NOT_RUN unless separately verified.
