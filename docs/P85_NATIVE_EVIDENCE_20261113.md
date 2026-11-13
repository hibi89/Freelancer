# CITEVAULT AX — P85 actual native document evidence

**Checked 2026-11-13 KST, Linux Node 22.16.0 and Python 3.11.**
Owner target: **85% of the entire agreed final blueprint**. Official completion: **UNASSESSED / 85% NOT VERIFIED**. `[작업중]` and `RELEASE HOLD` remain.

## Architectural decision and alternatives

1. **Original RAG Studio native extractors:** Most consistent with existing PDF.js + Mammoth, lowest long-term duplication. Pinned original `hibi89/RAG_STUDIO@c5867b3951f51bfa97cadd1aad8fb13e9cf9e604` still cannot be checked out in the current execution container (GitHub DNS). Original hosted P512/P538/P540/P549 workflow configured but actual run/log unknown. Therefore **not presented as executed**.
2. **Separate ACL-before-read bytes adapter using Node + Python:** Chosen for a directly executable offline synthetic proof in the current environment. Node vault verifies account, tenant, group, project, source path and exact SHA before opening document bytes. A child Python process receives **bytes over stdin**, no customer path or remote service; local pypdf returns real page markers and python-docx returns real paragraph markers. This path is separate from original RAG, a bounded prototype with extra Python dependencies.
3. **Custom PDF/OOXML full parser reimplementation:** Rejected: high security/maintenance cost, worse fidelity, no license benefit.

## Source, SHA and test validation

| Repository file | GitHub blob SHA | Function |
|---|---|---|
| `enterprise/p85-vault.mjs` | `762321a71736f4ebeee73b28c7834a5ae876be66` | Enforces ACL + digest + file length before passing verified native bytes to parser; `native_kind` is explicit `txt/pdf/docx`; citation unit recorded as line/page/paragraph |
| `enterprise/p85-native-extract.py` | `05f2d7fd371fc22bb1313c0e47d710653ed270ff` | Python input buffer, PDF page and DOCX paragraph text; strict file/ZIP budget, no path args, no OCR/network, returns HOLD on missing/corrupt/encrypted/unsupported |
| `enterprise/p85-native-extract.mjs` | `fbd40284ee42c237608ec0aef649ceeef1fc77b6` | Restricted interpreter invocation with timeout and JSON output validation |
| `tests/p85-native-fixture.py` | `0847f627c7b21eec4654471b734c47f12385de39` | Creates synthetic 2-page PDF, private PDF and 2 native Korean DOCX fixtures in temp directory |
| `tests/p85-native-integration.test.mjs` | `4d6aec409468c531149f3e626f7f8509854f2b59` | Actual PDF+DOCX file source/lineage, ACL deny, SHA tamper, symlink/hardlink, no-model, native conflict, SQLite persistence/retire |
| `tests/requirements-p85-native.txt` | `5cc9a2a8939678546aa55ad1ce6fd1369ceefb43` | Pinned pypdf 5.9.0, python-docx 1.2.0, reportlab 4.4.9 for CI |

Six GitHub blobs were fetched after writes and each matches the **exact tested local file `git hash-object`**. No live private RAG Studio, SMAX, PREP or original customer files modified.

## Verified execution

```sh
node --check enterprise/p85-vault.mjs
node --check enterprise/p85-native-extract.mjs
python -m py_compile enterprise/p85-native-extract.py tests/p85-native-fixture.py
node --test tests/p85-native-integration.test.mjs
# 13 PASS, 0 FAIL, 0 SKIP (12 nested + suite)
```

Actual synthetic native evidence verified: PDF page 1/2, Korean DOCX paragraph 1/2, mixed PDF+DOCX source search, 7/14-day conflict requiring `POSSIBLE_CONFLICT`, SHA tamper refusal *before* parser, denied PDF cannot leak via full-corpus search, symlink/hardlink denial, corrupted data `NATIVE_HOLD`, SQLite native_kind persistence across process restart and native retire preserving original files.

**Exact local complete regression:**
```sh
node --test /mnt/data/citevault85/tests/*.test.mjs \
  /mnt/data/citevault70/tests/*.test.mjs \
  /tmp/citevault-local/tests/p50.test.mjs
# 108 TOTAL / 105 PASS / 0 FAIL / 3 SKIP
```

The three SKIPs remain the original **pinned RAG SQL/BM25/SMAX checkout integration**, not native-test failures. This product now has its own native test path, but that does **not** verify the original RAG extractor or native SQL query from RAG Studio. Original P85 58 PASS remain intact. Temporary synthetic fixture files are not customer approved or packaged as real confidential data.

## CI and operational limits

- Existing `.github/workflows/citevault-p50.yml` now adds independent `p85-native-evidence` Linux Ubuntu24.04 Node22.16/Python3.11 and Windows2022 Node22.23/Python3.11 job, installs pinned requirements and runs actual native tests; existing P85 auth/SQLite jobs unaffected. **Hosted CI run/job status and actual Windows execution are UNVERIFIED**, workflow source alone does not mean PASS.
- Bounded to 2MiB input, <=64 pages/paragraphs, <=4096 chars per evidence; readable PDFs only, no OCR; DOCX ordinary body paragraphs, not exhaustive tables/track changes/text boxes. Extraction may be held for complex files. Offline test dependencies have their own packaging/license requirements; python-docx shows MIT, ReportLab installed metadata BSD, pypdf package license must be checked before distribution. No model weights or private document content transmitted.
- Parsing untrusted PDF/DOCX within a subprocess with only a time limit is **not a complete hardened sandbox**; memory quotas, low privileges, isolation, threat modeling and Windows malicious document tests remain to do. No public server or actual customer IAM.
- Local BM25-like lexical fallback is **not** a Korean pretrained model. Production model licenses/quality, real employee identity/IdP and PREP/SMAX signed source rights, real fixed SQLite SQL linked to RAG, persistent enterprise ACL/index isolation, Gold and physical Windows testing all remain unimplemented/unverified.

## Follow-up and release gate

Real customer authorization and data/privacy/role changes require explicit approval. Prioritize exact original RAG pinned-SHA hosted job logs, native PDF/DOCX + real fixed SQL + signed PREP/SMAX→AX test, real account provisioning and hard tenancy, small licensed Korean model evaluation, actual Windows 10/11 offline install, user-approved weighted final blueprint acceptance. Do not claim 85% until these are tested.

**Official final completion UNASSESSED — 85% goal not verified — [작업중] / RELEASE HOLD / SALE NO-GO.**
