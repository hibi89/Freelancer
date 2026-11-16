"""Windows Sandbox coding, AppContainer acceptance and host-only Git promotion."""
from __future__ import annotations

from contextlib import ExitStack
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import secrets
import subprocess
import tempfile
import time
import xml.etree.ElementTree as ET
import zipfile

from .core import ContractError, Factory, git, plan_hash, single_worker_lock
from .batch import _event
from .sandbox_payload import (
    BINARIES, MAX_ARCHIVE, MAX_RECEIPT, RUN_ID, SHA40, SHA256,
    decode_files, extract_snapshot, hex_sha, no_reparse, portable_path, read_json, snapshot_entries, write_json,
)
from .sandbox_review import verify_candidate, validate_acceptance
from .windows_review_process import run_restricted, single_sandbox_slot, system_directory

MAX_MANIFEST = 4 * 1024 * 1024
BACKEND = "windows-sandbox-v2"
ENGINE = (
    "axdev/__init__.py", "axdev/core.py", "axdev/repo_trust.py",
    "axdev/batch.py", "axdev/opencode_guard.py", "axdev/sandbox_payload.py",
    "config/opencode-local-only.json", ".opencode/skills/ax-coding/SKILL.md",
    "scripts/sandbox_guest.py",
)


def bundle_inventory(bundle: Path) -> dict[str, str]:
    bundle = no_reparse(bundle)
    if not bundle.is_dir():
        raise ContractError("offline bundle directory missing")
    top = {"python", "git", "ollama", "opencode", "models", "ruff", "manifest.json"}
    if any(item.name not in top for item in bundle.iterdir()):
        raise ContractError("offline bundle contains an unexpected root entry")
    files = {}
    for directory, folders, names in os.walk(bundle, followlinks=False, onerror=_walk_error):
        for name in folders:
            no_reparse(Path(directory) / name)
        for name in names:
            file = no_reparse(Path(directory) / name)
            relative = file.relative_to(bundle).as_posix()
            if relative == "manifest.json":
                continue
            if len(files) >= 20000 or not file.is_file():
                raise ContractError("invalid or oversized offline bundle inventory")
            files[relative] = hex_sha(file)
    if not set(BINARIES) <= files.keys() or not any(p.startswith("models/") for p in files):
        raise ContractError("offline binaries or model data are missing")
    return files


def _walk_error(exc):
    raise exc


def _read_bundle(bundle: Path, expected_sha: str) -> dict:
    if not SHA256.fullmatch(expected_sha):
        raise ContractError("offline bundle manifest SHA256 must be owner-pinned")
    data, digest = read_json(bundle / "manifest.json", MAX_MANIFEST)
    if digest != expected_sha:
        raise ContractError("offline runtime bundle hash mismatched approved pin")
    if data.get("version") != 2 or data.get("files") != bundle_inventory(bundle):
        raise ContractError("offline runtime files differ from the approved manifest")
    return data


def _sandbox_binary() -> Path:
    executable = no_reparse(system_directory() / "WindowsSandbox.exe")
    if not executable.is_file():
        raise ContractError("Windows Sandbox unavailable; a supported enabled host is required")
    return executable


def _sandbox_running() -> bool:
    # Windows 10 has one active Sandbox per user. Wait for its host client to
    # exit before opening another coding guest or advancing the task.
    client = system_directory() / "tasklist.exe"
    result = subprocess.run([str(client), "/fo", "csv", "/nh"], check=True,
                            stdin=subprocess.DEVNULL, capture_output=True, timeout=15)
    clients = (b'"windowssandbox.exe"', b'"windowssandboxclient.exe"',
               b'"windowssandboxremotesession.exe"')
    return any(line.lower().startswith(clients) for line in result.stdout.splitlines())


