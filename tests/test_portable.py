"""Reproducible, local-only zipapp packaging and executable CLI acceptance."""
from __future__ import annotations
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("bidax_portable_builder",ROOT/"packaging"/"build_portable.py")
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PortableTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.zip=Path(self.tmp.name)/"BID_AX.pyz"
        module.build(self.zip)

    def test_reproducible_without_caches_or_secrets(self):
        other=Path(self.tmp.name)/"other.pyz"
        self.assertEqual(module.build(other)["sha256"],hashlib.sha256(self.zip.read_bytes()).hexdigest())
        self.assertEqual(other.read_bytes(),self.zip.read_bytes())
        with zipfile.ZipFile(self.zip) as z:
            self.assertNotIn(".env"," ".join(z.namelist()))
            self.assertFalse(any(".db" in name or "__pycache__" in name for name in z.namelist()))
            manifest=json.loads(z.read("BIDAX_MANIFEST.json"))
            self.assertEqual(manifest["status"],"UNRELEASED")
            for path,sha in manifest["files"].items():
                self.assertEqual(hashlib.sha256(z.read(path)).hexdigest(),sha)

    def test_actual_zipapp_import_screen_and_duplicate_replay(self):
        db=Path(self.tmp.name)/"customer.db"
        input_file=ROOT/"examples"/"notices.json"
        profile=ROOT/"examples"/"profile.json"
        def run(*args):
            result=subprocess.run([sys.executable,str(self.zip),"--db",str(db),*args],
                                  capture_output=True,text=True,timeout=15,check=True)
            return json.loads(result.stdout)
        self.assertEqual(run("import",str(input_file))["added_versions"],len(json.loads(input_file.read_text())))
        self.assertEqual(run("import",str(input_file))["added_versions"],0)
        screen=run("screen",str(profile))
        self.assertEqual(screen["scope"],"OFFLINE_PRELIMINARY_ONLY")
        self.assertEqual(screen["count"],len(json.loads(input_file.read_text())))
        target=Path(self.tmp.name)/"report.html"
        self.assertEqual(run("export",str(profile),str(target),"--format","html")["format"],"html")
        self.assertTrue(target.exists())
        with self.assertRaises(subprocess.CalledProcessError):
            run("export",str(profile),str(target),"--format","html")

    def test_no_overwrite_package(self):
        with self.assertRaises(FileExistsError):
            module.build(self.zip)

if __name__=="__main__": unittest.main()

class PortableCrossSourceAcceptance(unittest.TestCase):
    def test_packaged_zipapp_three_source_overview_and_watch(self):
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td)/'portable.pyz'
            module.build(dest)
            db = Path(td)/'evidence.sqlite'
            def cmd(*args):
                p = subprocess.run([sys.executable, str(dest), '--db', str(db), *args],
                                   cwd=ROOT, capture_output=True, text=True, timeout=12, check=True)
                return json.loads(p.stdout)
            cmd('import', str(ROOT/'examples'/'notices.json'))
            cmd('onbid-import', str(ROOT/'examples'/'onbid_assets_synthetic.json'))
            portfolio = cmd('portfolio-report')
            self.assertGreater(portfolio['g2b']['count'], 0)
            self.assertGreater(portfolio['onbid']['count'], 0)
            self.assertEqual(portfolio['court']['count'], 0)
            self.assertFalse(portfolio['legal_or_investment_approval'])
            prop = portfolio['onbid']['assets'][0]
            self.assertTrue(cmd('onbid-watch', prop['property_id'], prop['condition_id'],
                                '관심', '원문 검증 예정')['written'])
            self.assertEqual(cmd('onbid-watchlist')['active_count'], 1)
