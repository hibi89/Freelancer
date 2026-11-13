"""Offline, evidence-preserving public procurement bid screening. No HTTP calls."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
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
    unknown = set(raw) - (required | {"budget_min_krw", "published_at"})
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
        self.conn.execute("CREATE TABLE IF NOT EXISTS notice_events (id INTEGER PRIMARY KEY, notice_no TEXT NOT NULL, revision TEXT NOT NULL, fingerprint TEXT NOT NULL, payload TEXT NOT NULL, observed_at TEXT NOT NULL, UNIQUE(notice_no, revision, fingerprint))")
        self.conn.execute("CREATE INDEX IF NOT EXISTS notice_events_lookup ON notice_events(notice_no,id DESC)")
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

    def current(self) -> list[dict]:
        rows = self.conn.execute("SELECT e.payload,e.fingerprint,e.observed_at FROM notice_events e WHERE e.id = (SELECT MAX(i.id) FROM notice_events i WHERE i.notice_no=e.notice_no) ORDER BY e.notice_no").fetchall()
        return [dict(json.loads(payload), fingerprint=fingerprint, observed_at=observed) for payload, fingerprint, observed in rows]

    def events(self, notice_no: str) -> list[dict]:
        rows = self.conn.execute("SELECT revision,fingerprint,observed_at FROM notice_events WHERE notice_no=? ORDER BY id", (notice_no,)).fetchall()
        return [{"revision": r, "fingerprint": fp, "observed_at": ts} for r, fp, ts in rows]

    def backup(self, target: str | Path):
        target = Path(target)
        if target.resolve() == self.path.resolve():
            raise ValueError("backup target equals database")
        if target.exists():
            raise FileExistsError("backup target already exists; no overwrites")
        # Opened in exclusive creation mode to avoid clobbering existing customer data.
        with open(target, "xb"):
            pass
        try:
            with sqlite3.connect(target) as dest:
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
    label = "부적합" if failures else "추가 확인 필요" if review else "적합"
    return {"notice_no": notice["notice_no"], "revision": notice["revision"], "company": profile["company"], "status": label, "deterministic_mismatch": failures, "needs_review": review, "matched": passed, "deadline": notice["deadline"], "source_url": notice["source_url"], "source_fingerprint": notice.get("fingerprint"), "disclaimer": DISCLAIMER}
