"""Explicit Windows Sandbox local-only queue entrypoint.

Never installs OS features or binaries. Windows Home/unavailable Sandbox is
a hard blocker; no silent fallback to direct OpenCode execution.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from axdev.core import ContractError, load_plan
from axdev.windows_sandbox_runtime import run_sandbox_queue


def report(results: list[dict], states: dict) -> int:
    print(json.dumps({"results": results, "states": states}, ensure_ascii=False, indent=2))
    if any(item.get("status") == "HOLD" for item in results):
        return 2
    if any(state != "VERIFIED" for state in states.values()):
        return 3
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description="AXDEV isolated Windows Sandbox queue")
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--plan", type=Path, required=True)
    p.add_argument("--plan-sha256", help="SHA256 of the approved local plan bytes")
    p.add_argument("--state", type=Path, required=True)
    p.add_argument("--offline-bundle", type=Path, required=True)
    p.add_argument("--bundle-manifest-sha256", required=True)
    p.add_argument("--model", default="ollama/qwen2.5-coder:3b")
    p.add_argument("--max-tasks", type=int, default=1)
    p.add_argument("--daily-model-call-budget", type=int)
    p.add_argument("--execute", action="store_true")
    p.add_argument("--confirm-isolated-run", action="store_true",
                   help="explicitly launch owner-installed Windows Sandbox")
    args = p.parse_args(argv)
    if args.execute != args.confirm_isolated_run:
        raise ContractError("both --execute and --confirm-isolated-run are required")
    if not 1 <= args.max_tasks <= 100:
        raise ContractError("max tasks must be 1..100")
    if not args.execute:
        tasks = load_plan(args.plan)
        print(json.dumps({
            "status": "DRY_RUN", "task_count": len(tasks),
            "sandbox_required": True, "model_calls_started": 0,
            "windows_sandbox_host_available": "NOT_CHECKED",
            "p2_acceptance": "NOT_RUN", "no_fallback_to_host": True,
        }, ensure_ascii=False, indent=2))
        return 0
    if os.name != "nt":
        raise ContractError("isolated execution requires supported Windows Sandbox host")
    results, states = run_sandbox_queue(
        args.repo, args.plan, args.state, args.offline_bundle,
        args.bundle_manifest_sha256, args.model, args.max_tasks, True,
        plan_sha256=args.plan_sha256, daily_budget=args.daily_model_call_budget)
    return report(results, states)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError, ContractError) as exc:
        # External error text can contain private host paths: show only type.
        print("AXDEV_SANDBOX_ERROR:", type(exc).__name__)
        raise SystemExit(2)
