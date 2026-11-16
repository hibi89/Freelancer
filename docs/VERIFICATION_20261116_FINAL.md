# AX Dev Factory — GitHub Actions evidence checkpoint (2026-11-16 KST)

## CI results (real hosted job, no model)

- Branch under test: `verify/axdev-queue-20261116` (draft PR #2 into isolated `tools/ax-dev-factory-local`; **not main**), head SHA `54155eb0f7715de1e690e1015817945d8360264b`.
- GitHub Actions [run 43783778986](https://github.com/hibi89/Freelancer/actions/runs/43783778986), job `axdev-python` ID `133026729467`: **completed / success**, Ubuntu Python **3.11**.
- Actual job log: `Ran 19 tests in 1.185s\nOK`, **19 PASS, 0 FAIL, 0 SKIP**. Python `compileall -q axdev scripts tests`, CLI doctor and version, generated disposable Git fixture and `DRY_RUN` all completed successfully.
- GitHub Actions [run 43783196717](https://github.com/hibi89/Freelancer/actions/runs/43783196717), prior PR #1: Python3.11 **17 PASS** before the additional one-time queue tests.

## Verified code identity across branches

GitHub `fetch_file` blob SHA comparison after copying tested files into `tools/ax-dev-factory-local`:

- `axdev/core.py`: `243ec8be4a11f3ab137c693eb9ff2bdc2b1994a3`.
- `config/opencode-local-only.json`: `7711dfe3034c5c787765c6c59ddc562b031a1635`.
- `tests/test_axdev.py` (19 tests): `55a30af31260b1faf7f0b090813e0a8514d80ad1`.
- `.github/workflows/axdev-local-tests.yml`: `51cd1df1dfd53707e4188b2154867c1590357918`.

Test-only PRs #1 and #2 were **closed without merging** after copying their tested files byte-for-byte. `main` remained at `204f70169d4c7bff2d1ad58d024a184c32360a50` in the last remote comparison.

## Covered behaviors

- Strict immutable task contracts, dependency graph, forbidden/sensitive paths and symlink fail-closed handling.
- Isolated Git worktrees, one active local model worker, independent deterministic review, one repair and HOLD.
- Cumulative local Git integration: Task B starts from Task A's verified commit, while source checkout remains untouched.
- Crash/REVIEW/PREPARED checkpoint recovery without second unbounded code-generation pass.
- Per-task OpenCode V2 edit allowlist and Ollama-only provider config (policy evaluated synthetically; actual CLI not run).
- Optional Ruff check contract (tool not installed or run in this CI).
- One-time non-overwriting local settings, generated disposable repo, CLI dry-run, no-model first test.

## Limits / no false completion

- `RUN_MODEL_TRIAL.cmd`, `RUN_QUEUE.cmd`, Windows10 on GTX1050Ti, actual Ollama and OpenCode v2 runtime, GPU/VRAM, live task success, automatic restart and autonomous GitHub PR are **NOT RUN**.
- The OpenCode permission configuration is NOT an OS sandbox. Unit tests can execute arbitrary trusted project code. Use only disposable worktrees without secrets under a non-admin account until local acceptance.
- High-authored plans can be consumed from a local file, but **automatic remote GitHub fetching/sync is NOT IMPLEMENTED**, and neither EAI nor AXNODE is integrated.
- No Prod URL/Vercel, no paid API, no user data or other repo changed. Official full-design completion remains **UNASSESSED**, no 100% claim.

## Immediate user acceptance

1. Clone this branch once and run `RUN_TRIAL.cmd` (synthetic dry-run; no live AI).
2. Confirm installed `ollama` and `opencode` V2; run `RUN_MODEL_TRIAL.cmd` (synthetic local AI run only).
3. Inspect worktree, test result, memory/VRAM/latency and permissions. If PASS, configure a **single small non-sensitive private task** with `python -m scripts.configure_queue`, then use `RUN_QUEUE.cmd`.
4. Keep real project, private plans and credentials out of the PUBLIC Freelancer repository.
