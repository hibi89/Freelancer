"""Source-repository trust preflight for AX Dev Factory worktree execution.

Git checkout/status/commit can launch executable hooks and content filters
outside OpenCode's policy. Reject these configurations before staging model
changes. This guard reduces ambient execution risks; it is NOT OS isolation.
"""
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

from .core import ContractError

EXECUTABLE_GIT_CONFIG = re.compile(
    r"^(core\.(hookspath|fsmonitor)|filter\..*\.(clean|smudge|process))$",
    re.IGNORECASE,
)
GIT_ENV_EXEC = {
    "GIT_CONFIG_COUNT", "GIT_CONFIG_PARAMETERS", "GIT_SSH_COMMAND",
    "GIT_EXEC_PATH", "GIT_TEMPLATE_DIR", "GIT_EXTERNAL_DIFF"
}


def _git_read(repo: Path, *argv: str) -> bytes:
    try:
        p = subprocess.run(["git", *argv], cwd=repo, shell=False, check=False,
                           stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, timeout=15)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ContractError("Git trust inspection unavailable") from exc
    if p.returncode or len(p.stdout) > 8 * 1024 * 1024:
        raise ContractError("Git trust inventory failed/oversized")
    return p.stdout


def _under_repo(repo: Path, path: Path) -> bool:
    absolute = path.resolve()
    return absolute == repo or repo in absolute.parents


def assert_safe_git_checkout(repo: Path) -> None:
    repo = repo.expanduser().resolve()
    for name in os.environ:
        upper = name.upper()
        if (upper in GIT_ENV_EXEC or upper.startswith("GIT_CONFIG_KEY_")
                or upper.startswith("GIT_CONFIG_VALUE_")):
            raise ContractError("Git environment may inject executable behavior")
    # Read only keys, never expose credentials or values in tool logs.
    config = _git_read(repo, "config", "--list", "--name-only").decode(
        "utf-8", errors="replace").splitlines()
    for name in config:
        if EXECUTABLE_GIT_CONFIG.fullmatch(name.strip()):
            raise ContractError("Git executable hooks/filters require trusted isolation")

    # Git default hooks are *.sample; a real hook can run at commit/rebase.
    git_root = _git_read(repo, "rev-parse", "--git-path", "hooks").decode(
        "utf-8", errors="strict").strip()
    if not git_root or "\n" in git_root:
        raise ContractError("Git hooks path invalid")
    hooks = Path(git_root)
    if not hooks.is_absolute():
        hooks = repo / hooks
    if hooks.is_symlink():
        raise ContractError("Git hooks directory symlink forbidden")
    if hooks.is_dir():
        entries = list(hooks.iterdir())
        if len(entries) > 256:
            raise ContractError("Git hooks inventory oversized")
        for file in entries:
            if file.is_symlink() or (file.is_file() and not file.name.endswith(".sample")):
                raise ContractError("active Git hook detected")

    # Content filters may be activated by tracked or locally configured
    # .gitattributes even when no executable filter appears in local config.
    all_tracked = _git_read(repo, "ls-files", "-z").split(b"\0")
    if len(all_tracked) > 500001:
        raise ContractError("Git tracked path inventory oversized")
    for raw in all_tracked:
        if not raw:
            continue
        try:
            path = raw.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise ContractError("Git path name cannot be inspected") from exc
        if Path(path).name != ".gitattributes":
            continue
        candidate = repo / path
        if candidate.is_symlink() or not _under_repo(repo, candidate):
            raise ContractError("Git attributes symlink/escape forbidden")
        if candidate.exists():
            if candidate.stat().st_size > 128 * 1024:
                raise ContractError("Git attributes too large")
            for line in candidate.read_text(encoding="utf-8").splitlines():
                clean = line.strip()
                if clean and not clean.startswith("#") and re.search(
                        r"(?:^|\s)filter=\S+", clean, re.IGNORECASE):
                    raise ContractError("Git content filter attribute forbidden")

    # Untracked .git/info/attributes can also activate local filters.
    info = _git_read(repo, "rev-parse", "--git-path", "info/attributes").decode(
        "utf-8", errors="strict").strip()
    local_attr = Path(info)
    if not local_attr.is_absolute():
        local_attr = repo / local_attr
    if local_attr.is_symlink():
        raise ContractError("Git local attributes symlink forbidden")
    if local_attr.is_file():
        if local_attr.stat().st_size > 128 * 1024:
            raise ContractError("Git local attributes too large")
        for line in local_attr.read_text(encoding="utf-8").splitlines():
            clean = line.strip()
            if clean and not clean.startswith("#") and re.search(
                    r"(?:^|\s)filter=\S+", clean, re.IGNORECASE):
                raise ContractError("Git local filter attribute forbidden")
