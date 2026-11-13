"""BID AX stage-70 offline end-to-end and security regression tests."""
import csv
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from io import StringIO
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from uuid import uuid4

from bidax.cli import main
from bidax.core import BidLedger, restore_backup
from bidax.desktop import LocalController
from bidax.workflow import build_report, due_alerts, report_csv, report_html, write_new_report

T = timezone(timedelta(hours=9))
NOW = datetime(2026, 11, 13, 15, 0, tzinfo=T)
NOTICE = {"notice_no":"R26BK700001", "revision":"000", "title":"서버 유지보수", "category":"services",
          "issuer":"합성 발주처", "deadline":"2026-11-14T16:00:00+09:00",
          "source_url":"https://www.g2b.go.kr/notice/R26BK700001", "regions":["부산"],
          "license_codes":["S/W"], "required_documents":["사업자등록증"], "budget_min_krw":3000000}
PROFILE = {"company":"합성 업체", "regions":["부산"], "license_codes":["S/W"],
           "documents":{"사업자등록증":"2026-12-31"}, "max_budget_krw":4000000}


class Stage70Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.db = self.dir / "ledger.db"

    def make_ledger(self, records=None):
        ledger = BidLedger(self.db)
        ledger.ingest([NOTICE] if records is None else records, NOW)
        return ledger

    def test_report_counts_and_provenance(self):
        with self.make_ledger() as ledger:
            report = build_report(ledger, PROFILE, NOW)
        self.assertEqual(report["scope"], "OFFLINE_PRELIMINARY_ONLY")
        self.assertEqual(report["count"], 1)
        self.assertEqual(report["summary"]["적합"], 1)
        self.assertEqual(report["results"][0]["title"], NOTICE["title"])
        self.assertEqual(len(report["results"][0]["source_fingerprint"]), 64)
        self.assertIn("원문", report["disclaimer"])

    def test_report_unknown_never_compliance_approved(self):
        with self.make_ledger() as ledger:
            profile = dict(PROFILE, license_codes=[])
            r = build_report(ledger, profile, NOW)
        self.assertEqual(r["summary"]["추가 확인 필요"], 1)

    def test_csv_formula_injection(self):
        malicious = dict(NOTICE, title="=HYPERLINK(\"http://evil\")")
        with self.make_ledger([malicious]) as ledger:
            report = build_report(ledger, PROFILE, NOW)
        csv_text = report_csv(report)
        parsed = list(csv.reader(StringIO(csv_text)))
        self.assertEqual(len(parsed), 2)
        self.assertTrue(parsed[1][2].startswith("'="))
        self.assertNotIn("http://evil", parsed[1][7])

    def test_html_escapes_user_notice(self):
        malicious = dict(NOTICE, title="<script>alert(1)</script>", issuer="<p>test</p>")
        with self.make_ledger([malicious]) as ledger:
            content = report_html(build_report(ledger, PROFILE, NOW))
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", content)
        self.assertNotIn("<script>", content)
        self.assertIn("Content-Security-Policy", content)

    def test_new_report_file_and_no_overwrite(self):
        with self.make_ledger() as ledger:
            report = build_report(ledger, PROFILE, NOW)
        target = self.dir / "report.csv"
        write_new_report(target, report, "csv")
        self.assertTrue(target.read_bytes().startswith(b"\xef\xbb\xbf"))
        before = target.read_bytes()
        with self.assertRaises(FileExistsError):
            write_new_report(target, report, "csv")
        self.assertEqual(target.read_bytes(), before)

    def test_html_and_json_new_reports(self):
        with self.make_ledger() as ledger:
            report = build_report(ledger, PROFILE, NOW)
        for fmt in ("json", "html"):
            path = self.dir / ("report." + fmt)
            write_new_report(path, report, fmt)
            self.assertTrue(path.read_bytes())
        self.assertEqual(json.loads((self.dir / "report.json").read_text())["count"], 1)

    def test_bad_format_rejected_without_file(self):
        target = self.dir / "report.pdf"
        with self.assertRaises(ValueError):
            write_new_report(target, {}, "pdf")
        self.assertFalse(target.exists())

    def test_due_alerts_upcoming(self):
        with self.make_ledger() as ledger:
            alerts = due_alerts(ledger, now=NOW, within_hours=48)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["state"], "마감 임박")

    def test_due_alerts_expired(self):
        with self.make_ledger() as ledger:
            alerts = due_alerts(ledger, now=NOW + timedelta(days=4))
        self.assertEqual(alerts[0]["state"], "마감 경과")

    def test_due_alerts_no_remote_or_future_far(self):
        with self.make_ledger() as ledger:
            self.assertEqual(due_alerts(ledger, now=NOW, within_hours=1), [])

    def test_due_alerts_invalid_hours(self):
        with self.make_ledger() as ledger:
            for bad in (0, 721, True):
                with self.subTest(bad=bad), self.assertRaises(ValueError):
                    due_alerts(ledger, now=NOW, within_hours=bad)

    def test_manual_review_append_only(self):
        with self.make_ledger() as ledger:
            fp = ledger.current()[0]["fingerprint"]
            row = ledger.record_review(NOTICE["notice_no"], fp, "검토 담당", "보류", "첨부 재확인", request_id=uuid4().hex, now=NOW)
            self.assertEqual(row["decision"], "보류")
            self.assertEqual(len(ledger.review_history(NOTICE["notice_no"])), 1)
            self.assertEqual(len(ledger.current()), 1)

    def test_manual_review_idempotent_retry(self):
        with self.make_ledger() as ledger:
            fp = ledger.current()[0]["fingerprint"]
            key = uuid4().hex
            a = ledger.record_review(NOTICE["notice_no"], fp, "홍길동", "확인", "원문 대조", request_id=key, now=NOW)
            b = ledger.record_review(NOTICE["notice_no"], fp, "홍길동", "확인", "원문 대조", request_id=key, now=NOW + timedelta(minutes=1))
            self.assertEqual(a, b)
            self.assertEqual(len(ledger.review_history(NOTICE["notice_no"])), 1)

    def test_manual_review_conflicting_request_id(self):
        with self.make_ledger() as ledger:
            fp = ledger.current()[0]["fingerprint"]
            key = uuid4().hex
            ledger.record_review(NOTICE["notice_no"], fp, "홍길동", "확인", "원문 대조", request_id=key, now=NOW)
            with self.assertRaises(ValueError):
                ledger.record_review(NOTICE["notice_no"], fp, "홍길동", "보류", "변조", request_id=key, now=NOW)
            self.assertEqual(len(ledger.review_history(NOTICE["notice_no"])), 1)

    def test_manual_review_stale_version_blocked(self):
        with self.make_ledger() as ledger:
            old_fp = ledger.current()[0]["fingerprint"]
            ledger.ingest([dict(NOTICE, revision="001", title="수정")], NOW)
            with self.assertRaises(ValueError):
                ledger.record_review(NOTICE["notice_no"], old_fp, "홍길동", "보류", "과거 버전", request_id=uuid4().hex)

    def test_manual_review_rejects_unsupported_decision(self):
        with self.make_ledger() as ledger:
            fp = ledger.current()[0]["fingerprint"]
            with self.assertRaises(ValueError):
                ledger.record_review(NOTICE["notice_no"], fp, "홍길동", "법적 승인", "불가", request_id=uuid4().hex)

    def test_manual_review_requires_reason(self):
        with self.make_ledger() as ledger:
            fp = ledger.current()[0]["fingerprint"]
            with self.assertRaises(ValueError):
                ledger.record_review(NOTICE["notice_no"], fp, "홍길동", "확인", "", request_id=uuid4().hex)

    def test_change_audit_diff(self):
        with self.make_ledger() as ledger:
            nextv = dict(NOTICE, revision="001", deadline="2026-11-15T16:00:00+09:00")
            ledger.ingest([nextv], NOW + timedelta(minutes=1))
            trail = ledger.changes(NOTICE["notice_no"])
        self.assertEqual([x["change_kind"] for x in trail], ["NEW", "REVISED"])
        self.assertIn("deadline", trail[1]["changed_fields"])
        self.assertNotIn("title", trail[1]["changed_fields"])

    def test_db_tamper_detected(self):
        with self.make_ledger() as ledger:
            with ledger.conn:
                ledger.conn.execute("UPDATE notice_events SET payload='{}'")
            with self.assertRaisesRegex(ValueError, "fingerprint"):
                ledger.current()

    def test_backup_restore_to_new_path(self):
        backup = self.dir / "backup.db"
        restored = self.dir / "restored.db"
        with self.make_ledger() as ledger:
            ledger.backup(backup)
        result = restore_backup(backup, restored)
        self.assertTrue(result["original_preserved"])
        with BidLedger(restored) as ledger:
            self.assertEqual(ledger.current()[0]["notice_no"], NOTICE["notice_no"])
        self.assertTrue(backup.exists())

    def test_restore_never_overwrites(self):
        backup = self.dir / "backup.db"
        with self.make_ledger() as ledger:
            ledger.backup(backup)
        original = self.db.read_bytes()
        with self.assertRaises(FileExistsError):
            restore_backup(backup, self.db)
        self.assertEqual(self.db.read_bytes(), original)

    def test_restore_garbage_blocked(self):
        invalid = self.dir / "bad.db"
        target = self.dir / "restore.db"
        invalid.write_text("not sqlite")
        with self.assertRaises(sqlite3.DatabaseError):
            restore_backup(invalid, target)
        self.assertFalse(target.exists())

    def test_restore_rejects_non_bidax_sqlite(self):
        invalid = self.dir / "unrelated.db"
        target = self.dir / "restore.db"
        from contextlib import closing
        with closing(sqlite3.connect(invalid)) as conn:
            conn.execute("CREATE TABLE unrelated(id INTEGER)")
            conn.commit()
        with self.assertRaises(ValueError):
            restore_backup(invalid, target)
        self.assertFalse(target.exists())

    def test_controller_customer_flow(self):
        notices = self.dir / "notices.json"
        profile = self.dir / "profile.json"
        notices.write_text(json.dumps([NOTICE], ensure_ascii=False), encoding="utf-8")
        profile.write_text(json.dumps(PROFILE, ensure_ascii=False), encoding="utf-8")
        ctl = LocalController(self.db)
        with self.assertRaises(ValueError):
            ctl.screen()
        ctl.load_profile(profile)
        self.assertEqual(ctl.import_notices(notices)["added_versions"], 1)
        report = ctl.screen()
        self.assertEqual(report["count"], 1)
        ctl.export(self.dir / "output.html", "html")
        self.assertTrue((self.dir / "output.html").exists())
        fp = report["results"][0]["source_fingerprint"]
        ctl.review(NOTICE["notice_no"], fp, "홍길동", "확인", "원문 직접 대조")
        self.assertEqual(len(ctl.history(NOTICE["notice_no"])["reviews"]), 1)
        ctl.backup(self.dir / "copy.db")
        self.assertTrue((self.dir / "copy.db").exists())

    def test_controller_import_invalid_rollback(self):
        file = self.dir / "bad.json"
        file.write_text(json.dumps([NOTICE, dict(NOTICE, source_url="http://evil.example")], ensure_ascii=False))
        ctl = LocalController(self.db)
        with self.assertRaises(ValueError):
            ctl.import_notices(file)
        with BidLedger(self.db) as ledger:
            self.assertEqual(ledger.current(), [])

    def test_cli_end_to_end(self):
        import contextlib
        from io import StringIO
        notices = self.dir / "notices.json"
        profile = self.dir / "profile.json"
        notices.write_text(json.dumps([NOTICE], ensure_ascii=False), encoding="utf-8")
        profile.write_text(json.dumps(PROFILE, ensure_ascii=False), encoding="utf-8")
        def run(*parts):
            out = StringIO()
            with contextlib.redirect_stdout(out):
                main(["--db", str(self.db), *parts])
            return json.loads(out.getvalue())
        self.assertEqual(run("import", str(notices))["added_versions"], 1)
        screening = run("screen", str(profile), "--now", NOW.isoformat())
        self.assertEqual(screening["count"], 1)
        self.assertEqual(run("export", str(profile), str(self.dir / "export.html"), "--format", "html")["format"], "html")
        self.assertEqual(len(run("changes", NOTICE["notice_no"])["changes"]), 1)
        self.assertEqual(run("alerts", "--hours", "48")["scope"], "ON_DEMAND_ONLY")
        self.assertEqual(run("review", NOTICE["notice_no"], screening["results"][0]["source_fingerprint"],
                             "홍길동", "보류", "수동 재확인")["decision"], "보류")
        self.assertEqual(len(run("history", NOTICE["notice_no"])["reviews"]), 1)
        run("backup", str(self.dir / "backup.db"))
        restored = self.dir / "restored.db"
        out = StringIO()
        with contextlib.redirect_stdout(out):
            main(["--db", str(restored), "restore", str(self.dir / "backup.db")])
        self.assertTrue(restored.exists())
        self.assertEqual(json.loads(out.getvalue())["current_notices"], 1)

if __name__ == "__main__":
    unittest.main()
