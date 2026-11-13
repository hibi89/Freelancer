"""Onbid OFFLINE evidence store. No network, no API credentials, no investment advice.

Accepts only a deliberately normalized, customer-authorized local JSON snapshot.
Official live response shape and operating permission remain unverified.
"""
from __future__ import annotations

from contextlib import closing
from datetime import datetime
import hashlib
import json
from pathlib import Path
import sqlite3
from urllib.parse import urlsplit

from .core import KST, _canonical, _text, _when

ALLOWED_HOSTS = frozenset({"www.onbid.co.kr", "onbid.co.kr", "www.data.go.kr", "data.go.kr", "apis.data.go.kr"})
DATASET_URLS = {
    "assets": "https://www.data.go.kr/data/15157220/openapi.do",
    "results": "https://www.data.go.kr/data/15157254/openapi.do",
}
STATUS_VALUES = frozenset({"낙찰", "유찰", "취소", "확인 필요"})
TYPES = frozenset({"부동산", "동산", "차량", "기타"})
MAX_ITEMS = 500
DISCLAIMER = "공매 데이터는 로컬로 가져온 미검증 사본입니다. 물건 상태·권리·부담·입찰 결과는 온비드 원문과 전문가 확인이 필요합니다. 투자·법적 적합성 보장 아님."


def _optional_id(v: object, label: str) -> str:
    if v is None:
        return ""
    s = _text(v, label)
    if len(s) > 120 or any(ord(c) < 32 for c in s):
        raise ValueError(f"{label}: invalid identifier")
    return s


def _price(v: object, label: str) -> int | None:
    if v is None:
        return None
    if type(v) is not int or v < 0 or v > 10**17:
        raise ValueError(f"{label}: integer KRW amount required")
    return v


def _url(v: object) -> str:
    u = _text(v, "source_url")
    parts = urlsplit(u)
    if (parts.scheme != "https" or parts.hostname not in ALLOWED_HOSTS
            or parts.username or parts.password or not parts.netloc or len(u) > 2048):
        raise ValueError("source_url must be official HTTPS without credentials")
    return u


def validate_record(raw: object, dataset: str) -> dict:
    if not isinstance(raw, dict) or dataset not in DATASET_URLS:
        raise ValueError("unsupported Onbid dataset/row")
    required = {"property_id", "condition_id", "source_url"}
    if dataset == "assets":
        required |= {"announcement_id", "title", "property_type", "appraised_krw", "minimum_bid_krw", "failed_rounds", "bid_start", "bid_end"}
    else:
        required |= {"result_status", "winning_bid_krw"}
    optional = {"remarks"}
    missing, extra = required-set(raw), set(raw)-(required|optional)
    if missing or extra:
        raise ValueError(f"onbid {dataset} fields missing={sorted(missing)} unknown={sorted(extra)}")
    row = {"property_id": _optional_id(raw["property_id"], "property_id"),
           "condition_id": _optional_id(raw["condition_id"], "condition_id"),
           "source_url": _url(raw["source_url"])}
    if not row["property_id"]:
        raise ValueError("property_id is required")
    if "remarks" in raw:
        row["remarks"] = _text(raw["remarks"], "remarks")[:400]
    if dataset == "assets":
        row["announcement_id"] = _optional_id(raw["announcement_id"], "announcement_id")
        if not row["announcement_id"]:
            raise ValueError("announcement_id required for asset")
        row["title"] = _text(raw["title"], "title")[:400]
        if raw["property_type"] not in TYPES:
            raise ValueError("unknown property_type")
        row["property_type"] = raw["property_type"]
        for key in ("appraised_krw", "minimum_bid_krw"):
            row[key] = _price(raw[key], key)
        failures = raw["failed_rounds"]
        if failures is not None and (type(failures) is not int or failures < 0 or failures > 1000):
            raise ValueError("failed_rounds invalid")
        row["failed_rounds"] = failures
        for key in ("bid_start", "bid_end"):
            row[key] = _when(raw[key], key).isoformat() if raw[key] is not None else None
        if row["bid_start"] and row["bid_end"] and _when(row["bid_start"], "bid_start") > _when(row["bid_end"], "bid_end"):
            raise ValueError("bid_start after bid_end")
    else:
        if raw["result_status"] not in STATUS_VALUES:
            raise ValueError("unknown bid result; do not guess from API code")
        row["result_status"] = raw["result_status"]
        row["winning_bid_krw"] = _price(raw["winning_bid_krw"], "winning_bid_krw")
        if row["result_status"] != "낙찰" and row["winning_bid_krw"] is not None:
            raise ValueError("winning bid conflicts with non-awarded result")
    return row


