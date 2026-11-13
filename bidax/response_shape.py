"""Offline, bounded structural diagnosis of a quarantined API packet.

Only public schema field *names*, container kinds, and coarse status categories
are returned. No government record fields or values, keys, URLs, identifiers,
result messages, or original data are printed. Never performs HTTP.
"""
from __future__ import annotations

from pathlib import Path

from .response_audit import inspect_packet, _fingerprint, MAX_PACKET_BYTES, _has_sensitive_key
from .api_gateway import _safe_json_pairs
import json

# Output labels are fixed here; caller-supplied key names are never echoed.
_FIELDS = (
    "response", "header", "body", "resultCode", "resultMsg", "code",
    "status", "error", "errors", "data", "result", "results", "items",
    "item", "list", "content", "pagination", "pageNo", "numOfRows",
    "totalCount", "TotalCount", "count", "page", "size",
    "getCltrBidRsltList2", "getCltrBidRsltDtl2", "output", "headerInfo"
)


def _kind(value: object) -> str:
    if isinstance(value, dict): return "object"
    if isinstance(value, list): return "array"
    if value is None: return "null"
    if isinstance(value, bool): return "boolean"
    if isinstance(value, (int, float)): return "number"
    return "string" if isinstance(value, str) else "other"


def _status_class(value: object) -> str:
    # No raw status codes or server error messages are printed, even if they are
    # unexpectedly long or contain personal data / an echoed credential.
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        return "UNUSUAL_TYPE"
    string = str(value)
    if string in ("0", "00", "0000"):
        return "SUCCESS_CODE_CANDIDATE"
    if len(string) <= 6 and string.isascii() and string.isalnum():
        return "NON_SUCCESS_OR_UNRECOGNIZED_CODE"
    return "UNUSUAL_CODE_REDACTED"


def _shape(node: object) -> dict:
    if isinstance(node, dict):
        known = [key for key in _FIELDS if key in node]
        return {"kind": "object", "known_keys": known,
                "other_key_count": max(0, len(node) - len(known))}
    if isinstance(node, list):
        return {"kind": "array", "elements": len(node)}
    return {"kind": _kind(node)}


def diagnose_packet(filename: str | Path) -> dict:
    """Read one LOCAL quarantined packet and print schema-only observations.

    Calls the full restrictive inspector first to recheck service, request,
    dataset, sensitive fields, and canonical digest. May diagnose an unfamiliar
    shape but never upgrades its approval or imports records.
    """
    result = inspect_packet(filename)
    path = Path(filename)
    if path.stat().st_size > MAX_PACKET_BYTES or path.is_symlink():
        raise ValueError("unsafe packet")
    try:
        packet = json.loads(path.read_text(encoding="utf-8-sig"),
                            object_pairs_hook=_safe_json_pairs)
        raw = packet["raw_response"]
        if not isinstance(raw, dict) or _has_sensitive_key(raw):
            raise ValueError("invalid response object")
        canonical = packet.get("canonical_response_sha256")
        if canonical is not None and canonical != _fingerprint(raw):
            raise ValueError("response integrity check failed")
    except (OSError, UnicodeError, ValueError, KeyError, TypeError):
        raise ValueError("cannot safely diagnose quarantined packet") from None

    nodes = [{"path": "$", **_shape(raw)}]
    # Only fixed public schema labels may appear in output. Never traverse item
    # records or print content, even as truncated samples.
    for key in ("response", "header", "body", "data", "result", "results",
                "items", "output", "getCltrBidRsltList2"):
        if key in raw:
            val = raw[key]
            nodes.append({"path": key, **_shape(val)})
            if isinstance(val, dict):
                for key2 in ("header", "body", "items", "item", "data", "result", "results"):
                    if key2 in val:
                        nodes.append({"path": key + "." + key2, **_shape(val[key2])})
    states = []
    for pathlabel, obj in [("$", raw)] + [(str(n['path']), raw[n['path']]) for n in nodes[1:]
                                     if '.' not in str(n['path']) and isinstance(raw.get(n['path']), dict)]:
        if isinstance(obj, dict):
            for code_name in ("resultCode", "code"):
                if code_name in obj:
                    states.append({"path": pathlabel + "." + code_name,
                                   "class": _status_class(obj[code_name])})
            if isinstance(obj.get("header"), dict):
                header = obj["header"]
                for code_name in ("resultCode", "code"):
                    if code_name in header:
                        states.append({"path": pathlabel + ".header." + code_name,
                                       "class": _status_class(header[code_name])})
    return {"service": result["service"], "dataset_id": result["dataset_id"],
            "diagnostic": "OFFLINE_PUBLIC_SCHEMA_NAMES_ONLY", "inspection_state": result["state"],
            "inspection_reason": result.get("reason", "NONE"),
            "integrity": result["integrity"], "nodes": nodes[:20], "status_classes": states[:8],
            "raw_values_disclosed": False, "auto_import_allowed": False,
            "legal_qualification_approved": False}
