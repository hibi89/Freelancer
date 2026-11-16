# AX Dev Factory F13 staged plan import — objective verification

- Date: 2026-11-16 KST
- Source commit: fb4de6ed0e361c5a6ccd4f6a865fc5f636db2a78
- Branch: tools/ax-dev-factory-local, main unchanged
- Hosted CI: https://github.com/hibi89/Freelancer/actions/runs/43788443205
- Python3.11 unittest: 28 PASS, 0 FAIL, 0 SKIP (new import tests 9)
- Separate blueprint-gate check: https://github.com/hibi89/Freelancer/actions/runs/43788443559 SUCCESS
- Import source blob: 3e6d436114fd50c8ac4a7feaed343e311abba93e
- Core blob: 62406b9ac4b616b58ee650cf1a175afe944573f7
- Policy blob: aa2128126daf30ba4067a6a5dab137d676182ca6

## Verified with mocked GitHub responses

Read-only API construction and expected branch HEAD identity, Git blob hash,
strict version-1 task contract, existing output unchanged, identical re-import,
malicious path rejection, branch advancement detection, and symlink refusal.
Original prior tests cover worktree isolation, dependency DAG, recovery, HOLD
and policy JSON assertions. Compileall, doctor/version, synthetic dry-run pass.

## Not verified

No actual GitHub REST network request was made during new 9 tests. There is
no Windows10/GTX1050Ti, OpenCode V2 runtime or Ollama model invocation evidence.
Policy JSON assertion is not actual enforcement proof; --standalone is only
an isolation improvement, not an OS/network sandbox. PR/push, continuous
polling, private repo sync and real project acceptance remain unimplemented.

## Next verification command (owner-controlled disposable environment)

python -m axdev sync-plan --source hibi89/Freelancer --branch tools/ax-dev-factory-local --path examples/sample-plan.json --expected-sha APPROVED_BRANCH_SHA --output LOCAL_PRIVATE_NEW_FILE.json

Only a reviewed 40-character SHA can replace APPROVED_BRANCH_SHA. The
command never launches the coding queue. After inspection, the owner may
configure_queue separately. Formal blueprint completion UNASSESSED.
