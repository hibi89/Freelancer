# CITEVAULT AX — 100 synthetic Korean query evidence (2026-11-14 KST)

**NOT customer Gold100, NOT semantic/LLM model acceptance, NOT 85% final-blueprint proof.**

- Code `tests/p85-synthetic100.test.mjs` at functional SHA `0cf969fb2908cca985f4655d2c713ad7e030d168`.
- Real hosted [GitHub Actions #43525453183](https://github.com/hibi89/Freelancer/actions/runs/43525453183), Ubuntu24.04 Node22.16/Windows2022 Node22.23; both synthetic100 harness tests 1/1 PASS, 100 queries each, no network.
- Measured synthetic p95: Ubuntu **0.328ms**, heap used **7,342,008 bytes**; Windows **1.001ms**, heap used **8,103,480 bytes**. Specific hosted runner/time/sample only; not customer SLA/physical Windows result.
- Synthetic corpus: 4 small internal policy TXT documents across two fake tenants; two conflict return policies and one secret document. All synthetic data committed is fake policy text, no customer identifiers.
- Exactly 20 controlled retrieval cases (grounded text, answer:null, network_calls=0); 20 insufficient cases (no hallucination); 20 conflict cases (human HOLD even limit1); 20 inaccessible direct source cases (NOT_FOUND); 20 mixed allowed+disallowed selection cases (all request denied). 100 **template variants**, not 100 independently reviewed customer questions.
- Test restores temporary synthetic files automatically, checks source SHA unchanged; no actual employee IdP/SMAX producer/customer rights or real model weights. Original RAG pinned source upstream35+CITEVAULT bridge36 validated separately in same 6/6 CI.
- Next: customer-provided licensed Gold100 (rights/identity authorization), independent heldout, real model artifact+checksum/license, actual large corpora recall/MRR/NDCG, p95 latency/peak memory on Windows10/11. Owner's development approval does not synthesize such acceptance.
- Final status: `UNASSESSED`, `CITEVAULT AX [작업중]`, `RELEASE HOLD/SALE NO-GO`.
