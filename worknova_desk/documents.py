"""Owner-initiated, offline Korean document exports (not a tax/legal certification).

DOCX uses only the Python standard library and references an OS font; PDF is
optional and embeds a caller-selected, rights-cleared TTF via reportlab.
No customer data, font bytes, or document is transmitted anywhere.
"""
from __future__ import annotations

import hashlib
import io
import os
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape

from .core import DeskError

_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
_XML = "http://www.w3.org/XML/1998/namespace"
ET.register_namespace('w', _NS)
_NOTICE = "오프라인 사용자 수기 기록 · 세금계산서·공인 전자서명·입금 확인 증빙이 아닙니다."


def _cell_text(value) -> str:
    # XML 1.0 permitted text, with tabs/newlines normalized for document output.
    return ''.join(c if c == '\n' or c == '\t' or ord(c) >= 32 else ' ' for c in str(value))


def _money(value: int) -> str:
    return f"{value:,}원"


def _lines(desk, document_type: str, identifier: str, disclose_customer: bool):
    if document_type == "quote":
        q = desk._fetch('quotes', identifier)
        import json
        lines = ["WORKNOVA Desk | 견적 검토서", _NOTICE,
                 "문서 형태: 견적 검토 초안 (발송·승인·계약 체결 자동 수행 없음)",
                 f"견적 ID: {q['id']}", f"견적 버전: {q['revision']}",
                 f"승인 상태: {q['status']}"]
        if disclose_customer:
            lines.append(f"고객명: {desk._fetch('customers', q['customer_id'])['name']}")
        else:
            lines.append("고객명: [비공개]")
        items = json.loads(q['items_json'])
        for i, entry in enumerate(items, start=1):
            lines.append(f"품목 {i}: {entry['description']} | 수량 {entry['quantity']} | 단가 {_money(entry['unit_krw'])} | 금액 {_money(entry['line_total_krw'])}")
        lines.extend([f"공급가액: {_money(q['subtotal_krw'])}",
                      f"기록된 부가세: {_money(q['vat_krw'])}",
                      f"합계: {_money(q['total_krw'])}",
                      "세율·면세 여부는 사용자 입력 기준이며 세무 적법성은 별도 확인해야 합니다."])
    elif document_type == "contract":
        c = desk._fetch('contracts', identifier)
        rep = desk.report(identifier, include_customer=disclose_customer)
        lines = ["WORKNOVA Desk | 작업·납품·수금 현황서", _NOTICE,
                 "문서 형태: 소유자 내부 기록 (계약서·세금계산서·은행 확인서 아님)",
                 f"계약 ID: {c['id']}", f"연결 견적 ID: {c['quote_id']}",
                 f"계약 상태: {c['status']}", f"고객명: {rep['customer']}",
                 f"작업 범위: {c['scope']}",
                 f"견적 합계: {_money(rep['total_krw'])}",
                 f"수기 수금 기록: {_money(rep['paid_krw'])}",
                 f"미수 잔액: {_money(rep['outstanding_krw'])}"]
        for i, item in enumerate(rep['milestones'], start=1):
            lines.append(f"단계 {i}: {item['title']} | {item['status']} | 합계 {_money(item['amount_krw'])} | 수금 {_money(item['paid_krw'])} | 잔액 {_money(item['outstanding_krw'])}")
        lines.append("결제 데이터는 사용자가 직접 기입했으며 실제 은행·PayPal 입금과 검증되지 않았습니다.")
    else:
        raise DeskError("unsupported document type")
    lines.append("문서 생성 방식: 인터넷 없는 로컬 출력. 제3자 진본성/공식 인증 없음.")
    return [_cell_text(x) for x in lines]


