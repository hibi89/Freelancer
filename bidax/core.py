"""Offline, evidence-preserving public procurement bid screening. No HTTP calls."""
from __future__ import annotations

from contextlib import closing
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
from uuid import UUID
from urllib.parse import urlsplit

KST = timezone(timedelta(hours=9))
OFFICIAL_HOSTS = {"g2b.go.kr", "www.g2b.go.kr", "data.go.kr", "www.data.go.kr", "apis.data.go.kr", "pps.go.kr", "www.pps.go.kr"}
OPERATIONS = {
    "goods": "getBidPblancListInfoThng02",
    "services": "getBidPblancListInfoServc02",
    "construction": "getBidPblancListInfoCnstwk02",
    "foreign": "getBidPblancListInfoFrgcpt02",
}
DISCLAIMER = "자동 사전검토 결과이며 최종 입찰자격·법적 적합성·공고 최신성을 보장하지 않습니다. 원문과 담당자 확인이 필수입니다."


def _canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field}: non-empty string required")
    return value.strip()


def _strings(value: object, field: str) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(v, str) or not v.strip() for v in value):
        raise ValueError(f"{field}: list of non-empty strings required")
    return sorted(set(v.strip() for v in value))


def _when(value: object, field: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError(f"{field}: ISO8601 with offset required")
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field}: invalid ISO8601") from exc
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError(f"{field}: timezone offset required")
    return dt


def validate_notice(raw: object) -> dict:
    """Validate a normalized, licensed notice fixture; never infer missing clauses."""
    if not isinstance(raw, dict):
        raise ValueError("notice must be object")
    required = {"notice_no", "revision", "title", "category", "issuer", "deadline", "source_url", "regions", "license_codes", "required_documents"}
    unknown = set(raw) - (required | {"budget_min_krw", "published_at", "provenance_state", "unverified_clauses", "raw_snapshot_sha256"})
    missing = required - set(raw)
    if missing or unknown:
        raise ValueError(f"notice fields missing={sorted(missing)} unknown={sorted(unknown)}")
    result = {k: _text(raw[k], k) for k in ("notice_no", "revision", "title", "category", "issuer", "source_url")}
    if result["category"] not in OPERATIONS:
        raise ValueError("unsupported category")
    parsed = urlsplit(result["source_url"])
    if parsed.scheme != "https" or parsed.hostname not in OFFICIAL_HOSTS or parsed.username or parsed.password:
        raise ValueError("source_url must reference an allowed official HTTPS host")
    result["deadline"] = _when(raw["deadline"], "deadline").isoformat()
    result["regions"] = _strings(raw["regions"], "regions")
    result["license_codes"] = _strings(raw["license_codes"], "license_codes")
    result["required_documents"] = _strings(raw["required_documents"], "required_documents")
    if "published_at" in raw:
        result["published_at"] = _when(raw["published_at"], "published_at").isoformat()
    if "budget_min_krw" in raw:
        b = raw["budget_min_krw"]
        if type(b) is not int or b < 0:
            raise ValueError("budget_min_krw must be nonnegative integer")
        result["budget_min_krw"] = b
    if "provenance_state" in raw:
        if raw["provenance_state"] not in {"OFFICIAL_SNAPSHOT_UNVERIFIED", "OFFLINE_NORMALIZED"}:
            raise ValueError("unsupported provenance_state")
        result["provenance_state"] = raw["provenance_state"]
    if "unverified_clauses" in raw:
        result["unverified_clauses"] = _strings(raw["unverified_clauses"], "unverified_clauses")
    if "raw_snapshot_sha256" in raw:
        value = raw["raw_snapshot_sha256"]
        if not isinstance(value, str) or len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
            raise ValueError("raw_snapshot_sha256 must be lowercase SHA256")
        result["raw_snapshot_sha256"] = value
    return result


