"""Offline official-metadata Onbid plans. No live API credentials or network."""
import unittest
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from bidax.onbid_plan import build_plan


class OnbidRequestPlanTests(unittest.TestCase):
    def test_announcement_assets(self):
        x = build_plan('announcement_assets',{'pbancMngNo':'202406-21411-00'})
        self.assertEqual(x['dataset_id'], 15157220)
        self.assertEqual(x['parameters']['pbancMngNo'],'202406-21411-00')
        self.assertFalse(x['network_ready'])
        self.assertIsNone(x['operation_path'])
        self.assertNotIn('serviceKey',x['parameters'])

    def test_result_detail(self):
        x=build_plan('result_detail',{'cltrMngNo':'2024-1100-084555','pbctCdtnNo':'3621804'},page=2,rows=20)
        self.assertEqual(x['dataset_id'],15157254)
        self.assertEqual(x['parameters']['pageNo'],'2')
        self.assertEqual(x['parameters']['numOfRows'],'20')

    def test_result_list(self):
        x=build_plan('result_list',{'cltrTypeCd':'0001','prptDivCd':'0007,0005','opbdDtStart':'20241119','opbdDtEnd':'20241120','pbctStatCd':'0011'})
        self.assertEqual(x['dataset_id'],15157252)
        self.assertEqual(x['parameters']['pbctStatCd'],'0011')

    def test_reject_invalid_inputs(self):
        cases=[
          ('unsupported',{},1,10),
          ('result_detail',{'cltrMngNo':'ABC','serviceKey':'SECRET'},1,10),
          ('result_detail',{'cltrMngNo':'http://evil'},1,10),
          ('announcement_assets',{},1,10),
          ('announcement_assets',{'pbancMngNo':'A'},True,10),
          ('announcement_assets',{'pbancMngNo':'A'},1,101),
          ('result_list',{'cltrTypeCd':'0001','prptDivCd':'0007','opbdDtStart':'20240230','opbdDtEnd':'20240301'},1,10),
          ('result_list',{'cltrTypeCd':'0001','prptDivCd':'0007','opbdDtStart':'20241231','opbdDtEnd':'20240101'},1,10),
          ('result_list',{'cltrTypeCd':'0008','prptDivCd':'0007','opbdDtStart':'20241119','opbdDtEnd':'20241120'},1,10),
          ('result_list',{'cltrTypeCd':'0001','prptDivCd':'0007,0007','opbdDtStart':'20241119','opbdDtEnd':'20241120'},1,10),
        ]
        for kind,params,page,rows in cases:
            with self.subTest(kind=kind,params=params):
                with self.assertRaises(ValueError):build_plan(kind,params,page=page,rows=rows)

    def test_real_cli_offline_plan(self):
        with tempfile.TemporaryDirectory() as t:
            source=Path(t)/"params.json"
            source.write_text(json.dumps({"pbancMngNo":"202406-21411-00"}),encoding="utf-8")
            db=Path(t)/"unused.db"
            r=subprocess.run([sys.executable,"-m","bidax.cli","--db",str(db),"onbid-plan","announcement_assets",str(source)],capture_output=True,text=True,timeout=10,check=True)
            x=json.loads(r.stdout)
            self.assertEqual(x["dataset_id"],15157220)
            self.assertFalse(x["network_ready"])
            self.assertFalse(db.exists(),"planning must not open a DB or send a request")

    def test_never_build_executable_uri_or_allow_secrets(self):
        for k,p in [
          ('announcement_assets',{'pbancMngNo':'A'}),
          ('result_detail',{'cltrMngNo':'B'}),
          ('result_list',{'cltrTypeCd':'0001','prptDivCd':'0007','opbdDtStart':'20241119','opbdDtEnd':'20241120'})
        ]:
            o=build_plan(k,p)
            self.assertFalse(o['network_ready'])
            self.assertNotIn('serviceKey',str(o['parameters']))
            self.assertEqual(o['service_key'],'CUSTOMER_APPLICATION_REQUIRED_NOT_COLLECTED')

if __name__=='__main__':unittest.main()