def _word_document(paragraphs: list[str]) -> bytes:
    document = ET.Element(f"{{{_NS}}}document")
    body = ET.SubElement(document, f"{{{_NS}}}body")
    for index, line in enumerate(paragraphs):
        p = ET.SubElement(body, f"{{{_NS}}}p")
        ppr = ET.SubElement(p, f"{{{_NS}}}pPr")
        if index == 0:
            ET.SubElement(ppr, f"{{{_NS}}}pStyle", {f"{{{_NS}}}val": "Title"})
        for part_index, segment in enumerate(line.split('\n')):
            r = ET.SubElement(p, f"{{{_NS}}}r")
            rpr = ET.SubElement(r, f"{{{_NS}}}rPr")
            ET.SubElement(rpr, f"{{{_NS}}}rFonts", {f"{{{_NS}}}ascii": "Malgun Gothic", f"{{{_NS}}}eastAsia": "맑은 고딕", f"{{{_NS}}}hAnsi": "Malgun Gothic"})
            t = ET.SubElement(r, f"{{{_NS}}}t", {f"{{{_XML}}}space":"preserve"})
            t.text = segment
            if part_index < len(line.split('\n')) - 1:
                ET.SubElement(r, f"{{{_NS}}}br")
    sect = ET.SubElement(body, f"{{{_NS}}}sectPr")
    ET.SubElement(sect, f"{{{_NS}}}pgSz", {f"{{{_NS}}}w":"11906", f"{{{_NS}}}h":"16838"})  # A4
    xml = ET.tostring(document, encoding="utf-8", xml_declaration=True)
    content_types = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                     '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                     '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                     '<Default Extension="xml" ContentType="application/xml"/>'
                     '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
                     '</Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
            '</Relationships>')
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        # Fixed timestamps prevent unstable archive differences with identical inputs.
        for name, payload in [('[Content_Types].xml',content_types.encode('utf-8')),
                              ('_rels/.rels',rels.encode('utf-8')),
                              ('word/document.xml',xml)]:
            info = zipfile.ZipInfo(name, date_time=(2020,1,1,0,0,0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, payload)
    return out.getvalue()


def _pdf_document(paragraphs: list[str], font_path: str | Path) -> bytes:
    # No implicit Windows/system font redistribution; font path is explicit.
    font = Path(font_path)
    if font.is_symlink() or not font.is_file() or font.suffix.lower() != '.ttf' or font.stat().st_size > 25*1024*1024:
        raise DeskError("PDF requires a locally installed, rights-cleared .ttf font <=25 MiB")
    try:
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_LEFT
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether
    except ImportError as exc:
        raise DeskError("PDF requires optional reportlab; DOCX works with Python stdlib") from exc
    try:
        # Register the user's supplied font only in-memory; never store it in source/output ZIP.
        font_name = 'WorknovaOwnerFont' + hashlib.sha256(str(font.resolve()).encode()).hexdigest()[:10]
        if font_name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(font_name, str(font)))
        title_style = ParagraphStyle('WorknovaTitle', fontName=font_name, fontSize=15, leading=22, spaceAfter=14, wordWrap='CJK')
        body_style = ParagraphStyle('WorknovaBody', fontName=font_name, fontSize=9.5, leading=17, spaceAfter=7, wordWrap='CJK')
        out = io.BytesIO()
        document = SimpleDocTemplate(out, pagesize=A4, rightMargin=43, leftMargin=43, topMargin=45, bottomMargin=45,
                                     title='WORKNOVA Desk - offline owner record', author='WORKNOVA Desk')
        story=[]
        for i,line in enumerate(paragraphs):
            style = title_style if i==0 else body_style
            story.append(Paragraph(escape(line).replace('\n','<br/>'), style))
        document.build(story)
        payload=out.getvalue()
        if not payload.startswith(b'%PDF-'):
            raise DeskError('PDF encoding failed')
        return payload
    except DeskError:
        raise
    except Exception as exc:
        raise DeskError(f"PDF generation failed: {type(exc).__name__}") from exc


def _write_new(destination: str | Path, content: bytes, *, expected_suffix: str) -> dict:
    path = Path(destination)
    if path.suffix.lower() != expected_suffix or not path.parent.is_dir() or path.parent.is_symlink() or path.exists() or path.is_symlink():
        raise DeskError("document output must be a NEW local file of correct type in an existing folder")
    if len(content) > 10 * 1024 * 1024:
        raise DeskError('document exceeds 10 MiB output limit')
    if os.name == 'nt' and str(path).startswith(('\\\\','//')):
        raise DeskError('network share output not supported for owner-private documents')
    descriptor = None
    created = False
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os,'O_BINARY',0), 0o600)
        created = True
        with os.fdopen(descriptor,'wb') as stream:
            descriptor = None
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
    except Exception:
        if descriptor is not None:
            os.close(descriptor)
        if path.exists():
            path.unlink()
        raise
    return {'sha256':hashlib.sha256(content).hexdigest(), 'bytes':len(content), 'document_type':expected_suffix[1:], 'privacy':'redacted-by-default'}


def export_document(desk, document_type: str, identifier: str, destination: str | Path,
                    *, format: str='docx', pdf_font: str | Path | None=None,
                    include_customer: bool=False, confirm_disclosure: bool=False) -> dict:
    if type(include_customer) is not bool or type(confirm_disclosure) is not bool:
        raise DeskError('disclosure settings must be booleans')
    if include_customer and not confirm_disclosure:
        raise DeskError('including customer name requires explicit privacy confirmation')
    # Refuse to certify a tampered audit and check DB integrity before reporting.
    desk.verify_audit()
    paragraphs = _lines(desk, document_type, identifier, include_customer)
    if format == 'docx':
        output = _word_document(paragraphs)
    elif format == 'pdf':
        if not pdf_font:
            raise DeskError('PDF requires --pdf-font path to a licensed Korean TrueType font')
        output = _pdf_document(paragraphs, pdf_font)
    else:
        raise DeskError('unsupported document format')
    return _write_new(destination, output, expected_suffix='.'+format)
