"""Offline tests: optional Korean PDF and consented court PDF mention preview."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

from bidax.pdf_report import build_pdf_bytes
from bidax.court import preview_document
from bidax.workflow import write_new_report

ROOT = Path(__file__).resolve().parents[1]


def synthetic_report():
    return {
        "scope": "OFFLINE_PRELIMINARY_ONLY", "generated_at": "2026-11-14T05:00:00+09:00",
        "company": "합성 안전 업체", "count": 1,
        "source_freshness": "실시간 공고가 아니므로 원문 직접 대조",
        "disclaimer": "모의 데이터이며 입찰 법률자격 보장 없음",
        "results": [{"notice_no": "TEST-1", "title": "<script>위조 공고</script>",
            "status": "추가 확인 필요", "deadline": "2026-12-12T17:00:00+09:00",
            "source_url": "https://www.g2b.go.kr/", "source_fingerprint": "0" * 64,
            "deterministic_mismatch": [], "needs_review": ["법률 및 서류 확인 필요"]}]
    }


@unittest.skipUnless(importlib.util.find_spec("reportlab") and importlib.util.find_spec("pypdf"),
                     "Optional PDF dependencies absent: reportlab+pypdf")
class TestPdfReport(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "report.pdf"

    def test_create_pdf_and_read_pages(self):
        write_new_report(self.path, synthetic_report(), "pdf")
        self.assertTrue(self.path.read_bytes().startswith(b"%PDF-"))
        from pypdf import PdfReader
        self.assertEqual(len(PdfReader(str(self.path)).pages), 1)
        self.assertLess(self.path.stat().st_size, 100_000)

    def test_no_overwrite_of_customer_file(self):
        self.path.write_bytes(b"keep-customer-data")
        with self.assertRaises(FileExistsError):
            write_new_report(self.path, synthetic_report(), "pdf")
        self.assertEqual(self.path.read_bytes(), b"keep-customer-data")

    def test_report_scope_must_be_offline(self):
        r = synthetic_report(); r["scope"] = "LEGAL_APPROVED"
        with self.assertRaises(ValueError): build_pdf_bytes(r)

    def test_count_mismatch_rejected(self):
        r = synthetic_report(); r["count"] = 40
        with self.assertRaises(ValueError): build_pdf_bytes(r)

    def test_bound_rows_rejected(self):
        r = synthetic_report(); r["results"] *= 1201; r["count"] = len(r["results"])
        with self.assertRaises(ValueError): build_pdf_bytes(r)

    def test_invalid_issue_item_rejected(self):
        r = synthetic_report(); r["results"][0]["needs_review"] = [None]
        with self.assertRaises(ValueError): build_pdf_bytes(r)

    def test_cli_export_real_command(self):
        db = Path(self.temp.name) / "data.db"
        from bidax.core import BidLedger
        with BidLedger(db) as ledger:
            ledger.ingest(json.loads((ROOT / "examples" / "notices.json").read_text()))
        cmd = [sys.executable, "-m", "bidax.cli", "--db", str(db), "export",
               str(ROOT / "examples" / "profile.json"), str(self.path), "--format", "pdf"]
        result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr[-1000:])
        self.assertTrue(self.path.read_bytes().startswith(b"%PDF-"))


@unittest.skipUnless(importlib.util.find_spec("reportlab") and importlib.util.find_spec("pypdf"),
                     "Optional PDF dependencies absent: reportlab+pypdf")
class TestCourtPDFPreview(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "user_supplied.pdf"
        from reportlab.pdfgen import canvas
        c = canvas.Canvas(str(self.path))
        c.drawString(72, 760, "Synthetic file, no rights or legal conclusion")
        c.showPage(); c.save()
        self.args = {"case_id": "2026타경12345", "user_consent": True,
                     "source_note": "synthetic test with consent"}

    def test_valid_pdf_preview_without_full_document_text(self):
        record = preview_document(self.path, **self.args)
        self.assertEqual(record["pages_checked"], 1)
        self.assertEqual(record["review_status"], "추가 확인 필요")
        self.assertEqual(record["extraction"], "PDF_KEYWORD_MENTIONS_ONLY_NOT_LEGAL_FINDINGS")
        self.assertFalse(record["full_document_text_in_output"])
        self.assertNotIn("Synthetic file", json.dumps(record))
        self.assertFalse(record["malware_scan_performed"])

    def test_consent_false_rejected_before_parse(self):
        with self.assertRaises(PermissionError):
            preview_document(self.path, **{**self.args, "user_consent": False})

    def test_page_cap_bounds(self):
        with self.assertRaises(ValueError): preview_document(self.path, **self.args, max_pages=0)
        with self.assertRaises(ValueError): preview_document(self.path, **self.args, max_pages=True)

    def test_corrupt_pdf_fails_closed(self):
        self.path.write_bytes(b"%PDF-1.7\nrandom")
        with self.assertRaises(ValueError): preview_document(self.path, **self.args)

    def test_annotated_pdf_rejected(self):
        from pypdf import PdfReader, PdfWriter
        writer = PdfWriter()
        writer.append_pages_from_reader(PdfReader(str(self.path)))
        writer.add_uri(0, "https://example.com", [70, 70, 110, 110])
        out = Path(self.temp.name) / "with_link.pdf"
        with out.open("wb") as f: writer.write(f)
        with self.assertRaises(ValueError): preview_document(out, **self.args)

    def test_encrypted_pdf_rejected(self):
        from pypdf import PdfReader, PdfWriter
        writer = PdfWriter(); writer.append_pages_from_reader(PdfReader(str(self.path)))
        writer.encrypt("secret")
        out = Path(self.temp.name) / "encrypted.pdf"
        with out.open("wb") as f: writer.write(f)
        with self.assertRaises(ValueError): preview_document(out, **self.args)

    def test_cli_preview_keeps_file_local(self):
        db = Path(self.temp.name) / "data.db"
        cmd = [sys.executable, "-m", "bidax.cli", "--db", str(db),
               "court-preview", str(self.path), "--case-id", self.args["case_id"],
               "--source-note", self.args["source_note"], "--consent"]
        result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr[-1000:])
        payload = json.loads(result.stdout)
        self.assertEqual(payload["pages_checked"], 1)
        self.assertFalse(db.exists(), "preview should not open or create DB")

    def test_cli_without_consent_fails(self):
        db = Path(self.temp.name) / "data.db"
        cmd = [sys.executable, "-m", "bidax.cli", "--db", str(db),
               "court-preview", str(self.path), "--case-id", self.args["case_id"],
               "--source-note", self.args["source_note"]]
        result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=15)
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__": unittest.main()
