# AX Dev Factory optional UI verification adapters (2026-11-16 KST)

Status: **DESIGN ONLY / NOT IMPLEMENTED / Windows host NOT TESTED**. No new weighted completion points, no claim of integration or release. These are optional local test instruments, **not AI coding models**, and must not be launched by the core coder autonomously.

## Selection

1. **agent-browser** (`vercel-labs/agent-browser`, Apache-2.0): priority optional adapter for *web application acceptance*. It is a Rust CLI backed by a browser. For an approved localhost URL only, take a structured snapshot, run an explicit allowlisted element interaction, and verify expected response/visible state. Screenshots and snapshots stay local. No login bypass, unknown websites, real customer data or production writes.
2. **agent-desktop** (`vercel-labs/agent-desktop`, Apache-2.0): later optional adapter for native *Windows GUI acceptance*. Uses Windows UI Automation via accessibility tree. Only an authorized synthetic local app window is in scope. Never interact with another user app, desktop secrets, system dialogs or privileged controls. Signed-in interactive Windows desktop may be needed. No blanket desktop control permission.
3. **No UI adapter** for deterministic Python backends, pure libraries, CLI tasks or data processing. Unit tests and static checks have better speed and reproducibility.

## GTX 1050 Ti / 16GB RAM default policy

- Keep **one local Ollama coder model** resident and a deterministic CPU reviewer. Never launch both UI adapters by default.
- Start UI verification **after coding** and only for tasks with a fixed `ui_kind: browser|desktop` and vetted assertions. `ui_kind` is a future *optional* schema extension; **v0.1 task parser does not yet accept or execute this field**.
- For web tests launch one browser instance only, with short capped timeout and no screenshots except on explicit local consent. Browser memory can compete with Ollama.
- For desktop tests require an interactive user session, named allowlisted app process and strictly restricted operations; no unattended desktop-wide clicks.
- Report `NOT_RUN`, `PASS`, `FAIL` separately. Never infer UI PASS from Python unit tests, web server 200 or launch alone.

## Security and architecture bridge

Current `config/opencode-local-only.json` tries to deny generalized shell/web access. Keep that principle. Do **not** enable unrestricted shell commands just to allow agent-browser or agent-desktop. In later implementation, the controller must call **explicit allowlisted binary + arguments** through a dedicated review adapter with timeouts, per-repo scope, bounded output, synthetic fixtures and opt-in UI permissions. Verify the exact OpenCode policy schema on the user's installed version first.

The UI adapters receive no blanket model authority; they run from a trusted reviewer tool, not coder-generated arbitrary scripts. Their results are evidence for the same immutable High task contract and independent acceptance tests. F07/F19 in the [final blueprint](FINAL_BLUEPRINT.md) cover verification goals without modifying owner-approved scope or official weight.

## Sources

- https://github.com/vercel-labs/agent-browser
- https://github.com/vercel-labs/agent-desktop

Runtime installation, third-party version pinning and actual host compatibility are **NOT_RUN**.
