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
