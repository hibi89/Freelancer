"""Consent-safe local cross-module portfolio and human-curated Onbid watchlist.

No network, bidding, legal eligibility conclusion, external data, or automated trading.
All source ledgers remain independent; no asset IDs are merged across providers.
"""
from __future__ import annotations

from datetime import datetime
from contextlib import closing
from pathlib import Path
import hashlib
import json
import sqlite3
from uuid import UUID
from urllib.parse import quote

from .core import BidLedger, KST, _canonical
from .court import CourtStore
from .onbid import OnbidStore

MAX_NOTE = 240
STATUS = frozenset(("관심", "검토 보류", "관심 해제"))


def _watch_table(conn: sqlite3.Connection) -> None:
    conn.execute('''CREATE TABLE IF NOT EXISTS onbid_watch_events (
        id INTEGER PRIMARY KEY, request_id TEXT UNIQUE NOT NULL,
        property_id TEXT NOT NULL, condition_id TEXT NOT NULL,
        state TEXT NOT NULL, note TEXT NOT NULL,
        asset_sha256 TEXT NOT NULL, occurred_at TEXT NOT NULL,
        fingerprint TEXT NOT NULL)''')
    conn.execute("CREATE INDEX IF NOT EXISTS onbid_watch_asset ON onbid_watch_events(property_id,condition_id,id DESC)")
    conn.commit()


def _verified_events(conn: sqlite3.Connection) -> list[dict]:
    try:
        rows = conn.execute('''SELECT request_id,property_id,condition_id,state,note,asset_sha256,occurred_at,fingerprint
                           FROM onbid_watch_events ORDER BY id''').fetchall()
    except sqlite3.OperationalError as exc:
        if "no such table: onbid_watch_events" in str(exc):
            return []
        raise
    verified = []
    for request_id, prop, cond, state, note, sha, when, fp in rows:
        row = dict(request_id=request_id, property_id=prop, condition_id=cond,
                   state=state, note=note, asset_sha256=sha, occurred_at=when)
        if hashlib.sha256(_canonical(row).encode("utf-8")).hexdigest() != fp:
            raise ValueError("Onbid watchlist audit tampered; restore a verified backup")
        verified.append(row)
    return verified


def watch_onbid(db: str | Path, *, property_id: str, condition_id: str, state: str,
                note: str, request_id: str) -> dict:
    """Append human preference anchored to the exact current local property version."""
    if state not in STATUS or not isinstance(note, str) or not 1 <= len(note.strip()) <= MAX_NOTE:
        raise ValueError("watch state and 1..240 character local note required")
    if any(ord(c) < 32 for c in note):
        raise ValueError("control characters in note")
    try:
        UUID(request_id)
    except (ValueError, TypeError, AttributeError):
        raise ValueError("watch request_id must be UUID") from None
    with OnbidStore(db) as store:
        report = store.report()  # independently verifies immutable original data
        matches = [x for x in report["assets"]
                   if x["property_id"] == property_id and x["condition_id"] == condition_id]
        if len(matches) != 1:
            raise ValueError("watch only an existing identified Onbid asset")
        source_sha = store.conn.execute('''SELECT fingerprint FROM onbid_events
                   WHERE dataset='assets' AND property_id=? AND condition_id=? ORDER BY id DESC LIMIT 1''',
                   (property_id, condition_id)).fetchone()[0]
        prior = _verified_events(store.conn)
        duplicate = next((r for r in prior if r["request_id"] == request_id), None)
        if duplicate:
            if (duplicate["property_id"], duplicate["condition_id"], duplicate["state"], duplicate["note"], duplicate["asset_sha256"]) != (property_id, condition_id, state, note.strip(), source_sha):
                raise ValueError("conflicting watch request_id reuse")
            return {"written": False, "replay": True, "request_id": request_id, "legal_review_complete": False}
        entry = dict(request_id=request_id, property_id=property_id, condition_id=condition_id,
                     state=state, note=note.strip(), asset_sha256=source_sha,
                     occurred_at=datetime.now(KST).isoformat())
        fp = hashlib.sha256(_canonical(entry).encode("utf-8")).hexdigest()
        _watch_table(store.conn)
        with store.conn:
            store.conn.execute('''INSERT INTO onbid_watch_events
                       (request_id,property_id,condition_id,state,note,asset_sha256,occurred_at,fingerprint)
                       VALUES (?,?,?,?,?,?,?,?)''', (request_id, property_id, condition_id,
                       state, note.strip(), source_sha, entry["occurred_at"], fp))
        return {"written": True, "request_id": request_id, "state": state,
                "property_id": property_id, "condition_id": condition_id,
                "source_fingerprint": source_sha, "legal_review_complete": False}


