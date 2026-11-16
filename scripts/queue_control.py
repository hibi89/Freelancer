"""Local-only status/stop/resume controls. No AI or GitHub network actions."""
from __future__ import annotations
import argparse
import json
import sqlite3
from pathlib import Path
from scripts.configure_queue import default_file
from axdev.core import ContractError


def _settings(path: Path):
    path = path.expanduser().absolute()
    if path.is_symlink() or any(part.is_symlink() for part in path.parents) or not path.is_file():
        raise ContractError("reviewed local queue settings not found")
    config = json.loads(path.read_text(encoding="utf-8"))
    if config.get("version") != 1:
        raise ContractError("unsupported local queue version")
    raw_state = Path(config["state"]).expanduser().absolute()
    if raw_state.is_symlink() or any(part.is_symlink() for part in raw_state.parents):
        raise ContractError("state path cannot contain symlinks")
    state = raw_state.resolve()
    repo = Path(config["repo"]).expanduser().resolve()
    if state == repo or repo in state.parents:
        raise ContractError("queue state must not be inside target checkout")
    return config, state


def control(command: str, settings: Path, confirm: bool = False) -> dict:
    config, state = _settings(settings)
    signal = state / "STOP.REQUESTED"
    if signal.is_symlink():
        raise ContractError("stop signal must not be symlink")
    if command == "stop":
        state.mkdir(parents=True, exist_ok=True)
        # Concurrent calls are safely idempotent; no running coder is killed.
        try:
            with signal.open("x", encoding="utf-8") as file:
                file.write("Owner stop requested between tasks.\n")
        except FileExistsError:
            pass
        return {"action": "stop", "stop_requested": True,
                "effect": "next-task boundary only", "execution_started": False}
    if command == "resume":
        if not confirm:
            raise ContractError("resume requires --confirm; no tasks are auto-started")
        signal.unlink(missing_ok=True)
        return {"action": "resume", "stop_requested": False,
                "execution_started": False}
    if command == "status":
        statuses = {}
        db = state / "factory.sqlite3"
        if db.is_symlink():
            raise ContractError("SQLite state cannot be symlink")
        if db.is_file():
            # SQLite URI read-only mode; never create or modify a state database.
            with sqlite3.connect(db.resolve().as_uri() + "?mode=ro", uri=True) as conn:
                statuses = dict(conn.execute("SELECT id, status FROM runs").fetchall())
        counts = {state: list(statuses.values()).count(state)
                  for state in ("QUEUED", "CODING", "REVIEW", "PREPARED", "VERIFIED", "HOLD")}
        events = state / "run-events.jsonl"
        event_count = 0
        if events.is_symlink():
            raise ContractError("event log cannot be symlink")
        if events.is_file():
            with events.open("r", encoding="utf-8") as file:
                event_count = sum(1 for _ in file)
        return {"action": "status", "stop_requested": signal.exists(),
                "counts": counts, "tasks": statuses, "events_recorded": event_count,
                "model_running": "UNKNOWN", "execution_started": False}
    raise ContractError("unsupported queue control action")


def main(argv=None):
    parser = argparse.ArgumentParser(description="AXDEV local queue controls")
    parser.add_argument("action", choices=("status", "stop", "resume"))
    parser.add_argument("--settings", type=Path, default=default_file())
    parser.add_argument("--confirm", action="store_true")
    args = parser.parse_args(argv)
    result = control(args.action, args.settings, args.confirm)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, sqlite3.Error, ContractError) as exc:
        print("AXDEV_CONTROL_ERROR:", str(exc))
        raise SystemExit(1)
