# CITEVAULT AX — P85 durable tenant prototype evidence
**Verified: 2026-11-13 KST. Full owner-blueprint target: 85%. Official final completion: UNASSESSED; 85% not verified.**

## Exact scope and approved design

The original enterprise CITEVAULT design requires real user authentication and document ACL *before* raw bytes/index loading, version/delete/reindex lifecycle, model/evidence, original PDF/DOCX, Windows/Linux, real PREP/SMAX approval, and final customer validation. The earlier RAG original's `loadPackage` eagerly loads its entire package. Its session document selector cannot be treated as a true pre-read enterprise ACL.

| Option | Cost/complexity | Failure and maintenance | Decision |
| --- | --- | --- | --- |
| A. Append-only JSON state alongside a local search wrapper | Low initial code | Missing transaction atomicity and concurrent revision protection | Not selected |
| B. **Node 22 built-in SQLite metadata + isolated source vault** | No new npm package or network; local SQLite uses Node experimental `node:sqlite` | ACID revision+audit, version/revocation checked at every request; still prototype, not an IdP | **Implemented/tested** |
| C. Standalone enterprise IdP/server/DB and full RAG document migration | Realistic end-state but larger scope | Requires real customer identities, permission change, consent, secure deployment and model licenses | Deferred pending required approvals |

Existing `enterprise/p85-vault.mjs` and `enterprise/p85-loopback.mjs` remain **synthetic-only**; no external listener, no actual identities, no private customer sources, no network model API.

## Implemented and source-bound to exact GitHub blobs

| Path | Blob SHA | Verified function |
| --- | --- | --- |
| `enterprise/p85-vault.mjs` | `d6be6e910f6baa995d99d78fc250f28e8ae30465` | Existing scrypt login/15-minute sessions; optional store-backed account/document metadata, ACL before raw read, cross-instance revoked-account checks, tenant-scoped retire/version/reindex; metadata mutation with audit in one transaction |
| `enterprise/p85-state-store.mjs` | `de3193c5132163d60ecd142d7dbb105fdbaf5cb4` | Fixed local `citevault-synthetic-state.sqlite` path, bounded/symlink-rejected file, initial seed only once, transactional document revision + audit, persistent revoked accounts, tenant-filtered document and audit retrieval, fails closed on stale concurrent generation |
| `enterprise/p85-loopback.mjs` | `573b326574127c16a8ab8a97819f867511b7c323` | Local-only `127.0.0.1` HTTP account revocation endpoint, source/search, data lifecycle; no CORS, bounded JSON body |
| `tests/p85-vault.test.mjs` | `5e455611732c067bbcbcd7c5b8ea005e775e3dea` | Original 27 session, tenant ACL, document version, symlink and audit tests |
| `tests/p85-loopback.test.mjs` | `147bded3723d5859f17b3a5e49710d84bcff3a09` | 17 actual loopback HTTP security regression tests including revoke and cross-tenant denial |
| `tests/p85-state-store.test.mjs` | `57c905aeaa7c326f01b18fc3b3694edaadc3bb9e` | 14 SQLite restart/rights/version/revocation/concurrency/transactional audit tests |

Original pinned RAG `hibi89/RAG_STUDIO@c5867b3951f51bfa97cadd1aad8fb13e9cf9e604` unchanged. Private PREP/SMAX sources unchanged; no real customers, accounts, payments or permissions changed.

## Exact local execution evidence

Linux Node v22.16.0; all source/test files above compare against their GitHub blob SHAs via `git hash-object`. Actual tests:

```bash
node --check enterprise/p85-vault.mjs
node --check enterprise/p85-state-store.mjs
node --check enterprise/p85-loopback.mjs
node --test tests/p85-vault.test.mjs tests/p85-loopback.test.mjs tests/p85-state-store.test.mjs
# 58 total / 58 PASS / 0 FAIL / 0 SKIP
```

Combined P50/P70/P85 exact-source local test run: **95 total / 92 PASS / 0 FAIL / 3 SKIP**. All 3 SKIPs require a separately available pinned RAG original checkout; not integration PASS. The P70 V8-only 24-case policy check is historical and **not included** in the 95 Node run.

`.github/workflows/citevault-p50.yml` blob `8e0613422b58d886ae136bbd8ca694929b7f737b` includes Linux Ubuntu24.04 Node22.16 and Windows2022 Node22.23 P85 matrix; **hosted Actions run ID, job logs, and Windows test results not obtained**. PDF/DOCX native original RAG tests also remain hosted unverified.

## Security and consistency results (limited to synthetic fixture)

- Passwords are derived into scrypt verifiers; SQLite inspection found **no plaintext test passwords or document body bytes**. Sessions stay process-local; a restart invalidates tokens. Persisted disabled accounts block future login and immediately block an already authenticated session in another process.
- Reopening with a forged new accounts/docs seed does not overwrite existing metadata. Retired documents remain inaccessible across restart and across two simultaneous vault instances. Old source bytes remain unchanged.
- Document version and its matching SHA-256 must exist before activation. Stale concurrent generation rejects both proposed mutation and audit event; successful version/reindex/retire/revoke commit corresponding audit events transactionally.
- Tenant admin A cannot inspect or revoke tenant B's documents/users; cross-tenant audit listing filters events. Invalid/unknown source paths never leak raw filesystem paths in API JSON.
- Source remains synthetic line-based only. Correct real PDF-page/DOCX-paragraph numbering, native prep/SMAX source approvals and production tenant indexes are *not supplied* by this prototype.

## Remaining entire-blueprint P85 blockers

1. Actual customer-backed IAM/IdP identity verification, durable enterprise provisioning, group/collection revocation, password policies/rate limits hardened for production and tenant-specific actual index/search-before-load.
2. Original RAG native **PDF+DOCX 2+ document** integration with source page/paragraph citation and SQL totals actually executed on the exact pinned SHA, plus signed authorized PREP/SMAX→AX export and rights approvals.
3. Small Korean local model quality and license benchmark, prompt-injection and data leak tests with controlled evaluation sets.
4. Real hosted Linux/Windows CI run evidence and actual Windows 10/11 hardware verification (hosted Windows build is not the same as physical Windows customer acceptance).
5. Full owner-approved 100% blueprint requirement weighting and final scored acceptance (not a synthetic test-count ratio).

**Status: [작업중], official UNASSESSED, target 85% not proven, RELEASE HOLD / SALE NO-GO.** Continue only with evidence-based source changes and required approvals. Do not count configuration commits as a CI success.
