"""Real AES-GCM roundtrip/negative tests on disposable synthetic ledgers."""
from __future__ import annotations

import hashlib
import os
import stat
import tempfile
import unittest
from pathlib import Path
from unittest import mock
from contextlib import redirect_stdout, redirect_stderr
import io
from worknova_desk.__main__ import main as cli_main

from worknova_desk.core import Desk, DeskError
from worknova_desk.secure_backup import encrypted_backup, encrypted_restore_new
from scripts.build_portable import bundle
from scripts.verify_portable import verify

PASSWORD = 'owner-local-비밀-remember-this-passphrase'

class SecureBackupTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.root = Path(self.td.name)
        self.db_path = self.root/'original.sqlite'
        self.desk = Desk(self.db_path)
        self.addCleanup(self.desk.close)
        self.customer = self.desk.add_customer('실제고객아님-합성개인정보')
        q = self.desk.new_quote(self.customer,[dict(description='독립개발',quantity=2,unit_krw=150000)])
        self.desk.approve_quote(q, 'owner')
        c = self.desk.new_contract(q,'synthetic scope',[dict(title='deliverable',amount_krw=330000)])
        self.desk.activate_contract(c, 'owner')
        self.event_count=self.desk.verify_audit()
        self.out = self.root/'private.wndesk'
        self.restored = self.root/'restored.sqlite'
    def test_valid_roundtrip_with_audit(self):
        result=encrypted_backup(self.desk, self.out, PASSWORD)
        self.assertTrue(result['encrypted'])
        content=self.out.read_bytes()
        self.assertNotIn('실제고객아님'.encode('utf8'),content)
        self.assertFalse(content.startswith(b'SQLite format 3'))
        parsed=encrypted_restore_new(self.out,self.restored,PASSWORD,expected_sha256=result['sha256'])
        self.assertEqual(parsed['verified_events'],self.event_count)
        restored=Desk(self.restored,allow_create=False)
        try:
            self.assertEqual(restored.verify_audit(),self.event_count)
        finally: restored.close()
    def test_restore_matches_customer_and_finances(self):
        encrypted_backup(self.desk,self.out,PASSWORD)
        encrypted_restore_new(self.out,self.restored,PASSWORD)
        restored=Desk(self.restored,allow_create=False)
        try:
            self.assertEqual(restored.verify_audit(),self.event_count)
            self.assertEqual(restored.list_customers()[0]['name'],'실제고객아님-합성개인정보')
            self.assertEqual(restored.list_quotes(self.customer)[0]['total_krw'],330000)
        finally:restored.close()
    def test_wrong_passphrase_preserves_destination_absence(self):
        encrypted_backup(self.desk,self.out,PASSWORD)
        with self.assertRaisesRegex(DeskError,'wrong passphrase'):
            encrypted_restore_new(self.out,self.restored,'incorrect-secret-long-enough')
        self.assertFalse(self.restored.exists())
    def test_ciphertext_tampering_detected(self):
        encrypted_backup(self.desk,self.out,PASSWORD)
        payload=bytearray(self.out.read_bytes());payload[-19]^=0x40;self.out.write_bytes(payload)
        with self.assertRaisesRegex(DeskError,'modified'):
            encrypted_restore_new(self.out,self.restored,PASSWORD)
        self.assertFalse(self.restored.exists())
    def test_source_sha_pin_detects_replacement(self):
        encrypted_backup(self.desk,self.out,PASSWORD)
        with self.assertRaisesRegex(DeskError,'SHA256 differs'):
            encrypted_restore_new(self.out,self.restored,PASSWORD,expected_sha256='0'*64)
        self.assertFalse(self.restored.exists())
    def test_existing_restore_destination_preserved(self):
        encrypted_backup(self.desk,self.out,PASSWORD)
        self.restored.write_bytes(b'UNCHANGED ORIGINAL')
        with self.assertRaisesRegex(DeskError,'NEW file'):
            encrypted_restore_new(self.out,self.restored,PASSWORD)
        self.assertEqual(self.restored.read_bytes(),b'UNCHANGED ORIGINAL')
    def test_refuse_existing_backup_target(self):
        self.out.write_bytes(b'ORIGINAL')
        with self.assertRaisesRegex(DeskError,'NEW file'):
            encrypted_backup(self.desk,self.out,PASSWORD)
        self.assertEqual(self.out.read_bytes(),b'ORIGINAL')
    def test_bad_password_policy_and_no_partial_output(self):
        for bad in ('short', ' ', None, 'a'*300):
            with self.subTest(bad=str(bad)[:8]):
                with self.assertRaises(DeskError):
                    encrypted_backup(self.desk,self.out,bad)
                self.assertFalse(self.out.exists())
    def test_unencrypted_filename_and_wrong_format(self):
        self.out.write_bytes(self.db_path.read_bytes())
        with self.assertRaisesRegex(DeskError,'not a valid'):
            encrypted_restore_new(self.out,self.restored,PASSWORD)
        self.assertFalse(self.restored.exists())
    def test_reject_symlink_source(self):
        encrypted_backup(self.desk,self.out,PASSWORD)
        fake=self.root/'alias.wndesk'; fake.symlink_to(self.out)
        with self.assertRaisesRegex(DeskError,'regular file'):
            encrypted_restore_new(fake,self.restored,PASSWORD)
        self.assertFalse(self.restored.exists())
    def test_encrypted_backup_keeps_original_digest(self):
        before=self.db_path.read_bytes()
        encrypted_backup(self.desk,self.out,PASSWORD)
        self.assertEqual(before,self.db_path.read_bytes())
    @unittest.skipUnless(os.name=='posix','POSIX owner permissions only')
    def test_owner_only_encrypted_blob_and_recovered_db(self):
        old=os.umask(0)
        try:
            encrypted_backup(self.desk,self.out,PASSWORD)
            encrypted_restore_new(self.out,self.restored,PASSWORD)
        finally:os.umask(old)
        for p in (self.out,self.restored):
            self.assertEqual(stat.S_IMODE(p.stat().st_mode),0o600)
    def test_cli_backup_and_restore_without_password_on_argv(self):
        std=io.StringIO()
        with mock.patch('worknova_desk.__main__.getpass.getpass',side_effect=[PASSWORD,PASSWORD]),redirect_stdout(std):
            exitcode=cli_main(['--db',str(self.db_path),'backup-encrypted','--out',str(self.out)])
        self.assertEqual(exitcode,0)
        self.assertNotIn(PASSWORD,std.getvalue())
        data=__import__('json').loads(std.getvalue())
        self.assertTrue(data['result']['encrypted'])
        std=io.StringIO()
        with mock.patch('worknova_desk.__main__.getpass.getpass',return_value=PASSWORD),redirect_stdout(std):
            exitcode=cli_main(['--db',str(self.db_path),'restore-encrypted-new',
                               '--encrypted-file',str(self.out),'--new-db',str(self.restored),
                               '--sha256',data['result']['sha256']])
        self.assertEqual(exitcode,0)
        self.assertTrue(self.restored.is_file())
        self.assertNotIn(PASSWORD,std.getvalue())
    def test_cli_bad_confirmation_is_rejected_without_output(self):
        with mock.patch('worknova_desk.__main__.getpass.getpass', side_effect=[PASSWORD,'wrong confirmation']),redirect_stderr(io.StringIO()):
            self.assertEqual(cli_main(['--db',str(self.db_path),'backup-encrypted','--out',str(self.out)]),2)
        self.assertFalse(self.out.exists())
    def test_dependency_absence_fails_closed(self):
        with mock.patch('worknova_desk.secure_backup._aead',side_effect=DeskError('optional dependency unavailable')):
            with self.assertRaisesRegex(DeskError,'unavailable'):
                encrypted_backup(self.desk,self.out,PASSWORD)
        self.assertFalse(self.out.exists())
    def test_package_manifest_includes_secure_backup_module(self):
        package=self.root/'package.zip'
        src=Path(__file__).resolve().parents[1]
        bundle(src,package)
        import zipfile
        target=self.root/'extracted'
        target.mkdir()
        with zipfile.ZipFile(package) as z:z.extractall(target)
        self.assertEqual(verify(target)['verified_files'],15)
        self.assertIn('secure_backup.py',str((target/'FILE_MANIFEST.json').read_text()))

if __name__=='__main__':unittest.main()
