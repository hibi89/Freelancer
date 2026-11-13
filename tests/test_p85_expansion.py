"""Synthetic, no-network acceptance for new Onbid and consented court adapters."""
from __future__ import annotations
from datetime import datetime
from contextlib import closing
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from bidax.onbid import OnbidStore, validate_snapshot, validate_record, DATASET_URLS
from bidax.court import CourtStore, inspect_document, MAX_DOCUMENT_BYTES
from bidax.desktop import LocalController

ROOT=Path(__file__).resolve().parents[1]
URL="https://www.data.go.kr/data/15157220/openapi.do"
URL_R="https://www.data.go.kr/data/15157254/openapi.do"


def asset(prop="P-1",condition="C-1"):
    return {"property_id":prop,"condition_id":condition,"announcement_id":"A-1","title":"합성 공매물건",
            "property_type":"부동산","appraised_krw":200000000,"minimum_bid_krw":100000000,
            "failed_rounds":2,"bid_start":"2026-11-20T10:00:00+09:00","bid_end":"2026-11-25T17:00:00+09:00",
            "source_url":URL}


def result(prop="P-1",condition="C-1",status="유찰"):
    return {"property_id":prop,"condition_id":condition,"result_status":status,
            "winning_bid_krw":None if status != "낙찰" else 120000000,"source_url":URL_R}


def snapshot(records,dataset="assets",observed="2026-11-13T09:15:00+09:00"):
    return {"source":"ONBID_LOCAL_AUTHORIZED_SNAPSHOT","dataset":dataset,
            "documentation_url":DATASET_URLS[dataset],"obtained_at":observed,"records":records}


