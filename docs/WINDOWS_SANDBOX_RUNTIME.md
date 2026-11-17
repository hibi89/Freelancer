# Windows Sandbox coding and independent acceptance

The host owns approvals, SQLite state, Git writes and the final verdict.

1. Validate the exact plan SHA256, dependency graph, toolchain and model manifest. Build the source ZIP from raw pinned Git blobs.
2. Launch the coding guest with networking, clipboard, peripherals and vGPU disabled. Only a fresh outbox is writable. The guest limits Ollama to one resident model and one active request. OpenCode works in a disposable Git worktree and the guest returns `CANDIDATE` bytes or `HOLD`.
3. After the client exits, validate and seal the bytes outside the outbox. Give the host reviewer a read-only snapshot of the exact candidate Git tree.
4. The host runs protected project checks and independent callable probes in separate capability-free Windows AppContainers. The host compares actual JSON results with the approved expected values. An existing project test remains protected even when a task adds tests. Verdicts from guest files, stdout labels, EAI or model responses cannot substitute for the host comparison.
5. Allow one isolated repair using the sealed candidate. A repeated failure is HOLD; only VERIFIED prerequisites unblock dependencies. A trusted proof links the candidate digest, task SHA, Git base/tree/commit, and run ID. Persist PREPARED before atomic ref promotion so interrupted completion can be recovered.

## Disposable first run

Use Windows 10 Pro/Enterprise/Education with Windows Sandbox and virtualization already enabled. Choose a portable runtime with Python 3.11+, Git, compatible OpenCode, Ollama and local model files. The bundle uses `python/`, `git/`, `opencode/`, `ollama/`, `models/` and optional `ruff/`. Prepare a new v2 manifest with `python -m scripts.prepare_offline_bundle --offline-bundle <path>` and review its SHA256. The inventory pins libraries and model data as well as executables.

Keep the approved plan, state, bundle and project in separate locations. Include independent `acceptance` probes in the approved plan and use the correct plan SHA256. Set `AXDEV_OFFLINE_BUNDLE`, `AXDEV_BUNDLE_SHA256` and optionally `AXDEV_MODEL`; run `RUN_TRIAL.cmd` then `RUN_MODEL_TRIAL.cmd` on a fresh disposable fixture. For an approved project, use `RUN_SANDBOX.cmd` or configure `RUN_QUEUE.cmd` with `--offline-bundle` and `--bundle-manifest-sha256`. The direct sandbox CLI additionally requires `--plan-sha256 --execute --confirm-isolated-run` and the corresponding SHA argument. Use a fresh state after legacy verified execution.

The full Windows 10 coding guest, disabled network mappings, offline runtime dependencies, recovery and hardware behavior still require a target run. See the [Windows 11 physical-device results and remaining Windows 10 checks](WINDOWS11_VERIFICATION.md) and [P2 ledger](P2_VERIFICATION_LEDGER.md).
