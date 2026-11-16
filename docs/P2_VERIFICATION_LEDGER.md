# AX Dev Factory P2 acceptance evidence · 2026-11-16 KST

Functional source `f2becd6d3b9c19347516cd46f40186cc211f7340`, branch `codex/axdev-full-verification`, based on `5ab94180471c7ea86344b691fc77ad5c29989071`. The following handoff commit changes documentation only. The PR checks check out the exact PR HEAD. [GitHub Actions for this branch](https://github.com/hibi89/Freelancer/actions?query=branch%3Acodex%2Faxdev-full-verification).

**12/20 F-ID acceptance rows PASS. Eight rows have requirements still NOT_RUN.** A row passes only when its listed behavior has evidence at its defined interface. Section 6 device trial gates are tracked separately below. Formal weighted progress is UNASSESSED. Owner real-use remains HOLD.

| ID | Status | Evidence and remaining checks |
| --- | --- | --- |
| F01 | PASS | Public plan retrieved at approved branch SHA; Git blob and local SHA256 pinned. Plan mismatch, candidate replay and unauthorized path rejected. Task and oracle immutable across restart. |
| F02 | PASS | Cycle/unknown dependency rejected; fixture queues prove VERIFIED prerequisite ordering and HOLD isolation. |
| F03 | NOT_RUN | Queue and worker locks, disjoint coding/reviewer processes and serial staging exercised. Real OpenCode worker lifecycle and single resident model on target remain untested. |
| F04 | NOT_RUN | Effective Ollama-only policy checked synthetically; local Ollama metadata and generation tested on Windows 11. Real offline OpenCode tool calls and provider enforcement untested. |
| F05 | PASS | Separate Git worktree in synthetic coding; sandbox snapshot and exact isolated integration ref exercised while original checkout and HEAD remained unchanged. |
| F06 | PASS | Candidate digest and allowlist, tracked test protection, Windows aliases/reparse probes, and AppContainer write denial tested. |
| F07 | PASS | Native AppContainer executes protected tests and distinct callable probes. A fake successful test process cannot make a wrong callable result pass. |
| F08 | PASS | Isolated controller rejects failed probes, loads the candidate into one repair only, HOLDs continued failure, proceeds with unrelated work and leaves dependents queued. |
| F09 | PASS | SQLite task and policy pins, proof digest, exact commit parent/tree and integration history cross-checked; forged or stale checkpoint/history resisted. |
| F10 | NOT_RUN | Interrupted coding and PREPARED promotion recovery tested; real Windows Sandbox termination, Windows 10 restart and power-loss behavior untested. |
| F11 | PASS | Actual Git commits from reviewed bytes, original ref untouched, proof and commit/tree/parent verified on resume. Forged guest and modified host proof attempts stopped. |
| F12 | NOT_RUN | Offline PR preview, exact approved remote and double confirmation guards tested. Actual AXDEV publication under the owner’s explicit export approval still needed. The development PR is separate. |
| F13 | PASS | Live GitHub GET-only import at `5ab94180471c7ea86344b691fc77ad5c29989071`, blob `41fed2876b33831987384b3bcc3c96c79b7cf93e`. First run `created=true`; identical repeat `created=false`. SHA race, alternate HTTP errors and cache guards covered by regression tests. |
| F14 | PASS | Actual public EAI code `a911540fd07b72533e215849e142148327a5adbc` ran a synthetic goal in a Windows AppContainer. Exit 0, `DECIDED`, independent verifier accepted, receipt SHA256 `158281229032b62cd8ff0da3c5a43815b290ae17ab29322469f1e832093826ec`. Adapter requires the independent policy and exact goal SHA. EAI is an extra gate and cannot grant task VERIFIED. |
| F15 | PASS | Adapter produces typed nodes, dependency edges and hashes and rechecks checkpoint against current plan and SQLite; changed spec and tampered JSON rejected. Scope is the typed bridge. Native AXNODE binary import was not exercised. |
| F16 | NOT_RUN | Actual Windows 11 Pro build 26200, GTX 1050 Ti 4096 MiB, 15.8 GiB RAM. Ollama 0.40.16 with installed `qwen3:4b-instruct` generated a 2-token sample at 16.6 eval tokens/s; sampled VRAM usage 0 MiB. Target Win10, second model, GPU coding and workflow comparison untested. |
| F17 | NOT_RUN | Cooperative stop/resume, invocation caps, durable budget, locks and metadata events tested. Actual owner startup, OS task registration and scheduled launch untested. |
| F18 | NOT_RUN | Original receipt exploit reproduced at the data boundary. Fake promotion denied; separate host AppContainer denies private file I/O, snapshot writes and connection to a listening localhost port on Windows 11. Forged project test result and proof mutation regressions pass. Windows 10 Sandbox launch, VM mapping and actual no-egress still require device proof. |
| F19 | PASS | Installed local GGUF `qwen3:4b-instruct` returned `SEMANTIC_PASS_LOCAL_ONLY` for a synthetic code sample. Deterministic oracle gates promotion before a semantic verdict; malformed or external model evaluations rejected. |
| F20 | NOT_RUN | Synthetic sequential fleet, approved plan checks, caps, loopback HTTP owner dashboard, CSRF and Host validation covered. Live owner browser use and authorized status synchronization untested. |

## Final blueprint §6 trial gates

| Gate | Evidence | Target trial |
| --- | --- | --- |
| 1. Prerequisites | Win11 preflight detected Ollama, GTX 1050 Ti and the tool-capable installed model; OpenCode unavailable; Windows Sandbox optional feature disabled. | NOT_RUN on Windows 10; current-host readiness FAIL. |
| 2. Safe dry run | Synthetic fixture and dry-run verification in Linux/Windows CI. | NOT_RUN on the target device. |
| 3. Allowed changes by the coder | Synthetic scope, candidate validation and exact Git bytes. | NOT_RUN with real OpenCode in Windows Sandbox. |
| 4. Protected tests pass and unauthorized edits HOLD | Native AppContainer positive and adversarial tests plus guarded candidate and commit regression tests. | NOT_RUN for the full isolated coding path on Windows 10. |
| 5. No duplicate after replay | Public GitHub import replay and simulated interruption/SQLite/Git recovery pass. | NOT_RUN after real Sandbox interruption. |
| 6. Independent queue after HOLD | Isolated controller synthetic fixture checks one fix, HOLD, independent VERIFIED and dependent QUEUED. | NOT_RUN with the actual coding runtime. |
| 7. Performance vs manual GPT workflow | Local Win11 4B short inference sampled. | NOT_RUN with Windows 10, both local models, coding tool calls and manual comparison. |

## Evidence and next handoff

- The baseline Linux `139 PASS`, hosted Windows `138 PASS / 1 SKIP`, and CMD fixture pass remain tied to `841f957664023ac04cb4ee9abc4870d2a11596b3`. [Baseline CI](https://github.com/hibi89/Freelancer/actions/runs/43820637531).
- The PR checks and its evidence comment/body record final hosted test results and checkout SHA. A successful hosted job cannot certify the owner's machine. Python-native AppContainer tests exercise the reviewer alone.
- Remaining blocker is access to the supported Windows 10 machine with an enabled Sandbox and an owner-vetted offline toolchain. Then exercise denial and real coding, interrupted runs, startup, performance and allowed publication checks. Start with the fixed disposable fixture in [Windows Sandbox runtime](WINDOWS_SANDBOX_RUNTIME.md). Keep private state, logs and test assets on the device.
- Manual High handoff should compare the final design and exact branch diff, review the scope of the independent oracle, and rerun every missing device gate. Relevant evidence is the reviewable PR and these source-linked results.
