# CITEVAULT AX — restored catalog consistency / synthetic QA (2026-11-14 KST)

## Function and CI evidence
- Exact source SHA `d32f530e2425da0129a4eb2e9a4a7aef6708dab8` on `hibi89/Freelancer@product/rag-enterprise-knowledge`.
- [Hosted GitHub Actions #43527372030](https://github.com/hibi89/Freelancer/actions/runs/43527372030) exact SHA: **6/6 SUCCESS**, **404 test executions PASS / 0 FAIL / 0 SKIP** (Ubuntu and Windows test repetitions count separately).
- CI breakdown: pinned upstream RAG **11+24**, CITEVAULT pinned source bridge **36**, P70 local contracts **31**, Ubuntu and Windows P85 identity/vault/UI/signature **107 each**, synthetic100 harness **1 each** (each runs 100 cases), offline snapshot tests **12 each**, native PDF/DOCX+SQL journey **31 each**. Sum 11+24+36+31+2×(107+1+12+31) = **404**.
- Source/test blobs verified equal to locally tested `git hash-object`: `enterprise/p85-offline-backup.mjs` `dff2521f95f17e96e531a9438993644a0f71ac09`, `tests/p85-offline-backup.test.mjs` `83ef68dceecab680437600fbf522de21332cfaba`.
- Local Node22.16 Linux `node --test tests/p85-offline-backup.test.mjs` **12/12 PASS**; exact new code hosted Linux + Windows 12 PASS each.

## Bug prevented
- Former restore validated individual SHA and SQLite `header` only. A snapshot with SQLite document catalog changed but file manifest hashes re-computed could pass integrity checks while active document provenance was invalid. An SQLite with just a valid header and missing users/docs/audit tables also passed.
- New code requires the four durable SQLite tables, known format/generation, user count 1..100, document row count 1..256, valid document catalog IDs/kind/digests, and exact SHA match between **every active document metadata record** and the staged recovered file bytes. Inactive/retired documents may lack raw source by design.
- New negative tests: tampered live document before snapshot, malicious modified SQLite catalog with recomputed file+manifest hashes, header-only forged SQLite; all fail closed without creating destination.
- No client data, account privileges, RAG upstream source, signed PREP/SMAX producer, actual LAN/Production, billing, model weights or third-party services modified.

## Remaining acceptance and caution
- This is a **manual, service-stopped synthetic backup**. The source must be quiescent; concurrent database/document writes are outside guarantees. SHA/manifest checks cannot authenticate a malicious publisher controlling **both** source data and metadata. Strong authenticated/custodial backup trust still needed for customer use.
- The 100 Korean template tests measure tiny synthetic corpus only; not 100 independent customer Gold questions, no real dense model or LLM.
- Real enterprise identity/IdP + document rights, signed authoritative PREP/SMAX `AX_DATA_PACKAGE`, actual Korean model with verified license/hash/quality, Windows10/11 installer and customer acceptance, long-run scale/penetration testing remain.
- Shared `Freelancer` is **PUBLIC** by owner choice; all branches and Git history exposed. No full historic secret scan performed; do not upload client data.
- **Final 24-requirement blueprint official completion: UNASSESSED. User target 85% NOT VERIFIED.** `CITEVAULT AX [작업중]`, `RELEASE HOLD/SALE NO-GO`, Production/Vercel N/A.
