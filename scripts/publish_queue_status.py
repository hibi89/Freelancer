"""Explicit, public-metadata-only queue status/handoff sync via GitHub CLI.

No model execution, no client source upload, no task IDs, no secrets,
no remote actions in preview mode. Publication is never automatic.
"""
from __future__ import annotations

import argparse
import base64
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from axdev.core import ContractError, git
from scripts.daily_status import summary
from scripts.queue_control import _settings

REPO = re.compile(r"^hibi89/[A-Za-z0-9_.-]{1,100}$")
BRANCH = re.compile(r"^[A-Za-z0-9_./-]{1,150}$")
SHA40 = re.compile(r"^[0-9a-f]{40}$")
REMOTE_PATH = "docs/axdev-queue-public-handoff.json"


def build_preview(settings: Path, approved_repo: str, target_branch: str) -> dict:
    if not isinstance(approved_repo, str) or not REPO.fullmatch(approved_repo):
        raise ContractError("approved GitHub repo must be explicit and owned by hibi89")
    if (not isinstance(target_branch, str) or not BRANCH.fullmatch(target_branch)
            or ".." in target_branch or "//" in target_branch
            or target_branch.startswith(("/", "-")) or target_branch.endswith(("/", ".lock"))):
        raise ContractError("invalid approved branch")
    config, state = _settings(settings)
    repo = Path(config["repo"]).expanduser().resolve()
    if not (repo / ".git").exists():
        raise ContractError("local target must be a Git repository")
    original = git(repo, "remote", "get-url", "origin").strip()
    allowed = {"https://github.com/" + approved_repo,
               "https://github.com/" + approved_repo + ".git",
               "git@github.com:" + approved_repo,
               "git@github.com:" + approved_repo + ".git"}
    if original not in allowed:
        raise ContractError("local origin differs from explicitly approved repository")
    original_head = git(repo, "rev-parse", "HEAD")
    if not SHA40.fullmatch(original_head):
        raise ContractError("invalid local code SHA")
    # Local queue's integration ref was initialized separately and may not
    # be uploaded. Public metadata deliberately contains only SHA and counts.
    aggregate = summary(state)
    states = aggregate["counts"]
    payload = {
        "format": "axdev.public-queue-handoff.v1",
        "generated_date_utc": datetime.now(timezone.utc).date().isoformat(),
        "approved_repo": approved_repo,
        "source_head": original_head,
        "task_state_counts": states,
        "reserved_model_calls_today": aggregate["model_calls_today"],
        "official_final_verification": "UNASSESSED",
        "implementation_is_not_verification": True,
        "no_task_ids_or_source_exported": True,
    }
    if any(not isinstance(v, int) or v < 0 for v in states.values()):
        raise ContractError("invalid public checkpoint counts")
    return {"target_repo": approved_repo, "target_branch": target_branch,
            "target_path": REMOTE_PATH, "payload": payload,
            "external_write_executed": False, "owner_approval_required": True}


def publish(preview: dict, expected_remote_blob: str | None = None) -> dict:
    """Only call after an owner explicitly supplied BOTH publication flags."""
    if expected_remote_blob is not None and not SHA40.fullmatch(expected_remote_blob):
        raise ContractError("expected remote blob must be exactly 40 lowercase hex characters")
    if shutil.which("gh") is None:
        raise ContractError("GitHub CLI unavailable; no publishing attempted")
    # Verify actual authenticated identity before any publication. Do not
    # interpolate a shell, construct arbitrary command or print auth tokens.
    try:
        actor = subprocess.run(["gh", "api", "user", "--jq", ".login"],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True, check=False, timeout=15, shell=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ContractError("GitHub identity check failed") from exc
    if actor.returncode or actor.stdout.strip() != "hibi89":
        raise ContractError("GitHub publishing identity must be owner hibi89")
    repo = preview["target_repo"]
    branch = preview["target_branch"]
    path = preview["target_path"]
    if (not REPO.fullmatch(repo) or not BRANCH.fullmatch(branch)
            or path != REMOTE_PATH):
        raise ContractError("unapproved remote publication target")
    content = base64.b64encode(
        (json.dumps(preview["payload"], sort_keys=True, ensure_ascii=False,
                    indent=2) + "\n").encode("utf-8")
    ).decode("ascii")
    cmd = ["gh", "api", "--method", "PUT",
           "/repos/" + repo + "/contents/" + path,
           "--raw-field", "message=docs(axdev): owner-approved local status metadata",
           "--raw-field", "branch=" + branch,
           "--raw-field", "content=" + content]
    if expected_remote_blob:
        cmd.extend(["--raw-field", "sha=" + expected_remote_blob])
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, check=False, timeout=50, shell=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ContractError("remote status publish state unknown; inspect GitHub before retry") from exc
    if result.returncode != 0:
        raise ContractError("GitHub status publication failed; do not blind-retry")
    try:
        response = json.loads(result.stdout)
        commit = response["commit"]["sha"]
    except (ValueError, KeyError, TypeError) as exc:
        raise ContractError("GitHub publication outcome unverified; inspect remote") from exc
    if not SHA40.fullmatch(commit):
        raise ContractError("GitHub publication commit SHA invalid")
    return dict(preview, external_write_executed=True, commit_sha=commit,
                identity_verified=True, owner_approval_required=False)


def main(argv=None):
    p = argparse.ArgumentParser(description="Owner-controlled minimal GitHub queue status sync")
    p.add_argument("--settings", required=True, type=Path)
    p.add_argument("--approved-repo", required=True)
    p.add_argument("--branch", required=True)
    p.add_argument("--publish", action="store_true")
    p.add_argument("--confirm-public-export", action="store_true")
    p.add_argument("--expected-remote-blob", help="exact old GitHub blob SHA; omitted means create-only")
    a = p.parse_args(argv)
    if a.publish != a.confirm_public_export:
        raise ContractError("remote write requires BOTH publication approval flags")
    result = build_preview(a.settings, a.approved_repo, a.branch)
    if a.publish:
        result = publish(result, a.expected_remote_blob)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, ContractError) as exc:
        print("AXDEV_PUBLIC_SYNC_ERROR:", type(exc).__name__)
        raise SystemExit(2)
