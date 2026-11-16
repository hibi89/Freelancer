# High → Local AI task contract v1

Source of truth: GitHub approved blueprint; plan is a *derived execution queue*, not a change to requirements. Use `examples/sample-plan.json`.

Required fields:
- `version: 1`, `tasks: []`
- `id`: stable uppercase alphanumeric/hyphen/underscore, 3–40 chars
- `goal`: measurable instruction including expected behavior and forbidden regressions, maximum 4000 characters
- `files`: exact relative paths, 1–16, no glob, absolute path, traversal or .git
- `depends_on`: IDs of tasks whose status must be VERIFIED
- `checks`: version-1 allowlisted argv arrays (Python unittest discovery or compileall). No arbitrary shell strings.

High responsibility: break into small jobs, map each to final-blueprint requirement IDs and protected acceptance tests, order dependencies, define exact allowed paths. The local model may suggest a new task but cannot add it to the approved plan or change acceptance automatically.

Controller state: QUEUED → CODING → REVIEW → VERIFIED; one FIX_ONCE on fail → REVIEW; otherwise HOLD. Queue bypasses blocked tasks only if independent. SQLite persists state and task-spec SHA; changing an existing task contract stops until manual reconciliation.

Limitations of v0.1: GitHub plan synchronization, AI semantic reviewer, EAI/AXNODE direct adapters, sandboxed OpenCode permissions, secure publishing, dashboard, auto-start and Windows hardware tests are not delivered. Local Git branch commit is not a remote PR. Model output is untrusted.