def validate_profile(raw: object) -> dict:
    if not isinstance(raw, dict):
        raise ValueError("profile must be object")
    required = {"company", "regions", "license_codes", "documents"}
    missing = required - set(raw)
    unknown = set(raw) - (required | {"max_budget_krw"})
    if missing or unknown:
        raise ValueError(f"profile fields missing={sorted(missing)} unknown={sorted(unknown)}")
    result = {"company": _text(raw["company"], "company"), "regions": _strings(raw["regions"], "regions"), "license_codes": _strings(raw["license_codes"], "license_codes")}
    docs = raw["documents"]
    if not isinstance(docs, dict):
        raise ValueError("documents must be map of document name to ISO date")
    clean_docs = {}
    for name, expiration in docs.items():
        name = _text(name, "document name")
        if not isinstance(expiration, str):
            raise ValueError("document expiry must be ISO date")
        try:
            clean_docs[name] = date.fromisoformat(expiration).isoformat()
        except ValueError as exc:
            raise ValueError("document expiry must be ISO date") from exc
    result["documents"] = clean_docs
    if "max_budget_krw" in raw:
        b = raw["max_budget_krw"]
        if type(b) is not int or b < 0:
            raise ValueError("max_budget_krw must be nonnegative integer")
        result["max_budget_krw"] = b
    return result


def official_query(kind: str, start: datetime, end: datetime, page: int = 1, size: int = 100) -> dict:
    """Return a request *plan* only; caller supplies own key and performs any approved HTTP."""
    if kind not in OPERATIONS:
        raise ValueError("unsupported kind")
    if start.tzinfo is None or end.tzinfo is None:
        raise ValueError("timezone-aware range required")
    if not start < end or end - start > timedelta(days=7):
        raise ValueError("official API maximum query window is 7 days")
    if type(page) is not int or type(size) is not int or page < 1 or not 1 <= size <= 100:
        raise ValueError("invalid page/size")
    return {"base_url": "https://apis.data.go.kr/1230000/ad/BidPublicInfoService02/" + OPERATIONS[kind], "params_without_service_key": {"pageNo": page, "numOfRows": size, "inqryDiv": "1", "type": "json", "inqryBgnDt": start.astimezone(KST).strftime("%Y%m%d%H%M"), "inqryEndDt": end.astimezone(KST).strftime("%Y%m%d%H%M")}}


