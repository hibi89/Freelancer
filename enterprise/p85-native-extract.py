"""CITEVAULT P85 experimental isolated native extractor; only stdin bytes, no file paths.
Dependencies pinned in tests/requirements-p85-native.txt; not a customer-ready parser.
This is NOT the pinned original RAG Studio native parser.
"""
import io
import json
import sys

MAX_SOURCE = 2 * 1024 * 1024
MAX_UNITS = 64
MAX_QUOTE = 4096


def emit(status, unit=None, rows=None):
    payload = {"status": status, "unit": unit, "rows": rows or []}
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))


def normalize(value):
    if not isinstance(value, str):
        raise ValueError("unsupported text")
    return " ".join(value.replace("\u0000", "").split())


def extract_pdf(data):
    from pypdf import PdfReader
    reader = PdfReader(io.BytesIO(data), strict=True)
    if reader.is_encrypted or len(reader.pages) > MAX_UNITS:
        raise ValueError("unsupported PDF")
    rows = []
    for position, page in enumerate(reader.pages, 1):
        text = normalize(page.extract_text() or "")
        if text:
            if len(text) > MAX_QUOTE:
                raise ValueError("oversized text")
            rows.append({"position": position, "quote": text})
    return rows


def extract_docx(data):
    from zipfile import ZipFile
    # Fail before library decompression for unreasonable zip contents or zip bombs.
    with ZipFile(io.BytesIO(data)) as archive:
        items = archive.infolist()
        if not 1 <= len(items) <= 512 or any(
            info.file_size > 1024 * 1024 or info.compress_size > 1024 * 1024
            or (info.compress_size == 0 and info.file_size > 0)
            or (info.compress_size > 0 and info.file_size / info.compress_size > 150)
            for info in items
        ):
            raise ValueError("unsafe ZIP")
        if sum(info.file_size for info in items) > 4 * 1024 * 1024:
            raise ValueError("zip expanded too large")
        if any(info.filename.lower().endswith((".bin", ".vbaproject")) for info in items):
            raise ValueError("unsupported embedded binary")
    from docx import Document
    document = Document(io.BytesIO(data))
    if len(document.paragraphs) > MAX_UNITS:
        raise ValueError("too many paragraphs")
    rows = []
    for position, paragraph in enumerate(document.paragraphs, 1):
        text = normalize(paragraph.text)
        if text:
            if len(text) > MAX_QUOTE:
                raise ValueError("oversized text")
            rows.append({"position": position, "quote": text})
    return rows


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("pdf", "docx"):
        emit("UNSUPPORTED")
        return
    data = sys.stdin.buffer.read(MAX_SOURCE + 1)
    if not data or len(data) > MAX_SOURCE:
        emit("UNSUPPORTED")
        return
    kind = sys.argv[1]
    if (kind == "pdf" and not data.startswith(b"%PDF-")) or (
        kind == "docx" and not data.startswith(b"PK\x03\x04")
    ):
        emit("UNSUPPORTED")
        return
    try:
        rows = extract_pdf(data) if kind == "pdf" else extract_docx(data)
        if not rows:
            emit("UNSUPPORTED_OR_EMPTY")
            return
        emit("OK", "page" if kind == "pdf" else "paragraph", rows)
    except Exception:
        emit("UNSUPPORTED_OR_EMPTY")


if __name__ == "__main__":
    main()
