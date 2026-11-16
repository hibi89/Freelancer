# AX Dev Factory — optional IMPLEMENTATION_BATCH (owner-only)

**Code baseline:** `1a6c772ced52529a860e22ba67e6c9f259402e90`. **Status:** synthetic Linux + hosted Windows verified, not owner laptop model proof.

## Selection and processing

- **Legacy safe default:** `RUN_QUEUE.cmd`; each approved task is coded, independently checked and committed before the next.
- **Opt-in batch:** `RUN_BATCH.cmd` with an already approved local `settings.json` (`RUN_QUEUE.cmd` requirements unchanged). Equivalent `python -m scripts.run_configured_queue --implementation-batch --execute`. Alternative explicit source command: `python -m axdev run --repo <local-clone> --plan <approved-json> --state <private-state-dir> --max-tasks 100 --implementation-batch --execute`.
- **Read-only progress:** `RUN_STATUS.cmd` reports `IMPLEMENTED` separate from `VERIFIED`; `RUN_REQ_STATUS.cmd` lists F01–F20 implementation evidence and remaining work without official weighting.
- **Batch design:** select independent QUEUED tasks with VERIFIED prerequisites and disjoint exact file scopes; one model coding call at a time; perform mandatory path/symlink checks immediately; save stage SHA256 to SQLite and status `IMPLEMENTED` (NOT verified); after stage wave, validate each stage on a new isolated Git worktree created at latest verified integration SHA; run approved deterministic checks, at most one repair, then either VERIFIED commit or HOLD. Dependent tasks become eligible in the same bounded invocation only after prerequisite VERIFIED.
- **Scope and failures:** batch maximum 1–100 tasks including resumed tasks. Code stage and verification status are durable; stop is cooperative at task boundaries. Resume does not recode a staged task. Any changed staged bytes, unsafe extra/ignored files, unsupported symlinks, invalid contract/CLI/provider policy, or review check failure cannot silently promote. An unresolved review exits code **3** through the batch CLIs; HOLD returns **2**; preflight failure returns **1**. No automatic Git push, PR or merge.
- **Safety/performance tradeoff:** batched coding postpones independent acceptance tests but not cheap path checks or configured provider/tool policy. Avoids repeating full checks after every model call in a group; throughput improvement has **not** been measured on real GTX1050Ti. CPU/RAM and filesystem overhead require a user-host benchmark. No OS/process/network isolation is provided by this mode.

## Tests and operational limitations

Run `python -m unittest discover -s tests -p "test_*.py" -q` locally when available; CI baseline [Actions #43809324284](https://github.com/hibi89/Freelancer/actions/runs/43809324284) Linux 113 PASS; Windows 112 PASS/1 SKIP. First use still requires the existing disposable `RUN_FIRST_USE.cmd` flow on a non-admin machine with already installed Python/Git/Ollama/OpenCode >=2.2.6. F01–F20 user-approved official completion remains UNASSESSED. Production/Vercel N/A.
