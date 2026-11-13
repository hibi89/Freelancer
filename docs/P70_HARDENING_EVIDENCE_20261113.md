# BID AX P70 hardening verification — 2026-11-13 KST

## Scope and result
- Source SHA: 027c4592e7aed1d806a9218269efe534952a8f04, private repository hibi89/Freelancer, branch product/bid-ax-public-procurement.
- Exact six changed source/test Git blobs matched local git hash-object.
- Local Linux Python 3.13.5: python -Werror::ResourceWarning -m unittest discover -s tests -q -> 60 PASS / 0 FAIL / 0 SKIP (45 prior + 15 new).
- python -m compileall -q bidax: PASS.
- Tk 8.6 Linux Xvfb smoke: PASS. This is not real Windows 10/11 acceptance or customer GUI validation.
- New GitHub Python CI: NOT RUN. Production/Vercel: NOT APPLICABLE. Real data.go.kr live queries: 0. No customer data, key or secrets used.
- Final blueprint R01-R21 official completion: UNASSESSED. User target 70% is NOT VERIFIED; [작업중] remains, RELEASE HOLD, no Kmong listing.

## Implemented and separately tested
1. Local, strictly validated JSON response snapshot adapter in bidax/official.py; no network; bounded page and success response checks, official HTTPS source guards, missing time fields fail closed. Original snapshot SHA-256 linked to imported notices. Imported notices always marked OFFICIAL_SNAPSHOT_UNVERIFIED, with mandatory human review for region, license, docs and budget; never automatically certify eligibility.
2. Local SQLite profile_events: multiple company profiles, version fingerprints, duplicate-safe event ingestion, latest lookup/history, integrity checks, backup and restore. Profile data is plaintext and must be protected with local OS account and filesystem permissions; this is not encryption or an authorization system.
3. CLI: import-official-snapshot, profile-save, profiles, screen-stored.
4. Tk controller: save and choose stored company profiles, preserving existing notice workflow.
5. JSON parser rejects duplicate object keys, preventing field-shadowing.
6. Tests/test_p70_hardening.py validates offline official response failure paths, URL spoofing, all-or-none import, revision/deduplication, profile tamper/restore, CLI and controller flow.

## R01–R21 denominator is unchanged
- R01–R04: official metadata/7-day query plan documented; actual API 1.3 response, legitimate customer key/terms, authorized listing/detail/attachments/quota/retry not yet verified.
- R05–R07: normalized input, immutable version, SQLite integrity, provisional offline response mapping (live contract unverified).
- R08: multiple saved profiles and reviewable versions now implemented offline; authentication and encryption unimplemented.
- R09–R11: prelim screening and fail-closed unknown qualifications implemented; legal/real bid eligibility NOT verified.
- R12–R16: existing on-demand deadlines, JSON/CSV/HTML, manual audit records, change trail, offline Tk GUI tested in synthetic scope. Real background alert, role separation, customer Windows and PDF not verified.
- R17–R18: installer/EXE NOT BUILT; backup/restore and profile SHA tested, key security and recovery-in-production NOT verified.
- R19–R21: 100 real notice cases, 10 human qualification reviews, commercial rights and Win10/11 pilot/owner launch approval NOT RUN.

## Architecture, cost and safety
- A hosted SaaS: continuous monitoring, but recurring server cost, high credentials/PII risk and operations burden.
- B customer-owned local SQLite/Tkinter: zero mandatory hosting cost, deterministic offline evidence, user-controlled storage; PC must run and source must be refreshed by user. Retained B for this work, no scope reduction.
- Official dataset: https://www.data.go.kr/data/15129394/openapi.do . Portal announced maximum 7-day query windows on 2026-11-10. Actual field mapping from customer-authorized 1.3 response remains unverified; if absent or inconsistent, quarantine instead of inventing qualifications.
- Source rollback: earlier P70 head 0b09ae630184333aa6c147579a429c20bddb016e; source commits f3aeff768c846d0e23803f1c0c4c19c36ddce6b3 and 027c4592e7aed1d806a9218269efe534952a8f04; preserve old customer DB/backup, restore only to a new file.

## Next verifiable gates
1. Approved owner R01–R21 weighted 100-point acceptance trace, separate from P70 technical stage; independent review to establish any actual final percent.
2. Authorized live API 1.3 schema and pagination, quota/429/retry/attachments and 100 genuine notices with 10 independently human-verified eligibility cases.
3. Python 3.11 + actual Windows10/11 use, secure role/at-rest handling, local alert resume, Korean report/PDF, EXE/installer, customer acceptance and release approval.

No official 70% claim or [작업중] removal without complete evidence and approved weights.
