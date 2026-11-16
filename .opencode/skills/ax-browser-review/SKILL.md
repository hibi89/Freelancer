---
name: ax-browser-review
description: Optional localhost web UI acceptance review for approved tasks; not active in initial v0.1.
---
# AX Dev Factory: Browser review (FUTURE OPTIONAL ADAPTER)

- Run **only** after an approved code task reaches REVIEW and has explicit UI acceptance criteria from the same High-authored immutable task contract.
- Verify version-pinned `agent-browser` CLI and local browser runtime. Target allowlisted **localhost** application URLs and synthetic users/data only; no production URL, private account login or external navigation.
- Snapshot the browser accessibility tree, interact with only task-approved elements, take a fresh snapshot after each navigation and independently check expected page state, console errors and functional result.
- Bound browser lifetime, number of steps, memory, time and output size on 1050Ti/16GB; do not keep an extra local AI model alive for UI testing.
- Return machine-readable PASS/FAIL/NOT_RUN and evidence to reviewer. No self-grading by coder. Store private screenshots locally and never in PUBLIC Freelancer repo.
- No unrestricted shell/network or blanket browser permissions; execution must be through a future allowlisted controller adapter. **Current v0.1: documentation only, NOT CONNECTED.**
