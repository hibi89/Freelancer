# AX Dev Factory — Requirements

**Scope:** Personal local automation, NOT Kmong productization. Owner's goals: no recurring chat input, High task decomposition once per product, local free repeated coding, shared immutable coding/review criteria, one repair, fail-closed security, progress evidence preserved in GitHub, notebook GTX 1050 Ti / RAM16GB / Windows10.

**Early-use MVP:** F01–F11 from [FINAL_BLUEPRINT](docs/FINAL_BLUEPRINT.md), with isolated Git worktree and independent deterministic check runner. No sellable package, Vercel, GUI, extra cloud model or full native EAI/AXNODE refactor. Real Windows execution and actual Qwen model not yet validated.

**System contract:** `examples/sample-plan.json`, spec in [TASK_CONTRACT](docs/TASK_CONTRACT.md). One AI coding invocation at a time; review controller runs programmatic checks from approved allowlist; model cannot mark its own work verified. Start next task only if independent of any failed prerequisite.

**State contract:** QUEUED → CODING → REVIEW → VERIFIED / HOLD. One fix attempt after first failed review, then HOLD. Each task binds to SHA256 of its immutable approved spec; changed specs require manual reconciliation. Do not corrupt/overwrite originals on crash.

**Deployment/security:** Local only, Python >=3.11, SQLite stdlib, Git + separately installed OpenCode and Ollama. No paid API required; model license, installed driver, speed, actual offline guarantees and OpenCode permissions must be verified locally. No automatic git push/PR, root permissions or arbitrary commands in v0.1.

**Target full requirements:** F01–F20 in FINAL_BLUEPRINT.md. User owner approval required for scope and official weights. Current engineering readiness is partial and official completion UNASSESSED.
