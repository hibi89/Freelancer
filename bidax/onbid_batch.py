"""Offline, restart-safe Onbid result-list page evidence ledger.

Staging requires explicit consent. It stores only local paths, non-secret query
hashes, packet hashes and counts in SQLite, not asset records, API keys or raw
agency replies. It never contacts the network or promotes raw data to a bid,
auction or qualification ledger. Completed batches remain dependent on the
presence and integrity of every original quarantine file.
"""
from __future__ import annotations

from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import sqlite3
from uuid import UUID

from .api_gateway import _safe_json_pairs
from .onbid_official_bridge import _read_validated_page
from .response_audit import MAX_PACKET_BYTES, _fingerprint

MAX_PAGES = 1000


def _batch_id(value: str) -> str:
    try:
        return str(UUID(value))
    except (AttributeError, TypeError, ValueError):
        raise ValueError('batch ID must be a UUID') from None


def _packet(path: str | Path) -> dict:
    """Accept only an already structurally verified Onbid result-list page."""
    location = Path(path)
    if location.is_symlink() or not location.is_file() or not 0 < location.stat().st_size <= MAX_PACKET_BYTES:
        raise ValueError('untrusted or missing local quarantine file')
    status, rows = _read_validated_page(location)
    if status['service'] != 'onbid_result_list' or status['dataset_id'] != 15157252:
        raise ValueError('requires Onbid result-list packet')
    raw_bytes = location.read_bytes()
    if len(raw_bytes) > MAX_PACKET_BYTES:
        raise ValueError('quarantine file too large')
    # Recheck after reading: _read_validated_page already verified the envelope
    # and canonical response, but no caller-supplied page metadata is trusted.
    packet = json.loads(raw_bytes.decode('utf-8-sig'), object_pairs_hook=_safe_json_pairs)
    if (packet.get('source') != 'OFFICIAL_API_RAW_UNVERIFIED_MAPPING' or
            packet.get('service') != 'onbid_result_list' or
            packet.get('dataset_id') != 15157252 or
            packet.get('canonical_response_sha256') != _fingerprint(packet.get('raw_response'))):
        raise ValueError('quarantine packet changed during second inspection')
    params = packet.get('request_without_key')
    if not isinstance(params, dict):
        raise ValueError('missing request contract')
    if params.get('pageNo') != str(status['page']) or params.get('numOfRows') != str(status['page_size']):
        raise ValueError('request/page contract mismatch')
    canonical = json.dumps({k: v for k, v in params.items() if k != 'pageNo'},
                           ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)
    query_hash = hashlib.sha256(canonical.encode('utf-8')).hexdigest()
    expected_pages = max(1, math.ceil(status['total_count_reported'] / status['page_size']))
    if expected_pages > MAX_PAGES or status['page'] > expected_pages:
        raise ValueError('unsafe or out-of-range page count')
    return {
        'page': status['page'], 'page_size': status['page_size'],
        'total': status['total_count_reported'], 'pages': expected_pages,
        'items': len(rows), 'query_sha256': query_hash,
        'packet_sha256': hashlib.sha256(raw_bytes).hexdigest(),
        'canonical_sha256': packet['canonical_response_sha256'],
        'path': str(location.resolve(strict=True)),
    }


def _connect(db_path: str | Path):
    """Use an existing local parent; no arbitrary directory creation."""
    target = Path(db_path)
    if target.is_symlink() or not target.parent.is_dir():
        raise ValueError('unsafe database path')
    conn = sqlite3.connect(str(target), timeout=8)
    try:
        conn.execute('PRAGMA busy_timeout=8000')
        conn.execute('PRAGMA foreign_keys=ON')
        conn.execute('''CREATE TABLE IF NOT EXISTS onbid_stage_batches (
            batch_id TEXT PRIMARY KEY, query_sha256 TEXT NOT NULL,
            page_size INTEGER NOT NULL, total_count INTEGER NOT NULL,
            expected_pages INTEGER NOT NULL, sealed INTEGER NOT NULL DEFAULT 0,
            created_at_utc TEXT NOT NULL)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS onbid_stage_pages (
            batch_id TEXT NOT NULL REFERENCES onbid_stage_batches(batch_id),
            page_no INTEGER NOT NULL, packet_path TEXT NOT NULL,
            packet_sha256 TEXT NOT NULL, canonical_sha256 TEXT NOT NULL,
            items_count INTEGER NOT NULL, PRIMARY KEY(batch_id,page_no))''')
        conn.commit()
        return conn
    except BaseException:
        conn.close()
        raise


