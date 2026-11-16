"""Optional implementation-first batch with independent post-batch acceptance.

No unverified commit can become the next trusted integration base. All
candidate worktrees remain local; no network or PR is used here.
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone

from .core import ContractError, git, call, single_worker_lock


PENDING = frozenset(("CODING", "IMPLEMENTED", "REVIEW", "PREPARED"))


def _event(factory, result: dict, elapsed: float) -> None:
    if result.get("status") not in ("IMPLEMENTED", "VERIFIED", "HOLD"):
        return
    event = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "task_id": result["id"], "status": result["status"],
        "duration_seconds": round(elapsed, 3),
    }
    if result.get("commit"):
        event["commit"] = result["commit"]
    with (factory.state / "run-events.jsonl").open("a", encoding="utf-8") as out:
        out.write(json.dumps(event, ensure_ascii=False) + "\n")


def _stage(factory, task: dict) -> dict:
    """A successful model call is IMPLEMENTED, never VERIFIED."""
    tid = task["id"]
    try:
        work = factory._workspace(tid)
        factory._preflight_workspace(task, work)
        if factory._changed(work):
            raise ContractError("queued batch worktree already has changes")
        factory._set(tid, "CODING", "batch coding in progress")
        factory._active_allowed_files = tuple(task["files"])
        rc, output = factory.coder(work, factory._prompt(task, "CODING"))
        if rc:
            factory._set(tid, "HOLD", "MODEL_FAILURE " + str(rc) + ": " + output)
            return {"id": tid, "status": "HOLD", "reason": "MODEL_FAILURE"}
        # Fail-closed path inventory is a mandatory lightweight safety gate.
        # The full approved acceptance checks are postponed until batch review.
        factory._preflight_workspace(task, work)
        changed = factory._changed(work)
        if not changed or changed - set(task["files"]):
            # Preserve the original one-fix path. REVIEW will be handled
            # before any more coding, with no unverified promotion.
            factory._set(tid, "REVIEW", "batch immediate scope review required")
            return {"id": tid, "status": "REVIEW", "review_pending": True}
        factory._set(tid, "IMPLEMENTED", "coder finished; acceptance not run")
        return {"id": tid, "status": "IMPLEMENTED",
                "verified": False, "changed_files": sorted(changed)}
    except Exception as exc:
        factory._set(tid, "HOLD", "BATCH_IMPLEMENT_EXCEPTION: " + str(exc))
        return {"id": tid, "status": "HOLD", "reason": str(exc)[:500]}


def materialize_review_workspace(factory, task: dict):
    """Copy allowlisted staged bytes to a NEW worktree at current verified ref.

    The original staged worktree survives a crash. File scopes remain exact,
    and each independent task is reviewed against all earlier VERIFIED commits.
    """
    from pathlib import Path

    tid = task["id"]
    source = factory._workspace(tid)
    factory._preflight_workspace(task, source)
    changed = factory._changed(source)
    if not changed or changed - set(task["files"]):
        raise ContractError("staged changes are missing or outside approved scope")
    snapshot = {}
    for path in changed:
        src = source / path
        if src.is_symlink():
            raise ContractError("staged source contains a symlink")
        if src.is_file():
            snapshot[path] = src.read_bytes()
        elif src.exists():
            raise ContractError("staged source has unsupported file type")
        else:
            snapshot[path] = None  # Approved deletion.

    target = factory.state / "worktrees" / ("batch-review-" + tid)
    if target.is_symlink():
        raise ContractError("review worktree path is a symlink")
    verified_sha = git(factory.repo, "rev-parse", factory.integration_ref)
    if not target.exists():
        rc, out = call(
            ["git", "worktree", "add", "-b", "axdev/batch-review-" + tid,
             str(target), verified_sha], factory.repo, timeout=60)
        if rc:
            raise ContractError("cannot create isolated batch review worktree: " + out)
    if Path(git(target, "rev-parse", "--show-toplevel")).resolve() != target.resolve():
        raise ContractError("batch review worktree root changed")
    if git(target, "rev-parse", "HEAD") != verified_sha:
        raise ContractError("batch review base changed; manual inspection required")
    factory._preflight_workspace(task, target)
    for path, content in snapshot.items():
        dst = target / path
        if dst.is_symlink():
            raise ContractError("review destination is a symlink")
        if content is None:
            if dst.is_dir():
                raise ContractError("cannot remove a directory as an approved file")
            dst.unlink(missing_ok=True)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(content)
    factory._preflight_workspace(task, target)
    if factory._changed(target) != changed:
        raise ContractError("review transfer did not preserve exact modified paths")
    return target


def run_implementation_batch(factory, maximum: int, execute: bool) -> list[dict]:
    if not 1 <= maximum <= 100:
        raise ContractError("max tasks 1..100")
    if not execute:
        return [factory.run_one(False)]
    results: list[dict] = []
    with single_worker_lock(factory.state):
        states = factory.status()
        pending = any(value in PENDING for value in states.values())
        if not pending:
            occupied: set[str] = set()
            count = 0
            for task in factory.tasks:
                if count >= maximum:
                    break
                if (factory.state / "STOP.REQUESTED").exists():
                    break
                states = factory.status()
                if (states[task["id"]] != "QUEUED" or
                        any(states[dep] != "VERIFIED"
                            for dep in task.get("depends_on", []))):
                    continue
                # Staged siblings cannot edit overlapping paths. A dependent
                # task must wait for its prerequisite to become VERIFIED.
                filenames = {path.casefold() for path in task["files"]}
                if filenames & occupied:
                    continue
                started = time.monotonic()
                result = _stage(factory, task)
                count += 1
                results.append(result)
                _event(factory, result, time.monotonic() - started)
                if result["status"] == "IMPLEMENTED":
                    occupied |= filenames
                if result["status"] == "REVIEW":
                    # A scope anomaly must be assessed immediately.
                    break

        # After all eligible coding invocations, run independent acceptance.
        # If a stop was requested, leave IMPLEMENTED records for explicit
        # later resume without another model invocation.
        for _ in range(maximum):
            if (factory.state / "STOP.REQUESTED").exists():
                results.append({"status": "STOP_REQUESTED",
                                "message": "pending review retained in SQLite"})
                break
            if not any(value in PENDING for value in factory.status().values()):
                break
            started = time.monotonic()
            result = factory.run_one(True)
            results.append(result)
            _event(factory, result, time.monotonic() - started)
            if result["status"] == "NO_READY_TASK":
                break
    return results
