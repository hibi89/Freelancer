"""Explicit, on-PC only deadline polling with durable deduplication.

An active local UI/CLI may poll. No background daemon, email, SMS or external push.
Checks after a device wakes are safe to repeat; expired notices are not omitted.
"""
from __future__ import annotations

from datetime import datetime
import hashlib
from .core import BidLedger, KST
from .workflow import due_alerts


def poll_due(ledger: BidLedger, *, now: datetime | None=None, within_hours: int=72) -> dict:
    current=now or datetime.now(KST)
    if current.tzinfo is None or current.utcoffset() is None:
        raise ValueError("explicit timezone offset required")
    ledger.verify_integrity()
    alerts=due_alerts(ledger,now=current,within_hours=within_hours)
    ledger.conn.execute("""CREATE TABLE IF NOT EXISTS reminder_events (
        key TEXT PRIMARY KEY, notice_no TEXT NOT NULL, fingerprint TEXT NOT NULL,
        state TEXT NOT NULL, first_seen TEXT NOT NULL)""")
    newly=[]
    with ledger.conn:
        for alert in alerts:
            source="\u0000".join((alert["notice_no"],alert["fingerprint"],alert["deadline"],alert["state"],str(within_hours)))
            key=hashlib.sha256(source.encode()).hexdigest()
            cursor=ledger.conn.execute("INSERT OR IGNORE INTO reminder_events(key,notice_no,fingerprint,state,first_seen) VALUES (?,?,?,?,?)",
                                       (key,alert["notice_no"],alert["fingerprint"],alert["state"],current.astimezone(KST).isoformat()))
            if cursor.rowcount:
                newly.append(alert)
    return {"new":newly,"new_count":len(newly),"visible_count":len(alerts),
            "scope":"ACTIVE_PC_POLL_ONLY", "disclaimer":"PC 종료 중에는 조회/알림이 실행되지 않습니다"}