class BidLedger:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.conn = sqlite3.connect(self.path)
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.conn.execute("PRAGMA busy_timeout=5000")
        self.conn.execute("PRAGMA synchronous=FULL")
        self.conn.execute("CREATE TABLE IF NOT EXISTS notice_events (id INTEGER PRIMARY KEY, notice_no TEXT NOT NULL, revision TEXT NOT NULL, fingerprint TEXT NOT NULL, payload TEXT NOT NULL, observed_at TEXT NOT NULL, UNIQUE(notice_no, revision, fingerprint))")
        self.conn.execute("CREATE INDEX IF NOT EXISTS notice_events_lookup ON notice_events(notice_no,id DESC)")
        self.conn.execute("CREATE TABLE IF NOT EXISTS manual_reviews (id INTEGER PRIMARY KEY, notice_no TEXT NOT NULL, fingerprint TEXT NOT NULL, reviewer TEXT NOT NULL, decision TEXT NOT NULL, note TEXT NOT NULL, reviewed_at TEXT NOT NULL, request_id TEXT NOT NULL UNIQUE)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS manual_reviews_lookup ON manual_reviews(notice_no,id DESC)")
        self.conn.execute("CREATE TABLE IF NOT EXISTS profile_events (id INTEGER PRIMARY KEY, company TEXT NOT NULL, fingerprint TEXT NOT NULL, payload TEXT NOT NULL, saved_at TEXT NOT NULL, UNIQUE(company, fingerprint))")
        self.conn.execute("CREATE INDEX IF NOT EXISTS profile_events_lookup ON profile_events(company,id DESC)")
        self.conn.commit()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.conn.close()

    def ingest(self, notices: object, observed_at: datetime | None = None) -> dict:
        if not isinstance(notices, list):
            raise ValueError("notices must be JSON list")
        validated = [validate_notice(n) for n in notices]  # all-or-nothing preflight
        observed = (observed_at or datetime.now(KST)).astimezone(KST).isoformat()
        added = 0
        with self.conn:
            for record in validated:
                payload = _canonical(record)
                fp = hashlib.sha256(payload.encode("utf-8")).hexdigest()
                cursor = self.conn.execute("INSERT OR IGNORE INTO notice_events(notice_no,revision,fingerprint,payload,observed_at) VALUES(?,?,?,?,?)", (record["notice_no"], record["revision"], fp, payload, observed))
                added += cursor.rowcount
        return {"received": len(validated), "added_versions": added, "unchanged": len(validated) - added}

    def verify_integrity(self) -> None:
        """Fail closed if SQLite, stored payload hashes, or stored field contracts disagree."""
        result = self.conn.execute("PRAGMA quick_check").fetchone()
        if not result or result[0] != "ok":
            raise ValueError("SQLite integrity check failed")
        for payload, fingerprint in self.conn.execute("SELECT payload, fingerprint FROM profile_events"):
            if hashlib.sha256(payload.encode("utf-8")).hexdigest() != fingerprint:
                raise ValueError("Profile fingerprint mismatch; restore verified backup")
            try:
                if validate_profile(json.loads(payload)) != json.loads(payload):
                    raise ValueError("Invalid profile payload in ledger")
            except (TypeError, ValueError) as exc:
                raise ValueError("Invalid profile payload in ledger") from exc
        for payload, fingerprint in self.conn.execute("SELECT payload, fingerprint FROM notice_events"):
            if hashlib.sha256(payload.encode("utf-8")).hexdigest() != fingerprint:
                raise ValueError("Notice fingerprint mismatch; stop and restore verified backup")
            try:
                parsed = json.loads(payload)
                if validate_notice(parsed) != parsed:
                    raise ValueError("Notice contract mismatch")
            except (TypeError, ValueError) as exc:
                raise ValueError("Invalid notice payload in ledger") from exc

    def save_profile(self, raw: object, saved_at: datetime | None = None) -> dict:
        """Append changed customer profile versions; no secret material is required."""
        checked = validate_profile(raw)
        payload = _canonical(checked)
        fingerprint = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        moment = saved_at or datetime.now(KST)
        if moment.tzinfo is None or moment.utcoffset() is None:
            raise ValueError("saved_at needs timezone offset")
        self.verify_integrity()
        with self.conn:
            cursor = self.conn.execute(
                "INSERT OR IGNORE INTO profile_events(company,fingerprint,payload,saved_at) VALUES(?,?,?,?)",
                (checked["company"], fingerprint, payload, moment.astimezone(KST).isoformat()))
        return {"company": checked["company"], "fingerprint": fingerprint,
                "new_version": bool(cursor.rowcount), "local_only": True}

    def list_profiles(self) -> list[dict]:
        self.verify_integrity()
        rows = self.conn.execute(
            "SELECT p.company,p.fingerprint,p.saved_at FROM profile_events p "
            "WHERE p.id=(SELECT MAX(q.id) FROM profile_events q WHERE q.company=p.company) "
            "ORDER BY p.company").fetchall()
        return [dict(zip(("company", "fingerprint", "saved_at"), row)) for row in rows]

    def get_profile(self, company: str) -> dict:
        self.verify_integrity()
        row = self.conn.execute(
            "SELECT payload FROM profile_events WHERE company=? ORDER BY id DESC LIMIT 1",
            (_text(company, "company"),)).fetchone()
        if row is None:
            raise KeyError("stored company profile not found")
        return json.loads(row[0])

    def profile_history(self, company: str) -> list[dict]:
        self.verify_integrity()
        rows = self.conn.execute(
            "SELECT fingerprint,saved_at FROM profile_events WHERE company=? ORDER BY id",
            (_text(company, "company"),)).fetchall()
        return [dict(zip(("fingerprint", "saved_at"), row)) for row in rows]

    def current(self) -> list[dict]:
        self.verify_integrity()
        rows = self.conn.execute("SELECT e.payload,e.fingerprint,e.observed_at FROM notice_events e WHERE e.id = (SELECT MAX(i.id) FROM notice_events i WHERE i.notice_no=e.notice_no) ORDER BY e.notice_no").fetchall()
        return [dict(json.loads(payload), fingerprint=fingerprint, observed_at=observed) for payload, fingerprint, observed in rows]

    def changes(self, notice_no: str) -> list[dict]:
        """Field-level immutable revision trail; no overwriting the prior evidence."""
        self.verify_integrity()
        rows = self.conn.execute(
            "SELECT revision,fingerprint,observed_at,payload FROM notice_events WHERE notice_no=? ORDER BY id", (notice_no,)
        ).fetchall()
        previous = None
        changes = []
        for revision, fingerprint, observed_at, payload in rows:
            current = json.loads(payload)
            delta = {k: {"before": (previous or {}).get(k), "after": current.get(k)}
                     for k in sorted(set(current) | set(previous or {}))
                     if previous is None or (previous or {}).get(k) != current.get(k)}
            changes.append({"revision": revision, "fingerprint": fingerprint, "observed_at": observed_at,
                            "change_kind": "NEW" if previous is None else "REVISED",
                            "changed_fields": delta})
            previous = current
        return changes

    def record_review(self, notice_no: str, fingerprint: str, reviewer: str, decision: str,
                      note: str, *, request_id: str, now: datetime | None = None) -> dict:
        """Human-authored review; never implies legal qualification or automated approval."""
        notice_no = _text(notice_no, "notice_no")
        fingerprint = _text(fingerprint, "fingerprint")
        reviewer = _text(reviewer, "reviewer")
        note = _text(note, "note")
        if len(reviewer) > 100 or len(note) > 2000:
            raise ValueError("reviewer/note exceeds safe length")
        if decision not in {"확인", "보류", "반려"}:
            raise ValueError("decision must be 확인/보류/반려")
        try:
            request_id = UUID(request_id).hex
        except (TypeError, ValueError, AttributeError) as exc:
            raise ValueError("valid UUID request_id required") from exc
        current = now or datetime.now(KST)
        if current.tzinfo is None or current.utcoffset() is None:
            raise ValueError("review time must be timezone-aware")
        self.verify_integrity()
        active = self.conn.execute(
            "SELECT fingerprint FROM notice_events WHERE notice_no=? ORDER BY id DESC LIMIT 1", (notice_no,)
        ).fetchone()
        if active is None or active[0] != fingerprint:
            raise ValueError("source version changed; review latest notice first")
        observed = current.astimezone(KST).isoformat()
        with self.conn:
            self.conn.execute(
                "INSERT OR IGNORE INTO manual_reviews(notice_no,fingerprint,reviewer,decision,note,reviewed_at,request_id) VALUES(?,?,?,?,?,?,?)",
                (notice_no, fingerprint, reviewer, decision, note, observed, request_id))
        row = self.conn.execute(
            "SELECT id,notice_no,fingerprint,reviewer,decision,note,reviewed_at FROM manual_reviews WHERE request_id=?",
            (request_id,)).fetchone()
        if row[1:6] != (notice_no, fingerprint, reviewer, decision, note):
            # Same idempotency key with different content cannot silently succeed.
            raise ValueError("request_id already used for different review")
        return dict(zip(("id", "notice_no", "fingerprint", "reviewer", "decision", "note", "reviewed_at"), row),
                    source_freshness="OFFLINE_NO_LEGAL_APPROVAL")

    def review_history(self, notice_no: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT id,notice_no,fingerprint,reviewer,decision,note,reviewed_at FROM manual_reviews WHERE notice_no=? ORDER BY id",
            (notice_no,)).fetchall()
        names = ("id", "notice_no", "fingerprint", "reviewer", "decision", "note", "reviewed_at")
        return [dict(zip(names, row)) for row in rows]

    def events(self, notice_no: str) -> list[dict]:
        rows = self.conn.execute("SELECT revision,fingerprint,observed_at FROM notice_events WHERE notice_no=? ORDER BY id", (notice_no,)).fetchall()
        return [{"revision": r, "fingerprint": fp, "observed_at": ts} for r, fp, ts in rows]

    def backup(self, target: str | Path):
        self.verify_integrity()
        target = Path(target)
        if target.resolve() == self.path.resolve():
            raise ValueError("backup target equals database")
        if target.exists():
            raise FileExistsError("backup target already exists; no overwrites")
        # Opened in exclusive creation mode to avoid clobbering existing customer data.
        with open(target, "xb"):
            pass
        try:
            with closing(sqlite3.connect(target)) as dest:
                self.conn.backup(dest)
        except Exception:
            target.unlink(missing_ok=True)
            raise


