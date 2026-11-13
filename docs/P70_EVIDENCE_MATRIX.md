# CITEVAULT AX — P70 implementation and verification matrix (2026-11-13 KST)

## [2026-11-13 KST] P70 second push — executed Node guard and local byte-bound PREP/SMAX review

**New source (GitHub source and test blobs exactly matched by local `git hash-object`):**
- `enterprise/p70-citation-contract.mjs` blob `03f09a31ded87cefe728f381511512f93b44b6b8`: extracted shared validator for original RAG bridge. A `FOUND` result with zero citations now **rejects**; validates original RAG file_id, source line, quote budget, scoped ID list, `NO_EVIDENCE` abstention and distinct conflicting day periods.
- `tests/p70-citation-contract.test.mjs` blob `c62eeeed6958d771fd6a0ddfe633d6da8eed6b59`: 14 Node22 assertion tests; `enterprise/p70-rag-bridge.mjs` imports this exact validator rather than the previous inline function.
- `enterprise/p70-local-review.mjs` blob `0e8929298b879947117fd2c1bd30d3074bbdcfcc`: reads only three bounded fixed-named local files (`sales.csv`, `smax-review.json`, `prep-mapping.json`) for **synthetic** PREP/SMAX review. Checks real bytes SHA-256; symlink/hardlink/TOCTOU bounds; UTF-8/CSV/field mapping/tax unknown/row-count; BigInt quantity × price = amount with exact provisional total. **Always** returns `REVIEW_HOLD`/`approval NOT_GRANTED`, no AX package, no customer ownership or native SMAX signature, `row_lineage_verified:false`. It is **not** an actual SMAX producer or commercial importer.
- `tests/p70-local-review.test.mjs` blob `9d87f01fc53b06d7592db2a347788ce5f9361345`: 17 Node22 tests with temp synthetic CSV/JSON files including actual file byte reads, 5-column mapping, digest failures, fake approval, tamper, symlink/hardlink, Excel formula-like CSV ID and source unchanged checks.

**Actual execution**, container Linux Node v22.16.0, 2026-11-13 KST:
```sh
node --test tests/p70-citation-contract.test.mjs tests/p70-local-review.test.mjs
# 31 PASS / 0 FAIL / 0 SKIP, 31 total
```
Combined with the previous exactly source-bound P50 standalone tests: **37 total / 34 PASS / 0 FAIL / 3 SKIP**. The three skipped cases are the original RAG checkout SQL/BM25/SMAX integration. **Node integration tests for original RAG/PDF/DOCX, Hosted Actions, real identity and real producer approval still not executed.**

**Original RAG code-path inspection and in-memory V8 execution:** Actual original `src/document-search.mjs` blob `4a39383e37f33532c2ee5f94bcc52bb1c04b861f` + `src/knowledge-base.mjs` blob `3dfd6495ad1e7a59ef4f7b5661bb3350e0afe608` (pinned `c5867b39`) were evaluated against exact public returns/shipping fixture text in a separate pure JS harness (no filesystem package loading). **5 positive comparison assertions passed** including FOUND, NO_EVIDENCE, full-corpus conflicting 7/14 days, and forged empty evidence refusal. This does **not** prove original `loadPackage`/SHA/runtime native PDF integration.

**Discovered and corrected:** previous `enterprise/p70-rag-bridge.mjs` accepted `status:'FOUND'` without any `evidence` because its inline validator checked only items in arrays that existed. New helper enforces citation cardinality and documented source units, with 14 Node regression tests. Hosted run still unverified.

**Workflow:** `.github/workflows/citevault-p50.yml` now has independent `local-contracts` Node22 job (no package installation, 31 tests) plus original pinned `synthetic-evidence` job (P50/P70 and RAG P512/P538/P540/P549). GitHub Actions push run and job logs **unknown**, not declared PASS.

**Final-design boundary:** P70 enterprise **model** and local synthetic source mapping review tests are stronger. Production ACL-before-load, authenticated employee identity, native customer-authorized PREP/SMAX → signed/approved AX export and real native PDF/DOCX app E2E remain missing/unverified. Official final-design completion **UNASSESSED**; 70% goal **not verified**. `[작업중]` and `RELEASE HOLD` retained.



**Owner goal:** 70% of the *complete approved* enterprise blueprint. **Result:** partial implementation; official score **UNASSESSED** and 70% milestone **NOT VERIFIED**. Keep `[작업중]`, `RELEASE HOLD`, `SALE NO-GO`. This document cannot redefine the approved 100% denominator.

## Architecture decision (previous blueprint solution B retained)

| Design | Performance / cost | Maintenance / safety | Decision |
| --- | --- | --- | --- |
| Rebuild full SQL, PDF, DOCX, ACL and model within Freelancer | Expensive and slow; duplicative; risks drift from original RAG | Separate security bugs and divergent data contracts | Reject |
| **Separate P70 synthetic policy + exact-source RAG adapter + pinned original RAG regression** | Small deterministic code, no paid model API; reuses already tested RAG native parsers | Clear source custody, easy rollback, **does not falsely become enterprise IAM** | **Adopt for development** |
| Deploy existing localhost RAG bearer to corporate LAN as "multi-user" | Low upfront coding cost | No verifiable employee identity or department isolation | Reject |

**Exact original engine:** `hibi89/RAG_STUDIO@c5867b3951f51bfa97cadd1aad8fb13e9cf9e604`. Current implementation branch: `hibi89/Freelancer@product/rag-enterprise-knowledge`; restore to pre-P70 `6c36d02e71a751c8473b0bb36c9dc8b2c5ed460c` without force pushes if necessary.

