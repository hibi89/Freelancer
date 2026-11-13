"""Opt-in, pinned official API transport with durable daily attempt budget.

Not invoked by CLI/GUI. The credential is ephemeral, supplied by caller and
never stored or logged. A live call additionally requires customer permission.
The *response mapping* remains provisional until independently tested against
an authorized raw government response and original attachments.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, build_opener, Request

from .core import BidLedger, KST, official_query

MAX_RESPONSE_BYTES = 10 * 1024 * 1024
RETRY_CODES = {429, 500, 502, 503, 504}


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("redirect prohibited by pinned official transport")


def _unique_keys(pairs):
    result={}
    for key,value in pairs:
        if key in result:
            raise ValueError("duplicate response JSON key")
        result[key]=value
    return result


def _reserve(ledger: BidLedger, daily_limit: int, now: datetime):
    if type(daily_limit) is not int or not 1 <= daily_limit <= 1000:
        raise ValueError("daily_limit must be 1..1000 until production quota confirmed")
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("timezone-aware time required")
    day=now.astimezone(KST).date().isoformat()
    ledger.conn.execute("""CREATE TABLE IF NOT EXISTS api_attempts (
        day TEXT PRIMARY KEY, count INTEGER NOT NULL CHECK (count>=0))""")
    # Durable reservation precedes the HTTP request; a crash uses budget rather
    # than accidentally exceeding quota. SQLite serialize writes through a lock.
    with ledger.conn:
        ledger.conn.execute("INSERT OR IGNORE INTO api_attempts(day,count) VALUES(?,0)",(day,))
        saved=ledger.conn.execute("UPDATE api_attempts SET count=count+1 WHERE day=? AND count<?",
                                  (day,daily_limit))
        if saved.rowcount!=1:
            raise ValueError("local daily API attempt budget exhausted")


def fetch_one_page(ledger: BidLedger, *, category: str, start: datetime, end: datetime,
                   page: int, service_key: str, daily_limit: int=8,
                   permission: bool=False, opener=None, sleep=time.sleep,
                   now: datetime | None=None, max_attempts: int=3) -> dict:
    """Explicitly opted-in single page; never uses API automatically.

    Args `opener` and `sleep` support zero-network tests. HTTP status and
    headers may be viewed in tests; live key and full URL are never returned.
    """
    if permission is not True:
        raise PermissionError("explicit customer approval for live government request required")
    if not isinstance(service_key,str) or not service_key.strip() or len(service_key)>4096:
        raise ValueError("customer-owned API key required")
    if type(max_attempts) is not int or not 1<=max_attempts<=3:
        raise ValueError("max_attempts must be 1..3")
    plan=official_query(category,start,end,page)
    base=plan["base_url"]
    parts=urlsplit(base)
    if parts.scheme!="https" or parts.hostname!="apis.data.go.kr" or not parts.path.startswith("/1230000/ad/BidPublicInfoService02/"):
        raise ValueError("untrusted request host or path")
    params={**plan["params_without_service_key"],"serviceKey":service_key.strip()}
    url=base+"?"+urlencode(params)
    http=opener or build_opener(_NoRedirect())
    for attempt in range(max_attempts):
        # Each retry uses the current KST day unless a test clock is injected.
        _reserve(ledger,daily_limit,now if now is not None else datetime.now(timezone.utc))
        request=Request(url,headers={"Accept":"application/json","User-Agent":"BIDAX-manual-approved/0.85"},method="GET")
        try:
            response=http.open(request,timeout=15)
            with response:
                code=getattr(response,"status",200)
                if code!=200:
                    raise ValueError("unexpected official HTTP status")
                mime=response.headers.get("Content-Type", "")
                if "json" not in mime.lower():
                    raise ValueError("non-JSON official response quarantined")
                blob=response.read(MAX_RESPONSE_BYTES+1)
            if len(blob)>MAX_RESPONSE_BYTES:
                raise ValueError("official response larger than 10 MiB")
            return json.loads(blob.decode("utf-8-sig"),object_pairs_hook=_unique_keys)
        except HTTPError as error:
            code=error.code
            error.close()
            if code not in RETRY_CODES or attempt==max_attempts-1:
                raise ValueError("official HTTP request rejected or retries exhausted; key redacted") from None
        except (URLError, TimeoutError, ConnectionError):
            if attempt==max_attempts-1:
                raise ValueError("official network unavailable; key redacted") from None
        except ValueError as error:
            if str(error) == "duplicate response JSON key":
                raise ValueError("duplicate response JSON key") from None
            raise ValueError("official transport failure; key redacted") from None
        except Exception:
            # Unexpected openers may raise errors containing a secret-bearing URL.
            raise ValueError("official transport failure; key redacted") from None
        if attempt<max_attempts-1:
            sleep(min(2**attempt,4))
    raise ValueError("official request failed")
