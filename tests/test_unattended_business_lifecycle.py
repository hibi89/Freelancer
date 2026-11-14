"""Unattended, offline WORKNOVA Desk whole-lifecycle regression.

All writes target a unique, auto-deleted TemporaryDirectory. No customer data,
paid APIs, network, Tk interaction, PayPal action, or Windows administrator needed.
This verifies the source-level core; it does NOT certify an EXE or a real buyer.
"""
from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from worknova_desk.core import Desk, DeskError


class UnattendedBusinessLifecycle(unittest.TestCase):
    def test_quote_to_collection_survives_new_database_session(self):
        with tempfile.TemporaryDirectory(prefix="worknova-business-qa-") as temp:
            db_path = Path(temp) / "synthetic.sqlite"
            desk = Desk(db_path)
            try:
                customer = desk.add_customer("WORKNOVA_SYNTHETIC_CUSTOMER")
                quote = desk.new_quote(
                    customer,
                    [{"description": "Synthetic test work", "quantity": 1,
                      "unit_krw": 1000}],
                    taxable=False,
                )
                self.assertEqual(desk.list_quotes(customer)[0]["total_krw"], 1000)

                # A contract cannot be created from an unapproved quote.
                with self.assertRaises(DeskError):
                    desk.new_contract(
                        quote, "Synthetic scoped deliverable",
                        [{"title": "Synthetic step", "amount_krw": 1000}],
                    )

                desk.approve_quote(quote, "qa-owner")
                contract = desk.new_contract(
                    quote, "Synthetic scoped deliverable",
                    [{"title": "Synthetic step", "amount_krw": 1000}],
                )
                desk.activate_contract(contract, "qa-owner")
                milestone = desk.list_milestones(contract)[0]["id"]

                # No unaccepted delivery may be recorded as collected funds.
                with self.assertRaises(DeskError):
                    desk.record_collection(
                        milestone, 1000, "SYNTHETIC-REF-01", "qa-owner"
                    )

                desk.deliver(milestone, "qa-owner", "Synthetic evidence only")
                desk.accept(milestone, "qa-client")
                first_receipt = desk.record_collection(
                    milestone, 1000, "SYNTHETIC-REF-01", "qa-owner"
                )
                second_receipt = desk.record_collection(
                    milestone, 1000, "SYNTHETIC-REF-01", "qa-owner"
                )
                self.assertEqual(first_receipt, second_receipt)
                self.assertGreaterEqual(desk.verify_audit(), 7)
            finally:
                desk.close()

            # Reopen the exact existing SQLite file. Never create a replacement.
            reopened = Desk(db_path, allow_create=False)
            try:
                customers = reopened.list_customers("WORKNOVA_SYNTHETIC_CUSTOMER")
                self.assertEqual(len(customers), 1)
                self.assertEqual(customers[0]["id"], customer)
                quotes = reopened.list_quotes(customer)
                self.assertEqual(len(quotes), 1)
                self.assertEqual(quotes[0]["status"], "APPROVED")
                self.assertEqual(quotes[0]["total_krw"], 1000)
                contracts = reopened.list_contracts(customer)
                self.assertEqual(len(contracts), 1)
                self.assertEqual(contracts[0]["status"], "ACTIVE")
                steps = reopened.list_milestones(contract)
                self.assertEqual(len(steps), 1)
                self.assertEqual(steps[0]["status"], "ACCEPTED")
                self.assertEqual(
                    reopened.db.execute(
                        "SELECT COUNT(*) FROM receipts WHERE reference=?",
                        ("SYNTHETIC-REF-01",),
                    ).fetchone()[0], 1,
                )
                self.assertEqual(reopened.schema_version, 2)
                self.assertEqual(
                    reopened.db.execute("PRAGMA integrity_check").fetchone()[0], "ok"
                )
                self.assertGreaterEqual(reopened.verify_audit(), 7)
            finally:
                reopened.close()

    def test_rejects_fake_receipt_overpayment_without_extra_audit(self):
        with tempfile.TemporaryDirectory(prefix="worknova-business-negative-") as temp:
            db_path = Path(temp) / "synthetic.sqlite"
            desk = Desk(db_path)
            try:
                customer = desk.add_customer("WORKNOVA_NEGATIVE_CUSTOMER")
                quote = desk.new_quote(
                    customer,
                    [{"description": "Synthetic service", "quantity": 1,
                      "unit_krw": 2000}],
                    taxable=False,
                )
                desk.approve_quote(quote, "qa-owner")
                contract = desk.new_contract(
                    quote, "Synthetic service scope",
                    [{"title": "Synthetic milestone", "amount_krw": 2000}],
                )
                desk.activate_contract(contract, "qa-owner")
                milestone = desk.list_milestones(contract)[0]["id"]
                desk.deliver(milestone, "qa-owner", "Only synthetic work")
                desk.accept(milestone, "qa-client")
                desk.record_collection(
                    milestone, 1500, "SYNTHETIC-REF-PART", "qa-owner"
                )
                audit_count = desk.verify_audit()
                with self.assertRaises(DeskError):
                    desk.record_collection(
                        milestone, 600, "SYNTHETIC-REF-OVER", "qa-owner"
                    )
                self.assertEqual(
                    desk.db.execute("SELECT SUM(amount_krw) FROM receipts").fetchone()[0],
                    1500,
                )
                self.assertEqual(desk.verify_audit(), audit_count)
                self.assertEqual(
                    desk.db.execute("PRAGMA integrity_check").fetchone()[0], "ok"
                )
            finally:
                desk.close()


if __name__ == "__main__":
    unittest.main()
