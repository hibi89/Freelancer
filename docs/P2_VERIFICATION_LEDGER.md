# AX Dev Factory P2 acceptance evidence · 2026-11-17 KST

Functional source `448fcc34bb328b179f314af62c0d14afc94fc0a5`, branch `codex/axdev-full-verification`, base `5ab94180471c7ea86344b691fc77ad5c29989071`. The supplemental [Windows 11 report](WINDOWS11_VERIFICATION.md) pins each physical test to its checkout. [PR #3](https://github.com/hibi89/Freelancer/pull/3)

**Windows 11 field acceptance passed 20/20 F-ID rows (100% by row count).** The earlier checkpoint passed 14/20. The six Windows 10 device checks remain NOT_RUN. Formal weighted completion remains UNASSESSED.

| ID | Windows 11 status | Evidence |
| --- | --- | --- |
| F01 | PASS | Public plan retrieved at approved branch SHA; Git blob and local SHA256 pinned. Plan mismatch, candidate replay and unauthorized path rejected. Task and oracle immutable across restart. |
| F02 | PASS | Cycle/unknown dependency rejected; fixture queues prove VERIFIED prerequisite ordering and HOLD isolation. |
| F03 | PASS | The sandbox ran one resident Ollama 4B model under its guest account. Separate host AppContainers performed project checks and independent probes before promotion. Native locking and the one-request limit have regression coverage. |
| F04 | PASS | Native Windows OpenCode 2.3.0 and Ollama 0.40.16 completed approved offline edits. In the no-egress Sandbox, OpenCode rejected the requested external model and the canary observed no network-call error. The earlier 3B coding result remains FAIL. |
| F05 | PASS | Separate Git worktree in synthetic coding; sandbox snapshot and exact isolated integration ref exercised while original checkout and HEAD remained unchanged. |
| F06 | PASS | Candidate digest and allowlist, tracked test protection, Windows aliases/reparse probes, and AppContainer write denial tested. |
| F07 | PASS | Native AppContainer executes protected tests and distinct callable probes. A fake successful test process cannot make a wrong callable result pass. |
| F08 | PASS | The real 4B candidate failed an independent oracle. One repair also failed, so the task entered HOLD. An unrelated task subsequently verified and the dependent task stayed queued without a model call. |
| F09 | PASS | SQLite task and policy pins, proof digest, exact commit parent/tree and integration history cross-checked; forged or stale checkpoint/history resisted. |
| F10 | PASS | After a real guest edit and independent approval, the controller exited after Git adopted the commit and before SQLite recorded VERIFIED. A fresh controller recovered the same commit with one total coding reservation. A separate exact-ID Sandbox was force-stopped before publishing a candidate and remained HOLD. |
| F11 | PASS | Actual Git commits from reviewed bytes, original ref untouched, proof and commit/tree/parent verified on resume. Forged guest and modified host proof attempts stopped. |
| F12 | PASS | Owner authorized the synthetic public write. The tool created and read back [draft PR #4](https://github.com/hibi89/Freelancer/pull/4) on the exact approved base and reviewed head. The diff contains only the reviewed fixture. Regression tests deny unpublished ancestry, implicit tag pushes and mismatched draft heads. |
| F13 | PASS | Live GitHub GET-only import at `5ab94180471c7ea86344b691fc77ad5c29989071`, blob `41fed2876b33831987384b3bcc3c96c79b7cf93e`. First run `created=true`; identical repeat `created=false`. SHA race, alternate HTTP errors and cache guards covered by regression tests. |
| F14 | PASS | Actual public EAI code `a911540fd07b72533e215849e142148327a5adbc` ran a synthetic goal in a Windows AppContainer. Exit 0, `DECIDED`, independent verifier accepted, receipt SHA256 `158281229032b62cd8ff0da3c5a43815b290ae17ab29322469f1e832093826ec`. Adapter requires the independent policy and exact goal SHA. EAI is an extra gate and cannot grant task VERIFIED. |
| F15 | PASS | Adapter produces typed nodes, dependency edges and hashes and rechecks checkpoint against current plan and SQLite; changed spec and tampered JSON rejected. Scope is the typed bridge. Native AXNODE binary import was not exercised. |
| F16 | PASS | The physical GTX 1050 Ti processed both pinned models at 8,192-token context. Throughput was 28.06 tokens/s for 3B and 4.42 for 4B. The 4B model created the approved native files. The 3B coding trial lacked the required edit. The report records memory and a same-contract manual GPT reference. |
| F17 | PASS | An actual Windows 11 restart and login invoked the least-privilege temporary task with the exact approved queue arguments. The first runtime returned a safe HOLD, and the task was removed. The production runtime and persisted states were verified after the guest startup fix. |
| F18 | PASS | Native Windows Sandbox blocked writes to input and bundle, access to an unmapped host file and TCP to a reachable host listener. Guest loopback worked. Host AppContainers authorize Git promotion through independent probes. Receipt forgery regressions passed. |
| F19 | PASS | Installed local GGUF `qwen3:4b-instruct` returned `SEMANTIC_PASS_LOCAL_ONLY` for a synthetic code sample. Deterministic oracle gates promotion before a semantic verdict; malformed or external model evaluations rejected. |
| F20 | PASS | Synthetic sequential fleet, approved plan checks, caps, loopback HTTP owner dashboard, CSRF and Host validation covered. Real browser on a disposable Windows 11 fixture confirmed ELIGIBLE → PAUSED → ELIGIBLE after repairing a 403 caused by the form referrer policy. Two-project CLI configure, dry-run and status passed after fixing a false nonzero exit. Metadata-only preview showed one queued task, and a single publish flag refused the write. Tests pin the GitHub host and reject receipts with a different content path or blob SHA. Owner-authorized live publication wrote the [synthetic aggregate](https://github.com/hibi89/Freelancer/blob/f8d9a109839e02911afeda9d5ca6072253f57b06/docs/axdev-queue-public-handoff.json) to the dedicated status branch. Exact commit, branch head and blob matched on read-back. |

## Separate execution gates

- Windows 10 field gates for F03, F04, F10, F16, F17 and F18 remain NOT_RUN. [Minimal Windows 10 run](WINDOWS11_VERIFICATION.md#remaining-windows-10-device-work)
- GitHub publication passed under the owner’s approval for synthetic outputs. F12 draft PR #4 matched reviewed head `57d282bc65d72af21d0ba8cfe1f1b0227158f6e1` and original public base `5ab94180471c7ea86344b691fc77ad5c29989071`. F20 status commit `f8d9a109839e02911afeda9d5ca6072253f57b06` changed one JSON file and read back at blob `7b67b204c97a9e95cec6a356b6cf9a3bed19fdcb`. Both fixtures were isolated from the development branch.

## Final blueprint §6 trial gates

| Gate | Windows 11 evidence |
| --- | --- |
| Prerequisites | PASS. Physical device and version-pinned offline bundle used successfully. |
| Dry run | PASS. Disposable queue preserved the original checkout. |
| Approved coding scope | PASS. Native 4B OpenCode created exactly the two permitted files. |
| Protected tests and scope enforcement | PASS. Host AppContainers approved valid changes and held the failed independent oracle after one repair. |
| Safe replay | PASS. The interrupted Git/SQLite promotion recovered its exact commit without another coding call. |
| Queue continuation | PASS. The independent task verified and the held-dependent task remained queued. |
| Performance comparison | PASS. Physical host 8K measurements and the manual GPT reference are recorded with their individual sample scopes. |

## Evidence and next handoff

- The baseline Linux `139 PASS`, hosted Windows `138 PASS / 1 SKIP`, and CMD fixture pass remain tied to `841f957664023ac04cb4ee9abc4870d2a11596b3`. [Baseline CI](https://github.com/hibi89/Freelancer/actions/runs/43820637531).
- At `5246d10d0492d430db5d91ea4ea1a393d37b216d`, hosted Linux passed 149/151 (2 skips) and Windows passed 150/151 (1 skip). See PR #3 checks for the final checkout with the Markdown agent hardening. The portable Windows OpenCode 2.3.0 executable SHA256 is `38153a142354634c82b5cfe6c00b19df15a71e6cf8c17ef5f5c1a4cc684a6917`. [Prior CI](https://github.com/hibi89/Freelancer/actions/runs/43841403055) · [Final CI](https://github.com/hibi89/Freelancer/pull/3/checks)
- The final runtime SHA `448fcc34bb328b179f314af62c0d14afc94fc0a5` passed Linux with 155 tests and 2 skips and Windows with 156 tests and 1 skip. [Linux and Windows CI](https://github.com/hibi89/Freelancer/actions/runs/43977508805) · [Blueprint evidence check](https://github.com/hibi89/Freelancer/actions/runs/43977498171)
- The High reviewer can compare the final runtime diff against the approved queue, machine evidence and exact CI run. The remaining platform work is the retained Windows 10 device matrix.
