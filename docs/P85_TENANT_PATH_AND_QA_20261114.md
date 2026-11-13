# CITEVAULT AX P85 — tenant-bound sales paths and deterministic test throughput
**Evidence checkpoint: 2026-11-14 KST. Product-wide 85% target NOT yet verified; official UNASSESSED.**

## Design choice and security decision

- **A. Trust a caller-provided `salesDirectory` after verifying only its string `tenantId`:** lower implementation cost but susceptible to a product operator/plugin accidentally mapping an authorized organization's policy label to a different organization's CSV bytes. Rejected.
- **B. Require a fixed, tenant-owned `<vault root>/<tenantId>/sales-only` path before CSV read:** minimal change, no external API or costs, straightforward cross-tenant regression. **Implemented**. The vault verifies the caller's authenticated tenant, groups, project and clearance, then verifies the exact absolute directory string and rejects a symlink or non-directory component.
- **C. Full independent per-tenant storage + signed policy + trusted employee IAM:** necessary for a real corporate release but requires verified customer identity and source-rights authorization. Not implemented by this change.

### Changed GitHub blobs, exact local verification

| Source | Git blob SHA | Change |
| --- | --- | --- |
| `enterprise/p85-vault.mjs` | `3256d1e52fed8bcf4748060478b381e9c5afe542` | Extend `authorizeSyntheticDataset` to require the verified tenant-specific sales path and reject symlinks before CSV reading |
| `enterprise/p85-journey.mjs` | `7e194a8def953e851e8413f217212338d033a994` | Pass the actual server-configured sales directory into the vault's pre-read authorization |
| `tests/p85-journey.test.mjs` | `40a171cadb662275f34c62f5f602ae3cdb7ab4d8` | Add forged-tenant path and symlink directory denial cases, cache only immutable synthetic PDF/DOCX fixture bytes (each test still receives its own mutable file copies), reuse immutable synthetic account verifiers |

All three files were saved to `hibi89/Freelancer@product/rag-enterprise-knowledge`, fetched again by the GitHub connector and matched to the corresponding exact locally tested `git hash-object` values.

### Test commands / actual results

Executed in the current isolated container, **Linux Node 22.16.0 / Python 3.13.5** (prior proof used Python 3.11; no claim of new Windows CI execution):

```sh
node --test tests/p85-vault.test.mjs                   # 27 PASS
node --test tests/p85-loopback.test.mjs                # 17 PASS
node --test tests/p85-state-store.test.mjs             # 14 PASS
node --test tests/p85-native-integration.test.mjs      # 13 PASS
node --test tests/p85-journey.test.mjs                 # 18 PASS
node scripts/p85-synthetic-demo.mjs --self-test         # PASS, REVIEW_HOLD
node --test --test-concurrency=1 tests/*.test.mjs      # 89 PASS / 0 FAIL / 0 SKIP
```

Native parser performs actual synthetic PDF page / DOCX Korean paragraph extraction; JSON/CSV rights remain `REVIEW_HOLD`, no customer data or external model. Journey suite fell from about **66.7s before** to **28.0s after** immutable fixture caching in this container; no negative cases removed. The fully sequential standalone suite took **74.0s**, all 89 passing.

Prior current-branch P50/P70/P85 combined local evidence (before the new two tests) was **124 total / 121 PASS / 0 FAIL / 3 SKIP**; **the enlarged combined 126-case command was not executed here**, so do not label it a fresh aggregate PASS. Those SKIPs require an exact original RAG Studio checkout. A new authored workflow push is not confirmation of a GitHub-hosted successful run.

### Original RAG version drift check

Current original `hibi89/RAG_STUDIO@develop` checked HEAD `bb8529ed689c1e95ccd7bbb722d4d6616eb46130`, which has **diverged** from the pinned `c5867b3951f51bfa97cadd1aad8fb13e9cf9e604` (GitHub compare: head three ahead and forty behind from the pin, two changed files). **Keep the exact pinned SHA** until integration and regression tests establish a safe replacement. Do not silently import a new branch or treat mismatched source as validated.

### Remaining full-blueprint acceptance barriers

1. Original RAG exact pinned-source SQL/BM25/native PDF+DOCX and PREP/SMAX regression 3 skipped due isolated execution environment GitHub DNS. GitHub-hosted workflow logs/results not verifiable from connected Actions metadata.
2. Actual corporate employee identity, group provisioning, robust enterprise tenant storage/authorization, **approved customer rights and signed PREP/SMAX→AX**. The current mechanism is synthetic-only and does not grant a legal/technical production approval.
3. Real Korean pretrained local model licensing and controlled acceptance benchmark, physical Windows 10/11 deployment and customer Gold/Negative/heldout + malicious document evaluation.
4. Customer/owner-approved full 100% design requirement weighting and verified production acceptance. Test pass ratio is not product-wide completion.

**Security limitation:** A time-of-check/time-of-use filesystem race is still possible between directory checks and subsequent file opening; the demo is not a fully hardened multi-user sandbox. Refuse production rollout or live customer data until this is resolved and customer permissions are explicitly authorized.

**Status: UNASSESSED · 85% NOT verified · [작업중] · RELEASE HOLD / SALE NO-GO · Production/Vercel 미적용.**