def _status(conn, identity: str) -> dict:
    metadata = conn.execute('''SELECT query_sha256,page_size,total_count,expected_pages,sealed
                              FROM onbid_stage_batches WHERE batch_id=?''', (identity,)).fetchone()
    if metadata is None:
        raise KeyError('unknown Onbid local batch')
    sha, size, total, pages, sealed = metadata
    received = conn.execute('''SELECT page_no,packet_path,packet_sha256,canonical_sha256,items_count
                               FROM onbid_stage_pages WHERE batch_id=? ORDER BY page_no''', (identity,)).fetchall()
    present = []
    total_items = 0
    for page, path, packet_sha, canonical, count in received:
        try:
            live = _packet(path)
        except (OSError, ValueError, KeyError, UnicodeError):
            raise ValueError('staged local Onbid evidence missing, modified or invalid') from None
        if (page != live['page'] or packet_sha != live['packet_sha256'] or
                canonical != live['canonical_sha256'] or count != live['items'] or
                sha != live['query_sha256'] or size != live['page_size'] or
                total != live['total'] or pages != live['pages']):
            raise ValueError('staged Onbid evidence changed or has inconsistent contract')
        present.append(page)
        total_items += count
    if present != sorted(set(present)) or any(page < 1 or page > pages for page in present):
        raise ValueError('invalid Onbid page ledger')
    missing = [number for number in range(1, pages + 1) if number not in set(present)]
    all_pages_verified = not missing and total_items == total
    if sealed and not all_pages_verified:
        raise ValueError('sealed Onbid evidence batch is incomplete')
    return {
        'batch_id': identity, 'state': 'OFFLINE_COMPLETE_NOT_IMPORTED' if sealed else 'OFFLINE_PARTIAL_NOT_IMPORTED',
        'dataset_id': 15157252, 'source': 'ONBID', 'page_size': size,
        'reported_total_items': total, 'reported_total_pages': pages,
        'verified_local_pages': present, 'missing_pages': missing,
        'verified_local_item_count': total_items,
        'all_local_pages_verified': all_pages_verified, 'sealed': bool(sealed),
        'network_calls': 0, 'raw_records_stored_in_sqlite': False,
        'auto_import_allowed': False, 'source_field_mapping_verified': False,
        'legal_qualification_approved': False,
    }


def batch_status(db_path: str | Path, batch_id: str) -> dict:
    """Read-only status; unlike staging, never creates a database or tables."""
    identity = _batch_id(batch_id)
    path = Path(db_path)
    if path.is_symlink() or not path.is_file():
        raise ValueError('no existing local Onbid evidence database')
    # SQLite mode=ro ensures status has no schema/table creation side effects.
    with closing(sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True, timeout=8)) as conn:
        try:
            return _status(conn, identity)
        except sqlite3.OperationalError:
            raise ValueError('local Onbid evidence ledger unavailable') from None


def stage_page(db_path: str | Path, batch_id: str, packet_file: str | Path, *, consent: bool) -> dict:
    """Stage one local official packet with transactional idempotency.

    After a crash on the last page a replay will recheck every saved packet and
    seal the batch. Never writes to the original JSON or calls the provider.
    """
    if consent is not True:
        raise PermissionError('explicit local evidence path storage consent required')
    identity = _batch_id(batch_id)
    page = _packet(packet_file)
    with closing(_connect(db_path)) as conn:
        with conn:
            conn.execute('INSERT OR IGNORE INTO onbid_stage_batches VALUES (?,?,?,?,?,?,?)',
                         (identity, page['query_sha256'], page['page_size'], page['total'],
                          page['pages'], 0, datetime.now(timezone.utc).isoformat()))
            row = conn.execute('''SELECT query_sha256,page_size,total_count,expected_pages,sealed
                                  FROM onbid_stage_batches WHERE batch_id=?''', (identity,)).fetchone()
            if row[:4] != (page['query_sha256'],page['page_size'],page['total'],page['pages']):
                raise ValueError('batch ID reused for changed filters, reported total or page size')
            prior = conn.execute('''SELECT packet_sha256,canonical_sha256,items_count,packet_path
                                    FROM onbid_stage_pages WHERE batch_id=? AND page_no=?''',
                                 (identity,page['page'])).fetchone()
            if prior is not None and prior != (page['packet_sha256'],page['canonical_sha256'],page['items'],page['path']):
                raise ValueError('page replay changed; start a new batch with original files preserved')
            if row[4] and prior is None:
                raise ValueError('cannot change a sealed evidence batch')
            if prior is None:
                conn.execute('''INSERT INTO onbid_stage_pages VALUES(?,?,?,?,?,?)''',
                             (identity,page['page'],page['path'],page['packet_sha256'],
                              page['canonical_sha256'],page['items']))
        outcome = _status(conn, identity)
        if outcome['all_local_pages_verified'] and not outcome['sealed']:
            with conn:
                conn.execute('UPDATE onbid_stage_batches SET sealed=1 WHERE batch_id=? AND sealed=0', (identity,))
            outcome = _status(conn, identity)
        return {**outcome, 'page_replayed': prior is not None}
