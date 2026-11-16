"""AXDEV Windows Sandbox guest: one synthetic isolated local task.

Executed INSIDE a Windows Sandbox with networking/vGPU/clipboard off.
A clean Git snapshot and an approved offline toolchain are read-only host
mappings; only a fresh outbox is writable from the guest. This is NOT
an implementation for running on the host and never grants remote access.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import getpass
import json
import os
import re
import stat
import subprocess
import sys
import time
import zipfile
from pathlib import Path
from urllib.request import ProxyHandler, Request, build_opener

SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
RUN = re.compile(r"^[0-9a-f]{32}$")
MAX_ARCHIVE = 64 * 1024 * 1024
MAX_CODE = 8 * 1024 * 1024
BINARIES = ("python/python.exe", "git/cmd/git.exe",
            "ollama/ollama.exe", "opencode/opencode.exe")


def _digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as source:
        while True:
            chunk = source.read(1024 * 1024)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def _run(argv, cwd: Path, timeout: int = 45) -> bytes:
    p = subprocess.run(argv, cwd=cwd, shell=False, check=False,
                       stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, timeout=timeout)
    if p.returncode or len(p.stdout) > MAX_CODE:
        raise RuntimeError("SANDBOX_COMMAND_FAILED")
    return p.stdout


def _safe_payload(raw: bytes) -> dict:
    if len(raw) > 64 * 1024:
        raise ValueError("SANDBOX_REQUEST_TOO_LARGE")
    request = json.loads(raw.decode("utf-8"))
    mandatory = {"version", "run_id", "base_sha", "task",
                 "task_sha256", "model", "archive_sha256", "bundle_sha256"}
    if not isinstance(request, dict) or set(request) != mandatory:
        raise ValueError("SANDBOX_REQUEST_FIELDS")
    if (request["version"] != 1 or not RUN.fullmatch(request["run_id"])
            or not SHA40.fullmatch(request["base_sha"])
            or not SHA256.fullmatch(request["task_sha256"])
            or not SHA256.fullmatch(request["archive_sha256"])
            or not SHA256.fullmatch(request["bundle_sha256"])):
        raise ValueError("SANDBOX_REQUEST_PIN_INVALID")
    model = request["model"]
    if not isinstance(model, str) or not re.fullmatch(
            r"ollama/[A-Za-z0-9_.:/-]{2,100}", model):
        raise ValueError("SANDBOX_MODEL_UNSUPPORTED")
    return request


def _toolchain(bundle: Path, expected: str) -> dict:
    manifest = bundle / "manifest.json"
    if not manifest.is_file() or manifest.stat().st_size > 4096:
        raise ValueError("SANDBOX_OFFLINE_BUNDLE_MANIFEST_MISSING")
    if _digest(manifest) != expected:
        raise ValueError("SANDBOX_OFFLINE_BUNDLE_PIN_MISMATCH")
    data = json.loads(manifest.read_text(encoding="utf-8"))
    if (not isinstance(data, dict) or data.get("version") != 1
            or set(data.get("executables", {})) != set(BINARIES)):
        raise ValueError("SANDBOX_BUNDLE_SCHEMA")
    for rel in BINARIES:
        path = bundle / Path(rel)
        if (path.is_symlink() or not path.is_file()
                or not SHA256.fullmatch(data["executables"][rel])
                or _digest(path) != data["executables"][rel]):
            raise ValueError("SANDBOX_BINARY_HASH_MISMATCH")
    if not (bundle / "models").is_dir():
        raise ValueError("SANDBOX_OFFLINE_MODELS_MISSING")
    return data


def _extract(source: Path, destination: Path) -> None:
    if not source.is_file() or source.stat().st_size > MAX_ARCHIVE:
        raise ValueError("SANDBOX_ARCHIVE_MISSING_OR_LARGE")
    destination.mkdir(parents=True, exist_ok=False)
    budget = MAX_ARCHIVE
    with zipfile.ZipFile(source, "r") as archive:
        files = archive.infolist()
        if not files or len(files) > 6000:
            raise ValueError("SANDBOX_ARCHIVE_ENTRY_LIMIT")
        seen = set()
        for item in files:
            path = item.filename.rstrip("/")
            parts = path.split("/")
            if (not path or path.startswith("/") or "\\" in path
                    or any(p in ("", ".", "..") or ":" in p for p in parts)
                    or ".git" in parts or len(path) > 260 or path.casefold() in seen):
                raise ValueError("SANDBOX_ARCHIVE_UNSAFE_PATH")
            seen.add(path.casefold())
            mode = item.external_attr >> 16
            if stat.S_ISLNK(mode):
                raise ValueError("SANDBOX_ARCHIVE_SYMLINK")
            if item.is_dir():
                continue
            if item.file_size < 0 or item.file_size > budget:
                raise ValueError("SANDBOX_ARCHIVE_DECOMPRESSION_LIMIT")
            budget -= item.file_size
            target = destination.joinpath(*parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(item) as data:
                content = data.read(item.file_size + 1)
            if len(content) != item.file_size:
                raise ValueError("SANDBOX_ARCHIVE_CORRUPT")
            with target.open("xb") as target_file:
                target_file.write(content)


def _wait_local_ollama(process: subprocess.Popen, timeout: int = 90) -> None:
    client = build_opener(ProxyHandler({}))
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError("SANDBOX_OLLAMA_EARLY_EXIT")
        try:
            with client.open(Request("http://127.0.0.1:11434/api/tags"),
                             timeout=2) as response:
                if response.status == 200 and len(response.read(65537)) <= 65536:
                    return
        except (OSError, ValueError, RuntimeError):
            pass
        time.sleep(1)
    raise TimeoutError("SANDBOX_OLLAMA_BOOT_TIMEOUT")


def _files(repo: Path, before: str, after: str, task: dict) -> list[dict]:
    raw = _run(["git", "diff", "--name-only", "-z", before, after, "--"], repo)
    if raw and not raw.endswith(b"\0"):
        raise RuntimeError("SANDBOX_DIFF_NOT_NUL_TERMINATED")
    changed = [name.decode("utf-8") for name in raw.split(b"\0")[:-1]]
    if not changed or len(changed) > 16 or not set(changed) <= set(task["files"]):
        raise RuntimeError("SANDBOX_DIFF_OUTSIDE_APPROVED_SCOPE")
    output = []
    bytes_left = MAX_CODE
    for name in changed:
        tree = _run(["git", "ls-tree", after, "--", name], repo)
        if not tree:
            output.append({"path": name, "sha256": None, "data_b64": None})
            continue
        entry = tree.decode("utf-8", errors="strict").split(maxsplit=2)
        if not entry or entry[0] not in ("100644", "100755"):
            raise RuntimeError("SANDBOX_GIT_UNSAFE_FILE_MODE")
        body = _run(["git", "show", after + ":" + name], repo)
        bytes_left -= len(body)
        if bytes_left < 0:
            raise RuntimeError("SANDBOX_OUTPUT_FILE_LIMIT")
        output.append({"path": name, "sha256": hashlib.sha256(body).hexdigest(),
                       "data_b64": base64.b64encode(body).decode("ascii")})
    return output


def _work(request: dict, input_root: Path, bundle: Path) -> dict:
    from axdev.core import Factory, git, plan_hash

    task = request["task"]
    if not isinstance(task, dict) or plan_hash(task) != request["task_sha256"]:
        raise ValueError("SANDBOX_TASK_SPEC_MISMATCH")
    origin_archive = input_root / "source.zip"
    if _digest(origin_archive) != request["archive_sha256"]:
        raise ValueError("SANDBOX_SOURCE_ARCHIVE_PIN_MISMATCH")
    workroot = Path(r"C:\AXDEV_RUN")
    workroot.mkdir(parents=True, exist_ok=True)
    repo = workroot / "project"
    _extract(origin_archive, repo)
    _run(["git", "init", "-q"], repo)
    _run(["git", "config", "user.name", "AXDEV Sandbox"], repo)
    _run(["git", "config", "user.email", "sandbox@local.invalid"], repo)
    _run(["git", "config", "core.autocrlf", "false"], repo)
    _run(["git", "add", "--all"], repo)
    _run(["git", "commit", "-q", "-m", "trusted disposable import"], repo)
    before = git(repo, "rev-parse", "HEAD")

    # Dependency proof was already checked against the immutable host queue.
    # Only this task's approved file/check contract is executed in the guest.
    guest_task = dict(task)
    guest_task["depends_on"] = []
    plan = workroot / "single-approved-task.json"
    with plan.open("x", encoding="utf-8") as file:
        json.dump({"version": 1, "tasks": [guest_task]}, file)
    ollama = bundle / "ollama" / "ollama.exe"
    env = os.environ.copy()
    env["OLLAMA_HOST"] = "127.0.0.1:11434"
    env["OLLAMA_MODELS"] = str(bundle / "models")
    env["OPENCODE_DISABLE_AUTOUPDATE"] = "true"
    env["OPENCODE_AUTO_SHARE"] = "false"
    env["HTTP_PROXY"] = env["HTTPS_PROXY"] = env["ALL_PROXY"] = "http://127.0.0.1:9"
    env["NO_PROXY"] = "127.0.0.1,localhost"
    server = subprocess.Popen([str(ollama), "serve"], cwd=workroot, env=env,
                              stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL, shell=False)
    try:
        _wait_local_ollama(server)
        f = Factory(repo, plan, workroot / "state", model=request["model"])
        try:
            outcome = f.run_one(True)
            if outcome.get("status") != "VERIFIED":
                raise RuntimeError("SANDBOX_TASK_DID_NOT_VERIFY")
            latest = outcome["commit"]
            files = _files(repo, before, latest, task)
            if git(repo, "rev-parse", f.integration_ref) != latest:
                raise RuntimeError("SANDBOX_INTEGRATION_NOT_VERIFIED")
            return {"status": "VERIFIED", "files": files, "guest_commit": latest}
        finally:
            f.close()
    finally:
        server.terminate()
        try:
            server.wait(timeout=8)
        except subprocess.TimeoutExpired:
            server.kill()


def _deliver(outbox: Path, obj: dict) -> None:
    if not outbox.is_dir():
        raise ValueError("SANDBOX_OUTBOX_MISSING")
    raw = json.dumps(obj, ensure_ascii=False, sort_keys=True).encode("utf-8")
    if len(raw) > 12 * 1024 * 1024:
        raise ValueError("SANDBOX_RECEIPT_TOO_LARGE")
    temporary = outbox / "receipt.tmp"
    with temporary.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, outbox / "receipt.json")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=r"C:\AXDEV_INPUT", type=Path)
    parser.add_argument("--bundle", default=r"C:\AXDEV_BUNDLE", type=Path)
    parser.add_argument("--outbox", default=r"C:\AXDEV_OUTBOX", type=Path)
    args = parser.parse_args(argv)
    # Sandbox images normally run as WDAGUtilityAccount. This heuristic
    # rejects accidental host invocation; it does not replace OS isolation.
    if os.name != "nt" or getpass.getuser().casefold() != "wdagutilityaccount":
        raise ValueError("SANDBOX_GUEST_ACCOUNT_REQUIRED")
    request = _safe_payload((args.input / "request.json").read_bytes())
    response = {"version": 1, "run_id": request["run_id"],
                "base_sha": request["base_sha"],
                "task_id": request["task"]["id"],
                "task_sha256": request["task_sha256"]}
    try:
        _toolchain(args.bundle, request["bundle_sha256"])
        result = _work(request, args.input, args.bundle)
        response.update(result)
    except (OSError, ValueError, RuntimeError, TimeoutError,
            subprocess.SubprocessError, zipfile.BadZipFile) as exc:
        # Never print or persist prompt, source bytes, secrets or model output.
        response.update({"status": "HOLD", "error_code": type(exc).__name__})
    _deliver(args.outbox, response)
    return 0 if response["status"] == "VERIFIED" else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        # Do not echo exceptions that may contain private paths/source.
        raise SystemExit(2)
