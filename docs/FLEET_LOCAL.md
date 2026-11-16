# AX Dev Factory local multi-project fleet (F20 first stage, F17 bounded)

**Scope:** An owner-initiated, serial queue across 1..10 locally approved
projects. No new project creation, code submission, scheduler installation,
cloud model, GitHub write, or automatic new plan approval.

First configure each project separately with \`python -m scripts.configure_queue\`
using its own absolute repo/plan/settings paths outside target repositories.
This saves the owner-reviewed plan SHA256. Then create a new fleet file
(never overwrites an existing one):

    python -m scripts.fleet configure --settings C:\AXDEV_PRIVATE\project1-settings.json --settings C:\AXDEV_PRIVATE\project2-settings.json --output "%LOCALAPPDATA%\AXDevFactory\fleet.json"

Review without any AI/code writes:

    RUN_FLEET_STATUS.cmd
    python -m scripts.fleet run

To run the previously approved projects only, start **RUN_FLEET.cmd**.
It explicitly passes --execute --confirm-reviewed; at most 10 projects
and 100 tasks per project. Each subprocess delegates to the original
single-project run_configured_queue, so the same immutable plan SHA,
SQLite checkpoints, Git worktree review and single-worker lock apply.

Stop between projects: \`RUN_FLEET_STOP.cmd\`, then
\`RUN_FLEET_RESUME.cmd\` when ready. To stop *within* one project use
\`RUN_STOP.cmd\` with that project's settings passed directly through
\`python -m scripts.queue_control stop --settings ABSOLUTE_PATH\`.
A current Ollama coding call is never force-killed. A project HOLD or
runtime error is recorded and the next independent approved project can
continue. Unexpected settings/plan changes STOP THE ENTIRE FLEET
before starting any project. No force push/merge or automatic restart.

The fleet manifest pins *each configuration's* SHA256, and each
configuration pins its task plan SHA256. A changed plan/settings means
create a NEW manifest and approve explicitly, not auto-update an old one.
Local-only \`.axdev-fleet-state/fleet-events.jsonl\` records project index,
status, exit code and UTC timestamp, not prompts/code/credentials.
Never publish this private state in the PUBLIC Freelancer repository.

**Limitations:** This is a persistent sequential batch, NOT a Windows
boot scheduler, background service, model installation, OS sandbox, live
GPU/VRAM acceptance, or automatic PR publication. Windows10 + real
OpenCode/Ollama execution remains NOT_RUN.
