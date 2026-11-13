# BID AX official API quarantine response audit (2026-11-14 KST)

**Scope:** Final blueprint R01–R29 unchanged, target 85%. Existing 4 portal-service applications are reported complete by the user; the four service identifiers are 15129394, 15157220, 15157252 and 15157254. A shared credential can be used for separately authorized services; the key itself was never received, stored in GitHub, or used in this test.

## Actual code and reproducible verification

- `bidax/api_gateway.py`: credential reflection defense now also checks parsed/URL-encoded response and sensitive field keys, not just literal wire bytes; creates a canonical SHA256 of the parsed JSON response alongside the original wire SHA256. SHA is an accidental mutation check, not an agency signature or adversarial integrity guarantee.
- New `bidax/response_audit.py` and `api-inspect LOCAL_PACKET.json` CLI: strictly OFFLINE read of a saved packet. Confirms BID AX quarantine marker, service/dataset/parameter identity and stored canonical response hash when present. Fails closed on duplicate JSON keys, symlink/large files, unsuccessful envelopes, inconsistent page/total/item count and unexpected JSON shapes. Returns **only safe metadata**, with explicit `auto_import_allowed=false` and `legal_qualification_approved=false`.
- Legacy packets without canonical response hash remain `LEGACY_HASH_NOT_STORED`. A structurally consistent packet is only `STRUCTURE_CANDIDATE_REVIEW_REQUIRED`; **it cannot be promoted to the actual bidding/auction ledgers**, cannot prove which agency sent it and cannot satisfy legal qualification or commercial-use review. The reader cannot validate original wire SHA because the original transfer bytes were not retained in legacy snapshots.
- `.gitignore`: ignore `local/`, `quarantine/`, `*.raw-api.json`, preventing common accidental Git commits. Users must still not share customer original replies, files, keys, personal identifiers, or raw data with ChatGPT/GitHub.
- New offline response audit unit tests exercise parser, safe CLI, mismatch, tamper, shared-key reflection. **Official API requests: zero.** Real Windows and Python3.11 OS run: unverified; original private GitHub Actions blueprint gate is NOT a Python cross-platform test.

## Owner PC instructions (only after choosing to transmit to official API)

From a Python terminal in the repository's own folder; create the `local` folder first. These commands do not read `.env`, store keys or transmit files to ChatGPT.

```powershell
New-Item -ItemType Directory -Force .\local | Out-Null
python -m bidax.cli --db .\local\bidax.db api-probe onbid_result_detail examples\onbid_result_detail_plan_LOCAL_ONLY.json
```

When the user deliberately approves a real single-page request and replaces example IDs/dates with their own permitted query:

```powershell
python -m bidax.cli --db .\local\bidax.db api-probe onbid_result_detail examples\onbid_result_detail_plan_LOCAL_ONLY.json --live --out .\local\result_001.json
python -m bidax.cli --db .\local\bidax.db api-inspect .\local\result_001.json
```

The `--live` variant contacts the official endpoint with the entered customer service key, counts attempts even on failure, and saves an **unverified, potentially sensitive** raw packet on the customer's PC. Never run it without operator consent. A dry-run has no network or key prompt. The printed `api-inspect` summary is intentionally free of the raw documents and credentials, but should still be handled confidentially until inspection of actual agency fields and rights.

## Current remaining final-85 gates

1. Verified real G2B and all three Onbid services' official operations and actual response field mapping, authorized live query, full pagination/resume/attachment evidence. The 15157220 **base endpoint and `pbancMngNo` are official**, but actual operation route remains unverified and `ready=false` stays mandatory.
2. Real 100 official notices and 10 independently human-reviewed qualification cases, not synthetics; access permissions and commercial/API/attachment rights.
3. Real Windows10/11 customer installation, Python3.11 GUI, EXE/installer, Korean PDF/font rights, local data security, encrypted key if persistence is later needed, customer acceptance.
4. Other R01–R29 acceptance items remain unchanged; do not claim official 85% from unit counts or partial engineering milestones.

**Status: 85% NOT VERIFIED / official UNASSESSED, [작업중], RELEASE HOLD, Kmong not registered. No extra weights or re-baselining requested.**

## Sources

- https://www.data.go.kr/data/15129394/openapi.do
- https://www.data.go.kr/data/15157220/openapi.do
- https://www.data.go.kr/data/15157252/openapi.do
- https://www.data.go.kr/data/15157254/openapi.do
