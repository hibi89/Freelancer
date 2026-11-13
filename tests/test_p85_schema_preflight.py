"""Foreign/corrupt SQLite must never be transformed into a legitimate WORKNOVA ledger."""
from __future__ import annotations
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from worknova_desk.core import Desk, DeskError, restore_new

ROOT = Path(__file__).resolve().parents[1]

class SchemaPreflightTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.folder = Path(temp.name)
        self.db = self.folder / 'owner.sqlite'

    def test_foreign_sqlite_v0_is_not_initialized_even_when_allow_create(self):
        with sqlite3.connect(self.db) as db:
            db.execute('CREATE TABLE unrelated (secret TEXT)')
            db.execute("INSERT INTO unrelated VALUES ('PRESERVE')")
        original = self.db.read_bytes()
        for allow in (True, False):
            with self.subTest(allow_create=allow), self.assertRaisesRegex(DeskError, 'no WORKNOVA schema'):
                Desk(self.db, allow_create=allow)
            self.assertEqual(self.db.read_bytes(), original)
        with sqlite3.connect(self.db) as db:
            self.assertEqual(db.execute('SELECT secret FROM unrelated').fetchone()[0], 'PRESERVE')
            self.assertEqual([r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE name='customers'")], [])

    def test_preexisting_empty_file_refused_without_overwrite(self):
        self.db.touch()
        with self.assertRaisesRegex(DeskError, 'no WORKNOVA schema'):
            Desk(self.db)
        self.assertEqual(self.db.stat().st_size, 0)

    def test_corrupt_non_sqlite_refused_without_modification(self):
        self.db.write_bytes(b'CLIENT-KEEP-OLD-ORIGINAL')
        with self.assertRaisesRegex(DeskError, 'invalid or corrupt SQLite'):
            Desk(self.db, allow_create=False)
        self.assertEqual(self.db.read_bytes(), b'CLIENT-KEEP-OLD-ORIGINAL')

    def test_incomplete_v2_schema_is_not_silently_repaired(self):
        with sqlite3.connect(self.db) as db:
            db.executescript('PRAGMA user_version=2; CREATE TABLE customers(id TEXT PRIMARY KEY);')
        original = self.db.read_bytes()
        with self.assertRaisesRegex(DeskError, 'incomplete WORKNOVA v2'):
            Desk(self.db, allow_create=False)
        self.assertEqual(self.db.read_bytes(), original)

    def test_invalid_v2_quote_columns_refused(self):
        desk = Desk(self.db); desk.close()
        with sqlite3.connect(self.db) as db:
            db.execute('ALTER TABLE quotes DROP COLUMN parent_quote_id')
        with self.assertRaisesRegex(DeskError, 'invalid WORKNOVA v2 quote columns'):
            Desk(self.db, allow_create=False)

    def test_tampered_audit_blocks_reopen_and_preserves_file(self):
        desk = Desk(self.db)
        desk.add_customer('synthetic')
        desk.close()
        with sqlite3.connect(self.db) as db:
            db.execute("UPDATE audit_events SET actor='altered' WHERE seq=1")
        original = self.db.read_bytes()
        with self.assertRaisesRegex(DeskError, 'audit chain mismatch'):
            Desk(self.db, allow_create=False)
        self.assertEqual(self.db.read_bytes(), original)

    def test_normal_existing_v2_reopens_and_preserves_data(self):
        desk = Desk(self.db)
        cid = desk.add_customer('synthetic')
        desk.close()
        recovered = Desk(self.db, allow_create=False)
        try:
            self.assertEqual(recovered._fetch('customers', cid)['name'], 'synthetic')
        finally:
            recovered.close()

    def test_restoring_foreign_sqlite_rejected_without_new_destination(self):
        with sqlite3.connect(self.db) as db:
            db.execute('CREATE TABLE private_notes(note TEXT)')
        before = self.db.read_bytes()
        target = self.folder / 'recovered.sqlite'
        with self.assertRaisesRegex(DeskError, 'no WORKNOVA schema'):
            restore_new(self.db, target, hashlib.sha256(before).hexdigest())
        self.assertFalse(target.exists())
        self.assertEqual(self.db.read_bytes(), before)

    def test_cli_rejects_foreign_sqlite_without_traceback(self):
        with sqlite3.connect(self.db) as db:
            db.execute('CREATE TABLE unrelated (value TEXT)')
        proc = subprocess.run([sys.executable, '-m','worknova_desk','--db',str(self.db),'verify'],
            cwd=ROOT, env={**os.environ,'PYTHONPATH':str(ROOT)}, capture_output=True,text=True,timeout=15)
        self.assertEqual(proc.returncode, 2)
        self.assertFalse('Traceback' in proc.stderr)
        self.assertFalse(json.loads(proc.stderr)['ok'])

if __name__ == '__main__': unittest.main()