class OnbidExpansion(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.db=Path(self.tmp.name)/"ledger.db"

    def test_clean_import_and_idempotent_replay(self):
        with OnbidStore(self.db) as store:
            self.assertEqual(store.import_snapshot(snapshot([asset()]))["new_versions"],1)
            self.assertEqual(store.import_snapshot(snapshot([asset()]))["new_versions"],0)
            rep=store.report()
            self.assertEqual(len(rep["assets"]),1)
            self.assertEqual(rep["assets"][0]["review_status"],"추가 확인 필요")
            self.assertFalse(rep["legal_qualification_approved"])

    def test_older_changed_snapshot_cannot_replace_latest(self):
        with OnbidStore(self.db) as st:
            st.import_snapshot(snapshot([asset()], observed="2026-11-13T10:15:00+09:00"))
            changed = asset(); changed["minimum_bid_krw"] = 1
            with self.assertRaises(ValueError):
                st.import_snapshot(snapshot([changed], observed="2026-11-13T09:15:00+09:00"))
            self.assertEqual(st.report()["assets"][0]["minimum_bid_krw"], 100000000)

    def test_result_linked_by_property_and_condition(self):
        with OnbidStore(self.db) as st:
            st.import_snapshot(snapshot([asset()]))
            st.import_snapshot(snapshot([result()],"results"))
            self.assertEqual(st.report()["assets"][0]["result_status"],"유찰")
            self.assertFalse(st.report()["assets"][0]["result_provenance_verified"])

    def test_result_different_condition_not_crosslinked(self):
        with OnbidStore(self.db) as st:
            st.import_snapshot(snapshot([asset()]))
            st.import_snapshot(snapshot([result(condition="C-2")],"results"))
            self.assertEqual(st.report()["assets"][0]["result_status"],"미확인")
            self.assertEqual(st.report()["orphan_result_count"],1)

    def test_same_property_in_separate_conditions_allowed(self):
        with OnbidStore(self.db) as st:
            st.import_snapshot(snapshot([asset(condition="C-1"),asset(condition="C-2")]))
            self.assertEqual(len(st.report()["assets"]),2)

    def test_inconsistent_duplicate_within_one_snapshot_atomic(self):
        row=asset();other=asset();other["minimum_bid_krw"]=100
        with OnbidStore(self.db) as st:
            with self.assertRaises(ValueError):st.import_snapshot(snapshot([row,other]))
            self.assertEqual(st.report()["assets"],[])

    def test_invalid_second_row_atomic(self):
        bad=asset("P-2");bad["source_url"]="https://evil.onbid.co.kr.attacker.com/"
        with OnbidStore(self.db) as st:
            with self.assertRaises(ValueError):st.import_snapshot(snapshot([asset(),bad]))
            self.assertEqual(st.report()["assets"],[])

    def test_missing_fields_quarantine(self):
        bad=asset();del bad["announcement_id"]
        with self.assertRaises(ValueError):validate_snapshot(snapshot([bad]))

    def test_wrong_dataset_or_doc_url(self):
        bad=snapshot([asset()]);bad["documentation_url"]=URL_R
        with self.assertRaises(ValueError):validate_snapshot(bad)

    def test_rejected_unsupported_raw_response(self):
        with self.assertRaises(ValueError):validate_snapshot({"response":{"body":{"items":[]}}})

    def test_nonofficial_http_url_rejected(self):
        bad=asset();bad["source_url"]="http://www.onbid.co.kr/"
        with self.assertRaises(ValueError):validate_record(bad,"assets")

    def test_bool_is_not_krw(self):
        bad=asset();bad["minimum_bid_krw"]=True
        with self.assertRaises(ValueError):validate_record(bad,"assets")

    def test_legal_status_unknown_code_fails_closed(self):
        bad=result();bad["result_status"]="0010"
        with self.assertRaises(ValueError):validate_record(bad,"results")

    def test_negative_price_rejected(self):
        bad=asset();bad["minimum_bid_krw"]=-1
        with self.assertRaises(ValueError):validate_record(bad,"assets")

    def test_non_awarded_winning_bid_conflict(self):
        bad=result();bad["winning_bid_krw"]=999
        with self.assertRaises(ValueError):validate_record(bad,"results")

    def test_invalid_deadline_rejected(self):
        bad=asset();bad["bid_start"]="2026-11-30T00:00:00+09:00"
        with self.assertRaises(ValueError):validate_record(bad,"assets")

    def test_db_payload_tamper_fails_closed(self):
        with OnbidStore(self.db) as st:st.import_snapshot(snapshot([asset()]))
        with closing(sqlite3.connect(self.db)) as conn:
            with conn:conn.execute("UPDATE onbid_events SET payload='{}'")
        with OnbidStore(self.db) as st:
            with self.assertRaises(ValueError):st.report()

    def test_cli_offline_asset_result_end_to_end(self):
        def run(*args):
            command=[sys.executable,"-m","bidax.cli","--db",str(self.db),*args]
            completed=subprocess.run(command,cwd=ROOT,check=True,capture_output=True,text=True,timeout=12)
            return json.loads(completed.stdout)
        assets=ROOT/"examples"/"onbid_assets_synthetic.json"
        results=ROOT/"examples"/"onbid_results_synthetic.json"
        self.assertEqual(run("onbid-import",str(assets))["new_versions"],1)
        self.assertEqual(run("onbid-import",str(results))["new_versions"],1)
        report=run("onbid-report")
        self.assertEqual(len(report["assets"]),1)
        self.assertEqual(report["assets"][0]["review_status"],"추가 확인 필요")

    def test_cli_offline_onbid_duplicate_replay(self):
        assets=ROOT/"examples"/"onbid_assets_synthetic.json"
        cmd=[sys.executable,"-m","bidax.cli","--db",str(self.db),"onbid-import",str(assets)]
        p1=subprocess.run(cmd,cwd=ROOT,check=True,capture_output=True,text=True,timeout=12)
        p2=subprocess.run(cmd,cwd=ROOT,check=True,capture_output=True,text=True,timeout=12)
        self.assertEqual(json.loads(p1.stdout)["new_versions"],1)
        self.assertEqual(json.loads(p2.stdout)["unchanged"],1)

    def test_g2b_same_identifier_never_collides(self):
        from bidax.core import BidLedger
        with BidLedger(self.db) as g2b:
            g2b.ingest([{"notice_no":"P-1","revision":"C-1","title":"별도 발주공고",
                "category":"goods","issuer":"기관","deadline":"2026-11-26T17:00:00+09:00",
                "source_url":"https://www.g2b.go.kr/","regions":[],"license_codes":[],"required_documents":[]}])
        with OnbidStore(self.db) as onbid:
            onbid.import_snapshot(snapshot([asset("P-1","C-1")]))
            self.assertEqual(len(onbid.report()["assets"]),1)
        with BidLedger(self.db) as g2b:self.assertEqual(len(g2b.current()),1)


class CourtExpansion(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.db=Path(self.tmp.name)/"db.sqlite"
        self.txt=Path(self.tmp.name)/"court.txt"
        self.txt.write_text("임차인 보증금, 점유, 유치권 언급. 법률 확인 필요.",encoding="utf-8")

    def test_court_document_and_onbid_can_share_db(self):
        with OnbidStore(self.db) as onbid:
            onbid.import_snapshot(snapshot([asset()]))
        with CourtStore(self.db) as court:
            court.import_document(self.txt,case_id="2026타경12345",user_consent=True,source_note="고객 제공 원본")
            self.assertEqual(len(court.case_report("2026타경12345")["document_versions"]),1)
        with OnbidStore(self.db) as onbid:
            self.assertEqual(len(onbid.report()["assets"]),1)

    def test_consent_required(self):
        with self.assertRaises(PermissionError):inspect_document(self.txt,case_id="2026타경12345",user_consent=False,source_note="소유자 제공 원본")

    def test_string_true_not_consent(self):
        with self.assertRaises(PermissionError):inspect_document(self.txt,case_id="2026타경12345",user_consent="True",source_note="소유자 제공 원본")

    def test_txt_mentions_are_not_legal_findings(self):
        r=inspect_document(self.txt,case_id="2026타경12345",user_consent=True,source_note="소유자 제공 원본")
        self.assertIn("권리",r["keyword_mentions"])
        self.assertIn("임대차",r["keyword_mentions"])
        self.assertEqual(r["review_status"],"추가 확인 필요")
        self.assertEqual(r["extraction"],"KEYWORD_MENTIONS_ONLY_NOT_LEGAL_FINDINGS")

    def test_receipt_contains_no_document_text_or_path(self):
        with CourtStore(self.db) as st:
            st.import_document(self.txt,case_id="2026타경12345",user_consent=True,source_note="소유자 제공 원본")
            report=st.case_report("2026타경12345")
            asjson=json.dumps(report,ensure_ascii=False)
            self.assertNotIn("보증금, 점유",asjson)
            self.assertNotIn(self.tmp.name,asjson)
            self.assertEqual(report["network_calls"],0)
            self.assertFalse(report["legal_qualification_approved"])

    def test_replay_is_idempotent(self):
        with CourtStore(self.db) as st:
            a=st.import_document(self.txt,case_id="2026타경12345",user_consent=True,source_note="소유자 제공 원본")
            b=st.import_document(self.txt,case_id="2026타경12345",user_consent=True,source_note="소유자 제공 원본")
            self.assertTrue(a["added"]);self.assertFalse(b["added"])
            self.assertEqual(len(st.case_report("2026타경12345")["document_versions"]),1)

    def test_revision_history_with_new_hash(self):
        with CourtStore(self.db) as st:
            st.import_document(self.txt,case_id="2026타경12345",user_consent=True,source_note="소유자 제공 원본")
            self.txt.write_text("변경된 점유 관계",encoding="utf-8")
            st.import_document(self.txt,case_id="2026타경12345",user_consent=True,source_note="소유자 제공 원본")
            self.assertEqual(len(st.case_report("2026타경12345")["document_versions"]),2)

    def test_pdf_header_only_not_parsed(self):
        pdf=Path(self.tmp.name)/"doc.pdf";pdf.write_bytes(b"%PDF-1.7\nnot a legal PDF acceptance")
        with CourtStore(self.db) as st:
            st.import_document(pdf,case_id="2026타경12345",user_consent=True,source_note="고객 제공 승인 문서")
            self.assertEqual(st.case_report("2026타경12345")["document_versions"][0]["extraction"],"PDF_NOT_PARSED_MALWARE_SCAN_REQUIRED")

    def test_invalid_pdf_magic(self):
        pdf=Path(self.tmp.name)/"bad.pdf";pdf.write_bytes(b"not-a-pdf")
        with self.assertRaises(ValueError):inspect_document(pdf,case_id="2026타경12345",user_consent=True,source_note="고객 제공 원본")

    def test_symlink_rejected(self):
        link=Path(self.tmp.name)/"alias.txt";link.symlink_to(self.txt)
        with self.assertRaises(ValueError):inspect_document(link,case_id="2026타경12345",user_consent=True,source_note="고객 제공 원본")

    def test_large_document_rejected(self):
        huge=Path(self.tmp.name)/"huge.txt"
        with huge.open("wb") as f:f.truncate(MAX_DOCUMENT_BYTES+1)
        with self.assertRaises(ValueError):inspect_document(huge,case_id="2026타경12345",user_consent=True,source_note="고객 제공 원본")

    def test_unsupported_extension_rejected(self):
        doc=Path(self.tmp.name)/"document.docx";doc.write_bytes(b"dummy")
        with self.assertRaises(ValueError):inspect_document(doc,case_id="2026타경12345",user_consent=True,source_note="고객 제공 원본")

    def test_bad_case_id_rejected(self):
        with self.assertRaises(ValueError):inspect_document(self.txt,case_id="../../etc/passwd",user_consent=True,source_note="고객 제공 원본")

    def test_corrupted_audit_row_detected(self):
        with CourtStore(self.db) as st:
            st.import_document(self.txt,case_id="2026타경12345",user_consent=True,source_note="소유자 제공 원본")
        with closing(sqlite3.connect(self.db)) as conn:
            with conn:conn.execute("UPDATE court_document_events SET payload='{}'")
        with CourtStore(self.db) as st:
            with self.assertRaises(ValueError):st.case_report("2026타경12345")

    def test_cli_consent_gate(self):
        cmd=[sys.executable,"-m","bidax.cli","--db",str(self.db),"court-import",str(self.txt),"--case-id","2026타경12345","--source-note","고객 제공 원본"]
        failed=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=12)
        self.assertNotEqual(failed.returncode,0)
        ok=subprocess.run(cmd+["--consent"],cwd=ROOT,capture_output=True,text=True,timeout=12,check=True)
        self.assertTrue(json.loads(ok.stdout)["added"])

    def test_gui_controller_noninteractive_local_only(self):
        ctrl=LocalController(self.db)
        self.assertTrue(ctrl.import_court(self.txt,"2026타경12345","고객 제공 원본",consent=True)["added"])
        self.assertEqual(ctrl.court_report("2026타경12345")["review_status"],"추가 확인 필요")


if __name__=="__main__":unittest.main()
