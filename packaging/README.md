# BID AX Windows packaging — not a released installer

- Target: **Windows 10/11 x64, Python 3.11**. Source tests must pass on an actual Windows machine before distributing binaries.
- `build_windows.ps1` is **manual-only**. Requires operator-installed PyInstaller in a disposable environment; the script does not install packages or transmit data automatically.
- Run from repo root: `powershell -ExecutionPolicy Bypass -File packaging/build_windows.ps1` after reviewing it and pinning/testing a PyInstaller release and dependencies.
- Entry point creates only `%LOCALAPPDATA%\\BidAX\\bidax.db` after customer launch. It is not a signed installer and does **not** auto-update, schedule itself or access government APIs.
- **Do not ship:** Windows EXE build, clean-VM install/uninstall, SmartScreen/antivirus review, Korean UI/fonts, data migration, file ACL, real customer acceptance and code-signing are **NOT RUN**.
- To uninstall a test package, remove the EXE manually; `%LOCALAPPDATA%\\BidAX` retains customer data intentionally until the owner backs it up and explicitly chooses deletion.
- For recovery, retain historical Git commit SHA; backed-up DBs must be restored to **new** paths, never overwrite.
