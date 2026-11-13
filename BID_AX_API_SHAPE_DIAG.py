"""BID AX: safe offline envelope diagnosis of local/result_001.json.

Reads the already downloaded customer-owned packet, verifies its original BID AX
quarantine integrity, and prints only fixed *schema labels*, never records,
service keys, result messages or downloaded contents. No network calls.
"""
from __future__ import annotations

from pathlib import Path
import json

from bidax.response_audit import inspect_packet

_BASE = Path(__file__).resolve().parent
_FILE = _BASE / "local" / "result_001.json"
_ALLOW = (
    "response", "header", "body", "resultCode", "resultMsg", "data", "result",
    "results", "items", "item", "list", "pageNo", "numOfRows", "totalCount",
    "TotalCount", "status", "code", "error", "errors", "page", "content",
    "getCltrBidRsltList2", "output", "headerInfo",
)
_PATHS = ("response", "header", "body", "data", "result", "results", "items", "output", "getCltrBidRsltList2")


def _shape(v):
    if isinstance(v, dict):
        known = [k for k in _ALLOW if k in v]
        return {"kind": "object", "known_fields": known, "other_field_count": len(v) - len(known)}
    if isinstance(v, list):
        return {"kind": "array", "elements": len(v)}
    return {"kind": "scalar_or_null"}


def _code_class(v):
    # Never print a raw status message/code. Only a fixed category.
    if isinstance(v, str) and v in ("0", "00", "0000"):
        return "SUCCESS_CODE_CANDIDATE"
    if isinstance(v, (str, int)) and not isinstance(v, bool):
        return "OTHER_OR_ERROR_CODE"
    return "UNUSUAL_TYPE"


def run():
    if not _FILE.is_file() or _FILE.is_symlink():
        raise ValueError("local/result_001.json not found or linked")
    summary = inspect_packet(_FILE)  # original full source/digest check
    from bidax.api_gateway import _safe_json_pairs
    p = json.loads(_FILE.read_text(encoding="utf-8-sig"),object_pairs_hook=_safe_json_pairs)
    raw = p["raw_response"]
    nodes = [{"path": "$", **_shape(raw)}]
    status = []
    if isinstance(raw, dict):
        for k in _PATHS:
            if k in raw:
                nodes.append({"path": k, **_shape(raw[k])})
                if isinstance(raw[k], dict):
                    for k2 in ("header", "body", "data", "items", "result"):
                        if k2 in raw[k]:
                            nodes.append({"path": k+"."+k2,**_shape(raw[k][k2])})
        for parent, value in [("$", raw)]+[(k,raw[k]) for k in _PATHS if isinstance(raw.get(k),dict)]:
            if isinstance(value, dict):
                for k in ("resultCode", "code"):
                    if k in value:
                        status.append({"path":parent+"."+k,"category":_code_class(value[k])})
                h = value.get("header")
                if isinstance(h,dict):
                    for k in ("resultCode", "code"):
                        if k in h:
                            status.append({"path":parent+".header."+k,"category":_code_class(h[k])})
    print(json.dumps({"mode":"OFFLINE_SCHEMA_ONLY","service":summary["service"],
                      "state":summary["state"],"reason":summary.get("reason","NONE"),
                      "integrity":summary["integrity"],"nodes":nodes[:20],
                      "status_categories":status[:8],"raw_values_disclosed":False,
                      "auto_import_allowed":False},ensure_ascii=False,indent=2))

if __name__ == "__main__":
    try: run()
    except Exception:
        # Never print filesystem paths or exception contents: secrets may occur.
        print('{"state":"DIAGNOSIS_FAILED","raw_values_disclosed":false}')
        raise SystemExit(1)
