# Windows first-use single entrypoint (no installation or real source edits)

The owner may run **RUN_FIRST_USE.cmd** after explicitly reviewing the
existing synthetic task contract and having already installed Python3.11,
Git, Ollama and OpenCode V2. It does not install programs or download
weights; it performs:

1. One new disposable fixture dry run under \`%USERPROFILE%\AXDEV_TRIAL\`
   (refuses to overwrite an unknown existing directory).
2. Local-only prerequisite check with \`RUN_PREFLIGHT.cmd\`.
3. An explicitly owner-launched synthetic coding trial using one
   \`ollama/\` model via \`RUN_MODEL_TRIAL.cmd\`, in a separate Git worktree.
4. A read-only SQLite/checkpoint status summary saved in a **new**
   private \`%LOCALAPPDATA%\AXDevFactory\trial-evidence\trial-*.json\`.

If the synthetic fixture was already created, the script will not
overwrite it. A second run may find no tasks ready after a previous
VERIFIED result; use the report/console to avoid claiming a second model
inference occurred.

The evidence file contains counts and run metadata, not prompts,
source files, model output, credentials or private paths (except the
local console prints the new report's location). No automatic GitHub
upload or PR. A green synthetic run does not prove Windows OS network
isolation, provider policy enforcement, GPU residency or safe customer
project use. Do not run as Administrator.

Optional throughput probe is separate: \`RUN_BENCHMARK.cmd\`.
Actual host outcomes remain NOT_RUN until the owner executes on the
GTX1050Ti Windows laptop.
