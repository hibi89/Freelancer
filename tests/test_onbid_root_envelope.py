"""Real user-observed Onbid envelope shape; mock data only, no credentials/network."""
from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
import unittest

from bidax.api_gateway import create_plan, fetch_quarantined
from bidax.response_audit import inspect_packet
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

    def test_non_success_code_stays_on_hold(self):
        out = inspect_packet(self.capture(self.envelope(code='99')))
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
