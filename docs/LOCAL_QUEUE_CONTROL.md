# AX Dev Factory local stop/resume/status (does not need ChatGPT)

The approved task queue already runs one Ollama coder at a time up to
100 tasks. To stop at the next task boundary, run:

    RUN_STOP.cmd

The active model call is **not** killed midway; one current 20-minute
max call can finish before the stop is observed. The stop file is
saved outside the target repo and survives process crashes/restarts.

To inspect SQLite status without running GitHub sync or AI:

    RUN_STATUS.cmd

To remove the stop signal without starting execution:

    RUN_RESUME.cmd

To continue the existing approved queue, explicitly launch RUN_QUEUE.cmd
again. New plan versions always require separate approval and immutable SHA
checks. Existing Git worktrees/checkpoints and main remain untouched.

The local run-events.jsonl contains task ID, timestamp UTC, VERIFIED/HOLD,
elapsed seconds and reviewed local Git commit SHA only. No prompts, source
contents, model responses or credentials are written to this event stream.
Do not publish runtime directories to the PUBLIC GitHub repository.

This control is a cooperative stop BETWEEN tasks, not an emergency OS
process kill or an unattended boot scheduler.
