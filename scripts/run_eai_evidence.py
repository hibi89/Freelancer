"""Read-only owner-invoked EAI evidence bridge, never auto-run by queue."""
import argparse
import json
from pathlib import Path
from axdev.eai_adapter import run_eai_goal
from axdev.core import ContractError


def main(argv=None):
    p = argparse.ArgumentParser(description="SHA-pinned local EAI evidence adapter")
    p.add_argument("--eai-repo", type=Path, required=True)
    p.add_argument("--expected-sha", required=True)
    p.add_argument("--approved-dir", type=Path, required=True)
    p.add_argument("--goal", type=Path, required=True)
    args = p.parse_args(argv)
    result = run_eai_goal(args.eai_repo, args.expected_sha, args.goal, args.approved_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["independent_receipt_accepted"] else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, ContractError) as exc:
        print("AXDEV_EAI_ADAPTER_ERROR:", type(exc).__name__)
        raise SystemExit(1)
