"""Private read-only daily AXDEV run summary, never a completion claim."""
from __future__ import annotations

import argparse
import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

from axdev.core import ContractError, VALID_STATES


def summary(state: Path) -> dict:
    dbpath = state.expanduser().absolute() / "factory.sqlite3"
    if dbpath.is_symlink() or any(part.is_symlink() for part in dbpath.parents):
        raise ContractError("status database symlink forbidden")
    if not dbpath.is_file():
        return {"phase": "NOT_INITIALIZED", "counts": {s: 0 for s in sorted(VALID_STATES)},
                "model_calls_today": 0, "daily_budget_configured": False,
                "official_verification": "NOT_VERIFIED"}
    with closing(sqlite3.connect(dbpath.resolve().as_uri() + "?mode=ro", uri=True)) as db:
        records = db.execute("SELECT status, COUNT(*) FROM runs GROUP BY status").fetchall()
        tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        daily = 0
        if "model_calls" in tables:
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            daily = db.execute("SELECT COUNT(*) FROM model_calls WHERE day_utc=?",
                               (today,)).fetchone()[0]
    counts = {s: 0 for s in sorted(VALID_STATES)}
    for state_name, count in records:
        if state_name not in counts:
            raise ContractError("unknown checkpoint state")
        counts[state_name] = count
    return {"phase": "RUNNING_OR_STOPPED", "counts": counts,
            "model_calls_today": daily, "daily_budget_configured": "UNKNOWN",
            "official_verification": "NOT_VERIFIED",
            "note": "Model call reservations include failed/interrupted attempts; not model success."}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Read-only private AXDEV daily summary")
    parser.add_argument("--state", type=Path, required=True)
    a = parser.parse_args(argv)
    print(json.dumps(summary(a.state), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, sqlite3.Error, ContractError) as exc:
        print("AXDEV_DAILY_STATUS_ERROR:", type(exc).__name__)
        raise SystemExit(2)
