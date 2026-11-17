"""Private command inbox for the standalone owner desktop app.

Natural-language requests are inert drafts. They become executable only after
the owner supplies exact paths and independent acceptance probes and explicitly
approves an isolated, SHA-pinned task contract. No remote service is used.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import subprocess
import sys
from datetime import datetime, timezone

from axdev.core import ContractError, load_plan, safe_path
from axdev.sandbox_review import validate_acceptance
from scripts.configure_queue import default_file

_TASK = re.compile(r"^CMD-[A-F0-9]{12}$")
_SHA = re.compile(r"^[a-f0-9]{64}$")
_DEFAULT_CHECK = ["python", "-m", "unittest", "discover", "-s", "tests", "-q"]
_MAX_GOAL = 4000


def drafts_home() -> Path:
    return default_file().parent / "desktop-commands"


def _safe_local(path: Path) -> Path:
    path = Path(path).expanduser().absolute()
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ContractError("symbolic/reparse command path not permitted")
    return path


def _private_dir(path: Path) -> Path:
    path = _safe_local(path)
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    return path


def _write_exclusive(path: Path, obj: dict) -> None:
    raw = (json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as file:
        file.write(raw)
        file.flush()
        os.fsync(file.fileno())


def _read_object(path: Path, limit: int = 65536) -> dict:
    path = _safe_local(path)
    if not path.is_file() or path.stat().st_size > limit:
        raise ContractError("missing, unsafe or oversized local command record")
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError) as exc:
        raise ContractError("invalid private command JSON") from exc
    if not isinstance(obj, dict):
        raise ContractError("private command must be a JSON object")
    return obj


def _repo_path(repo: Path) -> Path:
    try:
        repo = _safe_local(repo).resolve(strict=True)
    except OSError as exc:
        raise ContractError("command repository path is missing or inaccessible") from exc
    if not repo.is_dir() or not (repo / ".git").exists():
        raise ContractError("command requires an existing approved local Git checkout")
    return repo


def save_draft(goal: str, repo: Path, *, home: Path | None = None) -> dict:
    if not isinstance(goal, str):
        raise ContractError("command must be text")
    goal = goal.strip()
    if (not 1 <= len(goal) <= _MAX_GOAL or
            any(ord(c) < 32 and c not in "\n\t" for c in goal)):
        raise ContractError("command must contain 1..4000 safe characters")
    repo = _repo_path(repo)
    root = _safe_local(home if home is not None else drafts_home())
    if root == repo or repo in root.parents or root in repo.parents:
        raise ContractError("private drafts must be separate from the source repository")
    _private_dir(root)
    task_id = "CMD-" + secrets.token_hex(6).upper()
    record = {
        "version": 1, "id": task_id, "goal": goal,
        "repo": str(repo), "state": "DRAFT",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "model_called": False, "execution_started": False,
    }
    _write_exclusive(root / (task_id + ".json"), record)
    return record


def recent_drafts(*, home: Path | None = None, limit: int = 20) -> list[dict]:
    root = _safe_local(home if home is not None else drafts_home())
    if not root.is_dir():
        return []
    results = []
    for path in sorted(root.glob("CMD-*.json"), reverse=True)[:max(1, min(limit, 50))]:
        if not _TASK.fullmatch(path.stem):
            continue
        try:
            record = _read_object(path)
            if record.get("id") == path.stem and record.get("state") == "DRAFT":
                results.append(record)
        except (OSError, ContractError):
            continue
    return results


def approve_draft(
    draft_id: str, allowed_files: list[str], acceptance: list[dict],
    *, source_settings: Path | None = None, home: Path | None = None,
    checks: list[list[str]] | None = None,
) -> dict:
    """Owner's explicit approval: create separate SHA-pinned plan/settings.

    Does not launch a model or modify the existing settings/approved queue.
    The private owner also must separately approve execution in the UI.
    """
    if not isinstance(draft_id, str) or not _TASK.fullmatch(draft_id):
        raise ContractError("invalid draft task ID")
    root = _private_dir(home if home is not None else drafts_home())
    draft = _read_object(root / (draft_id + ".json"))
    if draft.get("id") != draft_id or draft.get("state") != "DRAFT":
        raise ContractError("draft approval state mismatch")
    repo = _repo_path(Path(draft["repo"]))
    if (not isinstance(allowed_files, list) or not 1 <= len(allowed_files) <= 16
            or any(not isinstance(x, str) for x in allowed_files)):
        raise ContractError("owner must specify 1..16 exact allowed files")
    paths = [safe_path(p) for p in allowed_files]
    if len({p.casefold() for p in paths}) != len(paths):
        raise ContractError("duplicate Windows file paths")
    validate_acceptance(acceptance)
    if checks is None:
        checks = [_DEFAULT_CHECK.copy()]
    task = {
        "id": draft_id, "goal": draft["goal"], "files": paths,
        "depends_on": [], "checks": checks, "acceptance": acceptance,
    }
    plan = {"version": 1, "tasks": [task]}
    source = _read_object(source_settings if source_settings else default_file())
    if source.get("version") != 1 or _repo_path(Path(source["repo"])) != repo:
        raise ContractError("approved source queue must refer to this exact repository")
    sandbox = source.get("sandbox")
    if (not isinstance(sandbox, dict) or set(sandbox) != {"bundle", "manifest_sha256"}
            or not isinstance(sandbox["bundle"], str)
            or not isinstance(sandbox["manifest_sha256"], str)
            or not _SHA.fullmatch(sandbox["manifest_sha256"])):
        raise ContractError("an owner-pinned offline Windows Sandbox bundle is required")
    model = source.get("model", "")
    if not isinstance(model, str) or not re.fullmatch(r"ollama/[A-Za-z0-9_.:/-]{2,100}", model):
        raise ContractError("approved offline model must use Ollama")
    # Validate the task with the engine parser before writing anything durable.
    from tempfile import TemporaryDirectory
    with TemporaryDirectory(prefix="axdev-contract-") as tmp:
        test_file = Path(tmp) / "plan.json"
        test_file.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
        load_plan(test_file)
    run_root = _safe_local(root / ("run-" + draft_id))
    run_root.mkdir(mode=0o700, exist_ok=False)
    plan_path, settings_path = run_root / "plan.json", run_root / "settings.json"
    try:
        _write_exclusive(plan_path, plan)
        digest = hashlib.sha256(plan_path.read_bytes()).hexdigest()
        settings = {
            "version": 1, "repo": str(repo), "plan": str(plan_path),
            "state": str(run_root / "state"), "model": model,
            "max_tasks": 1, "plan_sha256": digest,
            "sandbox": sandbox,
        }
        if "daily_model_call_budget" in source:
            settings["daily_model_call_budget"] = source["daily_model_call_budget"]
        _write_exclusive(settings_path, settings)
    except BaseException:
        # Do not modify or overwrite owner source settings on partial failure.
        for path in (plan_path, settings_path):
            path.unlink(missing_ok=True)
        run_root.rmdir()
        raise
    return {
        "id": draft_id, "settings": str(settings_path),
        "plan_sha256": digest, "approved": True,
        "execution_started": False, "model_called": False,
    }


def inspect_approval(settings: Path) -> dict:
    settings = _safe_local(settings)
    obj = _read_object(settings)
    if obj.get("version") != 1 or obj.get("max_tasks") != 1:
        raise ContractError("desktop requires a one-task approved settings file")
    plan = _safe_local(Path(obj["plan"]))
    if not plan.is_file() or hashlib.sha256(plan.read_bytes()).hexdigest() != obj.get("plan_sha256"):
        raise ContractError("approved task contract SHA256 changed")
    tasks = load_plan(plan)
    if len(tasks) != 1 or not _TASK.fullmatch(tasks[0]["id"]):
        raise ContractError("desktop approved task identifier differs")
    if _repo_path(Path(obj["repo"])) == plan.parent or plan.parent in _repo_path(Path(obj["repo"])).parents:
        raise ContractError("plan must remain outside the source repository")
    sandbox = obj.get("sandbox")
    if (not isinstance(sandbox, dict)
            or not _SHA.fullmatch(str(sandbox.get("manifest_sha256", "")))):
        raise ContractError("approved Sandbox is missing")
    return {"id": tasks[0]["id"], "goal": tasks[0]["goal"],
            "files": tasks[0]["files"], "checks": tasks[0]["checks"],
            "probe_count": len(tasks[0].get("acceptance", [])),
            "model": obj["model"], "settings": str(settings),
            "plan_sha256": obj["plan_sha256"]}


def launch_approved(settings: Path, *, app_root: Path, frozen: bool = False):
    """Explicit click only. OS process lock/approval remains in the core runtime."""
    proof = inspect_approval(settings)
    cfg = _safe_local(Path(proof["settings"]))
    cmd = ([sys.executable, "--axdev-worker"] if frozen
           else [sys.executable, "-m", "scripts.run_configured_queue"])
    cmd += ["--settings", str(cfg), "--max-tasks", "1", "--execute"]
    log = _safe_local(cfg.with_name("worker.log"))
    out = open(log, "ab", buffering=0)
    try:
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        worker = subprocess.Popen(cmd, cwd=app_root, stdin=subprocess.DEVNULL,
                                  stdout=out, stderr=subprocess.STDOUT,
                                  close_fds=True, creationflags=flags)
    finally:
        out.close()
    return {"pid": worker.pid, "task_id": proof["id"], "log": str(log),
            "execution_started": True, "result": "STARTED_NOT_VERIFIED"}
