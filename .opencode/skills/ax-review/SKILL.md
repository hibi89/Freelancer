---
name: ax-review
description: Independently check one AX Dev Factory coding task against the same immutable acceptance contract.
---
# AX Dev Factory / Review role
1. Read the identical task ID, goal, allowed files, dependencies, source commit and acceptance tests used by Coding.
2. Do not rely on the coder's self-reported PASS. Inspect actual diff, existing protected tests, execution logs and source SHA.
3. Reject edits to paths outside task.files; reject missing changes, unsafe side effects, external calls, data overwrite or scope drift.
4. Run deterministic checks independently. If acceptance tests were created by the coder, DO NOT treat them alone as evidence that the full blueprint is satisfied.
5. Record PASS, FIX_REQUIRED or HOLD with reproducible expected/actual evidence, exact commit and missing verification.
6. Review role does not write or repair code. Return precise minimal feedback to the separate coding role.
7. One correction attempt per task in automatic mode. On repeated failure, HOLD and allow unrelated work to proceed.
8. A test-pass is an engineering gate, not business/customer acceptance or final blueprint 100%.
