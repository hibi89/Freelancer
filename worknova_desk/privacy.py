"""Explicit, owner-only, minimised offline customer portfolio export.

Does not implement logins, encryption, GDPR compliance, buyer identity checks, or
access to third-party data. All fields are amounts/statuses/opaque local IDs by
DEFAULT; no scopes, free text, names, notes, addresses, bank references or files.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path

from .core import Desk, DeskError, _json


def _portfolio(desk: Desk, customer_id: str, *, include_name: bool) -> dict:
    customer = desk._fetch("customers", customer_id)
    desk.verify_audit()
    quotes = [dict(row) for row in desk.db.execute(
        "SELECT id,revision,status,total_krw,created_at FROM quotes WHERE customer_id=? ORDER BY rowid",
        (customer_id,))]
    contracts = [dict(row) for row in desk.db.execute("""
        SELECT c.id,c.quote_id,c.status FROM contracts c
        JOIN quotes q ON q.id=c.quote_id WHERE q.customer_id=? ORDER BY c.rowid
    """, (customer_id,))]
    total_paid = 0
    for contract in contracts:
        steps = desk.db.execute("""
            SELECT m.id,m.status,m.amount_krw,COALESCE(SUM(r.amount_krw),0) paid_krw
            FROM milestones m LEFT JOIN receipts r ON r.milestone_id=m.id
            WHERE m.contract_id=? GROUP BY m.id ORDER BY m.rowid
        """, (contract["id"],))
        contract["milestones"] = [{"id": row["id"], "status": row["status"],
             "amount_krw": row["amount_krw"], "paid_krw": row["paid_krw"],
             "outstanding_krw": row["amount_krw"]-row["paid_krw"]} for row in steps]
        if any(item["paid_krw"] < 0 or item["paid_krw"] > item["amount_krw"] for item in contract["milestones"]):
            raise DeskError("inconsistent manual receipt amounts; summary refused")
        total_paid += sum(x["paid_krw"] for x in contract["milestones"])
    return {"format":"worknova-local-customer-summary-v1",
            "warning":"Local unsigned manual records; not verified bank payments, legal/consent/tax certification. IDs and monetary values remain confidential business data.",
            "customer_id":customer["id"],"customer_name":customer["name"] if include_name else "[REDACTED]",
            "quotes":quotes,"contracts":contracts,"manual_collections_krw":total_paid,
            "excluded_fields":["scope","item_descriptions","delivery_notes","customer_free_text","bank_references","evidence_paths","evidence_bytes"]}


def export_customer_summary(desk: Desk, customer_id: str, destination: str | Path,
                            *, include_name: bool=False, confirm_disclosure: bool=False) -> dict:
    if type(include_name) is not bool or type(confirm_disclosure) is not bool:
        raise DeskError("invalid privacy controls")
    if include_name and not confirm_disclosure:
        raise DeskError("customer-name disclosure requires explicit confirmation")
    dest=Path(destination)
    if dest.suffix.lower()!=".json" or dest.exists() or dest.is_symlink() or not dest.parent.is_dir() or dest.parent.is_symlink():
        raise DeskError("customer summary requires a NEW .json in existing non-symlink directory")
    # Keep all related quote/contract/receipt totals in one consistent snapshot;
    # no customer record is changed by an export.
    desk.db.execute("BEGIN")
    try:
        data = (_json(_portfolio(desk,customer_id,include_name=include_name))+"\n").encode("utf-8")
    finally:
        desk.db.execute("ROLLBACK")
    if len(data)>10*1024*1024:
        raise DeskError("summary exceeds 10 MiB; export canceled without writing")
    created=False
    try:
        flags=os.O_CREAT|os.O_EXCL|os.O_WRONLY|getattr(os,"O_BINARY",0)
        if hasattr(os,"O_NOFOLLOW"): flags |= os.O_NOFOLLOW
        fd=os.open(dest,flags,0o600)
        created=True
        with os.fdopen(fd,"wb") as fp:
            fp.write(data)
            fp.flush()
            os.fsync(fp.fileno())
    except Exception:
        if created: dest.unlink(missing_ok=True)
        raise
    return {"created":True,"sha256":hashlib.sha256(data).hexdigest(),
            "bytes":len(data),"customer_name_included":include_name,
            "note":"Local confidential data; no network transmission; store with OS access controls"}
