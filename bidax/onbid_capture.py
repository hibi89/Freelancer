"""User-authorized, bounded continuation of an already verified Onbid result-list.

No default network access. The caller's existing quarantined first page is the
only source for query parameters and the reported page count. New pages are
quarantined as create-only files before an offline integrity checkpoint.
Everything remains subject to official field/rights and human review.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from uuid import UUID

from .api_gateway import _safe_json_pairs, create_plan, fetch_quarantined
from .onbid_batch import MAX_PAGES, _packet, batch_status, stage_page

MAX_NEW_CALLS_PER_RUN = 25


def continue_onbid_pages(
    db_path: str | Path, batch_id: str, first_packet: str | Path,
    output_directory: str | Path, *, consent: bool, live: bool = False,
    service_key: str | None = None, max_new_pages: int = 4,
    daily_limit: int = 24, opener=None, now=None,
) -> dict:
    """Dry plan or explicitly fetch at most max_new_pages missing pages.

    A missing saved packet is never re-fetched under the same name. If power
    fails after an HTTP response was saved but before it was staged, the next
    run inspects that exact local file first. A malformed/cross-query file
    stops execution instead of consuming another call or overwriting evidence.
    """
    if consent is not True:
        raise PermissionError("explicit local file path/storage approval required")
    try:
        identity = str(UUID(batch_id))
    except (TypeError, AttributeError, ValueError):
        raise ValueError("batch ID must be a UUID") from None
    if type(max_new_pages) is not int or not 1 <= max_new_pages <= MAX_NEW_CALLS_PER_RUN:
        raise ValueError("max_new_pages must be 1..25")
    if type(daily_limit) is not int or not 1 <= daily_limit <= 1000:
        raise ValueError("daily_limit must be 1..1000")
    if type(live) is not bool:
        raise ValueError("live flag must be boolean")
    if live and (not isinstance(service_key, str) or not service_key.strip()):
        raise ValueError("live requests require a customer-owned in-memory service key")
    if not live and service_key is not None:
        raise ValueError("dry plan never accepts a credential")

    folder = Path(output_directory)
    if folder.is_symlink() or not folder.is_dir():
        raise ValueError("output must be an existing, non-symlink local directory")
    db = Path(db_path)
    if db.is_symlink() or not db.parent.is_dir():
        raise ValueError("unsafe database path")

    first = _packet(first_packet)
    if first["pages"] > MAX_PAGES:
        raise ValueError("unbounded reported page count")
    raw = Path(first_packet).read_bytes()
    if hashlib.sha256(raw).hexdigest() != first["packet_sha256"]:
        raise ValueError("first evidence file changed while inspecting")
    packet = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=_safe_json_pairs)
    params = packet["request_without_key"]
    filters = {key: value for key, value in params.items()
               if key not in ("pageNo", "numOfRows", "resultType")}

    # Existence and integrity are verified before every additional request.
    # In dry mode, do not create a DB, files, or ask for a service key.
    existing = None
    if db.is_file():
        try:
            existing = batch_status(db, identity)
        except KeyError:
            existing = None
    if existing is not None and (
        existing["reported_total_items"] != first["total"]
        or existing["page_size"] != first["page_size"]
        or existing["reported_total_pages"] != first["pages"]
    ):
        raise ValueError("existing batch conflicts with reference snapshot")
    verified = set(existing["verified_local_pages"]) if existing else set()
    if existing is not None and existing["sealed"]:
        return _summary(existing, 0, 0, False)
    if not live:
        missing = [p for p in range(1, first["pages"] + 1)
                   if p not in verified and p != first["page"]]
        return {
            "state": "OFFLINE_DRY_PLAN_NO_NETWORK",
            "reported_total_items": first["total"],
            "reported_total_pages": first["pages"],
            "reference_page": first["page"],
            "other_pages_missing_or_unverified": missing,
            "request_limit_for_next_explicit_run": max_new_pages,
            "network_calls": 0, "database_modified": False,
            "auto_import_allowed": False, "source_field_mapping_verified": False,
        }

    # Explicit opt-in to persist the existing reference. This may seal an
    # already complete one-page response and never calls any provider.
    state = stage_page(db, identity, first_packet, consent=True)
    if state["sealed"]:
        return _summary(state, 0, 0, True)
    new_calls = 0
    reused = 0
    for number in state["missing_pages"]:
        file = folder / f"bidax-onbid-{identity}-p{number:04d}.json"
        if file.is_symlink():
            raise ValueError("refuse linked local quarantine destination")
        if file.exists():
            # Crash recovery: validate and stage, never overwrite or re-fetch.
            state = stage_page(db, identity, file, consent=True)
            reused += 1
            continue
        if new_calls >= max_new_pages:
            break
        plan = create_plan("onbid_result_list", {
            "parameters": filters, "page": number, "rows": first["page_size"]})
        if plan.get("ready") is not True:
            raise ValueError("Onbid official operation is not verified")
        # Retry intentionally disabled. Daily counters include ALL attempted
        # calls. A 429/error stops rather than looping or silently spending.
        fetch_quarantined(
            plan, service_key=service_key, permission=True,
            db_path=db, output_path=file, daily_limit=daily_limit,
            max_attempts=1, opener=opener, now=now)
        new_calls += 1
        # If a provider changes totalCount/query/row shape, this raises and
        # preserves the quarantined file for human review (no auto-normalize).
        state = stage_page(db, identity, file, consent=True)
    return _summary(state, new_calls, reused, True)


def _summary(state: dict, new_calls: int, reused: int, live: bool) -> dict:
    return {
        "state": state["state"],
        "verified_local_pages": state["verified_local_pages"],
        "missing_pages": state["missing_pages"],
        "reported_total_items": state["reported_total_items"],
        "verified_local_item_count": state["verified_local_item_count"],
        "reported_total_pages": state["reported_total_pages"],
        "new_http_calls_this_run": new_calls,
        "existing_saved_packets_recovered": reused,
        "explicit_live": live,
        "auto_import_allowed": False,
        "source_field_mapping_verified": False,
        "legal_qualification_approved": False,
    }
