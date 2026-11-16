"""AX Dev Factory: bounded, local-first one-coder/one-reviewer queue."""
from __future__ import annotations

import hashlib
import json
import os
from contextlib import contextmanager
import re
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

ID = re.compile(r"^[A-Z][A-Z0-9_-]{2,39}$")
ALLOWED_CHECKS = {
    ("python", "-m", "unittest", "discover", "-s", "tests", "-q"),
    ("python", "-m", "compileall", "-q", "src"),
    ("python", "-m", "compileall", "-q", "axdev"),
}
VALID_STATES = {"QUEUED", "CODING", "REVIEW", "VERIFIED", "HOLD"}

class ContractError(ValueError):
    pass

@contextmanager
def single_worker_lock(state: Path):
    """Kernel-released file lock; no duplicate model worker after a crash."""
    state.mkdir(parents=True, exist_ok=True)
    file = open(state / "worker.lock", "a+b")
    try:
        file.seek(0)
        file.write(b"0")
        file.flush()
        if os.name == "nt":
            import msvcrt
            file.seek(0)
            msvcrt.locking(file.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            yield
        finally:
            if os.name == "nt":
                file.seek(0)
                msvcrt.locking(file.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(file.fileno(), fcntl.LOCK_UN)
    except OSError as e:
        raise ContractError("another AXDEV worker is already active") from e
    finally:
        file.close()

def safe_path(value: str) -> str:
    p = Path(value)
    if (not value or p.is_absolute() or "\\" in value or ":" in value
            or any(s in ("", ".", "..") for s in value.split("/"))
            or value.startswith(".git") or value.startswith(".axdev")):
        raise ContractError(f"unsafe path: {value!r}")
    return value

def load_plan(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("version") != 1 or not isinstance(data.get("tasks"), list):
        raise ContractError("plan must be version 1 with tasks")
    if len(data["tasks"]) > 100:
        raise ContractError("at most 100 tasks")
    seen = set()
    for t in data["tasks"]:
        tid = t.get("id")
        if not isinstance(tid, str) or not ID.fullmatch(tid) or tid in seen:
            raise ContractError("invalid or duplicate task id")
        seen.add(tid)
        if not isinstance(t.get("goal"), str) or not 1 <= len(t["goal"]) <= 4000:
            raise ContractError(f"{tid}: goal must be 1..4000 characters")
        if not isinstance(t.get("files"), list) or not 1 <= len(t["files"]) <= 16:
            raise ContractError(f"{tid}: files must contain 1..16 paths")
        for p in t["files"]:
            if not isinstance(p, str):
                raise ContractError("file path must be text")
            safe_path(p)
        if len(set(t["files"])) != len(t["files"]):
            raise ContractError(f"{tid}: repeated file")
        deps = t.get("depends_on", [])
        if not isinstance(deps, list) or len(deps) != len(set(deps)):
            raise ContractError(f"{tid}: invalid dependencies")
        checks = t.get("checks")
        if (not isinstance(checks, list) or not checks or
                any(not isinstance(c, list) or tuple(c) not in ALLOWED_CHECKS for c in checks)):
            raise ContractError(f"{tid}: unsupported check command")
    tasks = {t["id"]: t for t in data["tasks"]}
    def visit(k, active, done):
        if k in active:
            raise ContractError("dependency cycle")
        if k in done:
            return
        active.add(k)
        for dep in tasks[k].get("depends_on", []):
            if dep not in tasks:
                raise ContractError(f"unknown dependency {dep}")
            visit(dep, active, done)
        active.remove(k)
        done.add(k)
    done = set()
    for tid in tasks:
        visit(tid, set(), done)
    return data["tasks"]

def call(argv: list[str], cwd: Path, timeout: int = 60, env=None) -> tuple[int, str]:
    try:
        p = subprocess.run(argv, cwd=cwd, text=True, encoding="utf-8",
                           errors="replace", stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, timeout=timeout,
                           shell=False, check=False, env=env)
        return p.returncode, p.stdout[-6000:]
    except (OSError, subprocess.TimeoutExpired) as e:
        return 124, str(e)

def git(cwd: Path, *args: str) -> str:
    rc, out = call(["git", *args], cwd)
    if rc != 0:
        raise RuntimeError(f"git {' '.join(args)}: {out}")
    return out.strip()

def plan_hash(task: dict) -> str:
    return hashlib.sha256(json.dumps(task, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

class Factory:
    def __init__(self, repo: Path, plan: Path, state: Path, model: str = "ollama/qwen2.5-coder:3b",
                 coder=None):
        self.repo, self.state = repo.resolve(), state.resolve()
        if self.state == self.repo or self.repo in self.state.parents:
            raise ContractError("state directory must be outside target repository")
        if not model.startswith("ollama/"):
            raise ContractError("only explicitly selected local Ollama provider is permitted")
        if git(self.repo, "rev-parse", "--is-inside-work-tree") != "true":
            raise ContractError("target must be a git repository")
        self.tasks = load_plan(plan)
        self.model = model
        self.coder = coder or self._opencode
        self.state.mkdir(parents=True, exist_ok=True)
        (self.state / "worktrees").mkdir(exist_ok=True)
        self.db = sqlite3.connect(self.state / "factory.sqlite3")
        self.db.execute("CREATE TABLE IF NOT EXISTS runs "
                        "(id TEXT PRIMARY KEY, spec TEXT NOT NULL, status TEXT NOT NULL, "
                        "attempts INTEGER NOT NULL DEFAULT 0, evidence TEXT NOT NULL DEFAULT '', "
                        "commit_sha TEXT NOT NULL DEFAULT '')")
        for task in self.tasks:
            row = self.db.execute("SELECT spec FROM runs WHERE id=?", (task["id"],)).fetchone()
            digest = plan_hash(task)
            if row and row[0] != digest:
                self.db.close()
                raise ContractError(f"{task['id']} contract changed: manual reconciliation required")
            if not row:
                self.db.execute("INSERT INTO runs (id,spec,status) VALUES (?,?,?)",
                                (task["id"], digest, "QUEUED"))
        self.db.commit()

    def status(self) -> dict[str, str]:
        return dict(self.db.execute("SELECT id,status FROM runs").fetchall())

    def _set(self, tid: str, status: str, evidence: str = "", commit: str = "") -> None:
        if status not in VALID_STATES:
            raise ContractError("invalid state")
        self.db.execute("UPDATE runs SET status=?, evidence=?, commit_sha=? WHERE id=?",
                        (status, evidence[-3000:], commit, tid))
        self.db.commit()

    def next_task(self) -> dict | None:
        states = self.status()
        for t in self.tasks:
            if states[t["id"]] in ("QUEUED", "CODING", "REVIEW"):
                if all(states[d] == "VERIFIED" for d in t.get("depends_on", [])):
                    return t
        return None

    def _workspace(self, tid: str) -> Path:
        target = self.state / "worktrees" / tid
        if not target.exists():
            # Separate worktree; never modify the user's current checkout.
            rc, out = call(["git", "worktree", "add", "-b", f"axdev/{tid}",
                            str(target), "HEAD"], self.repo, 60)
            if rc != 0:
                raise RuntimeError(f"cannot create worktree: {out}")
        if Path(git(target, "rev-parse", "--show-toplevel")).resolve() != target.resolve():
            raise RuntimeError("unexpected worktree root")
        return target

    def _opencode(self, cwd: Path, prompt: str) -> tuple[int, str]:
        if shutil.which("opencode") is None:
            return 127, "opencode executable not found"
        config = (Path(__file__).resolve().parent.parent /
                  "config" / "opencode-local-only.json")
        if not config.is_file():
            return 125, "missing local-only OpenCode policy"
        env = os.environ.copy()
        env["OPENCODE_CONFIG"] = str(config)
        # Inline policy may have stronger precedence in some OpenCode releases.
        env["OPENCODE_CONFIG_CONTENT"] = config.read_text(encoding="utf-8")
        return call(["opencode", "run", "--model", self.model, prompt], cwd,
                    timeout=1200, env=env)

    def _prompt(self, task: dict, phase: str, feedback: str = "") -> str:
        paths = ", ".join(task["files"])
        skill = (Path(__file__).resolve().parent.parent /
                 ".opencode" / "skills" / "ax-coding" / "SKILL.md")
        rules = skill.read_text(encoding="utf-8") if skill.is_file() else ""
        return (f"AX Dev Factory {phase} for {task['id']}. Only modify these exact files: {paths}. "
                "Do not change credentials, permissions, network settings, dependencies, "
                "project requirements, git branches, or deployment. No remote AI provider. "
                "Do not commit or push. Follow project AGENTS.md and this coding skill. "
                f"Acceptance requirement: {task['goal']}\n"
                f"Prior review feedback: {feedback[-2200:]}\n"
                f"CODING SKILL RULES:\n{rules[:2400]}\n"
                "Implement the smallest compatible change; retain existing behavior.")

    def _changed(self, workspace: Path) -> set[str]:
        tracked = git(workspace, "diff", "--name-only", "HEAD", "--").splitlines()
        untracked = git(workspace, "ls-files", "--others", "--exclude-standard").splitlines()
        return set(tracked + untracked)

    def _review(self, task: dict, workspace: Path) -> tuple[bool, str]:
        changed = self._changed(workspace)
        if not changed:
            return False, "NO_CHANGES"
        extras = changed - set(task["files"])
        if any((workspace / p).is_symlink() for p in changed):
            return False, "SYMLINK_CHANGES_FORBIDDEN"
        if extras:
            return False, "FORBIDDEN_PATHS: " + ", ".join(sorted(extras))
        for command in task["checks"]:
            rc, out = call([sys.executable, *command[1:]], workspace, timeout=240)
            if rc:
                return False, f"CHECK_FAIL {command}: {out[-1800:]}"
        return True, "ALL_CHECKS_PASS"

    def run_one(self, execute: bool = False) -> dict:
        task = self.next_task()
        if task is None:
            return {"status": "NO_READY_TASK", "states": self.status()}
        tid = task["id"]
        if not execute:
            return {"id": tid, "status": "DRY_RUN", "goal": task["goal"],
                    "files": task["files"], "checks": task["checks"]}
        try:
            workspace = self._workspace(tid)
            prior = self.status()[tid]
            if prior != "REVIEW":
                self._set(tid, "CODING")
                rc, output = self.coder(workspace, self._prompt(task, "CODING"))
                if rc:
                    self._set(tid, "HOLD", f"MODEL_FAILURE {rc}: {output}")
                    return {"id": tid, "status": "HOLD", "reason": "MODEL_FAILURE"}
                self._set(tid, "REVIEW")
            ok, feedback = self._review(task, workspace)
            if not ok:
                used = self.db.execute("SELECT attempts FROM runs WHERE id=?", (tid,)).fetchone()[0]
                if used >= 1:
                    self._set(tid, "HOLD", feedback)
                    return {"id": tid, "status": "HOLD", "reason": feedback[-500:]}
                self.db.execute("UPDATE runs SET attempts=attempts+1 WHERE id=?", (tid,))
                self.db.commit()
                rc, output = self.coder(workspace, self._prompt(task, "FIX_ONCE", feedback))
                if rc:
                    self._set(tid, "HOLD", f"FIX_MODEL_FAILURE: {output}")
                    return {"id": tid, "status": "HOLD", "reason": "FIX_MODEL_FAILURE"}
                ok, feedback = self._review(task, workspace)
            if not ok:
                self._set(tid, "HOLD", feedback)
                return {"id": tid, "status": "HOLD", "reason": feedback[-500:]}
            changed = sorted(self._changed(workspace))
            git(workspace, "add", "--", *changed)
            git(workspace, "commit", "-m", f"axdev: {tid} reviewed local change")
            commit = git(workspace, "rev-parse", "HEAD")
            self._set(tid, "VERIFIED", "DETERMINISTIC_CHECKS_PASS (not buyer acceptance)", commit)
            return {"id": tid, "status": "VERIFIED", "commit": commit,
                    "workspace": str(workspace)}
        except Exception as e:
            self._set(tid, "HOLD", f"EXECUTION_EXCEPTION: {e}")
            return {"id": tid, "status": "HOLD", "reason": str(e)[:500]}

    def run_many(self, maximum: int, execute: bool) -> list[dict]:
        if not 1 <= maximum <= 100:
            raise ContractError("max tasks 1..100")
        results = []
        with single_worker_lock(self.state):
            for _ in range(maximum):
                result = self.run_one(execute)
                results.append(result)
                if result["status"] in ("NO_READY_TASK", "DRY_RUN"):
                    break
        return results

    def close(self) -> None:
        self.db.close()
