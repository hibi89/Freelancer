# CITEVAULT AX — P70 implementation and verification matrix (2026-11-13 KST)

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
