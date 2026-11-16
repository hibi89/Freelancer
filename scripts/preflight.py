"""Read-only, localhost-only preflight before the first disposable model trial.

Never downloads models, installs tools, executes AI, alters configuration,
or makes any network request except 127.0.0.1:11434.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from urllib.request import ProxyHandler, Request, build_opener
from pathlib import Path


def _version(executable: str, *args: str) -> tuple[bool, str]:
    found = shutil.which(executable)
    if not found:
        return False, "not installed"
    try:
        result = subprocess.run([found, *args], capture_output=True,
                                text=True, errors="replace", timeout=8,
                                check=False, shell=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, type(exc).__name__
    return result.returncode == 0, (result.stdout or result.stderr).strip()[:200]


def _ollama_models() -> list[str]:
    url = "http://127.0.0.1:11434/api/tags"
    opener = build_opener(ProxyHandler({}))
    with opener.open(Request(url, headers={"Accept": "application/json"}),
                     timeout=3) as response:
        if response.status != 200:
            raise RuntimeError("Ollama localhost returned non-200")
        payload = response.read(65537)
    if len(payload) > 65536:
        raise RuntimeError("Ollama tags response too large")
    decoded = json.loads(payload)
    if not isinstance(decoded, dict) or not isinstance(decoded.get("models"), list):
        raise RuntimeError("unexpected Ollama tags JSON")
    return [obj["name"] for obj in decoded["models"]
            if isinstance(obj, dict) and isinstance(obj.get("name"), str)]


def inspect(model: str) -> dict:
    result = {"preflight_version": 1, "platform": platform.system(),
              "python": platform.python_version(), "model": model,
              "approved_for_real_tasks": False,
              "opencode_permission_e2e_verified": False,
              "gpu_performance_verified": False}
    blockers = []
    if sys.version_info < (3, 11):
        blockers.append("Python 3.11+ required")
    if not model.startswith("ollama/") or len(model) <= len("ollama/"):
        blockers.append("explicit local ollama/<model> is required")
    checks = {}
    for executable in ("git", "ollama", "opencode"):
        args = ("--version",)
        okay, message = _version(executable, *args)
        checks[executable] = {"found_and_runs": okay, "version": message}
        if not okay:
            blockers.append(executable + " missing or failed --version")
    oc_help, help_text = _version("opencode", "--help")
    standalone = oc_help and "--standalone" in help_text
    checks["opencode"]["standalone_advertised"] = standalone
    major = re.search(r"(?<!\d)(\d+)\.\d+", checks["opencode"]["version"])
    if checks["opencode"]["found_and_runs"] and (not major or int(major.group(1)) < 2):
        blockers.append("OpenCode 2+ is required; verify --version")
    if not standalone:
        blockers.append("OpenCode --standalone option not confirmed")
    try:
        installed = _ollama_models()
    except (OSError, ValueError, RuntimeError, TimeoutError) as exc:
        installed = []
        blockers.append("Ollama localhost API unavailable: " + type(exc).__name__)
    result["ollama_models"] = installed
    model_id = model.removeprefix("ollama/") if model.startswith("ollama/") else ""
    result["model_present"] = model_id in installed
    if not result["model_present"]:
        blockers.append("selected Ollama model not installed")
    found_gpu = shutil.which("nvidia-smi") is not None
    gpu_ok, gpu_msg = _version("nvidia-smi", "--query-gpu=name,memory.total",
                               "--format=csv,noheader,nounits") if found_gpu else (False, "not found")
    result["gpu_detected"] = gpu_ok
    result["gpu_summary"] = gpu_msg
    # CPU fallback is possible; absence of an NVIDIA GPU must not be treated
    # as proof that a local coding model will fail.
    result["checks"] = checks
    result["blockers"] = blockers
    result["ready_for_disposable_model_trial"] = not blockers
    result["notes"] = [
        "This is read-only host introspection, not a tool-permission enforcement test.",
        "Use a disposable non-admin checkout with no secrets for the first trial.",
        "No packages, remote APIs or model weights were downloaded.",
    ]
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description="Local-only AXDEV model preflight")
    parser.add_argument("--model", default=os.environ.get("AXDEV_MODEL", "ollama/qwen3:4b-instruct"))
    parser.add_argument("--output", type=Path, help="optional private JSON evidence path (new file only)")
    options = parser.parse_args(argv)
    report = inspect(options.model)
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if options.output:
        path = options.output.expanduser().absolute()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x", encoding="utf-8") as fp:
            fp.write(payload)
    print(payload)
    return 0 if report["ready_for_disposable_model_trial"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
