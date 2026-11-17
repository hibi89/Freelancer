# AX Dev Factory — Owner Console (Windows 11)

This is the local owner-facing interface for the existing AX Dev Factory F01–F20 engine. It does not change the immutable task contract, review identity, local Git integration behavior, model permissions or publishing policy.

## Launch

1. Keep the approved private queue settings in `%LOCALAPPDATA%\AXDevFactory\settings.json` (created separately by `scripts.configure_queue`).
2. From the AX Dev Factory project root, double-click `RUN_OWNER_DASHBOARD.cmd` or run:

   ```powershell
   python -m scripts.owner_dashboard --settings "$env:LOCALAPPDATA\AXDevFactory\settings.json" --port 8765 --confirm-local-dashboard
   ```
3. On the **same Windows PC**, open `http://127.0.0.1:8765/`. Stop the console server with Ctrl+C. Do not forward or publish this port.

No environment, dependencies, service account or OS scheduler task is installed by the dashboard. It uses only Python 3.11+ stdlib and the existing local configuration.

## Implemented functions

- Live-on-refresh summary of task checkpoint counts `QUEUED`, `CODING`, `IMPLEMENTED`, `REVIEW`, `PREPARED`, `VERIFIED` and `HOLD` from the existing `scripts.queue_control.control('status', ...)` endpoint. Shows up to 12 bounded task identifiers, never task bodies, customer content, repository paths, credentials or model responses.
- Verified/total ratio is a **local SQLite task checkpoint ratio**, not a formal product verification percentage or proof of current model residency.
- One click to request **stop at the next safe task boundary**, and one confirmed **resume signal** to clear the stop flag. Resume does **not** launch an AI model or queue. Manual refresh; no hidden automatic action.
- Responsive layout, keyboard focus, accessible table and progress semantics, Korean copy. No network resources, JavaScript, external fonts or analytics.
- Fail-closed host authority, same-origin referrer, CSRF token, response CSP and local-only HTTP binding remain in `scripts.owner_dashboard.py`.

## Product preview

The downloadable `AXDevFactory_Product_Preview.html` included in the conversation is a **static synthetic-data preview** of this renderer. It has both control buttons disabled. The GitHub product's live browser dashboard must be launched locally for actual status updates and stop/resume controls.

## Validation and limits

- Check the new `tests/test_owner_dashboard_view.py` renderer checks plus existing `tests/test_owner_dashboard_http.py` HTTP authority/CSRF tests.
- All real-model coding and Windows Sandbox execution remain owned by the existing local queue; the dashboard must not create a new model run, modify a task contract, approve GitHub writes or introduce untrusted uploads.
- A real Windows 11 browser check of the newly styled dashboard is still required for final UX sign-off. Do not confuse this with prior browser checks of the earlier basic dashboard.
- The Windows 10 matrix, owner real-use approval, formal weighted verification and any commercial deployment remain distinct.
