"""Real user-observed Onbid envelope shape; mock data only, no credentials/network."""
from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
import unittest

from bidax.api_gateway import create_plan, fetch_quarantined
from bidax.response_audit import inspect_packet, plan_remaining_pages
from bidax.response_shape import diagnose_packet


class _Reply:
    status = 200
    headers = {"Content-Type": "application/json"}

    def __init__(self, content):
        self.content = json.dumps(content).encode("utf-8")

    def read(self, n):
        return self.content[:n]

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None


class _Opener:
    def __init__(self, body):
        self.body = body
        self.calls = 0

    def open(self, request, timeout=15):
        self.calls += 1
        return _Reply(self.body)


class OnbidRootEnvelopeTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.plan = create_plan("onbid_result_list", {
            "parameters": {"cltrTypeCd":"0001", "prptDivCd":"0002",
                           "opbdDtStart":"20261110", "opbdDtEnd":"20261113"},
            "page": 1, "rows": 10})
        self.path = self.root / 'packet.json'

    def capture(self, body):
        if self.path.exists():
            self.path.unlink()
        stub = _Opener(body)
        fetch_quarantined(self.plan, service_key='FAKE_SECRET_ONLY_FOR_TEST',
                          permission=True, db_path=self.root/'quota.db',
                          output_path=self.path, opener=stub,
                          now=datetime(2026, 11, 14, tzinfo=timezone.utc))
        self.assertEqual(stub.calls, 1)
        return self.path

    def envelope(self, code='00', page=1, total=2, rows=None):
        if rows is None:
            rows = [{'cltrMngNo': 'PLACEHOLDER_1'}, {'cltrMngNo': 'PLACEHOLDER_2'}]
        return {'header': {'resultCode': code, 'resultMsg': 'DO_NOT_ECHO_THIS_MESSAGE'},
                'body': {'items': {'item': rows}, 'numOfRows': 10,
                         'pageNo': page, 'totalCount': total}}

    def test_observed_root_header_body_can_be_reviewed_not_imported(self):
        path = self.capture(self.envelope())
        out = inspect_packet(path)
        self.assertEqual(out['state'], 'STRUCTURE_CANDIDATE_REVIEW_REQUIRED')
        self.assertEqual(out['items_in_page'], 2)
        self.assertEqual(out['integrity'], 'CANONICAL_RESPONSE_SHA256_MATCH')
        self.assertFalse(out['auto_import_allowed'])
        self.assertFalse(out['source_field_mapping_verified'])
        self.assertFalse(out['legal_qualification_approved'])
        self.assertNotIn('DO_NOT_ECHO_THIS_MESSAGE', json.dumps(out))
        shape = diagnose_packet(path)
        self.assertEqual(shape['inspection_state'], 'STRUCTURE_CANDIDATE_REVIEW_REQUIRED')
        self.assertEqual(shape['nodes'][0]['known_keys'], ['header', 'body'])

    def test_real_observed_186_total_with_10_items_plans_19_pages_offline(self):
        path = self.capture(self.envelope(total=186, rows=[{'fake_id': i} for i in range(10)]))
        out = inspect_packet(path)
        self.assertEqual((out['page'], out['items_in_page'], out['total_count_reported']), (1, 10, 186))
        p = plan_remaining_pages(path)
        self.assertEqual((p['reported_total_pages'], p['next_page_if_sequential'], p['pages_after_inspected_page']), (19, 2, 18))
        self.assertFalse(p['auto_fetch_allowed'])
        self.assertFalse(p['other_pages_verified'])
        self.assertNotIn('fake_id', json.dumps(p))

    def test_failed_packet_never_offers_next_page(self):
        path = self.capture(self.envelope(total=186, rows=[{'a': i} for i in range(10)], page=2))
        p = plan_remaining_pages(path)
        self.assertEqual(p['state'], 'REVIEW_HOLD')
        self.assertFalse(p['auto_fetch_allowed'])
        self.assertNotIn('next_page_if_sequential', p)

    def test_local_page_plan_cli_no_network_and_no_values(self):
        import io, contextlib
        from unittest.mock import patch
        from bidax.cli import main
        path = self.capture(self.envelope(total=186, rows=[{'private_amount': i} for i in range(10)]))
        out = io.StringIO()
        with patch('bidax.api_gateway.fetch_quarantined', side_effect=AssertionError('network forbidden')):
            with contextlib.redirect_stdout(out):
                main(['--db', str(self.root/'unused.db'), 'api-page-plan', str(path)])
        report = json.loads(out.getvalue())
        self.assertEqual(report['reported_total_pages'], 19)
        self.assertNotIn('private_amount', out.getvalue())
        self.assertFalse(report['auto_fetch_allowed'])

    def test_onbid_direct_root_error_not_saved_by_transport(self):
        body = self.envelope(code='99')
        opener = _Opener(body)
        with self.assertRaisesRegex(ValueError, 'credential redacted'):
            fetch_quarantined(self.plan, service_key='FAKE_SECRET_ONLY_FOR_TEST',
                              permission=True, db_path=self.root/'quota.db',
                              output_path=self.path, opener=opener,
                              now=datetime(2026, 11, 14, tzinfo=timezone.utc))
        self.assertEqual(opener.calls, 1)
        self.assertFalse(self.path.exists())

    def test_onbid_last_page_has_no_followup(self):
        plan = create_plan('onbid_result_list', {
            'parameters': {'cltrTypeCd':'0001','prptDivCd':'0002',
                           'opbdDtStart':'20261110','opbdDtEnd':'20261113'},
            'page': 19, 'rows': 10})
        self.plan = plan
        path = self.capture({'header': {'resultCode': '00'},
                             'body': {'items': {'item': [{'fake_id':i} for i in range(6)]},
                                      'pageNo': 19, 'numOfRows':10, 'totalCount':186}})
        p = plan_remaining_pages(path)
        self.assertEqual(p['reported_total_pages'], 19)
        self.assertIsNone(p['next_page_if_sequential'])
        self.assertEqual(p['pages_after_inspected_page'], 0)

    def test_non_success_code_stays_on_hold(self):
        # Historical/foreign packets may contain an agency error; the new
        # transport refuses them before persistence, while inspector holds.
        from bidax.response_audit import _fingerprint
        path = self.capture(self.envelope())
        packet = json.loads(path.read_text(encoding='utf-8'))
        packet['raw_response']['header']['resultCode'] = '99'
        packet['canonical_response_sha256'] = _fingerprint(packet['raw_response'])
        path.write_text(json.dumps(packet), encoding='utf-8')
        out = inspect_packet(path)
        self.assertEqual((out['state'], out['reason']), ('REVIEW_HOLD', 'RESPONSE_NOT_SUCCESS'))

    def test_wrong_page_stays_on_hold(self):
        out = inspect_packet(self.capture(self.envelope(page=2)))
        self.assertEqual(out['reason'], 'PAGINATION_MISMATCH_OR_UNKNOWN')

    def test_wrong_item_count_stays_on_hold(self):
        out = inspect_packet(self.capture(self.envelope(total=3)))
        self.assertEqual(out['reason'], 'ITEM_COUNT_INCONSISTENT')

    def test_ambiguous_envelope_stays_on_hold(self):
        ambiguous = self.envelope()
        ambiguous['response'] = self.envelope()
        out = inspect_packet(self.capture(ambiguous))
        self.assertEqual((out['state'], out['reason']), ('REVIEW_HOLD', 'AMBIGUOUS_ENVELOPE'))

    def test_canonical_integrity_still_enforced_for_direct_root(self):
        path = self.capture(self.envelope())
        packet = json.loads(path.read_text(encoding='utf-8'))
        packet['raw_response']['body']['totalCount'] = 999
        path.write_text(json.dumps(packet), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'changed after capture'):
            inspect_packet(path)

    def test_sensitive_reflected_field_rejected_before_saved(self):
        body = self.envelope()
        body['body']['serviceKey'] = 'DO_NOT_SAVE'
        opener = _Opener(body)
        with self.assertRaisesRegex(ValueError, 'credential redacted'):
            fetch_quarantined(self.plan, service_key='FAKE_SECRET_ONLY_FOR_TEST',
                              permission=True, db_path=self.root/'quota.db',
                              output_path=self.path, opener=opener,
                              now=datetime(2026, 11, 14, tzinfo=timezone.utc))
        self.assertFalse(self.path.exists())


if __name__ == '__main__':
    unittest.main()
