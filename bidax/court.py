"""Consent-gated LOCAL court-auction document fingerprint/checklist.

Never downloads, scrapes, extracts PDF content or issues legal conclusions.
Only hashes metadata are written; local text mentions are NOT legal analysis.
"""
from __future__ import annotations

from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import sqlite3

from .core import KST, _canonical

MAX_DOCUMENT_BYTES = 5 * 1024 * 1024
ALLOWED_SUFFIXES = frozenset({".txt", ".pdf"})
CASE_RE = re.compile(r"^[0-9A-Za-z가-힣-]{2,80}$")
MENTION_WORDS = {
    "점유": ("점유", "점유자"),
    "임대차": ("임차", "임대차", "전세", "보증금"),
    "권리": ("근저당", "유치권", "가압류", "말소기준"),
    "배당": ("배당", "배당요구"),
    "명도": ("명도", "인도명령"),
    "세금": ("체납", "관리비", "조세"),
}
REVIEW_ITEMS = ("문서 진정성", "사건번호·매각기일", "등기부/말소기준권리", "임차/점유/보증금",
                "배당/인수권리", "유치권·법정지상권", "관리비·세금·명도", "현황조사서·감정서 최신 버전")
DISCLAIMER = "업로드 문서의 단어 언급은 법적 권리분석이 아니며 사건 원본·등기사항·공고 변경 여부를 전문가가 직접 확인해야 합니다."


def inspect_document(file: str | Path, *, case_id: str, user_consent: bool, source_note: str) -> dict:
    if user_consent is not True:
        raise PermissionError("explicit owner consent required; no automatic court scraping")
    if not isinstance(case_id,str) or not CASE_RE.fullmatch(case_id):
        raise ValueError("invalid court case identifier")
    if not isinstance(source_note,str) or not 4 <= len(source_note.strip()) <= 240:
        raise ValueError("source_note must describe legal possession/permission")
    path=Path(file)
    if path.is_symlink() or not path.is_file() or path.suffix.lower() not in ALLOWED_SUFFIXES:
        raise ValueError("only regular local .txt/.pdf files allowed; no symlinks")
    size=path.stat().st_size
    if not 1 <= size <= MAX_DOCUMENT_BYTES:
        raise ValueError("document exceeds 5 MiB / is empty")
    with path.open("rb") as f:
        data=f.read(MAX_DOCUMENT_BYTES+1)
    if len(data)!=size or len(data)>MAX_DOCUMENT_BYTES:
        raise ValueError("document changed size or exceeded 5 MiB")
    sha=hashlib.sha256(data).hexdigest()
    mentions=[]
    extraction="CONTENT_NOT_EXTRACTED"
    if path.suffix.lower()==".txt":
        if b"\x00" in data:
            raise ValueError("binary data in .txt")
        content=data.decode("utf-8", errors="strict")
        mentions=sorted(k for k,words in MENTION_WORDS.items() if any(word in content for word in words))
        extraction="KEYWORD_MENTIONS_ONLY_NOT_LEGAL_FINDINGS"
    else:
        if not data.startswith(b"%PDF-"):
            raise ValueError("invalid PDF signature")
        extraction="PDF_NOT_PARSED_MALWARE_SCAN_REQUIRED"
    return {"case_id":case_id,"file_name":path.name,"size_bytes":size,"sha256":sha,
            "source_note":source_note.strip(),"file_type":path.suffix.lower(),"extraction":extraction,
            "keyword_mentions":mentions,"review_status":"추가 확인 필요",
            "required_human_checks":list(REVIEW_ITEMS),"disclaimer":DISCLAIMER}


class CourtStore:
    def __init__(self, db: str | Path):
        self.conn=sqlite3.connect(Path(db))
        self.conn.execute("PRAGMA busy_timeout=5000")
        self.conn.execute("PRAGMA synchronous=FULL")
        self.conn.execute("""CREATE TABLE IF NOT EXISTS court_document_events
            (id INTEGER PRIMARY KEY, case_id TEXT NOT NULL, sha256 TEXT NOT NULL,
             fingerprint TEXT NOT NULL, payload TEXT NOT NULL, imported_at TEXT NOT NULL,
             UNIQUE(case_id,sha256))""")
        self.conn.execute("CREATE INDEX IF NOT EXISTS court_case_lookup ON court_document_events(case_id,id DESC)")
        self.conn.commit()

    def __enter__(self):return self
    def __exit__(self,*_):self.conn.close()

    def _verify(self):
        if self.conn.execute("PRAGMA quick_check").fetchone()[0] != "ok":
            raise ValueError("court DB failed SQLite integrity")
        for case,sha,fp,payload in self.conn.execute("SELECT case_id,sha256,fingerprint,payload FROM court_document_events"):
            if hashlib.sha256(payload.encode("utf-8")).hexdigest()!=fp:
                raise ValueError("court event fingerprint mismatch")
            doc=json.loads(payload)
            if case!=doc["case_id"] or sha!=doc["sha256"] or doc["review_status"]!="추가 확인 필요":
                raise ValueError("court event metadata mismatch")

    def import_document(self, filename: str | Path, *, case_id: str, user_consent: bool, source_note: str) -> dict:
        record=inspect_document(filename,case_id=case_id,user_consent=user_consent,source_note=source_note)
        self._verify()
        payload=_canonical(record)
        fp=hashlib.sha256(payload.encode("utf-8")).hexdigest()
        with self.conn:
            inserted=self.conn.execute("INSERT OR IGNORE INTO court_document_events(case_id,sha256,fingerprint,payload,imported_at) VALUES(?,?,?,?,?)",
                                       (record["case_id"],record["sha256"],fp,payload,datetime.now(KST).isoformat())).rowcount
        return {"added": bool(inserted),"case_id":record["case_id"],"sha256":record["sha256"],
                "review_status":record["review_status"],"local_only":True,"original_bytes_stored":False}

    def case_report(self, case_id: str) -> dict:
        if not isinstance(case_id,str) or not CASE_RE.fullmatch(case_id):
            raise ValueError("invalid case ID")
        self._verify()
        rows=self.conn.execute("SELECT payload,imported_at FROM court_document_events WHERE case_id=? ORDER BY id",(case_id,)).fetchall()
        events=[]
        for payload,when in rows:
            r=json.loads(payload)
            r["imported_at"]=when
            events.append(r)
        return {"source":"COURT_CONSENTED_LOCAL","case_id":case_id,"document_versions":events,
                "review_status":"추가 확인 필요","required_human_checks":list(REVIEW_ITEMS),
                "legal_qualification_approved":False,"disclaimer":DISCLAIMER,
                "network_calls":0}
