"""Prevent accidental empty-ledger recreation after an owner DB goes missing."""
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

ROOT = Path(__file__).resolve().parents[1]


class MissingDatabaseSafetyTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.db = self.root / 'owner.sqlite'

    def _cli(self, *args):
        return subprocess.run([sys.executable, '-m', 'worknova_desk', '--db', str(self.db), *args],
                              cwd=ROOT, env={**os.environ, 'PYTHONPATH': str(ROOT)},
                              capture_output=True, text=True, timeout=15)

    def test_existing_required_never_creates_missing_ledger(self):
        with self.assertRaisesRegex(DeskError, 'database not found/readable'):
            Desk(self.db, allow_create=False)
        self.assertFalse(self.db.exists())

    def test_cli_query_missing_refuses_without_touching_disk(self):
        result = self._cli('list-customers')
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn('database not found', result.stderr)
        self.assertFalse(self.db.exists())

    def test_cli_mutation_missing_refuses_without_creating(self):
        result = self._cli('customer', '--name', 'new')
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertFalse(self.db.exists())

    def test_cli_init_then_existing_workflow(self):
        self.assertEqual(self._cli('init').returncode, 0)
        self.assertEqual(self._cli('customer', '--name', '가상 구매자').returncode, 0)
        output = self._cli('list-customers')
        self.assertEqual(output.returncode, 0, output.stderr)
        self.assertEqual(len(json.loads(output.stdout)['result']), 1)

    @unittest.skipUnless(os.name == 'posix', 'POSIX permission model only')
    def test_new_owner_db_private_by_default(self):
        desk = Desk(self.db)
        self.addCleanup(desk.close)
        self.assertEqual(stat.S_IMODE(self.db.stat().st_mode), 0o600)

    @unittest.skipUnless(os.name == 'posix', 'POSIX permission model only')
    def test_existing_owner_db_permissions_not_rewritten(self):
        desk = Desk(self.db)
        desk.close()
        self.db.chmod(0o640)
        reopened = Desk(self.db, allow_create=False)
        reopened.close()
        self.assertEqual(stat.S_IMODE(self.db.stat().st_mode), 0o640)

    def test_existing_unknown_schema_refuses(self):
        desk = Desk(self.db)
        desk.db.execute('PRAGMA user_version=99')
        desk.close()
        with self.assertRaisesRegex(DeskError, 'unsupported schema'):
            Desk(self.db, allow_create=False)
        self.assertTrue(self.db.exists())

    def test_symlink_existing_path_rejected(self):
        another = self.root / 'another.sqlite'
        d = Desk(another)
        d.close()
        try:
            self.db.symlink_to(another)
        except OSError:
            self.skipTest('symlink not permitted')
        with self.assertRaises(DeskError):
            Desk(self.db, allow_create=False)
        self.assertTrue(another.exists())


if __name__ == '__main__':
    unittest.main()
