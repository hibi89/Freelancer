> **[BID_AX_P70_DOC_SYNC_20261113]** BID AX 개발 담당: 사용자 70% 목표, 최종 R01–R21 고정. Python 로컬 기술 P70 45 PASS/GUI Xvfb smoke만 확인되므로 **공식 UNASSESSED·[작업중] 유지·RELEASE HOLD**, API/실 Windows/가중치 승인 없이 공식 70%·판매 완료 주장 금지. 소스 SHA `22d44f5e2fb39024703331903b881bec7bfd6521`. 코드는 이 전용 브랜치에만, BID OWL/타 브랜치 무수정. [검증 상세](docs/P70_STAGE_EVIDENCE_20261113.md).

# BID AX branch operating rules

Source of truth: `docs/FINAL_BLUEPRINT.md` + `REQUIREMENTS.md`. User's OWNER-FINAL-BLUEPRINT-100 policy from the central `hibi89/hackathon-command-center-2026@kmong-productization` applies. This private branch is separate from historical excluded `hibi89/Bid_Owl`; no Bid_Owl source or customer data is transferred.

Workflow: HANDOFF → STATUS → AGENTS → REQUIREMENTS → FINAL_BLUEPRINT → code/tests; protect original evidence; no data/credential/network calls or paid/cloud deployment without separate approval; maintain exact SHA/test counts and blockers; mark `[작업중]` until final blueprint 50% is provably met. Official score uses only approved weights + exact source/real test evidence; otherwise UNASSESSED. Keep sale RELEASE HOLD and central 29→19 classification untouched.
