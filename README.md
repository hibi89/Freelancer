# AX Dev Factory — local personal developer, verified synthetic build

**GitHub status (2026-11-16 KST):** Python 3.11 GitHub Actions [run 43783778986](https://github.com/hibi89/Freelancer/actions/runs/43783778986) **19 PASS / 0 FAIL / 0 SKIP**. Exact verified `axdev/core.py` and local-only OpenCode policy Git blobs matched on tools branch. No real Windows/GTX1050Ti/Ollama/OpenCode inference validated. This is not a finished autonomous product.

## One-time laptop setup, shortest route

From Windows PowerShell (Git + Python 3.11+ preinstalled):

```powershell
git clone --branch tools/ax-dev-factory-local https://github.com/hibi89/Freelancer.git ax-dev-factory
cd ax-dev-factory
.\RUN_TRIAL.cmd
```

This **only** creates a disposable synthetic Git project, checks local prerequisites and dry-runs one task. Your existing projects stay untouched. Once OpenCode V2 and Ollama are installed and checked, execute **only the synthetic test**:

```powershell
.\RUN_MODEL_TRIAL.cmd
```

The live trial defaults to your previously installed `ollama/qwen3:4b-instruct` model and does not auto-download any new model. If `opencode` is missing, its official V2 npm install command is `npm install -g @opencode/cli` (manual network download, not auto-executed by this repository). Inspect the `config/opencode-local-only.json` policy and avoid running as administrator.

## Once the synthetic model trial is accepted

```powershell
python -m scripts.configure_queue --repo "C:\\path\\to\\target-git-repo" --plan "C:\\path\\to\\owner-approved-plan.json"
.\RUN_QUEUE.cmd
```

One-time settings are written under `%LOCALAPPDATA%\AXDevFactory\settings.json`, **outside GitHub**, and refuse overwrite. The queue can execute up to 100 approved tasks serially, with one local coding model, protected deterministic review, at most one repair, checkpoint/resume and isolated local Git commit integration. **No automatic remote GitHub plan fetch, push, PR or startup registration yet.** It does not need repeated chat input while its current local queue is processing. An approved plan for a private repo must remain private.

**Hard boundary:** This is not an OS security sandbox; executing imported code/tests is powerful. Only use a disposable, non-admin checkout until the exact OpenCode v2 permissions and local Ollama tool behavior pass the real Windows trial. If the model cannot solve a task, it is marked HOLD; no fabricated success.

---
> **Verified synthetic milestone (2026-11-16 KST):** Byte-identical GitHub source/test check, Linux Python3.13.5 **10/10 tests PASS**, CLI doctor/dry-run and fake-model protected-test commit PASS. [Exact evidence](docs/VERIFICATION_20261116.md). Windows/GTX1050Ti/real Ollama/OpenCode and remote GitHub PR **NOT TESTED**.

# AX Dev Factory — Personal Local Automation (v0.1)

Branch: `tools/ax-dev-factory-local` in PUBLIC `hibi89/Freelancer`. Personal-use tool, not a Kmong sales product. No secrets, client data, models, API tokens or owner files are stored here.

**Mission:** GPT-6 High defines tiny tasks once; a GTX 1050 Ti / 16GB Windows 10 notebook consumes the approved plan with one local coding model, deterministic review and a single repair attempt. No repeated chat "ㄱ" needed after the local queue is configured.

## Install/trial (no cloud AI required)

**Fastest safe Windows test:** clone this branch, then double-click `RUN_TRIAL.cmd`. It creates a disposable fixture, checks prerequisites and performs a dry-run without invoking a model. See `docs/WINDOWS_TRIAL.md` for the explicitly approved live-model test.

Prerequisites: Git, Python >=3.11, Ollama and OpenCode CLI configured to use **only a local Ollama provider**. Begin with `qwen2.5-coder:3b`; compare with installed `qwen3:4b-instruct` only after measuring. OpenCode and GPU acceleration remain **UNVERIFIED on this notebook**.

1. Clone this branch into a local folder (NOT the target project): `git clone --branch tools/ax-dev-factory-local https://github.com/hibi89/Freelancer.git ax-dev-factory`.
2. From that folder run `python -m axdev doctor --plan examples/sample-plan.json`.
3. Use a separate disposable test Git repository containing Python tests. Create an owner-reviewed plan JSON using the schema in `docs/TASK_CONTRACT.md`. Files in plan must be exact target paths.
4. `python -m axdev run --repo C:\path\to\disposable-repo --plan C:\path\to\plan.json --state C:\axdev-state --max-tasks 1` — **dry run**, no model call and no target edits.
5. Only after checking the plan, and with no sensitive content or credentials in the agent workspace: `python -m axdev run --repo C:\path\to\disposable-repo --plan C:\path\to\plan.json --state C:\axdev-state --model ollama/qwen2.5-coder:3b --max-tasks 1 --execute`.

Run tests: `python -m unittest discover -s tests -p test_axdev.py -q`.

**Current capabilities:** JSON contract/DAG validation, exact allowed paths, separate Git worktree, Ollama-only OpenCode command invocation, fixed argv acceptance checks, one retry, SQLite checkpoints and local VERIFIED Git commits. **Not yet available:** automatic GitHub plan pull, automatic push/PR, real external EAI/AXNODE adapter, scheduled auto-start, independent AI semantic review or hardened process/network sandbox. Never assume full autonomous production readiness from these initial features.

GitHub docs: [final blueprint](docs/FINAL_BLUEPRINT.md), [task contract](docs/TASK_CONTRACT.md), [coding skill](.opencode/skills/ax-coding/SKILL.md), [review skill](.opencode/skills/ax-review/SKILL.md), [recovery skill](.opencode/skills/ax-recovery/SKILL.md), STATUS.md and HANDOFF.md.

Do not run coding tests on main or an important existing product as the first trial. The current developer has no access to your personal notebook to validate local drivers, installed model or runtime performance.
