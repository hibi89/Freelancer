# AX Dev Factory — Windows EXE desktop UI standard (owner-approved V1)

**Design lock date:** 2026-11-17 KST  
**Product:** AX Dev Factory, personal/free/local autonomous development control center  
**Source branch:** `feature/axdev-owner-product-ui-20261117` (PR #5); parent Windows 11 F01–F20 verification candidate PR #3  
**Scope:** One user's native Windows 11 application. No browser, public website, SaaS, external HTTP server or paid AI API.

## 0. Owner-selected exact reference image

- **Owner's actual uploaded image:** `AXDEV_DESKTOP_UI_STANDARD_20261117.png` (508 × 279 px), SHA-256 **`6043e2d17fe79c62e6b1f05e284b583e26aa3e8c153419ee5e2060065014f33f`**.
- **GitHub versioned image reference:** [selected dark desktop thumbnail (330×181 WebP)](design/AXDEV_DESKTOP_REFERENCE_20261117.webp). The original 508×279 screenshot is archived unmodified in the private owner Library.
- **Persistent owner Library location:** `/AX Dev Factory/Design References/AXDEV_DESKTOP_UI_STANDARD_20261117.png`. The original image is stored there; GitHub includes the smaller actual-image preview above and this specification for Codex/Astra design reference.
- **Visual identity is fixed by owner:** dark midnight-navy, restrained violet/teal status highlights, dense operator-workstation layout. The provided screenshot is a **visual reference**, not evidence that every pictured metric or control already exists.
- **Astra Max revision policy:** may propose improved polish, accessibility and responsive behavior; must preserve the functional zones, natural-language command entry, immutable approval gate, semantics of state, and the offline/isolated security posture. Changes become official only after final-design review/owner direction.

## 1. Visual layout contract

| Zone | Screen region | Required behavior |
| --- | --- | --- |
| Windows title bar | Native OS chrome | EXE name: AX Dev Factory — 오프라인 개발 오케스트레이터. No browser URL. |
| Left navigation | 200px dark vertical rail | `현황`, `자동화`, `검수`, `작업 로그`, `모델 관리`, `보안`. Controls actually navigate/focus functional information. |
| Four top metrics | Compact KPI row | Real SQLite task verification ratio, HOLD count, configured Ollama model, Sandbox policy state. No fictitious percentages or unmeasured 'running' claims. |
| Main left | Monospaced console | Whitelisted local event fields only: UTC timestamp, task ID, VERIFIED/HOLD/IMPLEMENTED, bounded elapsed duration. Never echo secret, project source, model raw output. |
| Main right | Work details and controls | Real SQLite task list; safe STOP at task boundary, RESUME signal, read-only verification report. No unapproved destructive button. |
| Bottom workflow | Horizontal process diagram | Approved contract → local coder → independent reviewer → Windows Sandbox → Git/SQLite proof. |
| **Bottom command composer** | Prominent sticky-looking purple/blue area | **User enters natural-language instructions here.** Three explicit stages: 1. save inert draft; 2. review exact allowlist + independent probes and approve SHA-pinned contract; 3. execute one approved task with fresh confirmation. |

## 2. Native/EXE architecture

- **Runtime UI:** Python 3.11+ Tkinter (stdlib). No Flask, FastAPI, Electron, browser, localhost web listener or cloud infrastructure.
- **Core reused:** `scripts.run_configured_queue`, `axdev.windows_sandbox_runtime`, Git/SQLite worktree & separate AppContainer reviewer, Ollama/OpenCode local 4B. Private configuration and checkpoints remain outside the source repository.
- **Human request:** text typed in native GUI. The first action only saves a private DRAFT under `%LOCALAPPDATA%\AXDevFactory\desktop-commands`.
- **Approval:** owner specifies exact allowed files, approved unittest check and 1–12 distinct callable acceptance probes; the typed plan is validated by `axdev.core.load_plan`. New private plan and settings have a SHA256 lock and do not modify existing global settings.
- **Execution:** only after distinct explicit user confirmation, run at most one approved contract via a separate non-admin process `scripts.run_configured_queue --settings ... --max-tasks 1 --execute`. PyInstaller onefile mode uses the embedded `--axdev-worker` entrypoint.
- **Stop:** signals STOP at next safe boundary; not a kernel kill. **Resume:** only clears STOP. No generic shell executor, arbitrary AI command execution, production deployment or GitHub publication through GUI.
- **Packaging:** `BUILD_AXDEV_EXE.cmd` works only in a Windows environment with preinstalled PyInstaller. Offline local build; never `pip install` on the owner's PC without separate approval. `RUN_AXDEV_DESKTOP.cmd` uses the built EXE if present or source Python for development.
- **Unsigned development build:** do not claim a signed installer or release-ready application without real Windows EXE end-to-end test.

## 3. Truthful completion metrics

- `VERIFIED / all SQLite tasks` is the **current local task acceptance checkpoint ratio**, not official F01–F20 verification completion.
- Original AX Dev Factory F01–F20 **Windows 11 field row candidate 20/20** is evidence from PR #3, not new native UI acceptance.
- Original Windows 10 six gates `NOT_RUN`; formal **weighted** verification `UNASSESSED`; release/real-use `HOLD` until owner approval and native UI + packaged EXE test.
- No invented chart, usage token rates, resource counters, running model, speed, logs or statistics from the supplied design screenshot. Show `미확인` or computed real values instead.

## 4. Native acceptance checklist (must be evidenced before declaring 100%)

1. [ ] GitHub exact code HEAD and Python syntax/tests Linux/Windows pass, including command draft and approval tests.
2. [ ] Windows 11 non-admin Tkinter app launches without a browser/server and closes cleanly; keyboard controls and DPI work.
3. [ ] Windows app builds an unsigned `AXDevFactory.exe` and packaged worker mode imports all required Python modules.
4. [ ] In native EXE, one synthetic natural-language command saves an inert draft without any model invocation.
5. [ ] Unapproved command has no allowed file edits; unsafe paths/check/probes fail closed.
6. [ ] Owner-approved SHA-locked command starts exactly one local Offline Sandbox run and AppContainer independently verifies only the approved files, Git/SQLite proof matches.
7. [ ] STOP/RESUME UI never silently runs a second model; close/restart app preserves private state and does not corrupt running worker.
8. [ ] 1920×1080, 1366×768, 125% DPI and keyboard/contrast check.
9. [ ] The actual owner's connected Windows 11 device tests the build in a disposable fixture; no Production/main merge or external customer data.

## 5. Next task responsibilities

The web High design authority owns layout contract and final F-ID acceptance. The current GitHub feature branch may implement the native frontend and source-level tests. Real Windows EXE creation/smoke and installed-device integration remain separate evidence gates. The Windows Sandbox itself already requires native virtualization and local model files even though the GUI no longer needs a web server.
