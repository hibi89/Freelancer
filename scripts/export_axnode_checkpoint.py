"""Explicit private metadata checkpoint export; not an AXNODE binary."""
import argparse
import json
import sqlite3
from pathlib import Path
from axdev.axnode_adapter import export_checkpoint, verify_checkpoint
from axdev.core import ContractError


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--plan", required=True, type=Path)
    p.add_argument("--database", required=True, type=Path)
    action = p.add_mutually_exclusive_group(required=True)
    action.add_argument("--output", type=Path)
    action.add_argument("--verify", type=Path, help="verify existing export against current SQLite")
    a = p.parse_args(argv)
    result = (verify_checkpoint(a.plan, a.database, a.verify)
              if a.verify else export_checkpoint(a.plan, a.database, a.output))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, sqlite3.Error, ContractError) as exc:
        print("AXDEV_AXNODE_BRIDGE_ERROR:", type(exc).__name__)
        raise SystemExit(1)
