"""One-at-a-time fixed-synthetic 3B vs 4B local Ollama comparison.

No model downloads, external APIs, customer code, unattended startup, or
remote export. Only explicitly requested --execute invokes local inference.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from axdev.core import ContractError
from scripts.benchmark_local import MODEL, benchmark

DEFAULTS = ("ollama/qwen2.5-coder:3b", "ollama/qwen3:4b-instruct")


def compare_models(models: tuple[str, str] = DEFAULTS, execute: bool = False,
                   runner=benchmark) -> dict:
    if (len(models) != 2 or models[0] == models[1] or
            any(not isinstance(m, str) or not MODEL.fullmatch(m) for m in models)):
        raise ContractError("two distinct local Ollama model IDs required")
    rows = [runner(m, execute=execute) for m in models]
    complete = execute and all(r.get("status") == "LOCAL_INFERENCE_COMPLETE"
                               for r in rows)
    best = None
    if complete:
        ratios = [r.get("eval_tokens_per_second") for r in rows]
        if all(isinstance(v, (float, int)) and v > 0 for v in ratios):
            best = models[0] if ratios[0] >= ratios[1] else models[1]
    return {"version": 1, "models": list(models),
            "local_only": True, "sequential": True,
            "completed": bool(complete), "best_throughput_model": best,
            "results": rows, "real_device_test": "REQUIRED" if not execute else "OWNER_RUN",
            "note": "Speed is an observation, not coding-quality or isolation proof."}


def main(argv=None):
    p = argparse.ArgumentParser(description="Sequential local Ollama 3B/4B comparison")
    p.add_argument("--first", default=DEFAULTS[0])
    p.add_argument("--second", default=DEFAULTS[1])
    p.add_argument("--execute", action="store_true")
    p.add_argument("--output", type=Path, help="new owner-private evidence file")
    a = p.parse_args(argv)
    result = compare_models((a.first, a.second), a.execute)
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if a.output:
        output = a.output.expanduser().absolute()
        if output.is_symlink() or any(p.is_symlink() for p in output.parents):
            raise ContractError("comparison output symlink forbidden")
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("x", encoding="utf-8") as f:
            f.write(payload)
    print(payload)
    return 0 if (result["completed"] or not a.execute) else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError, ContractError) as exc:
        print("AXDEV_COMPARE_ERROR:", type(exc).__name__)
        raise SystemExit(2)
