---
name: ax-desktop-review
description: Optional Windows desktop GUI acceptance for approved local applications; not active in initial v0.1.
---
# AX Dev Factory: Desktop review (FUTURE OPTIONAL ADAPTER)

- Use only if an approved task explicitly requires real Windows native GUI behavior; never for ordinary backend or web-only tests.
- Verify compatible `agent-desktop` binary, accessibility permissions and a named, approved synthetic test application in the signed-in user's Windows session.
- Scope all snapshots, clicks and typing to the approved application window and specific task assertions; do not access other desktop apps, clipboard secrets, credential dialogs, file managers or OS settings.
- Use Windows UI Automation accessibility refs, inspect the actual UI before/after actions, and report PASS/FAIL/NOT_RUN separately. A window appearing is not proof of functional success.
- Cap action count and timeout; fail closed if refs are stale or the window identity changes. Keep screenshots and logs local, not in PUBLIC GitHub.
- No broad desktop control through unrestricted OpenCode shell; only a future approved controller adapter may run these commands. **Current v0.1: documentation only, NOT CONNECTED.**
