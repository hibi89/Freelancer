"""Explicit offline recovery rehearsal; the operator chooses a local scratch parent.

This command copies sensitive records temporarily into a fresh private subdirectory.
It never overwrites a database and deletes the drill workspace on exit.
"""
from __future__ import annotations

import os
import stat
import tempfile
from pathlib import Path

from .core import Desk, DeskError, restore_new
from .evidence import _snapshot


def rehearse_restore(desk: Desk, workspace_dir: str | Path) -> dict:
    """Backup+SHA-pin+restore+table-by-table identity check with no original writes.

    ``workspace_dir`` is an explicitly authorized existing local directory; it
    MUST NOT be the directory of an untrusted network mount or a shared folder.
    The drill creates a private temporary child and removes it at the end.
    """
    parent = Path(workspace_dir)
    if not parent.is_dir() or parent.is_symlink():
        raise DeskError("recovery drill requires an explicit existing non-symlink workspace")
    # Avoid writing a second DB directly beside an owner's live file unless
    # the workspace was independently and intentionally selected by the user.
    if parent.resolve() == desk.path.parent.resolve():
        raise DeskError("choose a separate local workspace, not the active database directory")
    before = _snapshot(desk)
    with tempfile.TemporaryDirectory(prefix=".worknova-restore-drill-", dir=parent) as directory:
        scratch = Path(directory)
        # Private 0700 workspace on POSIX; the backup itself is 0600.
        if os.name == "posix" and stat.S_IMODE(scratch.stat().st_mode) != 0o700:
            raise DeskError("temporary recovery workspace is not private")
        backup = scratch / "snapshot.sqlite"
        restored = scratch / "recovered.sqlite"
        digest = desk.backup(backup)
        result = restore_new(backup, restored, digest)
        rebuilt = Desk(restored, allow_create=False)
        try:
            after = _snapshot(rebuilt)
        finally:
            rebuilt.close()
        if before != after:
            raise DeskError("recovery rehearsal mismatch: restored business state differs")
        if result["schema_version"] != desk.schema_version:
            raise DeskError("recovery rehearsal schema mismatch")
        return {"verified": True,
                "schema_version": desk.schema_version,
                "audit_events": before["audit_events"],
                "tables_verified": len(before["tables"]),
                "note": "Local backup and restore rehearsal only; scratch removed; not disaster recovery or Windows proof"}
