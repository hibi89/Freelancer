# F13 SHA-pinned import + queue integration: hosted live verification

**2026-11-16 11:10 KST**

| Item | Evidence |
| --- | --- |
| Repository/branch | `hibi89/Freelancer@tools/ax-dev-factory-local` |
| Source SHA | `160babf5143d1b866cd3958df4f0ebab6afdfc3b` |
| Hosted CI | https://github.com/hibi89/Freelancer/actions/runs/43790449613 |
| Hosted Python3.11 | **34 PASS / 0 FAIL / 0 SKIP** |
| Blueprint gate | https://github.com/hibi89/Freelancer/actions/runs/43790450087 — SUCCESS |
| Live public GitHub HTTP | **SUCCESS**, from `axdev sync-plan` on runner |
| First live import | `created: true, tasks: 1, executed: false` |
| Repeated live import | `created: false, tasks: 1, executed: false` |
| Source HEAD | `160babf5143d1b866cd3958df4f0ebab6afdfc3b` |
| Public plan SHA256 | `e02daa2ad587b6d4dc22dea4155663be03ffd67ec4f448cb31aaea82e0900c2c` |

### Verified behavior

The CI job executed the actual importer against public GitHub REST
without a GitHub token. It checked the source branch SHA, downloaded
`examples/sample-plan.json` by pinned 40-hex commit SHA, verified Git
blob/content and strict task contract, wrote a new local approved file,
then reimported without modifying the identical existing file. Doctor
read the resulting plan. Source was only READ; no git push, PR or model
execution. Python bytecode/CLI and synthetic worktree tests passed.

Synthetic unit tests also covered GitHub ref race, blob tampering,
invalid source identifiers, symlink output/parents, immutable local
approved plan SHA256, remote SHA change HOLD before coder, and
transport-down fallback to SHA256-identical local cache.

### Limitations and STOP gates

The new queue integration still has no real Windows host run, real
OpenCode process, GPU measurement, or permission policy enforcement
evidence. A transport outage means the remote branch cannot be checked;
the unchanged owner-approved local plan may still be used, explicitly
marked offline in logs, not claimed fresh. GitHub HTTP 403 and SHA
mismatch are not suppressed. No plan upgrade without a reviewed new
SHA, and no automatic push/PR/deploy. Public-only remote plans; local
private plans stay outside the public repository.

**Formal full blueprint completion: UNASSESSED.**

### Rollback / next

Code rollback reference: `6b592b689e36374ce63d321c752de50cbffbbf54`.
No force or history rewrite. Next: on-device disposable OpenCode/Ollama
smoke and Windows permission policy checks; then explicit owner-approved
PR publication (not implemented).
