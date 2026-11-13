# CITEVAULT AX — GitHub Actions P85 hosted CI recovery (2026-11-14 KST)

## Source of truth / scope
- Repository: `hibi89/Freelancer`, branch `product/rag-enterprise-knowledge`.
- **Tested functional commit:** `cea0ec09ac4a85a16e369bd302986959fca408b0`; parent/recovery `4f7277e70a46c24b6cf0ccf394df714450a7a719`.
- [CITEVAULT CI #43523337142](https://github.com/hibi89/Freelancer/actions/runs/43523337142): **6/6 jobs SUCCESS**, actual hosted Ubuntu 24.04 + Windows 2022 runners allocated and executed; exact SHA matched.
- [Final blueprint evidence gate #43523337300](https://github.com/hibi89/Freelancer/actions/runs/43523337300): **SUCCESS** (policy/document validation, not full enterprise acceptance).
- Hosted per-command results with no failures/skips:
  - Ubuntu local-contracts P70 citation/PREP-SMAX: **31 PASS**.
  - Ubuntu pinned RAG `RAG_STUDIO@c5867b3951f51bfa97cadd1aad8fb13e9cf9e604`: P512 **11 PASS**, P538/P540/P549 **24 PASS**, CITEVAULT P50/P70 source-bound bridge **36 PASS**; this is **71 executions**.
  - Ubuntu P85 local accounts/ACL/SQLite/UI/BM25/signed review: **107 PASS**.
  - Windows 2022 P85 local accounts/ACL/SQLite/UI/BM25/signed review: **107 PASS**.
  - Ubuntu 24.04 actual native PDF/DOCX/signed SQL journey: **31 PASS**.
  - Windows 2022 actual native PDF/DOCX/signed SQL journey: **31 PASS**.
  - Total **378 executed test cases PASS / 0 FAIL / 0 SKIP** across jobs/platforms, including repeated tests run on different OSs; **not 378 distinct requirements**.
- Two cross-platform fixes: `enterprise/p85-native-extract.mjs` uses Python `-X utf8` with `-I` for Unicode/Windows pipe output; `tests/p85-state-store.test.mjs` closes all SQLite connections before Windows filesystem deletion. Both exact new blobs checked via GitHub connector: `7be87914cbf44712896d9f7342a63c72f9cb08b5`, `15080dd7578a213166a139760244301689cc05c1`.
- Prior failed CI attempt #43516278650, attempt 1, jobs never started because GitHub Actions account spending/billing restriction confirmed by owner screenshot. After owner changed repo visibility, attempt 2 obtained actual runners, original pinned RAG bridge 36 PASS, but Windows DOCX `NATIVE_HOLD` and SQLite `EBUSY` were confirmed. Latest patch above resolved CI failures.
- **Privacy caution:** owner changed shared `hibi89/Freelancer` to **PUBLIC**. This makes other product branches/history broadly accessible, not just CITEVAULT. Owner was warned; no visibility/permissions change performed by assistant and no comprehensive history secret scan completed. Do not add real customer documents/tokens/secrets. This is not evidence that PUBLIC was safe.
- Functional limits: product is still a localhost synthetic acceptance path. No real employee/customer IdP, licensed customer source rights/producer authorization and release, actual Korean LLM artifact/quality, real Win10/11 installer+physical acceptance, customer Gold100, PII/security pen-test, customer legal/price/signoff. Original RAG **synthetic bridge exercised**, not a complete approved enterprise production path.
- **Overall final blueprint 24 requirements: OFFICIAL UNASSESSED; 85% NOT VERIFIED.** Keep `[작업중]`, `RELEASE HOLD/SALE NO-GO`. CI success cannot be converted into an arbitrary weighted percentage.
- Zero new billing changes, no original RAG/PREP/SMAX edits, no customer data or secrets added, no deploy. Production/Vercel: `N/A`.
