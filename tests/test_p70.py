"""P70 database acceptance, privacy, failure safety, GUI parser (offline synthetic)."""
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from worknova_desk.core import Desk, DeskError, restore_new
from worknova_desk.gui import parse_rows


class P70Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder=Path(self.temp.name)
        self.app=Desk(self.folder/'live.sqlite')
        self.addCleanup(self.app.close)
        self.customer=self.app.add_customer('가상 고객 <img src=x>')

    def make_quote(self, price=500):
        return self.app.new_quote(self.customer,[{'description':'디자인 <script>', 'quantity':1,'unit_krw':price}],taxable=True)

    def test_v2_schema_new_db(self):
        self.assertEqual(self.app.schema_version,2)
        self.assertEqual(self.app.db.execute('PRAGMA foreign_key_check').fetchall(),[])

    def test_revision_chain_immutable_approved_source(self):
        q=self.make_quote()
        self.app.approve_quote(q,'owner')
        v2=self.app.revise_quote(q,[{'description':'디자인','quantity':2,'unit_krw':500}],actor='owner')
        self.assertEqual(self.app._fetch('quotes',q)['status'],'APPROVED')
        self.assertEqual(self.app._fetch('quotes',q)['total_krw'],550)
        self.assertEqual(self.app._fetch('quotes',v2)['status'],'DRAFT')
        self.assertEqual(self.app._fetch('quotes',v2)['total_krw'],1100)
        self.assertEqual([x['revision'] for x in self.app.quote_history(v2)], [1,2])
        self.assertEqual(self.app.quote_history(v2)[1]['parent_quote_id'],q)

    def test_cannot_approve_obsolete_draft(self):
        q=self.make_quote()
        v2=self.app.revise_quote(q,[{'description':'new','quantity':1,'unit_krw':700}])
        with self.assertRaises(DeskError):self.app.approve_quote(q,'owner')
        self.app.approve_quote(v2,'owner')
        self.assertEqual(self.app._fetch('quotes',q)['status'],'DRAFT')

    def test_multiple_revisions_and_outdated_parent_refused(self):
        q=self.make_quote()
        v2=self.app.revise_quote(q,[{'description':'v2','quantity':1,'unit_krw':600}])
        v3=self.app.revise_quote(v2,[{'description':'v3','quantity':1,'unit_krw':700}])
        self.assertEqual(len(self.app.quote_history(q)),3)
        with self.assertRaises(DeskError): self.app.revise_quote(q,[{'description':'bad','quantity':1,'unit_krw':999}])
        self.assertEqual(self.app._fetch('quotes',v3)['revision'],3)

    def test_revising_does_not_reprice_existing_contract(self):
        q=self.make_quote(); self.app.approve_quote(q,'owner')
        c=self.app.new_contract(q,'원래 합의',[{'title':'납품','amount_krw':550}]);self.app.activate_contract(c,'owner')
        self.app.revise_quote(q,[{'description':'추가','quantity':1,'unit_krw':999}])
        self.assertEqual(self.app.report(c)['total_krw'],550)
        self.assertEqual(self.app.report(c)['status'],'ACTIVE')

    def test_quote_html_csp_and_escape(self):
        q=self.make_quote()
        html=self.app.export_quote_html(q)
        self.assertIn('Content-Security-Policy',html)
        self.assertNotIn('<script>',html)
        self.assertNotIn('<img',html)
        self.assertIn('&lt;script&gt;',html)
        self.assertNotIn('가상 고객',html)

    def test_lists_search_and_references(self):
        q=self.make_quote()
        self.assertEqual(len(self.app.list_customers('가상')),1)
        self.assertEqual(len(self.app.list_customers('없음')),0)
        self.assertEqual(self.app.list_quotes(self.customer)[0]['id'],q)
        self.app.approve_quote(q,'owner')
        c=self.app.new_contract(q,'scope',[{'title':'단계','amount_krw':550}])
        self.assertEqual(self.app.list_contracts(self.customer)[0]['id'],c)
        self.assertEqual(len(self.app.list_milestones(c)),1)

    def test_backup_restore_new_full_audit(self):
        q=self.make_quote();self.app.approve_quote(q,'owner')
        backup=self.folder/'snapshot.sqlite';sha=self.app.backup(backup)
        new=self.folder/'restored.sqlite'
        proof=restore_new(backup,new,sha)
        self.assertEqual(proof['schema_version'],2)
        app2=Desk(new)
        try:
            self.assertEqual(app2.verify_audit(),3)
            self.assertEqual(app2._fetch('quotes',q)['status'],'APPROVED')
            self.assertEqual(app2._fetch('quotes',q)['total_krw'],550)
        finally:app2.close()
        self.assertTrue(self.app.path.exists())
        self.assertTrue(backup.exists())

    def test_restore_wrong_hash_no_creation(self):
        bak=self.folder/'snapshot.sqlite';sha=self.app.backup(bak)
        dst=self.folder/'no.sqlite'
        with self.assertRaises(DeskError):restore_new(bak,dst,'0'*64)
        self.assertFalse(dst.exists())
        self.assertNotEqual(sha,'0'*64)

    def test_restore_existing_destination_refused(self):
        bak=self.folder/'snapshot.sqlite';sha=self.app.backup(bak)
        with self.assertRaises(DeskError):restore_new(bak,self.app.path,sha)
        self.assertTrue(self.app.path.exists())

    def test_restore_bad_sqlite_even_if_checksum_matches(self):
        bak=self.folder/'broken.sqlite';bak.write_bytes(b'not a database')
        dst=self.folder/'restore.sqlite'
        with self.assertRaises((DeskError,sqlite3.DatabaseError)):restore_new(bak,dst,hashlib.sha256(bak.read_bytes()).hexdigest())
        self.assertFalse(dst.exists())

    def test_backup_tampered_audit_refused(self):
        self.make_quote()
        self.app.db.execute("UPDATE audit_events SET actor='tamper' WHERE seq=1")
        bak=self.folder/'should-not-exist.sqlite'
        with self.assertRaises(DeskError):self.app.backup(bak)
        self.assertFalse(bak.exists())

    def test_gui_parser_quote_good_and_bad(self):
        self.assertEqual(parse_rows('A|2|100\nB|1|30',kind='quote'),[
          {'description':'A','quantity':2,'unit_krw':100},{'description':'B','quantity':1,'unit_krw':30}])
        for val in ('A|bad|100','A|1','A|2|10|extra','','A|\x001|10'):
            with self.subTest(val=val),self.assertRaises((DeskError,ValueError)):parse_rows(val,kind='quote')

    def test_gui_parser_milestones(self):
        self.assertEqual(parse_rows('착수|100\n완료|200',kind='milestone')[1]['amount_krw'],200)

    def test_gui_parser_illegal_kind(self):
        with self.assertRaises(DeskError):parse_rows('x|1',kind='bogus')

    def test_db_user_version_reopened(self):
        path=self.app.path;self.app.close();self.app=Desk(path)
        self.assertEqual(self.app.schema_version,2)

    def test_cli_revision_and_preview(self):
        q=self.make_quote();out=self.folder/'quote.html'
        env=os.environ.copy();env['PYTHONPATH']=str(Path(__file__).resolve().parents[1])
        cmd=[sys.executable,'-m','worknova_desk','--db',str(self.app.path)]
        rev=subprocess.run(cmd+['revise-quote','--quote-id',q,'--items-json',json.dumps([
          {'description':'item','quantity':1,'unit_krw':500}]),'--actor','owner'],env=env,capture_output=True,text=True)
        self.assertEqual(rev.returncode,0,rev.stderr)
        v2=json.loads(rev.stdout)['result']['quote_id']
        preview=subprocess.run(cmd+['quote-preview','--quote-id',v2,'--out',str(out)],env=env,capture_output=True,text=True)
        self.assertEqual(preview.returncode,0,preview.stderr)
        self.assertIn('견적',out.read_text())
        failed=subprocess.run(cmd+['quote-preview','--quote-id',v2,'--out',str(out)],env=env,capture_output=True,text=True)
        self.assertEqual(failed.returncode,2)

    def test_quote_revisions_preserve_audit(self):
        q=self.make_quote();v2=self.app.revise_quote(q,[{'description':'new','quantity':1,'unit_krw':100}]);self.app.approve_quote(v2,'owner')
        self.assertEqual(self.app.verify_audit(),4)


