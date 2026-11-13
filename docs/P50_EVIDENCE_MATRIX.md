# CITEVAULT AX — P50 source-bound evidence matrix (2026-11-13 KST)

## Target and non-negotiable boundary
Owner request: reach **50% of the full CITEVAULT AX final blueprint**. This is an implementation goal, **not an achieved score**. The owner's `OWNER-FINAL-BLUEPRINT-100` requires approved requirement weights and exact-SHA execution evidence. Official status is **UNASSESSED**, and release remains **HOLD**.

- Source of design: `docs/FINAL_BLUEPRINT.md` / `docs/ACCEPTANCE_AND_ROADMAP.md`.
- Product implementation: `enterprise/p50-gate.mjs` (read-only synthetic integration harness); `tests/p50.test.mjs`; `.github/workflows/citevault-p50.yml`.
- Original engine: `hibi89/RAG_STUDIO@feature/p550-mapped-cited-journey`, **pinned** `c5867b3951f51bfa97cadd1aad8fb13e9cf9e604`. RAG `develop` and earlier tested `0e88301059c9cb6b876dd0f9cd9181e6fb5c6dc2` diverge (3 ahead / 48 behind when comparing tested commit to develop); do not reuse 95% personal-RAG acceptance as this enterprise product score.
- No SMAX/PREP private source copied; no customer input, real API, IAM change, network export, package promotion or production deployment.

## 50-stage evidence checklist

| Requirement / check | Implementation path | Evidence boundary | Status |
|---|---|---|---|
| AX approved fixture hash and schema | RAG `src/validate.mjs`, `enterprise/p50-gate.mjs` | Code inspected at pinned source; exact new gate CI not yet confirmed | WRITTEN / RUNTIME UNVERIFIED |
| Fixed SQLite revenue + order-row provenance | RAG `src/mixed-question.mjs` + `fixtures/ax_sample_v0` | Synthetic KRW 157,000 expected, integer SQL fixed query; no arbitrary SQL | WRITTEN / RUNTIME UNVERIFIED |
| TXT refund-policy citation and BM25 | RAG `src/document-search.mjs` and `mixed-question.mjs` | SHA-verified fixture lines; must refuse missing evidence | WRITTEN / RUNTIME UNVERIFIED |
| Fail-closed SMAX V1 producer contract | RAG `src/smax-intake.mjs` with `fixtures/smax_v1_boundary` | `REVIEW_REQUIRED` and `NOT_GRANTED`; **not** authorized AX promotion | WRITTEN / RUNTIME UNVERIFIED |
| No source mutation | `enterprise/p50-gate.mjs` full fixture digest before/after | Only synthetic AX fixture and bounded files; not customer documents | WRITTEN / RUNTIME UNVERIFIED |
| Negative tests: symlink, incorrect SQL oracle, altered SMAX | `tests/p50.test.mjs` | Intended GitHub action on private product branch | WRITTEN / CI UNCONFIRMED |
| PDF/DOCX parse and citation | Separate RAG core; not exercised by new gate | Need pinned-source executable test and accurate page/paragraph evidence | GAP |
| One real SMAX→approved AX package roundtrip | Private producer + authenticated reviewer | Two separate fixtures cannot prove conversion; HOLD preserved | GAP |
| PREP/SMAX native rights+semantic approval | Private producer and user signoff | Real authorization, signature, retention unverified | GAP |
| Full final design weighted 100-point acceptance | Owner-approved REQ weights + verified SHA | No arbitrary 50% credited; current official rate UNASSESSED | GAP |

## How to validate without copying original implementation
Clone/check out **both** repos with permission. In CITEVAULT's branch, use the exact pinned RAG commit:

```bash
# CITEVAULT checkout from Freelancer; RAG checkout separately:
git -C ../RAG_STUDIO checkout c5867b3951f51bfa97cadd1aad8fb13e9cf9e604
RAG_STUDIO_ROOT="$(cd ../RAG_STUDIO && pwd)" node --test tests/p50.test.mjs
```

GitHub Actions workflow uses `actions/checkout` for the product branch plus an exact pinned **public RAG** revision, permissions `contents:read`, no customer files, and runs the same command with Node 22.16.0. A push and workflow definition are **not** evidence of a passing job; check job log, run ID, test count, and exact SHA before upgrading status.

## Follow-up for a genuine P50 milestone
1. Observe action run and repair only reproduced failures; verify successful pinned-source 6-test gate and negative refusal cases.
2. Add actual PDF/DOCX tests and one *reviewer-authorized* PREP/SMAX→AX transfer, or record an explicit unmet 50 criterion. Never auto-authorize `REVIEW_HOLD`.
3. Review blueprint requirement weights with the owner. Until all P50 acceptance conditions and official scoring gates are evidenced, retain `[작업중]`, `UNASSESSED`, `RELEASE HOLD` and mark 50 **not yet verified**.
