"""One-time private local settings; refuse overwrite and never upload settings."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path

def default_file():
    root = Path(os.environ.get("LOCALAPPDATA") or Path.home() / ".axdev")
    return root / "AXDevFactory" / "settings.json"

def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--plan", type=Path, required=True)
    p.add_argument("--model", default="ollama/qwen3:4b-instruct")
    p.add_argument("--settings", type=Path, default=default_file())
    a = p.parse_args(argv)
    repo, plan, settings = a.repo.resolve(), a.plan.resolve(), a.settings.resolve()
    if not (repo / ".git").exists():
        raise SystemExit("target must be an existing local Git clone")
    if not plan.is_file():
        raise SystemExit("plan must exist locally")
    if not a.model.startswith("ollama/"):
        raise SystemExit("only local Ollama is supported")
    if settings.exists():
        raise SystemExit("settings exist; refusing overwrite (back up and review manually)")
    state = settings.parent / "state"
    if repo == state or repo in state.parents:
        raise SystemExit("state cannot be inside target repo")
    settings.parent.mkdir(parents=True, exist_ok=True)
    obj = {"version": 1, "repo": str(repo), "plan": str(plan),
           "state": str(state), "model": a.model, "max_tasks": 100}
    # Contains local paths only; never put secrets in this configuration.
    settings.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
    print("Created private path-only configuration:", settings)
    print("Review its contents; then run RUN_QUEUE.cmd once to execute the queue.")

if __name__ == "__main__":
    main()
