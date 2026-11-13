# CITEVAULT AX — P85 integrated offline PDF/DOCX + reviewed SQLite evidence (2026-11-13 KST)

> Full blueprint goal from user: **85%**. **Official final completion remains UNASSESSED, NOT validated 85%.** `[작업중]` and `RELEASE HOLD/SALE NO-GO` remain. This is an actual executable **synthetic-only** integrated source, *not* an enterprise-approved service.

## Architecture comparison and selected implementation

1. **Original RAG Studio `withReadOnlySales` + `loadPackage` in same service:** Native fixed SQL/manifest/parse contract exists in public `hibi89/RAG_STUDIO@c5867b3951f51bfa97cadd1aad8fb13e9cf9e604` but `loadPackage` loads the package before employee ACL. Pinned checkout unavailable in execution container (GitHub DNS) and hosted workflow job status not available. Cannot claim original integration PASS.
2. **Separate on-disk per-tenant pre-read ACL + immutable server dataset scope + strict P70 review + exact in-memory SQLite + page/paragraph citations:** Implemented and **actually executed** on synthetic fixtures. No network or external model and no dependency on original RAG package loading. Correctness limited to strict five-column CSV subset and local PDF/DOCX bounded pages/paragraphs. The only business output is `REVIEW_HOLD`; no customer-rights approval is inferred.
3. **Full IdP+signed PREP/SMAX→AX production import in one change:** Needs explicit user/customer role, legal source rights, approved account/secret environment; postponed. No cloud or payment spend authorized.

## New end-to-end behavior

1. Ephemeral process-local scrypt account/session and verified fixed tenant/group/project/classification scope; unauthorized sales user denied before `sales.csv` is opened.
2. Same authenticated HTTP `POST /v1/assess` request selects a tenant-allowed actual PDF and Korean DOCX; before native parser runs, source path/type/symlink/hardlink/byte SHA are checked; citations report actual `page` and `paragraph`.
3. For `총매출` requests, P70 `reviewSyntheticSalesDirectory` checks fixed synthetic SMAX/PREP `NOT_GRANTED` and original SHA. Bounded CSV bytes are independently read with SHA match and a **fixed, prepared node:sqlite in-memory read-only** aggregate. Quantity × price and total units/revenue match P70 independently; arbitrary SQL is not exposed. Unexpected headers/quotes, unsafe numeric range, altered source, fake approval and unsupported timeframe force HOLD.
4. The result has `answer:null`, `status:REVIEW_HOLD`, separate document citations and provisional SQL totals with original hash, `source_rights_verified:false`, `ax_package_created:false`, `network_calls:0`. The API does **not** upgrade held CSV to `ACCEPTED`.
5. `scripts/p85-synthetic-demo.mjs --self-test` uses an ephemeral `127.0.0.1` HTTP socket and a randomly generated synthetic credential, performs actual login plus native PDF/DOCX+SQLite assessment, checks `REVIEW_HOLD`, and removes the temporary fixture. Without `--self-test`, it prints the ephemeral username/password and demo instructions until SIGINT/SIGTERM. **Never expose outside loopback.**

## Exact GitHub blobs (local `git hash-object` verified against connected repository)

| Path | Blob |
| --- | --- |
| `enterprise/p85-vault.mjs` | `ec48e31ef796eaf76f90c8828d8071028d86d3cf` |
| `enterprise/p85-loopback.mjs` | `c849fe22f511151c0e9f8c9a1d81f608d70ab2ed` |
| `enterprise/p85-review-sql.mjs` | `f881b8a4a97e14a865622e5690cf2de071a3cc2a` |
| `enterprise/p85-journey.mjs` | `36a2f8093d6b6852bd9df07d17255bd4ab9078b6` |
| `tests/p85-journey.test.mjs` | `ecd68c352609d878beda25d7263b5b4ed9ea446a` |
| `scripts/p85-synthetic-demo.mjs` | `4cfe0af457c75ec11a703a6c182ef56868f2e70c` |
| `.github/workflows/citevault-p50.yml` | `4e5fe24c4b25cba8bc7054c91d8e2cd4de95c193` |

Previous P85 SQLite/identity/PDF/DOCX verified blobs and original RAG pin remain unchanged except the two explicitly modified P85 source files above.

## Actual execution evidence and commands

Linux Node v22.16.0 + Python 3.11, installed synthetic fixture dependencies `pypdf==5.9.0`, `python-docx==1.2.0`, `reportlab==4.4.9`.

```sh
node --test tests/p85-journey.test.mjs
# 16 PASS, 0 FAIL, 0 SKIP
node scripts/p85-synthetic-demo.mjs --self-test
# JSON status PASS, offline true, review_status REVIEW_HOLD, answer null
node --test /tmp/citevault-local/tests/p50.test.mjs /mnt/data/citevault70/tests/*.test.mjs /mnt/data/citevault85/tests/*.test.mjs
# 124 TOTAL / 121 PASS / 0 FAIL / 3 SKIP
```

The 3 SKIPs all require the separately unavailable pinned RAG original checkout; they are **not** counted as success. The full local repository P85 suite includes prior actual native PDF/DOCX and SQLite lifecycle tests.

**Reproducible isolated ZIP:** `CITEVAULT_AX_P85_unified_offline_20261113.zip` (17 source/test/docs entries). Unpacked in a fresh directory; `node scripts/p85-synthetic-demo.mjs --self-test` PASS and `node --test --test-concurrency=1 tests/*.test.mjs` **87 PASS/0 FAIL/0 SKIP**, duration about 56 seconds. An earlier parallel zip run exceeded tool timeout; retry using serial execution established 87/87 PASS. No source files changed in retry.

GitHub workflow now runs actual Python3.11/Node22 native and 16 end-to-end unified tests **plus demo self-test** on `ubuntu-24.04` and `windows-2022`, and retains prior original RAG checkout job. **Hosted GitHub Actions run IDs, actual Windows jobs and original RAG native/SQL/PREP/SMAX jobs remain UNVERIFIED**; workflow YAML does not prove a job passed.

## Why product-wide 85% is NOT proved

- Actual corporate trusted employee IdP/account provisioning, enterprise secrets/permissions, independent tenant index and production-grade revocation have **not** been implemented or customer-authorized.
- Actual source-rights approval, true signed native PREP/SMAX producer→AX acceptance/lineage, original pinned RAG Studio fixed SQL and PDF/DOCX production integration remain unverified.
- No licensed, quality-evaluated real Korean local model, no malware-safe parser isolation, real Windows 10/11 physical install, customer Gold/Negative/heldout acceptance or measured release SLOs.
- User-approved complete-blueprint requirement weighting/denominator missing. Synthetic total test counts are not a product completion percentage.

**Result:** genuine functional integration and repeatable offline demo + all local synthetic tests PASS. **Official UNASSESSED, user target 85% NOT verified, [작업중], RELEASE HOLD, NO PROD DEPLOYMENT.**
