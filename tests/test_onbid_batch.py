"""Onbid multi-page offline checkpoint; all packets are synthetic/no network."""
from datetime import datetime, timezone
import contextlib
import io
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from uuid import uuid4

from bidax.api_gateway import create_plan, fetch_quarantined
from bidax.onbid_batch import batch_status, stage_page


class _Reply:
    status = 200
    headers = {'Content-Type': 'application/json'}
    def __init__(self, payload): self.content = json.dumps(payload).encode('utf-8')
    def read(self, count): return self.content[:count]
    def __enter__(self): return self
    def __exit__(self, *args): pass


class OnbidCheckpointTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.db = self.root/'offline.db'
        self.id = str(uuid4())
        self.when = datetime(2026, 11, 14, tzinfo=timezone.utc)
        self.filters = {'cltrTypeCd':'0001','prptDivCd':'0002',
                        'opbdDtStart':'20261110','opbdDtEnd':'20261113'}

    def capture(self, page, total, *, size=10, mutate_filters=None, payload_rows=None, non_success=False):
        filters = mutate_filters if mutate_filters is not None else self.filters
        plan = create_plan('onbid_result_list', {'parameters':filters,'page':page,'rows':size})
        expected = min(size, max(0,total-(page-1)*size))
        rows = ([{'fake_note': 'PRIVATE_ASSET_TEXT_%s' % k} for k in range(expected)]
                if payload_rows is None else payload_rows)
        response = {'header': {'resultCode': '99' if non_success else '00'},
                    'body': {'items': {'item': rows}, 'pageNo': page,
                             'numOfRows': size, 'totalCount': total}}
        class Opener:
            def open(self, request, timeout=15): return _Reply(response)
        path = self.root / ('p%s_%s_%s.json' % (page, total, len(list(self.root.iterdir()))))
        if non_success:
            with self.assertRaisesRegex(ValueError, 'credential redacted'):
                fetch_quarantined(plan, service_key='PRIVATE_TEST_KEY', permission=True,
                                  db_path=self.root/'quota.db', output_path=path, opener=Opener(), now=self.when)
            return path
        fetch_quarantined(plan, service_key='PRIVATE_TEST_KEY', permission=True,
                          db_path=self.root/'quota.db', output_path=path, opener=Opener(), now=self.when)
        return path

    def test_186_total_first_page_staged_missing_18(self):
        p = self.capture(1,186)
        result = stage_page(self.db,self.id,p,consent=True)
        self.assertEqual(result['reported_total_items'],186)
        self.assertEqual(result['reported_total_pages'],19)
        self.assertEqual(result['verified_local_pages'],[1])
        self.assertEqual(result['missing_pages'],list(range(2,20)))
        self.assertEqual(result['verified_local_item_count'],10)
        self.assertFalse(result['sealed'])
        self.assertFalse(result['auto_import_allowed'])
        self.assertFalse(result['source_field_mapping_verified'])
        self.assertEqual(result['network_calls'],0)

    def test_reverse_order_recovery_and_exact_final_seal(self):
        second = self.capture(2,11)
        first = self.capture(1,11)
        partial = stage_page(self.db,self.id,second,consent=True)
        self.assertEqual(partial['missing_pages'],[1])
        complete = stage_page(self.db,self.id,first,consent=True)
        self.assertEqual(complete['state'],'OFFLINE_COMPLETE_NOT_IMPORTED')
        self.assertEqual(complete['verified_local_item_count'],11)
        self.assertEqual(complete['verified_local_pages'],[1,2])
        self.assertTrue(complete['all_local_pages_verified'])
        self.assertTrue(complete['sealed'])
        self.assertFalse(complete['auto_import_allowed'])
        replay=stage_page(self.db,self.id,first,consent=True)
        self.assertTrue(replay['page_replayed'])
        self.assertEqual(replay['verified_local_pages'],[1,2])

    def test_replay_identical_page_is_idempotent(self):
        p=self.capture(1,19)
        stage_page(self.db,self.id,p,consent=True)
        replay=stage_page(self.db,self.id,p,consent=True)
        self.assertTrue(replay['page_replayed'])
        with contextlib.closing(sqlite3.connect(self.db)) as conn:
            self.assertEqual(conn.execute('select count(*) from onbid_stage_pages').fetchone()[0],1)

    def test_changed_reported_total_rejected(self):
        stage_page(self.db,self.id,self.capture(1,21),consent=True)
        with self.assertRaisesRegex(ValueError,'changed filters, reported total'):
            stage_page(self.db,self.id,self.capture(2,22),consent=True)
        self.assertEqual(batch_status(self.db,self.id)['verified_local_pages'],[1])

    def test_changed_filters_rejected_without_partial_insert(self):
        stage_page(self.db,self.id,self.capture(1,21),consent=True)
        filters=dict(self.filters);filters['prptDivCd']='0003'
        with self.assertRaisesRegex(ValueError,'changed filters'):
            stage_page(self.db,self.id,self.capture(2,21,mutate_filters=filters),consent=True)
        self.assertEqual(batch_status(self.db,self.id)['missing_pages'],[2,3])

    def test_changed_page_size_rejected(self):
        stage_page(self.db,self.id,self.capture(1,21),consent=True)
        with self.assertRaises(ValueError):
            stage_page(self.db,self.id,self.capture(2,21,size=5),consent=True)

    def test_page_replacement_rejected(self):
        old=self.capture(1,15)
        stage_page(self.db,self.id,old,consent=True)
        newer=self.capture(1,15,payload_rows=[{'changed':'x'} for _ in range(10)])
        with self.assertRaisesRegex(ValueError,'page replay changed'):
            stage_page(self.db,self.id,newer,consent=True)
        self.assertEqual(batch_status(self.db,self.id)['verified_local_pages'],[1])

    def test_modified_original_after_stage_is_detected(self):
        p=self.capture(1,15)
        stage_page(self.db,self.id,p,consent=True)
        data=json.loads(p.read_text(encoding='utf8'))
        data['raw_response']['body']['items']['item'][0]['fake_note']='CHANGED_AFTER_CAPTURE'
        p.write_text(json.dumps(data),encoding='utf8')
        with self.assertRaisesRegex(ValueError,'missing, modified or invalid'):
            batch_status(self.db,self.id)

    def test_removed_original_after_seal_detected(self):
        p=self.capture(1,1)
        stage_page(self.db,self.id,p,consent=True)
        p.unlink()
        with self.assertRaisesRegex(ValueError,'missing, modified or invalid'):
            batch_status(self.db,self.id)

    def test_absolutely_no_item_values_in_db_or_summary(self):
        p=self.capture(1,1,payload_rows=[{'raw':'CUSTOMER_PRIVATE_ROW_CONTENT'}])
        summary=stage_page(self.db,self.id,p,consent=True)
        with contextlib.closing(sqlite3.connect(self.db)) as conn:
            payload=' '.join(str(row) for tbl in ('onbid_stage_batches','onbid_stage_pages')
                             for row in conn.execute('select * from '+tbl))
        self.assertNotIn('CUSTOMER_PRIVATE_ROW_CONTENT',payload)
        self.assertNotIn('PRIVATE_TEST_KEY',payload)
        self.assertNotIn('CUSTOMER_PRIVATE_ROW_CONTENT',json.dumps(summary))
        self.assertFalse(summary['raw_records_stored_in_sqlite'])

    def test_explicit_consent_required_and_doesnt_create_db(self):
        p=self.capture(1,1)
        with self.assertRaises(PermissionError):
            stage_page(self.db,self.id,p,consent=False)
        self.assertFalse(self.db.exists())

    def test_bad_batch_id_rejected_before_writes(self):
        p=self.capture(1,1)
        with self.assertRaises(ValueError):stage_page(self.db,'../../escape',p,consent=True)
        self.assertFalse(self.db.exists())

    def test_staging_rejects_untrusted_or_symlink_packet(self):
        p=self.capture(1,1)
        link=self.root/'link.json'
        try:link.symlink_to(p)
        except (NotImplementedError,OSError):self.skipTest('symlinks not permitted')
        with self.assertRaises(ValueError):stage_page(self.db,self.id,link,consent=True)
        self.assertFalse(self.db.exists())

    def test_responded_error_is_not_saved_or_staged(self):
        path=self.capture(1,10,non_success=True)
        self.assertFalse(path.exists())
        with self.assertRaises(ValueError):stage_page(self.db,self.id,path,consent=True)
        self.assertFalse(self.db.exists())

    def test_unknown_batch_rejected(self):
        # No confusing empty collection with a successful batch.
        with self.assertRaises(ValueError):
            batch_status(self.db,self.id)
        self.assertFalse(self.db.exists())

    def test_empty_official_batch_seals_one_empty_page(self):
        p=self.capture(1,0)
        result=stage_page(self.db,self.id,p,consent=True)
        self.assertTrue(result['sealed'])
        self.assertEqual(result['reported_total_pages'],1)
        self.assertEqual(result['verified_local_item_count'],0)

    def test_cli_stage_and_status_are_offline(self):
        p=self.capture(1,11)
        from bidax.cli import main
        output=io.StringIO()
        with patch('bidax.api_gateway.fetch_quarantined',side_effect=AssertionError('network forbidden')):
            with contextlib.redirect_stdout(output):
                main(['--db',str(self.db),'onbid-stage-page',self.id,str(p),'--consent'])
                main(['--db',str(self.db),'onbid-stage-status',self.id])
        self.assertEqual(output.getvalue().count('"network_calls": 0'),2)
        self.assertNotIn('PRIVATE_ASSET_TEXT',output.getvalue())

    def test_stage_other_batch_is_separate(self):
        p=self.capture(1,5)
        one=stage_page(self.db,self.id,p,consent=True)
        two=stage_page(self.db,str(uuid4()),p,consent=True)
        self.assertTrue(one['sealed'] and two['sealed'])
        with contextlib.closing(sqlite3.connect(self.db)) as conn:
            self.assertEqual(conn.execute('select count(*) from onbid_stage_batches').fetchone()[0],2)

if __name__=='__main__':unittest.main()
