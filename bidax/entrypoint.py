"""Executable GUI entrypoint for a manually built, local Windows package."""
from __future__ import annotations
import os
from pathlib import Path
from .desktop import launch


def default_db_path() -> Path:
    # No writes to Program Files or the current directory; no API keys in EXE.
    root = os.environ.get("LOCALAPPDATA") or os.environ.get("XDG_DATA_HOME")
    base = Path(root) if root else Path.home() / ".local" / "share"
    dest = base / "BidAX" / "bidax.db"
    dest.parent.mkdir(parents=True, exist_ok=True)
    return dest


def main() -> None:
    launch(default_db_path())


if __name__ == "__main__":
    main()