def _git_data(repo: Path, *args: str, index: Path | None = None, data: bytes | None = None,
              limit: int = MAX_ARCHIVE) -> bytes:
    # No hooks, filters, checked-out project code or Git replace objects.
    environment = {k: v for k, v in os.environ.items() if not k.upper().startswith("GIT_")}
    if index is not None:
        environment["GIT_INDEX_FILE"] = str(index)
    options = {"stdin": subprocess.DEVNULL} if data is None else {"input": data}
    result = subprocess.run(
        ["git", "--no-replace-objects", "-c", "commit.gpgsign=false", *args],
        cwd=repo, env=environment, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        check=False, timeout=60, **options)
    if result.returncode or len(result.stdout) > limit:
        raise ContractError("sandbox Git object operation failed")
    return result.stdout


def _inventory(repo: Path, ref: str) -> dict[str, tuple[str, str]]:
    result = _git_data(repo, "ls-tree", "-r", "-z", ref, limit=8 * 1024 * 1024)
    tracked = {}
    for entry in result.split(b"\0")[:-1]:
        metadata, raw = entry.split(b"\t", 1)
        mode, kind, digest = metadata.decode("ascii").split()
        if kind != "blob" or mode not in ("100644", "100755") or not SHA40.fullmatch(digest):
            raise ContractError("sandbox tracked snapshot contains a symlink or non-file entry")
        tracked[raw.decode("utf-8")] = (mode, digest)
    return tracked


