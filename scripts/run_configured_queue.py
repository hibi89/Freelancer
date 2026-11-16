"""Execute up to 100 owner-approved tasks from private local settings."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from scripts.configure_queue import default_file
from axdev.core import ContractError, Factory

def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--settings", type=Path, default=default_file())
    p.add_argument("--execute", action="store_true")
    a = p.parse_args(argv)
    obj = json.loads(a.settings.read_text(encoding="utf-8"))
    if obj.get("version") != 1:
        raise ContractError("unsupported settings version")
    maximum = int(obj.get("max_tasks", 1))
    if not 1 <= maximum <= 100:
        raise ContractError("invalid max tasks")
    factory = Factory(Path(obj["repo"]), Path(obj["plan"]), Path(obj["state"]),
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
