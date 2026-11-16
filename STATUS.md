# AX Dev Factory status — 2026-11-16 KST

Repo: \`hibi89/Freelancer\` (GitHub **public**). Branch: \`tools/ax-dev-factory-local\`. Use: owner personal development only; not a Kmong product. Formal blueprint completion: **UNASSESSED**. Vercel/Production: **NOT APPLICABLE**.

## Implemented in GitHub (source claims, pending independent CI proof)
- \`axdev/core.py\`: strict task JSON, graph dependency cycle and path validation; single-worker plan; git worktree isolation; OpenCode model command tied to \`ollama/\`; no shell=True; allowlisted Python checks; one correction; HOLD and local SQLite source-spec SHA checkpoints; local Git commit on reviewed result.
- \`axdev/__main__.py\`: doctor + safe dry-run by default; \`--execute\` opt-in; JSON results.
- \`tests/test_axdev.py\`: synthetic Git worktree and fail-closed regression tests.
- 3 OpenCode skills: coding/review/recovery. Full final blueprint F01–F20, HIGH task format and trial README.
- Existing main/product branches untouched. No private files, tokens or model weights uploaded.

## Not yet verified / not yet implemented
- GitHub Actions full pass and source SHA **PENDING** (fill in after actual run); end-user Windows10 GTX1050Ti/driver/Ollama/OpenCode live trials **NOT_RUN**.
- Self-authored tests are not independent business acceptance. AI semantic review and third-party/safe sandbox **NOT IMPLEMENTED**.
- GitHub plan synchronization, remote push/PR automation, automatic startup/monitoring, real EAI/AXNODE integration, Windows fault-recovery and multi-product throughput benchmark **NOT IMPLEMENTED**.
- No percentage promotion or release claim.

## Next gates
1. GitHub hosted Python3.11 synthetic unit tests, source SHA readback; fix defects.
2. Owner's disposable Windows Git fixture, \`doctor\`, dry run, model smoke, record 5-task throughput.
3. Implement remote GitHub task synchronization, explicit safe PR publication and scheduler only after credential/auth safety review.
4. EAI and AXNODE optional adapters after separate interface design and owner approval.
