"""Execute up to 100 owner-approved tasks from private local settings."""
from __future__ import annotations
import argparse
import json
import hashlib
from urllib.error import HTTPError, URLError
from pathlib import Path

from scripts.configure_queue import default_file
from axdev.core import ContractError, Factory
from axdev.github_sync import sync_public_plan

def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--settings", type=Path, default=default_file())
    p.add_argument("--execute", action="store_true")
    p.add_argument("--daily-model-call-budget", type=int,
                   help="optional UTC daily local model invocation cap")
    p.add_argument("--eai-policy", type=Path,
                   help="opt-in owner-private pinned EAI receipt policy")
    p.add_argument("--semantic-review", action="store_true",
                   help="require local Ollama semantic check after deterministic acceptance")
    p.add_argument("--implementation-batch", action="store_true",
                   help="stage independent jobs, then independently review each before promotion")
    p.add_argument("--max-tasks", type=int, help="cap this invocation without raising approved settings limit")
    a = p.parse_args(argv)
    obj = json.loads(a.settings.read_text(encoding="utf-8"))
    if obj.get("version") != 1:
        raise ContractError("unsupported settings version")
    maximum = int(obj.get("max_tasks", 1))
    if not 1 <= maximum <= 100:
        raise ContractError("invalid max tasks")
    if a.max_tasks is not None:
        if not 1 <= a.max_tasks <= 100:
            raise ContractError("requested max tasks outside 1..100")
        maximum = min(maximum, a.max_tasks)
    budgets = [value for value in (obj.get("daily_model_call_budget"), a.daily_model_call_budget)
               if value is not None]
    if any(type(value) is not int or not 1 <= value <= 10000 for value in budgets):
        raise ContractError("daily model-call budget must be 1..10000")
    daily_budget = min(budgets) if budgets else None
    plan_path = Path(obj["plan"])
    approved = obj.get("plan_sha256")
    if approved is not None:
        if (not isinstance(approved, str) or len(approved) != 64
                or hashlib.sha256(plan_path.read_bytes()).hexdigest() != approved):
            raise ContractError("local approved plan SHA256 differs: refusing execution")
    remote = obj.get("github")
    if remote is not None:
        if approved is None or not isinstance(remote, dict):
            raise ContractError("remote queue requires pinned local SHA256 and source")
        try:
            sync_public_plan(remote["source"], remote["branch"], remote["path"],
                             remote["sha"], plan_path)
        except HTTPError as exc:
            remaining = exc.headers.get("X-RateLimit-Remaining") if exc.headers else None
            if exc.code in (403, 429) and remaining == "0":
                # No remote freshness claim; only previously SHA256-approved local bytes.
                print("AXDEV_REMOTE_RATE_LIMIT: using identical SHA256-pinned local plan")
            else:
                raise
        except (URLError, TimeoutError) as exc:
            # Offline operation is safe only with an unchanged, owner-approved cache.
            print("AXDEV_REMOTE_UNREACHABLE: using identical SHA256-pinned local plan")
        if hashlib.sha256(plan_path.read_bytes()).hexdigest() != approved:
            raise ContractError("remote plan differs from approved local SHA256")
    if a.execute:
        sandbox = obj.get("sandbox")
        if not isinstance(sandbox, dict) or set(sandbox) != {"bundle", "manifest_sha256"}:
            raise ContractError("configure the approved offline Sandbox bundle before starting tasks")
        from axdev.windows_sandbox_runtime import run_sandbox_queue
        from scripts.run_sandbox_queue import report
        results, states = run_sandbox_queue(
            Path(obj["repo"]), plan_path, Path(obj["state"]), Path(sandbox["bundle"]),
            sandbox["manifest_sha256"], obj["model"], maximum, True,
            plan_sha256=approved, daily_budget=daily_budget,
            eai_policy=a.eai_policy, semantic_review=a.semantic_review,
            implementation_batch=a.implementation_batch)
        return report(results, states)
    factory = Factory(Path(obj["repo"]), plan_path, Path(obj["state"]),
                      model=obj["model"], semantic_review=a.semantic_review,
                      max_daily_model_calls=daily_budget,
                      eai_policy=a.eai_policy)
    try:
        results = (factory.run_implementation_batch(maximum, execute=a.execute)
                   if a.implementation_batch else factory.run_many(maximum, execute=a.execute))
        print(json.dumps({"results": results, "states": factory.status()},
                         ensure_ascii=False, indent=2))
        if any(x["status"] == "HOLD" for x in results):
            return 2
        if any(x["status"] == "BUDGET_WAIT" for x in results):
            return 3
        if a.implementation_batch and any(
                s in ("CODING", "IMPLEMENTED", "REVIEW", "PREPARED")
                for s in factory.status().values()):
            return 3  # Pending review is not successful completion.
        return 0
    finally:
        factory.close()

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, ContractError) as exc:
        print("AXDEV_ERROR:", str(exc))
        raise SystemExit(1)
