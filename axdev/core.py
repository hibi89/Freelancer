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
import time
from datetime import datetime, timezone
import sys
from pathlib import Path

ID = re.compile(r"^[A-Z][A-Z0-9_-]{2,39}$")
ALLOWED_CHECKS = {
    ("python", "-m", "unittest", "discover", "-s", "tests", "-q"),
    ("python", "-m", "compileall", "-q", "src"),
    ("python", "-m", "compileall", "-q", "axdev"),
    ("ruff", "check", "--no-cache", "src"),
    ("ruff", "check", "--no-cache", "."),
    ("ruff", "check", "--no-cache", "axdev"),
}
VALID_STATES = {"QUEUED", "CODING", "IMPLEMENTED", "REVIEW", "PREPARED", "VERIFIED", "HOLD"}

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

_WINDOWS_RESERVED = frozenset(
    {"CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$"} |
    {f"{prefix}{suffix}" for prefix in ("COM", "LPT")
     for suffix in "123456789¹²³"}
)

def safe_path(value: str) -> str:
    if not isinstance(value, str):
        raise ContractError("file path must be text")
    p = Path(value)
    segments = value.split("/")
    if (not value or p.is_absolute() or "\\" in value
            or any(s in ("", ".", "..") for s in segments)
            or any(segment.lower().startswith((".git", ".axdev", ".github",
                                                    ".opencode", ".env"))
                   for segment in segments)
            # Windows disallows these characters and aliasing names. Reject
            # them even on Linux so the same approved plan remains portable.
            or any(any(ord(ch) < 32 or ch in '<>:"|?*' for ch in s)
                   for s in segments)
            or any(s.endswith((" ", ".")) for s in segments)
            or any(s.split(".")[0].upper() in _WINDOWS_RESERVED
                   for s in segments)):
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
        if len({p.casefold() for p in t["files"]}) != len(t["files"]):
            raise ContractError(f"{tid}: repeated file or Windows case collision")
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

