"""P85 bounded offline staging, reminders, and mocked opt-in official transport."""
from __future__ import annotations

import io
import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4
from urllib.error import HTTPError, URLError
from bidax.batch import stage_snapshot, batch_status
from bidax.core import BidLedger
from bidax.entrypoint import default_db_path
from bidax.reminders import poll_due
from bidax.transport import fetch_one_page

NOW=datetime(2026,11,13,7,0,tzinfo=timezone.utc)
UNTIL=NOW+timedelta(days=3)
ROW={"bidNtceNo":"202611130001", "bidNtceOrd":"000", "bidNtceNm":"sample",
     "ntceInsttNm":"issuer", "bidClseDt":"202611171800",
     "bidNtceDtlUrl":"https://www.g2b.go.kr/sample"}


def response(page,rows,total=2,size=1):
    return {"response":{"header":{"resultCode":"00"},"body":{"pageNo":page,
            "numOfRows":size,"totalCount":total,"items":{"item":rows}}}}


class FakeResponse:
    status=200
    headers={"Content-Type":"application/json; charset=utf-8"}
    def __init__(self,value): self.value=value
    def __enter__(self): return self
    def __exit__(self,*exc): pass
    def read(self,size): return self.value


class MockOpener:
    def __init__(self,values): self.values=list(values); self.calls=[]
    def open(self,req,timeout):
        self.calls.append((req.full_url,timeout))
        result=self.values.pop(0)
        if isinstance(result,Exception): raise result
        return FakeResponse(result)


