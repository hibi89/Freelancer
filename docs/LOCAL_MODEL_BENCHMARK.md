# Synthetic local Ollama throughput benchmark (F16 preparation)

From a non-admin Windows10 owner terminal in AX Dev Factory checkout:

    RUN_BENCHMARK.cmd

The launcher first runs RUN_PREFLIGHT.cmd (read-only). If the selected
model and OpenCode 2+ are available, the benchmark performs exactly
one bounded synthetic POST to 127.0.0.1:11434/api/generate using a
public fixed prompt, max 16 generated tokens and a 120-second timeout.
It reports generated tokens/s, wall time and optional before/after
nvidia-smi memory snapshots.

This is NOT a peak VRAM benchmark, not a test of OpenCode file editing,
not proof that all weights reside on the GTX1050Ti GPU, and not evidence
of actual autonomous coding. No source files, credentials, prompts from
real projects or model output are uploaded or stored in GitHub.
The optional --output writes only a NEW local JSON file (never overwrites).

For custom locally installed model:

    python -m scripts.benchmark_local --model ollama/qwen3:4b-instruct --execute

Actual performance remains NOT_RUN until the owner runs it on the
Windows GTX1050Ti host. No installation or model pull occurs here.
