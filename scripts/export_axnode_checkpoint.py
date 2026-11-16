"""Explicit private metadata checkpoint export; not an AXNODE binary."""
import argparse
import json
import sqlite3
from pathlib import Path
from axdev.axnode_adapter import export_checkpoint
from axdev.core import ContractError


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--plan", required=True, type=Path)
    p.add_argument("--database", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    a = p.parse_args(argv)
    print(json.dumps(export_checkpoint(a.plan, a.database, a.output),
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, sqlite3.Error, ContractError) as exc:
        print("AXDEV_AXNODE_BRIDGE_ERROR:", type(exc).__name__)
        raise SystemExit(1)
