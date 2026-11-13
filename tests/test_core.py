import json
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
import unittest
from bidax.core import BidLedger, evaluate, official_query, validate_notice, validate_profile

T = timezone(timedelta(hours=9))
NOW = datetime(2026, 11, 13, 15, 0, tzinfo=T)
NOTICE = {"notice_no":"R26BK000001", "revision":"000", "title":"서버 유지보수", "category":"services", "issuer":"테스트 공공기관", "deadline":"2026-11-20T18:00:00+09:00", "source_url":"https://www.g2b.go.kr/notice/R26BK000001", "regions":["부산"], "license_codes":["S/W"], "required_documents":["사업자등록증"], "budget_min_krw":3000000}
PROFILE = {"company":"가상 테스트업체", "regions":["부산"], "license_codes":["S/W"], "documents":{"사업자등록증":"2026-12-31"}, "max_budget_krw":4000000}

class BidAxTests(unittest.TestCase):
    def test_happy_preliminary(self):
        r=evaluate(validate_notice(NOTICE), PROFILE, NOW)
        self.assertEqual(r["status"], "적합")
        self.assertIn("최종 입찰자격",r["disclaimer"])
    def test_region_mismatch(self):
        p=dict(PROFILE,regions=["서울"])
        self.assertEqual(evaluate(validate_notice(NOTICE),p,NOW)["status"],"부적합")
    def test_missing_license_needs_review(self):
        p=dict(PROFILE,license_codes=[])
        self.assertEqual(evaluate(validate_notice(NOTICE),p,NOW)["status"],"추가 확인 필요")
    def test_expired_document_needs_review(self):
        p=dict(PROFILE,documents={"사업자등록증":"2026-11-01"})
        self.assertIn("필수서류 만료",evaluate(validate_notice(NOTICE),p,NOW)["needs_review"][0])
    def test_deadline_passed(self):
        self.assertEqual(evaluate(validate_notice(NOTICE),PROFILE,NOW+timedelta(days=10))["status"],"부적합")
    def test_budget_exceeds_user_cap(self):
        self.assertEqual(evaluate(validate_notice(NOTICE),dict(PROFILE,max_budget_krw=1000),NOW)["status"],"부적합")
    def test_unknown_fields_fail_closed(self):
        with self.assertRaises(ValueError): validate_notice(dict(NOTICE,ignored=True))
    def test_not_https_or_unofficial(self):
        for u in ["http://www.g2b.go.kr/x","https://evil.example/x","https://www.g2b.go.kr.evil.com/x"]:
            with self.subTest(u=u),self.assertRaises(ValueError): validate_notice(dict(NOTICE,source_url=u))
    def test_no_naive_datetime(self):
        with self.assertRaises(ValueError): validate_notice(dict(NOTICE,deadline="2026-11-20T18:00:00"))
    def test_no_boolean_budget(self):
        with self.assertRaises(ValueError): validate_notice(dict(NOTICE,budget_min_krw=True))
    def test_profile_strict(self):
        with self.assertRaises(ValueError): validate_profile(dict(PROFILE,documents={"x":"not-date"}))
    def test_official_7day_window(self):
        self.assertIn("getBidPblancListInfoServc02",official_query("services",NOW,NOW+timedelta(days=7))["base_url"])
        with self.assertRaises(ValueError): official_query("services",NOW,NOW+timedelta(days=8))
    def test_official_no_key_in_plan(self):
        self.assertNotIn("serviceKey", json.dumps(official_query("goods",NOW,NOW+timedelta(hours=1))))
    def test_official_naive_rejected(self):
        with self.assertRaises(ValueError): official_query("goods",NOW.replace(tzinfo=None),NOW+timedelta(days=1))
    def test_duplicate_and_revision_history(self):
        with tempfile.TemporaryDirectory() as td:
            with BidLedger(Path(td)/"a.db") as db:
                self.assertEqual(db.ingest([NOTICE,NOTICE]),{"received":2,"added_versions":1,"unchanged":1})
                self.assertEqual(db.ingest([NOTICE])["added_versions"],0)
                nextv=dict(NOTICE,revision="001",deadline="2026-11-21T18:00:00+09:00")
                self.assertEqual(db.ingest([nextv])["added_versions"],1)
                self.assertEqual(len(db.current()),1)
                self.assertEqual(db.current()[0]["revision"],"001")
                self.assertEqual(len(db.events(NOTICE["notice_no"])),2)
    def test_atomic_rejection(self):
        with tempfile.TemporaryDirectory() as td:
            with BidLedger(Path(td)/"a.db") as db:
                with self.assertRaises(ValueError):db.ingest([NOTICE,dict(NOTICE,source_url="https://evil.example/x")])
                self.assertEqual(db.current(),[])
    def test_backup_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            src=Path(td)/"src.db";dest=Path(td)/"copy.db"
            with BidLedger(src) as db:
                db.ingest([NOTICE]);db.backup(dest)
                with self.assertRaises(FileExistsError):db.backup(dest)
                with self.assertRaises(ValueError):db.backup(src)
            with BidLedger(dest) as copied:self.assertEqual(len(copied.current()),1)
    def test_empty_region_needs_review(self):
        self.assertEqual(evaluate(validate_notice(dict(NOTICE,regions=[])),PROFILE,NOW)["status"],"추가 확인 필요")
    def test_empty_documents_needs_review(self):
        self.assertEqual(evaluate(validate_notice(dict(NOTICE,required_documents=[])),PROFILE,NOW)["status"],"추가 확인 필요")

if __name__=="__main__":unittest.main()
