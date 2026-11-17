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

from axdev.opencode_guard import supported_release


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
    return result.returncode == 0, ((result.stdout or "") + (result.stderr or "")).strip()[-12000:]


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


def _ollama_capabilities(model_id: str) -> list[str]:
    """Ollama's native /api/show reports completion and tool-call capabilities."""
    if not re.fullmatch(r"[A-Za-z0-9_.:/-]{2,100}", model_id):
        raise RuntimeError("invalid selected local model ID")
    request = Request("http://127.0.0.1:11434/api/show",
                      data=json.dumps({"model": model_id}).encode("utf-8"),
                      headers={"Content-Type": "application/json"},
                      method="POST")
    opener = build_opener(ProxyHandler({}))
    with opener.open(request, timeout=5) as response:
        if response.status != 200:
            raise RuntimeError("Ollama show returned non-200")
        payload = response.read(65537)
    if len(payload) > 65536:
        raise RuntimeError("Ollama show response too large")
    value = json.loads(payload)
    if not isinstance(value, dict) or not isinstance(value.get("capabilities"), list):
        raise RuntimeError("Ollama show did not expose a capability list")
    caps = value["capabilities"]
    if any(not isinstance(cap, str) for cap in caps):
        raise RuntimeError("unexpected Ollama capabilities")
    return caps


def _git_identity_ready(repo: Path) -> bool:
    """Check actual author+committer Git identities without exposing emails."""
    repo = Path(repo).expanduser().absolute()
    if repo.is_symlink() or any(parent.is_symlink() for parent in repo.parents):
        return False
    if not (repo / ".git").exists():
        return False
    for role in ("GIT_AUTHOR_IDENT", "GIT_COMMITTER_IDENT"):
        try:
            outcome = subprocess.run(["git", "-C", str(repo), "var", role],
                                     capture_output=True, text=True, errors="replace",
                                     timeout=5, shell=False, check=False)
        except (OSError, subprocess.TimeoutExpired):
            return False
        # Never persist the actual username/email: only a boolean.
        if outcome.returncode or not outcome.stdout.strip():
            return False
    return True


def inspect(model: str, repo: Path | None = None) -> dict:
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
    oc_help, help_text = _version("opencode", "run", "--help")
    standalone = oc_help and "--standalone" in help_text
    checks["opencode"]["standalone_advertised"] = standalone
    # plugin.use needs >=2.2.3; websearch.use is ignored before 2.2.6.
    # A permissive older CLI must never silently bypass deny policies.
    if checks["opencode"]["found_and_runs"] and not supported_release(checks["opencode"]["version"]):
        blockers.append("OpenCode 2.2.6+ required for effective V2 hard policies")
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
    # Installed weights alone are not enough: OpenCode needs a completion
    # model that can emit tool calls for scoped source edits.
    capabilities = []
    if result["model_present"]:
        try:
            capabilities = _ollama_capabilities(model_id)
        except (OSError, ValueError, RuntimeError, TimeoutError) as exc:
            blockers.append("Ollama model capabilities unavailable: " + type(exc).__name__)
        else:
            if "completion" not in capabilities:
                blockers.append("selected Ollama model does not support completion")
            if "tools" not in capabilities:
                blockers.append("selected Ollama model does not support tool calling")
    if repo is not None:
        identity_ok = _git_identity_ready(repo)
        result["git_author_committer_ready"] = identity_ok
        result["git_identity_github_account_verified"] = False
        if not identity_ok:
            blockers.append("local Git author/committer identity is missing or invalid")
    result["model_capabilities"] = capabilities
    result["model_tool_calls_supported"] = "tools" in capabilities
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
    parser.add_argument("--repo", type=Path,
                        help="optional target checkout; checks both Git identities without exposing email")
    options = parser.parse_args(argv)
    report = inspect(options.model, options.repo)
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
