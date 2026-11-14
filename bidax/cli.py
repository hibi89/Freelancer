"""BID AX local-only CLI. No network, billing, or bid submission."""
from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
from uuid import uuid4

from .core import BidLedger, restore_backup
from .workflow import build_report, due_alerts, write_new_report, read_local_json


def main(argv=None):
    p = argparse.ArgumentParser(prog="bidax", description="Offline tender pre-screening; not legal eligibility")
    p.add_argument("--db", required=True, help="local SQLite path")
    sub = p.add_subparsers(dest="command", required=True)
    imp = sub.add_parser("import", help="import normalized, authorized JSON notices")
    official = sub.add_parser("import-official-snapshot", help="strict OFFLINE local G2B response; provisional mapping")
    official.add_argument("json_file")
    official.add_argument("--category", required=True, choices=("goods", "services", "construction", "foreign"))
    official.add_argument("--obtained-at", required=True, help="real observed ISO timestamp with timezone")
    prof_save = sub.add_parser("profile-save", help="append local company profile version")
    prof_save.add_argument("json_file")
    sub.add_parser("profiles", help="list locally saved companies")
    prof_stored = sub.add_parser("screen-stored", help="screen against latest saved local company profile")
    prof_stored.add_argument("company")
    imp.add_argument("json_file")
    screen = sub.add_parser("screen", help="source-linked preliminary report")
    screen.add_argument("profile_file")
    screen.add_argument("--now", help="ISO8601 offset-aware time for reproducible checks")
    export = sub.add_parser("export", help="create new JSON/CSV/HTML/PDF report; never overwrite")
    export.add_argument("profile_file")
    export.add_argument("output_file")
    export.add_argument("--format", choices=("json", "csv", "html", "pdf"), required=True)
    hist = sub.add_parser("history")
    hist.add_argument("notice_no")
    changes = sub.add_parser("changes")
    changes.add_argument("notice_no")
    review = sub.add_parser("review", help="human-only audit entry; no legal approval")
    review.add_argument("notice_no")
    review.add_argument("fingerprint", help="fingerprint from current screened result")
    review.add_argument("reviewer")
    review.add_argument("decision", choices=("확인", "보류", "반려"))
    review.add_argument("note")
    review.add_argument("--request-id", default=None, help="UUID for idempotent retries")
    alerts = sub.add_parser("alerts", help="on-demand deadline reminders")
    alerts.add_argument("--hours", type=int, default=72)
    backup = sub.add_parser("backup")
    backup.add_argument("target")
    restore = sub.add_parser("restore", help="restore backup into NEW database file")
    restore.add_argument("source")
    stage = sub.add_parser("stage-page", help="offline local authorized G2B page, resumable batch")
    stage.add_argument("json_file")
    stage.add_argument("--batch-id", required=True, help="unique UUID for one query snapshot")
    stage.add_argument("--category", required=True, choices=("goods", "services", "construction", "foreign"))
    stage.add_argument("--start", required=True, help="7-day-or-less query start with UTC offset")
    stage.add_argument("--end", required=True, help="query end with UTC offset")
    stage.add_argument("--obtained-at", required=True, help="observed ISO timestamp with UTC offset")
    status = sub.add_parser("stage-status", help="view durable offline staging checkpoint")
    status.add_argument("batch_id", help="UUID of the staged batch")
    poll = sub.add_parser("poll-alerts", help="save-once due reminder observations; PC must be on")
    poll.add_argument("--hours", type=int, default=72)
    onbid_plan = sub.add_parser("onbid-plan", help="validate official metadata query inputs OFFLINE, no network/key")
    onbid_plan.add_argument("kind", choices=("announcement_assets", "result_list", "result_detail"))
    onbid_plan.add_argument("params_json", help="local object of documented required query parameters, without serviceKey")
    onbid_plan.add_argument("--page", type=int, default=1)
    onbid_plan.add_argument("--rows", type=int, default=10)
    onbid_imp = sub.add_parser("onbid-import", help="import authorized normalized LOCAL Onbid asset/result snapshot")
    onbid_imp.add_argument("json_file")
    sub.add_parser("onbid-report", help="report locally imported Onbid assets and results")
    court_imp = sub.add_parser("court-import", help="store SHA/checklist of user-owned LOCAL court PDF/TXT")
    court_imp.add_argument("file")
    court_imp.add_argument("--case-id", required=True)
    court_imp.add_argument("--source-note", required=True, help="why user has permission to inspect file")
    court_imp.add_argument("--consent", action="store_true", help="owner explicitly agrees to local import")
    preview = sub.add_parser("court-preview", help="optional local PDF/TXT keyword mentions (not legal findings)")
    preview.add_argument("file")
    preview.add_argument("--case-id", required=True)
    preview.add_argument("--source-note", required=True)
    preview.add_argument("--consent", action="store_true")
    court_rep = sub.add_parser("court-report", help="local-only human-review checklist")
    court_rep.add_argument("case_id")
    portfolio = sub.add_parser("portfolio-report", help="three-source offline summary; no legal conclusion")
    filt = sub.add_parser("onbid-filter", help="local filters for known Onbid asset records")
    filt.add_argument("--property-type", choices=("부동산", "동산", "차량", "기타"))
    filt.add_argument("--max-bid-krw", type=int)
    filt.add_argument("--min-failed-rounds", type=int)
    watch = sub.add_parser("onbid-watch", help="append human-curated Onbid interest/review status")
    watch.add_argument("property_id")
    watch.add_argument("condition_id")
    watch.add_argument("state", choices=("관심", "검토 보류", "관심 해제"))
    watch.add_argument("note")
    watch.add_argument("--request-id", default=None, help="stable UUID for retry-safe replay")
    sub.add_parser("onbid-watchlist", help="audited Onbid preferences and source staleness")
    api_probe = sub.add_parser("api-probe", help="prepare official API query; --live explicitly fetches ONE quarantined page")
    api_probe.add_argument("service", choices=("g2b_goods", "g2b_services", "g2b_construction", "g2b_foreign",
                                               "onbid_announcement_assets", "onbid_result_list", "onbid_result_detail"))
    api_probe.add_argument("params_file", help="local JSON request inputs; NEVER put the service key in this file")
    api_probe.add_argument("--live", action="store_true", help="perform one authorized official request")
    api_probe.add_argument("--out", help="NEW local JSON quarantine output; required with --live")
    api_probe.add_argument("--daily-limit", type=int, default=8, help="independent local per-service daily cap 1..1000")
    diag = sub.add_parser("api-shape", help="OFFLINE safe envelope diagnosis; prints no response values")
    diag.add_argument("file", help="local quarantine JSON; never uploaded")
    inspect = sub.add_parser("api-inspect", help="OFFLINE structural review of one raw API quarantine packet")
    inspect.add_argument("file", help="local output JSON created by api-probe --live; no network/key")
    page_plan = sub.add_parser("api-page-plan", help="OFFLINE safe pagination estimate from one verified packet; no calls")
    page_plan.add_argument("file", help="existing local quarantine packet; never uploaded")
    onbid_audit = sub.add_parser("onbid-field-audit", help="OFFLINE public field-presence only; no private values")
    onbid_audit.add_argument("file", help="existing Onbid result-list quarantine packet")
    onbid_queue = sub.add_parser("onbid-detail-queue", help="OFFLINE local-only unexecuted result-detail candidate queue")
    onbid_queue.add_argument("file", help="existing Onbid result-list quarantine packet")
    onbid_queue.add_argument("--out", required=True, help="NEW private local JSON file")
    onbid_queue.add_argument("--consent", action="store_true", help="explicit consent to store property identifiers locally")
    ob_stage = sub.add_parser("onbid-stage-page", help="OFFLINE checkpoint one quarantined result-list page")
    ob_stage.add_argument("batch_id", help="UUID identifying one immutable query snapshot")
    ob_stage.add_argument("file", help="existing local API quarantine packet")
    ob_stage.add_argument("--consent", action="store_true", help="consent to store local file path/hash in DB")
    ob_status = sub.add_parser("onbid-stage-status", help="OFFLINE verify all original files in an Onbid page batch")
    ob_status.add_argument("batch_id", help="previously staged UUID")
    capture = sub.add_parser("onbid-continue", help="OFFLINE dry-run by default; optional bounded local owner-key continuation")
    capture.add_argument("batch_id", help="UUID; reuse it to resume this one immutable snapshot")
    capture.add_argument("first_packet", help="existing verified official Onbid result-list quarantine JSON")
    capture.add_argument("--out-dir", required=True, help="EXISTING local folder for create-only page JSON")
    capture.add_argument("--consent", action="store_true", help="allow local storage of packet paths and hashes")
    capture.add_argument("--live", action="store_true", help="explicitly contact official API, never unattended")
    capture.add_argument("--max-new-pages", type=int, default=4, help="max new HTTP calls in this run (1..25)")
    capture.add_argument("--daily-limit", type=int, default=24, help="local per-service attempt cap (1..1000)")
    gui = sub.add_parser("gui", help="launch offline desktop GUI (Tkinter)")
    args = p.parse_args(argv)

    if args.command == "restore":
        result = restore_backup(args.source, args.db)
    elif args.command == "api-shape":
        from .response_shape import diagnose_packet
        result = diagnose_packet(args.file)
    elif args.command == "api-inspect":
        from .response_audit import inspect_packet
        result = inspect_packet(args.file)
    elif args.command == "api-page-plan":
        from .response_audit import plan_remaining_pages
        result = plan_remaining_pages(args.file)
    elif args.command == "onbid-field-audit":
        from .onbid_official_bridge import field_audit
        result = field_audit(args.file)
    elif args.command == "onbid-detail-queue":
        from .onbid_official_bridge import write_detail_candidate_queue
        result = write_detail_candidate_queue(args.file, args.out, consent=args.consent)
    elif args.command == "onbid-stage-page":
        from .onbid_batch import stage_page
        result = stage_page(args.db, args.batch_id, args.file, consent=args.consent)
    elif args.command == "onbid-stage-status":
        from .onbid_batch import batch_status
        result = batch_status(args.db, args.batch_id)
    elif args.command == "onbid-continue":
        from .onbid_capture import continue_onbid_pages
        key = None
        if args.live:
            if not args.consent:
                raise PermissionError("explicit --consent required before any key prompt")
            from getpass import getpass
            key = getpass("Data.go.kr key (memory only, not saved): ")
        result = continue_onbid_pages(
            args.db, args.batch_id, args.first_packet, args.out_dir,
            consent=args.consent, live=args.live, service_key=key,
            max_new_pages=args.max_new_pages, daily_limit=args.daily_limit)
    elif args.command == "api-probe":
        from .api_gateway import create_plan, fetch_quarantined
        plan = create_plan(args.service, read_local_json(args.params_file))
        if args.live:
            if not args.out:
                raise ValueError("--live requires --out NEW local filename")
            from getpass import getpass
            key = getpass("Data.go.kr serviceKey (not saved): ")
            result = fetch_quarantined(plan, service_key=key, permission=True, db_path=args.db,
                                       output_path=args.out, daily_limit=args.daily_limit)
        else:
            result = plan
    elif args.command == "onbid-plan":
        from .onbid_plan import build_plan
        result = build_plan(args.kind, read_local_json(args.params_json), page=args.page, rows=args.rows)
    elif args.command in {"onbid-import", "onbid-report"}:
        from .onbid import OnbidStore
        with OnbidStore(args.db) as store:
            result = (store.import_snapshot(read_local_json(args.json_file))
                      if args.command == "onbid-import" else store.report())
    elif args.command in {"portfolio-report", "onbid-filter", "onbid-watch", "onbid-watchlist"}:
        from .portfolio import filter_onbid, portfolio_report, watch_onbid, watchlist
        if args.command == "portfolio-report":
            result = portfolio_report(args.db)
        elif args.command == "onbid-filter":
            result = filter_onbid(args.db, property_type=args.property_type,
                                  max_bid_krw=args.max_bid_krw,
                                  min_failed_rounds=args.min_failed_rounds)
        elif args.command == "onbid-watch":
            result = watch_onbid(args.db, property_id=args.property_id,
                                condition_id=args.condition_id, state=args.state,
                                note=args.note, request_id=args.request_id or str(uuid4()))
        else:
            result = watchlist(args.db)
    elif args.command == "court-preview":
        from .court import preview_document
        result = preview_document(args.file, case_id=args.case_id, user_consent=args.consent,
                                  source_note=args.source_note)
    elif args.command in {"court-import", "court-report"}:
        from .court import CourtStore
        with CourtStore(args.db) as store:
            result = (store.import_document(args.file, case_id=args.case_id, user_consent=args.consent,
                                            source_note=args.source_note)
                      if args.command == "court-import" else store.case_report(args.case_id))
    elif args.command == "gui":
        from .desktop import launch
        launch(args.db)
        return
    else:
        with BidLedger(args.db) as ledger:
            if args.command == "import":
                result = ledger.ingest(read_local_json(args.json_file))
            elif args.command == "import-official-snapshot":
                from .official import parse_official_snapshot
                parsed = parse_official_snapshot(read_local_json(args.json_file), args.category,
                                                 datetime.fromisoformat(args.obtained_at))
                result = {**ledger.ingest(parsed["notices"]), "source": "LOCAL_OFFICIAL_SNAPSHOT_UNVERIFIED",
                          "snapshot_sha256": parsed["snapshot_sha256"], "page_no": parsed["page_no"],
                          "total_count": parsed["total_count"], "notice": parsed["warning"]}
            elif args.command == "stage-page":
                from .batch import stage_snapshot
                result = stage_snapshot(ledger, args.batch_id, args.category,
                                        datetime.fromisoformat(args.start), datetime.fromisoformat(args.end),
                                        read_local_json(args.json_file), datetime.fromisoformat(args.obtained_at))
            elif args.command == "stage-status":
                from .batch import batch_status
                result = batch_status(ledger, args.batch_id)
            elif args.command == "poll-alerts":
                from .reminders import poll_due
                result = poll_due(ledger, within_hours=args.hours)
            elif args.command == "profile-save":
                result = ledger.save_profile(read_local_json(args.json_file))
            elif args.command == "profiles":
                result = {"companies": ledger.list_profiles(), "scope": "LOCAL_DB_ONLY"}
            elif args.command == "screen-stored":
                result = build_report(ledger, ledger.get_profile(args.company))
            elif args.command in {"screen", "export"}:
                profile = read_local_json(args.profile_file)
                now = datetime.fromisoformat(args.now) if args.command == "screen" and args.now else None
                report = build_report(ledger, profile, now)
                if args.command == "screen":
                    result = report
                else:
                    write_new_report(args.output_file, report, args.format)
                    result = {"export_created": args.output_file, "format": args.format, "count": report["count"]}
            elif args.command == "history":
                result = {"notice_no": args.notice_no, "events": ledger.events(args.notice_no),
                          "reviews": ledger.review_history(args.notice_no)}
            elif args.command == "changes":
                result = {"notice_no": args.notice_no, "changes": ledger.changes(args.notice_no)}
            elif args.command == "review":
                result = ledger.record_review(args.notice_no, args.fingerprint, args.reviewer,
                                              args.decision, args.note, request_id=args.request_id or uuid4().hex)
            elif args.command == "alerts":
                result = {"scope": "ON_DEMAND_ONLY", "items": due_alerts(ledger, within_hours=args.hours)}
            elif args.command == "backup":
                ledger.backup(args.target)
                result = {"backup_created": args.target, "overwritten": False}
            else:
                raise AssertionError("unsupported command")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
