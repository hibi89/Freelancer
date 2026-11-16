# AX Dev Factory — Personal Local Autonomous Development System

**Date:** 2026-11-16 KST. **Type:** owner-only internal productivity tool; NOT a Kmong product. **Canonical repo:** hibi89/Freelancer, branch tools/ax-dev-factory-local. **Formal total completion:** UNASSESSED until owner-approved weights and real acceptance evidence. **Deployment:** local Windows10/11, no Vercel.

> **Current evidence refresh 2026-11-16 KST:** Evidence column updated against tested source `50dc2acb506f74f8330a25bb89c4e00fba3e1b56`; requirements/weights unchanged. Formal completion UNASSESSED; provisional 72/100 readiness, owner Windows model NOT_RUN. See [scorecard](../docs/PROGRESS_SCORECARD.md).

## 1. User-approved mission

Stop repeating web ChatGPT "ㄱ" and switching chats. GPT-6 High defines explicit tiny implementation contracts in GitHub; GTX1050Ti/16GB Windows PC consumes them without requiring further chat input, uses one local Ollama coder at a time, independently reviews each completed job against the SAME fixed contract, issues one bounded fix, holds failures, and continues unrelated tasks. Checkpoints survive interrupted sessions. Source code, requirement/goal history and proof live in GitHub; runtime state/logs remain local.

## 2. Alternative selection

A. Deeply redesign EAI + AXNODE before automation: stronger long-term native ownership but substantial integration risk, slower first useful test.
B. Lightweight Python stdlib + SQLite + OpenCode (local Ollama) and Git worktrees: faster proof and smaller resource footprint, but local coding quality limited by 3B/4B models.
**Select B for initial personal implementation.** EAI and AXNODE are future adapters, not hard dependencies or silently modified sources. AXNODE's own independently approved A-format remains intact.

## 3. Contract and lifecycle

GitHub approved blueprint → GPT-6 High micro-task plan (immutable task ID, goal, exact allowed files, dependencies, protected tests) → local queue → separate Git worktree → Ollama-only OpenCode coding → deterministic independent review → one repair if failed → review again → local verified commit → optionally authorized GitHub PR → STATUS/HANDOFF evidence → next ready task.

Do not start dependent tasks until their prerequisites are VERIFIED. Repeated bad model calls do not consume the entire queue; independent items proceed. A malicious or broken prompt cannot authorize new scopes, secret exfiltration, paid APIs, push, deployment, permission changes, force push or deleting originals.

## 4. V1 target acceptance matrix (requirements are full target, not proof of implementation)

| ID | Requirement | Current evidence |
|---|---|---|
| F01 | GitHub source-first High task contract with stable IDs/allowed file paths | Strict approved JSON task parser plus read-only SHA-pinned public import; automatic new task decomposition not implemented |
| F02 | Dependency graph validation, no cycles/unknown IDs | Verified by Linux hosted synthetic tests; Windows not run |
| F03 | One coding worker, one test reviewer, no second model residency | Serial queue and worker-lock synthetic tests PASS, GPU residency untested |
| F04 | Local Ollama provider only, no paid external LLM API | Static provider allowlist + resolved V2 config guard tested synthetically; real host/network isolation unverified |
| F05 | Isolated Git worktree, original checkout unchanged | Separate worktree & original checkout preservation hosted synthetic PASS; Windows pending |
| F06 | Exact allowed changed paths and fail-closed unsafe modifications | Post-test path/content hash guard blocks generated artifacts & mutations; Linux PASS, Windows pending |
| F07 | Independent deterministic acceptance commands | Linux hosted acceptance test PASS, task checks allowlisted; real-world acceptance unverified |
| F08 | At most one fix attempt, then HOLD | One bounded repair, HOLD and independent task continuation in hosted synthetic tests |
| F09 | Persistent SQLite state and task-spec SHA | SQLite spec SHA and checkpoints validated synthetic; Windows power-loss unverified |
| F10 | Resume incomplete worktree safely | PREPARED, REVIEW, interrupted CODING recovery and cooperative stop tested; Windows crash E2E pending |
| F11 | Verified local commit and SHA-backed evidence | Git worktree local SHA-backed commits verified synthetic, no real owner PR |
| F12 | GitHub push/PR with auth and branch protection | Preview and two-flag draft PR publisher implemented/tested offline; actual remote authorization/push NOT_RUN |
| F13 | GitHub source/task synchronization without duplicate execution | Public read-only GitHub SHA-pinned import actually live-tested once; local cache and idempotency tested; continuous new plans still gated |
| F14 | EAI independent cognition/evidence adapter | NOT IMPLEMENTED |
| F15 | AXNODE checkpoint/typed graph adapter | NOT IMPLEMENTED |
| F16 | Windows10 GTX1050Ti + Ollama 3B/4B speed/RAM benchmarks | Localhost synthetic benchmark code + test ready; actual Windows10 GTX1050Ti benchmark NOT_RUN |
| F17 | Startup scheduler, process lock, rate/budget control, daily status | Single-worker lock, bounded queue, stop/resume and runtime events implemented; Windows startup scheduling NOT_IMPLEMENTED |
| F18 | Security isolation, secret handling and repository trust review | Reviewed path/contract guards + merged V2 policy fail-closed check; actual OS/network sandbox NOT_IMPLEMENTED |
| F19 | AI semantic review beyond scripted tests | NOT IMPLEMENTED |
| F20 | Multi-project queue, PR/status/handoff sync, owner approval UI | Locally approved serial 1..10 project fleet synthetic PASS; remote status/owner UI NOT_IMPLEMENTED |

