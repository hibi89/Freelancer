# Windows 10 / GTX1050Ti owner-only test instructions

This branch is PUBLIC; never publish secrets, private code, customer data, API keys, local state or Ollama model weights to it.

## Stage 0 — dry run (no model execution)

Prerequisites: Git and Python 3.11+. Clone the named branch to a new folder:
- \`git clone --branch tools/ax-dev-factory-local https://github.com/hibi89/Freelancer.git ax-dev-factory\`
- \`cd ax-dev-factory\`
- \`RUN_TRIAL.cmd\`

The batch creates a synthetic Git repository at \`%USERPROFILE%\AXDEV_TRIAL\`, one approved task plan and a separate SQLite/worktree state directory. It runs a safe CLI doctor and dry run. Re-running does not overwrite that directory. No GitHub push or user-project editing occurs.

## Stage 1 — inspect free local coding engine

OpenCode V2 (as of 2026-11): \`npm install -g @opencode/cli\` using an already-installed Node.js. Installation downloads packages; never run an unknown installer unattended. Ollama: \`ollama list\`; if needed, after reviewing disk/network availability, \`ollama pull qwen2.5-coder:3b\` (about 1.9GB model file). Check \`nvidia-smi\` and updated GPU driver; a GTX1050Ti may fall back to CPU. Model memory, speed and end-to-end tool support are untested.

Controller uses \`config/opencode-local-only.json\` and passes it through environment variables; verify your exact OpenCode version honors provider and permission policies before running on sensitive code. The controller also forbids all remote providers by name, but model-name restrictions are NOT an operating-system network sandbox.

## Stage 2 — explicit live local model trial

From the AX Dev Factory checkout, first inspect the synthetic repository, immutable protected test and \`trial-plan.json\`. Then run:

\`\`\`powershell
python -m axdev run --repo "$env:USERPROFILE\AXDEV_TRIAL\trial-repo" --plan "$env:USERPROFILE\AXDEV_TRIAL\trial-plan.json" --state "$env:USERPROFILE\AXDEV_TRIAL\state" --model ollama/qwen2.5-coder:3b --max-tasks 1 --execute
\`\`\`

Expected only if successful: local \`VERIFIED\` commit on branch \`axdev/TRIAL-001\` inside a separate worktree and two pre-existing protected tests PASS. Model errors, unauthorized paths and failed checks should result in HOLD. No automatic GitHub push/PR, no release or real customer task is executed.

## After smoke

Record Python, Git, OpenCode and Ollama versions, whether GPU or CPU used, peak RAM/VRAM, wall time, test status and commit SHA. Do NOT mark a product 100% from this synthetic check. Only move to a small non-sensitive actual project task after the controlled trial, permission validation and source-protection checks.
