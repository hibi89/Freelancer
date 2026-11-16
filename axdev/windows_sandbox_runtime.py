"""Owner-opted Windows Sandbox executor for local code and acceptance.

The host NEVER invokes Ollama, OpenCode, or user acceptance commands. A
Windows Sandbox guest runs the existing Factory on a disposable snapshot.
Only approved content bytes return through a fresh, single-purpose outbox,
then the host imports/commits the reviewed result to a local integration ref.

Not a tested OS sandbox until exercised on the owner's Windows edition.
Windows Home/disabled Sandbox: fail closed, with NO fallback to host model.
"""
from __future__ import annotations

import base64
import hashlib
import json
import io
import os
import re
import secrets
import stat
import zipfile
import subprocess
import time
import xml.etree.ElementTree as ET
from pathlib import Path

from .core import ContractError, Factory, git, plan_hash, safe_path

SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
RUN = re.compile(r"^[0-9a-f]{32}$")
MAX_ARCHIVE = 64 * 1024 * 1024
MAX_CODE = 8 * 1024 * 1024
MAX_RECEIPT = 12 * 1024 * 1024
BINARIES = ("python/python.exe", "git/cmd/git.exe",
            "ollama/ollama.exe", "opencode/opencode.exe")
ENGINE = (
    "axdev/__init__.py", "axdev/core.py", "axdev/repo_trust.py",
    "axdev/batch.py", "axdev/opencode_guard.py", "axdev/semantic_review.py",
    "axdev/eai_adapter.py", "axdev/axnode_adapter.py",
    "config/opencode-local-only.json",
    ".opencode/skills/ax-coding/SKILL.md",
    "scripts/sandbox_guest.py",
)


def _hex_sha(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as data:
        while True:
            part = data.read(1024 * 1024)
            if not part:
                return result.hexdigest()
            result.update(part)


def _no_reparse(path: Path):
    """Fail closed on symbolic links and NTFS junction/reparse ancestors."""
    absolute = path.expanduser().absolute()
    for item in (absolute, *absolute.parents):
        if item.is_symlink():
            raise ContractError("sandbox path is a symbolic link")
        try:
            attributes = item.lstat().st_file_attributes
        except (FileNotFoundError, AttributeError):
            continue
        if attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400):
            raise ContractError("sandbox path uses a Windows reparse point")
    return absolute


def _reject_mapped_reparse_tree(root: Path) -> None:
    """Never share a junction/symlink that could escape the offline bundle.

    Read-only mapping does not guarantee that host-side reparse points are
    confined to the approved source tree. Refuse them before Sandbox launch.
    """
    visited = 0
    for directory, folders, files in os.walk(root, followlinks=False):
        _no_reparse(Path(directory))
        visited += len(folders) + len(files)
        if visited > 200000:
            raise ContractError("offline bundle contains too many host paths")
        for name in (*folders, *files):
            _no_reparse(Path(directory) / name)


def _read_bundle(bundle: Path, expected_sha: str) -> None:
    if not isinstance(expected_sha, str) or not SHA256.fullmatch(expected_sha):
        raise ContractError("offline bundle manifest SHA256 must be owner-pinned")
    manifest = bundle / "manifest.json"
    _no_reparse(bundle)
    _no_reparse(manifest)
    if not manifest.is_file() or manifest.stat().st_size > 4096:
        raise ContractError("missing offline bundle manifest")
    if _hex_sha(manifest) != expected_sha:
        raise ContractError("offline runtime bundle hash mismatched approved pin")
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ContractError("invalid offline bundle manifest") from exc
    if (not isinstance(data, dict) or data.get("version") != 1
            or not isinstance(data.get("executables"), dict)
            or set(data["executables"]) != set(BINARIES)):
        raise ContractError("offline bundle manifest schema differs")
    for name in BINARIES:
        file = _no_reparse(bundle / Path(name))
        expected = data["executables"][name]
        if (not isinstance(expected, str) or not SHA256.fullmatch(expected)
                or not file.is_file() or _hex_sha(file) != expected):
            raise ContractError("offline runtime binary missing/changed")
    if not _no_reparse(bundle / "models").is_dir():
        raise ContractError("offline model cache missing")
    _reject_mapped_reparse_tree(bundle)


