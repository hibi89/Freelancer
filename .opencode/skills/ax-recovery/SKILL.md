---
name: ax-recovery
description: Repair one failed AX Dev Factory task once from independent test evidence, then return it for re-review.
---
# AX Dev Factory / Recovery role
1. Receive task ID, immutable task contract, exact failing test command, observed log and original worktree path.
2. First determine whether failure is product defect, wrong test, environment fault, security policy conflict or inadequate model ability.
3. Make only the minimal allowed-file fix; never delete unrelated work, force push, loosen tests, drop requirements or alter permissions.
4. Do not repeat an identical action without changed evidence. Controller allows one automated fix attempt; then HOLD.
5. Respect task dependency graph; never mark dependent tasks complete while prerequisite remains unverified.
6. Preserve logs, evidence, Git branch and rollback point; report remaining unknowns clearly.


## One-pass systematic debugging
- Compare the first failing assertion with expected behavior. Identify the likely root cause using the smallest diff and one targeted reproduction.
- Change one hypothesis with the least patch; do not restart a failed task from scratch or repeat identical commands.
- If the failure is due to unavailable tools, unresolved dependencies, broad architecture changes, or a missing human approval, HOLD without consuming more model invocations.
