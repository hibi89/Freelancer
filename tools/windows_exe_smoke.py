"""Offline Windows onedir EXE GUI smoke using a disposable synthetic ledger.

Designed for a standard Windows CI runner. Never reads the real LOCALAPPDATA,
modifies OS security policies, or sends customer/QA data over a network.
Requires a visible Windows desktop session. Not buyer, Defender, or ACL proof.
"""
from __future__ import annotations

import argparse
from contextlib import closing
import ctypes
from ctypes import wintypes
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _own_visible_window(pid: int) -> int | None:
    """Return only a visible WORKNOVA top-level HWND owned by our EXE PID."""
    user32 = ctypes.windll.user32
    user32.EnumWindows.argtypes = [ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM), wintypes.LPARAM]
    user32.EnumWindows.restype = wintypes.BOOL
    user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
    user32.GetWindowThreadProcessId.restype = wintypes.DWORD
    user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
    user32.GetWindowTextLengthW.restype = ctypes.c_int
    user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user32.GetWindowTextW.restype = ctypes.c_int
    user32.IsWindowVisible.argtypes = [wintypes.HWND]
    user32.IsWindowVisible.restype = wintypes.BOOL
    found = []
    CALLBACK = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

    @CALLBACK
    def callback(hwnd, _):
        owner = wintypes.DWORD(0)
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
        if owner.value != pid or not user32.IsWindowVisible(hwnd):
            return True
        length = user32.GetWindowTextLengthW(hwnd)
        if not 0 < length < 300:
            return True
        name = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, name, length + 1)
        if 'WORKNOVA Desk' in name.value:
            found.append(int(hwnd))
            return False
        return True

    user32.EnumWindows(callback, 0)
    return found[0] if found else None


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description='Offline Windows EXE GUI smoke; synthetic data only')
    parser.add_argument('--exe', required=True)
    args = parser.parse_args(argv)
    stage = 'platform'
    try:
        if sys.platform != 'win32':
            raise RuntimeError('Native Windows desktop required')
        stage = 'validate-onedir-path'
        exe = Path(args.exe).absolute()
        if (exe.name != 'WORKNOVA-Desk.exe' or not exe.is_file() or exe.is_symlink()
                or not (exe.parent / '_internal').is_dir()):
            raise RuntimeError('Expected safe onedir EXE and _internal files required')
        stage = 'read-exe'
        with exe.open('rb') as stream:
            if stream.read(2) != b'MZ':
                raise RuntimeError('Invalid Windows EXE header')
            stream.seek(0)
            digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        stage = 'import-ledger'
        from worknova_desk.core import Desk
        stage = 'create-disposable-profile'
        with tempfile.TemporaryDirectory(prefix='worknova-ci-exe-') as qa_root:
            appdata = Path(qa_root) / 'appdata'
            data_dir = appdata / 'WORKNOVA Desk' / 'Data'
            data_dir.mkdir(parents=True)
            db_path = data_dir / 'desk.sqlite'
            test_name = 'WORKNOVA_CI_SYNTHETIC_CUSTOMER'
            stage = 'create-synthetic-ledger'
            desk = Desk(db_path, allow_create=True)
            try:
                desk.add_customer(test_name, actor='qa-only')
            finally:
                desk.close()
            env = os.environ.copy()
            env['LOCALAPPDATA'] = str(appdata)
            stage = 'launch-exe'
            proc = subprocess.Popen([str(exe)], cwd=str(exe.parent), env=env)
            try:
                stage = 'wait-for-owned-gui'
                hwnd = None
                deadline = time.monotonic() + 15
                while time.monotonic() < deadline:
                    if proc.poll() is not None:
                        raise RuntimeError('EXE closed before native GUI appeared')
                    hwnd = _own_visible_window(proc.pid)
                    if hwnd:
                        break
                    time.sleep(0.3)
                if not hwnd:
                    raise RuntimeError('No visible WORKNOVA GUI window in runner desktop')
                user32 = ctypes.windll.user32
                user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
                user32.PostMessageW.restype = wintypes.BOOL
                stage = 'close-owned-gui'
                if not user32.PostMessageW(hwnd, 0x0010, 0, 0):  # WM_CLOSE, only owned window
                    raise RuntimeError('Failed to request GUI close')
                if proc.wait(timeout=12) != 0:
                    raise RuntimeError('GUI exit code was nonzero')
            finally:
                if proc.poll() is None:
                    proc.terminate()
                    try:
                        proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                        proc.wait(timeout=5)
            stage = 'verify-synthetic-ledger'
            # sqlite3.Connection.__exit__ commits but does not close. On Windows
            # an open handle prevents TemporaryDirectory removal (WinError 32).
            with closing(sqlite3.connect(db_path.resolve().as_uri() + '?mode=ro', uri=True)) as db:
                if db.execute('PRAGMA user_version').fetchone()[0] != 2:
                    raise RuntimeError('SQLite schema version mismatch')
                if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                    raise RuntimeError('Synthetic SQLite integrity failure')
                if db.execute('SELECT COUNT(*) FROM customers WHERE name=?', (test_name,)).fetchone()[0] != 1:
                    raise RuntimeError('Synthetic customer missing after EXE GUI close')
            stage = 'frozen-synthetic-business-lifecycle'
            report_path = Path(qa_root) / 'frozen-lifecycle-report.json'
            qa_env = env.copy()
            qa_env['WORKNOVA_TEST_OFFLINE_ONLY'] = '1'
            completed = subprocess.run([str(exe), '--synthetic-qa-report', str(report_path)],
                                       cwd=str(exe.parent), env=qa_env, timeout=60,
                                       check=False)
            if completed.returncode != 0 or not report_path.is_file():
                raise RuntimeError('Native frozen EXE synthetic lifecycle failed')
            lifecycle = json.loads(report_path.read_text(encoding='utf-8'))
            if (not lifecycle.get('ok') or lifecycle.get('synthetic_only') is not True
                    or lifecycle.get('verified_receipts') != 2
                    or lifecycle.get('verified_restored_events', 0) < 8
                    or lifecycle.get('sqlite_integrity') != 'ok'):
                raise RuntimeError('Native frozen lifecycle report did not meet assertions')
        stage = 'cleanup-disposable-profile'
        print(json.dumps({'ok': True, 'scope': 'native Windows synthetic GUI plus frozen business lifecycle',
                          'sha256': digest, 'window': 'seen and closed',
                          'exit_code': 0, 'sqlite_integrity': 'ok',
                          'synthetic_customers': 1,
                          'frozen_business_lifecycle': 'PASS', 'verified_receipts': 2,
                          'backup_restore_rehearsal': 'PASS', 'release': 'HOLD'}))
        return 0
    except Exception as exc:
        print(json.dumps({'ok': False, 'stage': stage,
                          'error_type': type(exc).__name__,
                          'winerror': getattr(exc, 'winerror', None),
                          'scope': 'native Windows GUI NOT verified', 'release': 'HOLD'}))
        return 3


if __name__ == '__main__':
    raise SystemExit(main())
