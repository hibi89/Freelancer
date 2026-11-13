"""Offline official-response quarantine inspection only; no paid/external calls."""
import contextlib
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from bidax.api_gateway import create_plan, fetch_quarantined
from bidax.response_audit import inspect_packet


class _Reply:
    status = 200
    headers = {"Content-Type": "application/json; charset=utf-8"}
    def __init__(self, data): self.data = data
    def read(self, n): return self.data[:n]
    def __enter__(self): return self
    def __exit__(self, *args): return None


class _FakeOpener:
    def __init__(self, body): self.body = body; self.calls = 0
    def open(self, req, timeout=15):
        self.calls += 1
        return _Reply(json.dumps(self.body).encode('utf-8'))


class ResponseAuditTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.folder = Path(tmp.name)
        self.db = self.folder / "budget.sqlite"
        self.target = self.folder / "first.json"
        self.plan = create_plan('onbid_result_detail', {'parameters': {'cltrMngNo': '2024-1100-084555'},'page':1,'rows':10})
        self.now = datetime(2026,11,14,tzinfo=timezone.utc)
    def body(self, total=1, rows=None, page=1, size=10, code="00"):
        if rows is None: rows = [{'cltrMngNo':'2024-1100-084555', 'pbctStatCd':'0010'}]
        return {'response': {'header':{'resultCode':code}, 'body':{'pageNo':page,'numOfRows':size,'totalCount':total,'items':{'item':rows}}}}
    def capture(self, body):
        fake = _FakeOpener(body)
        fetch_quarantined(self.plan,service_key="ONLY_LOCAL_TEST_SECRET_123",permission=True,
            db_path=self.db,output_path=self.target,opener=fake,now=self.now)
        self.assertEqual(fake.calls,1)
        return self.target
    def test_success_envelope_is_not_import_or_legal_approval(self):
        result=inspect_packet(self.capture(self.body()))
        self.assertEqual(result['state'],'STRUCTURE_CANDIDATE_REVIEW_REQUIRED')
        self.assertEqual(result['items_in_page'],1)
        self.assertEqual(result['integrity'],'CANONICAL_RESPONSE_SHA256_MATCH')
        self.assertFalse(result['auto_import_allowed'])
        self.assertFalse(result['legal_qualification_approved'])
        self.assertNotIn('cltrMngNo', json.dumps(result))
    def test_empty_page_is_not_fake_approval(self):
        out=inspect_packet(self.capture(self.body(total=0,rows=[])))
        self.assertEqual(out['items_in_page'],0)
        self.assertFalse(out['auto_import_allowed'])
    def test_mismatched_page_is_review_hold(self):
        out=inspect_packet(self.capture(self.body(page=2)))
        self.assertEqual(out['state'],'REVIEW_HOLD')
        self.assertEqual(out['reason'],'PAGINATION_MISMATCH_OR_UNKNOWN')
    def test_bad_item_count_is_hold(self):
        out=inspect_packet(self.capture(self.body(total=1,rows=[{'i':i} for i in range(11)])))
        self.assertEqual(out['reason'],'ITEM_COUNT_INCONSISTENT')
    def test_reported_total_cannot_be_more_than_actual_page_payload(self):
        out=inspect_packet(self.capture(self.body(total=8,rows=[{'x':1}])))
        self.assertEqual(out['state'],'REVIEW_HOLD')
        self.assertEqual(out['reason'],'ITEM_COUNT_INCONSISTENT')
    def test_unexpected_envelope_holds_without_ever_importing(self):
        out=inspect_packet(self.capture({'error':'unknown schema'}))
        self.assertEqual(out['state'],'REVIEW_HOLD')
        self.assertEqual(out['reason'],'UNRECOGNIZED_ENVELOPE')
    def test_tampered_saved_response_rejected(self):
        p=self.capture(self.body()); packet=json.loads(p.read_text())
        packet['raw_response']['response']['body']['totalCount']=999
        p.write_text(json.dumps(packet))
        with self.assertRaisesRegex(ValueError,'changed after capture'):
            inspect_packet(p)
    def test_wrong_service_plan_and_duplicate_keys_rejected(self):
        p=self.capture(self.body());packet=json.loads(p.read_text());packet['dataset_id']=15157220
        p.write_text(json.dumps(packet))
        with self.assertRaisesRegex(ValueError,'contract mismatch'):
            inspect_packet(p)
        p.write_text('{"source":"a","source":"b"}')
        with self.assertRaises(ValueError): inspect_packet(p)
    def test_encoded_or_json_escaped_key_reflection_never_persisted(self):
        for string in ['ONLY_LOCAL_TEST_SECRET_123', 'ONLY_LOCAL_TEST_SECRET_123'.replace('_','%5F')]:
            if self.target.exists(): self.target.unlink()
            with self.subTest(string=string):
                fake=_FakeOpener({'response':{'header':{'resultCode':'00'},'body':{'secretEcho':string}}})
                with self.assertRaisesRegex(ValueError,'credential redacted'):
                    fetch_quarantined(self.plan,service_key="ONLY_LOCAL_TEST_SECRET_123",permission=True,
                        db_path=self.db,output_path=self.target,opener=fake,now=self.now)
                self.assertFalse(self.target.exists())
    def test_returned_servicekey_field_must_be_rejected(self):
        with self.assertRaisesRegex(ValueError,'credential redacted'):
            self.capture({'response':{'header':{'resultCode':'00'},'body':{'serviceKey':'redacted-placeholder'}}})
        self.assertFalse(self.target.exists())
    def test_offline_inspection_cli_never_uses_network(self):
        p=self.capture(self.body())
        output=io.StringIO()
        from bidax.cli import main
        with patch('bidax.api_gateway.fetch_quarantined',side_effect=AssertionError('network forbidden')):
            with contextlib.redirect_stdout(output):
                main(['--db',str(self.db),'api-inspect',str(p)])
        r=json.loads(output.getvalue())
        self.assertEqual(r['state'],'STRUCTURE_CANDIDATE_REVIEW_REQUIRED')
        self.assertNotIn('ONLY_LOCAL_TEST_SECRET_123',output.getvalue())
    def test_legacy_packet_cannot_claim_hash_verified(self):
        p=self.capture(self.body()); packet=json.loads(p.read_text());packet.pop('canonical_response_sha256')
        p.write_text(json.dumps(packet))
        report=inspect_packet(p)
        self.assertEqual(report['integrity'],'LEGACY_HASH_NOT_STORED')
    def test_symbolic_link_is_not_accepted(self):
        p=self.capture(self.body()); link=self.folder/'alias.json'
        try: link.symlink_to(p)
        except (OSError, NotImplementedError): self.skipTest('symlink disabled')
        with self.assertRaisesRegex(ValueError,'linked'):
            inspect_packet(link)

if __name__ == '__main__': unittest.main()
