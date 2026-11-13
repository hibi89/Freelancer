"""Offline, bounded, fail-closed structural review of quarantined official API replies.

Never promotes data to eligibility/auction ledgers, logs raw fields or sends HTTP.
A matching response envelope is *not* a verified government field contract.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .api_gateway import _safe_json_pairs, create_plan, _plan_to_inputs

MAX_PACKET_BYTES = 24 * 1024 * 1024


def _fingerprint(value: object) -> str:
    content = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(content).hexdigest()


def inspect_packet(filename: str | Path) -> dict:
    """Inspect one locally quarantined JSON file, returning metadata only.

    Structural PASS is NOT an official field mapping, commercial license,
    completeness, legal eligibility, or permission to auto-import.
    """
    path = Path(filename)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_PACKET_BYTES:
        raise ValueError("refuse missing, linked or oversized quarantine packet")
    try:
        packet = json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=_safe_json_pairs)
    except (UnicodeError, ValueError, OSError) as exc:
        raise ValueError("invalid quarantine JSON") from None
    if not isinstance(packet, dict) or packet.get("source") != "OFFICIAL_API_RAW_UNVERIFIED_MAPPING":
        raise ValueError("not a BID AX quarantined API packet")
    if packet.get("requires_human_contract_review") is not True:
        raise ValueError("human review gate missing")
    service = packet.get("service")
    params = packet.get("request_without_key")
    if not isinstance(service, str) or not isinstance(params, dict):
        raise ValueError("invalid source service/parameters")
    if any(str(k).lower() in ("servicekey", "authorization", "password") for k in params):
        raise ValueError("sensitive request field in quarantine")
    try:
        candidate = create_plan(service, _plan_to_inputs({"service": service, "parameters": params}))
    except (ValueError, TypeError, KeyError):
        raise ValueError("unrecognized or malformed service request") from None
    if candidate.get("ready") is not True or packet.get("dataset_id") != candidate.get("dataset_id") or params != candidate["parameters"]:
        raise ValueError("service, dataset or parameter contract mismatch")
    body_source = packet.get("raw_response")
    if not isinstance(body_source, dict):
        raise ValueError("missing response object")
    if _has_sensitive_key(body_source):
        raise ValueError("sensitive response field must not be inspected")
    canonical = packet.get("canonical_response_sha256")
    integrity = "LEGACY_HASH_NOT_STORED"
    if canonical is not None:
        if not isinstance(canonical, str) or len(canonical) != 64 or canonical != _fingerprint(body_source):
            raise ValueError("quarantined response changed after capture")
        integrity = "CANONICAL_RESPONSE_SHA256_MATCH"
    # Do not rely on source raw_sha256: JSON was parsed/re-serialized for local
    # storage, so it is not possible to recompute the original wire bytes.
    # G2B responses use {"response": {"header": ..., "body": ...}}.
    # The first independently observed Onbid result-list response instead has
    # {"header": ..., "body": ...} at the JSON root. Both share the same
    # conservative validation below. Mixed layouts are ambiguous and rejected.
    if "response" in body_source:
        if "header" in body_source or "body" in body_source:
            return _hold(service, packet["dataset_id"], integrity, "AMBIGUOUS_ENVELOPE")
        wrapper = body_source["response"]
    elif "header" in body_source and "body" in body_source:
        wrapper = body_source
    else:
        return _hold(service, packet["dataset_id"], integrity, "UNRECOGNIZED_ENVELOPE")
    if not isinstance(wrapper, dict):
        return _hold(service, packet["dataset_id"], integrity, "UNRECOGNIZED_ENVELOPE")
    header, body = wrapper.get("header"), wrapper.get("body")
    if not isinstance(header, dict) or str(header.get("resultCode", "")) not in ("00", "0", "0000"):
        return _hold(service, packet["dataset_id"], integrity, "RESPONSE_NOT_SUCCESS")
    if not isinstance(body, dict):
        return _hold(service, packet["dataset_id"], integrity, "BODY_MISSING")
    page = _bounded_int(body.get("pageNo"), 1, 100000)
    per_page = _bounded_int(body.get("numOfRows"), 1, 100)
    total = _bounded_int(body.get("totalCount"), 0, 10000000)
    expected_page = _bounded_int(params.get("pageNo"), 1, 100000)
    expected_rows = _bounded_int(params.get("numOfRows"), 1, 100)
    if None in (page, per_page, total, expected_page, expected_rows) or page != expected_page or per_page != expected_rows:
        return _hold(service, packet["dataset_id"], integrity, "PAGINATION_MISMATCH_OR_UNKNOWN")
    items = body.get("items", {})
    if items is None:
        items = {}
    if isinstance(items, dict):
        items = items.get("item", [])
    if items is None:
        items = []
    if isinstance(items, dict):
        items = [items]
    if not isinstance(items, list) or any(not isinstance(v, dict) for v in items):
        return _hold(service, packet["dataset_id"], integrity, "ITEMS_SHAPE_UNKNOWN")
    expected_count = max(0, min(per_page, total - (page - 1) * per_page))
    if (total > 0 and page > (total + per_page - 1) // per_page) or len(items) != expected_count:
        return _hold(service, packet["dataset_id"], integrity, "ITEM_COUNT_INCONSISTENT")
    return {"service": service, "dataset_id": packet["dataset_id"],
            "state": "STRUCTURE_CANDIDATE_REVIEW_REQUIRED", "integrity": integrity,
            "page": page, "page_size": per_page, "total_count_reported": total,
            "items_in_page": len(items), "pages_expected_reported": (total + per_page - 1) // per_page,
            "source_field_mapping_verified": False, "auto_import_allowed": False,
            "legal_qualification_approved": False,
            "note": "Only an offline structure check; independent real response/rights review required"}


def plan_remaining_pages(filename: str | Path) -> dict:
    """OFFLINE bounded metadata-only continuation plan for a single saved page.

    This does not assume any other page was fetched, does not reveal records,
    and NEVER produces HTTP requests or authorizes bulk collection.
    """
    result = inspect_packet(filename)
    if result["state"] != "STRUCTURE_CANDIDATE_REVIEW_REQUIRED":
        return {"state": "REVIEW_HOLD", "reason": result.get("reason", "UNVERIFIED_RESPONSE"),
                "auto_fetch_allowed": False}
    page = result["page"]
    pages = result["pages_expected_reported"]
    return {
        "state": "OFFLINE_PAGE_PLAN_ONLY", "service": result["service"],
        "dataset_id": result["dataset_id"], "inspected_page": page,
        "items_in_inspected_page": result["items_in_page"],
        "reported_total_items": result["total_count_reported"],
        "page_size": result["page_size"], "reported_total_pages": pages,
        "next_page_if_sequential": page + 1 if page < pages else None,
        "pages_after_inspected_page": max(0, pages - page),
        "other_pages_verified": False, "auto_fetch_allowed": False,
        "source_field_mapping_verified": False,
        "note": "No additional pages fetched. Counts reported by agency are unverified metadata."
    }


def _has_sensitive_key(root):
    if isinstance(root, dict):
        return any(str(k).lower() in ("servicekey", "authorization", "password", "x-api-key") or _has_sensitive_key(v) for k, v in root.items())
    if isinstance(root, list):
        return any(_has_sensitive_key(v) for v in root)
    return False


def _bounded_int(value, minimum, maximum):
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        return None
    try:
        number = int(value)
    except ValueError:
        return None
    return number if minimum <= number <= maximum and str(value).strip().lstrip("0") == str(number).lstrip("0") else None


def _hold(service, dataset, integrity, code):
    return {"service":service,"dataset_id":dataset,"state":"REVIEW_HOLD",
            "reason":code,"integrity":integrity,"source_field_mapping_verified":False,
            "auto_import_allowed":False,"legal_qualification_approved":False}
