import sqlite3
import tempfile
import unittest
from pathlib import Path

from worknova_desk import Desk, DeskError


class DeskTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "worknova.sqlite"
        self.app = Desk(self.path)
        self.customer = self.app.add_customer("가상의 고객 <script>")

    def tearDown(self):
        self.app.close()
        self.temp.cleanup()

    def quote(self, *, taxable=True, price=100):
        return self.app.new_quote(self.customer, [{"description": "로고 수정", "quantity": 2,
                                                   "unit_krw": price}], taxable=taxable)

    def active(self, price=100):
        q = self.quote(price=price)
        self.app.approve_quote(q, "owner")
        c = self.app.new_contract(q, "납품 범위", [{"title": "초안", "amount_krw": 100},
                                                  {"title": "완료", "amount_krw": 120}])
        self.app.activate_contract(c, "owner")
        mids = [r[0] for r in self.app.db.execute("SELECT id FROM milestones WHERE contract_id=? ORDER BY rowid", (c,))]
        return c, mids

    def test_vat_krw_rounding(self):
        q = self.quote()
        row = self.app._fetch("quotes", q)
        self.assertEqual((row["subtotal_krw"], row["vat_krw"], row["total_krw"]), (200, 20, 220))

    def test_vat_half_up_not_float(self):
        q = self.quote(price=3) # subtotal 6 => VAT 1
        self.assertEqual(self.app._fetch("quotes", q)["vat_krw"], 1)

    def test_non_taxable(self):
        q = self.quote(taxable=False)
        self.assertEqual(self.app._fetch("quotes", q)["total_krw"], 200)

    def test_no_implicit_approval(self):
        q = self.quote()
        with self.assertRaises(DeskError):
            self.app.new_contract(q, "scope", [{"title": "one", "amount_krw": 220}])

    def test_milestone_sum_must_match(self):
        q = self.quote(); self.app.approve_quote(q, "owner")
        with self.assertRaises(DeskError):
            self.app.new_contract(q, "scope", [{"title": "one", "amount_krw": 219}])

    def test_duplicate_approval_rejected(self):
        q = self.quote(); self.app.approve_quote(q, "owner")
        with self.assertRaises(DeskError):
            self.app.approve_quote(q, "owner")

    def test_contract_unique_per_quote(self):
        q = self.quote(); self.app.approve_quote(q, "owner")
        self.app.new_contract(q, "scope", [{"title": "one", "amount_krw": 220}])
        with self.assertRaises(DeskError):
            self.app.new_contract(q, "scope", [{"title": "one", "amount_krw": 220}])

    def test_state_flow_revision_delivery_accept(self):
        c, mids = self.active()
        with self.assertRaises(DeskError): self.app.accept(mids[0], "client")
        self.app.deliver(mids[0], "owner", "초안 전송")
        self.app.request_revision(mids[0], "client", "색상 변경")
        self.app.deliver(mids[0], "owner", "수정 전송")
        self.app.accept(mids[0], "client")
        self.assertEqual(self.app._fetch("milestones", mids[0])["status"], "ACCEPTED")

    def test_no_collection_before_acceptance(self):
        _, mids = self.active()
        with self.assertRaises(DeskError):
            self.app.record_collection(mids[0], 20, "manual-1", "owner")

    def test_partial_collection_and_idempotency(self):
        c, mids = self.active()
        self.app.deliver(mids[0], "owner", "납품")
        self.app.accept(mids[0], "client")
        r = self.app.record_collection(mids[0], 30, "bank-reference-001", "owner")
        self.assertEqual(self.app.record_collection(mids[0], 30, "bank-reference-001", "owner"), r)
        with self.assertRaises(DeskError): self.app.record_collection(mids[0], 31, "bank-reference-001", "owner")
        with self.assertRaises(DeskError): self.app.record_collection(mids[0], 71, "bank-reference-002", "owner")
        self.app.record_collection(mids[0], 70, "bank-reference-002", "owner")
        self.assertEqual(self.app.report(c)["paid_krw"], 100)
        self.assertEqual(self.app.report(c)["outstanding_krw"], 120)
        self.assertEqual(self.app.db.execute("SELECT count(*) FROM receipts").fetchone()[0], 2)

    def test_html_escapes_user_strings(self):
        c, _ = self.active()
        out = self.app.export_html(c)
        self.assertNotIn("<script>", out)
        self.assertNotIn("가상의 고객", out) # redacted by default
        self.assertIn("Content-Security-Policy", out)

    def test_report_redaction(self):
        c, _ = self.active()
        self.assertEqual(self.app.report(c)["customer"], "[REDACTED]")
        self.assertIn("가상의 고객", self.app.report(c, include_customer=True)["customer"])

    def test_audit_chain_detects_mutation(self):
        self.quote()
        self.assertEqual(self.app.verify_audit(), 2)
        self.app.db.execute("UPDATE audit_events SET actor='fake' WHERE seq=1")
        with self.assertRaises(DeskError): self.app.verify_audit()

    def test_backup_and_integrity(self):
        c, _ = self.active()
        backup = Path(self.temp.name) / "backup.sqlite"
        sha = self.app.backup(backup)
        self.assertEqual(len(sha), 64)
        with sqlite3.connect(backup) as db:
            self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(db.execute("SELECT count(*) FROM contracts").fetchone()[0], 1)
        with self.assertRaises(DeskError): self.app.backup(backup)

    def test_invalid_inputs_and_money_bounds(self):
        for invalid in (True, -1, 0, 1.01, "100", 10**13):
            with self.subTest(invalid=invalid), self.assertRaises(DeskError):
                self.app.new_quote(self.customer, [{"description": "test", "quantity": 1, "unit_krw": invalid}])
        with self.assertRaises(DeskError): self.app.new_quote(self.customer, [])
        with self.assertRaises(DeskError): self.app.add_customer("\x00bad")

    def test_reopen_persisted_data(self):
        q = self.quote()
        self.app.close()
        self.app = Desk(self.path)
        self.assertEqual(self.app._fetch("quotes", q)["status"], "DRAFT")
        self.assertEqual(self.app.verify_audit(), 2)

    def test_symlink_database_rejected(self):
        link = Path(self.temp.name) / "linked.sqlite"
        try: link.symlink_to(self.path)
        except (OSError, NotImplementedError): self.skipTest("symlinks unavailable")
        with self.assertRaises(DeskError): Desk(link)


if __name__ == "__main__":
    unittest.main()

class CLITests(unittest.TestCase):
    def test_cli_init_customer_and_bad_quote(self):
        import subprocess, sys, os
        with tempfile.TemporaryDirectory() as t:
            db = Path(t) / "cli.sqlite"
            env = dict(os.environ)
            env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])
            cmd = [sys.executable, "-m", "worknova_desk", "--db", str(db)]
            init = subprocess.run(cmd + ["init"], capture_output=True, text=True, env=env)
            self.assertEqual(init.returncode, 0, init.stderr)
            result = subprocess.run(cmd + ["customer", "--name", "테스트"], capture_output=True, text=True, env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("customer_id", result.stdout)
            fail = subprocess.run(cmd + ["quote", "--customer-id", "missing", "--items-json", "[]"],
                                  capture_output=True, text=True, env=env)
            self.assertEqual(fail.returncode, 2)
            self.assertIn('"ok": false', fail.stderr)
