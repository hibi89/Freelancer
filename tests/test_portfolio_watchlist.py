"""Full three-module offline evidence test. Synthetic sources; no real government calls."""
from contextlib import closing
from pathlib import Path
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from uuid import uuid4

from bidax.core import BidLedger
from bidax.onbid import OnbidStore, DATASET_URLS
from bidax.court import CourtStore
from bidax.portfolio import filter_onbid, portfolio_report, watch_onbid, watchlist

ROOT = Path(__file__).resolve().parents[1]


def asset(amount=100000000):
    return {"property_id": "42", "condition_id": "4", "announcement_id": "8",
            "title": "가상 공매", "property_type": "부동산", "appraised_krw": 200000000,
            "minimum_bid_krw": amount, "failed_rounds": 2,
            "bid_start": "2026-11-20T10:00:00+09:00", "bid_end": "2026-11-25T17:00:00+09:00",
            "source_url": "https://www.data.go.kr/data/15157220/openapi.do"}


def snapshot(a):
    return {"source": "ONBID_LOCAL_AUTHORIZED_SNAPSHOT", "dataset": "assets",
            "documentation_url": DATASET_URLS["assets"],
            "obtained_at": "2026-11-14T07:00:00+09:00", "records": [a]}


class PortfolioFlow(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.root = Path(t.name)
        self.db = self.root / "evidence.db"
        with BidLedger(self.db) as g2b:
            g2b.ingest([{
                "notice_no": "42", "revision": "1", "title": "가상 발주",
                "category": "goods", "issuer": "기관", "deadline": "2026-11-30T12:00:00+09:00",
                "source_url": "https://www.g2b.go.kr/", "regions": [],
                "license_codes": [], "required_documents": []}])
        with OnbidStore(self.db) as onbid:
            onbid.import_snapshot(snapshot(asset()))
        self.doc = self.root / "source.txt"
        self.doc.write_text("가상 사건 점유자 유치권", encoding="utf-8")
        with CourtStore(self.db) as court:
            court.import_document(self.doc, case_id="2026-42", user_consent=True,
                                  source_note="본인이 작성한 합성 테스트 파일")

    def test_three_distinct_sources_same_numeric_id(self):
        rep = portfolio_report(self.db)
        self.assertEqual([rep[k]["count"] for k in ("g2b", "onbid", "court")], [1, 1, 1])
        self.assertEqual(rep["g2b"]["notices"][0]["notice_no"], "42")
        self.assertEqual(rep["onbid"]["assets"][0]["property_id"], "42")
        self.assertEqual(rep["court"]["cases"][0]["case_id"], "2026-42")
        self.assertFalse(rep["legal_or_investment_approval"])
        self.assertFalse(rep["authoritative_live_lookup"])

    def test_filter_amount_and_failed_rounds(self):
        self.assertEqual(filter_onbid(self.db, max_bid_krw=100000000, min_failed_rounds=2)["matches"], 1)
        self.assertEqual(filter_onbid(self.db, max_bid_krw=99999999)["matches"], 0)
        self.assertEqual(filter_onbid(self.db, min_failed_rounds=3)["matches"], 0)
        self.assertEqual(filter_onbid(self.db, property_type="차량")["matches"], 0)
        self.assertFalse(filter_onbid(self.db)["investment_qualified"])

    def test_filter_validation_fails_closed(self):
        for kw in (dict(max_bid_krw=True), dict(max_bid_krw=-1),
                   dict(min_failed_rounds=-1), dict(property_type="법원")):
            with self.subTest(kw=kw), self.assertRaises(ValueError):
                filter_onbid(self.db, **kw)

    def test_watch_idempotent_exact_uuid(self):
        request = str(uuid4())
        args = dict(property_id="42", condition_id="4", state="관심", note="원문 검토 예정", request_id=request)
        self.assertTrue(watch_onbid(self.db, **args)["written"])
        self.assertTrue(watch_onbid(self.db, **args)["replay"])
        rep = watchlist(self.db)
        self.assertEqual(rep["audited_events"], 1)
        self.assertEqual(rep["active_count"], 1)
        self.assertFalse(rep["items"][0]["source_changed_since_watch"])

    def test_watch_replay_conflict_rejected(self):
        request = str(uuid4())
        args = dict(property_id="42", condition_id="4", state="관심", note="첫 요청", request_id=request)
        watch_onbid(self.db, **args)
        with self.assertRaisesRegex(ValueError, "conflicting"):
            watch_onbid(self.db, **{**args, "note": "변조된 재시도"})

    def test_watch_stale_after_new_asset_version(self):
        watch_onbid(self.db, property_id="42", condition_id="4", state="검토 보류",
                    note="변경 검토", request_id=str(uuid4()))
        changed = asset(amount=90000000)
        with OnbidStore(self.db) as store:
            store.import_snapshot({**snapshot(changed), "obtained_at": "2026-11-15T07:00:00+09:00"})
        self.assertTrue(watchlist(self.db)["items"][0]["source_changed_since_watch"])

    def test_watch_marked_inactive_keeps_audit(self):
        base = dict(property_id="42", condition_id="4")
        watch_onbid(self.db, **base, state="관심", note="관심", request_id=str(uuid4()))
        watch_onbid(self.db, **base, state="관심 해제", note="고객 수동 해제", request_id=str(uuid4()))
        rep = watchlist(self.db)
        self.assertEqual(rep["audited_events"], 2)
        self.assertEqual(rep["active_count"], 0)
        self.assertEqual(rep["items"][0]["state"], "관심 해제")

    def test_watch_requires_existing_asset(self):
        with self.assertRaises(ValueError):
            watch_onbid(self.db, property_id="99", condition_id="4", state="관심",
                        note="없는 물건", request_id=str(uuid4()))
        self.assertEqual(watchlist(self.db)["audited_events"], 0)

    def test_watch_rejects_invalid_request_id_and_note(self):
        for request, note in (("none", "메모"), (str(uuid4()), "\n")):
            with self.assertRaises(ValueError):
                watch_onbid(self.db, property_id="42", condition_id="4", state="관심",
                            note=note, request_id=request)

    def test_watch_tamper_quarantined(self):
        watch_onbid(self.db, property_id="42", condition_id="4", state="관심",
                    note="감사 기록", request_id=str(uuid4()))
        with closing(sqlite3.connect(self.db)) as conn:
            with conn:
                conn.execute("UPDATE onbid_watch_events SET state='관심 해제'")
        with self.assertRaisesRegex(ValueError, "tampered"):
            watchlist(self.db)
        with self.assertRaisesRegex(ValueError, "tampered"):
            watch_onbid(self.db, property_id="42", condition_id="4", state="관심",
                        note="두번째", request_id=str(uuid4()))

    def test_portfolio_rejects_missing_db(self):
        with self.assertRaisesRegex(ValueError, "existing"):
            portfolio_report(self.root / "missing.db")
        self.assertFalse((self.root / "missing.db").exists())

    def test_cli_portfolio_and_watchlist(self):
        def run(*args):
            proc = subprocess.run([sys.executable, "-m", "bidax.cli", "--db", str(self.db), *args],
                                  cwd=ROOT, capture_output=True, text=True, check=True, timeout=12)
            return json.loads(proc.stdout)
        self.assertEqual(run("portfolio-report")["onbid"]["count"], 1)
        self.assertEqual(run("onbid-filter", "--max-bid-krw", "100000000")["matches"], 1)
        self.assertTrue(run("onbid-watch", "42", "4", "관심", "현장 확인 예정")["written"])
        self.assertEqual(run("onbid-watchlist")["active_count"], 1)


if __name__ == "__main__":
    unittest.main()

class GUIControllerPortfolio(unittest.TestCase):
    def test_controller_methods_roundtrip(self):
        from bidax.desktop import LocalController
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / 'data.db'
            with OnbidStore(db) as store:
                store.import_snapshot(snapshot(asset()))
            gui = LocalController(db)
            self.assertEqual(gui.onbid_filter(max_bid_krw=100000000)['matches'], 1)
            self.assertEqual(gui.portfolio_report()['onbid']['count'], 1)
            gui.onbid_watch('42','4','관심','원문 확인 예정')
            self.assertEqual(gui.onbid_watchlist()['active_count'], 1)

class ReadOnlyWatchlist(unittest.TestCase):
    def test_reading_empty_watchlist_does_not_create_table(self):
        with tempfile.TemporaryDirectory() as td:
            db = Path(td)/'db.sqlite'
            with OnbidStore(db) as store:
                store.import_snapshot(snapshot(asset()))
            self.assertEqual(watchlist(db)['audited_events'], 0)
            with closing(sqlite3.connect(db)) as conn:
                self.assertIsNone(conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='onbid_watch_events'").fetchone())

class NonBidaxDatabaseProtection(unittest.TestCase):
    def test_portfolio_rejects_unrecognized_sqlite_without_migration(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'unrelated.db'
            with closing(sqlite3.connect(path)) as db:
                db.execute('CREATE TABLE other_system(id INTEGER)')
            with self.assertRaisesRegex(ValueError, 'none of the three source ledgers'):
                portfolio_report(path)
            with closing(sqlite3.connect(path)) as db:
                tables = {x[0] for x in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            self.assertEqual(tables, {'other_system'})
