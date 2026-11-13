"""No-network regression for same portal key across four individually approved APIs."""
from __future__ import annotations

from datetime import datetime, timezone
from io import BytesIO
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from bidax.api_gateway import create_plan, fetch_quarantined


class FakeResponse:
    status=200
    headers={"Content-Type":"application/json;charset=utf-8"}
    def __init__(self, data):
        self.data=BytesIO(data)
    def __enter__(self): return self
    def __exit__(self,*exc): self.data.close()
    def read(self, number): return self.data.read(number)


class FakeOpener:
    def __init__(self, data=b'{"response":{"header":{"resultCode":"00"},"body":{"items":[]}}}'):
        self.data=data
        self.requests=[]
    def open(self, req, timeout=15):
        self.requests.append(req)
        return FakeResponse(self.data)


class APIGatewayTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.d=Path(self.tmp.name)
        self.db=self.d/'budget.db'
        self.now=datetime(2026,11,14,0,0,tzinfo=timezone.utc)
        self.g2b = create_plan('g2b_goods',{'start':'2026-11-12T00:00:00+09:00',
            'end':'2026-11-13T00:00:00+09:00','page':1,'rows':10})
        self.onbid = create_plan('onbid_result_detail',{'parameters':{'cltrMngNo':'2024-1100-084555'},'page':1,'rows':10})

    def fetch(self, plan, filename, **kw):
        opener=kw.pop('opener', FakeOpener())
        result=fetch_quarantined(plan, service_key='SHARED_SECRET_123', permission=True,
            db_path=self.db,output_path=self.d/filename,opener=opener,now=self.now,**kw)
        return result,opener

    def test_offline_plans_contain_no_key_and_correct_separate_paths(self):
        self.assertNotIn('serviceKey',json.dumps(self.g2b))
        self.assertNotIn('serviceKey',json.dumps(self.onbid))
        self.assertIn('BidPublicInfoService02',self.g2b['endpoint'])
        self.assertTrue(self.onbid['endpoint'].endswith('getCltrBidRsltDtl2'))

    def test_result_list_is_verified_pinned_operation(self):
        p=create_plan('onbid_result_list',{'parameters':{'cltrTypeCd':'0001','prptDivCd':'0002',
            'opbdDtStart':'20260401','opbdDtEnd':'20260402'},'page':1,'rows':10})
        self.assertEqual(p['dataset_id'],15157252)
        self.assertTrue(p['endpoint'].endswith('/getCltrBidRsltList2'))

    def test_announcement_operation_remains_blocked(self):
        p=create_plan('onbid_announcement_assets',{'parameters':{'pbancMngNo':'202406-21411-00'},'page':1,'rows':10})
        self.assertFalse(p['ready'])
        with self.assertRaisesRegex(ValueError,'not independently verified'):
            fetch_quarantined(p,service_key='key',permission=True,db_path=self.db,
                              output_path=self.d/'out.json',opener=FakeOpener())
        self.assertFalse(self.db.exists())

    def test_live_requires_explicit_permission(self):
        with self.assertRaises(PermissionError):
            fetch_quarantined(self.onbid,service_key='key',permission=False,db_path=self.db,
                              output_path=self.d/'out.json',opener=FakeOpener())
        self.assertFalse(self.db.exists())

    def test_one_key_two_services_two_independent_counters(self):
        a,first=self.fetch(self.g2b,'g2b.json',daily_limit=1)
        b,second=self.fetch(self.onbid,'onbid.json',daily_limit=1)
        self.assertEqual(a['state'],'QUARANTINED_UNVERIFIED_OFFICIAL_MAPPING')
        self.assertEqual(b['state'],'QUARANTINED_UNVERIFIED_OFFICIAL_MAPPING')
        for request in (first.requests[0],second.requests[0]):
            self.assertIn('serviceKey=SHARED_SECRET_123',request.full_url)
        self.assertNotIn('SHARED_SECRET_123',json.dumps(a)+json.dumps(b))
        self.assertNotIn('SHARED_SECRET_123',(self.d/'g2b.json').read_text())
        c=sqlite3.connect(self.db)
        try:
            self.assertEqual(dict(c.execute('SELECT service,count FROM api_gateway_attempts')), {'g2b_goods':1,'onbid_result_detail':1})
        finally:
            c.close()

    def test_no_key_stored_in_sqlite_or_local_quarantine(self):
        self.fetch(self.onbid,'onbid.json')
        self.assertNotIn(b'SHARED_SECRET_123',self.db.read_bytes())
        self.assertNotIn(b'SHARED_SECRET_123',(self.d/'onbid.json').read_bytes())
        self.assertEqual(json.loads((self.d/'onbid.json').read_text())['dataset_id'],15157254)

    def test_existing_output_is_not_overwritten_and_no_network(self):
        out=self.d/'old.json';out.write_text('DO_NOT_OVERWRITE')
        fake=FakeOpener()
        with self.assertRaises(FileExistsError):
            self.fetch(self.onbid,'old.json',opener=fake)
        self.assertEqual(fake.requests,[])
        self.assertEqual(out.read_text(),'DO_NOT_OVERWRITE')

    def test_replayed_budget_stops_before_second_network(self):
        self.fetch(self.onbid,'one.json',daily_limit=1)
        fake=FakeOpener()
        with self.assertRaisesRegex(ValueError,'budget exhausted'):
            self.fetch(self.onbid,'two.json',daily_limit=1,opener=fake)
        self.assertEqual(fake.requests,[])
        self.assertFalse((self.d/'two.json').exists())

    def test_modified_endpoint_rejected_before_network(self):
        p={**self.onbid,'endpoint':'https://evil.example/secret'}
        fake=FakeOpener()
        with self.assertRaisesRegex(ValueError,'modified API plan'):
            self.fetch(p,'bad.json',opener=fake)
        self.assertEqual(fake.requests,[])

    def test_modified_parameters_rejected_before_network(self):
        p={**self.onbid,'parameters':{**self.onbid['parameters'],'serviceKey':'oops'}}
        with self.assertRaises(ValueError):
            self.fetch(p,'bad.json')
        self.assertFalse(self.db.exists())

    def test_bad_response_no_file_no_secret_leak(self):
        fake=FakeOpener(b'{"response":{"header":{"resultCode":"20","resultMsg":"SECRET"}}}')
        with self.assertRaisesRegex(ValueError,'credential redacted') as e:
            self.fetch(self.onbid,'bad.json',opener=fake)
        self.assertNotIn('SHARED_SECRET_123',str(e.exception))
        self.assertFalse((self.d/'bad.json').exists())

    def test_invalid_json_fails_closed(self):
        with self.assertRaisesRegex(ValueError,'credential redacted'):
            self.fetch(self.onbid,'bad.json',opener=FakeOpener(b'{invalid'))
        self.assertFalse((self.d/'bad.json').exists())

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaisesRegex(ValueError,'credential redacted'):
            self.fetch(self.onbid,'bad.json',opener=FakeOpener(b'{"a":1,"a":2}'))
        self.assertFalse((self.d/'bad.json').exists())

    def test_bad_daily_limit_does_not_make_http_request(self):
        fake=FakeOpener()
        with self.assertRaisesRegex(ValueError,'daily_limit'):
            self.fetch(self.onbid,'bad.json',opener=fake,daily_limit=1001)
        self.assertEqual(fake.requests,[])

    def test_output_permissions_owner_only_on_posix(self):
        self.fetch(self.onbid,'ok.json')
        self.assertEqual((self.d/'ok.json').stat().st_mode & 0o777,0o600)

    def test_date_range_g2b_7_days_validation(self):
        with self.assertRaises(ValueError):
            create_plan('g2b_goods',{'start':'2026-10-01T00:00:00+09:00',
                'end':'2026-11-13T00:00:00+09:00','page':1,'rows':10})

    def test_reflected_key_never_saved(self):
        blob=b'{"debug":"SHARED_SECRET_123"}'
        with self.assertRaisesRegex(ValueError,'credential redacted'):
            self.fetch(self.onbid,'leak.json',opener=FakeOpener(blob))
        self.assertFalse((self.d/'leak.json').exists())

    def test_http_retry_503_consumes_two_budget_units(self):
        from urllib.error import HTTPError
        class RetryOpener(FakeOpener):
            def open(self,req,timeout=15):
                self.requests.append(req)
                if len(self.requests)==1:
                    raise HTTPError(req.full_url,503,'service unavailable',{},None)
                return FakeResponse(self.data)
        fake=RetryOpener()
        response,_=self.fetch(self.onbid,'retry.json',opener=fake,max_attempts=2,sleep=lambda _:None)
        self.assertEqual(response['calls_this_run'],2)
        c=sqlite3.connect(self.db)
        try:
            self.assertEqual(c.execute('SELECT count FROM api_gateway_attempts').fetchone()[0],2)
        finally:
            c.close()

    def test_unapproved_key_raises_before_using_budget(self):
        with self.assertRaisesRegex(ValueError,'key required'):
            fetch_quarantined(self.onbid,service_key='',permission=True,db_path=self.db,
                 output_path=self.d/'none.json',opener=FakeOpener())
        self.assertFalse(self.db.exists())

    def test_different_known_operation_fails_if_modified(self):
        p={**self.onbid,'dataset_id':15157220}
        with self.assertRaisesRegex(ValueError,'modified API plan'):
            self.fetch(p,'none.json')
        self.assertFalse(self.db.exists())

    def test_cli_plan_does_not_prompt_or_touch_network_or_db(self):
        import contextlib, io
        from bidax.cli import main
        params={'parameters':{'cltrMngNo':'2024-1100-084555'},'page':1,'rows':10}
        src=self.d/'params.json';src.write_text(json.dumps(params))
        stdout=io.StringIO()
        with patch('getpass.getpass',side_effect=AssertionError('do not prompt')):
            with contextlib.redirect_stdout(stdout):
                main(['--db',str(self.db),'api-probe','onbid_result_detail',str(src)])
        parsed=json.loads(stdout.getvalue())
        self.assertTrue(parsed['ready'])
        self.assertFalse(self.db.exists())


if __name__ == '__main__': unittest.main()
