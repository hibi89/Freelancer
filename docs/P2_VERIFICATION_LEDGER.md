# AX Dev Factory — P2 validation evidence ledger

**Date:** 2026-11-16 KST. **Scope:** `hibi89/Freelancer@tools/ax-dev-factory-local`. **Verified functional commit:** `841f957664023ac04cb4ee9abc4870d2a11596b3`.

**검증 완료율 (stage 1): UNASSESSED.** F01–F20 are 20 code-implementation candidates; **0/20 have been formally signed off against their COMPLETE final acceptance conditions**. This is a signed-off acceptance count, NOT a weighted 0% score. The user has not approved a 100-point F-ID weight denominator; do not fabricate a percent from hosted test case counts or historical provisional readiness 72/100. Maintain this metric separately from both implementation progress and CI test pass rate.

## Evidence / state boundary

| Evidence gate | State at pinned functional SHA | Claim allowed |
| --- | --- | --- |
| Linux Python 3.11 synthetic suite | PASS: 139/139 | CI tests passed, not real model |
| GitHub-hosted Windows Python 3.11 synthetic suite | PASS: 138, 1 SKIP, 0 FAIL | Windows-hosted tests passed, not owner Windows10 |
| Windows CMD disposable no-model smoke | PASS | Synthetic local CLI readiness |
| Final blueprint evidence gate | PASS | Blueprint completeness gate, not product verified |
| F18 independent acceptance proof | SECURITY HOLD | Guest-writable receipt cannot certify its own tests; no host integration promotion |
| F20 dashboard loopback authority/CSRF | SYNTHETIC PASS (4 regression tests) | HTTP source behavior on hosted CI only |
| Owner Windows10 Sandbox/virtualization/no-egress | NOT_RUN | No claim of real OS isolation |
| Real local Ollama/OpenCode model + approved project | NOT_RUN | No model-derived accepted code |
| Power cut/restart, memory/VRAM/throughput | NOT_RUN | No device-specific proof |
| Codex Sol Max/Astra Max independent audits | NOT_RUN (next stage, not stage-1 denominator) | Must occur after High stage-1 100% |
| High final design acceptance / owner GO | NOT_RUN (later stages) | Not a stage-1 result |

## F-ID verification coverage

- **F01–F20:** code paths available from P1 implementation census (20/20 source candidates). Most scripted behavior covered by local/hosted synthetic tests. This does not imply 20 final acceptance passes.
- **F02/F05/F07–F11/F14/F15/F19:** useful deterministic/adapter tests already run in CI, but relevant full task, model, Windows or end-to-end evidence remains absent where required. No complete final F-ID approval was issued.
- **F18:** confirmed structural trust-boundary defect in the guest-writable result receipt: mitigation prohibits automatic host VERIFIED promotion, but secure independent reviewer/attestation requires design, implementation and physical tests.
- **F20:** dashboard Host protection, CSRF and native HTTP tests PASS; no live owner browser usability, full multi-project UI or on-device acceptance.
- **F16/F17 and cross-cutting controls:** real GPU/Windows startup and long-running power-loss tests not performed.

## Chronological code evidence

1. Baseline hosted P2 after initial Git LFS correction: code `9d6fe7f2300fbf135685a71d606a744a9e2d743e`, [CI #43817078016](https://github.com/hibi89/Freelancer/actions/runs/43817078016) PASS 133 Linux / Windows 132 + 1 skip.
2. Sandbox false acceptance mitigated: `41b2d311...` with syntax correction `5ad55aa...`, [CI #43819822302](https://github.com/hibi89/Freelancer/actions/runs/43819822302) PASS Linux 135 / Windows 134 + 1 skip.
3. Dashboard Host guard and HTTP tests: `e1948939...` had Windows test reset [#43820302560](https://github.com/hibi89/Freelancer/actions/runs/43820302560) FAIL, fixed at functional SHA `841f957664023ac04cb4ee9abc4870d2a11596b3`; [CI #43820637531](https://github.com/hibi89/Freelancer/actions/runs/43820637531) PASS Linux 139 / Windows 138 + 1 skip; [blueprint #43820638910](https://github.com/hibi89/Freelancer/actions/runs/43820638910) PASS.

## Next high-priority verification work

Implement a independently OS-enforced reviewer identity/process or host-verifiable attestation that the guest code/model/project tests **cannot** mint or tamper with. The existing hash-validated outbox may contain untrusted candidate bytes but must NEVER be promoted as VERIFIED. Evaluate supported Windows edition and trusted toolchain dependencies before a one-task disposable real-model trial; no Windows Home unisolated fallback or permission changes without approval. After stage-1 formal verification reaches 100%, commission separate Codex Sol Max technical/security and Astra Max frontend/UX reviews, then High final requirement comparison.

