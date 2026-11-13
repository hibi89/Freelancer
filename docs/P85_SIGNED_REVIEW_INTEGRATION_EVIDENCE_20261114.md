# CITEVAULT AX P85 — source-verified PREP mapping + signed SQL/document journey

**2026-11-14 KST / Full final-blueprint baseline v1.0 / target 85%. Official completion: UNASSESSED, 85% NOT established.** Release HOLD. This is an offline, synthetic-only source review bridge; no real customer use, producer approval, enterprise IdP or commercial license is assumed.

## Engineering decision: cost / security / maintenance

A. Trust `smax-review.json` / `prep-mapping.json` with editable `approval` fields and return numeric answer: fewer changes, **unacceptable**; stale/forged data can be treated as authorized.
B. **Selected:** preserve original review-only fixed SQL+document routing; bind validated actual CSV bytes **and exact reviewed PREP mapping bytes** by SHA-256, then verify a host-pinned Ed25519 review attestation *inside the actual `POST /v1/assess` path*. No external API/model cost, small maintenance footprint, no original RAG/PREP/SMAX change. **Even valid signature remains REVIEW_HOLD and answer:null.**
C. Actual signed PREP/SMAX producer → customer reviewer/legal source-rights approval → accepted AX package and original RAG: target architecture, needs authorized real customer identity/source scope and verified source; **not implemented** by this change.

## Exact code and safety boundaries

| Code file | Exact tested Git blob SHA | Purpose |
|---|---|---|
| `enterprise/p70-local-review.mjs` | `8d1980e58c08c5dec4b76b95f9b16ab0ffc6e045` | Bounded/checked PREP file bytes and SHA-256, second checked hash to reject in-review mutation |
| `enterprise/p85-review-sql.mjs` | `6c94e8a3ac31c3309586a0f0cfff7e8951d0f7c5` | Preserve P70 exact held CSV reconciliation + in-memory prepared `node:sqlite` totals; carry verified mapping SHA |
| `enterprise/p85-journey.mjs` | `14d3151223829dc0dda7f5bdeb4ae684956207cc` | After original tenant/group/project ACL and reviewed SQL data, validate optional signed review; invalid signature/expiry/tenant/replay returns no provisional totals or citations |
| `enterprise/p85-signed-review-gate.mjs` | `23daea4fb4b32f7dfef61d6d8d9dee14d4fbeee1` | Pin public key, tenant, producer key ID and version at host configuration, validate signed source+mapping SHA. Review only, never approval |
| `tests/p85-signed-journey.test.mjs` | `4961ef6eb7ece0c7a9a4e8c4c71abdf2aa2161e8` | 9 actual offline CSV/PREP/Ed25519/HTTP positive and adversarial tests |

All five files were individually retrieved from connected GitHub after write and their remote Git blob SHAs matched the exact files executed in the Linux container (verified via `git hash-object`).

An *optional* server-supplied `signedReview` object carries trusted public key, expected tenant/key ID/version and envelope. These are not taken from user-supplied HTTP request JSON. Missing signature retains prior review-only behavior, explicitly marks `signed_review.signature_verified=false`. A correct signed review asserts only authenticity of source metadata; `approved_customer_data:false`, `source_rights_verified:false`, `ax_package_created:false`, `answer:null`. No private signing key, model weights or customer data in repository.

## Test execution evidence

**Current container:** Linux Node v22.16.0 (experimental built-in SQLite), Python 3.13.5, local synthetic fixture packages.

```sh
node --test tests/p85-signed-journey.test.mjs       # 9 PASS / 0 FAIL / 0 SKIP
node --test tests/p85-journey.test.mjs              # 18 PASS / 0 FAIL
node --test tests/p85-loopback.test.mjs             # 17 PASS / 0 FAIL
node scripts/p85-operator-demo.mjs --self-test     # PASS
```

All ten P85 test files, **each run separately**, reported **138 PASS / 0 FAIL / 0 SKIP** in aggregate: BM25 6; UI 6; vault 27; HTTP 17; state-store 14; actual PDF/DOCX 13; original reviewed SQL/PDF-DOCX journey 18; existing Ed25519 provenance 18; operator users 10; newly signed reviewed SQL journey 9. Test evidence is per-file completed runs, **NOT** a single combined runner success. A prior `node --test --test-concurrency=1 tests/*.test.mjs` combined invocation hit execution timeout; no one-shot CI PASS claim.

**Offline ZIP artifact:** `CITEVAULT_AX_P85_signed_review_integrated_20261114.zip`, SHA256 `84a9ea2725fe8391451a6942f5ec4628471c86f0d66bb9bc3d3b8fab3d4aa99e`, 28 UTF-8 local source, fixture and README entries. Verified ZIP CRC OK. Fresh unzip → signed journey **9/9 PASS** and operator login→user role→citation→revoke demo self-test PASS. No customer files included.

**Actions workflow:** `.github/workflows/citevault-p50.yml` now runs signed review bridge syntax and signed journey tests with the P85 Ubuntu 24.04 / Windows 2022 Node 22 job. **Actual hosted Actions run ID and job conclusions for this product SHA remain unknown**. Workflow definition does not count as PASS.

**Original upstream RAG:** `hibi89/RAG_STUDIO` existing run ID `43231121679` is confirmed with success conclusions for Windows and Ubuntu jobs from the GitHub connector. That is a historical upstream RAG run (associated with different source history), **not** an execution of current CITEVAULT's exact pinned original commit `c5867b3951f51bfa97cadd1aad8fb13e9cf9e604`. Existing 3 exact pin-based integration checks remain unexecuted in this container due github.com DNS unavailable; don't rebrand upstream successful jobs as this project's RAG integration proof.

## Full-final-design 85% gaps that remain

- Real production approved PREP/SMAX producer, authenticated human reviewer, actual customer rights and `AX_DATA_PACKAGE_V0` acceptance/manifest, verifiable key custody and durable revocation watermark. **Not authorized/implemented.**
- Real customer-managed IdP/corporate identity, legally approved file access, enterprise threat modeling/sandbox, separate tenant index. Local synthetic accounts != corporate IAM.
- Exact original RAG pinned BM25/native/SQL/PREP-SMAX CI 3 SKIP, actual GitHub-hosted product Windows/Linux CI conclusion.
- Actual downloadable licensed Korean pretrained local model weights/SHA and measured mini benchmark; physical Win10/11 installer/Gold/customer acceptance.
- Full blueprint evidence weighting and owner approval: existing 24-row tracking `docs/FINAL_BLUEPRINT_85_ACCEPTANCE_MATRIX_20261114.md` remains the denominator, with no unsupported percent computed.

**Official UNASSESSED / user target 85% not verified / [작업중] / RELEASE HOLD / SALE NO-GO / production deployment not applicable.**
