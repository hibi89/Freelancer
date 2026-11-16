"""Independent read-only integrity gate for AXDEV's disposable first-use trial.

Checks accepted synthetic Git/SQLite evidence, never claims a real AI
provider or OS confinement. No source modifications, network, or Git writes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

from axdev.core import ContractError, load_plan, plan_hash

TASK = "TRIAL-001"
ALLOWED = ["src/hello.py"]
CHECK = ["python", "-m", "unittest", "discover", "-s", "tests", "-q"]
GOAL = ("Create src/hello.py defining greet(name) returning 'Hello, ' + name. "
        "Two pre-existing protected unittest cases must pass. "
        "Do not edit tests or any other file.")
ACCEPTANCE = [
    {"module": "src.hello", "function": "greet", "args": [name],
     "kwargs": {}, "expected": "Hello, " + name}
    for name in ("", "Independent reviewer")
]
PROTECTED_TEST = (
    "import unittest\n"
    "from src.hello import greet\n"
    "class TestHello(unittest.TestCase):\n"
    "    def test_greeting(self):\n"
    "        self.assertEqual(greet('AX'), 'Hello, AX')\n"
    "    def test_empty_name(self):\n"
    "        self.assertEqual(greet(''), 'Hello, ')\n"
)
FIXTURE_README = "# AXDEV disposable trial\nSynthetic only. Do not put secrets here.\n"
FIXTURE_AGENTS = ("# Trial repo\n"
                  "Only implement approved src/hello.py; protected acceptance tests must remain unchanged.\n")
SHA40 = re.compile(r"^[0-9a-f]{40}$")


def _safe(path: Path) -> Path:
    raw = Path(path).expanduser().absolute()
    if raw.is_symlink() or any(parent.is_symlink() for parent in raw.parents):
        raise ContractError("synthetic trial root contains a symlink")
    return raw.resolve()


def _git(repo: Path, *argv: str) -> str:
    result = subprocess.run(["git", "-C", str(repo), *argv], check=False,
                            capture_output=True, text=True, encoding="utf-8",
                            errors="replace", shell=False, timeout=15)
    if result.returncode:
        raise ContractError("synthetic Git validation failed: " + argv[0])
    return result.stdout.strip()


def _read_only_db(state: Path):
    db = state / "factory.sqlite3"
    if db.is_symlink() or any(parent.is_symlink() for parent in db.parents):
        raise ContractError("trial state symlink forbidden")
    if not db.is_file():
        return None
    return sqlite3.connect(db.resolve().as_uri() + "?mode=ro", uri=True)


def verify(trial: Path, phase: str) -> dict:
    if phase not in ("ready", "completed"):
        raise ContractError("unsupported synthetic verification phase")
    root = _safe(trial)
    repo, state, plan = root / "trial-repo", root / "state", root / "trial-plan.json"
    for candidate in (repo, state, plan, repo / ".git",
                      repo / "tests" / "test_hello.py"):
        if candidate.is_symlink():
            raise ContractError("synthetic trial contains a symlink")
    if not (repo / ".git").exists() or not plan.is_file():
        raise ContractError("synthetic fixture missing; run RUN_TRIAL.cmd first")
    tasks = load_plan(plan)
    if (len(tasks) != 1 or tasks[0].get("id") != TASK
            or tasks[0].get("goal") != GOAL
            or tasks[0].get("files") != ALLOWED
            or tasks[0].get("depends_on") != []
            or tasks[0].get("checks") != [CHECK]
            or tasks[0].get("acceptance") != ACCEPTANCE):
        raise ContractError("synthetic trial plan differs from fixed acceptance contract")
    if Path(_git(repo, "rev-parse", "--show-toplevel")).resolve() != repo:
        raise ContractError("synthetic Git root differs from expected fixture")
    if _git(repo, "status", "--porcelain", "--untracked-files=all"):
        raise ContractError("synthetic original checkout is not clean")
    if _git(repo, "ls-files").splitlines() != ["AGENTS.md", "README.md", "tests/test_hello.py"]:
        raise ContractError("synthetic fixture tracked files differ")
    for name, expected in (("AGENTS.md", FIXTURE_AGENTS),
                           ("README.md", FIXTURE_README),
                           ("tests/test_hello.py", PROTECTED_TEST)):
        if (repo / name).read_text(encoding="utf-8") != expected:
            raise ContractError("synthetic protected fixture changed: " + name)
    baseline = _git(repo, "rev-parse", "HEAD")
    if not SHA40.fullmatch(baseline):
        raise ContractError("synthetic baseline SHA missing")
    db = _read_only_db(state)
    row = meta = backend = None
    if db is not None:
        try:
            row = db.execute(
                "SELECT spec, status, attempts, evidence, commit_sha FROM runs WHERE id=?",
                (TASK,)).fetchone()
            all_count = db.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
            meta = db.execute("SELECT value FROM meta WHERE key='base_sha'").fetchone()
            backend = db.execute("SELECT value FROM meta WHERE key='execution_backend'").fetchone()
        finally:
            db.close()
        if all_count != 1 or not row or not meta or meta[0] != baseline:
            raise ContractError("synthetic checkpoint does not match approved fixture")
        if row[0] != plan_hash(tasks[0]):
            raise ContractError("synthetic task SHA changed since approval")
    if phase == "ready":
        if row and row[1] != "QUEUED":
            raise ContractError("synthetic task already started or finished; no new model call")
        return {"phase": phase, "ready": True, "verified": False,
                "model_called_proven": False}
    if row is None or row[1] != "VERIFIED" or row[2] not in (0, 1):
        raise ContractError("synthetic task is not independently VERIFIED")
    commit = row[4]
    if not isinstance(commit, str) or not SHA40.fullmatch(commit):
        raise ContractError("synthetic task verified commit SHA missing")
    integration = ("refs/heads/axdev/integration-" +
                   hashlib.sha256(str(state.resolve()).encode("utf-8")).hexdigest()[:12])
    if backend:
        from axdev.windows_sandbox_runtime import validate_history
        db = _read_only_db(state)
        try:
            validate_history(repo, state, db, tasks, integration, allow_prepared=False)
        finally:
            db.close()
    elif "DETERMINISTIC_CHECKS_PASS" not in row[3]:
        raise ContractError("synthetic acceptance evidence missing")
    if _git(repo, "rev-parse", "--verify", integration) != commit:
        raise ContractError("synthetic integration ref differs from verified commit")
    if _git(repo, "rev-parse", commit + "^") != baseline:
        raise ContractError("synthetic commit is not based on original fixture")
    if _git(repo, "diff", "--name-only", baseline, commit).splitlines() != ALLOWED:
        raise ContractError("synthetic commit contains unexpected changed files")
    if not _git(repo, "show", commit + ":src/hello.py"):
        raise ContractError("synthetic expected source file is empty")
    events = state / "run-events.jsonl"
    if events.is_symlink() or not events.is_file():
        raise ContractError("synthetic VERIFIED event missing")
    matched = False
    with events.open("r", encoding="utf-8") as file:
        for line in file:
            if len(line) > 4096:
                raise ContractError("synthetic event log entry oversized")
            try:
                event = json.loads(line)
            except ValueError as exc:
                raise ContractError("synthetic event log is malformed") from exc
            if (event.get("task_id") == TASK and event.get("status") == "VERIFIED"
                    and event.get("commit") == commit):
                matched = True
    if not matched:
        raise ContractError("synthetic committed success lacks local run event")
    return {"phase": phase, "ready": False, "verified": True,
            "verified_commit": commit, "model_called_proven": False,
            "note": "Synthetic acceptance only; actor/tool policy/OS isolation unverified."}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Strict read-only AXDEV trial acceptance")
    parser.add_argument("--trial", type=Path, default=Path.home() / "AXDEV_TRIAL")
    parser.add_argument("--phase", choices=("ready", "completed"), required=True)
    args = parser.parse_args(argv)
    print(json.dumps(verify(args.trial, args.phase), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, sqlite3.Error, subprocess.TimeoutExpired,
            ContractError) as exc:
        print("AXDEV_TRIAL_VERIFICATION_ERROR:", str(exc), file=sys.stderr)
        raise SystemExit(2)
