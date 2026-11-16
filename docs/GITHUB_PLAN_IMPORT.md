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
