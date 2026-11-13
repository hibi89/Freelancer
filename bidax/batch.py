"""Resumable, offline-only G2B snapshot staging and idempotent promotion.

No API calls. A batch cannot alter the current notice ledger until every expected
page has been checked and matches the declared total. The local source mapping
remains provisional; all ingested notice eligibility requires human review.
"""
from __future__ import annotations

from datetime import datetime
import hashlib
import json
import math
from uuid import UUID
from .core import BidLedger, OPERATIONS, _canonical, official_query
from .official import parse_official_snapshot

MAX_PAGES = 10_000


def _uuid(value: str) -> str:
    try:
        return UUID(value).hex
    except (TypeError, ValueError, AttributeError) as exc:
        raise ValueError("batch_id must be UUID") from exc


def _init(ledger: BidLedger):
    ledger.conn.executescript("""
        CREATE TABLE IF NOT EXISTS snapshot_batches (
            batch_id TEXT PRIMARY KEY, category TEXT NOT NULL,
            period_start TEXT NOT NULL, period_end TEXT NOT NULL,
            page_size INTEGER NOT NULL, total_count INTEGER NOT NULL,
            expected_pages INTEGER NOT NULL, completed INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS snapshot_pages (
            batch_id TEXT NOT NULL REFERENCES snapshot_batches(batch_id),
            page_no INTEGER NOT NULL, fingerprint TEXT NOT NULL,
            payload TEXT NOT NULL, PRIMARY KEY (batch_id,page_no));
    """)


def batch_status(ledger: BidLedger, batch_id: str) -> dict:
    _init(ledger)
    batch_id = _uuid(batch_id)
    row = ledger.conn.execute(
        "SELECT category,period_start,period_end,total_count,expected_pages,completed "
        "FROM snapshot_batches WHERE batch_id=?", (batch_id,)).fetchone()
    if row is None:
        raise KeyError("unknown offline snapshot batch")
    items = ledger.conn.execute("SELECT page_no FROM snapshot_pages WHERE batch_id=? ORDER BY page_no", (batch_id,)).fetchall()
    present = [r[0] for r in items]
    return {"batch_id":batch_id, "category":row[0], "period_start":row[1],
            "period_end":row[2], "total_count":row[3], "expected_pages":row[4],
            "staged_pages":present, "missing_pages":[n for n in range(1,row[4]+1) if n not in present],
            "completed":bool(row[5]), "scope":"OFFLINE_SNAPSHOTS_ONLY"}


def stage_snapshot(ledger: BidLedger, batch_id: str, category: str, start: datetime,
                   end: datetime, snapshot: dict, obtained_at: datetime) -> dict:
    """Stage exactly one local page. Replays are safe; contradictory pages fail.

    At full coverage, promotion may be retried after a crash: immutable notice
    fingerprints dedupe across retries. The batch is never marked completed
    until the ledger import has succeeded. Not suitable for live API sync yet.
    """
    batch_id = _uuid(batch_id)
    if category not in OPERATIONS:
        raise ValueError("unsupported category")
    official_query(category, start, end)  # enforces <=7 days, explicit offsets
    parsed = parse_official_snapshot(snapshot, category, obtained_at)
    if parsed["page_size"] < 1 or parsed["total_count"] > 1_000_000:
        raise ValueError("unsafe batch size")
    expected = max(1, math.ceil(parsed["total_count"] / parsed["page_size"]))
    if expected > MAX_PAGES or parsed["page_no"] > expected:
        raise ValueError("batch requires too many pages or page outside total")
    count_expected = parsed["page_size"] if parsed["page_no"] < expected else parsed["total_count"] - (expected-1)*parsed["page_size"]
    if len(parsed["notices"]) != count_expected:
        raise ValueError("incomplete page; do not stage or advance checkpoint")
    _init(ledger)
    period_start, period_end = start.isoformat(), end.isoformat()
    stored_page = _canonical(parsed["notices"])
    fp = hashlib.sha256(stored_page.encode()).hexdigest()
    existing = ledger.conn.execute("SELECT category,period_start,period_end,page_size,total_count,expected_pages,completed FROM snapshot_batches WHERE batch_id=?", (batch_id,)).fetchone()
    contract = (category,period_start,period_end,parsed["page_size"],parsed["total_count"],expected)
    if existing is not None and existing[:6] != contract:
        raise ValueError("batch_id reused with different query or metadata")
    prior = ledger.conn.execute("SELECT fingerprint FROM snapshot_pages WHERE batch_id=? AND page_no=?", (batch_id, parsed["page_no"])).fetchone()
    if prior and prior[0] != fp:
        raise ValueError("same page changed; create a NEW snapshot batch")
    if existing and existing[6]:
        return {**batch_status(ledger,batch_id),"added_versions":0,"unchanged":"completed_replay"}
    with ledger.conn:
        if existing is None:
            ledger.conn.execute("INSERT INTO snapshot_batches(batch_id,category,period_start,period_end,page_size,total_count,expected_pages,completed,created_at) VALUES(?,?,?,?,?,?,?,?,?)",
                (batch_id,*contract,0,obtained_at.isoformat()))
        ledger.conn.execute("INSERT OR IGNORE INTO snapshot_pages(batch_id,page_no,fingerprint,payload) VALUES(?,?,?,?)",
                            (batch_id,parsed["page_no"],fp,stored_page))
    status=batch_status(ledger,batch_id)
    if status["missing_pages"]:
        return {**status,"promoted":False,"added_versions":0}
    rows=ledger.conn.execute("SELECT page_no,payload,fingerprint FROM snapshot_pages WHERE batch_id=? ORDER BY page_no",(batch_id,)).fetchall()
    notices=[]
    seen=set()
    for _,payload,digest in rows:
        if hashlib.sha256(payload.encode()).hexdigest()!=digest:
            raise ValueError("staged page payload tampered")
        for notice in json.loads(payload):
            key=(notice["notice_no"],notice["revision"])
            if key in seen:
                raise ValueError("duplicate notice/revision across pages: quarantine batch")
            seen.add(key)
            notices.append(notice)
    if len(notices)!=parsed["total_count"]:
        raise ValueError("total count mismatch; no promotion")
    # Ingest deduplicates immutable notice versions. A crash before marking
    # completion will replay harmlessly on next call.
    result=ledger.ingest(notices,observed_at=obtained_at)
    with ledger.conn:
        ledger.conn.execute("UPDATE snapshot_batches SET completed=1 WHERE batch_id=?",(batch_id,))
    return {**batch_status(ledger,batch_id),**result,"promoted":True}