def validate_snapshot(snapshot: object) -> dict:
    """Strict own schema. Not the official data.go.kr raw response contract."""
    if not isinstance(snapshot, dict):
        raise ValueError("snapshot must be object")
    required = {"source", "dataset", "obtained_at", "records", "documentation_url"}
    missing, unknown = required-set(snapshot), set(snapshot)-required
    if missing or unknown:
        raise ValueError(f"snapshot fields missing={sorted(missing)} unknown={sorted(unknown)}")
    if snapshot["source"] != "ONBID_LOCAL_AUTHORIZED_SNAPSHOT":
        raise ValueError("source consent/normalization must be explicit")
    ds = snapshot["dataset"]
    if ds not in DATASET_URLS or snapshot["documentation_url"] != DATASET_URLS[ds]:
        raise ValueError("incorrect dataset provenance")
    obtained = _when(snapshot["obtained_at"], "obtained_at").astimezone(KST).isoformat()
    records = snapshot["records"]
    if not isinstance(records, list) or not 1 <= len(records) <= MAX_ITEMS:
        raise ValueError("records requires 1..500 rows")
    clean = [validate_record(r, ds) for r in records]
    keys = {(r["property_id"],r["condition_id"]) for r in clean}
    if len(keys) != len(clean):
        raise ValueError("duplicate property/condition in snapshot")
    return {"dataset": ds, "records": clean, "obtained_at": obtained,
            "snapshot_sha256": hashlib.sha256(_canonical(snapshot).encode("utf-8")).hexdigest(),
            "documentation_url": DATASET_URLS[ds]}


class OnbidStore:
    """Tables have ONBID-specific names; cannot collide with the G2B tender ledger."""
    def __init__(self, path: str | Path):
        self.conn = sqlite3.connect(Path(path))
        self.conn.execute("PRAGMA busy_timeout=5000")
        self.conn.execute("PRAGMA synchronous=FULL")
        self.conn.execute("""CREATE TABLE IF NOT EXISTS onbid_events
            (id INTEGER PRIMARY KEY, dataset TEXT NOT NULL, property_id TEXT NOT NULL,
             condition_id TEXT NOT NULL, fingerprint TEXT NOT NULL, payload TEXT NOT NULL,
             obtained_at TEXT NOT NULL, snapshot_sha256 TEXT NOT NULL,
             UNIQUE(dataset,property_id,condition_id,fingerprint))""")
        self.conn.execute("CREATE INDEX IF NOT EXISTS onbid_lookup ON onbid_events(dataset,property_id,condition_id,id DESC)")
        self.conn.commit()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.conn.close()

    def _verify(self) -> None:
        if self.conn.execute("PRAGMA quick_check").fetchone()[0] != "ok":
            raise ValueError("onbid SQLite integrity failed")
        for ds, prop, condition, fp, payload in self.conn.execute("SELECT dataset,property_id,condition_id,fingerprint,payload FROM onbid_events"):
            if hashlib.sha256(payload.encode("utf-8")).hexdigest() != fp:
                raise ValueError("onbid payload fingerprint mismatch")
            row = json.loads(payload)
            if row != validate_record(row, ds) or prop != row["property_id"] or condition != row["condition_id"]:
                raise ValueError("onbid row contract mismatch")

    def import_snapshot(self, snapshot: object) -> dict:
        parsed = validate_snapshot(snapshot)
        self._verify()
        inserted = 0
        with self.conn:
            for r in parsed["records"]:
                payload = _canonical(r)
                fp = hashlib.sha256(payload.encode("utf-8")).hexdigest()
                last = self.conn.execute(
                    "SELECT obtained_at, fingerprint FROM onbid_events WHERE dataset=? AND property_id=? AND condition_id=? ORDER BY id DESC LIMIT 1",
                    (parsed["dataset"], r["property_id"], r["condition_id"])).fetchone()
                if last and fp != last[1] and _when(parsed["obtained_at"], "obtained_at") < _when(last[0], "previous_observed_at"):
                    raise ValueError("stale Onbid snapshot cannot replace newer property/result")
                cur = self.conn.execute("INSERT OR IGNORE INTO onbid_events(dataset,property_id,condition_id,fingerprint,payload,obtained_at,snapshot_sha256) VALUES(?,?,?,?,?,?,?)",
                                        (parsed["dataset"],r["property_id"],r["condition_id"],fp,payload,parsed["obtained_at"],parsed["snapshot_sha256"]))
                inserted += cur.rowcount
        return {"dataset": parsed["dataset"], "received": len(parsed["records"]),
                "new_versions": inserted, "unchanged": len(parsed["records"])-inserted,
                "snapshot_sha256": parsed["snapshot_sha256"], "status": "OFFLINE_UNVERIFIED_ORIGINAL_REVIEW_REQUIRED"}

    def report(self) -> dict:
        self._verify()
        current: dict[tuple[str,str,str],dict] = {}
        for ds, prop, cond, payload, obtained, sha in self.conn.execute(
            "SELECT dataset,property_id,condition_id,payload,obtained_at,snapshot_sha256 FROM onbid_events ORDER BY id"):
            row = json.loads(payload)
            row["obtained_at"] = obtained
            row["snapshot_sha256"] = sha
            current[(ds,prop,cond)] = row
        assets=[]
        results={(prop,cond):row for (ds,prop,cond),row in current.items() if ds=="results"}
        for (ds,prop,cond),asset in current.items():
            if ds != "assets":
                continue
            item = dict(asset)
            outcome=results.get((prop,cond))
            item["result_status"] = outcome["result_status"] if outcome else "미확인"
            item["result_provenance_verified"] = False
            item["review_status"] = "추가 확인 필요"
            item["manual_checks"] = ["공매공고 원본", "등기·권리관계", "점유·명도", "세금·관리비", "최신 입찰상태"]
            assets.append(item)
        return {"source": "ONBID", "assets":sorted(assets,key=lambda r:(r["property_id"],r["condition_id"])),
                "orphan_result_count": sum(1 for ds,prop,cond in current if ds=="results" and ("assets",prop,cond) not in current),
                "disclaimer": DISCLAIMER, "online_checked": False, "legal_qualification_approved": False}
