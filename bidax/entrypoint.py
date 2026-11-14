"""Executable GUI entrypoint for a manually built, local Windows package."""
from __future__ import annotations
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from .desktop import launch


def default_db_path() -> Path:
    # No writes to Program Files or the current directory; no API keys in EXE.
    root = os.environ.get("LOCALAPPDATA") or os.environ.get("XDG_DATA_HOME")
    base = Path(root) if root else Path.home() / ".local" / "share"
    dest = base / "BidAX" / "bidax.db"
    dest.parent.mkdir(parents=True, exist_ok=True)
    return dest


def main() -> None:
    # Support staff can exercise the ACTUAL frozen GUI with synthetic/empty data
    # without opening or creating a customer's active database.
    if sys.argv[1:] == ["--selftest-gui"]:
        with TemporaryDirectory(prefix="bidax-gui-smoke-") as temp:
            launch(Path(temp) / "test-gui.db", auto_close_ms=700)
        return
    if sys.argv[1:]:
        raise SystemExit("unsupported GUI argument; only --selftest-gui is allowed")
    launch(default_db_path())


if __name__ == "__main__":
    main()
