"""Run the fixed disposable trial with an owner-pinned offline bundle."""
from __future__ import annotations

import argparse
import os
from pathlib import Path

from axdev.core import ContractError
from axdev.sandbox_payload import hex_sha, no_reparse
from axdev.windows_sandbox_runtime import run_sandbox_queue
from scripts.run_sandbox_queue import report
from scripts.verify_trial import verify


def main():
    parser = argparse.ArgumentParser(description="AXDEV disposable Windows Sandbox trial")
    parser.add_argument("--trial", required=True, type=Path)
    args = parser.parse_args()
    bundle = os.environ.get("AXDEV_OFFLINE_BUNDLE")
    pin = os.environ.get("AXDEV_BUNDLE_SHA256")
    if not bundle or not pin:
        raise ContractError("set AXDEV_OFFLINE_BUNDLE and AXDEV_BUNDLE_SHA256 for the approved runtime")
    root = no_reparse(args.trial)
    verify(root, "ready")
    plan = root / "trial-plan.json"
    results, states = run_sandbox_queue(root / "trial-repo", plan, root / "state", Path(bundle), pin,
                                       os.environ.get("AXDEV_MODEL", "ollama/qwen3:4b-instruct"), 1,
                                       True, plan_sha256=hex_sha(plan))
    status = report(results, states)
    if status == 0:
        verify(root, "completed")
    return status


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, RuntimeError) as exc:
        print("AXDEV_MODEL_TRIAL:", exc)
        raise SystemExit(2)
