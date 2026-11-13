"""No-cost cross-platform tests for EXE build safety and explicit Windows gate.

These tests do NOT certify an EXE; the actual build requires native Windows.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import windows_build_exe as builder
import windows_gui_entry as entry


class WindowsExeBuildContract(unittest.TestCase):
    def test_plan_is_read_only_and_uses_python_free_onedir(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp) / 'new-output'
            r = builder.plan(dest)
            self.assertFalse(dest.exists())
            self.assertIn('--onedir', r['argv'])
            self.assertIn('--windowed', r['argv'])
            self.assertIn('--paths', r['argv'])
            self.assertIn(str(ROOT), r['argv'])
            self.assertNotIn('pip', r['argv'])
            self.assertFalse(r['signed'])
            self.assertFalse(r['production_ready'])

    def test_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(builder.BuildError, 'already exists'):
                builder.plan(Path(temp))

    def test_refuses_missing_parent(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(builder.BuildError, 'parent'):
                builder.plan(Path(temp) / 'missing' / 'new')

    def test_refuses_build_inside_source(self):
        with self.assertRaisesRegex(builder.BuildError, 'outside the source'):
            builder.plan(ROOT / 'dist-temptation')

    def test_refuses_build_over_customer_data(self):
        with tempfile.TemporaryDirectory() as temp:
            protected = Path(temp) / 'WORKNOVA Desk' / 'Data'
            protected.parent.mkdir(parents=True)
            with mock.patch.dict(os.environ, {'LOCALAPPDATA': temp}):
                with self.assertRaisesRegex(builder.BuildError, 'customer data'):
                    builder.plan(protected)

    def test_refuses_symlink_destination(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / 'target'
            target.mkdir()
            link = Path(temp) / 'symlink'
            try:
                link.symlink_to(target, target_is_directory=True)
            except OSError:
                self.skipTest('Symlinks unavailable in this environment')
            with self.assertRaisesRegex(builder.BuildError, 'symbolic link'):
                builder.plan(link / 'new')

    @unittest.skipIf(sys.platform == 'win32', 'On Windows, run real build separately')
    def test_nonwindows_cannot_build(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp) / 'unused'
            with self.assertRaisesRegex(builder.BuildError, 'native Windows'):
                builder.build(dest)
            self.assertFalse(dest.exists())

    def test_simulated_builder_requires_a_real_pe_header(self):
        # This is a mocked subprocess contract, NOT a native Windows build.
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp) / 'fake-build'
            def fake_run(*args, **kwargs):
                exe = dest / 'dist' / builder.APP_NAME / (builder.APP_NAME + '.exe')
                exe.parent.mkdir(parents=True)
                exe.write_bytes(b'not-a-pe')
                return mock.Mock(returncode=0)
            with mock.patch.object(builder.sys, 'platform', 'win32'), \
                 mock.patch.object(builder.subprocess, 'run', side_effect=fake_run):
                with self.assertRaisesRegex(builder.BuildError, 'not a Windows executable'):
                    builder.build(dest)
            self.assertTrue((dest / 'build.log').is_file())

    def test_entrypoint_requires_absolute_appdata(self):
        for path in ['', 'relative/path']:
            with self.subTest(path=path), self.assertRaises(RuntimeError):
                entry.data_directory(path)

    def test_entrypoint_refuses_unsafe_parent_symlink(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / 'real'
            target.mkdir()
            link = Path(temp) / 'link'
            try:
                link.symlink_to(target, target_is_directory=True)
            except OSError:
                self.skipTest('Symlinks unavailable in this environment')
            with self.assertRaisesRegex(RuntimeError, 'redirected'):
                entry.data_directory(str(link))

    def test_entrypoint_does_not_create_db_or_folder_during_plan(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = entry.data_directory(temp)
            self.assertFalse(folder.exists())

    def test_cli_plan_and_explicit_release_hold(self):
        with tempfile.TemporaryDirectory() as temp:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                rc = builder.main(['--out', str(Path(temp)/'new'), '--plan'])
            self.assertEqual(rc, 0)
            info = json.loads(output.getvalue())
            self.assertFalse(info['production_ready'])
            self.assertFalse(info['network'])


if __name__ == '__main__':
    unittest.main()