No 100% completion claim from CI unit PASS alone. Productization, commercialization, public cloud deployment and third-party customer files explicitly out of scope.

## 5. Performance / safety policy

- Start with `ollama/qwen2.5-coder:3b` vs installed `qwen3:4b-instruct`, compare real throughput & task success. 8K context target; increase only after measuring. One model call at a time.
- CPU validation may run while a **different** task is coding later, only after separate reviewer isolation is implemented; v0.1 does both sequentially for correctness and memory safety.
- Python 3.11 standard library. Exact argv check allowlist. No arbitrary task-command execution or shell=True.
- Model can issue local code tool calls; **v0.1 OpenCode is not an OS security sandbox**. Use a trusted non-admin Windows account and disposable clone. Do not give the agent secrets.
- Local state outside target project. No auto-push, delete, deployment, remote customer file exchange or paid API.
- Windows Defender, signing, driver compatibility, actual Ollama/OpenCode versions and real code success require host verification.

## Verified checkpoint — 2026-11-16 KST

Exact Git blob matches for runtime, CLI, test suite and synthetic trial generator, then Linux Python3.13.5 **10 PASS / 0 FAIL / 0 SKIP** and fake local coder E2E with protected tests/isolated Git commit PASS. No real Ollama/OpenCode, owner Windows10 GTX1050Ti, GitHub hosted CI or real user repository acceptance yet. See [verification details](VERIFICATION_20261116.md). Official full-product score remains UNASSESSED.

## Implemented decision and hosted CI checkpoint — 2026-11-16 KST

- **Fixed personal-use architecture:** High-approved immutable tasks (Spec Kit planning discipline), Python/SQLite scheduler/controller, one OpenCode V2 coder using a local Ollama model, selected original TDD/diagnostic steps aligned to Superpowers, independent Python acceptance tests with optional Ruff, and optional agent-browser only for approved web UI tasks. EAI and AXNODE are separate future adapters; no new independent model or remote paid service.
- **New safety and correctness:** local integration ref is separate from target main and advances only after independent acceptance; subsequent tasks start from latest verified code. PREPARED commit recovery and interrupted CODING review; nested-sensitive/symlink path rejection; per-task V2 edit permission scope; Ollama provider allowlist; scrub inherited secret environment keys (still not an OS sandbox).
- **One-time local operation:** `RUN_TRIAL.cmd` no-model synthetic; `RUN_MODEL_TRIAL.cmd` local-only synthetic once; then `scripts.configure_queue` stores private repo/plan paths outside GitHub and `RUN_QUEUE.cmd` runs up to 100 queued tasks without repeated `ㄱ` while the current local plan is executing.
- **Remote evidence:** GitHub Actions [run 43783778986](https://github.com/hibi89/Freelancer/actions/runs/43783778986) Ubuntu Python3.11 **19 PASS / 0 FAIL / 0 SKIP**, compileall, CLI and disposable fixture/dry-run PASS. [Exact source blob and test evidence](VERIFICATION_20261116_FINAL.md).
- **Not implemented/tested:** actual user's Windows10/GTX1050Ti Ollama/OpenCode trial, true OS network/process sandbox, secure automatic GitHub remote plan sync and PR, restart scheduler, EAI/AXNODE adapters, AI semantic review, browser or desktop UI integration, multi-project benchmarks. Official whole-blueprint completeness **UNASSESSED**; no release/production claim.
- **Avoid install explosion:** Ruff opt-in check, not a mandatory download; Graphify/Qwen Code/agent-desktop remain A/B or specialized future options. Installing all trending projects would add cost/complexity without proving local model coding quality.

## 6. Acceptance for first live trial

(1) `python -m axdev doctor` shows prereqs. (2) sample plan dry run leaves target untouched. (3) on a disposable fixture Git repo, coder creates only two allowed files. (4) protected tests PASS; unauthorized file edits HOLD. (5) replay prevents duplicate task. (6) queue handles independent next task after HOLD. (7) performance metrics are recorded and compared to manual GPT workflow.

Only after these pass, target a non-sensitive existing Kmong code repo and a single High-approved small issue. Runtime execution on user's Windows laptop cannot be validated through this GitHub-only session.
