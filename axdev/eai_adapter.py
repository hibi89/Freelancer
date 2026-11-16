"""Explicit, SHA-pinned EAI local evidence adapter; read-only and offline.

The EAI implementation belongs to hibi89/EAI and is NEVER copied into
AX Dev Factory. No subprocess is launched without the owner's local paths
and exact expected source SHA. Evidence cannot independently verify tasks.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from .core import ContractError, git

SHA40 = re.compile(r"[0-9a-f]{40}\Z")


def _trusted_file(root: Path, file: Path) -> Path:
    root = root.expanduser().absolute()
    file = file.expanduser().absolute()
    if root.is_symlink() or file.is_symlink() or any(p.is_symlink() for p in file.parents):
        raise ContractError("EAI input path contains a symbolic link")
    resolved_root, resolved_file = root.resolve(), file.resolve()
    if resolved_file == resolved_root or resolved_root not in resolved_file.parents:
        raise ContractError("EAI goal outside approved input directory")
    if not resolved_file.is_file() or resolved_file.stat().st_size > 64 * 1024:
        raise ContractError("missing or oversized approved EAI goal")
    return resolved_file


def run_eai_goal(eai_repo: Path, expected_commit: str, goal: Path,
                 approved_directory: Path, timeout: int = 90) -> dict:
    repo = eai_repo.expanduser().absolute()
    if (repo.is_symlink() or any(p.is_symlink() for p in repo.parents)
            or not (repo / "eai" / "__main__.py").is_file()):
        raise ContractError("EAI source checkout unavailable or symlinked")
    if not isinstance(expected_commit, str) or not SHA40.fullmatch(expected_commit):
        raise ContractError("exact EAI commit SHA required")
    if Path(git(repo, "rev-parse", "--show-toplevel")).resolve() != repo.resolve():
        raise ContractError("EAI checkout root differs")
    if git(repo, "rev-parse", "HEAD") != expected_commit:
        raise ContractError("EAI checkout SHA does not match owner's pin")
    if git(repo, "status", "--porcelain", "--untracked-files=all"):
        raise ContractError("EAI code checkout has unreviewed changes")
    goal = _trusted_file(approved_directory, goal)
    sha = hashlib.sha256(goal.read_bytes()).hexdigest()
    safe_keys = ("PATH", "SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT")
    env = {k: os.environ[k] for k in safe_keys if k in os.environ}
    env["PYTHONPATH"] = str(repo.resolve())
    env["PYTHONNOUSERSITE"] = "1"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["HTTP_PROXY"] = env["HTTPS_PROXY"] = env["ALL_PROXY"] = "http://127.0.0.1:9"
    env["NO_PROXY"] = "127.0.0.1,localhost"
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "eai", "solve-goal", str(goal), "--json"],
            cwd=repo, env=env, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=timeout, check=False, shell=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ContractError("EAI local evidence invocation unavailable") from exc
    if len(proc.stdout) > 128 * 1024 or len(proc.stderr) > 8 * 1024:
        raise ContractError("EAI evidence output exceeds configured bounds")
    if hashlib.sha256(goal.read_bytes()).hexdigest() != sha:
        raise ContractError("approved EAI input changed during execution")
    if proc.returncode not in (0, 2, 3):
        raise ContractError("EAI invocation failed (no evidence accepted)")
    try:
        report = json.loads(proc.stdout.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContractError("EAI evidence response is not strict JSON") from exc
    if not isinstance(report, dict) or report.get("status") not in (
            "AGREE", "DECIDED", "CONFLICT", "UNAVAILABLE"):
        raise ContractError("EAI evidence status missing or unsupported")
    accepted = proc.returncode == 0 and report["status"] in ("AGREE", "DECIDED")
    # Only hashes/metadata; no user goal contents or source rows in report.
    return {
        "adapter": "axdev.eai.v1", "eai_sha": expected_commit,
        "goal_sha256": sha,
        "receipt_sha256": hashlib.sha256(proc.stdout).hexdigest(),
        "status": report["status"],
        "exit_code": proc.returncode,
        "independent_receipt_accepted": accepted,
        "task_verification": "NOT_VERIFIED",
    }


def load_eai_policy(path: Path, approved_task_ids: set[str]) -> tuple[dict, str]:
    """Bind owner-private EAI receipt policy to exact approved task IDs.

    No customer goal content is exported to GitHub. Policy SHA is persisted
    with the SQLite queue and cannot be silently dropped on a restart.
    """
    path = path.expanduser().absolute()
    if path.is_symlink() or any(part.is_symlink() for part in path.parents):
        raise ContractError("EAI policy path contains a symlink")
    if not path.is_file() or path.stat().st_size > 64 * 1024:
        raise ContractError("EAI policy missing or too large")
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    try:
        obj = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContractError("EAI policy must be strict UTF-8 JSON") from exc
    if not isinstance(obj, dict) or set(obj) != {"version", "tasks"} or obj["version"] != 1:
        raise ContractError("EAI policy unsupported version or fields")
    tasks = obj["tasks"]
    if not isinstance(tasks, dict) or not tasks or len(tasks) > 100:
        raise ContractError("EAI policy requires 1..100 pinned task mappings")
    if not set(tasks).issubset(approved_task_ids):
        raise ContractError("EAI policy has unapproved task IDs")
    fields = {"eai_repo", "expected_sha", "goal", "approved_directory"}
    for task_id, rule in tasks.items():
        if (not isinstance(rule, dict) or set(rule) != fields
                or any(not isinstance(rule[f], str) or not rule[f]
                       for f in fields)
                or not SHA40.fullmatch(rule["expected_sha"])):
            raise ContractError("EAI rule is incomplete or unpinned for " + task_id)
    return tasks, digest
