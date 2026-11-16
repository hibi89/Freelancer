# Read-only local preflight: no installation, model downloads or AI calls

Execute from AX Dev Factory checkout on Windows:

    RUN_PREFLIGHT.cmd

Or:

    python -m scripts.preflight --model ollama/qwen3:4b-instruct

This prints Python/Git/Ollama/OpenCode versions, the OpenCode 2+
--standalone command option, local 127.0.0.1:11434/api/tags installed-model
list, and optional NVIDIA GPU detection. It makes **no internet request**,
does not run a model, and does not modify any user project or credentials.

Exit 0 means ready only for a disposable model E2E attempt; exit 2 means
prerequisites missing. Even exit 0 does NOT imply OpenCode permissions
are effectively enforced, GPU fits or coding works. The only optional
output write is an explicitly supplied --output new evidence filename.

After read-only preflight, the owner may separately opt in to the synthetic
model test with RUN_TRIAL.cmd and RUN_MODEL_TRIAL.cmd. Actual original
project workflows, GitHub push/PR, secrets, and automatic startup remain
out of scope until separately approved. No automatic installation.
