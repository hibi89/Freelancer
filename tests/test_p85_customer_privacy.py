"""Offline, opt-in customer financial summary must not leak free-text/PII by default."""
from __future__ import annotations
import hashlib
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from worknova_desk.core import Desk, DeskError
from worknova_desk.privacy import export_customer_summary

ROOT=Path(__file__).resolve().parents[1]

class CustomerSummaryTests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root=Path(tmp.name)
        self.desk=Desk(self.root/'owner.sqlite')
        self.addCleanup(self.desk.close)
        self.customer=self.desk.add_customer('고객사 비밀이름')
        quote=self.desk.new_quote(self.customer,[{'description':'비밀 프로젝트 이름', 'quantity':1,'unit_krw':10000}])
        self.desk.approve_quote(quote,'owner')
        self.contract=self.desk.new_contract(quote,'비밀 계약 범위',[{'title':'특수 단계명','amount_krw':11000}])
        self.desk.activate_contract(self.contract,'owner')
        self.milestone=self.desk.list_milestones(self.contract)[0]['id']
        self.desk.deliver(self.milestone,'owner','비밀 납품 메모')
        self.desk.accept(self.milestone,'client')
        self.desk.record_collection(self.milestone,3500,'비밀 은행 참조','owner')
        self.out=self.root/'customer-summary.json'

    def test_minimal_summary_excludes_sensitive_free_text(self):
        receipt=export_customer_summary(self.desk,self.customer,self.out)
        doc=json.loads(self.out.read_text())
        self.assertTrue(receipt['created'])
        self.assertEqual(doc['customer_name'],'[REDACTED]')
        self.assertEqual(doc['manual_collections_krw'],3500)
        self.assertEqual(doc['contracts'][0]['milestones'][0]['outstanding_krw'],7500)
        for forbidden in ['고객사 비밀이름','비밀 프로젝트 이름','비밀 계약 범위','특수 단계명','비밀 납품 메모','비밀 은행 참조']:
            self.assertNotIn(forbidden,self.out.read_text())
        self.assertEqual(receipt['sha256'],hashlib.sha256(self.out.read_bytes()).hexdigest())

    def test_default_summary_cannot_be_used_as_legal_or_banking_receipt(self):
        export_customer_summary(self.desk,self.customer,self.out)
        doc=json.loads(self.out.read_text())
        self.assertIn('not verified bank payments',doc['warning'])
        self.assertFalse('reference' in doc['contracts'][0])

    def test_name_requires_disclosure_and_boolean_controls(self):
        for kwargs in ({'include_name':True},{'include_name':1}, {'confirm_disclosure':1}):
            with self.subTest(kwargs=kwargs),self.assertRaises(DeskError):
                export_customer_summary(self.desk,self.customer,self.out,**kwargs)
            self.assertFalse(self.out.exists())
        export_customer_summary(self.desk,self.customer,self.out,include_name=True,confirm_disclosure=True)
        self.assertEqual(json.loads(self.out.read_text())['customer_name'],'고객사 비밀이름')

    def test_never_overwrite_existing_file(self):
        self.out.write_bytes(b'PRESERVE')
        with self.assertRaises(DeskError):export_customer_summary(self.desk,self.customer,self.out)
        self.assertEqual(self.out.read_bytes(),b'PRESERVE')

    def test_wrong_extension_no_output(self):
        with self.assertRaises(DeskError):export_customer_summary(self.desk,self.customer,self.root/'x.txt')
        self.assertFalse((self.root/'x.txt').exists())

    def test_unknown_customer_no_output(self):
        with self.assertRaises(DeskError):export_customer_summary(self.desk,'not-real',self.out)
        self.assertFalse(self.out.exists())

    def test_symlink_output_refused(self):
        target=self.root/'keep.json';target.write_bytes(b'keep')
        try:self.out.symlink_to(target)
        except OSError:self.skipTest('symlinks unavailable')
        with self.assertRaises(DeskError):export_customer_summary(self.desk,self.customer,self.out)
        self.assertEqual(target.read_bytes(),b'keep')

    @unittest.skipUnless(os.name=='posix','POSIX permission check')
    def test_private_new_file_under_permissive_umask(self):
        prev=os.umask(0o022)
        try:export_customer_summary(self.desk,self.customer,self.out)
        finally:os.umask(prev)
        self.assertEqual(stat.S_IMODE(self.out.stat().st_mode),0o600)

    def test_cli_default_redacts_and_output_has_no_names(self):
        cmd=[sys.executable,'-m','worknova_desk','--db',str(self.desk.path),
             'export-customer-summary','--customer-id',self.customer,'--out',str(self.out)]
        process=subprocess.run(cmd,cwd=ROOT,env={**os.environ,'PYTHONPATH':str(ROOT)},
            capture_output=True,text=True,timeout=15)
        self.assertEqual(process.returncode,0,process.stderr)
        self.assertNotIn('고객사 비밀이름',self.out.read_text()+process.stdout)
        self.assertTrue(json.loads(process.stdout)['ok'])

    def test_cli_sensitive_export_requires_two_explicit_flags(self):
        cmd=[sys.executable,'-m','worknova_desk','--db',str(self.desk.path),
             'export-customer-summary','--customer-id',self.customer,'--out',str(self.out),'--include-name']
        response=subprocess.run(cmd,cwd=ROOT,env={**os.environ,'PYTHONPATH':str(ROOT)},
            capture_output=True,text=True,timeout=15)
        self.assertEqual(response.returncode,2)
        self.assertFalse(self.out.exists())
        accepted=subprocess.run(cmd+['--confirm-disclosure'],cwd=ROOT,
            env={**os.environ,'PYTHONPATH':str(ROOT)},capture_output=True,text=True,timeout=15)
        self.assertEqual(accepted.returncode,0,accepted.stderr)
        self.assertIn('고객사 비밀이름',self.out.read_text())

if __name__=='__main__':unittest.main()