class TestP85(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.db=Path(self.tmp.name)/"bid.db"
        self.batch=uuid4().hex

    def stage(self,ledger,page,rows,total=2,size=1,**opts):
        return stage_snapshot(ledger,self.batch,"goods",NOW,UNTIL,
                              response(page,rows,total,size),NOW,**opts)

    def test_incremental_pages_do_not_leak_until_complete(self):
        with BidLedger(self.db) as ledger:
            a=self.stage(ledger,2,[dict(ROW,bidNtceNo="N2")])
            self.assertFalse(a["promoted"])
            self.assertEqual(ledger.current(),[])
            b=self.stage(ledger,1,[dict(ROW,bidNtceNo="N1")])
            self.assertTrue(b["promoted"])
            self.assertEqual(b["added_versions"],2)
            self.assertEqual(len(ledger.current()),2)
            c=self.stage(ledger,1,[dict(ROW,bidNtceNo="N1")])
            self.assertEqual(c["added_versions"],0)
            self.assertEqual(c["unchanged"],"completed_replay")

    def test_staging_persists_across_process_reopen(self):
        with BidLedger(self.db) as ledger:
            self.stage(ledger,1,[dict(ROW,bidNtceNo="N1")])
        with BidLedger(self.db) as ledger:
            self.assertEqual(batch_status(ledger,self.batch)["missing_pages"],[2])
            self.stage(ledger,2,[dict(ROW,bidNtceNo="N2")])
            self.assertEqual(len(ledger.current()),2)

    def test_same_page_contradiction_rejected(self):
        with BidLedger(self.db) as ledger:
            self.stage(ledger,1,[dict(ROW,bidNtceNo="N1")])
            with self.assertRaisesRegex(ValueError,"same page changed"):
                self.stage(ledger,1,[dict(ROW,bidNtceNo="OTHER")])
            self.assertEqual(ledger.current(),[])

    def test_query_contract_reuse_rejected(self):
        with BidLedger(self.db) as ledger:
            self.stage(ledger,1,[dict(ROW,bidNtceNo="N1")])
            with self.assertRaisesRegex(ValueError,"different query"):
                stage_snapshot(ledger,self.batch,"goods",NOW,UNTIL+timedelta(hours=1),
                               response(2,[dict(ROW,bidNtceNo="N2")]),NOW)

    def test_duplicate_across_pages_never_promoted(self):
        with BidLedger(self.db) as ledger:
            self.stage(ledger,1,[dict(ROW)])
            with self.assertRaisesRegex(ValueError,"duplicate notice"):
                self.stage(ledger,2,[dict(ROW)])
            self.assertEqual(ledger.current(),[])
            self.assertFalse(batch_status(ledger,self.batch)["completed"])

    def test_bad_page_or_incomplete_rejected(self):
        with BidLedger(self.db) as ledger:
            for page,rows in [(3,[dict(ROW)]),(1,[])]:
                with self.subTest(page=page),self.assertRaises(ValueError):
                    self.stage(ledger,page,rows)
            with self.assertRaises(ValueError):
                self.stage(ledger,1,[dict(ROW)],total=2,size=0)
            with self.assertRaises(ValueError):
                self.stage(ledger,1,[dict(ROW)],total=1000001,size=1)

    def test_bounded_7_day_period_and_uuid(self):
        with BidLedger(self.db) as ledger:
            with self.assertRaises(ValueError):
                stage_snapshot(ledger,self.batch,"goods",NOW,NOW+timedelta(days=8),
                               response(1,[dict(ROW)],1,1),NOW)
            with self.assertRaisesRegex(ValueError,"UUID"):
                stage_snapshot(ledger,"not-id","goods",NOW,UNTIL,response(1,[dict(ROW)],1,1),NOW)

    def test_zero_notice_page_is_complete(self):
        with BidLedger(self.db) as ledger:
            result=self.stage(ledger,1,[],total=0,size=100)
            self.assertTrue(result["promoted"])
            self.assertEqual(ledger.current(),[])

    def test_staged_tamper_rejected(self):
        with BidLedger(self.db) as ledger:
            self.stage(ledger,1,[dict(ROW,bidNtceNo="N1")])
            with ledger.conn: ledger.conn.execute("UPDATE snapshot_pages SET payload='[]' WHERE batch_id=?",(self.batch,))
            with self.assertRaisesRegex(ValueError,"tampered"):
                self.stage(ledger,2,[dict(ROW,bidNtceNo="N2")])
            self.assertEqual(ledger.current(),[])

    def test_reminder_dedupe_and_restart(self):
        from bidax.core import validate_notice
        notice={"notice_no":"N1","revision":"0","title":"A","category":"goods",
           "issuer":"Issuer","deadline":(NOW+timedelta(hours=12)).isoformat(),
           "source_url":"https://www.g2b.go.kr/x","regions":[],"license_codes":[],"required_documents":[]}
        with BidLedger(self.db) as ledger:
            ledger.ingest([notice])
            self.assertEqual(poll_due(ledger,now=NOW)["new_count"],1)
            self.assertEqual(poll_due(ledger,now=NOW)["new_count"],0)
        with BidLedger(self.db) as ledger:
            self.assertEqual(poll_due(ledger,now=NOW)["new_count"],0)
            self.assertEqual(poll_due(ledger,now=NOW+timedelta(days=1))["new_count"],1)
            ledger.ingest([dict(notice,revision="1",title="amended")])
            self.assertEqual(poll_due(ledger,now=NOW+timedelta(days=1))["new_count"],1)

    def test_reminder_bad_params(self):
        with BidLedger(self.db) as ledger:
            with self.assertRaises(ValueError):poll_due(ledger,now=NOW,within_hours=0)
            with self.assertRaises(ValueError):poll_due(ledger,now=NOW.replace(tzinfo=None))

    def test_transport_explicit_permission(self):
        with BidLedger(self.db) as ledger:
            mock=MockOpener([])
            with self.assertRaises(PermissionError):
                fetch_one_page(ledger,category="goods",start=NOW,end=UNTIL,page=1,
                               service_key="SECRET",opener=mock)
            self.assertEqual(mock.calls,[])

    def test_transport_success_redacted_and_bounded(self):
        with BidLedger(self.db) as ledger:
            content=json.dumps(response(1,[ROW],1,1)).encode()
            opener=MockOpener([content])
            data=fetch_one_page(ledger,category="goods",start=NOW,end=UNTIL,page=1,
                                service_key="SECRET",permission=True,opener=opener,now=NOW,daily_limit=1)
            self.assertEqual(data["response"]["body"]["totalCount"],1)
            self.assertIn("SECRET",opener.calls[0][0])
            self.assertEqual(ledger.conn.execute("SELECT count FROM api_attempts").fetchone()[0],1)
            with self.assertRaisesRegex(ValueError,"budget exhausted"):
                fetch_one_page(ledger,category="goods",start=NOW,end=UNTIL,page=1,
                              service_key="SECRET",permission=True,opener=opener,now=NOW,daily_limit=1)
            self.assertEqual(len(opener.calls),1)

    def test_transport_retry_and_request_no_data_leak(self):
        with BidLedger(self.db) as ledger:
            err=HTTPError("url-with-SECRET",503,"retry",{},io.BytesIO())
            opener=MockOpener([err,json.dumps(response(1,[ROW],1,1)).encode()])
            pauses=[]
            fetch_one_page(ledger,category="goods",start=NOW,end=UNTIL,page=1,
                         service_key="SECRET",permission=True,opener=opener,sleep=pauses.append,now=NOW)
            self.assertEqual(len(opener.calls),2)
            self.assertEqual(pauses,[1])
            self.assertEqual(ledger.conn.execute("SELECT count FROM api_attempts").fetchone()[0],2)

    def test_transport_unauthorized_never_retried(self):
        with BidLedger(self.db) as ledger:
            opener=MockOpener([HTTPError("secret",401,"unauthorized",{},io.BytesIO())])
            with self.assertRaisesRegex(ValueError,"key redacted") as ctx:
                fetch_one_page(ledger,category="goods",start=NOW,end=UNTIL,page=1,
                          service_key="SECRET",permission=True,opener=opener,now=NOW)
            self.assertNotIn("SECRET",str(ctx.exception))
            self.assertEqual(len(opener.calls),1)

    def test_transport_network_fail_and_json_guard(self):
        with BidLedger(self.db) as ledger:
            op=MockOpener([URLError("failed"),URLError("failed"),URLError("failed")])
            with self.assertRaisesRegex(ValueError,"key redacted"):
                fetch_one_page(ledger,category="goods",start=NOW,end=UNTIL,page=1,
                         service_key="SECRET",permission=True,opener=op,sleep=lambda _:None,now=NOW)
        with BidLedger(self.db) as ledger:
            op=MockOpener([b'{"a":1,"a":2}'])
            with self.assertRaisesRegex(ValueError,"duplicate"):
                fetch_one_page(ledger,category="goods",start=NOW,end=UNTIL,page=1,
                         service_key="SECRET",permission=True,opener=op,now=NOW)

    def test_transport_daily_quota_rejects_invalid(self):
        with BidLedger(self.db) as ledger:
            with self.assertRaises(ValueError):
                fetch_one_page(ledger,category="goods",start=NOW,end=UNTIL,page=1,
                           service_key="SECRET",permission=True,opener=MockOpener([]),now=NOW,daily_limit=1001)

    def test_package_entrypoint_local_data_dir(self):
        import os
        from unittest.mock import patch
        with patch.dict(os.environ,{"LOCALAPPDATA":self.tmp.name}):
            self.assertEqual(default_db_path(),Path(self.tmp.name)/"BidAX"/"bidax.db")
        self.assertFalse((Path(self.tmp.name)/"BidAX"/"bidax.db").exists())

if __name__=="__main__":unittest.main()

# Additional CLI and ZIP regressions intentionally use a separate class so
# stage tests remain independent of GUI and filesystem packaging.
class TestP85EndToEnd(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.db=Path(self.tmp.name)/"db.sqlite"

    def test_cli_stage_recover_and_reminder(self):
        from bidax.cli import main
        from contextlib import redirect_stdout
        from io import StringIO
        batch=uuid4().hex
        def run(*argv):
            buf=StringIO()
            with redirect_stdout(buf): main(["--db",str(self.db),*argv])
            return json.loads(buf.getvalue())
        for i in (2,1):
            p=Path(self.tmp.name)/f"page{i}.json"
            p.write_text(json.dumps(response(i,[dict(ROW,bidNtceNo=f"N{i}")]),ensure_ascii=False),encoding="utf-8")
            result=run("stage-page",str(p),"--batch-id",batch,"--category","goods",
                       "--start",NOW.isoformat(),"--end",UNTIL.isoformat(),"--obtained-at",NOW.isoformat())
            self.assertEqual(result["promoted"],i==1)
        self.assertTrue(run("stage-status",batch)["completed"])
        # Two observed future deadline records, within 5 days.
        self.assertEqual(run("poll-alerts","--hours","120")["new_count"],2)
        self.assertEqual(run("poll-alerts","--hours","120")["new_count"],0)

    def test_source_bundle_whitelist_and_existing(self):
        import zipfile
        from importlib.util import module_from_spec, spec_from_file_location
        script=Path(__file__).resolve().parents[1]/"packaging"/"build_source_zip.py"
        spec=spec_from_file_location("bid_ax_source_packager",script)
        module=module_from_spec(spec)
        spec.loader.exec_module(module)
        build=module.build
        target=Path(self.tmp.name)/"p85.zip"
        report=build(target)
        self.assertGreaterEqual(report["files"],10)
        with zipfile.ZipFile(target) as z:
            names=z.namelist()
            self.assertIn("BID_AX/MANIFEST.json",names)
            self.assertFalse(any(".db" in name or "__pycache__" in name for name in names))
            manifest=json.loads(z.read("BID_AX/MANIFEST.json"))
            for path,meta in manifest["files"].items():
                self.assertEqual(hashlib.sha256(z.read("BID_AX/"+path)).hexdigest(),meta["sha256"])
        with self.assertRaises(FileExistsError):build(target)
