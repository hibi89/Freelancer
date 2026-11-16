"""One-time private local settings; refuse overwrite and never upload settings."""
from __future__ import annotations
import argparse
import json
import hashlib
import os
import re
from pathlib import Path

from axdev.core import load_plan, safe_path
from axdev.github_sync import REPO, BRANCH, SHA

def default_file():
    root = Path(os.environ.get("LOCALAPPDATA") or Path.home() / ".axdev")
    return root / "AXDevFactory" / "settings.json"

def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--plan", type=Path, required=True)
    p.add_argument("--model", default="ollama/qwen3:4b-instruct")
    p.add_argument("--settings", type=Path, default=default_file())
    p.add_argument("--github-source")
    p.add_argument("--github-branch")
    p.add_argument("--github-path")
    p.add_argument("--github-sha")
    p.add_argument("--offline-bundle", type=Path)
    p.add_argument("--bundle-manifest-sha256")
    a = p.parse_args(argv)
    repo, plan = a.repo.resolve(), a.plan.resolve()
    settings = a.settings.expanduser().absolute()
    if (settings.is_symlink()
            or any(parent.is_symlink() for parent in settings.parents)):
        raise SystemExit("settings path must not contain symlinks")
    if not (repo / ".git").exists():
        raise SystemExit("target must be an existing local Git clone")
    if not plan.is_file():
        raise SystemExit("plan must exist locally")
    load_plan(plan)
    remote_values = (a.github_source, a.github_branch, a.github_path, a.github_sha)
    if any(remote_values) and not all(remote_values):
        raise SystemExit("GitHub source, branch, path and approved SHA must be supplied together")
    remote = None
    if all(remote_values):
        if (not REPO.fullmatch(a.github_source)
                or any(part in (".", "..") for part in a.github_source.split("/"))
                or not BRANCH.fullmatch(a.github_branch)
                or ".." in a.github_branch or "//" in a.github_branch
                or a.github_branch.endswith(("/", ".lock"))
                or not SHA.fullmatch(a.github_sha)):
            raise SystemExit("invalid approved GitHub source")
        try:
            safe_path(a.github_path)
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc
        if not a.github_path.endswith(".json"):
            raise SystemExit("GitHub task plan path must end in .json")
        remote = {"source": a.github_source, "branch": a.github_branch,
                  "path": a.github_path, "sha": a.github_sha}
    if not re.fullmatch(r"ollama/[A-Za-z0-9_.:/-]{2,100}", a.model):
        raise SystemExit("only valid local Ollama model IDs are supported")
    if bool(a.offline_bundle) != bool(a.bundle_manifest_sha256):
        raise SystemExit("offline bundle and approved manifest SHA256 must be supplied together")
    if a.offline_bundle and not re.fullmatch(r"[0-9a-f]{64}", a.bundle_manifest_sha256):
        raise SystemExit("offline bundle manifest SHA256 is invalid")
    if settings.exists():
        raise SystemExit("settings exist; refusing overwrite (back up and review manually)")
    state = settings.parent / "state"
    if repo == state or repo in state.parents:
        raise SystemExit("state cannot be inside target repo")
    settings.parent.mkdir(parents=True, exist_ok=True)
    obj = {"version": 1, "repo": str(repo), "plan": str(plan),
           "state": str(state), "model": a.model, "max_tasks": 100}
    obj["plan_sha256"] = hashlib.sha256(plan.read_bytes()).hexdigest()
    if remote:
        obj["github"] = remote
    if a.offline_bundle:
        obj["sandbox"] = {"bundle": str(a.offline_bundle.absolute()),
                          "manifest_sha256": a.bundle_manifest_sha256}
    # Contains only paths, hashes and public source coordinates; never secrets.
    # Atomic, exclusive creation avoids a race after the existence check.
    # The file contains local paths and approval hashes, so restrict modes
    # on platforms that honor O_CREAT permissions. No source repo is touched.
    try:
        fd = os.open(settings, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise SystemExit("settings exist; refusing overwrite") from exc
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            out.write(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")
    except BaseException:
        settings.unlink(missing_ok=True)
        raise
    print("Created private path-only configuration:", settings)
    print("Review its contents; then run RUN_QUEUE.cmd once to execute the queue.")

if __name__ == "__main__":
    main()
