"""P85 hardening: independent offline checkpoint and portable preflight negative cases."""
from __future__ import annotations
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from worknova_desk.core import Desk, DeskError
from worknova_desk.evidence import create_checkpoint, verify_checkpoint
from scripts.build_portable import bundle
from scripts.verify_portable import verify, PackageError

ROOT=Path(__file__).resolve().parents[1]


class CheckpointTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder=Path(self.temp.name)
        self.desk=Desk(self.folder/"desk.sqlite")
        self.addCleanup(self.desk.close)
        self.customer=self.desk.add_customer("SECRET_NAME_FOR_PRIVACY_TEST")
        self.quote=self.desk.new_quote(self.customer,[{"description":"Design","quantity":1,"unit_krw":200}], taxable=True)

    def test_create_verify_separately(self):
        checkpoint=self.folder/"checkpoint.json"
        result=create_checkpoint(self.desk,checkpoint)
        self.assertEqual(result["audit_events"],2)
        proof=verify_checkpoint(self.desk,checkpoint,expected_file_sha256=result["file_sha256"])
        self.assertTrue(proof["verified"])
        self.assertEqual(proof["tables_verified"],6)

    def test_privacy_hash_only(self):
        checkpoint=self.folder/"checkpoint.json"
        create_checkpoint(self.desk, checkpoint)
        raw=checkpoint.read_text(encoding="utf-8")
        self.assertNotIn("SECRET_NAME_FOR_PRIVACY_TEST",raw)
        self.assertNotIn(self.customer,raw)
        self.assertNotIn(self.quote,raw)

    def test_detect_business_row_rewrite_without_audit_rewrite(self):
        checkpoint=self.folder/"checkpoint.json"
        create_checkpoint(self.desk, checkpoint)
        self.desk.db.execute("UPDATE customers SET name='rewritten' WHERE id=?",(self.customer,))
        self.assertEqual(self.desk.verify_audit(),2)  # legacy audit does not cover table edits
        with self.assertRaisesRegex(DeskError,"customers"):
            verify_checkpoint(self.desk,checkpoint)

    def test_detect_new_transaction_and_recover_by_new_checkpoint_only(self):
        old=self.folder/"older.json"
        create_checkpoint(self.desk,old)
        self.desk.approve_quote(self.quote,"owner")
        with self.assertRaises(DeskError):verify_checkpoint(self.desk,old)
        new=self.folder/"newer.json"
        create_checkpoint(self.desk,new)
        self.assertTrue(verify_checkpoint(self.desk,new)["verified"])
        self.assertTrue(old.exists())

    def test_expected_file_hash_detects_replaced_checkpoint(self):
        p=self.folder/"proof.json"
        info=create_checkpoint(self.desk,p)
        doc=json.loads(p.read_text(encoding="utf-8"))
        doc["warning"]="changed"
        p.write_text(json.dumps(doc),encoding="utf-8")
        with self.assertRaises(DeskError):
            verify_checkpoint(self.desk,p,expected_file_sha256=info["file_sha256"])

    def test_create_existing_or_wrong_extension_never_overwrite(self):
        p=self.folder/"checkpoint.json"
        p.write_bytes(b"original")
        with self.assertRaises(DeskError):create_checkpoint(self.desk,p)
        self.assertEqual(p.read_bytes(),b"original")
        with self.assertRaises(DeskError):create_checkpoint(self.desk,self.folder/"proof.txt")

    def test_invalid_file_symlink_rejected(self):
        target=self.folder/"checkpoint.json"
        create_checkpoint(self.desk,target)
        link=self.folder/"link.json"
        try:link.symlink_to(target)
        except (OSError,NotImplementedError):self.skipTest("symlink not available")
        with self.assertRaises(DeskError):verify_checkpoint(self.desk,link)

    def test_cli_create_and_verify_roundtrip(self):
        target=self.folder/"cli-checkpoint.json"
        env={**os.environ, "PYTHONPATH":str(ROOT),
             "CUA_DD_PYTHON_TOOL_WARM_SPREADSHEET_RUNTIME":"false",
             "CUA_DD_INIT_ARTIFACT_TOOL_V2":"false"}
        command=[sys.executable,"-m","worknova_desk","--db",str(self.desk.path)]
        a=subprocess.run(command+["checkpoint-new","--out",str(target)],capture_output=True,text=True,env=env,timeout=15)
        self.assertEqual(a.returncode,0,a.stderr)
        file_sha=json.loads(a.stdout)["result"]["file_sha256"]
        b=subprocess.run(command+["checkpoint-verify","--file",str(target),"--expected-file-sha256",file_sha],
                         capture_output=True,text=True,env=env,timeout=15)
        self.assertEqual(b.returncode,0,b.stderr)
        self.assertTrue(json.loads(b.stdout)["result"]["verified"])


class PortableTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.p=Path(self.temp.name)
        path=self.p/"archive.zip"
        bundle(ROOT,path)
        self.pack=self.p/"extracted"
        self.pack.mkdir()
        with zipfile.ZipFile(path) as z:z.extractall(self.pack)

    def test_verify_extracted_portable(self):
        self.assertEqual(verify(self.pack)["verified_files"],12)

    def test_tampered_python_rejected(self):
        p=self.pack/"worknova_desk/core.py"
        p.write_bytes(p.read_bytes()+b"\n# modified")
        with self.assertRaisesRegex(PackageError,"size mismatch"):
            verify(self.pack)

    def test_same_size_patch_rejected(self):
        p=self.pack/"launch.cmd"
        data=p.read_bytes()
        p.write_bytes(data.replace(b"@echo off",b"@echo OFF"))
        with self.assertRaisesRegex(PackageError,"digest mismatch"):
            verify(self.pack)

    def test_unlisted_executable_code_rejected(self):
        (self.pack/"inject.pth").write_text("import os")
        with self.assertRaisesRegex(PackageError,"unlisted"):
            verify(self.pack)

    def test_missing_required_manifest_file_rejected(self):
        p=self.pack/"FILE_MANIFEST.json"
        doc=json.loads(p.read_text())
        doc["files"].pop()
        p.write_text(json.dumps(doc))
        with self.assertRaisesRegex(PackageError,"incomplete"):
            verify(self.pack)

    def test_package_symlink_rejected(self):
        path=self.pack/"worknova_desk/core.py"
        original=path.read_bytes()
        path.unlink()
        target=self.p/"other.py"
        target.write_bytes(original)
        try: path.symlink_to(target)
        except (OSError,NotImplementedError):self.skipTest("symlink not available")
        with self.assertRaises(PackageError):verify(self.pack)

    def test_manifest_no_pii(self):
        raw=(self.pack/"FILE_MANIFEST.json").read_text()
        self.assertNotIn("customer data", raw.lower())
        self.assertNotIn(".sqlite",raw)

    def test_script_requires_verify_first(self):
        launch=(ROOT/"scripts/launch.cmd").read_text(encoding="utf-8").lower()
        self.assertLess(launch.index("verify_portable.py"),launch.index("-m worknova_desk.gui"))
        self.assertIn("if errorlevel 1",launch)
