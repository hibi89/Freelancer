# Windows 11 physical-device verification · 2026-11-17 KST

The earlier acceptance baseline was **14/20 F-ID rows PASS**. F03, F04, F10, F16, F17 and F18 retain Windows 10 device checks marked **NOT_RUN**. [Acceptance ledger](P2_VERIFICATION_LEDGER.md) · [Observed test outputs](WINDOWS11_VERIFICATION.json)

The physical host used Windows 11 Pro build 26200, an Intel Core i7-8750H, 15.8 GiB RAM and a GeForce GTX 1050 Ti with 4,096 MiB VRAM and driver 552.22. The owner authorized enabling Windows Sandbox and one restart. The actual guest ran build 26100. Tests used disposable synthetic repositories and model prompts.

## Native Windows Sandbox lifecycle

- **Coding and independent approval.** Windows OpenCode 2.3.0 and Ollama 0.40.16 ran pinned `qwen3:4b-instruct` offline. The guest returned only the two approved files. A host AppContainer ran one protected project check and two independent probes before Git accepted commit `d63d29d2176b4ea0e5b32534e53f1c790036fec9`. The controller exited at the injected crash after Git adopted the commit and before SQLite recorded verification. A new process recovered the same commit with one total coding reservation. The original checkout remained clean. Source `e9572001907bababd3dd051be41ff69217f298c2`.
- **Guest isolation.** The read-only input and bundle allowed reads and denied writes. A file outside the mapped folders was invisible. The guest reached its own loopback service, had no IPv4 default route and could not reach a TCP listener that the host independently reached. The test closed its exact Sandbox instance.
- **On-device resource use.** The observer saw one resident model, with 3,186,108,660 bytes reported by Ollama. The guest had 6,143 MiB total and 1,053 MiB available at the sample. Its context was 4,096 and its VRAM allocation was zero with vGPU disabled. The 8K GPU comparison below was measured on the host.
- **Actual login.** On the approved restart, the Windows logon trigger invoked the exact configured queue at least privilege. The first run returned `HOLD` while Ollama attempted to update a read-only model store. The temporary scheduled task was removed. The guest model store now uses a writable copy inside the VM.
- **Same-task manual reference.** One GPT-authored patch applied by Codex in a separate worktree changed the same two files and passed the same one check and two independent probes. Task read to verdict took 93.538 seconds. The native Sandbox attempt took 347.8 seconds from run creation to candidate. The timings cover different intervals, including machine and tool overhead.

The Windows 11 launch now pins the instance ID to the host's run record. The host closes that exact instance when the guest publishes a result and reads the candidate after closure. The Windows 10 launcher remains available. [Runtime source](https://github.com/hibi89/Freelancer/commit/31ff8b9a02ace6748f5cc39153e156c86d1ac8f3)

