"""Synthetic-only P85 volume/recovery validation (NOT real procurement cases)."""
from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

from bidax.batch import batch_status, stage_snapshot
from bidax.core import BidLedger, restore_backup
from bidax.workflow import build_report

NOW = datetime(2026, 11, 13, 7, 30, tzinfo=timezone.utc)
START = NOW - timedelta(days=6)
TOTAL = 100
PAGE_SIZE = 20


def snapshot(page):
    rows = [
        {"bidNtceNo": f"SYNTHETIC-{i:04d}", "bidNtceOrd": "000",
         "bidNtceNm": f"합성 시험 공고 {i}", "ntceInsttNm": "가상 발주처",
         "bidClseDt": "202611171800",
         "bidNtceDtlUrl": "https://www.g2b.go.kr/synthetic-only"}
        for i in range((page-1)*PAGE_SIZE+1, page*PAGE_SIZE+1)
    ]
    return {"response": {"header": {"resultCode": "00"},
                         "body": {"pageNo": page, "numOfRows": PAGE_SIZE,
                                  "totalCount": TOTAL, "items": {"item": rows}}}}


class SyntheticVolumeAcceptance(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.db = self.root / "bidax.db"
        self.batch_id = str(uuid4())

    def stage(self, ledger, page, payload=None):
        return stage_snapshot(ledger, self.batch_id, "goods", START, NOW,
                              snapshot(page) if payload is None else payload, NOW)

    def prepare(self):
        with BidLedger(self.db) as ledger:
            for page in (5, 3, 1):
                self.assertFalse(self.stage(ledger, page)["completed"])
                self.assertEqual(ledger.current(), [])
        with BidLedger(self.db) as ledger:
            self.assertEqual(batch_status(ledger, self.batch_id)["missing_pages"], [2, 4])
            self.stage(ledger, 4)
            done = self.stage(ledger, 2)
            self.assertTrue(done["completed"])
            self.assertEqual(done["added_versions"], TOTAL)
            self.assertEqual(len(ledger.current()), TOTAL)

    def test_100_synthetic_notices_across_restarts(self):
        self.prepare()
        with BidLedger(self.db) as ledger:
            self.assertEqual(self.stage(ledger, 5)["added_versions"], 0)
            self.assertEqual(len(ledger.current()), TOTAL)
            ledger.verify_integrity()

    def test_no_synthetic_notice_auto_qualified(self):
        self.prepare()
        profile = {"company": "합성 기업", "regions": ["전국"],
                   "license_codes": [], "documents": {}}
        with BidLedger(self.db) as ledger:
            report = build_report(ledger, profile, now=NOW)
            self.assertEqual(report["count"], TOTAL)
            self.assertEqual(report["summary"]["추가 확인 필요"], TOTAL)
            self.assertEqual(report["summary"]["적합"], 0)
            for record in report["results"]:
                self.assertTrue(record["needs_review"])

    def test_10_simulated_reviews_survive_create_only_restore(self):
        self.prepare()
        with BidLedger(self.db) as ledger:
            for notice in ledger.current()[:10]:
                ledger.record_review(notice["notice_no"], notice["fingerprint"],
                                     "synthetic-test-operator", "보류",
                                     "합성 감사기록, 실제 사람이 검토하지 않음",
                                     request_id=str(uuid4()), now=NOW)
            self.assertEqual(ledger.conn.execute("SELECT count(*) FROM manual_reviews").fetchone()[0], 10)
            ledger.backup(self.root / "backup.db")
        result = restore_backup(self.root / "backup.db", self.root / "restored.db")
        self.assertTrue(result["original_preserved"])
        with BidLedger(self.root / "restored.db") as ledger:
            self.assertEqual(len(ledger.current()), TOTAL)
            self.assertEqual(ledger.conn.execute("SELECT count(*) FROM manual_reviews").fetchone()[0], 10)
            ledger.verify_integrity()
        with self.assertRaises(FileExistsError):
            restore_backup(self.root / "backup.db", self.root / "restored.db")

    def test_incomplete_final_page_rejected_atomically(self):
        incomplete = snapshot(5)
        incomplete["response"]["body"]["items"]["item"].pop()
        with BidLedger(self.db) as ledger:
            for page in (1, 2, 3, 4):
                self.stage(ledger, page)
            with self.assertRaisesRegex(ValueError, "incomplete page"):
                self.stage(ledger, 5, incomplete)
            self.assertEqual(ledger.current(), [])
            self.assertEqual(batch_status(ledger, self.batch_id)["missing_pages"], [5])


if __name__ == "__main__":
    unittest.main()
