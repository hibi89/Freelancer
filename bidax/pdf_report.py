"""Optional offline printable Korean PDF for BID AX reports.

Does not copy or ship font assets. Uses ReportLab's built-in Korean CID font
mapping; viewers may substitute fonts. Not a certificate of legal eligibility.
"""
from __future__ import annotations

from html import escape
from io import BytesIO
from typing import Any

MAX_REPORT_ROWS = 1200
MAX_CELL_CHARS = 900


def build_pdf_bytes(report: dict[str, Any]) -> bytes:
    """Render an already screened report. No network, no filesystem writes."""
    if type(report) is not dict or report.get("scope") != "OFFLINE_PRELIMINARY_ONLY":
        raise ValueError("only local preliminary report allowed")
    rows = report.get("results")
    if type(rows) is not list or len(rows) > MAX_REPORT_ROWS or report.get("count") != len(rows):
        raise ValueError("invalid or excessive report rows")
    try:
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_LEFT
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.cidfonts import UnicodeCIDFont
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, KeepTogether
    except ImportError as exc:
        raise RuntimeError("PDF export needs optional ReportLab; use HTML export without it") from exc

    # CID mapping avoids bundling licensed OS font binaries in an EXE or source ZIP.
    pdfmetrics.registerFont(UnicodeCIDFont("HYSMyeongJo-Medium"))
    font = "HYSMyeongJo-Medium"
    style = ParagraphStyle("BodyK", fontName=font, fontSize=9, leading=15,
                           alignment=TA_LEFT, spaceAfter=5, wordWrap="CJK")
    head = ParagraphStyle("HeadK", parent=style, fontSize=16, leading=22, spaceAfter=10)
    sub = ParagraphStyle("SubK", parent=style, fontSize=11, leading=18, spaceBefore=9)
    small = ParagraphStyle("SmallK", parent=style, fontSize=7.5, leading=12)

    def safe(value: Any) -> str:
        value = str(value if value is not None else "").replace("\x00", "")
        return escape(value[:MAX_CELL_CHARS], quote=True)

    flow = [Paragraph("BID AX — 로컬 입찰 준비 사전검토", head),
            Paragraph("기업: " + safe(report.get("company")) + " / 작성 시각: " + safe(report.get("generated_at")), style),
            Paragraph("원문 재확인 필수 · 자동 입찰 또는 법적 자격 승인 아님", style),
            Paragraph(safe(report.get("source_freshness", "실시간 원문 확인 필요")), small),
            HRFlowable(width="100%", thickness=0.5, color=colors.grey), Spacer(1, 9)]
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("invalid report row")
        issues = list(row.get("deterministic_mismatch", [])) + list(row.get("needs_review", []))
        if not all(isinstance(x, str) for x in issues):
            raise ValueError("invalid issue text")
        item = [Paragraph(safe(row.get("notice_no")) + " — " + safe(row.get("title")), sub),
                Paragraph("잠정 판정: " + safe(row.get("status")) + " / 마감: " + safe(row.get("deadline")), style),
                Paragraph("원문: " + safe(row.get("source_url")), small),
                Paragraph("원본 SHA256: " + safe(row.get("source_fingerprint")), small)]
        for issue in issues[:24]:
            item.append(Paragraph("• " + safe(issue), small))
        item.append(Spacer(1, 5))
        # Do not force a full page's worth of long source text to stay together.
        flow.extend(item)
    flow.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    flow.append(Paragraph(safe(report.get("disclaimer", "법률 자격 보장 없음")), small))
    output = BytesIO()
    SimpleDocTemplate(output, pagesize=A4, leftMargin=42, rightMargin=42, topMargin=43,
                      bottomMargin=43, title="BID AX Preliminary Evidence Report",
                      author="BID AX local", pageCompression=1).build(flow)
    blob = output.getvalue()
    if not blob.startswith(b"%PDF-"):
        raise ValueError("invalid generated PDF")
    return blob
