# Windows 11 physical-device verification · 2026-11-16 KST

The target acceptance baseline is **14/20 F-ID rows PASS**. F03, F04, F10, F16, F17 and F18 each retain a Windows 10 requirement marked **NOT_RUN**. The checks below supplement the baseline. [Acceptance ledger](P2_VERIFICATION_LEDGER.md) · [Observed test outputs](WINDOWS11_VERIFICATION.json)

The physical host used Windows 11 Pro build 26200, 15.8 GiB RAM and a GeForce GTX 1050 Ti with 4,096 MiB VRAM and driver 552.22. The Windows Sandbox optional feature was disabled and the standard System32 executable was absent. Native guest launch and in-guest isolation were **NOT_RUN**. Tests used disposable synthetic repositories and model prompts.

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

The measurements used temperature 0 and a 2,048-token context. Total request time includes cold loading and prompt evaluation. These were single synthetic generation samples. The 8K target and comparative task success, including the manual GPT baseline in the blueprint, remain NOT_RUN. See the [Ollama hardware documentation](https://docs.ollama.com/gpu) for driver and Vulkan support.

## OpenCode integration and defect fix

At `a0cd336404f8048323c83f3cabe4b07c364ee22c`, OpenCode 2.3.0 returned a configuration-source array with a structured model ID. The previous guard expected a single merged object with a string model ID, so it rejected even the approved configuration. [Fix commit](https://github.com/hibi89/Freelancer/commit/5246d10d0492d430db5d91ea4ea1a393d37b216d).

At `5246d10d0492d430db5d91ea4ea1a393d37b216d`, a repository's `.opencode/agents/build.md` could append an edit permission and the CLI wrote an unapproved disposable file. At [`2d7b0c7efb5e07b1bc299ccbeeb1608b352fe626`](https://github.com/hibi89/Freelancer/commit/2d7b0c7efb5e07b1bc299ccbeeb1608b352fe626), a separate hard edit policy enforces the approved file scope after the agent's own rules. Sensitive-path denies retain precedence. [OpenCode policy semantics](https://opencode.ai/docs/policies#tools)

Official OpenCode releases 2.2.6 and 2.3.0 passed in a WSL2 mount and network namespace with only private loopback. The Factory coding entry selected the intended Git worktree despite a stale inherited working directory. A deterministic Ollama protocol fixture requested an approved write, a prohibited write and a dummy `.env` read. The approved file was updated. The hard policy rejected the other write even when the repository's Markdown agent permitted it. The secret read was denied, and shell and web tools were absent. A separate project JSON override caused exit 125 before any further endpoint request.

The real model integration also passed at `2d7b0c7efb5e07b1bc299ccbeeb1608b352fe626`. OpenCode 2.3.0 ran in isolated WSL2 and reached a dedicated native Windows Ollama 0.40.16 server through a stdio relay that accepted only local model discovery and completion requests for the pinned 4B model. The GTX 1050 Ti increased VRAM usage by 2,565 MiB. The model changed only `probe.py` and the resulting bytes matched the target. The protected file and original checkout stayed unchanged. Both processes exited and the dedicated server stopped.

## Remaining Windows 10 device work

1. On the target Windows 10 machine with Windows Sandbox already enabled, pin the offline runtime and models. Run `RUN_TRIAL.cmd` and `RUN_MODEL_TRIAL.cmd` on a fresh fixture. Record real OpenCode tool edits, the independent verdict and exact commit. Exercise guest network and mapping denials, paid-provider denial, protected paths, a forged receipt, one repair followed by HOLD, an independent task and replay. [Sandbox runtime guide](WINDOWS_SANDBOX_RUNTIME.md)
2. On a disposable queue, exercise actual Sandbox interruption and restart across Git promotion. Confirm the startup task at an owner logon, along with the budget and lock. Check that the same reviewed commit is recovered and coding is never duplicated.
3. Compare 3B and 4B workloads on the target GTX 1050 Ti with the target context, one model resident at a time. Record tool support, driver/backend, RAM, VRAM, latency, throughput, independent task success and the manual GPT comparison.
