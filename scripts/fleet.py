"""Owner-initiated local multi-project AXDEV queue; never auto-starts or publishes.

The manifest pins each reviewed local queue configuration by SHA256.
No scheduled task, GitHub write, installation or OpenCode call on preview.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from contextlib import nullcontext
from datetime import datetime, timezone
from pathlib import Path

from axdev.core import ContractError, load_plan, single_worker_lock
from scripts.configure_queue import default_file
from scripts.queue_control import control

LIMIT = 10
ROOT = Path(__file__).resolve().parent.parent


def _local(path: Path) -> Path:
    raw = Path(path).expanduser()
    if not raw.is_absolute():
        raise ContractError("fleet requires absolute, owner-reviewed local paths")
    if raw.is_symlink() or any(parent.is_symlink() for parent in raw.parents):
        raise ContractError("symlink paths forbidden in fleet settings")
    return raw.resolve()


def _setting(path: Path) -> dict:
    source = _local(path)
    if not source.is_file():
        raise ContractError("fleet settings file is missing")
    raw = source.read_bytes()
    if len(raw) > 65536 or not raw:
        raise ContractError("invalid fleet settings file size")
    try:
        settings = json.loads(raw)
    except (ValueError, UnicodeDecodeError) as exc:
        raise ContractError("invalid fleet queue JSON") from exc
    if not isinstance(settings, dict) or settings.get("version") != 1:
        raise ContractError("fleet supports only version-1 queue settings")
    try:
        repo, state, plan = (_local(Path(settings[key]))
                             for key in ("repo", "state", "plan"))
    except (KeyError, TypeError, ValueError) as exc:
        raise ContractError("missing/invalid fleet queue paths") from exc
    if not (repo / ".git").exists() or not plan.is_file():
        raise ContractError("fleet requires existing local Git checkout and plan")
    if state == repo or repo in state.parents:
        raise ContractError("fleet state must be outside target repository")
    wanted = settings.get("plan_sha256")
    if not isinstance(wanted, str) or len(wanted) != 64:
        raise ContractError("fleet requires previously approved plan SHA256")
    if hashlib.sha256(plan.read_bytes()).hexdigest() != wanted:
        raise ContractError("approved fleet plan SHA256 mismatch")
    load_plan(plan)
    if not isinstance(settings.get("model"), str) or not settings["model"].startswith("ollama/"):
        raise ContractError("fleet permits only configured local Ollama model")
    maximum = settings.get("max_tasks")
    if type(maximum) is not int or not 1 <= maximum <= 100:
        raise ContractError("invalid task cap")
    return {"settings": str(source), "settings_sha256": hashlib.sha256(raw).hexdigest(),
            "repo": str(repo), "state": str(state)}


def _validate_unique(jobs: list[dict], manifest: Path):
    seen_settings, seen_repos, seen_states = set(), set(), set()
    for job in jobs:
        if (job["settings"] in seen_settings or job["repo"] in seen_repos
                or job["state"] in seen_states):
            raise ContractError("duplicate fleet settings, repository or state")
        seen_settings.add(job["settings"])
        seen_repos.add(job["repo"])
        seen_states.add(job["state"])
        root = manifest.parent
        for forbidden in (Path(job["repo"]), Path(job["state"])):
            if root == forbidden or forbidden in root.parents:
                raise ContractError("fleet manifest may not reside inside a target repo/state")


def create_manifest(settings_paths: list[Path], output: Path) -> dict:
    if not 1 <= len(settings_paths) <= LIMIT:
        raise ContractError("fleet supports 1..10 distinct owner-approved projects")
    output = _local(output)
    jobs = [_setting(path) for path in settings_paths]
    _validate_unique(jobs, output)
    data = {"version": 1, "jobs": [
        {"settings": j["settings"], "sha256": j["settings_sha256"]} for j in jobs]}
    output.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    try:
        fd = os.open(output, os.O_EXCL | os.O_CREAT | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise ContractError("fleet manifest already exists; no overwrite") from exc
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(encoded)
    except BaseException:
        output.unlink(missing_ok=True)
        raise
    return {"created": True, "projects": len(jobs), "output": str(output),
            "executed": False}


def load_manifest(manifest: Path) -> tuple[Path, list[dict]]:
    manifest = _local(manifest)
    if not manifest.is_file() or manifest.stat().st_size > 65536:
        raise ContractError("missing or oversized fleet manifest")
    data = json.loads(manifest.read_text(encoding="utf-8"))
    if (not isinstance(data, dict) or data.get("version") != 1
            or not isinstance(data.get("jobs"), list)
            or not 1 <= len(data["jobs"]) <= LIMIT):
        raise ContractError("invalid fleet manifest contract")
    jobs = []
    for item in data["jobs"]:
        if not isinstance(item, dict) or set(item) != {"settings", "sha256"}:
            raise ContractError("fleet job manifest requires exact keys")
        if not isinstance(item["settings"], str) or not isinstance(item["sha256"], str):
            raise ContractError("invalid fleet manifest entry")
        entry = _setting(Path(item["settings"]))
        if entry["settings_sha256"] != item["sha256"]:
            raise ContractError("fleet configuration changed since owner approval")
        jobs.append(entry)
    _validate_unique(jobs, manifest)
    return manifest, jobs


def _runtime(manifest: Path) -> Path:
    return manifest.parent / ".axdev-fleet-state"


def fleet_signal(manifest: Path, action: str, confirm: bool = False) -> dict:
    # STOP must still work if a project's settings/plan became corrupted.
    # RESUME must validate the entire reviewed manifest before unlocking.
    if action == "stop":
        manifest = _local(manifest)
        if not manifest.is_file():
            raise ContractError("fleet manifest missing")
    else:
        manifest, _ = load_manifest(manifest)
    root = _runtime(manifest)
    flag = root / "STOP.REQUESTED"
    if flag.is_symlink() or any(p.is_symlink() for p in flag.parents):
        raise ContractError("fleet stop path symlink forbidden")
    if action == "stop":
        root.mkdir(parents=True, exist_ok=True)
        try:
            with flag.open("x", encoding="utf-8") as f:
                f.write("Stop after currently executing project, before next project.\n")
        except FileExistsError:
            pass
    elif action == "resume":
        if not confirm:
            raise ContractError("fleet resume requires --confirm")
        flag.unlink(missing_ok=True)
    else:
        raise ContractError("invalid fleet signal")
    return {"action": action, "stop_requested": flag.exists(), "executed": False}


def fleet_run(manifest: Path, execute: bool = False, confirm: bool = False,
              max_projects: int = LIMIT, max_tasks: int = 100, runner=None) -> dict:
    if execute != confirm:
        raise ContractError("fleet execution requires BOTH --execute --confirm-reviewed")
    if (type(max_projects) is not int or not 1 <= max_projects <= LIMIT
            or type(max_tasks) is not int or not 1 <= max_tasks <= 100):
        raise ContractError("fleet limits must be 1..10 projects and 1..100 tasks")
    manifest, jobs = load_manifest(manifest)
    if not execute:
        return {"status": "DRY_RUN", "approved_projects": len(jobs),
                "selected_projects": min(len(jobs), max_projects), "executed": False}
    runner = runner or subprocess.run
    root = _runtime(manifest)
    results = []
    # Global fleet lock AND independent per-project Factory locks.
    with single_worker_lock(root):
        for index, job in enumerate(jobs[:max_projects], start=1):
            if (root / "STOP.REQUESTED").exists():
                results.append({"project": index, "status": "STOP_REQUESTED"})
                break
            # Recheck config/plan bytes before every independent project.
            check = _setting(Path(job["settings"]))
            if check["settings_sha256"] != job["settings_sha256"]:
                results.append({"project": index, "status": "CONFIG_CHANGED_HOLD"})
                break
            argv = [sys.executable, "-m", "scripts.run_configured_queue",
                    "--settings", job["settings"],
                    "--max-tasks", str(max_tasks), "--execute"]
            try:
                outcome = runner(argv, cwd=ROOT, check=False, shell=False)
                code = outcome.returncode
                state = "COMPLETE_OR_IDLE" if code == 0 else (
                    "TASK_HOLD" if code == 2 else "ERROR")
            except (OSError, subprocess.TimeoutExpired):
                code, state = 124, "PROCESS_ERROR"
            results.append({"project": index, "status": state, "exit_code": code})
            # This stream is outside all target repositories; no source/code text.
            record = {"utc": datetime.now(timezone.utc).isoformat(),
                      "project": index, "status": state, "exit_code": code}
            with (root / "fleet-events.jsonl").open("a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        # A failed project does not skip independent approved projects;
        # only changing approved settings or global stop ends the fleet.
    return {"status": "FINISHED_WITH_HOLDS" if any(
                x["status"] in ("TASK_HOLD", "ERROR", "PROCESS_ERROR", "CONFIG_CHANGED_HOLD")
                for x in results) else "DONE_OR_STOPPED",
            "projects": results, "executed": True,
            "remote_publication": False}


def fleet_status(manifest: Path) -> dict:
    manifest, jobs = load_manifest(manifest)
    root = _runtime(manifest)
    return {"stop_requested": (root / "STOP.REQUESTED").exists(),
            "projects": [{"index": i, "status": control("status", Path(j["settings"]))}
                         for i, j in enumerate(jobs, start=1)],
            "executed": False}


def main(argv=None):
    p = argparse.ArgumentParser(description="Owner-managed local AXDEV project fleet")
    sub = p.add_subparsers(dest="command", required=True)
    create = sub.add_parser("configure")
    create.add_argument("--settings", type=Path, action="append", required=True)
    create.add_argument("--output", type=Path, default=default_file().with_name("fleet.json"))
    for command in ("run", "status", "stop", "resume"):
        parser = sub.add_parser(command)
        parser.add_argument("--manifest", type=Path,
                            default=default_file().with_name("fleet.json"))
        if command == "run":
            parser.add_argument("--execute", action="store_true")
            parser.add_argument("--confirm-reviewed", action="store_true")
            parser.add_argument("--max-projects", type=int, default=10)
            parser.add_argument("--max-tasks", type=int, default=100)
        if command == "resume":
            parser.add_argument("--confirm", action="store_true")
    args = p.parse_args(argv)
    if args.command == "configure":
        result = create_manifest(args.settings, args.output)
    elif args.command == "run":
        result = fleet_run(args.manifest, args.execute, args.confirm_reviewed,
                           args.max_projects, args.max_tasks)
    elif args.command == "status":
        result = fleet_status(args.manifest)
    else:
        result = fleet_signal(args.manifest, args.command,
                              getattr(args, "confirm", False))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not any(x["status"] in ("TASK_HOLD", "ERROR", "PROCESS_ERROR", "CONFIG_CHANGED_HOLD")
                        for x in result.get("projects", [])) else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, TypeError, ContractError) as exc:
        print("AXDEV_FLEET_ERROR:", str(exc), file=sys.stderr)
        raise SystemExit(1)
