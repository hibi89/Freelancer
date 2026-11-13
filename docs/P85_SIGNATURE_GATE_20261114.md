# CITEVAULT AX — P85 ED25519 synthetic PREP/SMAX provenance review gate
**2026-11-14 KST. Target 85% of full final design. Official completion: UNASSESSED. RELEASE HOLD.**

## Scope and design comparison
- **A. Unsigned PREP/SMAX JSON approval flag:** cheap but anyone can change a field to `GRANTED`; violates safety and original rights requirements. Rejected.
- **B. Ed25519-signed SHA/version/tenant/key-id mapping and document digest attestation:** zero external service/API cost; offline Node built-in crypto, tamper-evident provenance; no real legal approval without trusted customer reviewer, no accepted AX package, signature key and monotonic version must come from trusted host. Selected, **synthetic-only**.
- **C. Production IAM and customer-permissioned signed PREP/SMAX→AX import:** full required end state but requires identities, contractual rights, secure private keys, a trusted reviewer and production data. Not authorized and **not implemented** in this step.

## Actual implementation
- `enterprise/p85-signed-provenance.mjs` Git blob **`78b777505a4325230ad7f780907bf08538dc7783`**: Ed25519 signed canonical review payload bound to tenant ID, external trusted key ID, SHA256 source, SHA256 mapping, sorted unique document SHA/type, producer revision, issue/expiry window <=24h, and `REVIEW_HOLD`/`SYNTHETIC_ONLY`/`rights_verified:false`. Source bytes never read or sent.
- `tests/p85-signed-provenance.test.mjs` blob **`ef21059e67ce5b2e4c7b5043d6ed0e738c151232`**: real cryptographic generated-key tests of signature verification, altered sources, swapped tenant, key mismatch, forged approval, mapping/document hashes, key identity, expiry, replay, duplicate documents, extra fields and unsupported signing algorithm. No private key committed.
- Local Linux Node22.16.0 **`node --check enterprise/p85-signed-provenance.mjs` PASS** and **`node --test tests/p85-signed-provenance.test.mjs` = 18PASS/0FAIL/0SKIP**, repeated after GitHub source exact hash check. The two local file SHA1 Git blob IDs agree with connected GitHub file readbacks.
- Added signature source and tests to `.github/workflows/citevault-p50.yml` Ubuntu24.04/Windows2022 `p85-loopback-contracts` job. **Actual hosted Actions runs, Windows result, PR checks and production release remain UNVERIFIED.**
- In current environment the attempted full 7-file sequential P85 suite timed out during the next native fixture suite after the HTTP section; **do not claim full-suite PASS in this turn**. Last fully completed 89PASS/0FAIL/0SKIP applied to the *previous* local sources. Signature tests were performed separately 18PASS.

## What this does NOT mean
- This signature verifies the source-review metadata only; **NOT** customer rights, not an authenticated human approval, not real external private producer integration, not an accepted `AX_DATA_PACKAGE_V0`, and not RAG `loadPackage` enterprise ACL.
- The version watermark is provided by the host; this is not a durable production anti-replay ledger. The signing tool is not wired into the real PREP/SMAX producer or current customer workflow. It is not a replacement for real IAM or a legally sufficient authorization.
- Real local Korean pretrained language model and licensing/acceptance, physical Windows customer installation, exact pinned RAG Studio native+SQL+SMAX end-to-end (previous 3 SKIP), official CI logs, customer Gold/negative sets are not validated.

**Next gates that require owner/customer action:** approve exact customer data-use scope, real employee IdP and permissions, trusted reviewer/signature key custody, usable licensed local Korean model weights, physical Windows device access. None of these should be falsely replaced with local synthetic identities.

**Official: UNASSESSED, 85% not reached/verified, [작업중], RELEASE HOLD / SALE NO-GO.**
