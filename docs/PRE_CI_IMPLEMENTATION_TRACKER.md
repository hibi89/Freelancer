# AX Dev Factory — P1 pre-CI source implementation: 100% candidate

**Date:** 2026-11-16 KST. **Implementation:** F01–F20 = 20/20 (100%). **Code SHA:** 8edcbce2b7164cd1b2fdb875f596ceb67ff97b06.

- The 100% metric means all 20 F-ID code paths now exist **just before full CI and integrated acceptance**. It is NOT the official whole-product verified score. Formal verified completion remains UNASSESSED.
- F18 source includes an explicit Windows Sandbox host and guest controller. It runs local Ollama/OpenCode and deterministic acceptance only inside the guest, enforces disabled networking/clipboard/vGPU, mounts input and vetted offline tools read-only, and exposes only a new per-run outbox as guest-writable.
- The host imports only exact approved changed file bytes after comparing task SHA, run ID, pinned integration SHA, SHA256 hashes, size and scope. A missing result never retriggers a model call automatically. It only promotes local isolated Git commits; no remote push occurs.
- Windows Sandbox is not available on Windows Home. Supported Pro/Enterprise/Education editions need virtualization and a separately vetted offline Python/Git/Ollama/OpenCode/model bundle. With guest vGPU disabled, CPU inference can be slow.
- **P2 validation:** NOT_RUN/NOT_CHECKED for this new code, per owner instruction. Deferred tests are authored but unexecuted. Existing GitHub Actions were not disabled. Physical Windows 10 GTX1050Ti, security isolation, network egress and real-model tooling remain unverified.
- No OS policy change, Windows Sandbox launch, software installation, customer-source upload, paid API or GitHub branch/permission change performed.
- **Next action:** one bundled P2 CI, security, Windows guest+host tests and defect resolution; then independent Codex reviews. If owner's Windows edition cannot run Sandbox, report blocked and obtain approval for an alternative isolation backend rather than falling back unisolated.

Source details: docs/WINDOWS_SANDBOX_RUNTIME.md.

---

# AX Dev Factory — P1 code 100% gate (before CI)

**As of 2026-11-16 KST: 19/20 = 95% implementation-only.** Code source at e8f439484747c7c9e9d69880e9f940f65b627827.

F01–F20 code creation 100% triggers P2 full CI and integration acceptance; 95% is not an independently tested release. Original F18 OS isolation remains PARTIAL.

F18 current: preflight Git executable hook/filter protection; effective local-only Ollama/OpenCode policies; Windows Sandbox network-disabled config generator. Missing: real sandboxed model/reviewer execution and OS network proof. Do not mark implemented merely because a .wsb file can be prepared.

Full CI/manual Actions review is deferred under user instruction until source code is 20/20. Automatic GitHub required CI is NOT disabled. Historical test successes refer to historical SHAs only.

No customer data or local credentials exported; no public status publication or Task Scheduler registration occurred.

Canonical pre-CI code coverage: docs/REQ_IMPLEMENTATION_MATRIX.json and read-only scripts/req_status.py. Official completion remains UNASSESSED.
