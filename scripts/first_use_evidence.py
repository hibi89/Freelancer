"""Generate a local-only, privacy-minimized read-only trial report.

Reads only AXDEV synthetic trial SQLite metadata, never model prompts,
project source, GitHub tokens, environment variables or model responses.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import re
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

from axdev.core import ContractError

HEX40 = re.compile(r"^[0-9a-f]{40}$")
VALID = {"QUEUED", "CODING", "IMPLEMENTED", "REVIEW", "PREPARED", "VERIFIED", "HOLD"}


def _safe(path: Path) -> Path:
    raw = Path(path).expanduser().absolute()
    if raw.is_symlink() or any(parent.is_symlink() for parent in raw.parents):
        raise ContractError("trial path contains a symlink")
    return raw.resolve()


def report(trial: Path) -> dict:
    root = _safe(trial)
    repo = root / "trial-repo"
    plan = root / "trial-plan.json"
    state = root / "state"
    if any(part.is_symlink() for part in (repo, plan, state, repo / ".git")):
        raise ContractError("synthetic trial fixture symlink forbidden")
    if not (repo / ".git").exists() or not plan.is_file():
        raise ContractError("synthetic trial fixture missing or invalid")
    counts = {k: 0 for k in sorted(VALID)}
    commit_count = 0
    if (state / "factory.sqlite3").is_symlink():
        raise ContractError("state database symlink forbidden")
    db = state / "factory.sqlite3"
    if db.is_file():
        with closing(sqlite3.connect(db.resolve().as_uri() + "?mode=ro", uri=True)) as conn:
            rows = conn.execute("SELECT status, commit_sha FROM runs").fetchall()
        for status, commit in rows:
            if status not in VALID:
                raise ContractError("unknown checkpoint state")
            counts[status] += 1
            if status == "VERIFIED" and HEX40.fullmatch(commit):
                commit_count += 1
    event_count = 0
    if (state / "run-events.jsonl").is_symlink():
        raise ContractError("event log symlink forbidden")
    if (state / "run-events.jsonl").is_file():
        with (state / "run-events.jsonl").open("r", encoding="utf-8") as f:
            for _ in f:
                event_count += 1
                if event_count > 10000:
                    raise ContractError("trial event count too large")
    return {
        "report_version": 1,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "platform": platform.system(), "python": platform.python_version(),
        "scope": "owner local synthetic trial; no actual product source",
        "state_counts": counts, "verified_commit_count": commit_count,
        "task_events": event_count,
        "real_model_call_proven_by_this_report": False,
        "effective_opencode_permissions_verified": False,
        "network_isolation_verified": False,
        "gpu_peak_vram_measured": False,
        "customer_source_uploaded": False,
        "notes": [
            "A VERIFIED SQLite row alone cannot prove which model or provider ran.",
            "Retain CLI invocation result and local runtime versions for owner inspection.",
            "This report never uploads, executes a model, or reads task source.",
        ],
    }


def main(argv=None):
    p = argparse.ArgumentParser(description="Private read-only AXDEV trial evidence report")
    p.add_argument("--trial", type=Path, default=Path.home() / "AXDEV_TRIAL")
    p.add_argument("--output", type=Path,
                   help="new evidence file; default private timestamped path")
    args = p.parse_args(argv)
    value = report(args.trial)
    if args.output is not None:
        output = _safe(args.output)
    else:
        private = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / ".axdev")))
        output = _safe(private / "AXDevFactory" / "trial-evidence" /
                       ("trial-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + ".json"))
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as f:
        f.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"evidence_file": str(output), "state_counts": value["state_counts"],
                      "real_model_e2e_verified": False,
                      "message": "Review local CLI and evidence before real project use."},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, TypeError, sqlite3.Error, ContractError) as exc:
        print("AXDEV_TRIAL_REPORT_ERROR:", str(exc))
        raise SystemExit(2)
