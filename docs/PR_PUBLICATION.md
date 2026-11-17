# Optional verified local draft PR publication (F12 — opt-in)

The AX Dev Factory queue never pushes code or creates PRs automatically.
This tool exists to **preview** publication and to prepare a strongly
gated, explicitly authorized publication path for later.

First run preview (no network, no writes):

    python -m scripts.publish_pr --approved-repo hibi89/Freelancer --base main --expected-commit EXACT_40_HEX_VERIFIED_SHA --head axdev/review-unique-name

The tool checks:
- local one-time settings approved plan SHA256 and every task's immutable
  spec digest against SQLite;
- origin URL matches exactly the explicitly supplied GitHub repository;
- isolated integration ref equals the expected reviewed local commit SHA;
- changes relative to the pinned baseline contain *only* approved
  added/modified paths (no rename, deletion, or sensitive path);
- at least one task is VERIFIED in the local database;
- branch naming limited to axdev/review-*.

To publish later, the owner must separately authorize the repository,
external code transfer and account identity, review the diff locally,
have GitHub CLI installed and authenticated as repository owner, then add
**both** flags --publish --confirm-public-export. Only then a non-force
push of the reviewed commit and a **DRAFT** PR creation is attempted. The local baseline must already be reachable from the approved GitHub base branch. The push excludes implicit tags and mirrored refs. The result must read back as a draft on the approved base and exact reviewed commit.

Publication is not run by default, RUN_QUEUE.cmd, or GitHub Actions.
A branch push can succeed while PR creation fails; in that case the
tool stops and reports the partial failure, leaving the branch for
manual reconciliation. No auto deletion, force push, merge, permission
change or deployment. Do not publish customers' data or private source
to a PUBLIC repo. Effective repository security/identity checks require
a real owner-host test before the tool is treated as production ready.
