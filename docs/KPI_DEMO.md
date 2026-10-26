# E-commerce KPI report — application demo

**Purpose:** Apply to Upwork KPI reporting projects showing evidence of AI-assisted data analysis, correct KPI definitions, and one independent human analytical decision.

## Generated in the user's previous conversation (owner-file preservation pending)
- `Ecommerce_KPI_Upwork_Portfolio_Package.zip`
- `Ecommerce_KPI_Sample/Executive_KPI_Report.pdf` — 2-page English report
- `Ecommerce_KPI_Sample/dashboard.html` — static dashboard
- `Ecommerce_KPI_Sample/KPI_Workbook.xlsx` — calculations/workbook
- `Ecommerce_KPI_Sample/portfolio_preview.png` — portfolio image
- `Ecommerce_KPI_Sample/synthetic_orders.csv`, `synthetic_ad_spend.csv`
- Code / storyboard may exist in ZIP — **inspect, don't assume**.

**Data:** Synthetic 2026 July–September mock e-commerce orders and ads, not actual customer data. These files were delivered via ChatGPT links; they are **NOT committed to this repository**. Verify they still exist in user's downloads. No private customer data used by design.

## QA checklist
- Files decode, HTML opens without internet, PDF and Excel open and graphs display.
- Revenue = valid gross-order value as defined; AOV = revenue/orders; ROAS = attributed revenue/ad spend; CAC = acquisition spend/new customers (must confirm distinct customers and source), profit margin definition transparently includes/excludes expenses.
- Compare 7, 8, 9-month/channel totals to raw CSV and documented assumptions. Do not fabricate new-customer counts or call attributed ROAS incremental return.
- No contradictions among PDF, dashboard, Excel or video.
- Big label: **SYNTHETIC DATA — PORTFOLIO DEMO.**
- Include screenshot and source links/QA in portfolio, avoid unearned claims.

## Video
- Prior posting indicated up to 2-minute Loom screen recording; verify live job details and whether user voice is specifically required.
- 0–20s: introduce *synthetic* case study and tools.
- 20–60s: show KPI charts/calculated totals and formulas, clear definition/limitations.
- 60–100s: explain one concrete decision (e.g. relative channel efficiency; conditional reallocation recommendation), not generic AI filler.
- 100–120s: deliverables and mention what was QA-checked.
- Codex can render a captioned MP4 if local video tooling exists, but a generated MP4 is **not automatically a Loom recording**; platform and client's instructions determine the final format.

**Status:** Demo artifact creation previously reported; local independent verification, Loom recording, actual bid **pending**.


## 2026-10-27: Job-spec gap analysis (public original text rechecked)
Job: https://www.upwork.com/freelance-jobs/apply/Build-Actionable-commerce-KPI-Reports-With-Long-Term-Steady-Work_~022113293406837226152/

**Actual demand, per original posting:**
- DVISIONMEDIA e-commerce agency. Build weekly/monthly/quarterly KPI reports, with AI (Claude for heavy lifting; ChatGPT or similar also explicitly accepted for portfolio proof).
- Each KPI evaluated against a **dynamic target calculated from that brand's own numbers**, never a typed static target.
- Every section ends in numeric-evidence-backed action; exact client-provided design system, KPI logic and targets.
- Document workflows so agency staff can reproduce them, with direct client materials: formulas, target definitions, design system, walkthrough video.
- Show reporting/AI proof, accurate instruction-following, reliable weekly availability. Paid trial only if shortlisted; before building give own time estimate.
- Apply with ACTIONABLE as first word, state hourly rate & weekly hours, Loom <=2m showing an AI-built report and ONE personally reasoned judgment. Live job status/terms still must be checked before actually applying.

**Inspected artifacts in this chat (current runtime):**
- Report PDF `Ecommerce_KPI_Sample/Executive_KPI_Report.pdf`: two pages, 2,806 mock orders, $192,975 net sales, 2.62x aggregate paid ROAS, 23.5% contribution margin.
- Synthetic order-level and spend CSVs and `build_sample.py`; reproducible deterministic seeded data calculations. `2min_demo_script.txt` present.
- Report has formulas/metrics and three evidenced recommendations (Meta ROAS Aug 2.46x -> Sep 1.77x; Google Aug 2.98x -> Sep 3.16x), plus synthetic/attribution disclaimers.
- **Important gap:** no per-KPI customer-data-derived target with actual-vs-target display; no client-specific brand design/template; no documented robust repeatable weekly/monthly/quarterly workflow with client data; no proof customer acceptance. Current mock report is an honest application DEMO, NOT the exact paid deliverable.
- GPT-6 + Python can implement transformations, targets, report layout and repeatable SOP once the customer's definitions, authentic source data and template are supplied; human QA essential for metric semantics, attribution, privacy, and strategic claims. No accuracy/client acceptance guarantee.
- Never pass client source data or secrets to external AI tools without authorization. Client instructions and actual case test determine feasibility.

**Immediate improvement for candidacy:** build a dynamic-target example using a transparently specified synthetic calculation (not inventing client formula), include an actual-vs-target chart in PDF/dashboard, and make a simple repeatability SOP. Then practice <=2m Loom and user approval before spending Connects.
