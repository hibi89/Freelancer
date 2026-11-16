# AX Dev Factory P2 acceptance evidence · 2026-11-16 KST

Functional source `2d7b0c7efb5e07b1bc299ccbeeb1608b352fe626`, branch `codex/axdev-full-verification`, base `5ab94180471c7ea86344b691fc77ad5c29989071`. The supplemental [Windows 11 report](WINDOWS11_VERIFICATION.md) pins each physical test to its checkout. [PR #3](https://github.com/hibi89/Freelancer/pull/3)

**14/20 F-ID acceptance rows PASS. Six rows have device requirements still NOT_RUN.** A row passes only when its listed behavior has evidence at its defined interface. Section 6 device trial gates are tracked separately below. Formal weighted progress is UNASSESSED. Owner real-use remains HOLD.

| ID | Status | Evidence and remaining checks |
| --- | --- | --- |
| F01 | PASS | Public plan retrieved at approved branch SHA; Git blob and local SHA256 pinned. Plan mismatch, candidate replay and unauthorized path rejected. Task and oracle immutable across restart. |
| F02 | PASS | Cycle/unknown dependency rejected; fixture queues prove VERIFIED prerequisite ordering and HOLD isolation. |
| F03 | NOT_RUN | Queue and worker locks, separate reviewer processes and serial staging exercised. The native slot recovered after abrupt exit. Physical Ollama 3B and 4B each used the single resident slot on Windows 11. Actual Windows 10 Sandbox worker lifecycle and residency remain NOT_RUN. |
| F04 | NOT_RUN | Official OpenCode rejected wider project config and enforced tool permissions in isolated WSL2. OpenCode plus native Windows 11 Ollama completed the approved edit using the local 4B model. The Windows portable executable reported 2.3.0 and standalone support. Actual Windows Sandbox model tools and paid-provider denial remain NOT_RUN. |
| F05 | PASS | Separate Git worktree in synthetic coding; sandbox snapshot and exact isolated integration ref exercised while original checkout and HEAD remained unchanged. |
| F06 | PASS | Candidate digest and allowlist, tracked test protection, Windows aliases/reparse probes, and AppContainer write denial tested. |
| F07 | PASS | Native AppContainer executes protected tests and distinct callable probes. A fake successful test process cannot make a wrong callable result pass. |
| F08 | PASS | Isolated controller rejects failed probes, loads the candidate into one repair only, HOLDs continued failure, proceeds with unrelated work and leaves dependents queued. |
| F09 | PASS | SQLite task and policy pins, proof digest, exact commit parent/tree and integration history cross-checked; forged or stale checkpoint/history resisted. |
| F10 | NOT_RUN | Windows kernel slot recovery and pre/post-promotion interruption were exercised. The Windows 11 controller exited after Git adopted the commit at `a0cd336404f8048323c83f3cabe4b07c364ee22c`. A cold process recovered the same reviewed commit with one total coding reservation and replay returned no task. The actual Sandbox and target device interruption remain NOT_RUN. |
| F11 | PASS | Actual Git commits from reviewed bytes, original ref untouched, proof and commit/tree/parent verified on resume. Forged guest and modified host proof attempts stopped. |
| F12 | PASS | Owner authorized the synthetic public write. The tool created and read back [draft PR #4](https://github.com/hibi89/Freelancer/pull/4) on the exact approved base and reviewed head. The diff contains only the reviewed fixture. Regression tests deny unpublished ancestry, implicit tag pushes and mismatched draft heads. |
| F13 | PASS | Live GitHub GET-only import at `5ab94180471c7ea86344b691fc77ad5c29989071`, blob `41fed2876b33831987384b3bcc3c96c79b7cf93e`. First run `created=true`; identical repeat `created=false`. SHA race, alternate HTTP errors and cache guards covered by regression tests. |
| F14 | PASS | Actual public EAI code `a911540fd07b72533e215849e142148327a5adbc` ran a synthetic goal in a Windows AppContainer. Exit 0, `DECIDED`, independent verifier accepted, receipt SHA256 `158281229032b62cd8ff0da3c5a43815b290ae17ab29322469f1e832093826ec`. Adapter requires the independent policy and exact goal SHA. EAI is an extra gate and cannot grant task VERIFIED. |
| F15 | PASS | Adapter produces typed nodes, dependency edges and hashes and rechecks checkpoint against current plan and SQLite; changed spec and tampered JSON rejected. Scope is the typed bridge. Native AXNODE binary import was not exercised. |
| F16 | NOT_RUN | On the Windows 11 GTX 1050 Ti, Ollama 0.40.16 Vulkan measured 31.45 tokens/s for 3B and 19.16 for 4B at 2K context. Target Windows 10, designed context, task success and manual GPT comparison remain NOT_RUN. |
| F17 | NOT_RUN | Cooperative stop/resume, durable budget, locks and status exercised. Windows 11 Task Scheduler validated and manually invoked the configured disposable queue with the exact arguments. Sandbox-disabled execution failed closed, dry run passed and the temporary task was removed. Actual owner logon and automatic target launch remain NOT_RUN. |
| F18 | NOT_RUN | The original guest receipt exploit was reproduced and fake promotion denied. The native Windows 11 AppContainer blocked protected file I/O, environment inheritance and connections to live loopback and private-interface listeners. OpenCode denied an unapproved write even with a malicious project Markdown agent granting edits. Actual Windows Sandbox mappings and network denials remain NOT_RUN. |
| F19 | PASS | Installed local GGUF `qwen3:4b-instruct` returned `SEMANTIC_PASS_LOCAL_ONLY` for a synthetic code sample. Deterministic oracle gates promotion before a semantic verdict; malformed or external model evaluations rejected. |
| F20 | PASS | Synthetic sequential fleet, approved plan checks, caps, loopback HTTP owner dashboard, CSRF and Host validation covered. Real browser on a disposable Windows 11 fixture confirmed ELIGIBLE → PAUSED → ELIGIBLE after repairing a 403 caused by the form referrer policy. Two-project CLI configure, dry-run and status passed after fixing a false nonzero exit. Metadata-only preview showed one queued task, and a single publish flag refused the write. Tests pin the GitHub host and reject receipts with a different content path or blob SHA. Owner-authorized live publication wrote the [synthetic aggregate](https://github.com/hibi89/Freelancer/blob/f8d9a109839e02911afeda9d5ca6072253f57b06/docs/axdev-queue-public-handoff.json) to the dedicated status branch. Exact commit, branch head and blob matched on read-back. |

## Separate execution gates

- The six target gates cover the Windows 10 coding worker and model residency, isolated Ollama/OpenCode permissions, abrupt VM/device interruption, hardware performance, owner logon and actual Sandbox launch/mapping/no-egress. They remain NOT_RUN. [Minimal Windows 10 run](WINDOWS11_VERIFICATION.md#remaining-windows-10-device-work)
- GitHub publication passed under the owner’s approval for synthetic outputs. F12 draft PR #4 matched reviewed head `57d282bc65d72af21d0ba8cfe1f1b0227158f6e1` and original public base `5ab94180471c7ea86344b691fc77ad5c29989071`. F20 status commit `f8d9a109839e02911afeda9d5ca6072253f57b06` changed one JSON file and read back at blob `7b67b204c97a9e95cec6a356b6cf9a3bed19fdcb`. Both fixtures were isolated from the development branch.

## Final blueprint §6 trial gates

| Gate | Evidence | Target trial |
| --- | --- | --- |
| 1. Prerequisites | Win11 preflight detected Ollama, GTX 1050 Ti and the tool-capable installed model; OpenCode absent on PATH; an official 2.3.0 portable copy was inspected separately. Windows Sandbox optional feature disabled. | NOT_RUN on Windows 10; current-host readiness FAIL. |
| 2. Safe dry run | Windows 11 scheduler queue dry run and Linux/Windows CI fixtures passed. | NOT_RUN on the target device. |
| 3. Allowed changes by the coder | Isolated WSL2 OpenCode and native Ollama 4B wrote only the approved file in a disposable Git worktree. | NOT_RUN with real OpenCode in Windows Sandbox. |
| 4. Protected tests pass and unauthorized edits HOLD | Native AppContainer checks, real OpenCode permission denials in WSL2 and independent candidate regression tests passed. | NOT_RUN for the full isolated coding path on Windows 10. |
| 5. No duplicate after replay | Live GitHub import replay and cold Windows 11 controller recovery passed. | NOT_RUN after real Sandbox interruption. |
| 6. Independent queue after HOLD | Isolated controller synthetic fixture checks one fix, HOLD, independent VERIFIED and dependent QUEUED. | NOT_RUN with the actual coding runtime. |
| 7. Performance vs manual GPT workflow | Native Windows 11 GPU inference measured for both 3B and 4B. | NOT_RUN on Windows 10 with target context, coding workloads and manual comparison. |

## Evidence and next handoff

- The baseline Linux `139 PASS`, hosted Windows `138 PASS / 1 SKIP`, and CMD fixture pass remain tied to `841f957664023ac04cb4ee9abc4870d2a11596b3`. [Baseline CI](https://github.com/hibi89/Freelancer/actions/runs/43820637531).
- At `5246d10d0492d430db5d91ea4ea1a393d37b216d`, hosted Linux passed 149/151 (2 skips) and Windows passed 150/151 (1 skip). See PR #3 checks for the final checkout with the Markdown agent hardening. The portable Windows OpenCode 2.3.0 executable SHA256 is `38153a142354634c82b5cfe6c00b19df15a71e6cf8c17ef5f5c1a4cc684a6917`. [Prior CI](https://github.com/hibi89/Freelancer/actions/runs/43841403055) · [Final CI](https://github.com/hibi89/Freelancer/pull/3/checks)
- Remaining blocker is access to the supported Windows 10 machine with an enabled Sandbox and an owner-vetted offline toolchain. Then exercise denial and real coding, interrupted runs, startup, performance and allowed publication checks. Start with the fixed disposable fixture in [Windows Sandbox runtime](WINDOWS_SANDBOX_RUNTIME.md). Keep private state, logs and test assets on the device.
- Manual High handoff should compare the final design and exact branch diff, review the scope of the independent oracle, and rerun every missing device gate. Relevant evidence is the reviewable PR and these source-linked results.
