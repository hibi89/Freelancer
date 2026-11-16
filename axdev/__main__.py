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
    run.add_argument("--daily-model-call-budget", type=int,
                     help="optional durable UTC daily model-invocation cap")
    run.add_argument("--semantic-review", action="store_true",
                     help="require separate local Ollama semantic verdict after deterministic checks")
    run.add_argument("--implementation-batch", action="store_true",
                     help="stage independent tasks, then review before verification")
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
        if a.execute and a.implementation_batch:
            from scripts.preflight import inspect
            health = inspect(a.model, a.repo)
            if not health["ready_for_disposable_model_trial"]:
                raise ContractError("local prerequisites missing; no tasks started: " +
                                    ", ".join(health["blockers"]))
        f = Factory(a.repo, a.plan, a.state, model=a.model,
                    semantic_review=a.semantic_review,
                    max_daily_model_calls=a.daily_model_call_budget)
        result = (f.run_implementation_batch(a.max_tasks, a.execute)
                  if a.implementation_batch else f.run_many(a.max_tasks, a.execute))
        print(json.dumps({"results": result, "states": f.status()},
                         ensure_ascii=False, indent=2))
        if any(x["status"] == "HOLD" for x in result):
            return 2
        if any(x["status"] == "BUDGET_WAIT" for x in result):
            return 3
        if a.implementation_batch and any(
                s in ("CODING", "IMPLEMENTED", "REVIEW", "PREPARED")
                for s in f.status().values()):
            return 3  # Some code is implemented but not independently verified.
        return 0
    finally:
        if f:
            f.close()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ContractError, OSError, ValueError, RuntimeError) as err:
        print(f"AXDEV_ERROR: {err}", file=sys.stderr)
        sys.exit(1)