def call(argv: list[str], cwd: Path, timeout: int = 60, env=None,
         output_limit: int = 6000) -> tuple[int, str]:
    try:
        p = subprocess.run(argv, cwd=cwd, text=True, encoding="utf-8",
                           errors="replace", stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, timeout=timeout,
                           shell=False, check=False, env=env)
        return p.returncode, p.stdout[-output_limit:]
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
                 coder=None, semantic_review: bool = False, semantic_reviewer=None):
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
        if type(semantic_review) is not bool:
            raise ContractError("semantic_review must be an explicit boolean")
        self.semantic_review_enabled = semantic_review
        self.semantic_reviewer = semantic_reviewer
        self.state.mkdir(parents=True, exist_ok=True)
        (self.state / "worktrees").mkdir(exist_ok=True)
        self.db = sqlite3.connect(self.state / "factory.sqlite3")
        self.db.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        self.integration_ref = ("refs/heads/axdev/integration-" +
            hashlib.sha256(str(self.state).encode("utf-8")).hexdigest()[:12])
        baseline = self.db.execute("SELECT value FROM meta WHERE key='base_sha'").fetchone()
        actual_head = git(self.repo, "rev-parse", "HEAD")
        ref_rc, ref_output = call(["git", "rev-parse", "--verify", self.integration_ref], self.repo)
        if baseline is None:
            existing = self.db.execute(
                "SELECT COUNT(*) FROM runs WHERE status IN ('VERIFIED','PREPARED')"
            ).fetchone()[0] if self.db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='runs'"
            ).fetchone() else 0
            if existing:
                self.db.close()
                raise ContractError("legacy verified state requires manual integration migration")
            if ref_rc == 0:
                self.db.close()
                raise ContractError("existing integration ref without state: manual inspection required")
            git(self.repo, "update-ref", self.integration_ref, actual_head)
            self.db.execute("INSERT INTO meta (key,value) VALUES ('base_sha',?)", (actual_head,))
        elif ref_rc != 0:
            self.db.close()
            raise ContractError("integration ref is missing: manual recovery required")
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
        # Resume unfinished/implemented work before starting a new model call.
        for eligible in (("CODING", "IMPLEMENTED", "REVIEW", "PREPARED"), ("QUEUED",)):
            for task in self.tasks:
                if (states[task["id"]] in eligible and
                        all(states[d] == "VERIFIED" for d in task.get("depends_on", []))):
                    return task
        return None

    def _workspace(self, tid: str) -> Path:
        target = self.state / "worktrees" / tid
        if not target.exists():
            # Separate worktree; never modify the user's current checkout.
            rc, out = call(["git", "worktree", "add", "-b", f"axdev/{tid}",
                            str(target), self.integration_ref], self.repo, 60)
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
        config_obj = json.loads(config.read_text(encoding="utf-8"))
        allowed = getattr(self, "_active_allowed_files", None)
        if not allowed:
            return 125, "coding task scope absent: refusing model execution"
        # V2 uses last matching rule; only exact task filenames may be written.
        config_obj["model"] = self.model
        config_obj["permissions"] += [
            {"action": "edit", "resource": path, "effect": "allow"}
            for path in allowed
        ]
        env = {key: value for key, value in os.environ.items()
               if not any(secret in key.upper() for secret in
                          ("TOKEN", "API_KEY", "PASSWORD", "SECRET", "CREDENTIAL"))}
        env["OPENCODE_CONFIG"] = str(config)
        env["OPENCODE_CONFIG_CONTENT"] = json.dumps(config_obj)
        env["OPENCODE_AUTO_SHARE"] = "false"
        env["OPENCODE_DISABLE_AUTOUPDATE"] = "true"
        env["OPENCODE_DISABLE_FREE_MODELS"] = "true"
        env["NO_PROXY"] = "127.0.0.1,localhost"
        env["HTTP_PROXY"] = "http://127.0.0.1:9"
        env["HTTPS_PROXY"] = "http://127.0.0.1:9"
        env["ALL_PROXY"] = "http://127.0.0.1:9"
        # OpenCode V2 merges user, project, inline and managed config.
        # The file alone is not evidence that the effective tool policy is safe.
        from .opencode_guard import validate_effective
        rc, merged = call(["opencode", "debug", "config"], cwd,
                          timeout=40, env=env, output_limit=65536)
        if rc != 0 or not validate_effective(merged, config_obj):
            return 125, "effective OpenCode V2 provider/edit/tool policy could not be verified"
        return call(["opencode", "run", "--standalone", "--model", self.model, prompt], cwd,
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

    @staticmethod
    def _git_path_list(workspace: Path, *args: str) -> set[str]:
        """Enumerate full NUL-separated Git paths; never review truncated output.

        Git's ordinary status omits ignored files, so a model or acceptance
        test could write an ignored secret/artifact without being detected.
        A fresh worktree should not contain ignored files. If an interrupted
        worktree does, fail closed rather than silently accepting its contents.
        """
        try:
            proc = subprocess.run(["git", *args], cwd=workspace, check=False,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  timeout=30, shell=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ContractError("Git path inventory unavailable") from exc
        if (proc.returncode != 0 or len(proc.stdout) > 8 * 1024 * 1024
                or (proc.stdout and not proc.stdout.endswith(b"\0"))):
            raise ContractError("Git path inventory failed or exceeded safe limit")
        try:
            names = [part.decode("utf-8")
                     for part in proc.stdout.split(b"\0")[:-1]]
        except UnicodeDecodeError as exc:
            raise ContractError("Git path inventory contains non-UTF8 names") from exc
        if any(not name for name in names):
            raise ContractError("Git path inventory contains an invalid name")
        return set(names)

    def _changed(self, workspace: Path) -> set[str]:
        tracked = self._git_path_list(
            workspace, "diff", "--name-only", "-z", "HEAD", "--")
        untracked = self._git_path_list(
            workspace, "ls-files", "--others", "--exclude-standard", "-z")
        ignored = self._git_path_list(
            workspace, "ls-files", "--others", "--ignored", "--exclude-standard", "-z")
        return tracked | untracked | ignored

    def _preflight_workspace(self, task: dict, workspace: Path) -> None:
        if workspace.is_symlink():
            raise ContractError("worktree path must not be a symlink")
        for filename in task["files"]:
            curr = workspace
            for part in filename.split("/"):
                curr = curr / part
                if curr.is_symlink():
                    raise ContractError("task path contains a symlink")
                if curr.exists() and curr.is_dir() and part == filename.split("/")[-1]:
                    raise ContractError("file target is a directory")

    def _review(self, task: dict, workspace: Path) -> tuple[bool, str]:
        try:
            self._preflight_workspace(task, workspace)
        except ContractError:
            return False, "UNSAFE_TASK_PATH"
        changed = self._changed(workspace)
        if not changed:
            return False, "NO_CHANGES"
        extras = changed - set(task["files"])
        if any((workspace / p).is_symlink() for p in changed):
            return False, "SYMLINK_CHANGES_FORBIDDEN"
        if extras:
            return False, "FORBIDDEN_PATHS: " + ", ".join(sorted(extras))
        # Capture the reviewed bytes before running untrusted project tests.
        # Tests may themselves write files even if their exit code is zero.
        def hashes(paths):
            return {p: (hashlib.sha256((workspace / p).read_bytes()).hexdigest()
                        if (workspace / p).is_file() else None)
                    for p in paths}
        reviewed = hashes(changed)
        # Redirect Python import and compileall bytecode OUTSIDE the worktree.
        # PYTHONDONTWRITEBYTECODE alone does not stop explicit compileall.
        # Never pass ChatGPT/GitHub/API credentials or user profile defaults
        # into project-supplied acceptance tests. This is process-env hygiene,
        # NOT an OS/network sandbox; untrusted code still needs isolation.
        safe_host_keys = ("PATH", "SYSTEMROOT", "WINDIR", "COMSPEC",
                          "PATHEXT", "LANG", "LC_ALL", "LC_CTYPE")
        env = {k: os.environ[k] for k in safe_host_keys if k in os.environ}
        review_home = (self.state / "review-home")
        review_home.mkdir(parents=True, exist_ok=True)
        env["HOME"] = str(review_home)
        env["USERPROFILE"] = str(review_home)
        env["APPDATA"] = str(review_home / "AppData" / "Roaming")
        env["LOCALAPPDATA"] = str(review_home / "AppData" / "Local")
        env["TEMP"] = env["TMP"] = env["TMPDIR"] = str(review_home)
        env["PYTHONPYCACHEPREFIX"] = str(self.state / "review-bytecode")
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONNOUSERSITE"] = "1"
        env["NO_PROXY"] = "127.0.0.1,localhost"
        env["HTTP_PROXY"] = "http://127.0.0.1:9"
        env["HTTPS_PROXY"] = "http://127.0.0.1:9"
        env["ALL_PROXY"] = "http://127.0.0.1:9"
        for command in task["checks"]:
            cmd = ([sys.executable, *command[1:]]
                   if command[0] == "python" else command)
            rc, out = call(cmd, workspace, timeout=240, env=env)
            if rc:
                return False, f"CHECK_FAIL {command}: {out[-1800:]}"
        try:
            self._preflight_workspace(task, workspace)
        except ContractError:
            return False, "POST_CHECK_UNSAFE_TASK_PATH"
        after = self._changed(workspace)
        if after != changed:
            return False, "POST_CHECK_CHANGED_PATHS: " + ", ".join(sorted(after ^ changed))
        if any((workspace / p).is_symlink() for p in after):
            return False, "POST_CHECK_SYMLINK_FORBIDDEN"
        if hashes(after) != reviewed:
            return False, "POST_CHECK_SOURCE_MUTATION"
        if self.semantic_review_enabled:
            # Separate local-only model call AFTER deterministic checks.
            # Semantic results cannot mark an unverified task VERIFIED.
            from .semantic_review import review_semantics
            reviewer = self.semantic_reviewer or review_semantics
            try:
                approved, reason = reviewer(task, workspace, after, self.model)
            except (OSError, ValueError, RuntimeError, TimeoutError) as exc:
                return False, "SEMANTIC_REVIEW_UNAVAILABLE: " + type(exc).__name__
            if not approved:
                return False, "SEMANTIC_HOLD: " + str(reason)[:280]
            try:
                self._preflight_workspace(task, workspace)
                if self._changed(workspace) != after or hashes(after) != reviewed:
                    return False, "POST_SEMANTIC_SOURCE_MUTATION"
            except (OSError, ValueError, RuntimeError):
                return False, "POST_SEMANTIC_UNSAFE_WORKTREE"
        return True, "ALL_CHECKS_PASS"

    def _promote_prepared(self, tid: str) -> dict:
        row = self.db.execute("SELECT commit_sha FROM runs WHERE id=?", (tid,)).fetchone()
        commit = row[0] if row else ""
        if not commit or not re.fullmatch(r"[0-9a-f]{40}", commit):
            raise ContractError("prepared commit SHA missing")
        current = git(self.repo, "rev-parse", self.integration_ref)
        if current != commit:
            parent = git(self.repo, "rev-parse", commit + "^")
            if parent != current:
                raise ContractError("integration advanced or diverged; manual reconciliation required")
            git(self.repo, "update-ref", self.integration_ref, commit, current)
        self._set(tid, "VERIFIED",
                  "DETERMINISTIC_CHECKS_PASS; promoted to isolated local integration ref", commit)
        return {"id": tid, "status": "VERIFIED", "commit": commit,
                "integration_ref": self.integration_ref}

    def run_one(self, execute: bool = False) -> dict:
        task = self.next_task()
        if task is None:
            return {"status": "NO_READY_TASK", "states": self.status()}
        tid = task["id"]
        if not execute:
            return {"id": tid, "status": "DRY_RUN", "goal": task["goal"],
                    "files": task["files"], "checks": task["checks"]}
        try:
            prior = self.status()[tid]
            if prior == "IMPLEMENTED":
                # Batch coding is NOT acceptance; replay only approved file
                # content onto the latest verified integration base.
                from .batch import materialize_review_workspace
                workspace = materialize_review_workspace(self, task)
                self._set(tid, "REVIEW", "batch implementation complete; review pending")
                prior = "REVIEW"
            else:
                review = self.state / "worktrees" / ("batch-review-" + tid)
                workspace = (review if prior in ("REVIEW", "PREPARED") and review.is_dir()
                             else self._workspace(tid))
            self._preflight_workspace(task, workspace)
            if prior == "CODING":
                # A crash during coding may leave partial edits. Inspect once; never
                # rerun an unrestricted model call against an unknown partial state.
                self._set(tid, "REVIEW", "interrupted coding: inspect changes")
                prior = "REVIEW"
            if prior == "PREPARED":
                return self._promote_prepared(tid)
            if prior != "REVIEW":
                self._set(tid, "CODING")
                self._active_allowed_files = tuple(task["files"])
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
                self._active_allowed_files = tuple(task["files"])
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
            self._set(tid, "PREPARED", "accepted tests; awaiting isolated ref promotion", commit)
            result = self._promote_prepared(tid)
            result["workspace"] = str(workspace)
            return result
        except Exception as e:
            self._set(tid, "HOLD", f"EXECUTION_EXCEPTION: {e}")
            return {"id": tid, "status": "HOLD", "reason": str(e)[:500]}

    def run_many(self, maximum: int, execute: bool) -> list[dict]:
        if not 1 <= maximum <= 100:
            raise ContractError("max tasks 1..100")
        results = []
        with single_worker_lock(self.state):
            for _ in range(maximum):
                # A control signal only pauses BETWEEN approved tasks.
                # It cannot terminate an in-flight OpenCode process or alter a commit.
                if (self.state / "STOP.REQUESTED").exists():
                    results.append({"status": "STOP_REQUESTED", "message":
                                    "paused before next task; resume requires explicit action"})
                    break
                began = time.monotonic()
                result = self.run_one(execute)
                results.append(result)
                if execute and result["status"] in ("VERIFIED", "HOLD"):
                    event = {"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                             "task_id": result["id"], "status": result["status"],
                             "duration_seconds": round(time.monotonic() - began, 3)}
                    if result.get("commit"):
                        event["commit"] = result["commit"]
                    # Local-only event stream; task plan, model output and secrets
                    # are deliberately excluded. SQLite remains canonical state.
                    with (self.state / "run-events.jsonl").open("a", encoding="utf-8") as fp:
                        fp.write(json.dumps(event, ensure_ascii=False) + "\n")
                if result["status"] in ("NO_READY_TASK", "DRY_RUN"):
                    break
        return results

    def run_implementation_batch(self, maximum: int, execute: bool) -> list[dict]:
        """Optional code-first / independent-review-later mode."""
        from .batch import run_implementation_batch
        return run_implementation_batch(self, maximum, execute)

    def close(self) -> None:
        self.db.close()
