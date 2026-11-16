# AX Dev Factory — GitHub Trending reuse decision (2026-11-16 KST)

**Status: research/architecture decision only. No third-party code installed or executed and no automatic integration has occurred.** Internal personal-use tool; source `hibi89/Freelancer@tools/ax-dev-factory-local`; repo is PUBLIC, customer/secret data prohibited. Owners' GTX 1050 Ti / RAM16GB / Windows10, one local coder + deterministic reviewer. Preserve existing EAI and AXNODE repositories, all existing product branches.

## What was examined and evidence quality
- Central historical 69-repository index: `hibi89/hackathon-command-center-2026@github-trending-daily/docs/github-trending/RESEARCH_HISTORY_INDEX.md`.
- Daily 2026-11-06..15 accumulated log; weekly 2026-11-09 historical **alternative** TOP30 (official GitHub Trending unavailable), monetization concepts master (30 categories), recent 11/13..15 findings. This is a historic candidate corpus, not a verified 2026-11-16 ranking.
- Official upstream README/config/installation/licence pages checked 2026-11-16 for selected projects below. **Not** all ~69 repos had individual code, dependencies, licence texts, malware, Windows execution and latest commits audited.
- No original/customer source, environment variables or private GitHub credentials transmitted to third-party AI tools.

## Decision matrix — adapt rather than bundle everything

