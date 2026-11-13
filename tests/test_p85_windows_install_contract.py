"""Offline regression of the Windows installer contract; NOT native PowerShell QA.

Models the files copied by the PowerShell installer into its staging directory,
then runs the real Python package verifier against that staged layout. These
checks catch previous verified defects but do NOT prove the installer ran on Win.
"""
from __future__ import annotations

import json
import re
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.build_portable import bundle
from scripts.verify_portable import PackageError, verify

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (ROOT / 'scripts/install_local.ps1').read_text(encoding='utf-8')
LAUNCH = (ROOT / 'scripts/launch.cmd').read_text(encoding='utf-8')


class WindowsInstallContractTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.package = self.root / 'package'
        self.package.mkdir()
        zip_path = self.root / 'product.zip'
        bundle(ROOT, zip_path)
        with zipfile.ZipFile(zip_path) as archive:
            archive.extractall(self.package)
        self.expected = json.loads((self.package / 'FILE_MANIFEST.json').read_text(encoding='utf-8'))

    def stage_model(self):
        """Replicate only the manifest-controlled file copying, never touch OS app paths."""
        stage = self.root / 'stage'
        stage.mkdir()
        for entry in self.expected['files']:
            src = self.package / entry['path']
            dest = stage / entry['path']
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dest)
        # Installer now must copy the manifest itself, which is NOT in manifest.files.
        self.assertRegex(SCRIPT, r'Copy-Item -LiteralPath \$manifestPath -Destination \$stagedManifest')
        shutil.copyfile(self.package / 'FILE_MANIFEST.json', stage / 'FILE_MANIFEST.json')
        return stage

    def test_staged_install_has_self_verifying_package(self):
        stage = self.stage_model()
        self.assertEqual(verify(stage)['verified_files'], 14)
        self.assertEqual((stage/'FILE_MANIFEST.json').read_bytes(),
                         (self.package/'FILE_MANIFEST.json').read_bytes())

    def test_installer_allowlist_explicitly_accepts_verifier(self):
        m = re.search(r"if \(\$name -notmatch '([^']+)'\)", SCRIPT)
        self.assertIsNotNone(m)
        expression = re.compile(m.group(1))
        for entry in self.expected['files']:
            self.assertRegex(entry['path'], expression)
        self.assertTrue(expression.fullmatch('verify_portable.py'))
        self.assertFalse(expression.fullmatch('../../unapproved.py'))
        self.assertFalse(expression.fullmatch('evil.ps1'))

    def test_manifest_copy_precedes_code_replacement(self):
        self.assertLess(SCRIPT.index('Copy-Item -LiteralPath $manifestPath -Destination $stagedManifest'),
                        SCRIPT.index('Move-Item -LiteralPath $app -Destination $previous'))
        self.assertLess(SCRIPT.index('Staging file mismatch'),
                        SCRIPT.index('Move-Item -LiteralPath $app -Destination $previous'))
        self.assertIn('Application removed; customer data and backup folders retained:', SCRIPT)

    def test_launcher_root_avoids_quoted_trailing_backslash(self):
        # Windows CRT parsing can interpret the final backslash of "%~dp0" as
        # escaping the closing quote; using the pushd working dir avoids it.
        self.assertEqual(LAUNCH.count('--root "."'), 2)
        self.assertNotIn('--root "%~dp0"', LAUNCH)
        self.assertLess(LAUNCH.index('verify_portable.py'), LAUNCH.index('-m worknova_desk.gui'))

    def test_untrusted_cache_refused_before_import(self):
        stage = self.stage_model()
        cache = stage / 'worknova_desk' / '__pycache__'
        cache.mkdir()
        (cache / '__init__.cpython-313.pyc').write_bytes(b'untrusted')
        with self.assertRaisesRegex(PackageError, 'bytecode/cache'):
            verify(stage)

    def test_unlisted_executable_refused(self):
        stage = self.stage_model()
        for extension in ['.exe', '.bat', '.psm1']:
            payload = stage / f'unexpected{extension}'
            payload.write_bytes(b'x')
            with self.assertRaisesRegex(PackageError, 'unlisted executable'):
                verify(stage)
            payload.unlink()

    def test_stage_manifest_missing_blocks_launch(self):
        stage = self.stage_model()
        (stage / 'FILE_MANIFEST.json').unlink()
        with self.assertRaisesRegex(PackageError, 'manifest'):
            verify(stage)

    def test_stage_mutation_blocks_launch(self):
        stage = self.stage_model()
        target = stage / 'worknova_desk' / 'core.py'
        target.write_bytes(target.read_bytes() + b'\n# corrupted')
        with self.assertRaises(PackageError):
            verify(stage)


if __name__ == '__main__':
    unittest.main()
