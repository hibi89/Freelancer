"""Independent local integrity checkpoint: hashes business rows without exporting PII.

A saved checkpoint in a separately protected location detects subsequent database changes.
No network, no signing key, and no claim of tamper resistance when both copies can be rewritten.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import sqlite3
from pathlib import Path

from .core import Desk, DeskError, _json

FORMAT = "worknova-independent-checkpoint-v1"
TABLES = ("customers", "quotes", "contracts", "milestones", "receipts", "audit_events")


def _snapshot(desk: Desk) -> dict:
    # A single SQLite read transaction prevents mixed-point-in-time table hashes.
    desk.db.execute("BEGIN")
    try:
        events = desk.verify_audit()
        tables = {}
        for table in TABLES:  # no untrusted SQL identifiers
            key = "seq" if table == "audit_events" else "id"
            rows = [dict(r) for r in desk.db.execute(f"SELECT * FROM {table} ORDER BY {key}")]
            encoded = _json(rows).encode("utf-8")
            tables[table] = {"count": len(rows), "sha256": hashlib.sha256(encoded).hexdigest()}
        last = desk.db.execute("SELECT digest FROM audit_events ORDER BY seq DESC LIMIT 1").fetchone()
        return {"schema_version": desk.schema_version,
                "audit_events": events,
                "audit_head": last[0] if last else "0"*64,
                "tables": tables}
    finally:
        desk.db.execute("ROLLBACK")  # read-only transaction cleanup


def _valid_target(path: Path) -> None:
    if path.exists() or path.is_symlink() or not path.parent.is_dir() or path.parent.is_symlink():
        raise DeskError("checkpoint requires NEW file in existing non-symlink local directory")
    if path.suffix.lower() != ".json":
        raise DeskError("checkpoint output must end in .json")


def create_checkpoint(desk: Desk, destination: str | Path) -> dict:
    path = Path(destination)
    _valid_target(path)
    state = _snapshot(desk)
    content = (_json({"format": FORMAT, **state,
        "warning": "Local unencrypted hashes; verify against separately protected original. No payment verification."}) + "\n").encode()
    if len(content) > 65536:
        raise DeskError("checkpoint too large")
    created = False
    fd = None
    try:
        # The checkpoint contains business-state hashes/counts. They are not
        # plaintext customer records, but still private commercial metadata.
        # Never rely on a permissive process umask for file permissions.
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        created = True
        with os.fdopen(fd, "wb") as f:
            fd = None
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
    except FileExistsError:
        raise DeskError("checkpoint destination already exists") from None
    except Exception:
        if fd is not None:
            os.close(fd)
        if created:
            path.unlink(missing_ok=True)
        raise
    return {"file_sha256": hashlib.sha256(content).hexdigest(),
            "audit_events": state["audit_events"], "schema_version": state["schema_version"],
            "note": "Keep this JSON and its SHA256 separately from the SQLite file; not cryptographically signed"}


def verify_checkpoint(desk: Desk, source: str | Path, *, expected_file_sha256: str | None = None) -> dict:
    path = Path(source)
    if not path.is_file() or path.is_symlink() or path.stat().st_size > 65536:
        raise DeskError("invalid checkpoint file")
    raw = path.read_bytes()
    file_sha = hashlib.sha256(raw).hexdigest()
    if expected_file_sha256 is not None:
        if (not isinstance(expected_file_sha256, str) or len(expected_file_sha256) != 64 or
                not all(c in "0123456789abcdef" for c in expected_file_sha256.lower()) or
                not hmac.compare_digest(file_sha, expected_file_sha256.lower())):
            raise DeskError("checkpoint file SHA256 mismatch")
    try:
        saved = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DeskError("invalid checkpoint JSON") from exc
    state = _snapshot(desk)
    if not isinstance(saved, dict) or saved.get("format") != FORMAT:
        raise DeskError("unsupported checkpoint format")
    for key in ("schema_version", "audit_events", "audit_head"):
        if _json(saved.get(key)) != _json(state[key]):
            raise DeskError(f"independent checkpoint mismatch: {key}")
    recorded_tables = saved.get("tables")
    if not isinstance(recorded_tables, dict) or set(recorded_tables) != set(TABLES):
        raise DeskError("independent checkpoint invalid table catalog")
    for table in TABLES:
        if _json(recorded_tables[table]) != _json(state["tables"][table]):
            raise DeskError(f"independent checkpoint mismatch: {table}")
    return {"verified": True, "file_sha256": file_sha,
            "audit_events": state["audit_events"], "tables_verified": len(TABLES),
            "note": "Business state matches saved local checkpoint; not a signed or bank-verified record"}
