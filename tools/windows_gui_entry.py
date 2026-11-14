"""No-network, no-admin entrypoint for a future unsigned Windows EXE.

Only this user's local app-data folder is addressed. Existing ledgers are never
replaced: worknova_desk.gui.main() performs its established first-run prompt.
This entrypoint is NOT evidence of Windows execution, accessibility or signing.
"""
from __future__ import annotations

import os
import stat
import sys
from pathlib import Path


def _assert_plain_ancestors(path: Path) -> None:
    """Fail closed on existing symlinks/junctions before writing to app data.

    This is a path preflight, not a substitute for authenticated OS ACLs. The
    parent chain is checked because testing only Data misses parent junctions.
    """
    for ancestor in (path, *path.parents):
        if ancestor.is_symlink():
            raise RuntimeError('Unsafe redirected application data path')
        if ancestor.exists():
            attrs = getattr(ancestor.stat(follow_symlinks=False), 'st_file_attributes', 0)
            if attrs & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0):
                raise RuntimeError('Unsafe redirected application data path')
            if not ancestor.is_dir():
                raise RuntimeError('Application data path is not a directory')


def data_directory(appdata: str) -> Path:
    if not appdata or not appdata.strip():
        raise RuntimeError('LOCALAPPDATA is not configured')
    base = Path(appdata)
    if not base.is_absolute():
        raise RuntimeError('LOCALAPPDATA must be absolute')
    folder = base / 'WORKNOVA Desk' / 'Data'
    _assert_plain_ancestors(folder)
    return folder


def main(argv=None) -> int:
    if sys.platform != 'win32':
        raise RuntimeError('This entrypoint is for native Windows only')
    args = list(sys.argv[1:] if argv is None else argv)
    if args:
        # Hidden, explicit CI-only mode. Never open, copy or modify the user's
        # normal LOCALAPPDATA ledger. The synthetic fixture is disposable.
        if len(args) != 2 or args[0] != '--synthetic-qa-report':
            raise RuntimeError('Unsupported Windows application arguments')
        if os.environ.get('WORKNOVA_TEST_OFFLINE_ONLY') != '1':
            raise RuntimeError('Synthetic test mode is disabled outside isolated QA')
        from worknova_desk.synthetic_acceptance import run
        run(args[1])
        return 0
    folder = data_directory(os.environ.get('LOCALAPPDATA', ''))
    folder.mkdir(parents=True, exist_ok=True)
    _assert_plain_ancestors(folder)
    from worknova_desk.gui import main as gui_main
    gui_main(['--db', str(folder / 'desk.sqlite')])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