def _archive_verified_base(repo: Path, ref: str, path: Path) -> str:
    tracked = _inventory(repo, ref)
    if not 1 <= len(tracked) <= 6000:
        raise ContractError("sandbox snapshot entry count invalid")
    # git archive can apply export-ignore, export-subst and checkout EOL
    # conversion. Read bounded blob bytes directly from Git objects instead.
    ids = list(dict.fromkeys(digest for _, digest in tracked.values()))
    query = ("\n".join(ids) + "\n").encode()
    metadata = _git_data(repo, "cat-file", "--batch-check", data=query, limit=1024 * 1024)
    sizes = {}
    for row in metadata.decode("ascii").splitlines():
        digest, kind, size = row.split()
        if kind != "blob" or not SHA40.fullmatch(digest) or not size.isdecimal():
            raise ContractError("sandbox Git object inventory invalid")
        sizes[digest] = int(size)
    if set(sizes) != set(ids) or sum(sizes[d] for _, d in tracked.values()) > MAX_ARCHIVE:
        raise ContractError("sandbox snapshot exceeds source byte limit")
    stream = io.BytesIO(_git_data(repo, "cat-file", "--batch", data=query,
                                  limit=MAX_ARCHIVE + len(metadata) + len(ids)))
    blobs = {}
    for digest in ids:
        size = sizes[digest]
        if stream.readline() != f"{digest} blob {size}\n".encode():
            raise ContractError("sandbox Git object header differs")
        raw = stream.read(size)
        if (stream.read(1) != b"\n" or
                hashlib.sha1(f"blob {size}\0".encode() + raw).hexdigest() != digest):
            raise ContractError("sandbox snapshot differs from the pinned Git blob")
        blobs[digest] = raw
    with zipfile.ZipFile(path, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, (_, digest) in tracked.items():
            archive.writestr(portable_path(name), blobs[digest])
        list(snapshot_entries(archive))
    if path.stat().st_size > MAX_ARCHIVE:
        raise ContractError("sandbox snapshot file exceeds size limit")
    return hex_sha(path)


def _candidate_tree(factory: Factory, baseline: str, candidate: Path, task: dict) -> str:
    sealed, _ = read_json(candidate, MAX_RECEIPT)
    files = decode_files(sealed.get("files"), set(task["files"]))
    tracked = _inventory(factory.repo, baseline)
    with tempfile.TemporaryDirectory(prefix="index-", dir=candidate.parent) as directory:
        index = Path(directory) / "index"
        _git_data(factory.repo, "read-tree", baseline, index=index)
        for name, content in files.items():
            if content is None:
                if name not in tracked:
                    raise ContractError("sandbox candidate deletes a nonexistent file")
                _git_data(factory.repo, "update-index", "--force-remove", "--", name, index=index)
            else:
                blob = _git_data(factory.repo, "hash-object", "-w", "--stdin", data=content).decode().strip()
                mode = tracked.get(name, ("100644", ""))[0]
                _git_data(factory.repo, "update-index", "--add", "--cacheinfo",
                          mode, blob, name, index=index)
        tree = _git_data(factory.repo, "write-tree", index=index).decode().strip()
    after = _inventory(factory.repo, tree)
    changed = {p for p in tracked.keys() | after.keys() if tracked.get(p) != after.get(p)}
    if not changed or not changed <= files.keys():
        raise ContractError("sandbox Git tree has no change or contains unapproved changes")
    return tree


def _wsb(input_dir: Path, bundle: Path, outbox: Path) -> bytes:
    root = ET.Element("Configuration")
    for name in ("Networking", "VGpu", "ClipboardRedirection",
                 "PrinterRedirection", "AudioInput", "VideoInput"):
        ET.SubElement(root, name).text = "Disable"
    mappings = ET.SubElement(root, "MappedFolders")
    for host, guest, readonly in (
        (input_dir, r"C:\AXDEV_INPUT", True),
        (bundle, r"C:\AXDEV_BUNDLE", True),
        (outbox, r"C:\AXDEV_OUTBOX", False),
    ):
        mapping = ET.SubElement(mappings, "MappedFolder")
        ET.SubElement(mapping, "HostFolder").text = str(no_reparse(host))
        ET.SubElement(mapping, "SandboxFolder").text = guest
        ET.SubElement(mapping, "ReadOnly").text = str(readonly).lower()
    ET.SubElement(ET.SubElement(root, "LogonCommand"), "Command").text = (
        r"powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass "
        r"-File C:\AXDEV_INPUT\bootstrap.ps1")
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def _bootstrap() -> str:
    return r"""
$ErrorActionPreference = 'Stop'
$env:PATH = 'C:\AXDEV_BUNDLE\python;C:\AXDEV_BUNDLE\git\cmd;C:\AXDEV_BUNDLE\ollama;C:\AXDEV_BUNDLE\opencode;' + $env:PATH
$env:PYTHONPATH = 'C:\AXDEV_INPUT\engine'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:HOME = $env:USERPROFILE = 'C:\AXDEV_RUN\home'
$env:APPDATA = 'C:\AXDEV_RUN\home\AppData\Roaming'
$env:LOCALAPPDATA = 'C:\AXDEV_RUN\home\AppData\Local'
New-Item -ItemType Directory -Force $env:HOME | Out-Null
try {
    & 'C:\AXDEV_BUNDLE\python\python.exe' 'C:\AXDEV_INPUT\engine\scripts\sandbox_guest.py'
} finally {
    & 'C:\Windows\System32\shutdown.exe' /s /t 0
}
"""


def _prepare(factory: Factory, task: dict, bundle: Path, bundle_sha: str,
             prior: Path | None = None) -> dict:
    baseline = git(factory.repo, "rev-parse", factory.integration_ref)
    if not SHA40.fullmatch(baseline):
        raise ContractError("unverified integration reference")
    run_id = secrets.token_hex(16)
    root = no_reparse(factory.state / "sandbox-runs" / run_id)
    input_dir, outbox = root / "input", root / "outbox"
    input_dir.mkdir(parents=True)
    outbox.mkdir()
    digest = _archive_verified_base(factory.repo, baseline, input_dir / "source.zip")
    source = Path(__file__).resolve().parent.parent
    for relative in ENGINE:
        origin = no_reparse(source / relative)
        target = input_dir / "engine" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(origin.read_bytes())
    initial_sha = None
    if prior is not None:
        initial, _ = read_json(prior, MAX_RECEIPT)
        initial_sha = write_json(input_dir / "initial.json", {"files": initial["files"]})
    coding_task = {key: task[key] for key in ("id", "goal", "files")}
    request = {"version": 2, "run_id": run_id, "base_sha": baseline,
               "task": coding_task, "task_sha256": plan_hash(task),
               "archive_sha256": digest, "bundle_sha256": bundle_sha,
               "model": factory.model, "initial_sha256": initial_sha}
    request_sha = write_json(input_dir / "request.json", request)
    (input_dir / "bootstrap.ps1").write_text(_bootstrap(), encoding="utf-8")
    (root / "launch.wsb").write_bytes(_wsb(input_dir, bundle, outbox))
    return {"backend": BACKEND, "run_id": run_id, "base_sha": baseline,
            "request_sha256": request_sha, "bundle_sha256": bundle_sha}


def _read_receipt(root: Path, run_id: str, task: dict, baseline: str) -> dict | None:
    path = no_reparse(root / "outbox" / "receipt.json")
    if not path.exists():
        return None
    data, _ = read_json(path, MAX_RECEIPT)
    keys = {"version", "run_id", "base_sha", "task_id", "task_sha256", "status"}
    if (data.get("version") != 2 or data.get("run_id") != run_id or
            data.get("base_sha") != baseline or data.get("task_id") != task["id"] or
            data.get("task_sha256") != plan_hash(task)):
        raise ContractError("sandbox candidate is not bound to the approved run and contract")
    if data.get("status") == "HOLD" and set(data) == keys:
        return data
    if data.get("status") != "CANDIDATE" or set(data) != keys | {"files"}:
        raise ContractError("sandbox accepts candidate bytes only")
    decode_files(data["files"], set(task["files"]))
    return data


def _read_state(factory: Factory, tid: str, bundle_sha: str) -> tuple[dict, Path]:
    row = factory.db.execute("SELECT evidence FROM runs WHERE id=?", (tid,)).fetchone()
    try:
        record = json.loads(row[0])
        if (record["backend"] != BACKEND or not RUN_ID.fullmatch(record["run_id"])
                or not SHA40.fullmatch(record["base_sha"]) or record["bundle_sha256"] != bundle_sha):
            raise ValueError
    except (ValueError, TypeError, KeyError, IndexError) as exc:
        raise ContractError("SANDBOX_UNATTESTED_LEGACY_STATE") from exc
    return record, no_reparse(factory.state / "sandbox-runs" / record["run_id"])


def _request_matches(root: Path, record: dict, task: dict) -> None:
    request, digest = read_json(root / "input" / "request.json", 65536)
    if (digest != record["request_sha256"] or request["task_sha256"] != plan_hash(task)
            or request["run_id"] != record["run_id"] or request["base_sha"] != record["base_sha"]
            or request["bundle_sha256"] != record["bundle_sha256"]):
        raise ContractError("sandbox request no longer matches host state")


def _hold(factory: Factory, tid: str, reason: str) -> dict:
    factory._set(tid, "HOLD", reason)
    return {"id": tid, "status": "HOLD", "verified": False, "reason": reason}


def _launch(factory: Factory, task: dict, bundle: Path, bundle_sha: str,
            executable: Path, prior: Path | None = None) -> tuple[dict, Path, object] | dict:
    tid = task["id"]
    if _sandbox_running():
        return {"id": tid, "status": "WAITING_SANDBOX_EXIT"}
    if not factory._reserve_model_call(tid, "SANDBOX_FIX_ONCE" if prior else "SANDBOX_CODING"):
        return {"id": tid, "status": "BUDGET_WAIT"}
    record = _prepare(factory, task, bundle, bundle_sha, prior)
    root = factory.state / "sandbox-runs" / record["run_id"]
    if prior is not None:
        factory.db.execute("UPDATE runs SET attempts=attempts+1 WHERE id=?", (tid,))
    factory._set(tid, "CODING", json.dumps(record))
    return record, root, _start_guest(executable, root)


def _start_guest(executable: Path, root: Path) -> subprocess.Popen:
    return subprocess.Popen([str(executable), str(root / "launch.wsb")],
                            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL, shell=False, cwd=root)


def _wait_candidate(task: dict, record: dict, root: Path, process, timeout: int) -> dict | None:
    _request_matches(root, record, task)
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if (process is None or process.poll() is not None) and not _sandbox_running():
            return _read_receipt(root, record["run_id"], task, record["base_sha"])
        time.sleep(2)
    return None


def _host_proof(task: dict, record: dict, root: Path, commit: str) -> dict:
    proof, digest = read_json(root / "acceptance.json", 16384)
    expected = {"backend": BACKEND, "task_sha256": plan_hash(task), "run_id": record["run_id"],
                "base_sha": record.get("review_base_sha"), "commit": commit,
                "candidate_sha256": record.get("candidate_sha256")}
    if (not SHA40.fullmatch(commit) or digest != record.get("proof_sha256")
            or any(not isinstance(v, str) or proof.get(k) != v for k, v in expected.items())
            or proof.get("project_checks") != len(task["checks"])
            or not task.get("acceptance") or proof.get("independent_probes") != len(task["acceptance"])):
        raise ContractError("host acceptance evidence is absent or differs")
    return proof


def _promote(factory: Factory, task: dict, record: dict, root: Path) -> dict:
    tid = task["id"]
    row = factory.db.execute("SELECT commit_sha FROM runs WHERE id=?", (tid,)).fetchone()
    proof = _host_proof(task, record, root, row[0])
    if (_git_data(factory.repo, "rev-parse", row[0] + "^{tree}").decode().strip() != proof["tree"]
            or _git_data(factory.repo, "rev-parse", row[0] + "^").decode().strip() != proof["base_sha"]):
        raise ContractError("host acceptance commit does not match its reviewed tree and base")
    return factory._promote_prepared(tid, evidence=json.dumps(record))


def validate_history(repo: Path, state: Path, db, tasks: list[dict], ref: str,
                     *, allow_prepared: bool) -> None:
    """Fail if SQLite status, host proofs and the exact first-parent chain diverge."""
    row = db.execute("SELECT value FROM meta WHERE key='base_sha'").fetchone()
    if not row or not SHA40.fullmatch(row[0]):
        raise ContractError("sandbox history baseline invalid")
    base = row[0]
    head = _git_data(repo, "rev-parse", "--verify", ref).decode().strip()
    chain = _git_data(repo, "log", "--first-parent", "--reverse", "--format=%H %T %P",
                      f"{base}..{head}", limit=32768).decode().splitlines()
    approved = {task["id"]: task for task in tasks}
    proofs = {}
    for tid, spec, status, evidence, commit in db.execute(
            "SELECT id,spec,status,evidence,commit_sha FROM runs WHERE status IN ('VERIFIED','PREPARED')"):
        if status == "PREPARED" and (not allow_prepared or commit != head):
            continue
        task = approved.get(tid)
        record = json.loads(evidence)
        run_id = record.get("run_id") if isinstance(record, dict) else None
        if (not task or spec != plan_hash(task) or not isinstance(run_id, str)
                or not RUN_ID.fullmatch(run_id) or commit in proofs or record.get("backend") != BACKEND):
            raise ContractError("sandbox history task or evidence identifiers differ")
        proofs[commit] = _host_proof(task, record, state / "sandbox-runs" / run_id, commit)
    for entry in chain:
        fields = entry.split()
        if len(fields) != 3:
            raise ContractError("sandbox integration history is not linear")
        commit, tree, parent = fields
        proof = proofs.pop(commit, None)
        if not proof or parent != base or tree != proof["tree"] or parent != proof["base_sha"]:
            raise ContractError("sandbox integration history lacks matching host proof")
        base = commit
    if proofs or base != head:
        raise ContractError("sandbox integration and checkpoint history differ")


def _review(factory: Factory, task: dict, bundle: Path, record: dict, root: Path) -> dict:
    _, digest = read_json(root / "candidate.json", MAX_RECEIPT)
    if digest != record["candidate_sha256"]:
        raise ContractError("host-sealed candidate changed")
    base = git(factory.repo, "rev-parse", factory.integration_ref)
    starting_base = record["base_sha"]
    if base != starting_base:
        _git_data(factory.repo, "merge-base", "--is-ancestor", starting_base, base)
        previous, current = _inventory(factory.repo, starting_base), _inventory(factory.repo, base)
        if any(previous.get(name) != current.get(name) for name in task["files"]):
            raise ContractError("approved paths changed since sandbox coding")
    tree = _candidate_tree(factory, base, root / "candidate.json", task)
    with tempfile.TemporaryDirectory(prefix="snapshot-", dir=root) as scratch:
        archive = Path(scratch) / "source.zip"
        _archive_verified_base(factory.repo, tree, archive)
        verdict = verify_candidate(task, archive, bundle, root)
        if verdict["ok"]:
            adapters = _review_adapters(factory, task, bundle, root, archive)
            if adapters.get("status") == "BUDGET_WAIT" or adapters.get("ok") is False:
                return adapters
            verdict.update(adapters)
    if not verdict["ok"]:
        return verdict
    if git(factory.repo, "rev-parse", factory.integration_ref) != base:
        raise ContractError("sandbox integration changed during review")
    commit = _git_data(factory.repo, "commit-tree", tree, "-p", base,
                       "-m", f"axdev: {task['id']} independently reviewed local change").decode().strip()
    proof = {"backend": BACKEND, "run_id": record["run_id"], "base_sha": base,
             "candidate_sha256": digest, "tree": tree, "task_sha256": plan_hash(task),
             "commit": commit, "project_checks": verdict["project_checks"],
             "independent_probes": verdict["independent_probes"],
             "semantic_review": verdict.get("semantic_review"), "eai_receipt_sha256": verdict.get("eai_receipt_sha256")}
    record["review_base_sha"] = base
    record["proof_sha256"] = write_json(root / "acceptance.json", proof)
    factory._set(task["id"], "PREPARED", json.dumps(record), commit)
    return _promote(factory, task, record, root)


def run_isolated_eai(repo: Path, pin: str, goal: Path, approved: Path,
                     bundle: Path, parent: Path, timeout: int) -> tuple[int, bytes]:
    with tempfile.TemporaryDirectory(prefix="eai-", dir=parent) as directory:
        stage = Path(directory)
        snapshot = stage / "eai.zip"
        _archive_verified_base(repo, pin, snapshot)
        project = stage / "eai-project"
        extract_snapshot(snapshot, project)
        inputs = stage / "approved-inputs"
        remaining = 8 * 1024 * 1024
        count = 0
        for current, folders, files in os.walk(approved, followlinks=False, onerror=_walk_error):
            for name in folders:
                no_reparse(Path(current) / name)
            for name in files:
                source = no_reparse(Path(current) / name)
                count += 1
                remaining -= source.stat().st_size
                if count > 256 or remaining < 0 or not source.is_file():
                    raise ContractError("EAI approved input directory exceeds isolated copy bounds")
                relative = portable_path(source.relative_to(approved).as_posix())
                output = inputs / relative
                output.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, output)
        copied_goal = inputs / goal.relative_to(approved)
        if hex_sha(goal) != hex_sha(copied_goal):
            raise ContractError("EAI input differs from isolated copy")
        runtime = stage / "python"
        shutil.copytree(bundle / "python", runtime)
        launch = ("import runpy, sys; sys.path.append(sys.argv.pop(1)); "
                  "runpy.run_module('eai', run_name='__main__')")
        return run_restricted([str(runtime / "python.exe"), "-I", "-S", "-B", "-X", "utf8", "-c",
                               launch, str(project), "solve-goal", str(copied_goal), "--json"],
                              stage, project, timeout)