def _sandbox_binary() -> Path:
    if os.name != "nt":
        raise ContractError("Windows Sandbox is unavailable on this host")
    import ctypes
    system_directory = ctypes.create_unicode_buffer(512)
    size = ctypes.windll.kernel32.GetSystemDirectoryW(
        system_directory, len(system_directory))
    if not 1 <= size < len(system_directory):
        raise ContractError("trusted Windows System32 path unavailable")
    executable = _no_reparse(
        Path(system_directory.value) / "WindowsSandbox.exe")
    if not executable.is_file():
        raise ContractError("Windows Sandbox unavailable; Windows Home is unsupported")
    return executable


def _engine_copy(destination: Path) -> None:
    source = Path(__file__).resolve().parent.parent
    for relative in ENGINE:
        origin = _no_reparse(source / Path(relative))
        if not origin.is_file() or origin.stat().st_size > 2 * 1024 * 1024:
            raise ContractError("trusted AXDEV engine file unavailable/oversized")
        target = destination / Path(relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        with origin.open("rb") as reader, target.open("xb") as writer:
            writer.write(reader.read(2 * 1024 * 1024 + 1))


def _archive_verified_base(factory: Factory, baseline: str, path: Path) -> str:
    try:
        p = subprocess.run(["git", "archive", "--format=zip", baseline],
                           cwd=factory.repo, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, stdin=subprocess.DEVNULL,
                           check=False, timeout=60, shell=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ContractError("sandbox source snapshot unavailable") from exc
    if p.returncode or not p.stdout or len(p.stdout) > MAX_ARCHIVE:
        raise ContractError("sandbox archive failed or exceeds configured source limit")
    # export-ignore could silently remove protected acceptance tests. Require
    # exact correspondence between Git's pinned commit tree and the archive.
    try:
        inventory = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", "-z", baseline],
            cwd=factory.repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL, check=False, timeout=30, shell=False)
        if inventory.returncode or len(inventory.stdout) > 8 * 1024 * 1024:
            raise ContractError("sandbox baseline path inventory unavailable")
        tracked = {name.decode("utf-8") for name in
                   inventory.stdout.split(b"\0") if name}
        with zipfile.ZipFile(io.BytesIO(p.stdout)) as archive:
            in_archive = {entry.filename for entry in archive.infolist()
                          if not entry.is_dir()}
        if not tracked or in_archive != tracked:
            raise ContractError("source snapshot omits a pinned tracked file")
    except (UnicodeError, ValueError, zipfile.BadZipFile,
            OSError, subprocess.TimeoutExpired) as exc:
        raise ContractError("source snapshot cannot be inventoried") from exc
    with path.open("xb") as out:
        out.write(p.stdout)
    return _hex_sha(path)


def _wsb(input_dir: Path, bundle: Path, outbox: Path) -> bytes:
    """Only the empty per-run outbox is writable; no host project mapping."""
    root = ET.Element("Configuration")
    for name in ("Networking", "VGpu", "ClipboardRedirection",
                 "PrinterRedirection", "AudioInput", "VideoInput"):
        ET.SubElement(root, name).text = "Disable"
    mappings = ET.SubElement(root, "MappedFolders")
    for host_path, guest_path, readonly in (
        (input_dir, r"C:\AXDEV_INPUT", True),
        (bundle, r"C:\AXDEV_BUNDLE", True),
        (outbox, r"C:\AXDEV_OUTBOX", False),
    ):
        mapped = ET.SubElement(mappings, "MappedFolder")
        ET.SubElement(mapped, "HostFolder").text = str(_no_reparse(host_path))
        ET.SubElement(mapped, "SandboxFolder").text = guest_path
        ET.SubElement(mapped, "ReadOnly").text = "true" if readonly else "false"
    command = ET.SubElement(root, "LogonCommand")
    ET.SubElement(command, "Command").text = (
        r"powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass "
        r"-File C:\AXDEV_INPUT\bootstrap.ps1"
    )
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def _bootstrap() -> str:
    """Guest-only PowerShell. Runtime and model are inside Windows Sandbox."""
    return (
        "$ErrorActionPreference = 'Stop'\n"
        "$env:PATH = 'C:\\AXDEV_BUNDLE\\python;C:\\AXDEV_BUNDLE\\git\\cmd;"
        "C:\\AXDEV_BUNDLE\\ollama;C:\\AXDEV_BUNDLE\\opencode;' + $env:PATH\n"
        "$env:PYTHONPATH = 'C:\\AXDEV_INPUT\\engine'\n"
        "$env:PYTHONDONTWRITEBYTECODE = '1'\n"
        "$env:OPENCODE_DISABLE_AUTOUPDATE = 'true'\n"
        "$env:OPENCODE_DISABLE_FREE_MODELS = 'true'\n"
        "$env:OPENCODE_AUTO_SHARE = 'false'\n"
        "$env:HOME = 'C:\\AXDEV_RUN\\home'\n"
        "$env:USERPROFILE = 'C:\\AXDEV_RUN\\home'\n"
        "$env:APPDATA = 'C:\\AXDEV_RUN\\home\\AppData\\Roaming'\n"
        "$env:LOCALAPPDATA = 'C:\\AXDEV_RUN\\home\\AppData\\Local'\n"
        "New-Item -ItemType Directory -Force 'C:\\AXDEV_RUN\\home' | Out-Null\n"
        "& 'C:\\AXDEV_BUNDLE\\python\\python.exe' "
        "'C:\\AXDEV_INPUT\\engine\\scripts\\sandbox_guest.py' "
        "--input 'C:\\AXDEV_INPUT' --bundle 'C:\\AXDEV_BUNDLE' "
        "--outbox 'C:\\AXDEV_OUTBOX'\n"
    )


def _prepare(factory: Factory, task: dict, bundle: Path, bundle_sha: str) -> tuple[str, Path, str]:
    baseline = git(factory.repo, "rev-parse", factory.integration_ref)
    if not SHA40.fullmatch(baseline):
        raise ContractError("unverified integration reference")
    run_id = secrets.token_hex(16)
    root = _no_reparse(factory.state / "sandbox-runs" / run_id)
    input_dir, outbox = root / "input", root / "outbox"
    input_dir.mkdir(parents=True, exist_ok=False)
    outbox.mkdir(parents=False, exist_ok=False)
    digest = _archive_verified_base(factory, baseline, input_dir / "source.zip")
    _engine_copy(input_dir / "engine")
    request = {
        "version": 1, "run_id": run_id, "base_sha": baseline,
        "task": task, "task_sha256": plan_hash(task),
        "model": factory.model, "archive_sha256": digest,
        "bundle_sha256": bundle_sha,
    }
    with (input_dir / "request.json").open("x", encoding="utf-8") as out:
        json.dump(request, out, ensure_ascii=False)
    (input_dir / "bootstrap.ps1").write_text(_bootstrap(), encoding="utf-8")
    (root / "launch.wsb").write_bytes(_wsb(input_dir, bundle, outbox))
    return run_id, root, baseline


def _read_receipt(root: Path, run_id: str, task: dict, baseline: str) -> dict | None:
    receipt_path = _no_reparse(root / "outbox" / "receipt.json")
    if not receipt_path.is_file():
        return None
    if receipt_path.stat().st_size > MAX_RECEIPT:
        raise ContractError("oversized sandbox output")
    try:
        data = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ContractError("invalid sandbox output") from exc
    required = {"version", "run_id", "base_sha", "task_id",
                "task_sha256", "status"}
    if (not isinstance(data, dict) or not required <= set(data)
            or data["version"] != 1 or data["run_id"] != run_id
            or data["base_sha"] != baseline
            or data["task_id"] != task["id"]
            or data["task_sha256"] != plan_hash(task)):
        raise ContractError("sandbox receipt is not bound to this approved task")
    if data["status"] == "HOLD":
        if set(data) != required | {"error_code"}:
            raise ContractError("malformed sandbox hold receipt")
        return data
    if (data["status"] != "VERIFIED" or
            set(data) != required | {"files", "guest_commit"} or
            not isinstance(data["guest_commit"], str)
            or not SHA40.fullmatch(data["guest_commit"])):
        raise ContractError("sandbox receipt did not prove guest verification")
    files = data["files"]
    if not isinstance(files, list) or not 1 <= len(files) <= 16:
        raise ContractError("sandbox output file scope invalid")
    approved = set(task["files"])
    seen = set()
    size_left = MAX_CODE
    decoded = {}
    for item in files:
        if not isinstance(item, dict) or set(item) != {"path", "sha256", "data_b64"}:
            raise ContractError("sandbox file receipt is malformed")
        name = item["path"]
        if (not isinstance(name, str) or safe_path(name) not in approved
                or name.casefold() in seen):
            raise ContractError("sandbox file outside approved allowlist")
        seen.add(name.casefold())
        value, digest = item["data_b64"], item["sha256"]
        if value is None and digest is None:
            decoded[name] = None
            continue
        if (not isinstance(value, str) or not isinstance(digest, str)
                or not SHA256.fullmatch(digest)):
            raise ContractError("sandbox file content invalid")
        try:
            content = base64.b64decode(value, validate=True)
        except (ValueError, base64.binascii.Error) as exc:
            raise ContractError("sandbox file base64 invalid") from exc
        size_left -= len(content)
        if size_left < 0 or hashlib.sha256(content).hexdigest() != digest:
            raise ContractError("sandbox file bytes exceed budget or hash differs")
        decoded[name] = content
    data["decoded_files"] = decoded
    return data


def _reconcile(factory: Factory, task: dict, result: dict, baseline: str) -> dict:
    """Never promote a guest-writable receipt as independent acceptance.

    The model and approved project tests run as the SAME Windows Sandbox
    account that can write receipt.json. Matching run IDs, hashes, paths and
    a claimed guest Git SHA authenticate the *payload*, not its test verdict.
    Until the reviewer has a separately enforced OS identity/attestation
    boundary, the host must never import/commit/promote these bytes.
    """
    raise ContractError("SANDBOX_RECEIPT_UNATTESTED")



def run_sandbox_one(factory: Factory, task: dict, bundle: Path, manifest_sha: str,
                    execute: bool, timeout: int = 1800) -> dict:
    tid = task["id"]
    if not execute:
        return {"id": tid, "status": "DRY_RUN", "backend": "WindowsSandbox",
                "real_isolation_tested": False}
    _sandbox_binary()  # Unsupported Windows edition must not consume a task.
    _read_bundle(bundle, manifest_sha)  # No executable auto-download or installs.
    state = factory.status()[tid]
    if state == "PREPARED":
        # Historical PREPARED entries may have been created from forged
        # guest-controlled receipts. Do not silently complete that promotion.
        factory._set(tid, "HOLD", "SANDBOX_UNATTESTED_PREPARED")
        return {"id": tid, "status": "HOLD", "verified": False,
                "reason": "SANDBOX_UNATTESTED_PREPARED"}
    if state == "QUEUED":
        # Reserve two bounded model calls for potential one-fix review.
        if not factory._reserve_model_call(tid, "SANDBOX_CODING"):
            return {"id": tid, "status": "BUDGET_WAIT"}
        if not factory._reserve_model_call(tid, "SANDBOX_POSSIBLE_FIX"):
            return {"id": tid, "status": "BUDGET_WAIT"}
        run_id, root, baseline = _prepare(factory, task, bundle, manifest_sha)
        factory._set(tid, "CODING", "SANDBOX_RUN:" + run_id)
        try:
            # Launch the trusted Windows System32 binary directly, rather
            # than trusting a user-overridable .wsb file association.
            subprocess.Popen(
                [str(_sandbox_binary()), str(root / "launch.wsb")],
                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL, shell=False, cwd=root)
        except OSError as exc:
            factory._set(tid, "HOLD", "SANDBOX_LAUNCH_FAILED")
            return {"id": tid, "status": "HOLD", "reason": type(exc).__name__}
    elif state == "CODING":
        row = factory.db.execute(
            "SELECT evidence FROM runs WHERE id=?", (tid,)).fetchone()
        evidence = row[0] if row else ""
        if not evidence.startswith("SANDBOX_RUN:") or not RUN.fullmatch(evidence[12:]):
            raise ContractError("interrupted coding lacks a pinned sandbox run")
        run_id = evidence[len("SANDBOX_RUN:"):]
        root = factory.state / "sandbox-runs" / run_id
        request_path = _no_reparse(root / "input" / "request.json")
        if not request_path.is_file():
            raise ContractError("interrupted sandbox request missing")
        request = json.loads(request_path.read_text(encoding="utf-8"))
        baseline = request["base_sha"]
        if (request.get("task_sha256") != plan_hash(task) or
                request.get("run_id") != run_id or not SHA40.fullmatch(baseline)):
            raise ContractError("interrupted sandbox request pin differs")
    else:
        raise ContractError("sandbox task state cannot be independently resumed")
    deadline = time.monotonic() + timeout
    reply = None
    while time.monotonic() < deadline:
        reply = _read_receipt(root, run_id, task, baseline)
        if reply is not None:
            break
        time.sleep(1)
    if reply is None:
        # Sandbox could still be running. Never start a duplicate model call.
        return {"id": tid, "status": "WAITING_RECEIPT", "verified": False,
                "reason": "sandbox result absent; manual inspection required"}
    if reply["status"] != "VERIFIED":
        factory._set(tid, "HOLD", "SANDBOX_GUEST_HOLD:" + reply["error_code"])
        return {"id": tid, "status": "HOLD",
                "reason": "SANDBOX_GUEST_HOLD"}
    # A malicious coding process can read request.json and write an entirely
    # plausible receipt.json without ever executing acceptance commands.
    # Preserve the receipt for offline inspection, but never turn it into a
    # local VERIFIED Git commit or advance dependent tasks.
    factory._set(tid, "HOLD", "SANDBOX_RECEIPT_UNATTESTED")
    return {"id": tid, "status": "HOLD", "verified": False,
            "guest_status": "CLAIMED_VERIFIED",
            "reason": "SANDBOX_RECEIPT_UNATTESTED"}
    # Any future promotion must first introduce an independently enforced
    # reviewer identity and a host-verifiable approval proof, with tests.


def run_sandbox_queue(repo: Path, plan: Path, state: Path, bundle: Path,
                      manifest_sha: str, model: str, maximum: int,
                      execute: bool) -> tuple[list[dict], dict]:
    if not 1 <= maximum <= 100:
        raise ContractError("sandbox queue maximum 1..100")
    # Optional mode. Ordinary RUN_QUEUE/RUN_BATCH remain unchanged.
    factory = Factory(repo, plan, state, model=model)
    try:
        from .core import single_worker_lock
        results: list[dict] = []
        with single_worker_lock(factory.state):
            for _ in range(maximum):
                if (factory.state / "STOP.REQUESTED").exists():
                    results.append({"status": "STOP_REQUESTED"})
                    break
                task = factory.next_task()
                if task is None:
                    break
                result = run_sandbox_one(
                    factory, task, bundle, manifest_sha, execute)
                results.append(result)
                if result["status"] not in ("VERIFIED", "HOLD"):
                    break
        return results, factory.status()
    finally:
        factory.close()
