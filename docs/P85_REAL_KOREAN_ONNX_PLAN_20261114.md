# CITEVAULT AX — actual local Korean E5 ONNX smoke (2026-11-14 KST)

## Choice / boundaries
A) Cloud embedding API: rejected because customer text leaves the device, recurring API costs and credential risks.
B) Local CPU ONNX E5 with exact SHA verification: selected. Optional Python runtime (numpy/onnxruntime/tokenizers), exact int8 ONNX SHA, strict query:/passage: prefixes, token budget, attention-mask mean pooling, L2 normalization, three fixed synthetic Korean ranking probes. No corporate content, paid APIs, hosted LLM, new identity privileges, or public model weights in GitHub.
C) Rewrite CITEVAULT production server around the model: rejected for regression and premature licensing risks.

## Execution
- Synthetic contract tests: python -m unittest discover -s tests -p test_p85_korean_real_onnx.py -v
- Download public Xenova model to a NEW ephemeral destination only (e.g. GitHub runner temp): python scripts/p85_korean_model_fetch.py --dest ABS_NEW_DIR
- Node preflight: node scripts/p85-korean-model-check.mjs --model-dir ABS_MODEL_DIR
- Actual CPU inference: python scripts/p85_korean_real_onnx.py --self-test --model-dir ABS_MODEL_DIR
- Workflow: .github/workflows/citevault-korean-onnx-smoke.yml uses standard public-repo Ubuntu runner; independent of prior core 8-job regression. No artifact uploads or caching. Only synthetic hardcoded phrases are embedded.

## Acceptance and restrictions
- Real ONNX weights are never committed. Downloaded model SHA must match 4d24e2bc01a447951524466ef533e52944bf48509e6552810bcee1a2711cb02c.
- Synthetic probes are a *runtime smoke*, not Gold100, enterprise permission validation, commercial model/Node redistribution license sign-off or production readiness.
- Existing CITEVAULT BM25 SEARCH_ONLY fallback remains unchanged: **not** routing customer content into an unapproved model.
- Evaluate CI result and exact commit SHA before claiming actual model execution PASS; code addition alone proves no inference success.
- Full 24-item blueprint completion stays **UNASSESSED / 85% NOT CERTIFIED / RELEASE HOLD / SALE NO-GO** until real enterprise IAM/rights, signed PREP-SMAX package and Win10/11/customer Gold evidence.

## [2026-11-14 10:25 KST] Real Korean E5 ONNX hosted inference verified

- Exact tested code SHA a3ffc4ba5a05e0b140ba08d8f248b6b0bc44e64e; [actual Actions run #43540387093](https://github.com/hibi89/Freelancer/actions/runs/43540387093) Ubuntu24.04 1/1 SUCCESS. Python 3.11 4/4 unit contracts PASS; SHA-matched ephemeral downloaded ONNX 118,054,593 bytes; real CPU inference 384 dimensions; fixed synthetic Korean query/positive/negative retrieval 3/3 correct, cosine margins [0.09215, 0.12037, 0.05195], 1,145ms measured for 9 synthetic embedding inputs on runner.
- Initial run #43540283742 at SHA 44e3e8a0 had 0-job YAML parse FAIL because pip --only-binary=:all: bare scalar colon+space; corrected workflow with run folded scalar at SHA a3ffc4ba. No repeated failed workflow needed.
- Only public model downloaded into GitHub hosted ephemeral environment; no weights/customer files/secrets checked into repository, no paid service. Original ACL/BM25 SEARCH_ONLY path, RAG, PREP/SMAX and production untouched.
- Existing CITEVAULT core CI #43537747863 still 8/8 SUCCESS 469 executed tests PASS on exact earlier source f4f5f088; THIS latest documentation change did not rerun core tests. No real customer Gold100, authorized PREP/SMAX production AX import, employee IdP, real Windows10/11 installer, security/legal/model redistribution licensing acceptance.
- OFFICIAL FULL-24-REQ FINAL COMPLETION UNASSESSED / 85% NOT CERTIFIED / [작업중] / RELEASE HOLD / SALE NO-GO. Public shared Freelancer historical branches still need secrets/IP audit.


## [2026-11-14 10:31 KST] Real Korean ONNX CPU both Ubuntu + Windows hosted PASS

- Exact code SHA bc3ee4e6d41bd0427e1f332793808bf109ba742b, [GitHub Actions #43540831305](https://github.com/hibi89/Freelancer/actions/runs/43540831305): **2/2 jobs SUCCESS**, 0 FAIL, 0 SKIP. Ubuntu24.04 + Windows2022 each Python 4/4 unit tests PASS, exact public ONNX SHA 4d24e2bc01a447951524466ef533e52944bf48509e6552810bcee1a2711cb02c (118054593 bytes) preflight PASS, actual CPU e5-small 384d inference with fixed synthetic Korean contrastive pairs **3/3 per OS**. Both reported margins [0.08814,0.11856,0.05041]; elapsed 1309.7ms Ubuntu and 1644.9ms Windows per 9 synthetic texts batch (not customer SLA). No paid APIs or customer data.
- Windows-specific synthetic missing-model path test fixed to use Path.home().resolve, not Unix-only /a. Workflow uses standard free hosted 2-OS matrix, no weights uploaded, model retained only in temporary hosted runner. First exact 1/1 Ubuntu source a3ffc4ba CI #43540387093 also succeeded.
- Existing production search/API/ACL and RAG/PREP/SMAX originals unchanged; **not yet full authenticated offline dense integration**. Real customer data rights/IdP, signed authoritative AX producer, heldout Gold100, physical Windows10/11 customer installation, commercial license and security sign-off remain.
- FULL FINAL BLUEPRINT 24 REQs OFFICIAL UNASSESSED, goal 85% NOT CERTIFIED, CITEVAULT AX [작업중], RELEASE HOLD/SALE NO-GO. Prior core 8/8 CI #43537747863 corresponds to older exact code SHA f4f5f088; do not misrepresent this 2-job model CI as a fresh run of all original 469 tests.