| Priority | Upstream and role | Decision | Why / duplicate guard | Runtime constraint / test |
|---|---|---|---|---|
| **P0** | [astral-sh/ruff](https://github.com/astral-sh/ruff): deterministic Python lint and formatting checks | **ADOPT AFTER EXTERNAL CLI ALLOWLIST REVIEW** | Very fast single native binary; supplements protected Python unittest; never let coder silently `--fix` or overwrite | Installed binary/version pin and `ruff check` no-write acceptance; Windows/host NOT_RUN; MIT |
| **P0** | [obra/superpowers](https://github.com/obra/superpowers): TDD, systematic debugging, verification-before-completion | **REUSE 2-3 SELECTED SKILL PROCEDURES, NOT WHOLE MULTI-AGENT RUNTIME** | Complements existing coding/review/recovery SKILL.md; prevent duplicate skill instructions & huge context | Test skill selection/summary under 3B/4B model; no subagents; MIT |
| **P0** | [github/spec-kit](https://github.com/github/spec-kit): specification→plan→tasks→convergence | **USE AS HIGH TASK-BREAKDOWN REFERENCE/TEMPLATES** | High already creates approved task JSON; avoid rerunning full SDD phases for every 1-file patch | `specify` install only if it improves conversion to immutable TASK IDs; not an unattended local requirement |
| **P1** | [vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser): browser-based functional acceptance | **OPTIONAL ADAPTER** | Only for web apps: DATA2WEB/DBVORA/FFAX, after scripted tests | One browser, explicit localhost allowlist, synthetic credentials, fixed assertion, OS process isolation; existing `docs/OPTIONAL_UI_ADAPTERS.md`; NOT IMPLEMENTED |
| **P1** | [Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify): AST/code relationships | **OPTIONAL LARGE-REPO CODE-ONLY INDEX** | For complex unfamiliar dependencies; skip for tiny tasks | `--code-only`, `GRAPHIFY_BACKEND=none`, exclude docs/media; logs sensitive, disable logs as needed; Linux/Windows untested |
| **P1** | [QwenLM/qwen-code](https://github.com/QwenLM/qwen-code): alternative coding CLI with local Ollama | **A/B AGAINST CURRENT OPENCODE, DO NOT RUN BOTH** | Compare SAME five High-approved synthetic jobs with matched models and review; switch if more completed jobs/hour | Node >=22, identical model, version and time budget; no claims that Qwen Code solves 3B reasoning limit |
| **P2** | [vercel-labs/agent-desktop](https://github.com/vercel-labs/agent-desktop): Windows GUI accessibility testing | **OPTIONAL AFTER REAL WINDOWS APP EXISTS** | Not needed for ordinary CLI/web projects; can inspect private desktop data | Window/app/process allowlist, no blanket desktop clicks; existing optional adapter document; NOT IMPLEMENTED |
| **P2** | [backnotprop/plannotator](https://github.com/backnotprop/plannotator): local interactive code review | **OPTIONAL ONLY FOR HOLD/OWNER ESCALATION** | Helps mobile/desktop user review stalled plans/diffs; **not** automatic independent semantic reviewer | Human interaction still required; local server and dependency scope review; MIT/Apache-2.0 |
| **P2** | [max-sixty/worktrunk](https://github.com/max-sixty/worktrunk): git worktree management | **DEFER** | AX Dev Factory currently uses built-in `git worktree`, only one coder; extra binary adds negligible immediate benefit | Windows `git-wt` possible, adopt only for multiple workers; MIT/Apache-2.0 |
| **P2** | [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem): persistent session memory | **DEFER** | Already have GitHub STATUS/HANDOFF + SQLite immutable task contracts; assess only after empirical context-loss incidents | Extra process/storage and possible model integration; no sensitive activity logs to public GitHub |
| **P2** | [cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill): adversarial security audit | **BORROW REPORTING DISCIPLINE ONLY; FULL HARNESS DEFER** | Full multi-agent parallel review requires tool-using model and OS sandbox, unsuitable for 1050Ti v0.1 | Can reference confirmed/needs-validation/rejected outcome format; no unsupported claims of independent security audit; MIT |
| **P2** | [ChromeDevTools/chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp), [GoogleChrome/modern-web-guidance-src](https://github.com/GoogleChrome/modern-web-guidance-src) | **DEFER** | Overlaps agent-browser on basic UI acceptance; use for specialized console/perf diagnostics after browser smoke proven | Chrome runtime/remote debugging must be isolated; no exposure outside localhost |
| **P3** | [pingdotgg/t3code](https://github.com/pingdotgg/t3code) | **DEFER** | Mobile dashboard for already configured agent may be useful, but doesn't produce extra local reasoning or remove paid provider caps | More server/UI and authentication/network exposure; one-worker 1050Ti takes priority |
| **P3** | [milind-soni/OpenMausBot](https://github.com/milind-soni/OpenMausBot), gstack, ECC, other multiagent suites | **SKIP FIRST PROTOTYPE** | Huge overlapping orchestration, VM or subagent burden; no proven productivity gain over local single coder and deterministic verifier | Re-evaluate only after stable 5–10 task benchmark |

### Outside target
Scrapling, auto-ontology, finance/stock tools, Handy/VibeVoice, image/video/media, smart-home, Uptime Kuma, LZ4, web design frameworks, generic cloud/provider/API gateways are useful in OTHER products, **not** the minimum local coding/verification factory. Avoid buying a GPU or adding model packages solely on trending popularity.

## Recommended minimal 1050Ti stack
1. GitHub's approved `AGENTS.md`/final blueprint + High-created tiny immutable task contract; reference *selected* Spec Kit structure, no live Spec Kit server.
2. Existing AX Dev Factory **Python+SQLite** queue, git worktree isolation, one worker, per-task SHA and one-fix/HOLD; no unattended PR until authorization security reviewed.
3. **Exactly one** local Ollama model + choose OpenCode OR Qwen Code after 5-task A/B test; avoid two concurrent language-model inference contexts.
4. Use Ruff `check` in separate deterministic reviewer stage for Python plus existing project acceptance tests. Optional Superpowers TDD/debugging text in role-specific skill.
5. For UI projects, after baseline passing, launch **one** approved agent-browser or agent-desktop probe, never both; only local synthetic data.
6. Graphify code-only only when task dependencies actually require it; no model-driven graph extraction.
7. Defect: no ready-made open-source tool makes a 3B/4B model GPT-6-level. Integration must check versions, APIs, credentials, model tool-use, RAM/VRAM, permissions, licences and actual Windows behavior.

## Highest priority to unblock real trial
- Verify exact OpenCode v2 schema and local-only configuration/permission policies under real installed CLI version, including denial of cloud providers, shell misuse, secrets and external directories. The current repo's JSON policy has not been live-validated.
- Fix on-disk plan import/task sync and push/PR *only after* local synthetic real-model success and GitHub access-scope decision; currently **NOT IMPLEMENTED**.
- Run disposable fixed 5-task benchmark on host with Qwen2.5-Coder 3B vs installed Qwen3-4B and optionally Qwen Code/OpenCode; record success/test count, average minutes, peak RAM/VRAM and max context.
- Only implement per-need optional adapters, not unconditional package installs and not third-party source vendor-copy.

## Integration estimate (ENGINEERING GUESS, not elapsed time)
- Map selected TDD/debug skill and add Ruff protected check: 1–3h with version/permissions tests.
- One approved browser acceptance adapter: 2–5h beyond working localhost app.
- Graphify code-only A/B on one small repo: 1–3h optional.
- Qwen Code vs OpenCode A/B: 2–5h excluding slow 1050Ti inference and installs.
- All are additional to first host model-backed E2E. A code repo being complete does NOT mean integration is just a file copy.

## Sources and licensing
Upstream docs verified separately on 2026-11-16; software licences must be pinned and reviewed again for the exact revision and dependency tree before copying binaries or shipping. Personal internal use only; third-party tools are *not* bundled. Reference sources:
- https://github.github.com/spec-kit/
- https://github.com/obra/superpowers
- https://github.com/astral-sh/ruff
- https://github.com/vercel-labs/agent-browser
- https://github.com/Graphify-Labs/graphify
- https://github.com/QwenLM/qwen-code
- https://github.com/backnotprop/plannotator
- https://github.com/max-sixty/worktrunk
- https://github.com/vercel-labs/agent-desktop
- https://github.com/cloudflare/security-audit-skill
- https://opencode.ai/docs/config
- https://opencode.ai/docs/permissions
