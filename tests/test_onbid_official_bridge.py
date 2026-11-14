"""Real-observed field-only Onbid contract tests; never touch the actual API."""
import contextlib
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from bidax.api_gateway import create_plan, fetch_quarantined
from bidax.onbid_official_bridge import field_audit, write_detail_candidate_queue


class Reply:
    status = 200
    headers = {'Content-Type': 'application/json'}

    def __init__(self, payload):
        self.data = json.dumps(payload).encode('utf-8')

    def read(self, size):
        return self.data[:size]

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None


class Opener:
    def __init__(self, raw):
        self.raw = raw
        self.calls = 0

    def open(self, request, timeout=15):
        self.calls += 1
        return Reply(self.raw)


class OnbidOfficialBridgeTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.packet = self.root / 'packet.json'
        self.out = self.root / 'candidates.json'
        self.plan = create_plan('onbid_result_list', {
            'parameters': {'cltrTypeCd': '0001', 'prptDivCd': '0002',
                           'opbdDtStart': '20261110', 'opbdDtEnd': '20261113'},
            'page': 1, 'rows': 10})

    def rows(self, n=10):
        return [{'cltrMngNo': f'2024-1100-{i:06d}', 'pbctCdtnNo': str(i+1),
                 'onbidCltrNm': f'PRIVATE_NAME_{i}', 'SENSITIVE_LOCATION': f'customeraddr_{i}'}
                for i in range(n)]

    def capture(self, items=None, *, total=186):
        if items is None:
            items = self.rows()
        raw = {'header': {'resultCode': '00'},
               'body': {'items': {'item': items}, 'numOfRows': 10,
                        'pageNo': 1, 'totalCount': total}}
        opener = Opener(raw)
        fetch_quarantined(self.plan, service_key='TEST_ONLY_NO_REAL_KEY', permission=True,
                          db_path=self.root / 'quota.sqlite', output_path=self.packet,
                          opener=opener, now=datetime(2026, 11, 14, tzinfo=timezone.utc))
        self.assertEqual(opener.calls, 1)
        return self.packet

    def test_safe_field_coverage_from_186_reported_first_page(self):
        report = field_audit(self.capture())
        self.assertEqual(report['items_in_page'], 10)
        self.assertEqual(report['reported_total_items'], 186)
        self.assertEqual(report['items_with_valid_property_and_condition_id'], 10)
        self.assertEqual(report['known_public_field_presence_counts']['cltrMngNo'], 10)
        self.assertEqual(report['unknown_fields_count'], 10)
        self.assertNotIn('PRIVATE_NAME', json.dumps(report))
        self.assertNotIn('SENSITIVE_LOCATION', json.dumps(report))
        self.assertFalse(report['auto_import_allowed'])

    def test_no_ids_is_safe_and_reports_missing(self):
        rows = [{'other_private_key': f'secret_{i}'} for i in range(10)]
        report = field_audit(self.capture(rows))
        self.assertEqual(report['items_with_valid_property_id'], 0)
        self.assertEqual(report['items_with_valid_property_and_condition_id'], 0)
        self.assertEqual(report['known_public_field_presence_counts']['cltrMngNo'], 0)

    def test_explicit_consent_creates_private_unexecuted_candidate_queue(self):
        self.capture()
        report = write_detail_candidate_queue(self.packet, self.out, consent=True)
        self.assertEqual(report['requests_prepared'], 10)
        self.assertEqual(report['network_calls'], 0)
        self.assertFalse(report['auto_import_allowed'])
        self.assertNotIn('2024-1100', json.dumps(report))
        data = json.loads(self.out.read_text())
        self.assertEqual(len(data['requests']), 10)
        self.assertEqual(data['requests'][0]['dataset_id'], 15157254)
        self.assertEqual(data['requests'][0]['request_without_key']['cltrMngNo'], '2024-1100-000000')
        self.assertNotIn('serviceKey', self.out.read_text())
        self.assertFalse(data['execution_authorized'])
        if __import__('os').name == 'posix':
            self.assertEqual(self.out.stat().st_mode & 0o777, 0o600)

    def test_no_consent_refuses_file_and_does_not_read_user_data(self):
        self.capture()
        with self.assertRaises(PermissionError):
            write_detail_candidate_queue(self.packet, self.out, consent=False)
        self.assertFalse(self.out.exists())

    def test_duplicate_identity_refuses_whole_queue(self):
        items = self.rows()
        items[7] = dict(items[1])
        self.capture(items)
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            write_detail_candidate_queue(self.packet, self.out, consent=True)
        self.assertFalse(self.out.exists())

    def test_missing_property_id_refuses_whole_queue(self):
        items = self.rows()
        del items[5]['cltrMngNo']
        self.capture(items)
        with self.assertRaisesRegex(ValueError, 'missing or invalid'):
            write_detail_candidate_queue(self.packet, self.out, consent=True)
        self.assertFalse(self.out.exists())

    def test_bad_condition_identifier_refuses(self):
        items = self.rows()
        items[3]['pbctCdtnNo'] = 'candidate?serviceKey=secret'
        self.capture(items)
        with self.assertRaisesRegex(ValueError, 'condition identifier'):
            write_detail_candidate_queue(self.packet, self.out, consent=True)
        self.assertFalse(self.out.exists())

    def test_condition_missing_uses_documented_optional_criterion(self):
        items = self.rows()
        for x in items:
            del x['pbctCdtnNo']
        self.capture(items)
        report = write_detail_candidate_queue(self.packet, self.out, consent=True)
        self.assertEqual(report['requests_prepared'], 10)
        data = json.loads(self.out.read_text())
        self.assertNotIn('pbctCdtnNo', data['requests'][0]['request_without_key'])

    def test_legacy_packet_with_missing_canonical_hash_fails(self):
        self.capture()
        packet = json.loads(self.packet.read_text())
        packet.pop('canonical_response_sha256')
        self.packet.write_text(json.dumps(packet))
        with self.assertRaisesRegex(ValueError, 'legacy'):
            field_audit(self.packet)

    def test_tampered_existing_response_fails_without_new_file(self):
        self.capture()
        packet = json.loads(self.packet.read_text())
        packet['raw_response']['body']['items']['item'][0]['cltrMngNo'] = 'TAMPERED'
        self.packet.write_text(json.dumps(packet))
        with self.assertRaises(ValueError):
            write_detail_candidate_queue(self.packet, self.out, consent=True)
        self.assertFalse(self.out.exists())

    def test_existing_destination_never_overwritten(self):
        self.capture()
        self.out.write_text('EXISTING_KEEP')
        with self.assertRaises(FileExistsError):
            write_detail_candidate_queue(self.packet, self.out, consent=True)
        self.assertEqual(self.out.read_text(), 'EXISTING_KEEP')

    def test_other_api_never_promoted_to_onbid_list(self):
        self.capture()
        packet = json.loads(self.packet.read_text())
        packet['service'] = 'onbid_result_detail'
        self.packet.write_text(json.dumps(packet))
        with self.assertRaises(ValueError):
            field_audit(self.packet)

    def test_cli_safe_audit_does_not_call_network_or_print_private_values(self):
        self.capture()
        from bidax.cli import main
        output = io.StringIO()
        with patch('bidax.api_gateway.fetch_quarantined', side_effect=AssertionError('network forbidden')):
            with contextlib.redirect_stdout(output):
                main(['--db', str(self.root / 'unused.db'), 'onbid-field-audit', str(self.packet)])
        report = json.loads(output.getvalue())
        self.assertEqual(report['items_in_page'], 10)
        self.assertNotIn('PRIVATE_NAME', output.getvalue())
        self.assertNotIn('TEST_ONLY_NO_REAL_KEY', output.getvalue())

    def test_cli_queue_needs_flag_and_runs_entirely_offline(self):
        self.capture()
        from bidax.cli import main
        output = io.StringIO()
        with patch('bidax.api_gateway.fetch_quarantined', side_effect=AssertionError('network forbidden')):
            with contextlib.redirect_stdout(output):
                main(['--db', str(self.root / 'unused.db'), 'onbid-detail-queue',
                      str(self.packet), '--out', str(self.out), '--consent'])
        self.assertTrue(self.out.is_file())
        self.assertEqual(json.loads(output.getvalue())['network_calls'], 0)

    def test_symlinked_packet_rejected(self):
        self.capture()
        link = self.root / 'packet-link.json'
        try:
            link.symlink_to(self.packet)
        except (OSError, NotImplementedError):
            self.skipTest('symlink unavailable')
        with self.assertRaisesRegex(ValueError, 'linked'):
            field_audit(link)


if __name__ == '__main__':
    unittest.main()
