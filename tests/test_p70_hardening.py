"""Regression tests for offline G2B snapshot quarantine and persistent profiles."""
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from bidax.cli import main
from bidax.core import BidLedger, evaluate, restore_backup
from bidax.desktop import LocalController
from bidax.official import parse_official_snapshot

AT = datetime(2026, 11, 13, 16, 0, tzinfo=timezone.utc)
PROFILE = {"company": "샘플기업", "regions": ["부산"], "license_codes": ["AA"],
           "documents": {"사업자등록증": "2027-12-31"}, "max_budget_krw": 5000000}
ROW = {"bidNtceNo": "202611130001", "bidNtceOrd": "000", "bidNtceNm": "샘플 물품 공고",
       "ntceInsttNm": "기관", "bidClseDt": "202611171800", "bidNtceDtlUrl": "https://www.g2b.go.kr/sample"}


def snapshot(rows=None, **body_overrides):
    body = {"totalCount": 1, "pageNo": 1, "numOfRows": 100,
            "items": {"item": [dict(ROW)] if rows is None else rows}}
    body.update(body_overrides)
    return {"response": {"header": {"resultCode": "00", "resultMsg": "NORMAL SERVICE"},
                         "body": body}}


class P70HardeningTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = Path(self.tmp.name) / "bid.db"

    def test_offline_snapshot_forces_manual_review(self):
        parsed = parse_official_snapshot(snapshot(), "goods", AT)
        self.assertEqual(parsed["total_count"], 1)
        self.assertEqual(len(parsed["snapshot_sha256"]), 64)
        with BidLedger(self.db) as ledger:
            self.assertEqual(ledger.ingest(parsed["notices"])["added_versions"], 1)
            notice = ledger.current()[0]
            report = evaluate(notice, PROFILE, AT)
            self.assertEqual(report["status"], "추가 확인 필요")
            self.assertIn("공식 API", " ".join(report["needs_review"]))
            self.assertEqual(notice["raw_snapshot_sha256"], parsed["snapshot_sha256"])

    def test_official_snapshot_idempotent_and_revision(self):
        first = parse_official_snapshot(snapshot(), "goods", AT)
        revised = parse_official_snapshot(snapshot([dict(ROW, bidNtceOrd="001", bidNtceNm="수정 공고")]), "goods", AT)
        with BidLedger(self.db) as ledger:
            self.assertEqual(ledger.ingest(first["notices"])["added_versions"], 1)
            self.assertEqual(ledger.ingest(first["notices"])["added_versions"], 0)
            self.assertEqual(ledger.ingest(revised["notices"])["added_versions"], 1)
            self.assertEqual([x["change_kind"] for x in ledger.changes(ROW["bidNtceNo"])], ["NEW", "REVISED"])

    def test_official_auth_error_rejected(self):
        s = snapshot()
        s["response"]["header"]["resultCode"] = "30"
        with self.assertRaisesRegex(ValueError, "not success"):
            parse_official_snapshot(s, "goods", AT)

    def test_official_missing_ambiguous_deadline_rejected(self):
        with self.assertRaisesRegex(ValueError, "bidClseDt missing"):
            parse_official_snapshot(snapshot([dict(ROW, bidClseDt=None)]), "goods", AT)
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            parse_official_snapshot(snapshot([dict(ROW, bidClseDt="2026-11-17")]), "goods", AT)

    def test_official_url_spoofing_and_atomicity(self):
        with self.assertRaisesRegex(ValueError, "official HTTPS"):
            parse_official_snapshot(snapshot([dict(ROW, bidNtceDtlUrl="https://www.g2b.go.kr.evil.test/")]), "goods", AT)
        good_bad = snapshot([dict(ROW), dict(ROW, bidNtceDtlUrl="https://evil.test")], totalCount=2)
        with BidLedger(self.db) as ledger:
            with self.assertRaises(ValueError):
                parsed = parse_official_snapshot(good_bad, "goods", AT)
                ledger.ingest(parsed["notices"])
            self.assertEqual(ledger.current(), [])

    def test_official_invalid_envelope_or_pagination(self):
        for bad in ({}, {"response": {"header": {"resultCode": "00"}}},
                    snapshot([], totalCount=9), snapshot(numOfRows=0), snapshot(pageNo="x")):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                parse_official_snapshot(bad, "goods", AT)

    def test_official_time_must_be_timezone_aware(self):
        with self.assertRaises(ValueError):
            parse_official_snapshot(snapshot(), "goods", datetime(2026, 11, 13))

    def test_persist_profile_idempotent_and_revisions(self):
        with BidLedger(self.db) as ledger:
            self.assertTrue(ledger.save_profile(PROFILE, AT)["new_version"])
            self.assertFalse(ledger.save_profile(PROFILE, AT)["new_version"])
            self.assertEqual(len(ledger.list_profiles()), 1)
            self.assertEqual(ledger.get_profile(PROFILE["company"]), PROFILE)
            modified = dict(PROFILE, license_codes=["BB"])
            self.assertTrue(ledger.save_profile(modified, AT)["new_version"])
            self.assertEqual(ledger.get_profile(PROFILE["company"])["license_codes"], ["BB"])
            self.assertEqual(len(ledger.profile_history(PROFILE["company"])), 2)

    def test_profiles_separate_businesses(self):
        with BidLedger(self.db) as ledger:
            ledger.save_profile(PROFILE, AT)
            ledger.save_profile(dict(PROFILE, company="다른기업"), AT)
            self.assertEqual(len(ledger.list_profiles()), 2)
            with self.assertRaises(KeyError):
                ledger.get_profile("유령회사")

    def test_profile_tamper_detected_and_backup_restores(self):
        backup = Path(self.tmp.name) / "backup.db"
        with BidLedger(self.db) as ledger:
            ledger.save_profile(PROFILE, AT)
            ledger.backup(backup)
            with ledger.conn:
                ledger.conn.execute("UPDATE profile_events SET payload='{}'")
            with self.assertRaisesRegex(ValueError, "fingerprint"):
                ledger.get_profile(PROFILE["company"])
        restored = Path(self.tmp.name) / "restored.db"
        restore_backup(backup, restored)
        with BidLedger(restored) as ledger:
            self.assertEqual(ledger.get_profile(PROFILE["company"]), PROFILE)

    def test_controller_stored_profile_workflow(self):
        fp = Path(self.tmp.name) / "profile.json"
        fp.write_text(json.dumps(PROFILE, ensure_ascii=False), encoding="utf-8")
        controller = LocalController(self.db)
        with self.assertRaisesRegex(ValueError, "먼저"):
            controller.save_current_profile()
        controller.load_profile(fp)
        self.assertTrue(controller.save_current_profile()["new_version"])
        self.assertEqual(len(controller.stored_profiles()), 1)
        again = LocalController(self.db)
        self.assertEqual(again.use_stored_profile(PROFILE["company"]), PROFILE)

    def test_cli_snapshot_and_profiles(self):
        import contextlib
        from io import StringIO
        path = Path(self.tmp.name) / "official.json"
        path.write_text(json.dumps(snapshot(), ensure_ascii=False), encoding="utf-8")
        pp = Path(self.tmp.name) / "profile.json"
        pp.write_text(json.dumps(PROFILE, ensure_ascii=False), encoding="utf-8")
        def run(*args):
            out = StringIO()
            with contextlib.redirect_stdout(out):
                main(["--db", str(self.db), *args])
            return json.loads(out.getvalue())
        imported = run("import-official-snapshot", str(path), "--category", "goods", "--obtained-at", AT.isoformat())
        self.assertEqual(imported["added_versions"], 1)
        run("profile-save", str(pp))
        self.assertEqual(len(run("profiles")["companies"]), 1)
        report = run("screen-stored", PROFILE["company"])
        self.assertEqual(report["count"], 1)
        self.assertEqual(report["summary"]["추가 확인 필요"], 1)

    def test_offline_duplicate_json_key_rejected(self):
        from bidax.workflow import read_local_json
        path = Path(self.tmp.name) / "dup.json"
        path.write_text('{"company": "one", "company": "two"}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            read_local_json(path)

    def test_official_zero_total_nonempty_rejected(self):
        with self.assertRaisesRegex(ValueError, "contradicts"):
            parse_official_snapshot(snapshot(totalCount=0), "goods", AT)

    def test_official_rejects_unsupported_kind(self):
        with self.assertRaises(ValueError):
            parse_official_snapshot(snapshot(), "none", AT)


if __name__ == "__main__":
    unittest.main()
