# BID AX — First Onbid actual response, offline shape-only investigation

2026-11-14 KST. **User-reported external test, not reproduced by assistant**:

- Windows Python3.11 API `onbid_result_list` (dataset `15157252`) requested with the authorized user key through `api-probe --live`.
- Console showed `saved=local\\result_001.json`, `bytes=15930`, `calls_this_run=1`, `state=QUARANTINED_UNVERIFIED_OFFICIAL_MAPPING`.
- Offline `api-inspect` returned `REVIEW_HOLD`, `UNRECOGNIZED_ENVELOPE`, `CANONICAL_RESPONSE_SHA256_MATCH`; `auto_import_allowed=false` and `source_field_mapping_verified=false`.
- These observations prove a **response was received and saved with a self-consistent canonical hash**. They DO NOT prove the response represents authorized successful data rather than a JSON error envelope, nor that public-auction items were retrieved. SHA-256 matches local saved data, not government-signed authenticity. The user's service key and raw JSON were never shared with the assistant.

## Root cause / next control

The previous inspector only accepts JSON response wrapper `response.header` plus `response.body`, and the server returned a JSON *not matching that exact layout*. An alternate flat envelope, a different wrapper, or a server-level error body is plausible; **actual shape unknown until the user runs the offline shape diagnosis**.

Added `bidax/response_shape.py` / `api-shape` and the standalone root script `BID_AX_API_SHAPE_DIAG.py` that can run in the user's **existing** BID_AX project folder. Both are **offline**, verify local packet integrity using `inspect_packet`, and return *fixed public schema-labels and container kinds*, never serviceKey, identifiers, messages, record values, filenames, or private data. No API calls or new key input.

Run in PowerShell from the **same folder with `local\\result_001.json`**:

```powershell
py -3.11 .\\BID_AX_API_SHAPE_DIAG.py
```

After the new GitHub source is copied locally, this alternative also works:

```powershell
py -3.11 -m bidax.cli --db .\\local\\test.db api-shape .\\local\\result_001.json
```

The original result stays quarantined; **do not upload the result file, API key, screenshot with real auction values, or customer records**. Only the safe diagnostic JSON text may be shared for structural analysis.

### Tests / limitations

- Existing old suite 201 PASS and updated suite 207 PASS, Linux Python3.13.5, mock shapes only. Python3.11 AST syntax checked, Windows operation unverified.
- This does **not** modify automatic import/screening; all unknown official response envelopes remain on `REVIEW_HOLD`. A future change to the real parser must be based on authenticated user diagnostic and official contract, with tests and new SHA. Full R01-R29 final 85% not verified, `[작업중]`, RELEASE HOLD, customer release blocked.
