"""No-network CLI for BID AX normalized notice fixtures and evidence review."""
import argparse
from datetime import datetime
import json
from pathlib import Path
from .core import BidLedger, evaluate


def main(argv=None):
    p = argparse.ArgumentParser(prog="bidax", description="Offline procurement pre-screening; not legal qualification")
    p.add_argument("--db", required=True, help="local SQLite file")
    subs = p.add_subparsers(dest="command", required=True)
    imp = subs.add_parser("import", help="import normalized authorized JSON notice array")
    imp.add_argument("json_file")
    match = subs.add_parser("screen", help="print review report with original source links")
    match.add_argument("profile_file")
    match.add_argument("--now", help="ISO8601 timezone-aware test time")
    history = subs.add_parser("history")
    history.add_argument("notice_no")
    backup = subs.add_parser("backup")
    backup.add_argument("target")
    args = p.parse_args(argv)
    with BidLedger(args.db) as ledger:
        if args.command == "import":
            result = ledger.ingest(json.loads(Path(args.json_file).read_text(encoding="utf-8")))
        elif args.command == "screen":
            profile = json.loads(Path(args.profile_file).read_text(encoding="utf-8"))
            now = datetime.fromisoformat(args.now) if args.now else None
            result = {"results": [evaluate(n, profile, now) for n in ledger.current()], "scope": "OFFLINE_PRELIMINARY_ONLY"}
        elif args.command == "history":
            result = {"notice_no": args.notice_no, "events": ledger.events(args.notice_no)}
        else:
            ledger.backup(args.target)
            result = {"backup_created": args.target}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
