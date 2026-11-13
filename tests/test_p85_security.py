"""BID AX P85 follow-up: offline evidence tamper and opt-in transport regression."""
from __future__ import annotations
import io
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError
from uuid import uuid4
from bidax.batch import batch_status, stage_snapshot
from bidax.core import BidLedger
from bidax.transport import fetch_one_page

NOW = datetime(2026, 11, 13, 7, 30, tzinfo=timezone.utc)
END = NOW + timedelta(days=2)
ROW = {"bidNtceNo": "N1", "bidNtceOrd": "000", "bidNtceNm": "공고",
       "ntceInsttNm": "발주처", "bidClseDt": "202611171800",
       "bidNtceDtlUrl": "https://www.g2b.go.kr/sample"}

def snapshot(rows, *, page=1, total=1):
    return {"response": {"header": {"resultCode": "00"},
            "body": {"pageNo": page, "numOfRows": 1, "totalCount": total,
                     "items": {"item": rows}}}}

class StubResponse:
    status = 200
    headers = {"Content-Type": "application/json"}
    def __init__(self, data):
        self.data = data
    def __enter__(self):
        return self
    def __exit__(self, *_):
        pass
    def read(self, _):
        return self.data

class StubOpener:
    def __init__(self, failures, success=None):
        self.failures = list(failures)
        self.success = success or json.dumps(snapshot([ROW])).encode()
        self.calls = 0
    def open(self, request, timeout):
        self.calls += 1
        if self.failures:
            raise self.failures.pop(0)
        return StubResponse(self.success)

class TestP85Security(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / "bidax.db"
        self.batch = str(uuid4())

    def test_completed_batch_status_rejects_damaged_page(self):
        with BidLedger(self.path) as ledger:
            stage_snapshot(ledger, self.batch, "goods", NOW, END, snapshot([ROW]), NOW)
            self.assertTrue(batch_status(ledger, self.batch)["completed"])
            with ledger.conn:
                ledger.conn.execute("UPDATE snapshot_pages SET payload='[]' WHERE batch_id=?",
                                    (self.batch.replace("-", ""),))
            with self.assertRaisesRegex(ValueError, "tampered"):
                batch_status(ledger, self.batch)

    def test_completed_replay_rejects_other_page_corruption(self):
        with BidLedger(self.path) as ledger:
            stage_snapshot(ledger, self.batch, "goods", NOW, END,
                           snapshot([dict(ROW, bidNtceNo="N1")], page=1, total=2), NOW)
            stage_snapshot(ledger, self.batch, "goods", NOW, END,
                           snapshot([dict(ROW, bidNtceNo="N2")], page=2, total=2), NOW)
            with ledger.conn:
                ledger.conn.execute("UPDATE snapshot_pages SET payload='[]' WHERE batch_id=? AND page_no=2",
                                    (self.batch.replace("-", ""),))
            with self.assertRaisesRegex(ValueError, "tampered"):
                stage_snapshot(ledger, self.batch, "goods", NOW, END,
                               snapshot([dict(ROW, bidNtceNo="N1")], page=1, total=2), NOW)

    def test_permission_requires_boolean_true(self):
        with BidLedger(self.path) as ledger:
            fake = StubOpener([])
            for invalid in (1, "true", None, False, {}, []):
                with self.subTest(invalid=repr(invalid)), self.assertRaises(PermissionError):
                    fetch_one_page(ledger, category="goods", start=NOW, end=END, page=1,
                                   service_key="FAKE-KEY", permission=invalid, opener=fake)
            self.assertEqual(fake.calls, 0)

    def test_unexpected_url_exception_never_echoes_key(self):
        with BidLedger(self.path) as ledger:
            for error in (RuntimeError("URL includes FAKE-KEY"), ValueError("FAKE-KEY redirect")):
                with self.subTest(error=type(error).__name__):
                    fake = StubOpener([error])
                    with self.assertRaisesRegex(ValueError, "key redacted") as caught:
                        fetch_one_page(ledger, category="goods", start=NOW, end=END,
                                       page=1, service_key="FAKE-KEY", permission=True,
                                       opener=fake, now=NOW)
                    self.assertNotIn("FAKE-KEY", str(caught.exception))
                    self.assertEqual(fake.calls, 1)

    def test_timeout_retry_is_bounded_and_counts(self):
        with BidLedger(self.path) as ledger:
            fake = StubOpener([TimeoutError("temporary")])
            sleeps = []
            result = fetch_one_page(ledger, category="goods", start=NOW, end=END,
                                    page=1, service_key="FAKE-KEY", permission=True,
                                    opener=fake, now=NOW, sleep=sleeps.append, daily_limit=2)
            self.assertEqual(result["response"]["header"]["resultCode"], "00")
            self.assertEqual(fake.calls, 2)
            self.assertEqual(sleeps, [1])
            self.assertEqual(ledger.conn.execute("SELECT count FROM api_attempts").fetchone()[0], 2)

    def test_timeout_never_exceeds_budget(self):
        with BidLedger(self.path) as ledger:
            fake = StubOpener([TimeoutError("temporary")])
            with self.assertRaisesRegex(ValueError, "budget exhausted"):
                fetch_one_page(ledger, category="goods", start=NOW, end=END,
                               page=1, service_key="FAKE-KEY", permission=True,
                               opener=fake, now=NOW, sleep=lambda _: None, daily_limit=1)
            self.assertEqual(fake.calls, 1)

    def test_http_403_error_is_redacted_not_retried(self):
        with BidLedger(self.path) as ledger:
            fake = StubOpener([HTTPError("https://example/FAKE-KEY", 403, "forbidden",
                                         {}, io.BytesIO())])
            with self.assertRaisesRegex(ValueError, "key redacted") as caught:
                fetch_one_page(ledger, category="goods", start=NOW, end=END,
                               page=1, service_key="FAKE-KEY", permission=True,
                               opener=fake, now=NOW)
            self.assertNotIn("FAKE-KEY", str(caught.exception))
            self.assertEqual(fake.calls, 1)

if __name__ == "__main__":
    unittest.main()
