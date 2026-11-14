"""Contract tests for disposable frozen-EXE synthetic lifecycle; no real data."""
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from worknova_desk.core import DeskError
from worknova_desk.synthetic_acceptance import run
from tools import windows_gui_entry as entry


class SyntheticFrozenAcceptance(unittest.TestCase):
    def test_full_lifecycle_receipts_backup_restore_and_no_fixture_leaks(self):
        with tempfile.TemporaryDirectory(prefix='worknova-qa-contract-') as temp:
            report = Path(temp) / 'business-report.json'
            result = run(report)
            self.assertTrue(result['ok'])
            self.assertTrue(result['synthetic_only'])
            self.assertEqual(result['verified_receipts'], 2)
            self.assertEqual(result['verified_total_krw'], 1100)
            self.assertGreaterEqual(result['verified_restored_events'], 8)
            self.assertEqual(result, json.loads(report.read_text(encoding='utf-8')))
            self.assertEqual([p.name for p in Path(temp).iterdir()], [report.name])

    def test_refuses_overwrite_or_non_json_output(self):
        with tempfile.TemporaryDirectory(prefix='worknova-qa-contract-') as temp:
            report = Path(temp) / 'original.json'
            report.write_text('precious original', encoding='utf-8')
            with self.assertRaises(DeskError):
                run(report)
            self.assertEqual(report.read_text(encoding='utf-8'), 'precious original')
            with self.assertRaises(DeskError):
                run(Path(temp) / 'wrong-extension.txt')

    def test_frozen_entrypoint_rejects_qa_without_offline_flag(self):
        with tempfile.TemporaryDirectory(prefix='worknova-qa-contract-') as temp:
            report = Path(temp) / 'result.json'
            with mock.patch.object(entry.sys, 'platform', 'win32'), \
                 mock.patch.dict(os.environ, {'WORKNOVA_TEST_OFFLINE_ONLY': ''}):
                with self.assertRaisesRegex(RuntimeError, 'disabled'):
                    entry.main(['--synthetic-qa-report', str(report)])
            self.assertFalse(report.exists())

    def test_entrypoint_runs_qa_only_with_explicit_test_flag(self):
        with tempfile.TemporaryDirectory(prefix='worknova-qa-contract-') as temp:
            report = Path(temp) / 'result.json'
            with mock.patch.object(entry.sys, 'platform', 'win32'), \
                 mock.patch.dict(os.environ, {'WORKNOVA_TEST_OFFLINE_ONLY': '1'}):
                self.assertEqual(entry.main(['--synthetic-qa-report', str(report)]), 0)
            self.assertEqual(json.loads(report.read_text(encoding='utf-8'))['verified_receipts'], 2)


if __name__ == '__main__':
    unittest.main()
