"""BID AX customer GUI controller uses the real offline Onbid checkpoint.

All pages here are synthetic; no credential, official HTTP request, or release.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from uuid import uuid4

from bidax.api_gateway import create_plan, fetch_quarantined
from bidax.desktop import LocalController


class _Reply:
    status = 200
    headers = {'Content-Type': 'application/json'}

    def __init__(self, value):
        self.payload = json.dumps(value).encode('utf-8')

    def read(self, count):
        return self.payload[:count]

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None


class OnbidDesktopCheckpointTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.db = self.root / 'gui-owned.db'
        self.controller = LocalController(self.db)
        self.batch = str(uuid4())

    def _synthetic_packet(self, page=1, total=1):
        plan = create_plan('onbid_result_list', {
            'parameters': {'cltrTypeCd': '0001', 'prptDivCd': '0002',
                           'opbdDtStart': '20261110', 'opbdDtEnd': '20261113'},
            'page': page, 'rows': 10})
        expected_rows = min(10, max(0, total - (page - 1) * 10))
        payload = {
            'header': {'resultCode': '00'},
            'body': {'items': {'item': [{'synthetic': 'OFFLINE_ONLY'} for _ in range(expected_rows)]},
                     'pageNo': page, 'numOfRows': 10, 'totalCount': total}}
        class Opener:
            def open(self, request, timeout=15):
                return _Reply(payload)
        filename = self.root / f'synthetic-quarantine-page-{page}.json'
        fetch_quarantined(plan, service_key='NOT_A_REAL_KEY', permission=True,
                          db_path=self.root / 'mock-quota.db',
                          output_path=filename, opener=Opener(),
                          now=datetime(2026, 11, 14, tzinfo=timezone.utc))
        return filename

    def test_onbid_gui_controller_stages_and_reverifies_one_page(self):
        packet = self._synthetic_packet()
        result = self.controller.onbid_stage_page(self.batch, packet, consent=True)
        self.assertEqual(result['state'], 'OFFLINE_COMPLETE_NOT_IMPORTED')
        self.assertEqual(result['verified_local_pages'], [1])
        self.assertEqual(result['reported_total_pages'], 1)
        self.assertEqual(result['verified_local_item_count'], 1)
        self.assertFalse(result['auto_import_allowed'])
        self.assertFalse(result['source_field_mapping_verified'])
        self.assertEqual(result['network_calls'], 0)
        self.assertEqual(self.controller.onbid_stage_status(self.batch)['verified_local_pages'], [1])
        with sqlite3.connect(self.db) as conn:
            rows = conn.execute("select packet_path from onbid_stage_pages").fetchall()
            self.assertEqual(len(rows), 1)
            self.assertNotIn('OFFLINE_ONLY', str(conn.iterdump()))

    def test_gui_requires_explicit_path_consent(self):
        packet = self._synthetic_packet()
        with self.assertRaises(PermissionError):
            self.controller.onbid_stage_page(self.batch, packet, consent=False)
        self.assertFalse(self.db.exists())

    def test_gui_status_on_unknown_database_never_creates_file(self):
        with self.assertRaises(ValueError):
            self.controller.onbid_stage_status(self.batch)
        self.assertFalse(self.db.exists())

    def test_gui_bad_uuid_rejected_before_database_mutation(self):
        packet = self._synthetic_packet()
        with self.assertRaises(ValueError):
            self.controller.onbid_stage_page('not-a-uuid', packet, consent=True)
        self.assertFalse(self.db.exists())

    def test_multi_page_gui_select_and_recovery(self):
        second = self._synthetic_packet(page=2, total=11)
        first = self._synthetic_packet(page=1, total=11)
        result = self.controller.onbid_stage_pages(self.batch, [second, first], consent=True)
        self.assertEqual(result['files_processed_this_action'], 2)
        self.assertEqual(result['state'], 'OFFLINE_COMPLETE_NOT_IMPORTED')
        self.assertEqual(result['verified_local_item_count'], 11)
        self.assertEqual(result['verified_local_pages'], [1, 2])
        self.assertFalse(result['auto_import_allowed'])
        self.assertTrue(self.controller.onbid_stage_status(self.batch)['sealed'])

    def test_multi_page_gui_empty_selection_or_no_consent_never_creates_db(self):
        with self.assertRaises(ValueError):
            self.controller.onbid_stage_pages(self.batch, [], consent=True)
        with self.assertRaises(PermissionError):
            self.controller.onbid_stage_pages(self.batch, [], consent=False)
        self.assertFalse(self.db.exists())

    def test_multi_page_gui_partial_error_can_resume(self):
        first = self._synthetic_packet(page=1, total=11)
        with self.assertRaises(ValueError):
            self.controller.onbid_stage_pages(self.batch, [first, self.root / 'absent.json'], consent=True)
        state = self.controller.onbid_stage_status(self.batch)
        self.assertEqual(state['verified_local_pages'], [1])
        self.assertEqual(state['missing_pages'], [2])
        self.assertFalse(state['sealed'])

    def test_gui_reinspect_detects_original_packet_change(self):
        packet = self._synthetic_packet()
        self.controller.onbid_stage_page(self.batch, packet, consent=True)
        packet.write_bytes(packet.read_bytes() + b' ')
        with self.assertRaises(ValueError):
            self.controller.onbid_stage_status(self.batch)


if __name__ == '__main__':
    unittest.main()
