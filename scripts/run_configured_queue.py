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
    factory = Factory(Path(obj["repo"]), plan_path, Path(obj["state"]),
                      model=obj["model"])
    try:
        results = factory.run_many(maximum, execute=a.execute)
        print(json.dumps({"results": results, "states": factory.status()},
                         ensure_ascii=False, indent=2))
        return 2 if any(x["status"] == "HOLD" for x in results) else 0
    finally:
        factory.close()

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, ContractError) as exc:
        print("AXDEV_ERROR:", str(exc))
        raise SystemExit(1)
