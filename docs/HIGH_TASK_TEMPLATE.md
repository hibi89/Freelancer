# GPT-6 High task-breakdown guide (internal, high-level reference to Spec Kit)
Version: 1 / 2026-11-16 KST. This is an original compact template, not a copy of a third-party repo.

## Source order
Read HANDOFF.md → STATUS.md → AGENTS.md → REQUIREMENTS.md → full owner-approved FINAL_BLUEPRINT.md → actual source/test tree. High must never infer missing requirements.

## Derive executable tasks
1. Link each feature to its original requirement ID and exact target path(s). Identify dependencies, existing trusted tests and non-regression constraints.
2. Break into 1–2 implementation files, preferably under 300 changed lines per task when realistic. Don't split a fix across separate tasks that cannot pass their own acceptance tests.
3. For each task write task ID, goal, explicit expected behavior and observable assertions, exact allowlisted files, depends_on, and deterministic test argv. Do not allow arbitrary shell commands as acceptance checks.
4. Put independent tasks before dependency-bound ones. Include security review for file permissions, external API/network, pricing, third-party use, and database mutation.
5. Keep the immutable plan JSON within the target repo if private. **Freelancer repository is PUBLIC**—do not copy private code or sensitive plans into the tools branch.
6. Review and approve one version of the task list. Any changes to an existing task ID/spec SHA require explicit reconciliation. The local controller blocks silent changes to a task.
7. Do not claim overall product completeness based solely on unit tests; status must include verified/not-run gates against the entire user-approved blueprint.

### Sample conceptual task, not runnable as written
Requirement: R06
Task ID: D2W-041
Goal: Reject CSV files containing duplicate headers with an explicit error, preserving accepted ordinary CSV behavior; verify a protected regression suite.
Files: src/csv_loader.py
Depends on: D2W-039
Checks: Python unittest discover; Ruff check src (only if installed and task approves it)

### Derived JSON
See `examples/sample-plan.json` for the exact strict schema. Spec Kit is a *planning reference*, not a runtime agent or mandatory package.
