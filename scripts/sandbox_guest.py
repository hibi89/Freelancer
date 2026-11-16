"""Disposable Windows Sandbox coding guest. Its output is candidate data only."""
from __future__ import annotations

import getpass
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from urllib.request import ProxyHandler, Request, build_opener

# Also works with the official embeddable Python, which can ignore PYTHONPATH.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from axdev.core import ContractError, Factory, git, safe_path
from axdev.sandbox_payload import (
    BINARIES, MAX_CODE, MAX_RECEIPT, RUN_ID, SHA40, SHA256, decode_files, encode_files,
    extract_snapshot, hex_sha, no_reparse, read_json, write_json,
)


def _safe_payload(request: dict) -> dict:
    fields = {"version", "run_id", "base_sha", "task", "task_sha256", "model",
              "archive_sha256", "bundle_sha256", "initial_sha256"}
    if (set(request) != fields or request["version"] != 2
            or not RUN_ID.fullmatch(request["run_id"]) or not SHA40.fullmatch(request["base_sha"])
            or any(not SHA256.fullmatch(request[key]) for key in
                   ("task_sha256", "archive_sha256", "bundle_sha256"))
            or request["initial_sha256"] is not None and not SHA256.fullmatch(request["initial_sha256"])
            or not re.fullmatch(r"ollama/[A-Za-z0-9_.:/-]{2,100}", request["model"])):
        raise ContractError("invalid sandbox coding request")
    if set(request["task"]) != {"id", "goal", "files"}:
        raise ContractError("sandbox coding task contains unexpected fields")
    return request


def _toolchain(bundle: Path, expected: str) -> None:
    data, digest = read_json(bundle / "manifest.json", 4 * 1024 * 1024)
    if digest != expected or data.get("version") != 2:
        raise ContractError("sandbox bundle manifest differs")
    for name in BINARIES:
        if hex_sha(bundle / name) != data["files"][name]:
            raise ContractError("sandbox offline binary differs")


def _wait_local_ollama(process: subprocess.Popen, timeout: int = 90) -> None:
    client = build_opener(ProxyHandler({}))
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise ContractError("sandbox Ollama process exited")
        try:
            with client.open(Request("http://127.0.0.1:11434/api/tags"), timeout=2) as response:
                if response.status == 200 and len(response.read(65537)) <= 65536:
                    return
        except OSError:
            pass
        time.sleep(1)
    raise TimeoutError("sandbox Ollama startup timed out")


def _work(request: dict, input_root: Path, bundle: Path) -> dict:
    workroot = Path(r"C:\AXDEV_RUN")
    repo = workroot / "project"
    archive = input_root / "source.zip"
    if hex_sha(archive) != request["archive_sha256"]:
        raise ContractError("sandbox source archive differs")
    extract_snapshot(archive, repo)
    git(repo, "init", "-q")
    for name, value in (("user.name", "AXDEV Sandbox"), ("user.email", "sandbox@local.invalid"),
                        ("core.autocrlf", "false")):
        git(repo, "config", name, value)
    # The approved source is a Git snapshot; preserve tracked ignored files.
    git(repo, "add", "--force", "--all")
    git(repo, "commit", "-q", "-m", "disposable pinned snapshot")

    task = dict(request["task"], depends_on=[], checks=[["python", "-m", "compileall", "-q", "src"]])
    plan = workroot / "coding-task.json"
    write_json(plan, {"version": 1, "tasks": [task]})
    factory = Factory(repo, plan, workroot / "state", model=request["model"])
    server = None
    try:
        workspace = factory._workspace(task["id"])
        allowed = set(task["files"])
        initial_sha = request["initial_sha256"]
        if initial_sha:
            initial, digest = read_json(input_root / "initial.json", MAX_RECEIPT)
            if digest != initial_sha:
                raise ContractError("sandbox repair input differs")
            for name, body in decode_files(initial["files"], allowed).items():
                target = no_reparse(workspace / safe_path(name))
                if body is None:
                    target.unlink()
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(body)
        os.environ["OLLAMA_HOST"] = "127.0.0.1:11434"
        os.environ["OLLAMA_MODELS"] = str(bundle / "models")
        os.environ["OLLAMA_NO_CLOUD"] = "1"
        server = subprocess.Popen([str(bundle / "ollama" / "ollama.exe"), "serve"], cwd=workroot,
                                  stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                  stderr=subprocess.DEVNULL, shell=False)
        _wait_local_ollama(server)
        factory._active_allowed_files = tuple(task["files"])
        phase = "FIX_ONCE" if initial_sha else "CODING"
        feedback = "The previous candidate failed independent acceptance. Recheck the approved behavior." if initial_sha else ""
        rc, _ = factory._opencode(workspace, factory._prompt(task, phase, feedback))
        if rc:
            raise ContractError("sandbox coding command failed")
        changed = factory._changed(workspace)
        if not changed or not changed <= allowed:
            raise ContractError("sandbox candidate has no change or edits outside its scope")
        files = {}
        budget = MAX_CODE
        for name in changed:
            path = no_reparse(workspace / safe_path(name))
            if not path.exists():
                files[name] = None
                continue
            if not path.is_file() or path.stat().st_size > budget:
                raise ContractError("invalid or oversized sandbox candidate")
            data = path.read_bytes()
            budget -= len(data)
            if budget < 0:
                raise ContractError("sandbox candidate too large")
            files[name] = data
        return {"status": "CANDIDATE", "files": encode_files(files)}
    finally:
        factory.close()
        if server:
            server.terminate()
            try:
                server.wait(timeout=8)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait(timeout=8)


def main():
    if os.name != "nt" or getpass.getuser().casefold() != "wdagutilityaccount":
        raise ContractError("sandbox coding guest account required")
    input_root, bundle = Path(r"C:\AXDEV_INPUT"), Path(r"C:\AXDEV_BUNDLE")
    request = _safe_payload(read_json(input_root / "request.json", 65536)[0])
    receipt = {"version": 2, "run_id": request["run_id"], "base_sha": request["base_sha"],
               "task_id": request["task"]["id"], "task_sha256": request["task_sha256"]}
    try:
        _toolchain(bundle, request["bundle_sha256"])
        receipt.update(_work(request, input_root, bundle))
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError):
        receipt["status"] = "HOLD"
    write_json(Path(r"C:\AXDEV_OUTBOX\receipt.json"), receipt)
    return 0 if receipt["status"] == "CANDIDATE" else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        raise SystemExit(2)