class LegacyMigrationTests(unittest.TestCase):
    def test_explicit_v1_migration_retains_content_and_backup(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/'legacy.sqlite'
            # v1 customer/quote fixture from preexisting schema, including one approved quote.
            db=sqlite3.connect(path)
            try:
                db.executescript('''PRAGMA user_version=1;
                 CREATE TABLE customers (id TEXT PRIMARY KEY,name TEXT NOT NULL,created_at TEXT NOT NULL);
                 CREATE TABLE quotes (id TEXT PRIMARY KEY,customer_id TEXT NOT NULL REFERENCES customers(id),revision INTEGER NOT NULL CHECK(revision>0),items_json TEXT NOT NULL,subtotal_krw INTEGER NOT NULL,vat_krw INTEGER NOT NULL,total_krw INTEGER NOT NULL,status TEXT NOT NULL CHECK(status IN ('DRAFT','APPROVED')),created_at TEXT NOT NULL,approved_by TEXT,UNIQUE(customer_id,id));
                 INSERT INTO customers VALUES ('c1','기존 고객','2026-01-01');
                 INSERT INTO quotes VALUES ('q1','c1',1,'[]',100,10,110,'APPROVED','2026-01-01','owner');''')
            finally:
                db.close()
            app=Desk(path)
            self.assertEqual(app.schema_version,1)
            with self.assertRaises(DeskError):app.revise_quote('q1',[{'description':'new','quantity':1,'unit_krw':100}])
            before=app._fetch('quotes','q1')['total_krw']
            backup=Path(t)/'legacy-backup.sqlite'
            sha=app.migrate_v1(backup)
            self.assertEqual(app.schema_version,2)
            self.assertEqual(app._fetch('quotes','q1')['total_krw'],before)
            self.assertEqual(app._fetch('quotes','q1')['root_quote_id'],'q1')
            self.assertEqual(app.verify_audit(),1)
            self.assertEqual(hashlib.sha256(backup.read_bytes()).hexdigest(),sha)
            old=sqlite3.connect(backup)
            self.assertEqual(old.execute('PRAGMA user_version').fetchone()[0],1)
            self.assertEqual(old.execute('SELECT total_krw FROM quotes').fetchone()[0],110)
            old.close()
            app.close()

if __name__ == '__main__':unittest.main()
