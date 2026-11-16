# AX Dev Factory — P2 independent audit packet (2026-11-16 KST)

**Source to audit:** `hibi89/Freelancer@tools/ax-dev-factory-local`, exact functional commit `9d6fe7f2300fbf135685a71d606a744a9e2d743e`. Do not substitute the later docs-only HEAD, main or another product branch. Git history is the rollback reference. Personal owner-only local tool; F01–F20 code implementation 20/20 candidate, formal verified completion UNASSESSED.

## Available evidence

- [Full GitHub Actions #43817078016](https://github.com/hibi89/Freelancer/actions/runs/43817078016): Linux 133 PASS/0 FAIL/0 SKIP, hosted Windows 132 PASS/0 FAIL/1 SKIP and CMD disposable synthetic smoke.
- [Original P1 FAIL #43814585404](https://github.com/hibi89/Freelancer/actions/runs/43814585404): Git trust global dormant LFS caused most errors; an outdated test asserted the old P1 matrix count.
- [P2 first repair commit](https://github.com/hibi89/Freelancer/commit/079d54bc6da1c1596d43bf116355af07b3f0e54d), [F14/F15/F19 synthetic test commit](https://github.com/hibi89/Freelancer/commit/9d6fe7f2300fbf135685a71d606a744a9e2d743e).
- Real owner Windows10 GTX1050Ti, Ollama/OpenCode invocation, OS isolation/no-egress, GPU performance, actual EAI bridge execution and production/real-project acceptance: **NOT_RUN**. Hosted synthetic tests do not prove these.

## Codex GPT-6.1 Sol Max — independent technical/security audit

Review the exact source SHA without adopting developer conclusions. Inspect the immutable task SHA and dependency transition rules, SQLite crash recovery and double execution, one-fix/HOLD, Git worktree/ignored-file/symlink/NTFS reparse handling, Git hooks/filter/attributes (including global defaults), subprocess environment scrub and provider/CLI policy enforcement, EAI SHA + advisory receipts, AXNODE typed checkpoint equivalence, semantic reviewer prompt/response bounds and localhost-only model access. Verify test assertions against implementation rather than marking test existence PASS.

**F18 adversarial focus:** guest input is read-only but the per-run outbox is guest-writable. Determine whether an untrusted model, approved test script or modified source can forge/replace `receipt.json`, bypass independent acceptance, race the host importer, or misuse host-mapped directories. Review guest account restrictions, Windows Sandbox .wsb settings, archive/mapping/manifest pins, source/guest SHA distinction, guest binary chain, receipt schema, no replay, and host `_reconcile` trust boundaries. Treat potential attacks as hypotheses until reproduced; if acceptance can be forged, return SECURITY HOLD and propose a truly independent verifier/isolated second-pass solution. Never run untrusted output on the host to paper over this gap.

Report PASS/FAIL/UNVERIFIED for each F01–F20, reproducer or exact code locations for every problem, recommended minimal patch and regression tests, remaining environment blockers and impact on security. No direct edits to main, force pushes or remote publishing; if creating fixes, use the owner-authorized AX Dev Factory branch and preserve exact reviewed SHA references.

## Astra Max — independent frontend/UX audit

Evaluate `scripts/owner_dashboard.py` and `docs/OPTIONAL_UI_ADAPTERS.md`: stop/resume/status correctness, owner-only loopback access, no secrets/source snippets in responses, clear distinction `IMPLEMENTED` vs `VERIFIED`, HOLD and retry visibility, error handling, Windows accessibility/usability, truthful CPU/GPU and cost metrics. Do not claim rendered-browser verification when unavailable; separate source review from interactive Windows evidence. No scope changes or unapproved GUI frameworks.

## Integration and physical acceptance

High consolidates independent findings, accepts/rejects evidence and addresses defects before repeating affected tests and one full regression. On-device disposable trial is a separate final gate: Windows edition and virtualization, trusted offline Python/Git/Ollama/OpenCode bundle, model capabilities, no network egress, sandbox guest launch/receipt import, a real approved file edit + deterministic independent acceptance, STOP/reboot/idempotency, RAM/VRAM/latency. Windows Home must fail closed; any alternate isolation strategy requires owner approval. Report no real-use approval until all required gates are proven.

## Handoff semantics

Status snapshot and test counts live in `STATUS.md` and `HANDOFF.md`. Existing `docs/REQ_IMPLEMENTATION_MATRIX.json` and `docs/PRE_CI_IMPLEMENTATION_TRACKER.md` are P1 pre-CI snapshots, not a new P2 acceptance score. Do not reinterpret their historical NOT_RUN field as current hosted test state.
