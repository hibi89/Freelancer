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
    export = sub.add_parser("export", help="create new JSON/CSV/HTML report; never overwrite")
    export.add_argument("profile_file")
    export.add_argument("output_file")
    export.add_argument("--format", choices=("json", "csv", "html"), required=True)
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
    onbid_imp = sub.add_parser("onbid-import", help="import authorized normalized LOCAL Onbid asset/result snapshot")
    onbid_imp.add_argument("json_file")
    sub.add_parser("onbid-report", help="report locally imported Onbid assets and results")
    court_imp = sub.add_parser("court-import", help="store SHA/checklist of user-owned LOCAL court PDF/TXT")
    court_imp.add_argument("file")
    court_imp.add_argument("--case-id", required=True)
    court_imp.add_argument("--source-note", required=True, help="why user has permission to inspect file")
    court_imp.add_argument("--consent", action="store_true", help="owner explicitly agrees to local import")
    court_rep = sub.add_parser("court-report", help="local-only human-review checklist")
    court_rep.add_argument("case_id")
    gui = sub.add_parser("gui", help="launch offline desktop GUI (Tkinter)")
    args = p.parse_args(argv)

    if args.command == "restore":
        result = restore_backup(args.source, args.db)
    elif args.command in {"onbid-import", "onbid-report"}:
        from .onbid import OnbidStore
        with OnbidStore(args.db) as store:
            result = (store.import_snapshot(read_local_json(args.json_file))
                      if args.command == "onbid-import" else store.report())
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