## Implemented source and evidence

1. `enterprise/p70-policy.mjs`: bounded synthetic-only tenant/group/project/clearance/expiry checks, **deny whole mixed selection**, data-filter-first keyword ranking, corpus-wide return-policy conflict suppression, deterministic `SEARCH_ONLY` fallback, explicit `identity_verified:false`. No tokens, network or external model. Synthetic line indices are **not** called real PDF page numbers.
2. `enterprise/p70-policy.mjs` also contains PREP/SMAX proposal binding: explicit source digest string, approved column role *proposal* shape, tax-basis label and immutable `REVIEW_HOLD`, no producer promotion/real reviewer authority.
3. `enterprise/p70-rag-bridge.mjs`: chooses authorized **synthetic** scope then uses original `knowledgeSearch` for real, SHA-verified RAG package excerpts; original errors become generic `REVIEW_HOLD`. Every returned citation and selection scope is checked again against the authorized ID list.
4. `tests/p70.test.mjs`: **24/24 PASS in isolated pure-JavaScript V8 execution using exact remote GitHub policy/test source**, 0 FAIL. Covers roles, tenant, group/project, clearance, expiry, mixed-selection denial, unknown-vs-forbidden parity, conflict, injection inertness, model-less fallback, SMAX review refusal. **This is not a hosted Node run**, security review or customer IAM acceptance.
5. `tests/p70-rag-integration.test.mjs`: 6 Node regression cases for pinned real RAG scope, direct and mixed denied IDs, missing original checkout, and nonexistent tenant. **Authored, not executed in this evidence set**.
6. `.github/workflows/citevault-p50.yml`: configured read-only checkout of pinned original source, Node 22, original `tests/p512-native-document.test.mjs` / `tests/p538-full-corpus-conflict.test.mjs` / `tests/p540-native-collection.test.mjs` / `tests/p549-prep-smax-boundary.test.mjs`, plus product P50/P70 tests. **Run ID / job status / PASS not verified**. Do not count configured tests as passed.

## Full-design 50 and 70 requirement truth table

| Blueprint milestone | Grounded product evidence | 2026-11-13 verification state |
| --- | --- | --- |
| P50 original RAG fixed SQL + BM25 + citations | Original source inspected, new P50 gate, original fixture KRW 157,000 | New P50 standalone test 3 PASS / 3 SKIP; pinned actual RAG integration **UNVERIFIED** |
| P50 real PDF and DOCX + no mutation | Original `P512/P540` source tests selected in workflow | Original hosted run **UNVERIFIED** |
| P50 single SMAX producer → approved AX export | No authenticated producer/reviewer sign-off | **NOT IMPLEMENTED / HOLD** |
| P70 PREP/SMAX source mapping review and approval isolation | Original RAG `P549` bounded PREP/SMAX review code + pure P70 review refusal | Exact integration run pending; **real reviewer sign-off absent** |
| P70 >=2 PDF/DOCX simultaneous corpus | Original `P540` native collection source implementation | **Source exists; CITEVAULT execution unverified** |
| P70 full corpus contradictory policy HOLD | Original RAG `P538` and new synthetic deterministic policy | Synthetic pure check PASS; pinned original CI **unverified** |
| P70 model-absent evidence-only fallback | Pure `querySyntheticEvidence` returns only citations, no synthesis | Isolated V8 PASS; original browser/UI not linked |
| P70 roles/permissions model and tests | Synthetic tenant+group+project+clearance policy with prefilter, 24 cases | Isolated pure JS **PASS**, no real identity or customer ACL acceptance |
| Enterprise IAM, ACL-before-*loading*/indexing, tenancy, provenance | RAG `loadPackage()` currently loads entire accepted package before knowledge selection | **NOT IMPLEMENTED**; never expose bridge to actual employees |
| Full final-design 100-point owner-approved weights | Per-requirement independently approved weights still unavailable | **OFFICIAL UNASSESSED**, cannot assert 70% |

## Security limitations / next required slice

- Real role grants must be established by an authenticated server-side identity, **not client-provided `identity_state`**. The current synthetic-only contract intentionally rejects claims of real enterprise auth.
- Original RAG `loadPackage()` loads entire accepted source package before document selection, so the wrapper cannot claim **ACL before raw loading** or tenant isolation. A separate access-authorized storage and index boundary is necessary before a customer deployment.
- Text in synthetic documents is evidence, never executable instructions. An attacker can still submit a forged synthetic fixture: this module has **no real identity, source-byte authorization or signed PREP/SMAX approval**.
- Never elevate original producer `NOT_GRANTED`, `REVIEW_HOLD`, or provisional tax semantics to `ACCEPTED`; actual owner/rights review and verified source digests are required before AX promotion.
- Other gaps: real local model benchmark and license, Windows 10/11 customer machine, source version/reindex and deletion, genuine customer Gold100, security review, legal/privacy and service signoff.

**Next actions:** (1) obtain exact hosted CI run evidence for pinned source, (2) implement authorized file-to-reviewer identity/signature and explicit approval/revocation *after owner approval for security changes*, (3) isolate per-tenant storage and index before read, (4) recompute entire blueprint using owner-approved 100-point weights; never infer a new percentage from test counts.

**Deployment:** None; Vercel Production not applicable. All changes are source+synthetic QA on existing private product branch; original RAG, PREP, SMAX and customer data unchanged.