The live queue rejected the candidate and its one repair, recorded HOLD and resumed without a new call for the held task. The dependent remained queued. The independent next task reached VERIFIED at `9aca791fc5cce5fca55203e76f3e63d56b2a2e49`. The external-provider canary refused `openai/gpt-4o` before any observed network-call error. The controller force-stopped its exact native Sandbox before a receipt and recorded HOLD. An earlier combined canary timed out. The separate abort fixture established the final result. The final native source was `448fcc34bb328b179f314af62c0d14afc94fc0a5`. [Linux and Windows CI](https://github.com/hibi89/Freelancer/actions/runs/43977508805)

## Native Windows 11 observations

Tested checkout [`a0cd336404f8048323c83f3cabe4b07c364ee22c`](https://github.com/hibi89/Freelancer/commit/a0cd336404f8048323c83f3cabe4b07c364ee22c).

| Check | Result | Observation |
| --- | --- | --- |
| AppContainer reviewer (F18) | PASS | A capability-free process could neither read nor write a protected canary. Its private environment marker was absent. Both loopback and a private virtual adapter listener were reachable by the parent, and connection attempts by the reviewer timed out. The protected bytes stayed unchanged. |
| Abrupt controller exit and cold restart (F10) | PASS | The controller exited with code 73 after promotion of the Git ref and before saving VERIFIED. SQLite retained PREPARED. A fresh process accepted the same reviewed commit. Replay returned no task, the coding reservation count was one and the original checkout stayed unchanged. This used a synthetic coding response and the native AppContainer reviewer. |
| Owner task definition and manual scheduler invocation (F17) | PASS | The actual Task Scheduler validated the generated least-privilege XML. A disposable manually invoked copy used the exact configured queue arguments. Execution returned 1 before creating runtime state when Sandbox was unavailable. Dry run returned 0 and DRY_RUN. The temporary task was removed and its absence was checked. Owner logon and automatic restart were NOT_RUN. |
| Real local inference and model residency (F03, F04, F16) | PASS | A separate native Ollama 0.40.16 process used only localhost, one model slot, one request slot and Vulkan. Both models generated 128 tokens. Ollama's resident model report and NVIDIA's VRAM measurements confirmed GPU use. Each model unloaded before the next check and the dedicated server stopped. |

| Model | Eval tokens/s | Total request time | NVIDIA VRAM increase | Available RAM before → after |
| --- | ---: | ---: | ---: | ---: |
| `qwen2.5-coder:3b` | 31.45 | 12.010 s | 1,998 MiB | 3,366 → 1,115 MiB |
| `qwen3:4b-instruct` | 19.16 | 20.018 s | 2,564 MiB | 2,840 → 965 MiB |

These single generation samples used temperature 0 and a 2,048-token context. Total request time includes cold loading and prompt evaluation. See the [Ollama hardware documentation](https://docs.ollama.com/gpu) for driver and Vulkan support.

### 8K context on the physical GTX 1050 Ti

At [`8bd8267c32791c185d505843aba351d6b1878656`](https://github.com/hibi89/Freelancer/commit/8bd8267c32791c185d505843aba351d6b1878656), native Ollama allocated **8,192 tokens** for each pinned model. Each evaluated a long synthetic prompt, generated 128 tokens, and unloaded before the other model ran. Both reported tool support. [Allocated context fields](https://docs.ollama.com/api/ps) · [Generation timing fields](https://docs.ollama.com/api/generate)

| Model | Evaluated input tokens | Eval tokens/s | Total request time | NVIDIA VRAM increase | Available RAM before → after |
| --- | ---: | ---: | ---: | ---: | ---: |
| `qwen2.5-coder:3b` | 6,948 | 28.06 | 55.704 s | 2,227 MiB | 5,070 → 2,634 MiB |
| `qwen3:4b-instruct` | 6,927 | 4.42 | 99.830 s | 2,570 MiB | 5,016 → 1,818 MiB |

The 4B response reproduced a marker placed at the beginning of the long prompt. The 3B response missed it. Both performance measurements came from a single observed run. The Windows 10 benchmark remains NOT_RUN.

Runtime SHA [`2882e4c56a3a142df3e96beee1fddaa6a55b3756`](https://github.com/hibi89/Freelancer/commit/2882e4c56a3a142df3e96beee1fddaa6a55b3756) pins the Windows Sandbox Ollama launch to one resident model and one active request. A regression check confirmed both limits override inherited values at process start. Guest behavior on Windows 10 remains NOT_RUN. [Ollama concurrency settings](https://docs.ollama.com/faq#how-does-ollama-handle-concurrent-requests)

## OpenCode integration and defect fix

At `a0cd336404f8048323c83f3cabe4b07c364ee22c`, OpenCode 2.3.0 returned a configuration-source array with a structured model ID. The previous guard expected a single merged object with a string model ID, so it rejected even the approved configuration. [Fix commit](https://github.com/hibi89/Freelancer/commit/5246d10d0492d430db5d91ea4ea1a393d37b216d).

At `5246d10d0492d430db5d91ea4ea1a393d37b216d`, a repository's `.opencode/agents/build.md` could append an edit permission and the CLI wrote an unapproved disposable file. At [`2d7b0c7efb5e07b1bc299ccbeeb1608b352fe626`](https://github.com/hibi89/Freelancer/commit/2d7b0c7efb5e07b1bc299ccbeeb1608b352fe626), a separate hard edit policy enforces the approved file scope after the agent's own rules. Sensitive-path denies retain precedence. [OpenCode policy semantics](https://opencode.ai/docs/policies#tools)

Official OpenCode releases 2.2.6 and 2.3.0 passed in a WSL2 mount and network namespace with only private loopback. The Factory coding entry selected the intended Git worktree despite a stale inherited working directory. A deterministic Ollama protocol fixture requested an approved write, a prohibited write and a dummy `.env` read. The approved file was updated. The hard policy rejected the other write even when the repository's Markdown agent permitted it. The secret read was denied, and shell and web tools were absent. A separate project JSON override caused exit 125 before any further endpoint request.

The real model integration also passed at `2d7b0c7efb5e07b1bc299ccbeeb1608b352fe626`. OpenCode 2.3.0 ran in isolated WSL2 and reached a dedicated native Windows Ollama 0.40.16 server through a stdio relay that accepted only local model discovery and completion requests for the pinned 4B model. The GTX 1050 Ti increased VRAM usage by 2,565 MiB. The model changed only `probe.py` and the resulting bytes matched the target. The protected file and original checkout stayed unchanged. Both processes exited and the dedicated server stopped.

The same disposable coding prompt with the pinned 3B model at `2882e4c56a3a142df3e96beee1fddaa6a55b3756` was **FAIL**. OpenCode exited 0 and the model completed requests. The worktree had an empty diff and the expected bytes were absent. The original checkout and protected file stayed unchanged. This was one direct coding attempt. [Both coding observations](WINDOWS11_VERIFICATION.json)

## Remaining Windows 10 device work

1. On the target Windows 10 machine with Windows Sandbox already enabled, pin the offline runtime and models. Run `RUN_TRIAL.cmd` and `RUN_MODEL_TRIAL.cmd` on a fresh fixture. Record real OpenCode tool edits, the independent verdict and exact commit. Exercise guest network and mapping denials, paid-provider denial, protected paths, a forged receipt, one repair followed by HOLD, an independent task and replay. [Sandbox runtime guide](WINDOWS_SANDBOX_RUNTIME.md)
2. On a disposable queue, exercise actual Sandbox interruption and restart across Git promotion. Confirm the startup task at an owner logon, along with the budget and lock. Check that the same reviewed commit is recovered and coding is never duplicated.
3. Compare 3B and 4B workloads on the target GTX 1050 Ti with the target context, one model resident at a time. Record tool support, driver/backend, RAM, VRAM, latency, throughput, independent task success and the manual GPT comparison.