def watchlist(db: str | Path) -> dict:
    with OnbidStore(db) as store:
        report = store.report()
        events = _verified_events(store.conn)
        current = {(x["property_id"], x["condition_id"]): x for x in report["assets"]}
        latest = {}
        for row in events:
            latest[(row["property_id"], row["condition_id"])] = row
        out = []
        for key, row in sorted(latest.items()):
            asset = current.get(key)
            latest_sha = store.conn.execute('''SELECT fingerprint FROM onbid_events WHERE dataset='assets'
                     AND property_id=? AND condition_id=? ORDER BY id DESC LIMIT 1''', key).fetchone() if asset else None
            out.append({"property_id": key[0], "condition_id": key[1], "state": row["state"],
                        "note": row["note"], "recorded_at": row["occurred_at"],
                        "source_changed_since_watch": not latest_sha or latest_sha[0] != row["asset_sha256"],
                        "original_source_verified": False, "review_status": "추가 확인 필요"})
        return {"source": "ONBID_LOCAL_WATCHLIST", "items": out,
                "active_count": sum(x["state"] != "관심 해제" for x in out),
                "audited_events": len(events), "network_calls": 0,
                "disclaimer": "관심목록은 고객 메모이며 공매물건의 법률·수익성 검증이나 실시간 상태를 보증하지 않습니다."}


def filter_onbid(db: str | Path, *, property_type: str | None = None,
                 max_bid_krw: int | None = None, min_failed_rounds: int | None = None) -> dict:
    """Deterministic local search; missing price/round count cannot meet filters."""
    if property_type is not None and property_type not in ("부동산", "동산", "차량", "기타"):
        raise ValueError("invalid property type")
    if max_bid_krw is not None and (type(max_bid_krw) is not int or not 0 <= max_bid_krw <= 10**17):
        raise ValueError("invalid max bid")
    if min_failed_rounds is not None and (type(min_failed_rounds) is not int or not 0 <= min_failed_rounds <= 1000):
        raise ValueError("invalid round threshold")
    with OnbidStore(db) as store:
        records = store.report()["assets"]
    eligible = []
    for r in records:
        if property_type is not None and r["property_type"] != property_type:
            continue
        if max_bid_krw is not None and (r["minimum_bid_krw"] is None or r["minimum_bid_krw"] > max_bid_krw):
            continue
        if min_failed_rounds is not None and (r["failed_rounds"] is None or r["failed_rounds"] < min_failed_rounds):
            continue
        eligible.append(r)
    return {"source": "ONBID_OFFLINE_FILTER", "total": len(records), "matches": len(eligible),
            "assets": eligible, "online_checked": False, "investment_qualified": False,
            "disclaimer": "가격/유찰은 승인된 로컬 사본 기준입니다. 원문과 권리/비용을 개별 확인하세요."}


def portfolio_report(db: str | Path) -> dict:
    """One read-only overview with separate source identifiers and explicit freshness."""
    path = Path(db)
    if not path.is_file():
        raise ValueError("existing local database required; no new DB will be created")
    # A reporting action must not turn an arbitrary SQLite file into a new
    # BID AX database by silently creating missing source tables.
    with closing(sqlite3.connect(f"file:{quote(str(path.resolve()), safe='/')}?mode=ro", uri=True)) as ro:
        existing = {row[0] for row in ro.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if not {"notice_events", "onbid_events", "court_document_events"} & existing:
        raise ValueError("none of the three source ledgers are present; import authorized data first")
    notices = []
    if "notice_events" in existing:
        with BidLedger(path) as g2b:
            notices = g2b.current()
    auction = {"assets": []}
    if "onbid_events" in existing:
        with OnbidStore(path) as onbid:
            auction = onbid.report()
    cases = []
    if "court_document_events" in existing:
        with CourtStore(path) as court:
            court._verify()
            cases = court.conn.execute('''SELECT case_id, COUNT(*), MAX(imported_at)
                        FROM court_document_events GROUP BY case_id ORDER BY case_id''').fetchall()
    return {
        "scope": "LOCAL_OFFLINE_SUMMARY_NOT_LEGAL_ADVICE",
        "generated_at": datetime.now(KST).isoformat(),
        "g2b": {"source": "G2B", "count": len(notices),
                "notices": [{"source": "G2B", "notice_no": x["notice_no"],
                             "deadline": x["deadline"], "fingerprint": x["fingerprint"],
                             "review_status": "원문 추가 확인 필요"} for x in notices]},
        "onbid": {"source": "ONBID", "count": len(auction["assets"]),
                  "assets": [{"source": "ONBID", "property_id": x["property_id"],
                              "condition_id": x["condition_id"],
                              "result_status": x["result_status"],
                              "review_status": "추가 확인 필요"} for x in auction["assets"]]},
        "court": {"source": "COURT_CONSENTED_LOCAL", "count": len(cases),
                  "cases": [{"source": "COURT_CONSENTED_LOCAL", "case_id": k,
                             "document_versions": count, "last_local_import": ts,
                             "review_status": "추가 확인 필요"} for k, count, ts in cases]},
        "authoritative_live_lookup": False,
        "legal_or_investment_approval": False,
        "requires_human_verification": True,
    }
