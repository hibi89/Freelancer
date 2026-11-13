"""Recovery exercise must be explicit, private, verifiable, and non-destructive."""
from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from worknova_desk.core import Desk, DeskError
from worknova_desk.recovery import rehearse_restore

ROOT = Path(__file__).resolve().parents[1]


class RecoveryDrillTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.ledger = self.root / 'owner'
        self.workspace = self.root / 'scratch'
        self.ledger.mkdir()
        self.workspace.mkdir()
        self.path = self.ledger / 'ledger.sqlite'
        self.desk = Desk(self.path)
        self.addCleanup(self.desk.close)
        self.customer = self.desk.add_customer('합성 거래처')

    def test_rehearsal_matches_tables_and_removes_secret_copies(self):
        previous_bytes = self.path.read_bytes()
        result = rehearse_restore(self.desk, self.workspace)
        self.assertTrue(result['verified'])
        self.assertEqual(result['tables_verified'], 6)
        self.assertGreater(result['audit_events'], 0)
        self.assertNotIn('합성 거래처', json.dumps(result, ensure_ascii=False))
        self.assertEqual(list(self.workspace.iterdir()), [])
        self.assertEqual(self.path.read_bytes(), previous_bytes)

    def test_rehearsal_refuses_active_database_directory(self):
        with self.assertRaisesRegex(DeskError, 'separate local workspace'):
            rehearse_restore(self.desk, self.ledger)
        self.assertEqual({p.name for p in self.ledger.iterdir()}, {'ledger.sqlite'})

    def test_rehearsal_refuses_missing_workspace(self):
        with self.assertRaises(DeskError):
            rehearse_restore(self.desk, self.root / 'missing')
        self.assertFalse((self.root / 'missing').exists())

    def test_rehearsal_refuses_symlink_workspace(self):
        link = self.root / 'alias'
        try:
            link.symlink_to(self.workspace, target_is_directory=True)
        except OSError:
            self.skipTest('symlink privileges unavailable')
        with self.assertRaises(DeskError):
            rehearse_restore(self.desk, link)

    @unittest.skipUnless(os.name == 'posix', 'POSIX permission model')
    def test_backup_file_private_0600_under_permissive_umask(self):
        backup = self.workspace / 'backup.sqlite'
        old = os.umask(0o022)
        try:
            digest = self.desk.backup(backup)
        finally:
            os.umask(old)
        self.assertEqual(len(digest), 64)
        self.assertEqual(stat.S_IMODE(backup.stat().st_mode), 0o600)

    def test_backup_refuses_same_name_without_rewrite(self):
        backup = self.workspace / 'backup.sqlite'
        backup.write_bytes(b'DO_NOT_REPLACE')
        with self.assertRaises(DeskError):
            self.desk.backup(backup)
        self.assertEqual(backup.read_bytes(), b'DO_NOT_REPLACE')

    def test_cli_explicit_workspace_and_no_pii_in_output(self):
        completed = subprocess.run([sys.executable, '-m', 'worknova_desk', '--db', str(self.path),
                                    'rehearse-restore', '--workspace-dir', str(self.workspace)],
                                   cwd=ROOT, env={**os.environ, 'PYTHONPATH': str(ROOT)},
                                   capture_output=True, text=True, timeout=20)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        response = json.loads(completed.stdout)
        self.assertTrue(response['result']['verified'])
        self.assertNotIn('합성 거래처', completed.stdout)
        self.assertEqual(list(self.workspace.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