def _review_adapters(factory: Factory, task: dict, bundle: Path, root: Path, archive: Path) -> dict:
    tid = task["id"]
    evidence = {}
    if tid in factory.eai_tasks:
        from .eai_adapter import run_eai_goal
        rule = factory.eai_tasks[tid]
        approved = no_reparse(Path(rule["approved_directory"])).resolve(strict=True)
        def isolated(repo, pin, goal, timeout):
            return run_isolated_eai(repo, pin, goal, approved, bundle, root, timeout)
        receipt = run_eai_goal(Path(rule["eai_repo"]), rule["expected_sha"], Path(rule["goal"]),
                               approved, runner=isolated)
        if not receipt["independent_receipt_accepted"]:
            return {"ok": False, "reason": "EAI_RECEIPT_DISAGREEMENT"}
        factory.db.execute("INSERT OR IGNORE INTO eai_review_receipts VALUES (?,?,?,?,?)",
                           (tid, plan_hash(task), receipt["goal_sha256"],
                            receipt["receipt_sha256"], receipt["status"]))
        factory.db.commit()
        evidence["eai_receipt_sha256"] = receipt["receipt_sha256"]
    if factory.semantic_review_enabled:
        from .semantic_review import require_installed_model, review_semantics
        require_installed_model(factory.model)
        if not factory._reserve_model_call(tid, "SANDBOX_SEMANTIC_REVIEW"):
            return {"status": "BUDGET_WAIT", "id": tid}
        with tempfile.TemporaryDirectory(prefix="semantic-", dir=root) as directory:
            source = Path(directory) / "candidate"
            extract_snapshot(archive, source)
            record, _ = read_json(root / "candidate.json", MAX_RECEIPT)
            changed = set(decode_files(record["files"], set(task["files"])))
            approved, reason = review_semantics(task, source, changed, factory.model)
        if not approved:
            return {"ok": False, "reason": reason}
        evidence["semantic_review"] = reason
    return evidence


