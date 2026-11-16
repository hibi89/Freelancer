> **P2 SECURITY HOLD (2026-11-16):** A same-account sandbox guest, model and project checks can all write the mapped outbox. A plausible SHA/path/task-bound `receipt.json` is therefore **NOT** independent verification. The host must not import it into the VERIFIED integration ref. The code now rejects claimed guest VERIFIED receipts and historical untrusted PREPARED resume, preserving an advisory outbox for inspection. F18 remains BLOCKED until an OS-separated reviewer or independently trusted attestation scheme is implemented, tested and owner-device verified. This intentionally supersedes the optimistic promotion steps in the P1 historical flow below. No unisolated fallback or owner approval is implied. 

# F18 — Windows Sandbox execution: source contract and P2 gates

**Status:** P1 code implemented; Windows on-device execution and isolation NOT_RUN. Host data remains private. No Windows optional features or network permissions are modified by this repository.

## Execution flow

1. The host Factory checks immutable task spec hashes, approved files, dependencies and its verified integration Git SHA.
2. It archives the complete pinned Git commit. The archive inventory must include every tracked file so export-ignore cannot remove protected tests. It adds a vetted copy of AXDEV controller source and a private one-task request.
3. A generated .wsb uses Networking=Disable, VGpu=Disable, ClipboardRedirection=Disable and peripheral redirection disabled. The sandbox sees input and offline bundle read-only, plus ONLY a fresh per-run writable outbox. It does not map the source checkout, user home or credentials.
4. An ephemeral guest Windows session starts local Python/Git/Ollama/OpenCode from the approved offline bundle, runs the existing isolated worktree/SQLite Factory, performs deterministic independent checks and at most one repair, and emits a bounded receipt.
5. The host rejects mismatched source SHA, task spec, run ID, file scope, SHA256, paths, NTFS reparse points and oversized data; only exact modified bytes are imported into a separate host Git worktree. The checked result becomes a local integration commit. No GitHub push occurs.
6. An interrupted run resumes its original receipt ID; if the result is missing, WAITING_RECEIPT/HOLD is reported and no duplicate AI execution occurs. STOP.REQUESTED still pauses between tasks.

## Offline bundle, no auto-download

User-supplied offline folder needs python/python.exe, git/cmd/git.exe, ollama/ollama.exe, opencode/opencode.exe, their portable dependencies and a models folder. Existing source/credentials are NOT included in the bundle. The generated manifest SHA256 attests four executable files, not the model weights, DLL dependency chain or publisher identity; owner supply-chain review remains necessary.

Create a manifest with: python -m scripts.prepare_offline_bundle --offline-bundle D:/AXDEV_BUNDLE
Record its printed SHA256 privately. The command refuses overwrite, installs nothing and does not call any models.

Read-only entrypoint: python -m scripts.run_sandbox_queue --repo D:/APP --plan D:/PRIVATE/plan.json --state D:/PRIVATE/AXDEV_STATE --offline-bundle D:/AXDEV_BUNDLE --bundle-manifest-sha256 [64 hex].

First actual disposable test, only after owner prerequisites: append --max-tasks 1 --execute --confirm-isolated-run. RUN_SANDBOX.cmd delegates to this CLI. No automatic host-model fallback exists. Exit codes: 0 for completed verified local tasks, 2 for HOLD/preflight error and 3 for pending receipt/blocked queue.

## Limitations and deferred P2 validation

- Windows Sandbox is not supported on Windows Home; Pro/Enterprise/Education need virtualization. The local machine edition is NOT VERIFIED.
- vGPU is disabled for lower attack surface; the guest model may run only on CPU, reducing GTX1050Ti speed.
- The actual WindowsSandbox.exe invocation, guest identity, portable Python/Ollama/OpenCode compatibility, model tool calls, result transport, one-fix, crash resume, filesystem, network and memory isolation are NOT_RUN.
- Read/write outbox still represents a host mapping; host must never execute content returned by the guest. Strict receipt import and SHA validation are not equivalent to independent OS proof.
- No real user data or model weights have been uploaded anywhere. Existing automatic GitHub checks remain configured, but current-source CI was deliberately not inspected during P1.

## Reference documents

Microsoft Windows Sandbox configuration: https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-configure-using-wsb-file
Windows Sandbox prerequisites: https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-install
Windows edition support: https://learn.microsoft.com/en-us/windows/security/threat-protection/windows-sandbox/windows-sandbox-overview