def evaluate(notice: dict, profile_raw: object, now: datetime | None = None) -> dict:
    profile = validate_profile(profile_raw)
    current = now or datetime.now(KST)
    if current.tzinfo is None:
        raise ValueError("now must have offset")
    failures, review, passed = [], [], []
    if _when(notice["deadline"], "deadline") <= current:
        failures.append("마감시간 경과")
    else:
        passed.append("마감시간 전")
    if not notice["regions"]:
        review.append("공고 지역제한 정보 미제공")
    elif not profile["regions"]:
        review.append("기업 지역정보 누락")
    elif "전국" in notice["regions"] or set(notice["regions"]) & set(profile["regions"]):
        passed.append("지역 일치")
    else:
        failures.append("공고 지역과 기업 지역 불일치")
    missing = sorted(set(notice["license_codes"]) - set(profile["license_codes"]))
    if missing:
        review.append("면허/업종 등록 검토 필요: " + ", ".join(missing))
    elif notice["license_codes"]:
        passed.append("프로필에 기재된 면허코드 일치(원본 증빙 확인 필요)")
    else:
        review.append("공고 면허제한 데이터 미제공")
    min_budget = notice.get("budget_min_krw")
    max_budget = profile.get("max_budget_krw")
    if min_budget is None or max_budget is None:
        review.append("금액 정보 일부 미제공")
    elif min_budget > max_budget:
        failures.append("기업 설정 예산 상한 미충족")
    else:
        passed.append("사용자 설정 예산 범위")
    for doc in notice["required_documents"]:
        expiry = profile["documents"].get(doc)
        if expiry is None:
            review.append(f"필수서류 미등록: {doc}")
        elif date.fromisoformat(expiry) < current.astimezone(KST).date():
            review.append(f"필수서류 만료: {doc}")
        else:
            passed.append(f"서류 유효기간 확인: {doc}")
    if not notice["required_documents"]:
        review.append("필수서류 원문 확인 필요")
    if notice.get("provenance_state") == "OFFICIAL_SNAPSHOT_UNVERIFIED":
        review.append("공식 API 응답의 자격조건/첨부 원문 대조 미완료")
    review.extend("추가 확인 필요: " + clause for clause in notice.get("unverified_clauses", []))
    label = "부적합" if failures else "추가 확인 필요" if review else "적합"
    return {"notice_no": notice["notice_no"], "title": notice["title"], "revision": notice["revision"], "company": profile["company"], "status": label, "deterministic_mismatch": failures, "needs_review": review, "matched": passed, "deadline": notice["deadline"], "source_url": notice["source_url"], "source_fingerprint": notice.get("fingerprint"), "disclaimer": DISCLAIMER}


def restore_backup(source: str | Path, target: str | Path) -> dict:
    """Validate source and restore into a *new* SQLite file (never overwrite)."""
    source, target = Path(source), Path(target)
    if not source.is_file():
        raise FileNotFoundError("backup source not found")
    if source.resolve() == target.resolve():
        raise ValueError("cannot restore backup over itself")
    # URI mode=ro prevents source creation, side effects, and accidental rewrites.
    with closing(sqlite3.connect(source.resolve().as_uri() + "?mode=ro", uri=True)) as src:
        if src.execute("PRAGMA quick_check").fetchone()[0] != "ok":
            raise ValueError("invalid SQLite backup")
        has_events = src.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='notice_events'"
        ).fetchone()
        if not has_events:
            raise ValueError("not a BID AX ledger backup")
        try:
            with target.open("xb"):
                pass
        except FileExistsError:
            raise FileExistsError("restore target exists; original data preserved")
        try:
            with closing(sqlite3.connect(target)) as dest:
                src.backup(dest)
            with BidLedger(target) as restored:
                restored.verify_integrity()
                count = len(restored.current())
        except Exception:
            target.unlink(missing_ok=True)
            raise
    return {"restored_to_new_file": str(target), "current_notices": count, "original_preserved": True}