def run_sandbox_one(factory: Factory, task: dict, bundle: Path, manifest_sha: str,
                    execute: bool, timeout: int = 1800, executable: Path | None = None,
                    stage_only: bool = False) -> dict:
    tid = task["id"]
    if not execute:
        return {"id": tid, "status": "DRY_RUN", "backend": BACKEND}
    executable = executable or _sandbox_binary()
    if not task.get("acceptance"):
        return _hold(factory, tid, "INDEPENDENT_ACCEPTANCE_MISSING")
    validate_acceptance(task["acceptance"])
    # Existing baseline tests are a protected witness. New tests are permitted
    # as evidence but cannot replace the host comparisons.
    if any(cmd[2:4] == ["unittest", "discover"] for cmd in task["checks"]):
        baseline = git(factory.repo, "rev-parse", factory.integration_ref)
        protected = {p.casefold() for p in _inventory(factory.repo, baseline)
                     if p.casefold().startswith("tests/")}
        if any(p.casefold() in protected or p.casefold() == "tests" for p in task["files"]):
            return _hold(factory, tid, "APPROVED_SCOPE_OVERLAPS_PROTECTED_TESTS")
    try:
        state = factory.status()[tid]
        pending = _launch(factory, task, bundle, manifest_sha, executable) if state == "QUEUED" else None
        if isinstance(pending, dict):
            return pending
        if pending is None:
            record, root = _read_state(factory, tid, manifest_sha)
            process = None
        else:
            record, root, process = pending
            state = "CODING"
        if state == "PREPARED":
            return _promote(factory, task, record, root)
        while True:
            if state == "CODING":
                reply = _wait_candidate(task, record, root, process, timeout)
                if reply is None:
                    if (process is not None and process.poll() is None) or _sandbox_running():
                        return {"id": tid, "status": "WAITING_RECEIPT"}
                    return _hold(factory, tid, "SANDBOX_EXITED_WITHOUT_CANDIDATE")
                if reply["status"] == "HOLD":
                    return _hold(factory, tid, "SANDBOX_CODER_FAILED")
                record["candidate_sha256"] = write_json(root / "candidate.json", reply)
                factory._set(tid, "REVIEW", json.dumps(record))
            elif state != "REVIEW":
                return _hold(factory, tid, "SANDBOX_UNATTESTED_LEGACY_STATE")
            if stage_only:
                return {"id": tid, "status": "IMPLEMENTED"}
            result = _review(factory, task, bundle, record, root)
            if result.get("status") in ("VERIFIED", "BUDGET_WAIT"):
                return result
            attempts = factory.db.execute("SELECT attempts FROM runs WHERE id=?", (tid,)).fetchone()[0]
            if attempts >= 1:
                return _hold(factory, tid, result["reason"])
            pending = _launch(factory, task, bundle, manifest_sha, executable, root / "candidate.json")
            if isinstance(pending, dict):
                return pending
            record, root, process = pending
            state = "CODING"
    except ContractError as exc:
        if factory.status()[tid] == "PREPARED":
            # Keep the journal when this call prepared it or Git has adopted
            # its commit. Dropping the proof would leave Git ahead of SQLite.
            if state != "PREPARED":
                raise
            prepared = factory.db.execute("SELECT commit_sha FROM runs WHERE id=?", (tid,)).fetchone()[0]
            baseline = factory.db.execute("SELECT value FROM meta WHERE key='base_sha'").fetchone()[0]
            if prepared != baseline and git(factory.repo, "rev-parse", factory.integration_ref) == prepared:
                raise
        return _hold(factory, tid, str(exc))
    except (OSError, RuntimeError, ValueError, subprocess.SubprocessError, zipfile.BadZipFile) as exc:
        if factory.status()[tid] == "PREPARED":
            raise
        return _hold(factory, tid, "SANDBOX_ERROR_" + type(exc).__name__)


