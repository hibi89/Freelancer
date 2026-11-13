"""Owner-selected read-only file evidence, hashed into local audit without file/path/PII.

Evidence hash proves which bytes the local operator selected, not buyer identity,
external delivery, legal approval or authenticity of the unsigned audit database.
"""
from __future__ import annotations

import hashlib
import json
import os
import stat
from pathlib import Path

from .core import Desk, DeskError, _text

MAX_BYTES = 64 * 1024 * 1024


def file_fingerprint(source: str | Path) -> dict:
    path = Path(source)
    # Reject symbolic links before open; O_NOFOLLOW closes the open-time gap on supporting OSes.
    try:
        original = path.lstat()
    except OSError as exc:
        raise DeskError("evidence must be an existing regular file") from exc
    if not stat.S_ISREG(original.st_mode):
        raise DeskError("evidence must be a regular non-symlink file")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0)
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(str(path), flags)
    except OSError as exc:
        raise DeskError("cannot safely read evidence file") from exc
    try:
        with os.fdopen(fd, "rb") as stream:
            before = os.fstat(stream.fileno())
            if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_BYTES or before.st_size < 0:
                raise DeskError("evidence file not regular or exceeds 64 MiB")
            if before.st_nlink > 1:
                raise DeskError("hard-linked evidence file refused")
            if (original.st_dev, original.st_ino) != (before.st_dev, before.st_ino):
                raise DeskError("evidence path changed before read")
            digest = hashlib.sha256()
            count = 0
            while True:
                chunk = stream.read(65536)
                if not chunk:
                    break
                count += len(chunk)
                if count > MAX_BYTES:
                    raise DeskError("evidence file too large during read")
                digest.update(chunk)
            after = os.fstat(stream.fileno())
            if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns,
                before.st_ctime_ns) != (after.st_dev, after.st_ino, after.st_size,
                                        after.st_mtime_ns, after.st_ctime_ns) or count != before.st_size:
                raise DeskError("evidence file changed during read; retry only on stable source")
        # Recheck the path itself after closing: catches replacement when a platform
        # lacks O_NOFOLLOW. It cannot be a strict Windows ACL or reparse-point proof.
        try:
            final = path.lstat()
        except OSError as exc:
            raise DeskError("evidence path disappeared after read") from exc
        if not stat.S_ISREG(final.st_mode) or (final.st_dev, final.st_ino) != (before.st_dev, before.st_ino):
            raise DeskError("evidence path replaced during read")
        return {"sha256": digest.hexdigest(), "bytes": count}
    except OSError as exc:
        raise DeskError("evidence file reading failed") from exc


def _events(desk: Desk, milestone_id: str) -> list[dict]:
    desk._fetch("milestones", milestone_id)
    found = []
    for row in desk.db.execute("SELECT seq,payload_json FROM audit_events WHERE action='DELIVERY_EVIDENCE_HASHED' ORDER BY seq"):
        try:
            data = json.loads(row["payload_json"])
        except (ValueError, TypeError) as exc:
            raise DeskError("malformed evidence audit record") from exc
        if data.get("milestone_id") == milestone_id:
            found.append({"seq": row["seq"], "sha256": data["sha256"], "bytes": data["bytes"]})
    return found


def attach_file(desk: Desk, milestone_id: str, source: str | Path, *, actor: str, confirm: bool) -> dict:
    if confirm is not True:
        raise DeskError("explicit local evidence consent required")
    actor = _text(actor, "actor", 80)
    proof = file_fingerprint(source)
    with desk._write():
        milestone = desk._fetch("milestones", milestone_id)
        contract = desk._fetch("contracts", milestone["contract_id"])
        if contract["status"] != "ACTIVE" or milestone["status"] != "DELIVERED":
            raise DeskError("attach evidence only during DELIVERED state of active contract")
        for event in _events(desk, milestone_id):
            if event["sha256"] == proof["sha256"] and event["bytes"] == proof["bytes"]:
                return {**proof, "duplicate": True, "note": "existing local evidence fingerprint"}
        desk._event("DELIVERY_EVIDENCE_HASHED", actor, {"milestone_id": milestone_id, **proof,
                                                        "stored_original": False, "external_delivery": False})
    return {**proof, "duplicate": False,
            "note": "Hash only. No evidence file stored/uploaded; not buyer receipt or delivery proof"}


def list_evidence(desk: Desk, milestone_id: str) -> list[dict]:
    desk.verify_audit()
    return _events(desk, milestone_id)


def verify_file(desk: Desk, milestone_id: str, source: str | Path) -> dict:
    desk.verify_audit()
    proof = file_fingerprint(source)
    matching = [entry for entry in _events(desk, milestone_id) if entry["sha256"] == proof["sha256"]
                and entry["bytes"] == proof["bytes"]]
    if not matching:
        raise DeskError("file fingerprint is not recorded for this milestone")
    return {**proof, "verified": True, "event_seq": matching[-1]["seq"],
            "note": "Matches local unsigned audit only; not external delivery acceptance"}
