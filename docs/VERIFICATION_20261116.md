# AX Dev Factory — exact-source synthetic verification (2026-11-16 KST)

**Outcome:** local synthetic verification **PASS**, full Windows + real local LLM **NOT_RUN**. No personal project, customer data, paid API, GitHub main or other product branches touched.

## Verified exact remote blobs

The following GitHub branch files were fetched, reconstructed byte-for-byte in an isolated Linux working directory, and matched via `git hash-object` before running tests:

| Path | Exact Git blob SHA | Outcome |
|---|---|---|
| `axdev/core.py` | `c3138a301b97fa3b5916e46258f6732ce6341bd5` | Exact match; AST parse PASS |
| `tests/test_axdev.py` | `ac5d668cf276d5ee0596988b9e0f99e4759a5bf3` | Exact match |
| `axdev/__main__.py` | `3d52d145187612397d647ca30904e518055024ae` | Exact match |
| `scripts/prepare_trial.py` | `f007d75aa19853d08c6151081454e7b2bba0750b` | Exact match |

Local runtime: Linux, Python **3.13.5**; Git installed. OpenCode and Ollama executables NOT installed in the verification container. Windows 10 / Python 3.11.9, GTX1050Ti/GPU, real model and actual user projects were NOT RUN.

## Commands and evidence

- `python -m compileall -q axdev tests` → PASS.
- `python -m unittest discover -s tests -p test_axdev.py -v` → **10 passed / 0 failed / 0 skipped** (3.875s).
- `python scripts/prepare_trial.py --output <new isolated test directory>` → synthetic Git repo, protected tests and plan created; no overwrite.
- `python -m axdev doctor --plan <trial-plan>` → PASS, reports model_verified=false and gpu_verified=false.
- `python -m axdev run --repo <trial-repo> --plan <trial-plan> --state <state>` → DRY_RUN, QUEUED unchanged.
- Injected fake local coder on protected `TRIAL-001`: code generated in separate worktree; 2 protected test assertions pass; returned VERIFIED with ephemeral local commit `20e02cd39af0afaea86c4dfd7bc72ee530f8b79a`; original checkout untouched; repeated attempt returns NO_READY_TASK.
- GitHub Actions workflow was added. Its hosted job outcome could not be confirmed through the available GitHub connector; **CI status UNVERIFIED**. Local exact-source test is NOT a remote CI success claim.

## Critical gaps before unattended real-code use

1. User notebook's exact OpenCode v2 policy behavior; local Ollama-only provider and OS/network sandbox boundary; model tool-edit success.
2. Actual Windows 10 PowerShell/CMD encoding, Git identity and worktree behavior, 1050Ti driver/VRAM/RAM, time-per-task.
3. Remote GitHub task synchronization, authorized PR upload, true independent AI semantic reviewer, auto scheduler and safe credential separation.
4. EAI/AXNODE actual adapters; these are not connected in v0.1.

No official total completion score is assigned. This test proves a bounded synthetic local state machine, not GPT-6/Codex-equivalent coding capacity or autonomous product completion.
