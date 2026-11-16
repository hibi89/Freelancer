# First-use independent acceptance — 2026-11-16

`RUN_FIRST_USE.cmd` now gates the model call and final success with
`python -m scripts.verify_trial --phase ready|completed`.

Previously, `python -m axdev run` returned exit status 0 when no tasks
were available; it could be mistaken for a successful new trial.

The verifier is **read-only and restricted to the disposable fixture**:

- requires the exact single `TRIAL-001` task, original synthetic README,
  AGENTS.md and protected unittest acceptance source;
- refuses changed original Git checkout, symlinked files and foreign task plans;
- `ready` refuses existing CODING, REVIEW, PREPARED, HOLD or VERIFIED state;
- `completed` checks SQLite VERIFIED state and pinned spec hash, review
  evidence, original Git baseline, isolated integration commit, parent SHA,
  only `src/hello.py` modified and a matching private VERIFIED event.

A second run never silently claims success. Existing verified work must be
reviewed separately, not restarted as a new model trial.

**Limitations:** The test suite can use a synthetic fake coder to produce
the same VERIFIED checkpoint; that does **not** prove Ollama generated the
source. No actual GPU/Windows laptop measurement, live OpenCode tool
permission enforcement, OS isolation or GitHub publication is claimed.
