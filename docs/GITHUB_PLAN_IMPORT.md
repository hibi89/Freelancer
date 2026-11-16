# F13 public GitHub plan import: SHA-pinned read-only MVP

Use an already reviewed public GitHub branch commit SHA; never tokens:

    python -m axdev sync-plan --source hibi89/Freelancer --branch tools/ax-dev-factory-local --path examples/sample-plan.json --expected-sha YOUR_40_CHARACTER_SHA --output C:\AXDEV_PRIVATE\approved.json

Three GitHub read-only requests check the branch SHA before/after retrieving
the file at that SHA. Verify exact Git blob and strict task JSON, reject
changed plans and unsafe paths. Writes no remote data, does not execute
models, does not configure or launch the task queue. Existing output is
accepted only if byte-identical; manual reapproval required for new SHA.

Only public repo reads (no GitHub token), <=512 KiB, unauthenticated rate limits.
Windows live network, OpenCode actual effective permissions and Ollama GPU
remain NOT_RUN. Not an OS sandbox; private plans are future work. Use
scripts.configure_queue with the staged file only after reviewing it.

## Approved-source local queue configuration (optional)

After manually inspecting the first imported JSON, configure the queue once:

```powershell
python -m scripts.configure_queue --repo C:\\safe\\disposable-repo --plan C:\\AXDEV_PRIVATE\\approved.json --github-source hibi89/Freelancer --github-branch tools/ax-dev-factory-local --github-path examples/sample-plan.json --github-sha YOUR_REVIEWED_40_HEX_SHA
```

`RUN_QUEUE.cmd` now verifies the local approved plan SHA256 before starting
any worktree/model. If the optional GitHub pin is configured, it checks
the live branch identity and exact source content with `sync_public_plan`.
If GitHub is unreachable (network timeout / transport failure only), an
unchanged approved local plan may still run offline. If SHA identity, plan
content, or local checksum mismatches, it **fails closed** and does not code.
Existing local-only settings remain compatible. A changed remote branch
requires a new owner review and a new approved settings/plan version;
there is NO automatic re-approval, push, merge, or remote writes.
