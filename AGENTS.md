# AX Dev Factory — Agent operating principles

This is a personal-use automation TOOL branch, not a new Kmong product or AXNODE v1 release. Source: `hibi89/Freelancer@tools/ax-dev-factory-local` (GitHub repository currently **PUBLIC**). Existing `main`, `product/*`, EAI `feature/*` and AXNODE `product/axnode-sector-runtime` remain unchanged.

Read HANDOFF.md → STATUS.md → AGENTS.md → REQUIREMENTS.md → docs/FINAL_BLUEPRINT.md → actual code/tests before any development.

Source of truth: owner-confirmed final blueprint + signed-off immutable High task contract. Do not water down requirements or change accepted weights to increase completion. Official percentage: UNASSESSED without approved 100-point baseline and objective evidence.

Rules: separate coding and review roles; reviewer must verify actual Git changes and tests, not trust coding model text. One fix attempt, then HOLD. Dependencies require VERIFIED prerequisites. Preserve original code/data via separate worktrees and existing Git history. No force push, silent merge, production deployment, paid APIs, permission changes, model weight upload, customer content or credentials.

The runtime is not security-isolated simply because it uses Python or SKILL.md. Only use a non-admin account and disposable checkout for first tests. All model provider, network and shell permissions must be inspected locally before `--execute`.

After significant verified changes update STATUS/HANDOFF with exact source SHA, tests PASS/FAIL/SKIP, Windows/model/Production verification limits, next actions and rollback path. The user's `ㄱ` command is NOT needed for steady-state queue automation; unexpected failures should be bounded and saved for inspection. OpenCode tool execution is a security-sensitive external component.

GitHub is the sole source/version reference. Keep runtime SQLite/logs and private plans on the user's device. Do not publish secrets into this public GitHub repo.
