"""Run with python -m axdev; no network or edits without --execute."""
import argparse
import json
import shutil
import sys
from pathlib import Path

from . import __version__
from .core import ContractError, Factory, load_plan


def main(argv=None):
    p = argparse.ArgumentParser(prog="axdev")
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="command", required=True)
    doc = sub.add_parser("doctor", help="Inspect local prerequisites (no changes)")
    doc.add_argument("--plan", type=Path)
    run = sub.add_parser("run", help="Execute one or more pre-approved tasks")
    run.add_argument("--repo", type=Path, required=True)
    run.add_argument("--plan", type=Path, required=True)
    run.add_argument("--state", type=Path, required=True)
    run.add_argument("--model", default="ollama/qwen2.5-coder:3b")
    run.add_argument("--max-tasks", type=int, default=1)
    run.add_argument("--execute", action="store_true",
                     help="Opt in to local model tool execution and code writes")
    sync = sub.add_parser("sync-plan", help="Read-only import of SHA-pinned public GitHub task JSON")
    sync.add_argument("--source", required=True)
    sync.add_argument("--branch", required=True)
    sync.add_argument("--path", required=True)
    sync.add_argument("--expected-sha", required=True)
    sync.add_argument("--output", required=True, type=Path)
    a = p.parse_args(argv)
    if a.command == "doctor":
        result = {"python": sys.version.split()[0],
                  "git": bool(shutil.which("git")),
                  "opencode": bool(shutil.which("opencode")),
                  "ollama": bool(shutil.which("ollama")),
                  "model_verified": False,
                  "gpu_verified": False}
        if a.plan:
            result["task_count"] = len(load_plan(a.plan))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    if a.command == "sync-plan":
        from .github_sync import sync_public_plan
        value = sync_public_plan(a.source, a.branch, a.path, a.expected_sha, a.output)
        print(json.dumps(value, ensure_ascii=False, indent=2))
        return 0
    f = None
    try:
        f = Factory(a.repo, a.plan, a.state, model=a.model)
        result = f.run_many(a.max_tasks, a.execute)
        print(json.dumps({"results": result, "states": f.status()},
                         ensure_ascii=False, indent=2))
        return 0 if all(x["status"] not in ("HOLD",) for x in result) else 2
    finally:
        if f:
            f.close()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ContractError, OSError, ValueError, RuntimeError) as err:
        print(f"AXDEV_ERROR: {err}", file=sys.stderr)
        sys.exit(1)
