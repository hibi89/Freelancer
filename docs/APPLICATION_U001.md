# U-001 — KPI reporting application packet

Updated **2026-10-27 KST** after checking the public Upwork job description and building the demo v2 in this chat.

## Actual job
[Build Actionable E-commerce KPI Reports With AI — Long-Term, Steady Work](https://www.upwork.com/freelance-jobs/apply/Build-Actionable-commerce-KPI-Reports-With-Long-Term-Steady-Work_~022113293406837226152/)

DVISIONMEDIA, Denmark; client expects weekly/monthly/quarterly ecommerce KPI reports built with approved AI tools, **each KPI versus brand-calculated targets**, quantitative actions, their design system, documented reusable workflow. They provide formulas, target rules, visual template and a walkthrough. Async/no unnecessary meetings; paid test for shortlisted candidates; >6 months indicated but **not a payment or weekly-hour guarantee**.

**Required in proposal:** First word `ACTIONABLE`; actual hourly rate and genuine weekly availability; Loom video **max 2 minutes** demonstrating an AI-built report and one applicant judgment call. Public listing previously showed $15–22/hour and 20–50 proposals, interviewing 3; **exact open status, current cost and applicant counts must be rechecked in logged-in Upwork before submission.** Client can require the applicant's own voice or explanation; do not misrepresent AI voice as the owner's.

## Demo v2 created and verified in ChatGPT work container — not uploaded to GitHub

**Artifact:** `Freelancer_KPI_Application_Ready_v2.zip`, contains:
- `dashboard.html` offline with calculated target table;
- `Executive_KPI_Report_WITH_TARGETS.pdf` 3-page English PDF;
- `KPI_Workbook.xlsx`, synthetic order/spend CSVs, `metrics.json`, `dynamic_targets.json`, `dynamic_target_comparison.csv`;
- `build_sample.py`, `build_presentations.py`, `build_dynamic_targets.py`, `BUILD_ALL.py`, `BUILD_WINDOWS.bat`;
- `START_HERE_KO.txt`, `LOOM_SCRIPT_SHORT_EN.txt`, `UPWORK_PROPOSAL_DRAFT.txt`, `REBUILD_AND_TARGET_FORMULAS.md`.

The exact ZIP is in the **2026-10-27 ChatGPT conversation** with a download link; source paths in a chat runtime are **not durable GitHub paths**. Owner must download it on their PC. If inaccessible in a future chat, ask the owner to upload the ZIP rather than invent a path.

### Actual verified simulation
- 2,806 synthetic orders, July–Sept 2026; quarter net sales $192,975 (rounded).
- September Meta Ads actual attributed ROAS **1.773x** vs dynamic cost-derived break-even **2.287x**, post-ad contribution **-$1,738.33**.
- September Google Ads actual attributed ROAS **3.161x**, post-ad contribution **+$2,336.60**.
- September combined *PAID ONLY* ROAS **2.375x**. Validation caught and corrected an earlier accidental all-channel-sales / ad-spend aggregation that inflated paid ROAS. The finished v2 code explicitly checks against the correct paid-only figure.
- Break-even formula: `target_roas = net_sales / (net_sales - COGS - fulfillment - payment_fees)`. This is a retrospective demo **financial floor**, **NOT the real client's target formula**. Fixed overhead, tax and incrementality excluded.
- v2 QA: dynamic target source CSV cross-checks **PASS**, 9 table rows **PASS**, 3-page PDF render **PASS**, ZIP archive structure **PASS**. HTML existence/static content checked; interactive browser screenshot **not yet independently confirmed** (headless browser in container did not finish).
- Workbook reused from initial version and does **not** independently show the new dynamic targets (these are in CSV, HTML, PDF).

### Loom simple script
> Hello. I built this KPI dashboard with Python and AI tools. All numbers are simulated, not real client data. I calculated sales, return on ad spend, and profit. Here is my judgment call: I would not increase Meta Ads yet. In September, Meta's return was 1.77, below the calculated break-even level of 2.29. Its contribution after ads was negative, while Google was positive. I would check tracking and ad creatives first, then test a small change. I would measure the result using profit, not return on ad spend alone. Thank you.

### Tailored proposal draft (not sent)
> ACTIONABLE — I build repeatable e-commerce KPI reports with AI-assisted workflows and Python-based numerical checks. I prepared a synthetic demo with an offline dashboard, a PDF executive summary, and calculated break-even ROAS comparisons. My judgment call was to investigate Meta Ads before scaling because its September attributed ROAS (1.77x) was below the modeled break-even level (2.29x) and its contribution after ad spend was negative. I understand your team will provide the definitive target logic, templates and walkthrough; I would follow those exactly rather than substitute my demo's assumptions. I can document the workflow for weekly, monthly and quarterly reuse.
>
> Rate: $17/hour. Availability: 10 hours/week **only if genuinely available**.
>
> Loom: [replace with actual video link].
>
> This demo uses synthetic data, not a real client project. I can provide an hour estimate before a paid test.

## NEXT OWNER TASK — just one step
1. Click the ZIP download link in the generating chat, extract ZIP; **double-click dashboard.html**, scroll to `Cost-derived targets`, and verify it opens visually. The owner can reply `열렸다` or send screenshot.
2. Assistant then coaches **one-step Loom recording** in short Korean instructions; avoid overwhelming onboarding.
3. Check current Upwork account readiness (identity profile, Connects, job open), then seek explicit approval and submit only when everything is ready.

**NOT DONE:** user hasn't confirmed opening v2 ZIP/HTML; Loom is not recorded; proposal isn't submitted; no money spent; no job won. The minimum cost and job availability are not verified inside logged-in Upwork.

## Update — QA gating v3 (2026-10-27)
The latest owner-downloadable bundle is **`Freelancer_KPI_Application_QA_v3.zip`**, replacing v2. Detailed engineering verification is in [QUALITY_GATE.md](QUALITY_GATE.md).
- PASS: 85,783 assertion evaluations, 7/7 injected failures detected (duplicate order, wrong net revenue, missing ad spend, inflated ROAS, forged target, HTML tamper, broken PDF). PDF reviewed visually and key workbook values spot checked.
- Actual metrics unaffected: synthetic mock data July–September, Q3 net $192,975.16; true paid-channel ROAS 2.623x. No real client validation.
- **Connects:** official unit price $0.15, purchased in bundles/custom amounts; user last had 0 Connects. Specific bid cost unknown until clicking Apply now (do not submit). Paid monthly subscription not compulsory. Without free bonus/invitation or sufficient Connects, normal proposal requires buying some. No purchase recommended yet.
- Still need client-specific formulas, real client design, live-status check, human visual confirmation and 2-minute Loom; no application was sent.
