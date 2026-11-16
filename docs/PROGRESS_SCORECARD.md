# AX Dev Factory progress scorecard (provisional)

As of 2026-11-16 KST. This is a **provisional, not owner-approved**
engineering readiness proxy. It is NOT the formal F01–F20 acceptance score
and cannot prove that autonomous local AI works on Windows.

| Area | Maximum | Current evidence-backed | Reasons for unearned points |
| --- | ---: | ---: | --- |
| Approved task contracts, dependency graph, queue configuration | 20 | 20 | Linux synthetic tests prove parser + queue; target-project completeness is separate |
| Worktree coding/review and repair/HOLD | 20 | 15 | Real V2 model tool calling, permissions and actual code quality unproved |
| SQLite checkpoint and resumability | 20 | 18 | Windows power loss, cooperative stop/metrics not host tested |
| GitHub source/task sync and publishing | 20 | 10 | Live public read-only import passed; signed/authorized draft PR, owner status sync absent |
| Windows10 GTX1050Ti real AI, offline/security acceptance | 20 | 0 | No on-device E2E, GPU benchmark or OS/network sandbox proof |
| **Provisional total** | **100** | **63** | Formal completion remains UNASSESSED |

This is a _weighted readiness estimate_, not a timestamp-based labor
percentage. The underlying 20 features remain defined in
docs/FINAL_BLUEPRINT.md and REQUIREMENTS.md without modification.

Latest branch: hibi89/Freelancer@tools/ax-dev-factory-local.
Previous hosted CI: 36 tests success at commit 214cbb0fdd7e4c4d5340a67a93c524aac04e12c4;
later preflight/stop-control code CHECKS PENDING until proven by executable
CI or owner host. No automatic score increases from adding code.

Next evidence gates: independent new stop/resume, local preflight and V2
policy contract tests; Windows disposable 1-model E2E; token-free
snapshot/permission proof, then explicit owner-approved PR publish.
