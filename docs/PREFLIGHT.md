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


## Optional target Git identity check (read-only)

`python -m scripts.preflight --repo ABSOLUTE_GIT_CHECKOUT`
checks both `git var GIT_AUTHOR_IDENT` and
`git var GIT_COMMITTER_IDENT`. This detects a missing/invalid local
commit identity **before** queuing live coding; no name or email value is
written to evidence. The configured queue automatically supplies its
target checkout. A matching GitHub account is **not** proven by local
Git configuration and must be reviewed separately before any PR push.
Synthetic Windows `RUN_PREFLIGHT.cmd` supplies the fixture checkout
once it exists.
