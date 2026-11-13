# BID AX Onbid real response: support direct root header/body

2026-11-14 KST. **Confirmed by user's safe Windows field-name-only console output**, NOT by receiving the raw data or credential.

The user previously received `onbid_result_list` dataset 15157252 and saved a 15,930-byte quarantined JSON packet; local SHA audit passed, but the parser held it with `UNRECOGNIZED_ENVELOPE`.

Known structure of `raw_response` from the user is exactly root keys `header`, `body`; the header contains `resultCode` and `resultMsg`, and body contains `items`, `numOfRows`, `pageNo`, `totalCount`. No values, list items, private IDs or API key were shared. The prior inspector only handled `{"response":{"header":...,"body":...}}`, so the error can be explained by the envelope difference without asserting the API returned a successful business result.

## Implementation / controls

- `bidax/response_audit.py` accepts either direct `{header, body}` or nested `{response:{header, body}}`; rejects mixed/ambiguous direct+nested layout and all unknown layouts.
- Preserves canonical JSON hash, service/dataset/request validation, response-key reflection rejection, safe non-success status hold, page/rows/total/items strict checks, no automatic import, and human/legal review HOLD.
- `tests/test_onbid_root_envelope.py` covers newly observed direct shape, non-success status, page mismatch, item count mismatch, ambiguous shapes, tampered stored response, and sensitive reflected field. Existing nested-shape tests continue.
- Linux Python3.13.5 `python -Werror::ResourceWarning -m unittest discover -s tests -q` **215 PASS / 0 FAIL** and `python -m compileall -q bidax tests` **PASS**. No additional government API requests or real user packet received.

## Owner acceptance (offline; no download of sensitive JSON)

Use the latest inspector on the ORIGINAL quarantined packet in its original `BID_AX` project, or inspect an exact-copy packet in a separate folder. Run `api-inspect` with the existing absolute path. Report only the safe summary, never `raw_response`, file contents, API key, auction asset details or personal data. A `STRUCTURE_CANDIDATE_REVIEW_REQUIRED` result proves a candidate JSON layout only, not full field mapping, authenticity, rights, or approval of auction eligibility.

**Status:** 29 fixed full-design requirements. Official completion UNASSESSED, 85% NOT demonstrated, `[작업중]`, RELEASE HOLD, not listed on Kmong. Windows 3.11 actual reinspection not yet executed with updated parser.
