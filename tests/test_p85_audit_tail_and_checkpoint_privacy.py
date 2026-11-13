"""WD-08/WD-10 audit-tail and checkpoint privacy regressions (synthetic only)."""
from __future__ import annotations

import hashlib
import os
import stat
import tempfile
import unittest
from pathlib import Path

from worknova_desk.core import Desk, DeskError
from worknova_desk.evidence import create_checkpoint, verify_checkpoint


class AuditTailAndCheckpointPrivacyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        self.path = self.folder / "synthetic.sqlite"
        self.ledger = Desk(self.path)
        self.addCleanup(self.ledger.close)

    def test_delete_single_event_tail_detected(self):
        self.ledger.add_customer("합성 거래처")
        self.assertEqual(self.ledger.verify_audit(), 1)
        self.ledger.db.execute("DELETE FROM audit_events WHERE seq=1")
        with self.assertRaisesRegex(DeskError, "high-water"):
            self.ledger.verify_audit()

    def test_delete_last_event_of_two_detected(self):
        self.ledger.add_customer("합성 A")
        self.ledger.add_customer("합성 B")
        self.ledger.db.execute("DELETE FROM audit_events WHERE seq=2")
        with self.assertRaisesRegex(DeskError, "high-water"):
            self.ledger.verify_audit()

    def test_delete_middle_event_detects_gap(self):
        for k in range(3):
            self.ledger.add_customer(f"합성 {k}")
        self.ledger.db.execute("DELETE FROM audit_events WHERE seq=2")
        with self.assertRaisesRegex(DeskError, "sequence gap"):
            self.ledger.verify_audit()

    def test_missing_sqlite_high_water_record_detected(self):
        self.ledger.add_customer("합성 고객")
        self.ledger.db.execute("DELETE FROM sqlite_sequence WHERE name='audit_events'")
        with self.assertRaisesRegex(DeskError, "high-water"):
            self.ledger.verify_audit()

    def test_reopened_corrupt_tail_rejected_and_bytes_unchanged(self):
        self.ledger.add_customer("합성 거래처")
        self.ledger.db.execute("DELETE FROM audit_events WHERE seq=1")
        self.ledger.close()
        raw_before = hashlib.sha256(self.path.read_bytes()).hexdigest()
        with self.assertRaisesRegex(DeskError, "high-water"):
            Desk(self.path, allow_create=False)
        self.assertEqual(raw_before, hashlib.sha256(self.path.read_bytes()).hexdigest())

    def test_fresh_ledger_has_no_false_alarm(self):
        self.assertEqual(self.ledger.verify_audit(), 0)
        customer = self.ledger.add_customer("합성 고객")
        self.assertTrue(customer)
        self.assertEqual(self.ledger.verify_audit(), 1)

    @unittest.skipUnless(os.name == "posix", "POSIX permission semantics")
    def test_checkpoint_file_is_private_even_under_permissive_umask(self):
        self.ledger.add_customer("합성 고객")
        target = self.folder / "checkpoint.json"
        saved = os.umask(0o022)
        try:
            proof = create_checkpoint(self.ledger, target)
        finally:
            os.umask(saved)
        self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o600)
        self.assertEqual(verify_checkpoint(self.ledger, target, expected_file_sha256=proof["file_sha256"])["tables_verified"], 6)
        self.assertNotIn("합성 고객", target.read_text(encoding="utf-8"))

    def test_checkpoint_refuses_overwrite_without_mutating_old_file(self):
        target = self.folder / "checkpoint.json"
        target.write_text("original kept", encoding="utf-8")
        with self.assertRaises(DeskError):
            create_checkpoint(self.ledger, target)
        self.assertEqual(target.read_text(encoding="utf-8"), "original kept")

    def test_checkpoint_changes_are_detected(self):
        proof = create_checkpoint(self.ledger, self.folder / "check.json")
        self.ledger.add_customer("새 합성 고객")
        with self.assertRaisesRegex(DeskError, "mismatch"):
            verify_checkpoint(self.ledger, self.folder / "check.json", expected_file_sha256=proof["file_sha256"])


if __name__ == "__main__":
    unittest.main()
