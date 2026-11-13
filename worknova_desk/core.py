"""WORKNOVA Desk: standalone offline KRW quote, contract, delivery and collection ledger.

No network, PayPal API, AI calls, electronic signing, or legal/accounting guarantees.
"""
from __future__ import annotations

import hashlib
import html
import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


class DeskError(ValueError):
    """Domain or safety validation failure."""


def _text(value, field: str, limit: int = 200) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > limit or "\x00" in value:
        raise DeskError(f"{field}: invalid nonempty text (max {limit})")
    return value.strip()


def _won(value, field: str, *, allow_zero: bool = False) -> int:
    if type(value) is not int or value < (0 if allow_zero else 1) or value > 10**12:
        raise DeskError(f"{field}: expected positive integer KRW <= 10^12")
    return value


def _json(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _id() -> str:
    return uuid4().hex


class Desk:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        if self.path.is_symlink() or not self.path.parent.is_dir():
            raise DeskError("database path must be inside an existing local directory, not a symlink")
        self.db = sqlite3.connect(str(self.path), timeout=5, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute("PRAGMA busy_timeout=5000")
        version = self.db.execute("PRAGMA user_version").fetchone()[0]
        if version not in (0, 1):
            self.db.close()
            raise DeskError("unsupported schema version; backup and migrate manually")
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS customers (
          id TEXT PRIMARY KEY, name TEXT NOT NULL, created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS quotes (
          id TEXT PRIMARY KEY, customer_id TEXT NOT NULL REFERENCES customers(id),
          revision INTEGER NOT NULL CHECK(revision > 0), items_json TEXT NOT NULL,
          subtotal_krw INTEGER NOT NULL, vat_krw INTEGER NOT NULL,
          total_krw INTEGER NOT NULL, status TEXT NOT NULL CHECK(status IN ('DRAFT','APPROVED')),
          created_at TEXT NOT NULL, approved_by TEXT,
          UNIQUE(customer_id, id)
        );
        CREATE TABLE IF NOT EXISTS contracts (
          id TEXT PRIMARY KEY, quote_id TEXT UNIQUE NOT NULL REFERENCES quotes(id),
          scope TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('DRAFT','ACTIVE')),
          approved_by TEXT, created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS milestones (
          id TEXT PRIMARY KEY, contract_id TEXT NOT NULL REFERENCES contracts(id),
          title TEXT NOT NULL, amount_krw INTEGER NOT NULL CHECK(amount_krw>0),
          status TEXT NOT NULL CHECK(status IN ('PLANNED','DELIVERED','REVISION_REQUESTED','ACCEPTED')),
          delivered_note TEXT
        );
        CREATE TABLE IF NOT EXISTS receipts (
          id TEXT PRIMARY KEY, milestone_id TEXT NOT NULL REFERENCES milestones(id),
          reference TEXT UNIQUE NOT NULL, amount_krw INTEGER NOT NULL CHECK(amount_krw>0),
          actor TEXT NOT NULL, recorded_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS audit_events (
          seq INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, actor TEXT NOT NULL,
          action TEXT NOT NULL, payload_json TEXT NOT NULL, previous_hash TEXT NOT NULL,
          digest TEXT NOT NULL
        );
        PRAGMA user_version=1;
        """)

    def close(self):
        self.db.close()

    @contextmanager
    def _write(self):
        self.db.execute("BEGIN IMMEDIATE")
        try:
            yield
            self.db.execute("COMMIT")
        except Exception:
            self.db.execute("ROLLBACK")
            raise

    def _fetch(self, table: str, row_id: str):
        if table not in ("customers", "quotes", "contracts", "milestones"):
            raise DeskError("invalid table")
        row = self.db.execute(f"SELECT * FROM {table} WHERE id=?", (row_id,)).fetchone()
        if row is None:
            raise DeskError(f"{table}: unknown id")
        return row

    def _event(self, action: str, actor: str, payload: dict):
        last = self.db.execute("SELECT digest FROM audit_events ORDER BY seq DESC LIMIT 1").fetchone()
        prev = last[0] if last else "0" * 64
        ts = _now()
        raw = _json(payload)
        digest = hashlib.sha256(f"{prev}|{ts}|{actor}|{action}|{raw}".encode()).hexdigest()
        self.db.execute("INSERT INTO audit_events(ts,actor,action,payload_json,previous_hash,digest) VALUES(?,?,?,?,?,?)",
                        (ts, actor, action, raw, prev, digest))

    def add_customer(self, name: str, actor: str = "owner") -> str:
        name, actor = _text(name, "customer name"), _text(actor, "actor", 80)
        key = _id()
        with self._write():
            self.db.execute("INSERT INTO customers VALUES (?,?,?)", (key, name, _now()))
            self._event("CUSTOMER_CREATED", actor, {"id": key})
        return key

    def new_quote(self, customer_id: str, items: list[dict], *, taxable: bool = True,
                  actor: str = "owner") -> str:
        actor = _text(actor, "actor", 80)
        if type(taxable) is not bool or not isinstance(items, list) or not (1 <= len(items) <= 100):
            raise DeskError("quote needs 1..100 line items and boolean taxable")
        normalized, subtotal = [], 0
        for item in items:
            if not isinstance(item, dict):
                raise DeskError("line item must be object")
            name = _text(item.get("description"), "description")
            qty = _won(item.get("quantity"), "quantity")
            unit = _won(item.get("unit_krw"), "unit_krw")
            line = qty * unit
            subtotal += line
            if subtotal > 10**12:
                raise DeskError("quote exceeds maximum KRW amount")
            normalized.append({"description": name, "quantity": qty, "unit_krw": unit,
                               "line_total_krw": line})
        vat = (subtotal + 5) // 10 if taxable else 0  # 10% VAT, half-up to whole KRW
        key = _id()
        with self._write():
            self._fetch("customers", customer_id)
            self.db.execute("""INSERT INTO quotes
                (id,customer_id,revision,items_json,subtotal_krw,vat_krw,total_krw,status,created_at)
                VALUES (?,?,?,?,?,?,?,?,?)""",
                (key, customer_id, 1, _json(normalized), subtotal, vat, subtotal + vat, "DRAFT", _now()))
            self._event("QUOTE_CREATED", actor, {"id": key, "total_krw": subtotal + vat, "taxable": taxable})
        return key

    def approve_quote(self, quote_id: str, actor: str):
        actor = _text(actor, "actor", 80)
        with self._write():
            quote = self._fetch("quotes", quote_id)
            if quote["status"] != "DRAFT":
                raise DeskError("quote is not draft; duplicate approval rejected")
            self.db.execute("UPDATE quotes SET status='APPROVED',approved_by=? WHERE id=?", (actor, quote_id))
            self._event("QUOTE_APPROVED", actor, {"id": quote_id})

    def new_contract(self, quote_id: str, scope: str, steps: list[dict], actor: str = "owner") -> str:
        scope, actor = _text(scope, "scope", 2000), _text(actor, "actor", 80)
        if not isinstance(steps, list) or not (1 <= len(steps) <= 50):
            raise DeskError("contract needs 1..50 milestones")
        milestones = [(_text(s.get("title"), "milestone title"), _won(s.get("amount_krw"), "milestone KRW"))
                      if isinstance(s, dict) else (_text(None, "milestone title"), 0) for s in steps]
        if len({title for title, _ in milestones}) != len(milestones):
            raise DeskError("duplicate milestone titles")
        key = _id()
        with self._write():
            quote = self._fetch("quotes", quote_id)
            if quote["status"] != "APPROVED":
                raise DeskError("quote must be explicitly approved")
            if sum(value for _, value in milestones) != quote["total_krw"]:
                raise DeskError("milestones must total the approved quote amount")
            if self.db.execute("SELECT 1 FROM contracts WHERE quote_id=?", (quote_id,)).fetchone():
                raise DeskError("quote already has a contract")
            self.db.execute("INSERT INTO contracts VALUES(?,?,?,?,?,?)",
                            (key, quote_id, scope, "DRAFT", None, _now()))
            for title, amount in milestones:
                self.db.execute("INSERT INTO milestones VALUES (?,?,?,?,?,?)",
                                (_id(), key, title, amount, "PLANNED", None))
            self._event("CONTRACT_CREATED", actor, {"id": key, "quote_id": quote_id})
        return key

    def activate_contract(self, contract_id: str, actor: str):
        actor = _text(actor, "actor", 80)
        with self._write():
            row = self._fetch("contracts", contract_id)
            if row["status"] != "DRAFT":
                raise DeskError("contract is not draft")
            self.db.execute("UPDATE contracts SET status='ACTIVE',approved_by=? WHERE id=?", (actor, contract_id))
            self._event("CONTRACT_ACTIVATED", actor, {"id": contract_id, "local_only": True})

    def _milestone_transition(self, milestone_id: str, allowed: tuple, target: str,
                              actor: str, note: str | None = None):
        actor = _text(actor, "actor", 80)
        if note is not None:
            note = _text(note, "delivery/revision note", 2000)
        with self._write():
            milestone = self._fetch("milestones", milestone_id)
            contract = self._fetch("contracts", milestone["contract_id"])
            if contract["status"] != "ACTIVE" or milestone["status"] not in allowed:
                raise DeskError("invalid milestone transition or inactive contract")
            self.db.execute("UPDATE milestones SET status=?,delivered_note=? WHERE id=?",
                            (target, note if note is not None else milestone["delivered_note"], milestone_id))
            self._event("MILESTONE_" + target, actor, {"id": milestone_id})

    def deliver(self, milestone_id: str, actor: str, evidence_note: str):
        self._milestone_transition(milestone_id, ("PLANNED", "REVISION_REQUESTED"),
                                   "DELIVERED", actor, evidence_note)

    def request_revision(self, milestone_id: str, actor: str, reason: str):
        self._milestone_transition(milestone_id, ("DELIVERED",), "REVISION_REQUESTED", actor, reason)

    def accept(self, milestone_id: str, actor: str):
        self._milestone_transition(milestone_id, ("DELIVERED",), "ACCEPTED", actor)

    def record_collection(self, milestone_id: str, amount_krw: int, reference: str, actor: str):
        amount_krw, reference, actor = (_won(amount_krw, "receipt KRW"),
                                        _text(reference, "reference", 100), _text(actor, "actor", 80))
        with self._write():
            existing = self.db.execute("SELECT * FROM receipts WHERE reference=?", (reference,)).fetchone()
            if existing:
                if existing["milestone_id"] == milestone_id and existing["amount_krw"] == amount_krw:
                    return existing["id"]  # idempotent retry, no duplicate event
                raise DeskError("reference reused with different payment evidence")
            milestone = self._fetch("milestones", milestone_id)
            if milestone["status"] != "ACCEPTED":
                raise DeskError("collection can only be recorded after delivery acceptance")
            paid = self.db.execute("SELECT COALESCE(SUM(amount_krw),0) FROM receipts WHERE milestone_id=?",
                                   (milestone_id,)).fetchone()[0]
            if amount_krw > milestone["amount_krw"] - paid:
                raise DeskError("receipt would overpay milestone")
            key = _id()
            self.db.execute("INSERT INTO receipts VALUES(?,?,?,?,?,?)",
                            (key, milestone_id, reference, amount_krw, actor, _now()))
            self._event("COLLECTION_RECORDED", actor, {"id": key, "milestone_id": milestone_id,
                                                        "amount_krw": amount_krw})
            return key

    def report(self, contract_id: str, *, include_customer: bool = False) -> dict:
        contract = self._fetch("contracts", contract_id)
        quote = self._fetch("quotes", contract["quote_id"])
        customer = self._fetch("customers", quote["customer_id"])
        steps = []
        for row in self.db.execute("SELECT * FROM milestones WHERE contract_id=? ORDER BY rowid", (contract_id,)):
            paid = self.db.execute("SELECT COALESCE(SUM(amount_krw),0) FROM receipts WHERE milestone_id=?",
                                   (row["id"],)).fetchone()[0]
            steps.append({"id": row["id"], "title": row["title"], "amount_krw": row["amount_krw"],
                          "status": row["status"], "paid_krw": paid,
                          "outstanding_krw": row["amount_krw"]-paid})
        return {"contract_id": contract_id, "status": contract["status"],
                "customer": customer["name"] if include_customer else "[REDACTED]",
                "quote_id": quote["id"], "subtotal_krw": quote["subtotal_krw"],
                "vat_krw": quote["vat_krw"], "total_krw": quote["total_krw"],
                "paid_krw": sum(x["paid_krw"] for x in steps),
                "outstanding_krw": sum(x["outstanding_krw"] for x in steps),
                "milestones": steps, "note": "Manual offline record only; not a bank or PayPal confirmation"}

    def export_html(self, contract_id: str) -> str:
        r = self.report(contract_id)
        rows = "".join("<tr><td>" + html.escape(s["title"], quote=True) + "</td><td>" +
                       html.escape(s["status"], quote=True) + "</td><td>" +
                       str(s["amount_krw"]) + "</td><td>" + str(s["paid_krw"]) + "</td></tr>"
                       for s in r["milestones"])
        return ("<!doctype html><html lang='ko'><meta charset='utf-8'>"
                "<meta http-equiv='Content-Security-Policy' content=\"default-src 'none'; style-src 'unsafe-inline'\">"
                "<title>WORKNOVA Desk offline report</title><body><h1>WORKNOVA Desk</h1>"
                "<p>오프라인 수기 기록 · 결제 확인 또는 전자서명 아님</p>"
                f"<p>총 견적 {r['total_krw']:,}원 / 수금 기록 {r['paid_krw']:,}원 / 잔액 {r['outstanding_krw']:,}원</p>"
                "<table><thead><tr><th>단계</th><th>상태</th><th>금액</th><th>기록된 수금</th></tr></thead>"
                f"<tbody>{rows}</tbody></table></body></html>")

    def verify_audit(self) -> int:
        previous = "0" * 64
        count = 0
        for row in self.db.execute("SELECT * FROM audit_events ORDER BY seq"):
            calculated = hashlib.sha256((previous + "|" + row["ts"] + "|" + row["actor"] + "|" +
                                         row["action"] + "|" + row["payload_json"]).encode()).hexdigest()
            if row["previous_hash"] != previous or row["digest"] != calculated:
                raise DeskError(f"audit chain mismatch at event {row['seq']}")
            previous = calculated
            count += 1
        integrity = self.db.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise DeskError("SQLite integrity_check failed")
        return count

    def backup(self, destination: str | Path) -> str:
        dst = Path(destination)
        if not dst.parent.is_dir() or dst.exists() or dst.is_symlink() or dst.resolve() == self.path.resolve():
            raise DeskError("backup target must be a new file in an existing directory")
        self.verify_audit()
        # SQLite online backup retains a consistent snapshot even in WAL mode.
        try:
            with sqlite3.connect(str(dst)) as out:
                self.db.backup(out)
                if out.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                    raise DeskError("backup failed integrity check")
            digest = hashlib.sha256(dst.read_bytes()).hexdigest()
            return digest
        except Exception:
            dst.unlink(missing_ok=True)
            raise
