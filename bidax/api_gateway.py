"""Opt-in, key-in-memory public-data API probe; never auto-imports returned records.

BID AX can reuse ONE customer-owned portal service key across multiple
*separately authorized* services. Each service has its own endpoint, request
budget, diagnostic and output quarantine. Actual agency JSON mapping requires
inspection of authorized responses; this module makes no legal eligibility
assertions and does not silently issue network calls.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import ssl
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit, unquote_plus
from urllib.request import build_opener, HTTPRedirectHandler, HTTPSHandler, ProxyHandler, Request

from .core import KST, official_query
from .onbid_plan import build_plan

MAX_BYTES = 10 * 1024 * 1024
# Official portal Swagger paths confirmed, not inferred from naming convention.
_ONBID_OPERATIONS = {
    "result_list": "/getCltrBidRsltList2",
    "result_detail": "/getCltrBidRsltDtl2",
}
_G2B_CATEGORIES = {"goods", "services", "construction", "foreign"}


class _RejectRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("API redirects are not allowed")


def _safe_json_pairs(pairs):
    output = {}
    for k, v in pairs:
        if k in output:
            raise ValueError("duplicate JSON field")
        output[k] = v
    return output


def create_plan(service: str, inputs: dict) -> dict:
    """Pure metadata-backed plan with no key and NO network access."""
    if not isinstance(inputs, dict) or not isinstance(service, str):
        raise ValueError("invalid API request plan")
    if service.startswith("g2b_"):
        category = service[4:]
        if category not in _G2B_CATEGORIES:
            raise ValueError("unknown procurement service")
        if set(inputs) != {"start", "end", "page", "rows"}:
            raise ValueError("G2B needs start/end/page/rows")
        try:
            start = datetime.fromisoformat(inputs["start"])
            end = datetime.fromisoformat(inputs["end"])
        except (TypeError, ValueError):
            raise ValueError("invalid ISO date range") from None
        query = official_query(category, start, end, inputs["page"], inputs["rows"])
        endpoint = query["base_url"]
        params = query["params_without_service_key"]
        dataset = 15129394
    elif service.startswith("onbid_"):
        kind = service[6:]
        if set(inputs) != {"parameters", "page", "rows"}:
            raise ValueError("Onbid needs parameters/page/rows")
        plan = build_plan(kind, inputs["parameters"], page=inputs["page"], rows=inputs["rows"])
        dataset = plan["dataset_id"]
        params = plan["parameters"]
        if kind not in _ONBID_OPERATIONS:
            # Service 15157220's route not independently verified; preserve a
            # plan but prohibit every attempt to call it.
            return {"service": service, "dataset_id": dataset,
                    "parameters": params, "endpoint": None, "ready": False,
                    "reason": "official operation path unverified; no network call"}
        endpoint = plan["verified_api_base"] + _ONBID_OPERATIONS[kind]
    else:
        raise ValueError("unknown official dataset; arbitrary URLs forbidden")
    parts = urlsplit(endpoint)
    if parts.scheme != "https" or parts.hostname != "apis.data.go.kr" or parts.username or parts.password or parts.port or parts.query or parts.fragment:
        raise ValueError("untrusted API endpoint")
    if not (parts.path.startswith("/1230000/ad/BidPublicInfoService02/") or
            parts.path in ("/B010003/OnbidCltrBidRsltListSrvc2/getCltrBidRsltList2",
                           "/B010003/OnbidCltrBidRsltDtlSrvc2/getCltrBidRsltDtl2")):
        raise ValueError("unknown API operation")
    return {"service": service, "dataset_id": dataset, "endpoint": endpoint,
            "parameters": params, "ready": True,
            "note": "authorized live response mapping and commercial use remain unverified"}


def _reserve_attempt(db_path: str | Path, service: str, day: str, daily_limit: int) -> None:
    if type(daily_limit) is not int or not 1 <= daily_limit <= 1000:
        raise ValueError("daily_limit must be 1..1000")
    # Reserve *before* network, never roll back on failure; extra retries cost a
    # unit each. Independent counters per service, not a claim about provider quota.
    conn = sqlite3.connect(db_path, timeout=5)
    try:
        with conn:
            conn.execute("CREATE TABLE IF NOT EXISTS api_gateway_attempts (service TEXT NOT NULL, day TEXT NOT NULL, count INTEGER NOT NULL, PRIMARY KEY(service,day))")
            conn.execute("INSERT OR IGNORE INTO api_gateway_attempts VALUES(?,?,0)", (service, day))
            updated = conn.execute("UPDATE api_gateway_attempts SET count=count+1 WHERE service=? AND day=? AND count<?", (service,day,daily_limit))
            if updated.rowcount != 1:
                raise ValueError("local request budget exhausted; provider quota not checked")
    finally:
        conn.close()


def fetch_quarantined(plan: dict, *, service_key: str, permission: bool, db_path: str | Path,
                     output_path: str | Path, daily_limit: int = 8, opener=None,
                     sleep=time.sleep, now=None, max_attempts: int = 2) -> dict:
    """Fetch one page ONLY after explicit consent, save raw JSON to new local file.

    No raw payload/credential is displayed or imported into eligibility engines.
    Returns safe file metadata, never the request URL, serviceKey or body.
    Opener is injectable for no-network unit tests.
    """
    if permission is not True:
        raise PermissionError("explicit live API approval required")
    if not isinstance(plan, dict) or plan.get("ready") is not True:
        raise ValueError("service operation not independently verified")
    expected = create_plan(plan.get("service"),
                           _plan_to_inputs(plan))
    if plan != expected:
        raise ValueError("modified API plan rejected")
    if not isinstance(service_key, str) or not 1 <= len(service_key.strip()) <= 4096:
        raise ValueError("customer service key required")
    if type(max_attempts) is not int or not 1 <= max_attempts <= 3:
        raise ValueError("invalid retry count")
    dest = Path(output_path)
    if dest.exists() or not dest.parent.is_dir():
        raise FileExistsError("quarantine destination must be a NEW file in an existing directory")
    # Do not accept caller-supplied arbitrary host, URL or extra parameters.
    query = dict(plan["parameters"])
    query["serviceKey"] = service_key.strip()
    url = plan["endpoint"] + "?" + urlencode(query)
    # Bypass environment proxies; use platform CA and forbid all redirects.
    transport = opener if opener is not None else build_opener(ProxyHandler({}), HTTPSHandler(context=ssl.create_default_context()), _RejectRedirect())
    for attempt in range(max_attempts):
        current = now() if callable(now) else (now if now is not None else datetime.now(timezone.utc))
        if not isinstance(current, datetime) or current.tzinfo is None or current.utcoffset() is None:
            raise ValueError("aware time required")
        _reserve_attempt(db_path, plan["service"], current.astimezone(KST).date().isoformat(), daily_limit)
        try:
            response = transport.open(Request(url, headers={"Accept":"application/json","User-Agent":"BIDAX-explicit-probe/1"}, method="GET"), timeout=15)
            with response:
                if getattr(response, "status", 200) != 200:
                    raise ValueError("unexpected HTTP status")
                content_type = response.headers.get("Content-Type", "")
                if "json" not in content_type.lower():
                    raise ValueError("API returned non-JSON content; quarantined")
                raw = response.read(MAX_BYTES+1)
            if len(raw) > MAX_BYTES:
                raise ValueError("API response larger than allowed")
            if service_key.strip().encode("utf-8") in raw:
                raise ValueError("agency response reflected credential; refuse persistence")
            data = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=_safe_json_pairs)
            if not isinstance(data, dict):
                raise ValueError("API response is not an object")
            # Detect escaped/URL-encoded reflection as well as literal bytes.
            decoded = json.dumps(data, ensure_ascii=False, sort_keys=True)
            if (service_key.strip() in decoded or service_key.strip() in unquote_plus(decoded)
                    or _contains_sensitive_response_key(data)):
                raise ValueError("agency response reflected credential; refuse persistence")
            # Error envelopes must never count as successful official evidence.
            header = data.get("response", {}).get("header") if isinstance(data.get("response"),dict) else None
            if isinstance(header, dict) and str(header.get("resultCode", "00")) != "00":
                raise ValueError("agency returned an unsuccessful response")
            proof = {"source": "OFFICIAL_API_RAW_UNVERIFIED_MAPPING", "dataset_id": plan["dataset_id"],
                     "service": plan["service"], "retrieved_at":current.astimezone(KST).isoformat(),
                     "request_without_key":plan["parameters"], "raw_sha256":hashlib.sha256(raw).hexdigest(),
                     "raw_response":data, "requires_human_contract_review":True,
                     "canonical_response_sha256":hashlib.sha256(
                         json.dumps(data, ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":"), allow_nan=False).encode("utf-8")
                     ).hexdigest()}
            payload = json.dumps(proof,ensure_ascii=False,indent=2).encode("utf-8")
            fd = os.open(dest, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            try:
                with os.fdopen(fd,"wb") as fh:
                    fh.write(payload)
                    fh.flush()
                    os.fsync(fh.fileno())
            except BaseException:
                dest.unlink(missing_ok=True)
                raise
            return {"saved":str(dest),"service":plan["service"],"dataset_id":plan["dataset_id"],
                    "raw_sha256": proof["raw_sha256"],"bytes":len(payload),
                    "state":"QUARANTINED_UNVERIFIED_OFFICIAL_MAPPING","calls_this_run":attempt+1}
        except HTTPError as exc:
            status = exc.code
            exc.close()
            if status not in (429, 500, 502, 503, 504) or attempt == max_attempts-1:
                raise ValueError("API HTTP failure (credential redacted)") from None
        except (URLError, TimeoutError, ConnectionError):
            if attempt == max_attempts-1:
                raise ValueError("API network failure (credential redacted)") from None
        except (ValueError, UnicodeError, json.JSONDecodeError):
            raise ValueError("API returned invalid or unverified data (credential redacted)") from None
        except Exception:
            raise ValueError("API transport failed (credential redacted)") from None
        if attempt < max_attempts-1:
            sleep(min(2 ** attempt, 4))
    raise ValueError("API probe failed")


def _plan_to_inputs(plan: dict) -> dict:
    """Revalidate a serialized plan; cannot inject custom service or URL."""
    service = plan.get("service", "")
    pars = plan.get("parameters")
    if not isinstance(pars, dict):
        raise ValueError("invalid request parameters")
    if service.startswith("onbid_"):
        page = pars.get("pageNo")
        rows = pars.get("numOfRows")
        if not (isinstance(page,str) and page.isdigit() and isinstance(rows,str) and rows.isdigit()):
            raise ValueError("invalid Onbid page size")
        inner={k:v for k,v in pars.items() if k not in ("pageNo","numOfRows","resultType")}
        return {"parameters":inner,"page":int(page),"rows":int(rows)}
    if service.startswith("g2b_"):
        if not all(k in pars for k in ("inqryBgnDt","inqryEndDt","pageNo","numOfRows")):
            raise ValueError("invalid G2B plan")
        return {"start":datetime.strptime(pars["inqryBgnDt"],"%Y%m%d%H%M").replace(tzinfo=KST).isoformat(),
                "end":datetime.strptime(pars["inqryEndDt"],"%Y%m%d%H%M").replace(tzinfo=KST).isoformat(),
                "page":pars["pageNo"],"rows":pars["numOfRows"]}
    raise ValueError("unknown API service")


def _contains_sensitive_response_key(value):
    if isinstance(value, dict):
        return any(str(k).lower() in ("servicekey", "authorization", "password", "x-api-key")
                   or _contains_sensitive_response_key(v) for k, v in value.items())
    if isinstance(value, list):
        return any(_contains_sensitive_response_key(v) for v in value)
    return False