def run_sandbox_queue(repo: Path, plan: Path, state: Path, bundle: Path,
                      manifest_sha: str, model: str, maximum: int, execute: bool,
                      *, plan_sha256: str, daily_budget: int | None = None,
                      eai_policy: Path | None = None, semantic_review: bool = False,
                      implementation_batch: bool = False) -> tuple[list[dict], dict]:
    if not 1 <= maximum <= 100:
        raise ContractError("sandbox queue maximum 1..100")
    if not plan_sha256 or not SHA256.fullmatch(plan_sha256) or hex_sha(no_reparse(plan)) != plan_sha256:
        raise ContractError("local approved plan SHA256 differs")
    repo, state, bundle = (no_reparse(p).resolve() for p in (repo, state, bundle))
    for left, right in ((repo, state), (repo, bundle), (state, bundle), (plan.resolve(), bundle)):
        if left == right or left in right.parents or right in left.parents:
            raise ContractError("sandbox bundle, project and state require separate directories")
    executable = _sandbox_binary() if execute else None
    with ExitStack() as stack:
        if execute:
            stack.enter_context(single_sandbox_slot())
            _read_bundle(bundle, manifest_sha)
        stack.enter_context(single_worker_lock(state))
        factory = Factory(repo, plan, state, model=model, max_daily_model_calls=daily_budget,
                          eai_policy=eai_policy, semantic_review=semantic_review)
        stack.callback(factory.close)
        results = []
        if execute:
            factory.require_isolated_state(BACKEND, plan_sha256)
            validate_history(repo, state, factory.db, factory.tasks, factory.integration_ref,
                             allow_prepared=True)
        while len(results) < maximum:
            if (factory.state / "STOP.REQUESTED").exists():
                results.append({"status": "STOP_REQUESTED"})
                break
            task = factory.next_task()
            if task is None:
                break
            if execute and implementation_batch and factory.status()[task["id"]] == "QUEUED":
                staged = _stage_batch(factory, bundle, manifest_sha, executable, maximum - len(results))
                if staged and staged[-1]["status"] not in ("IMPLEMENTED", "HOLD"):
                    results.extend(staged)
                    break
                results.extend(r for r in staged if r["status"] == "HOLD")
                if len(results) >= maximum or (factory.state / "STOP.REQUESTED").exists():
                    break
                task = factory.next_task()
                if task is None:
                    break
            began = time.monotonic()
            result = run_sandbox_one(factory, task, bundle, manifest_sha, execute, executable=executable)
            if execute:
                _event(factory, result, time.monotonic() - began)
            results.append(result)
            if result["status"] not in ("VERIFIED", "HOLD"):
                break
        return results, factory.status()


def _stage_batch(factory: Factory, bundle: Path, manifest_sha: str, executable: Path,
                 maximum: int) -> list[dict]:
    states = factory.status()
    results = []
    used = set()
    for task in factory.tasks:
        if len(results) >= maximum or (factory.state / "STOP.REQUESTED").exists():
            break
        paths = {name.casefold() for name in task["files"]}
        if (states[task["id"]] != "QUEUED" or used & paths
                or any(states[key] != "VERIFIED" for key in task.get("depends_on", []))):
            continue
        began = time.monotonic()
        result = run_sandbox_one(factory, task, bundle, manifest_sha, True,
                                 executable=executable, stage_only=True)
        _event(factory, result, time.monotonic() - began)
        results.append(result)
        if result["status"] not in ("IMPLEMENTED", "HOLD"):
            break
        used.update(paths)
    return results
