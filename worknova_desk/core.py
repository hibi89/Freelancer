"""WORKNOVA Desk: standalone offline KRW quote, contract, delivery and collection ledger.

No network, PayPal API, AI calls, electronic signing, or legal/accounting guarantees.
"""
from __future__ import annotations

import hashlib
import html
import json
import os
import sqlite3
import tempfile
from contextlib import contextmanager, closing
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
    def __init__(self, path: str | Path, *, allow_create: bool = True):
        self.path = Path(path)
        if self.path.is_symlink() or not self.path.parent.is_dir() or self.path.parent.is_symlink():
            raise DeskError("database path must be inside an existing non-symlink directory")
        created_new_file = False
        if not allow_create:
            # SQLite's default connect silently creates a fresh empty ledger. For all
            # existing-ledger operations this can look like catastrophic data loss.
            # URI mode=rw makes the missing-file check atomic at SQLite open time.
            try:
                self.db = sqlite3.connect(self.path.resolve().as_uri() + '?mode=rw',
                                          uri=True, timeout=5, isolation_level=None)
            except sqlite3.OperationalError as exc:
                raise DeskError("database not found/readable; locate an existing backup, do not create a replacement") from exc
        else:
            # New private POSIX ledger with mode 0600. Existing file permissions are
            # never rewritten; Windows privacy depends on OS profile ACL/BitLocker.
            if not self.path.exists():
                try:
                    fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o600)
                except FileExistsError:
                    raise DeskError("database path changed during creation") from None
                except OSError as exc:
                    raise DeskError("cannot create new local ledger") from exc
                else:
                    os.close(fd)
                    created_new_file = True
            self.db = sqlite3.connect(str(self.path), timeout=5, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        try:
            # Fail closed *before* running CREATE TABLE IF NOT EXISTS. A foreign
            # SQLite file (user_version=0) must never be quietly converted to an
            # empty WORKNOVA ledger, especially during SHA-pinned restore.
            version = self.db.execute("PRAGMA user_version").fetchone()[0]
            if version not in (0, 1, 2):
                raise DeskError("unsupported schema version; backup and migrate manually")
            if version == 0 and not created_new_file:
                raise DeskError("existing file has no WORKNOVA schema; original left unchanged")
            if version == 2 and not created_new_file:
                required = {"customers", "quotes", "contracts", "milestones", "receipts", "audit_events"}
                names = {row[0] for row in self.db.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'")}
                if not required.issubset(names):
                    raise DeskError("incomplete WORKNOVA v2 schema; restore a verified backup")
                quote_columns = {row[1] for row in self.db.execute("PRAGMA table_info(quotes)")}
                if not {"root_quote_id", "parent_quote_id"}.issubset(quote_columns):
                    raise DeskError("invalid WORKNOVA v2 quote columns")
            self.db.execute("PRAGMA foreign_keys=ON")
            self.db.execute("PRAGMA busy_timeout=5000")
        except sqlite3.DatabaseError as exc:
            self.db.close()
            raise DeskError("invalid or corrupt SQLite database; no data changed") from exc
        except Exception:
            self.db.close()
            raise
        try:
            self.db.executescript("""
        CREATE TABLE IF NOT EXISTS customers (
          id TEXT PRIMARY KEY, name TEXT NOT NULL, created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS quotes (
          id TEXT PRIMARY KEY, customer_id TEXT NOT NULL REFERENCES customers(id),
          revision INTEGER NOT NULL CHECK(revision > 0), items_json TEXT NOT NULL,
          root_quote_id TEXT, parent_quote_id TEXT,
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
        """)
            if version == 0:
                self.db.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_quote_root_revision ON quotes(root_quote_id, revision)")
                self.db.execute("PRAGMA user_version=2")
            elif not created_new_file:
                # Refuse to operate on a corrupted historical audit on reopen.
                # Hashes are UNSIGNED: this detects accidental/partial changes,
                # not an administrator replacing both DB and checkpoint.
                self.verify_audit()
        except sqlite3.DatabaseError as exc:
            self.db.close()
            raise DeskError("database schema/audit unreadable; locate a verified backup") from exc
        except Exception:
            self.db.close()
            raise

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

    @staticmethod
    def _priced_items(items: list[dict], taxable: bool):
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
        return normalized, subtotal, vat

    def new_quote(self, customer_id: str, items: list[dict], *, taxable: bool = True,
                  actor: str = "owner") -> str:
        actor = _text(actor, "actor", 80)
        normalized, subtotal, vat = self._priced_items(items, taxable)
        key = _id()
        with self._write():
            self._fetch("customers", customer_id)
            if self.schema_version == 2:
                self.db.execute("""INSERT INTO quotes
                    (id,customer_id,revision,items_json,root_quote_id,parent_quote_id,
                     subtotal_krw,vat_krw,total_krw,status,created_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                    (key, customer_id, 1, _json(normalized), key, None, subtotal, vat, subtotal + vat, "DRAFT", _now()))
            else:
                self.db.execute("""INSERT INTO quotes
                    (id,customer_id,revision,items_json,subtotal_krw,vat_krw,total_krw,status,created_at)
                    VALUES (?,?,?,?,?,?,?,?,?)""",
                    (key, customer_id, 1, _json(normalized), subtotal, vat, subtotal + vat, "DRAFT", _now()))
            self._event("QUOTE_CREATED", actor, {"id": key, "total_krw": subtotal + vat, "taxable": taxable})
        return key

    @property
    def schema_version(self) -> int:
        return self.db.execute("PRAGMA user_version").fetchone()[0]

    def quote_history(self, quote_id: str) -> list[dict]:
        quote = self._fetch("quotes", quote_id)
        if self.schema_version != 2:
            return [{k: quote[k] for k in ("id", "revision", "status", "created_at", "total_krw")}]
        rows = self.db.execute("""SELECT id,revision,status,created_at,total_krw,parent_quote_id
            FROM quotes WHERE root_quote_id=? ORDER BY revision""", (quote["root_quote_id"],))
        return [dict(r) for r in rows]

    def revise_quote(self, quote_id: str, items: list[dict], *, taxable: bool=True, actor: str="owner") -> str:
        actor = _text(actor, "actor", 80)
        normalized, subtotal, vat = self._priced_items(items, taxable)
        if self.schema_version != 2:
            raise DeskError("explicit schema migration with verified backup is required")
        with self._write():
            source = self._fetch("quotes", quote_id)
            latest = self.db.execute("""SELECT id,revision FROM quotes WHERE root_quote_id=?
                ORDER BY revision DESC LIMIT 1""", (source["root_quote_id"],)).fetchone()
            if latest["id"] != quote_id:
                raise DeskError("can only revise latest quote version")
            key = _id()
            self.db.execute("""INSERT INTO quotes
                (id,customer_id,revision,items_json,root_quote_id,parent_quote_id,
                 subtotal_krw,vat_krw,total_krw,status,created_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (key, source["customer_id"], latest["revision"] + 1, _json(normalized),
                 source["root_quote_id"], quote_id, subtotal, vat, subtotal + vat, "DRAFT", _now()))
            self._event("QUOTE_REVISED", actor, {"id":key,"parent_id":quote_id,"root":source["root_quote_id"],
                                                  "revision":latest["revision"]+1,"total_krw":subtotal+vat})
            return key

    def list_customers(self, search: str="") -> list[dict]:
        if not isinstance(search,str) or len(search)>100: raise DeskError("invalid search")
        return [dict(r) for r in self.db.execute("SELECT id,name,created_at FROM customers ORDER BY created_at DESC, rowid DESC")
                if search.casefold() in r["name"].casefold()]

    def list_quotes(self, customer_id: str) -> list[dict]:
        self._fetch("customers", customer_id)
        return [dict(r) for r in self.db.execute("SELECT id,revision,status,total_krw,created_at FROM quotes WHERE customer_id=? ORDER BY rowid DESC", (customer_id,))]

    def list_contracts(self, customer_id: str) -> list[dict]:
        self._fetch("customers", customer_id)
        return [dict(r) for r in self.db.execute("""SELECT c.id,c.scope,c.status,c.quote_id FROM contracts c
                    JOIN quotes q ON c.quote_id=q.id WHERE q.customer_id=? ORDER BY c.rowid DESC""", (customer_id,))]

    def list_milestones(self, contract_id: str) -> list[dict]:
        self._fetch("contracts", contract_id)
        return [dict(r) for r in self.db.execute("SELECT id,title,amount_krw,status,delivered_note FROM milestones WHERE contract_id=? ORDER BY rowid", (contract_id,))]

    def export_quote_html(self, quote_id: str) -> str:
        quote = self._fetch("quotes", quote_id)
        entries = json.loads(quote["items_json"])
        rows = "".join("<tr><td>" + html.escape(x["description"],quote=True) + "</td><td>" +
             str(x["quantity"]) + "</td><td>" + str(x["unit_krw"]) + "</td><td>" + str(x["line_total_krw"]) + "</td></tr>" for x in entries)
        return ("<!doctype html><html lang='ko'><meta charset='utf-8'>"
                "<meta http-equiv='Content-Security-Policy' content=\"default-src 'none'; style-src 'unsafe-inline'\">"
                "<title>WORKNOVA 견적 미리보기</title><body><h1>WORKNOVA 견적 미리보기</h1>"
                "<p>오프라인 검토용 초안 · 고객 신원 비공개 · 법적 계약 또는 전자서명 아님</p>"
                f"<p>버전 {quote['revision']} / 상태 {html.escape(quote['status'])}</p>"
                "<table><tr><th>항목</th><th>수량</th><th>단가(원)</th><th>합계(원)</th></tr>" + rows + "</table>"
                f"<p>공급가 {quote['subtotal_krw']:,}원 | 세금 {quote['vat_krw']:,}원 | 총액 {quote['total_krw']:,}원</p>"
                "<p>부가세 여부는 작성자 입력에 따릅니다. 세무 신고의 적법성은 보증하지 않습니다.</p></body></html>")

    def migrate_v1(self, backup_out: str | Path) -> str:
        if self.schema_version != 1: raise DeskError("migration requires v1 database")
        digest = self.backup(backup_out)  # keep independently verifiable v1 copy; never overwrite
        with self._write():
            self.db.execute("ALTER TABLE quotes ADD COLUMN root_quote_id TEXT")
            self.db.execute("ALTER TABLE quotes ADD COLUMN parent_quote_id TEXT")
            self.db.execute("UPDATE quotes SET root_quote_id=id")
            self.db.execute("CREATE UNIQUE INDEX idx_quote_root_revision ON quotes(root_quote_id,revision)")
            self.db.execute("PRAGMA user_version=2")
            self._event("SCHEMA_MIGRATED", "owner", {"from":1,"to":2})
        self.verify_audit()
        return digest

    def approve_quote(self, quote_id: str, actor: str):
        actor = _text(actor, "actor", 80)
        with self._write():
            quote = self._fetch("quotes", quote_id)
            if quote["status"] != "DRAFT":
                raise DeskError("quote is not draft; duplicate approval rejected")
            if self.schema_version == 2 and self.db.execute(
                    "SELECT 1 FROM quotes WHERE root_quote_id=? AND revision>?",
                    (quote["root_quote_id"], quote["revision"])).fetchone():
                raise DeskError("cannot approve superseded quote revision")
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
        if integrity != "ok" or self.db.execute("PRAGMA foreign_key_check").fetchone():
            raise DeskError("SQLite integrity/foreign key check failed")
        return count

    def backup(self, destination: str | Path) -> str:
        dst = Path(destination)
        if (not dst.parent.is_dir() or dst.parent.is_symlink() or
                dst.exists() or dst.is_symlink() or dst.resolve() == self.path.resolve()):
            raise DeskError("backup target must be a new file in an existing non-symlink directory")
        self.verify_audit()
        # Never create customer backup using sqlite3's default OS mode: that can
        # inherit a permissive umask (e.g. 0644). Exclusively reserve mode 0600.
        # The existing file is NEVER modified, and errors remove only our own file.
        try:
            fd = os.open(dst, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            os.close(fd)
        except FileExistsError:
            raise DeskError("backup target already exists") from None
        except OSError as exc:
            raise DeskError("cannot create a private backup file") from exc
        # SQLite online backup retains a consistent snapshot even in WAL mode.
        try:
            with closing(sqlite3.connect(str(dst))) as out:
                self.db.backup(out)
                if out.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                    raise DeskError("backup failed integrity check")
            digest = hashlib.sha256(dst.read_bytes()).hexdigest()
            return digest
        except Exception:
            dst.unlink(missing_ok=True)
            raise


def restore_new(backup: str | Path, destination: str | Path, expected_sha256: str) -> dict:
    """Restore only into a NEW path, from a SHA-pinned local SQLite backup.

    Never overwrites original data or backup; rejects WAL sidecars and symlinks.
    """
    src, dst = Path(backup), Path(destination)
    if (not isinstance(expected_sha256, str) or len(expected_sha256)!=64 or
            any(ch not in "0123456789abcdef" for ch in expected_sha256.lower())):
        raise DeskError("expected SHA256 required")
    if not src.is_file() or src.is_symlink() or src.stat().st_size > 1024**3:
        raise DeskError("backup must be regular local file <= 1 GiB")
    if src.with_name(src.name+"-wal").exists() or src.with_name(src.name+"-shm").exists():
        raise DeskError("uncheckpointed backup WAL sidecar; refuse restore")
    if not dst.parent.is_dir() or dst.exists() or dst.is_symlink() or src.resolve()==dst.resolve():
        raise DeskError("restore target must be a new local path")
    if hashlib.sha256(src.read_bytes()).hexdigest()!=expected_sha256.lower():
        raise DeskError("backup SHA256 mismatch")
    # The backup API accepts SQLite only; a raw byte copy can propagate corrupt or unreadable data.
    tmp = None
    try:
        fd, tmp_name = tempfile.mkstemp(prefix=".worknova-restore-", suffix=".sqlite", dir=dst.parent)
        os.close(fd)
        tmp = Path(tmp_name)
        with closing(sqlite3.connect(src.resolve().as_uri()+"?mode=ro", uri=True)) as read_db:
            if read_db.execute("PRAGMA integrity_check").fetchone()[0]!="ok":
                raise DeskError("backup SQLite corruption")
            if read_db.execute("PRAGMA foreign_key_check").fetchone():
                raise DeskError("backup has invalid references")
            with closing(sqlite3.connect(str(tmp))) as write_db:
                read_db.backup(write_db)
                if write_db.execute("PRAGMA integrity_check").fetchone()[0]!="ok":
                    raise DeskError("restore corruption")
        test = Desk(tmp)
        try:
            events = test.verify_audit()
            schema = test.schema_version
        finally:
            test.close()
        # Hard-link atomically fails if the target appeared in the meantime (no overwrite).
        os.link(tmp, dst)
        return {"restored": True,"schema_version":schema,"verified_events":events}
    except (sqlite3.DatabaseError, OSError) as exc:
        raise DeskError("restore rejected: "+str(exc)) from exc
    finally:
        if tmp is not None: tmp.unlink(missing_ok=True)
