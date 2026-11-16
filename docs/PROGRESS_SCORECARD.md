# AX Dev Factory progress scorecard (provisional)

As of 2026-11-16 KST. This is a **provisional, not owner-approved**
engineering readiness proxy. It is NOT the formal F01–F20 acceptance score
and cannot prove that autonomous local AI works on Windows.

| Area | Maximum | Current evidence-backed (provisional) | Reasons for unearned points |
| --- | ---: | ---: | --- |
| Approved task contracts, dependency graph, queue configuration | 20 | 20 | Linux synthetic tests prove parser + queue; target-project completeness is separate |
| Worktree coding/review and repair/HOLD | 20 | 17 | Real V2 model tool calling, permissions and actual code quality unproved |
| SQLite checkpoint and resumability | 20 | 20 | Windows power loss, cooperative stop/metrics not host tested |
| GitHub source/task sync and publishing | 20 | 11 | Live public read-only import passed; signed/authorized draft PR, owner status sync absent |
| Windows10 GTX1050Ti real AI, offline/security acceptance | 20 | 0 | No on-device E2E, GPU benchmark or OS/network sandbox proof |
| **Provisional total** | **100** | **68** | Formal completion remains UNASSESSED |

This is a _weighted readiness estimate_, not a timestamp-based labor
percentage. The underlying 20 features remain defined in
docs/FINAL_BLUEPRINT.md and REQUIREMENTS.md without modification.

Latest branch: hibi89/Freelancer@tools/ax-dev-factory-local.
Evidence source commit: `2a24cf7e3230066ce6c5f296c4ee80b291c9e5c3`; Python3.11 hosted 57/57 deterministic
tests PASS, GitHub Actions run
https://github.com/hibi89/Freelancer/actions/runs/43794334081.

Historical CI prior to latest work: 36 tests at SHA 214cbb0f...
Current new 57 tests verify extra test-time generated files are never
committed, source mutation after checks blocks, local stop/resume,
PR publication preview only and bounded localhost benchmark logic.
**Real** Windows10/Ollama/OpenCode/GPU evidence remains NOT_RUN.
Score reflects reproducible code and synthetic checks, not live model proof.

Next evidence gates: independent new stop/resume, local preflight and V2
policy contract tests; Windows disposable 1-model E2E; token-free
snapshot/permission proof, then explicit owner-approved PR publish.
