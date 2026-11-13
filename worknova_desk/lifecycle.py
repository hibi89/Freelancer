"""Offline single-owner customer lifecycle with explicit consent and no schema migration.

Not multi-user authentication or legal erasure. Related financial records are preserved.
"""
from __future__ import annotations

from .core import Desk, DeskError, _text


def rename_customer(desk: Desk, customer_id: str, new_name: str, *, expected_name: str,
                    actor: str, confirmation: str) -> dict:
    if confirmation != "CONFIRM_CUSTOMER_UPDATE":
        raise DeskError("customer rename requires explicit confirmation")
    name = _text(new_name, "new customer name")
    old = _text(expected_name, "expected customer name")
    actor = _text(actor, "actor", 80)
    with desk._write():
        current = desk._fetch("customers", customer_id)
        if current["name"] != old:
            raise DeskError("stale customer edit: expected name no longer matches")
        if current["name"] == name:
            return {"customer_id": customer_id, "changed": False}
        desk.db.execute("UPDATE customers SET name=? WHERE id=?", (name, customer_id))
        # Names are low entropy: even unhashed comparison values can be recovered
        # from bare SHA256 by dictionary attack. Never put names or name hashes in audit.
        desk._event("CUSTOMER_RENAMED", actor, {"id": customer_id, "name_changed": True})
    return {"customer_id": customer_id, "changed": True}


def delete_unused_customer(desk: Desk, customer_id: str, *, actor: str, confirmation: str) -> dict:
    """Delete only a customer without ANY quote; never erase contractual/financial history."""
    if confirmation != "DELETE_UNUSED_CUSTOMER":
        raise DeskError("customer deletion requires explicit confirmation")
    actor = _text(actor, "actor", 80)
    with desk._write():
        desk._fetch("customers", customer_id)
        count = desk.db.execute("SELECT COUNT(*) FROM quotes WHERE customer_id=?", (customer_id,)).fetchone()[0]
        if count:
            raise DeskError("customer has financial history; deletion refused (no cascade)")
        desk.db.execute("DELETE FROM customers WHERE id=?", (customer_id,))
        desk._event("UNUSED_CUSTOMER_DELETED", actor, {"id": customer_id, "related_quotes": 0})
    return {"deleted": True, "related_financial_rows_removed": 0}
