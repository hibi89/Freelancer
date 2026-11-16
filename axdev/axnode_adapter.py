"""AXNODE typed checkpoint bridge: metadata-only, never fake .axnode bytes.

This is a typed DAG/checkpoint export for a future approved AXNODE native
compiler. AXNODE itself is a separate user-owned binary project.
"""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from contextlib import closing
from pathlib import Path

from .core import ContractError, load_plan, plan_hash, VALID_STATES

SHA40 = re.compile(r"[0-9a-f]{40}\Z")


def typed_checkpoint(plan: Path, database: Path) -> dict:
    if database.is_symlink() or any(part.is_symlink() for part in database.parents):
        raise ContractError("AXNODE checkpoint database symlink forbidden")
    if not database.is_file():
        raise ContractError("AXNODE checkpoint database is absent")
    tasks = load_plan(plan)
    if not tasks or len(tasks) > 100:
        raise ContractError("checkpoint requires 1..100 approved tasks")
    with closing(sqlite3.connect(database.resolve().as_uri() + "?mode=ro", uri=True)) as db:
        rows = db.execute("SELECT id,spec,status,commit_sha FROM runs").fetchall()
        baseline = db.execute("SELECT value FROM meta WHERE key='base_sha'").fetchone()
    ledger = {r[0]: r for r in rows}
    if len(ledger) != len(rows) or set(ledger) != {t["id"] for t in tasks}:
        raise ContractError("checkpoint task ledger differs from approved plan")
    if baseline is None or not SHA40.fullmatch(baseline[0]):
        raise ContractError("checkpoint baseline SHA absent or invalid")
    nodes = []
    for task in tasks:
        tid = task["id"]
        _, spec, status, commit = ledger[tid]
        if spec != plan_hash(task) or status not in VALID_STATES:
            raise ContractError("checkpoint contract or status has changed")
        if status == "VERIFIED" and (not isinstance(commit, str)
                                     or not SHA40.fullmatch(commit)):
            raise ContractError("verified checkpoint missing exact commit SHA")
        nodes.append({
            "id": tid, "kind": "TASK", "input_type": "ApprovedTaskSpecSHA256",
            "output_type": "VerifiedGitCommitSHA1", "status": status,
            "spec_sha256": spec, "verified_commit": commit if status == "VERIFIED" else None,
            "depends_on": list(task.get("depends_on", [])),
        })
    graph = {
        "format": "axdev.axnode-typed-bridge.v1",
        "native_axnode_binary": False,
        "user_approval_for_execution": False,
        "source_base_sha": baseline[0],
        "nodes": nodes,
        "edges": [{"from": dep, "to": t["id"], "type": "VERIFIED_PREREQUISITE"}
                  for t in tasks for dep in t.get("depends_on", [])],
    }
    payload = json.dumps(graph, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    graph["content_sha256"] = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return graph


def export_checkpoint(plan: Path, database: Path, output: Path) -> dict:
    """Create-only private JSON export; no source or credentials copied."""
    result = typed_checkpoint(plan, database)
    output = output.expanduser().absolute()
    if output.is_symlink() or any(part.is_symlink() for part in output.parents):
        raise ContractError("AXNODE output path cannot contain symlinks")
    if output.exists():
        raise ContractError("AXNODE checkpoint output exists; no overwrite")
    data = (json.dumps(result, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as stream:
        stream.write(data)
    return {"path": str(output), "payload_sha256": hashlib.sha256(data).hexdigest(),
            "nodes": len(result["nodes"]), "native_axnode_binary": False}
