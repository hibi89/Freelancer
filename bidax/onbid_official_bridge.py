"""Fail-closed offline Onbid result-list inspection and detail-query candidate queue.

Requires an existing validated quarantined response; no key, HTTP, import, bid
submission, or automatic pagination. The detailed queue contains customer data
and MUST remain on the customer's machine.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re

from .api_gateway import _safe_json_pairs, create_plan
from .response_audit import MAX_PACKET_BYTES, _fingerprint, inspect_packet

# Names confirmed as query identifiers by data.go.kr 15157252/15157254.
# Other names are published query parameters; their output presence is NOT assumed.
_PUBLIC_FIELDS = (
    'cltrMngNo', 'pbctCdtnNo', 'onbidCltrNm', 'pbctStatCd',
    'prptDivCd', 'cltrTypeCd', 'lowstBidPrc', 'apslEvlAmt',
    'opbdDt', 'usbdNft', 'orgNm',
)
_ID = re.compile(r'^[A-Za-z0-9-]{1,80}$')


def _read_validated_page(filename: str | Path) -> tuple[dict, list[dict]]:
    """Validate full quarantine envelope before allowing access to raw rows."""
    status = inspect_packet(filename)
    if status['state'] != 'STRUCTURE_CANDIDATE_REVIEW_REQUIRED':
        raise ValueError('review hold: official Onbid response is not structurally accepted')
    if status['service'] != 'onbid_result_list' or status['dataset_id'] != 15157252:
        raise ValueError('requires Onbid official result-list packet only')
    if status['integrity'] != 'CANONICAL_RESPONSE_SHA256_MATCH':
        raise ValueError('legacy packet without saved response hash is not accepted')
    path = Path(filename)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_PACKET_BYTES:
        raise ValueError('untrusted local packet path')
    try:
        packet = json.loads(path.read_text(encoding='utf-8-sig'), object_pairs_hook=_safe_json_pairs)
    except (OSError, UnicodeError, ValueError):
        raise ValueError('invalid local packet') from None
    raw = packet.get('raw_response')
    if not isinstance(raw, dict) or packet.get('canonical_response_sha256') != _fingerprint(raw):
        raise ValueError('raw packet changed during offline inspection')
    envelope = raw.get('response', raw)
    if not isinstance(envelope, dict):
        raise ValueError('bad Onbid response envelope')
    body = envelope.get('body')
    if not isinstance(body, dict):
        raise ValueError('missing Onbid body')
    items = body.get('items')
    if isinstance(items, dict):
        items = items.get('item', [])
    if items is None:
        items = []
    if isinstance(items, dict):
        items = [items]
    if not isinstance(items, list) or not all(isinstance(item, dict) for item in items):
        raise ValueError('unexpected Onbid items')
    if len(items) != status['items_in_page']:
        raise ValueError('Onbid page changed during inspection')
    return status, items


def field_audit(filename: str | Path) -> dict:
    """Safe to paste the returned summary; NO values or unknown field names."""
    status, items = _read_validated_page(filename)
    presence = {key: sum(key in row and row[key] is not None for row in items)
                for key in _PUBLIC_FIELDS}
    ids = sum(_valid_id(row.get('cltrMngNo')) for row in items)
    both = sum(_valid_id(row.get('cltrMngNo')) and _valid_id(row.get('pbctCdtnNo'))
               for row in items)
    return {
        'state': 'LOCAL_FIELD_COVERAGE_REVIEW_REQUIRED',
        'dataset_id': 15157252,
        'inspected_page': status['page'], 'items_in_page': len(items),
        'reported_total_items': status['total_count_reported'],
        'known_public_field_presence_counts': presence,
        'unknown_field_names_disclosed': False,
        'items_with_valid_property_id': ids,
        'items_with_valid_property_and_condition_id': both,
        'unknown_fields_count': sum(len(set(row) - set(_PUBLIC_FIELDS)) for row in items),
        'source_field_mapping_verified': False,
        'detail_api_automatically_called': False,
        'auto_import_allowed': False,
        'legal_qualification_approved': False,
    }


def _valid_id(value: object) -> bool:
    return type(value) is str and _ID.fullmatch(value) is not None


def write_detail_candidate_queue(filename: str | Path, output: str | Path, *, consent: bool) -> dict:
    """Prepare LOCAL-only detail requests from documented identifiers.

    This is intentionally NOT bulk HTTP polling or an authorization to access
    the detail API. Refuse an incomplete page instead of silently skipping rows.
    """
    if consent is not True:
        raise PermissionError('explicit local identifier storage consent required')
    status, items = _read_validated_page(filename)
    if not items:
        raise ValueError('empty result list cannot produce candidate detail queue')
    requests = []
    seen = set()
    for row in items:
        property_id = row.get('cltrMngNo')
        condition_id = row.get('pbctCdtnNo')
        if not _valid_id(property_id):
            raise ValueError('property identifier missing or invalid; no partial queue')
        if condition_id is not None and not _valid_id(condition_id):
            raise ValueError('condition identifier invalid; no partial queue')
        identity = (property_id, condition_id or '')
        if identity in seen:
            raise ValueError('duplicate source identity; no partial queue')
        seen.add(identity)
        parameters = {'cltrMngNo': property_id}
        if condition_id:
            parameters['pbctCdtnNo'] = condition_id
        plan = create_plan('onbid_result_detail', {'parameters': parameters, 'page': 1, 'rows': 10})
        if plan.get('ready') is not True or plan['dataset_id'] != 15157254:
            raise ValueError('result-detail plan not independently verified')
        requests.append({'service': 'onbid_result_detail',
                         'dataset_id': 15157254, 'request_without_key': plan['parameters'],
                         'state': 'LOCAL_CANDIDATE_NOT_EXECUTED'})
    dest = Path(output)
    if dest.is_symlink() or dest.exists() or not dest.parent.is_dir():
        raise FileExistsError('must write a NEW file in existing local directory')
    contents = {
        'source': 'BIDAX_ONBID_DETAIL_CANDIDATE_QUEUE_LOCAL_ONLY',
        'created_at_utc': datetime.now(timezone.utc).isoformat(),
        'source_dataset_id': status['dataset_id'],
        'source_page': status['page'],
        'source_items_in_page': len(items),
        'total_reported_unverified': status['total_count_reported'],
        'requests': requests,
        'network_calls': 0, 'execution_authorized': False,
        'mapping_human_review_required': True,
        'legal_qualification_approved': False,
    }
    blob = (json.dumps(contents, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')
    fd = os.open(dest, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(blob)
            f.flush()
            os.fsync(f.fileno())
    except BaseException:
        dest.unlink(missing_ok=True)
        raise
    return {'state': 'LOCAL_CANDIDATE_QUEUE_CREATED_NOT_EXECUTED', 'requests_prepared': len(requests),
            'source_page': status['page'], 'saved': str(dest),
            'raw_identifiers_printed': False, 'network_calls': 0,
            'auto_import_allowed': False, 'detail_api_automatically_called': False}
