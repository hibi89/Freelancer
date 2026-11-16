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
