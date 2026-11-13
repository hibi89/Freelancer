"""Quarantine parser for user-supplied *offline* G2B JSON snapshots.

This is NOT an API client. Field mappings are provisional pending authorized
live-response contract tests. Every converted notice forces manual review.
"""
from __future__ import annotations

from datetime import datetime
import hashlib
import json
from .core import KST, OPERATIONS, _canonical, validate_notice


def _deadline(row: dict) -> str:
    raw = row.get("bidClseDt")
    time = row.get("bidClseTm")
    if not isinstance(raw, str):
        raise ValueError("bidClseDt missing: quarantine entire snapshot")
    # Official data may contain compact or ISO variants; do not assume a default time.
    if len(raw) == 12 and raw.isdigit():
        dt = datetime.strptime(raw, "%Y%m%d%H%M")
    elif len(raw) == 10 and raw[4] == "-" and raw[7] == "-" and isinstance(time, str):
        dt = datetime.strptime(raw + " " + time, "%Y-%m-%d %H:%M")
    elif len(raw) == 8 and raw.isdigit() and isinstance(time, str) and len(time) == 4 and time.isdigit():
        dt = datetime.strptime(raw + time, "%Y%m%d%H%M")
    else:
        raise ValueError("ambiguous official bid deadline; quarantine")
    return dt.replace(tzinfo=KST).isoformat()


def parse_official_snapshot(snapshot: object, category: str, obtained_at: datetime) -> dict:
    """Fail-closed, all-or-nothing parsing of an authorized local JSON fixture.

    Never uses empty eligibility lists to certify participation: explicitly
    marks unknown region, licenses, attachments and budget as human-only.
    """
    if category not in OPERATIONS:
        raise ValueError("unsupported official category")
    if obtained_at.tzinfo is None or obtained_at.utcoffset() is None:
        raise ValueError("obtained_at must include offset")
    if not isinstance(snapshot, dict) or not isinstance(snapshot.get("response"), dict):
        raise ValueError("response envelope missing")
    response = snapshot["response"]
    header = response.get("header")
    body = response.get("body")
    if not isinstance(header, dict) or str(header.get("resultCode")) != "00":
        raise ValueError("official response is not success: quarantine")
    if not isinstance(body, dict):
        raise ValueError("official body missing")
    count, page, page_size = (body.get(k) for k in ("totalCount", "pageNo", "numOfRows"))
    try:
        total, page_no, size = int(count), int(page), int(page_size)
    except (TypeError, ValueError) as exc:
        raise ValueError("official pagination metadata invalid") from exc
    if not (0 <= total <= 10_000_000 and page_no >= 1 and 1 <= size <= 100):
        raise ValueError("official pagination outside safety bounds")
    items = body.get("items")
    raw_items = items.get("item", []) if isinstance(items, dict) else [] if items in (None, "") else None
    if isinstance(raw_items, dict):
        raw_items = [raw_items]
    if not isinstance(raw_items, list) or len(raw_items) > size or any(not isinstance(x, dict) for x in raw_items):
        raise ValueError("official items invalid")
    if (total and not raw_items) or len(raw_items) > total:
        raise ValueError("official item count contradicts metadata")
    snapshot_hash = hashlib.sha256(_canonical(snapshot).encode("utf-8")).hexdigest()
    notices = []
    for row in raw_items:
        fields = ("bidNtceNo", "bidNtceOrd", "bidNtceNm", "ntceInsttNm", "bidNtceDtlUrl")
        if any(not isinstance(row.get(field), (str, int)) or not str(row[field]).strip() for field in fields):
            raise ValueError("official field missing; manual mapping required")
        raw = {
            "notice_no": str(row["bidNtceNo"]).strip(),
            "revision": str(row["bidNtceOrd"]).strip(),
            "title": str(row["bidNtceNm"]).strip(),
            "category": category,
            "issuer": str(row["ntceInsttNm"]).strip(),
            "deadline": _deadline(row),
            "source_url": str(row["bidNtceDtlUrl"]).strip(),
            "regions": [], "license_codes": [], "required_documents": [],
            "provenance_state": "OFFICIAL_SNAPSHOT_UNVERIFIED",
            "unverified_clauses": ["지역/면허/서류/예산 조건은 목록 응답만으로 확인 불가"],
            "raw_snapshot_sha256": snapshot_hash,
        }
        notices.append(validate_notice(raw))
    return {"snapshot_sha256": snapshot_hash, "obtained_at": obtained_at.astimezone(KST).isoformat(),
            "page_no": page_no, "page_size": size, "total_count": total,
            "notices": notices, "warning": "OFFLINE PROVISIONAL FIELD MAPPING; VERIFY ORIGINAL CONTRACT"}
