> [BID_AX_P85_20261113] 사용자 최종설계 R01~R21 전체 85% 목표. 검증 가능한 오프라인 P85 범위와 최종완성률을 혼동하지 않는다. 공식 `UNASSESSED`·`[작업중]`·`RELEASE HOLD` 유지. [이번 기술 범위](docs/P85_STAGE_EVIDENCE_20261113.md). 원본 `Bid_Owl`·타 브랜치/고객 DB 미수정. 유료 CI·실 API 전송·배포·원본/보안 권한 변경 사전승인.

# BID AX branch operating rules

Source of truth: `docs/FINAL_BLUEPRINT.md` + `REQUIREMENTS.md`. User's OWNER-FINAL-BLUEPRINT-100 policy from the central `hibi89/hackathon-command-center-2026@kmong-productization` applies. This private branch is separate from historical excluded `hibi89/Bid_Owl`; no Bid_Owl source or customer data is transferred.

Workflow: HANDOFF → STATUS → AGENTS → REQUIREMENTS → FINAL_BLUEPRINT → code/tests; protect original evidence; no data/credential/network calls or paid/cloud deployment without separate approval; maintain exact SHA/test counts and blockers; mark `[작업중]` until final blueprint 50% is provably met. Official score uses only approved weights + exact source/real test evidence; otherwise UNASSESSED. Keep sale RELEASE HOLD and central 29→19 classification untouched.


## P70 continuation instructions (2026-11-13)

`[작업중]` target **70% of owner-defined full blueprint**; evidence file `docs/P70_STAGE_EVIDENCE_20261113.md`. The local P70 engineering workflow was tested (45/45), but do **not** mark official 70%, remove the marker or release product until owner weights and full acceptance are proven. Do not copy or mutate `Bid_Owl`, create a SaaS, call G2B with unspecified user key, access private external documents, or overwrite user DB. Record exact source SHA and readback; CI and Windows marked NOT_RUN unless separately verified.
