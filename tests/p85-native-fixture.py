"""Create only synthetic private test fixtures at caller-supplied temp folder."""
import pathlib
import sys
from reportlab.pdfgen import canvas
from docx import Document

root = pathlib.Path(sys.argv[1]).resolve()
def target(tenant, doc_id, name):
    p = root / tenant / doc_id / name
    p.parent.mkdir(parents=True, exist_ok=True)
    return p

pdf = target('orgA', 'manualPdf', 'v1.pdf')
c = canvas.Canvas(str(pdf))
c.drawString(72, 740, 'Product returns within 7 days after delivery')
c.showPage()
c.drawString(72, 740, 'Shipping starts within 2 business days')
c.showPage()
c.save()

secret = target('orgA', 'secretPdf', 'v1.pdf')
c = canvas.Canvas(str(secret))
c.drawString(72, 740, 'CONFIDENTIAL SECRET 2026 ACME reference')
c.save()

for doc_id, text in [
    ('rulesDocx','반품 신청은 14일 이내 가능합니다.'),
    ('compareDocx','반품 신청은 7일 이내 가능합니다.'),
]:
    d=Document()
    d.add_paragraph(text)
    d.add_paragraph('품질 점검 대상 부품입니다.')
    d.save(str(target('orgA', doc_id, 'v1.docx')))
