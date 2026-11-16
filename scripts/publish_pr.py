"""Explicit, guarded draft-PR publisher for locally VERIFIED AXDEV commits.

Default = offline preview. Remote Git push and draft PR require two flags
and already-verified owner/branch/commit identity; never merges or force-pushes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sqlite3
from contextlib import closing
import subprocess
from pathlib import Path

from axdev.core import ContractError, load_plan, plan_hash, safe_path
from axdev.repo_trust import assert_safe_git_checkout
from scripts.configure_queue import default_file

REMOTE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
HEAD = re.compile(r"^axdev/review-[a-z0-9][a-z0-9_-]{2,45}$")
SHA = re.compile(r"^[0-9a-f]{40}$")
BASE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,90}$")


def _git(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", *args], cwd=repo, capture_output=True,
                       text=True, encoding="utf-8", errors="replace",
                       timeout=30, check=False, shell=False)
    if p.returncode:
        raise ContractError("local Git validation failed: " + args[0])
    return p.stdout.strip()


def _safe_origin(origin: str, approved_repo: str) -> bool:
    return origin in (
        "https://github.com/" + approved_repo,
        "https://github.com/" + approved_repo + ".git",
        "git@github.com:" + approved_repo,
        "git@github.com:" + approved_repo + ".git",
    )


def preview(settings_path: Path, approved_repo: str, base: str,
            expected_commit: str, head_branch: str, *, require_sandbox: bool = False) -> dict:
    if not isinstance(approved_repo, str) or not REMOTE.fullmatch(approved_repo):
        raise ContractError("invalid approved GitHub owner/repo")
    if any(p in (".", "..") for p in approved_repo.split("/")):
        raise ContractError("invalid repository components")
    if (not isinstance(base, str) or not BASE.fullmatch(base)
            or ".." in base or "//" in base or base.endswith(("/", ".lock"))):
        raise ContractError("invalid base branch")
    if base.startswith("axdev/") or head_branch == base:
        raise ContractError("protected/review base not allowed")
    if not isinstance(head_branch, str) or not HEAD.fullmatch(head_branch):
        raise ContractError("head must be an explicit axdev/review-* branch")
    if not isinstance(expected_commit, str) or not SHA.fullmatch(expected_commit):
        raise ContractError("explicit reviewed 40-hex commit SHA required")

    settings = settings_path.expanduser().absolute()
    if settings.is_symlink() or not settings.is_file():
        raise ContractError("missing local settings or symlink")
    obj = json.loads(settings.read_text(encoding="utf-8"))
    if obj.get("version") != 1:
        raise ContractError("unsupported queue settings")
    repo = Path(obj["repo"]).expanduser().resolve()
    state = Path(obj["state"]).expanduser().resolve()
    plan = Path(obj["plan"]).expanduser().resolve()
    if not plan.is_file() or not (repo / ".git").exists():
        raise ContractError("missing approved plan or Git checkout")
    digest = hashlib.sha256(plan.read_bytes()).hexdigest()
    if digest != obj.get("plan_sha256"):
        raise ContractError("approved plan SHA256 mismatch")
    tasks = load_plan(plan)
    assert_safe_git_checkout(repo)
    fetch_url = _git(repo, "remote", "get-url", "--all", "origin")
    push_url = _git(repo, "remote", "get-url", "--push", "--all", "origin")
    if not _safe_origin(fetch_url, approved_repo) or not _safe_origin(push_url, approved_repo):
        raise ContractError("origin URL for fetch or push differs from the approved repository")
    if require_sandbox and not push_url.startswith("https://github.com/"):
        raise ContractError("actual publication requires HTTPS with the verified GitHub CLI identity")

    ref = "refs/heads/axdev/integration-" + hashlib.sha256(
        str(state).encode("utf-8")).hexdigest()[:12]
    actual = _git(repo, "rev-parse", "--verify", ref)
    if actual != expected_commit:
        raise ContractError("integration ref moved or does not match reviewed commit")
    with closing(sqlite3.connect((state / "factory.sqlite3").as_uri() + "?mode=ro", uri=True)) as conn:
        baseline = conn.execute("SELECT value FROM meta WHERE key='base_sha'").fetchone()
        saved = dict((id_, (digest_, status)) for id_, digest_, status
                     in conn.execute("SELECT id, spec, status FROM runs"))
        if require_sandbox:
            from axdev.windows_sandbox_runtime import BACKEND, validate_history
            row = conn.execute("SELECT value FROM meta WHERE key='execution_backend'").fetchone()
            policy = json.loads(row[0]) if row else None
            if (not isinstance(policy, list) or len(policy) != 4 or
                    policy[:2] != [BACKEND, digest]):
                raise ContractError("actual publication requires host-reviewed isolated execution evidence")
            validate_history(repo, state, conn, tasks, ref, allow_prepared=False)
    if not baseline or not SHA.fullmatch(baseline[0]):
        raise ContractError("verified integration baseline missing")
    allowed = set()
    verified = []
    for task in tasks:
        stored = saved.get(task["id"])
        if not stored or stored[0] != plan_hash(task):
            raise ContractError("local verified contract changed")
        if stored[1] == "VERIFIED":
            verified.append(task["id"])
            allowed.update(task["files"])
    if not verified:
        raise ContractError("no verified tasks available for PR")
    parents = _git(repo, "rev-list", "--ancestry-path",
                   baseline[0] + ".." + actual).splitlines()
    if not parents:
        raise ContractError("no verified commits after baseline")
    diff = _git(repo, "diff", "--name-status", "--no-renames", "-z", baseline[0], actual)
    fields = diff.split("\0")
    if not fields or fields[-1] != "" or len(fields) % 2 != 1:
        raise ContractError("malformed Git export path inventory")
    files = []
    for status, name in zip(fields[:-1:2], fields[1:-1:2]):
        if status not in ("A", "M"):
            raise ContractError("PR export includes deletion, renaming or unexpected changes")
        filename = safe_path(name)
        if filename not in allowed:
            raise ContractError("PR path outside approved tasks: " + repr(filename) + " not in " + repr(sorted(allowed)))
        files.append(filename)
    if not files:
        raise ContractError("no approved file changes to publish")

    return {"repository": approved_repo, "base_branch": base,
            "head_branch": head_branch, "reviewed_commit": actual,
            "source_baseline": baseline[0], "verified_task_ids": verified,
            "changed_files": sorted(files),
            "remote_write_executed": False, "pr_created": False,
            "identity_verified": False,
            "manual_publication_review_required": True}


def publish_draft(settings_path: Path, inspection: dict) -> dict:
    """Only called after a separately confirmed --publish --confirm-public-export."""
    if not shutil.which("gh"):
        raise ContractError("GitHub CLI gh must be installed and authenticated")
    refreshed = preview(settings_path, inspection["repository"], inspection["base_branch"],
                        inspection["reviewed_commit"], inspection["head_branch"], require_sandbox=True)
    if inspection != refreshed:
        raise ContractError("reviewed publication evidence changed")
    gh = subprocess.run(["gh", "api", "--hostname", "github.com", "user", "--jq", ".login"],
                        capture_output=True, text=True, timeout=15, check=False)
    if gh.returncode or gh.stdout.strip() != inspection["repository"].split("/")[0]:
        raise ContractError("GitHub CLI account does not match approved repository owner")
    repo = Path(json.loads(settings_path.read_text(encoding="utf-8"))["repo"]).resolve()
    head = inspection["head_branch"]
    remote_refs = _git(repo, "ls-remote", "--heads", "origin", "refs/heads/" + head)
    if remote_refs:
        raise ContractError("PR publication head branch already exists; manual reconciliation")
    # Deliberately no --force, no follow-up merge, and no remote delete on partial errors.
    commit = inspection["reviewed_commit"]
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    push = subprocess.run(["git", "-c", "credential.helper=", "-c",
                           "credential.https://github.com.helper=!gh auth git-credential", "push",
                           "origin", commit + ":refs/heads/" + head], cwd=repo, env=env,
                          stdin=subprocess.DEVNULL, capture_output=True, timeout=60, check=False)
    if push.returncode:
        raise ContractError("approved GitHub branch push failed")
    body = ("AX Dev Factory draft. Only locally reviewed Git worktree commits.\n"
            "Manual security/code/identity review is required before merging.\n"
            "Verified task IDs: " + ", ".join(inspection["verified_task_ids"]))
    try:
        pr = subprocess.run(["gh", "pr", "create", "--repo", inspection["repository"],
                             "--base", inspection["base_branch"], "--head", head,
                             "--draft", "--title", "AXDEV reviewed local tasks",
                             "--body", body],
                            cwd=repo, capture_output=True, text=True,
                            timeout=45, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ContractError("branch pushed; PR creation unverified; inspect remote manually") from exc
    if pr.returncode:
        raise ContractError("branch pushed but draft PR failed; do not retry push automatically")
    return dict(inspection, remote_write_executed=True, pr_created=True,
                pr_url=pr.stdout.strip(), identity_verified=True)


def main(argv=None):
    p = argparse.ArgumentParser(description="Preview or explicitly publish verified local draft PR")
    p.add_argument("--settings", type=Path, default=default_file())
    p.add_argument("--approved-repo", required=True)
    p.add_argument("--base", required=True)
    p.add_argument("--expected-commit", required=True)
    p.add_argument("--head", required=True)
    p.add_argument("--publish", action="store_true")
    p.add_argument("--confirm-public-export", action="store_true")
    a = p.parse_args(argv)
    # Both publication flags are required. This tool is never invoked by RUN_QUEUE.
    if a.publish != a.confirm_public_export:
        raise ContractError("publication requires BOTH --publish and --confirm-public-export")
    view = preview(a.settings, a.approved_repo, a.base, a.expected_commit, a.head,
                   require_sandbox=a.publish)
    if a.publish:
        view = publish_draft(a.settings, view)
    print(json.dumps(view, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, sqlite3.Error, ContractError) as exc:
        print("AXDEV_PR_ERROR:", str(exc))
        raise SystemExit(1)
