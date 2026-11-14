"""BID AX bounded Onbid pagination: offline synthetic payloads, never real HTTP."""
from __future__ import annotations

from contextlib import closing, redirect_stdout
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit
from uuid import uuid4

from bidax.api_gateway import create_plan, fetch_quarantined
from bidax.onbid_batch import batch_status
from bidax.onbid_capture import continue_onbid_pages


class Reply:
    status = 200
    headers = {"Content-Type": "application/json"}

    def __init__(self, payload):
        self.data = json.dumps(payload).encode("utf-8")

    def read(self, count):
        return self.data[:count]

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None


class FakeOnbid:
    def __init__(self, total=21, *, wrong_total_page=None):
        self.total = total
        self.wrong_total_page = wrong_total_page
        self.pages_requested = []

    def open(self, request, timeout=15):
        params = parse_qs(urlsplit(request.full_url).query)
        page = int(params["pageNo"][0])
        rows = int(params["numOfRows"][0])
        self.pages_requested.append(page)
        total = self.total + (1 if page == self.wrong_total_page else 0)
        count = max(0, min(rows, total - (page - 1) * rows))
        return Reply({
            "header": {"resultCode": "00"},
            "body": {
                "pageNo": page, "numOfRows": rows, "totalCount": total,
                "items": {"item": [{"SYNTHETIC_NOT_REAL": i} for i in range(count)]},
            },
        })


class ContinueOnbidTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.db = self.root / "local-test.db"
        self.batch = str(uuid4())
        self.key = "OFFLINE_FAKE_KEY"
        self.when = datetime(2026, 11, 14, tzinfo=timezone.utc)
        self.filters = {
            "cltrTypeCd": "0001", "prptDivCd": "0002",
            "opbdDtStart": "20261110", "opbdDtEnd": "20261113",
        }

    def ref(self, total=21):
        plan = create_plan("onbid_result_list", {
            "parameters": self.filters, "page": 1, "rows": 10})
        dest = self.root / "first-official-like-quarantine.json"
        fetch_quarantined(
            plan, service_key=self.key, permission=True, db_path=self.root / "ref-quota.db",
            output_path=dest, daily_limit=20, opener=FakeOnbid(total),
            now=self.when, max_attempts=1)
        return dest

    def go(self, source, *, live=True, opener=None, max_new_pages=4,
           service_key="OFFLINE_FAKE_KEY", consent=True, **kwargs):
        return continue_onbid_pages(
            self.db, self.batch, source, self.root,
            consent=consent, live=live, service_key=service_key if live else None,
            opener=opener, max_new_pages=max_new_pages, now=self.when, **kwargs)

    def test_dry_plan_never_touches_db_or_network(self):
        ref = self.ref(total=186)
        opener = FakeOnbid(186)
        status = self.go(ref, live=False, opener=opener)
        self.assertEqual(status["state"], "OFFLINE_DRY_PLAN_NO_NETWORK")
        self.assertEqual(status["reported_total_pages"], 19)
        self.assertEqual(status["other_pages_missing_or_unverified"], list(range(2, 20)))
        self.assertEqual(status["network_calls"], 0)
        self.assertEqual(opener.pages_requested, [])
        self.assertFalse(self.db.exists())

    def test_single_run_21_results_3_pages_and_sealed(self):
        ref = self.ref()
        fake = FakeOnbid(21)
        result = self.go(ref, opener=fake)
        self.assertEqual(fake.pages_requested, [2, 3])
        self.assertEqual(result["new_http_calls_this_run"], 2)
        self.assertEqual(result["verified_local_item_count"], 21)
        self.assertEqual(result["missing_pages"], [])
        self.assertEqual(result["state"], "OFFLINE_COMPLETE_NOT_IMPORTED")
        self.assertFalse(result["auto_import_allowed"])
        self.assertFalse(result["source_field_mapping_verified"])
        with closing(sqlite3.connect(self.db)) as conn:
            rows = conn.execute("SELECT count FROM api_gateway_attempts WHERE service='onbid_result_list'").fetchone()
            self.assertEqual(rows[0], 2)
            dumped = "\n".join(conn.iterdump())
            self.assertNotIn(self.key, dumped)
            self.assertNotIn("SYNTHETIC_NOT_REAL", dumped)

    def test_resume_only_missing_pages_and_no_duplicate_http(self):
        ref = self.ref()
        first = FakeOnbid(21)
        partial = self.go(ref, opener=first, max_new_pages=1)
        self.assertEqual(partial["missing_pages"], [3])
        self.assertEqual(first.pages_requested, [2])
        second = FakeOnbid(21)
        done = self.go(ref, opener=second, max_new_pages=1)
        self.assertEqual(second.pages_requested, [3])
        self.assertEqual(done["new_http_calls_this_run"], 1)
        third = FakeOnbid(21)
        replay = self.go(ref, opener=third)
        self.assertEqual(replay["new_http_calls_this_run"], 0)
        self.assertEqual(third.pages_requested, [])
        self.assertEqual(replay["state"], "OFFLINE_COMPLETE_NOT_IMPORTED")

    def test_saved_after_crash_reused_without_network(self):
        ref = self.ref(total=11)
        page2 = create_plan("onbid_result_list", {
            "parameters": self.filters, "page": 2, "rows": 10})
        local = self.root / f"bidax-onbid-{self.batch}-p0002.json"
        fetch_quarantined(page2, service_key=self.key, permission=True,
                          db_path=self.root / "separate-previous-quota.db",
                          output_path=local, opener=FakeOnbid(11), now=self.when)
        fake = FakeOnbid(11)
        result = self.go(ref, opener=fake)
        self.assertEqual(result["new_http_calls_this_run"], 0)
        self.assertEqual(result["existing_saved_packets_recovered"], 1)
        self.assertEqual(fake.pages_requested, [])
        self.assertEqual(result["state"], "OFFLINE_COMPLETE_NOT_IMPORTED")

    def test_bad_existing_local_packet_stops_without_overwrite_or_network(self):
        ref = self.ref()
        cached = self.root / f"bidax-onbid-{self.batch}-p0002.json"
        cached.write_bytes(b"invalid-customer-file")
        fake = FakeOnbid()
        with self.assertRaises(ValueError):
            self.go(ref, opener=fake)
        self.assertEqual(cached.read_bytes(), b"invalid-customer-file")
        self.assertEqual(fake.pages_requested, [])
        self.assertEqual(batch_status(self.db, self.batch)["missing_pages"], [2, 3])

    def test_provider_total_change_fails_closed_and_keeps_packet(self):
        ref = self.ref()
        fake = FakeOnbid(21, wrong_total_page=2)
        with self.assertRaises(ValueError):
            self.go(ref, opener=fake)
        self.assertEqual(fake.pages_requested, [2])
        self.assertTrue((self.root / f"bidax-onbid-{self.batch}-p0002.json").exists())
        self.assertEqual(batch_status(self.db, self.batch)["verified_local_pages"], [1])

    def test_budget_cap_blocks_second_call_preserving_first(self):
        ref = self.ref()
        fake = FakeOnbid(21)
        with self.assertRaises(ValueError):
            self.go(ref, opener=fake, daily_limit=1)
        self.assertEqual(fake.pages_requested, [2])
        self.assertEqual(batch_status(self.db, self.batch)["verified_local_pages"], [1, 2])

    def test_consent_key_and_bounds_reject_before_network_and_new_db(self):
        ref = self.ref()
        for kw in (
            {"consent": False},
            {"service_key": ""},
            {"max_new_pages": 0},
            {"max_new_pages": 26},
            {"daily_limit": 0},
        ):
            fake = FakeOnbid()
            with self.subTest(kw=kw), self.assertRaises((PermissionError, ValueError)):
                self.go(ref, opener=fake, **kw)
            self.assertEqual(fake.pages_requested, [])
            self.assertFalse(self.db.exists())

    def test_malformed_batch_id_rejected_before_network(self):
        ref = self.ref()
        fake = FakeOnbid()
        with self.assertRaises(ValueError):
            continue_onbid_pages(self.db, "unsafe/uuid", ref, self.root,
                                 consent=True, live=True, service_key=self.key,
                                 opener=fake)
        self.assertEqual(fake.pages_requested, [])
        self.assertFalse(self.db.exists())

    def test_cli_offline_dry_mode_no_prompt_and_no_db(self):
        from bidax.cli import main
        ref = self.ref()
        out = io.StringIO()
        argv = ["--db", str(self.db), "onbid-continue", self.batch,
                str(ref), "--out-dir", str(self.root), "--consent"]
        with patch("getpass.getpass", side_effect=AssertionError("must not prompt")):
            with redirect_stdout(out):
                main(argv)
        data = json.loads(out.getvalue())
        self.assertEqual(data["network_calls"], 0)
        self.assertFalse(self.db.exists())


if __name__ == "__main__":
    unittest.main()
