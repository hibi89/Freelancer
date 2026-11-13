"""P85 acceptance hardening: customer history and read-only local delivery evidence."""
from __future__ import annotations
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from worknova_desk.core import Desk, DeskError
from worknova_desk.lifecycle import rename_customer, delete_unused_customer
from worknova_desk.delivery_evidence import attach_file, verify_file, list_evidence, file_fingerprint

ROOT = Path(__file__).resolve().parents[1]


class Workflow(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.desk = Desk(self.root / "test.sqlite")
        self.addCleanup(self.desk.close)

    def populated(self):
        customer = self.desk.add_customer("고객A")
        quote = self.desk.new_quote(customer, [{"description":"작업", "quantity":1,"unit_krw":100}])
        self.desk.approve_quote(quote, "owner")
        contract = self.desk.new_contract(quote, "고객 합의에 따른 작업", [{"title":"1차", "amount_krw":110}])
        self.desk.activate_contract(contract,"owner")
        milestone = self.desk.list_milestones(contract)[0]["id"]
        self.desk.deliver(milestone, "owner", "납품파일 확인 필요")
        return customer, quote, contract, milestone

    def test_rename_preserves_quotes_and_audit_no_names(self):
        customer, _, contract, _ = self.populated()
        old_reports = self.desk.report(contract)
        result = rename_customer(self.desk, customer, "새이름", expected_name="고객A",
                                 actor="owner", confirmation="CONFIRM_CUSTOMER_UPDATE")
        self.assertTrue(result["changed"])
        self.assertEqual(self.desk.report(contract)["total_krw"], old_reports["total_krw"])
        events = [x[0] for x in self.desk.db.execute("SELECT payload_json FROM audit_events")]
        self.assertNotIn("새이름", ''.join(events))
        self.assertEqual(self.desk.verify_audit(), len(events))

    def test_rename_without_confirmation_refused(self):
        customer = self.desk.add_customer("고객A")
        with self.assertRaises(DeskError):
            rename_customer(self.desk, customer, "새이름", expected_name="고객A", actor="owner", confirmation="wrong")
        self.assertEqual(self.desk.list_customers()[0]["name"], "고객A")

    def test_stale_name_refused(self):
        customer = self.desk.add_customer("고객A")
        with self.assertRaisesRegex(DeskError, "stale"):
            rename_customer(self.desk, customer, "new", expected_name="somebody else",
                            actor="owner", confirmation="CONFIRM_CUSTOMER_UPDATE")

    def test_noop_rename_idempotent(self):
        customer = self.desk.add_customer("고객A")
        count=self.desk.verify_audit()
        result=rename_customer(self.desk, customer, "고객A", expected_name="고객A", actor="owner",
                               confirmation="CONFIRM_CUSTOMER_UPDATE")
        self.assertFalse(result["changed"])
        self.assertEqual(count,self.desk.verify_audit())

    def test_financial_records_block_delete(self):
        customer, _, _, _ = self.populated()
        before=self.desk.verify_audit()
        with self.assertRaisesRegex(DeskError, "financial history"):
            delete_unused_customer(self.desk, customer, actor="owner", confirmation="DELETE_UNUSED_CUSTOMER")
        self.assertEqual(self.desk.verify_audit(),before)

    def test_unused_delete_explicit_only(self):
        customer=self.desk.add_customer("고객A")
        with self.assertRaises(DeskError):
            delete_unused_customer(self.desk, customer, actor="owner", confirmation="no")
        result=delete_unused_customer(self.desk,customer,actor="owner",confirmation="DELETE_UNUSED_CUSTOMER")
        self.assertTrue(result["deleted"])
        self.assertFalse(self.desk.list_customers())
        self.assertEqual(self.desk.verify_audit(),2)

    def test_attach_then_verify_and_idempotent(self):
        _,_,_,milestone=self.populated()
        p=self.root/"evidence.txt"
        p.write_bytes("한글 파일".encode())
        original=p.read_bytes()
        before=self.desk.verify_audit()
        result=attach_file(self.desk,milestone,p,actor="owner",confirm=True)
        self.assertEqual(result["sha256"],hashlib.sha256(original).hexdigest())
        self.assertFalse(result["duplicate"])
        self.assertTrue(verify_file(self.desk,milestone,p)["verified"])
        self.assertEqual(self.desk.verify_audit(),before+1)
        duplicate=attach_file(self.desk,milestone,p,actor="owner",confirm=True)
        self.assertTrue(duplicate["duplicate"])
        self.assertEqual(self.desk.verify_audit(),before+1)
        self.assertEqual(len(list_evidence(self.desk,milestone)),1)
        self.assertEqual(p.read_bytes(),original)
        audit=''.join(x[0] for x in self.desk.db.execute("SELECT payload_json FROM audit_events"))
        self.assertNotIn("evidence.txt",audit)
        self.assertNotIn("한글 파일",audit)

    def test_attach_needs_explicit_consent(self):
        _,_,_,milestone=self.populated()
        p=self.root/"evidence.txt";p.write_text("a")
        with self.assertRaisesRegex(DeskError,"consent"):
            attach_file(self.desk,milestone,p,actor="owner",confirm=False)

    def test_attach_rejects_planned_and_accepted(self):
        customer=self.desk.add_customer("고객A")
        q=self.desk.new_quote(customer,[{"description":"test","quantity":1,"unit_krw":100}]);self.desk.approve_quote(q,"owner")
        con=self.desk.new_contract(q,"scope",[{"title":"one","amount_krw":110}]);self.desk.activate_contract(con,"owner")
        milestone=self.desk.list_milestones(con)[0]["id"]
        p=self.root/"f";p.write_text("a")
        with self.assertRaises(DeskError):attach_file(self.desk,milestone,p,actor="owner",confirm=True)
        self.desk.deliver(milestone,"owner","note")
        self.desk.accept(milestone,"buyer")
        with self.assertRaises(DeskError):attach_file(self.desk,milestone,p,actor="owner",confirm=True)

    def test_file_change_rejected_same_size(self):
        _,_,_,milestone=self.populated()
        p=self.root/"bytes";p.write_bytes(b"abcdef")
        attach_file(self.desk,milestone,p,actor="owner",confirm=True)
        p.write_bytes(b"abcdeg")
        with self.assertRaisesRegex(DeskError,"not recorded"):
            verify_file(self.desk,milestone,p)

    def test_symlink_and_hardlink_refused(self):
        p=self.root/"payload";p.write_text("a")
        link=self.root/"link"
        try:link.symlink_to(p)
        except OSError:self.skipTest("symlink unavailable")
        with self.assertRaises(DeskError):file_fingerprint(link)
        link.unlink()
        try:os.link(p,link)
        except OSError:self.skipTest("hardlink unavailable")
        with self.assertRaises(DeskError):file_fingerprint(p)

    def test_oversized_file_refused_without_reading(self):
        p=self.root/"big"
        with p.open("wb") as f:f.truncate(64*1024*1024+1)
        with self.assertRaisesRegex(DeskError, "64 MiB"):
            file_fingerprint(p)

    def test_cli_full_evidence_without_customer_upload(self):
        _,_,_,milestone=self.populated()
        p=self.root/"delivery.txt";p.write_text("test",encoding="utf-8")
        base=[sys.executable,"-m","worknova_desk","--db",str(self.desk.path)]
        env={**os.environ,"PYTHONPATH":str(ROOT)}
        attempt=subprocess.run(base+["evidence-attach","--milestone-id",milestone,"--file",str(p),"--actor","owner"],
                               text=True,capture_output=True,env=env,timeout=15)
        self.assertEqual(attempt.returncode,2)
        okay=subprocess.run(base+["evidence-attach","--milestone-id",milestone,"--file",str(p),"--actor","owner","--confirm-local-read"],
                            text=True,capture_output=True,env=env,timeout=15)
        self.assertEqual(okay.returncode,0,okay.stderr)
        result=json.loads(okay.stdout)["result"]
        self.assertEqual(result["bytes"],4)
        verify=subprocess.run(base+["evidence-verify","--milestone-id",milestone,"--file",str(p)],
                              text=True,capture_output=True,env=env,timeout=15)
        self.assertEqual(verify.returncode,0,verify.stderr)

if __name__=='__main__':unittest.main()
