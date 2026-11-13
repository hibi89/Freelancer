# CITEVAULT AX — P85 original blueprint acceptance evidence (2026-11-13 KST)

> **Target requested:** full owner-approved product blueprint 85%. **Verified product-wide final completion remains `UNASSESSED`**. This document records actual implementation evidence rather than converting local test counts into completion percentages. Keep `[작업중]`, `RELEASE HOLD` and `SALE NO-GO`.

## Design alternatives and decision

| Approach | Execution/cost | Security and maintenance | Outcome |
| --- | --- | --- | --- |
| A. Reuse RAG Studio `loadPackage()` and filter documents *after* package load | Smallest code changes, but all authorized tenant package bytes already opened | Raw-file access and index could bypass employee ACL; local bearer is not corporate identity | **Rejected for enterprise ACL** |
| B. **Separate local tenant-owned vault with password login and ACL-before-file-read** | No paid services and deterministic Node stdlib tests; currently TXT/MD-like line evidence only | Read path, group/project/clearance and exact SHA checked per tenant before any bytes are read; clear independent rollback | **Chosen for isolated synthetic P85 proof** |
| C. Deploy full multi-tenant IAM/IdP, model, real PDF pipeline and corporate storage at once | Higher operational complexity/cost, needs real identity, user accounts and data-rights approvals | Proper long-term product route but requires authorization and signed customer requirements | **Deferred for explicit owner authorization and environment** |

## Implemented source and exact tested blobs

**Repo:** `hibi89/Freelancer@product/rag-enterprise-knowledge`. No changes to `hibi89/RAG_STUDIO`, `SMAX`, `prep` source; original RAG pin `c5867b3951f51bfa97cadd1aad8fb13e9cf9e604`.

| File | GitHub blob SHA | Scope |
| --- | --- | --- |
| `enterprise/p85-vault.mjs` | `378523e03e4d42fe899e702504f8c37b6c23454e` | Synthetic scrypt-derived account verifiers, random opaque sessions, TTL/logout/rate lockout, tenant/group/project/classification ACL *before source read*, verified immutable source SHA, cross-tenant audit separation, active version/retirement and admin-only reindex |
| `tests/p85-vault.test.mjs` | `5e455611732c067bbcbcd7c5b8ea005e775e3dea` | 27 Node regression tests; wrong identities/tokens, tenant/project/group isolation, mixed selection refusal, lifecycle, stale SHA and directory/symlink/hardlink refusal |
| `enterprise/p85-loopback.mjs` | `dee33df73c1f677713c11c89156f07fd4de40dfd` | IPv4 `127.0.0.1` only ephemeral HTTP, Bearer authorization, 401/403/404/409/413/415/422, request JSON/body budget, no CORS, `no-store`; not open as a normal customer server |
| `tests/p85-loopback.test.mjs` | `80a30bccb792a8a37104ec5376c55ce1dce4a4f3` | 15 HTTP integration tests exercising actual local socket, sessions, denied doc IDs, data-retaining retire, malformed request and response boundaries |

All four blobs **match local `git hash-object` outputs byte-for-byte**, not inferred from a filename.

## Real local command execution (Linux Node v22.16.0)

```sh
node --check enterprise/p85-vault.mjs
node --check enterprise/p85-loopback.mjs
node --test tests/p85-vault.test.mjs tests/p85-loopback.test.mjs
# total 42, PASS 42, FAIL 0, SKIP 0
```

Combined source-bound local regression of previously verified P50/P70 source:
```sh
node --test \
  /tmp/citevault-local/tests/p50.test.mjs \
  /mnt/data/citevault70/tests/p70-citation-contract.test.mjs \
  /mnt/data/citevault70/tests/p70-local-review.test.mjs \
  /mnt/data/citevault85/tests/p85-vault.test.mjs \
  /mnt/data/citevault85/tests/p85-loopback.test.mjs
# total 79, PASS 76, FAIL 0, SKIP 3
```
The three SKIPs are actual original RAG pinned checkout integration, not P85 tests. Original PDF/DOCX parser and the joined PREP/SMAX live approval remain unverified. P70 24-case V8 policy check exists as separate earlier evidence, **not** counted in the 79-case Node run.

## P85 requirement trace

| Original full-design requirement | Source / actual evidence | Status |
| --- | --- | --- |
| Authenticate users, groups, collections and document ACL | LocalSyntheticVault scrypt login + session TTL + groups/projects/classification/tenant filter and 27 tests | **Synthetic local auth prototype PASS; real enterprise trusted IAM NOT_IMPLEMENTED** |
| Prevent unauthorized docs from being read, indexed or leaked | Checked before `readDocument`, absent/forbidden indistinguishable, 401/403/404 HTTP, symlink/hardlink/SHA boundary, tenant audit filter | **Local synthetic negative cases PASS; full customer threat model NOT_VERIFIED** |
| Document version, retire and reindex | SHA-bound version activation, deny retired sources, in-memory admin reindex, original v1 bytes preserved | **Local run PASS; durable catalog, backup/restore, cross-process invalidation NOT_IMPLEMENTED** |
| Korean model small acceptance | No model download or cloud calls. Search-only citations and conflict abstention | **NOT_IMPLEMENTED / no license or model verification** |
| Windows/Linux CI | New `p85-loopback-contracts` matrix Ubuntu 24.04 Node22.16 and Windows 2022 Node22.23 | **Workflow definition committed; hosted job RUN/RESULT NOT_VERIFIED** |
| P50 full actual RAG PDF/DOCX/SQL and SMAX→approved AX | Existing `p50-gate`, RAG P512/P538/P540/P549 workflow references | **RAG pinned run/real producer approval unverified** |

### Restrictions and production blockers

- This code reads only fixed, explicitly seeded synthetic plain-text files, not actual customer PDF/DOCX/CSV rights-approved corpus. There is no production auth provider, password reset, durable identity/session store, document metadata DB, signed reviewer approval, real approved SMAX→AX import or enterprise backup/recovery.
- Do not expose the test HTTP application to the public network, treat its test accounts as real employees, allow it to authorize production documents, or claim its source SHA proves legal usage rights.
- `LocalSyntheticVault` catalog/version state and audit event log are **in memory**, and the content search is bounded deterministic lexical matching, not the original RAG native PDF/DOCX pipeline or a real local LLM. Production authentication and **ACL-before-index/IO** require additional architecture review and owner authorization.
- Local negative tests passed but do not prove 0 leaks under adversarial concurrency, race conditions, bypass attempts or all Windows environments.
- No customer/Private SMAX material, secrets, live authorization changes, external submissions, deploys or payment events were performed.

### Next gate

1. Obtain **actual** GitHub-hosted Linux/Windows matrix run IDs and logs; investigate failed jobs once with evidence rather than assuming green from YAML.
2. Run original pinned RAG native PDF/DOCX multiple document and PREP/SMAX source approval E2E; avoid pretending a synthetic `reviewState` is legal authorization.
3. Before real employee use: explicitly approve customer identity and permission changes; implement trusted verifier, durable per-tenant metadata/version/revocation, document-select-before-index and source package isolation, audit durability.
4. Run real Korean local-model benchmark with verified license, real customer consent/Windows 10/11 QA and original blueprint requirement-by-requirement owner-approved weighting before declaring 85% complete.

**Outcome:** code/test/CI definition pushed; 42/42 P85 local, 76/79 combined local (3 RAG integration SKIP); **official `UNASSESSED`, 85% milestone not verified, RELEASE HOLD**.
