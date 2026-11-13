"""Credential-free public Onbid OpenAPI request PLAN, not an executable client.

Inputs/required parameters from data.go.kr dataset pages 15157220, 15157252,
15157254. Exact response contracts, operating rights, and method names remain
unverified; never construct or execute a network URL from this file.
"""
from __future__ import annotations

from datetime import date
import re

_API = {
    "announcement_assets": {
        "dataset_id": 15157220,
        "base": "https://apis.data.go.kr/B010003/OnbidPbancCltrDtlSrvc2",
        "required": ("pbancMngNo",),
        "optional": (),
    },
    "result_list": {
        "dataset_id": 15157252,
        "base": "https://apis.data.go.kr/B010003/OnbidCltrBidRsltListSrvc2",
        "required": ("cltrTypeCd", "prptDivCd", "opbdDtStart", "opbdDtEnd"),
        "optional": ("pbctStatCd",),
    },
    "result_detail": {
        "dataset_id": 15157254,
        "base": "https://apis.data.go.kr/B010003/OnbidCltrBidRsltDtlSrvc2",
        "required": ("cltrMngNo",),
        "optional": ("pbctCdtnNo",),
    },
}

_SINGLE_ID = re.compile(r"^[0-9A-Za-z-]{1,80}$")
_PROPERTY_TYPES = frozenset(("0001", "0002", "0003"))
_PROPERTY_CATEGORIES = frozenset(("0002", "0003", "0004", "0005", "0006", "0007", "0008", "0010", "0011", "0013"))
_RESULT_STATES = frozenset(("0010", "0011", "0012"))


def build_plan(kind: str, parameters: dict, *, page: int = 1, rows: int = 10) -> dict:
    """Validate known required query inputs without accessing internet or secrets.

    Notably, Onbid is NOT assigned G2B's seven-day date restriction. The portal
    does not establish that limit for these Onbid operations. No URL containing
    an API key or unverified operation name is emitted.
    """
    if kind not in _API:
        raise ValueError("unknown Onbid service; no implicit endpoint discovery")
    if type(page) is not int or not 1 <= page <= 100000:
        raise ValueError("page must be 1..100000")
    if type(rows) is not int or not 1 <= rows <= 100:
        raise ValueError("rows must be 1..100")
    if not isinstance(parameters, dict) or any(not isinstance(k, str) for k in parameters):
        raise ValueError("parameters must be a named object")
    spec = _API[kind]
    expected = set(spec["required"]) | set(spec["optional"])
    if set(parameters) - expected or set(spec["required"]) - set(parameters):
        raise ValueError("unknown or missing parameters; API key forbidden in plan")
    clean = {}
    for key, value in parameters.items():
        if not isinstance(value, str) or len(value) > 100 or any(ord(c) < 32 for c in value):
            raise ValueError("malformed Onbid parameter")
        value = value.strip()
        if key in ("opbdDtStart", "opbdDtEnd"):
            if not re.fullmatch(r"\d{8}", value):
                raise ValueError("date must be YYYYMMDD")
            try:
                date.fromisoformat(value[:4] + "-" + value[4:6] + "-" + value[6:])
            except ValueError as e:
                raise ValueError("invalid calendar date") from e
        elif key == "cltrTypeCd":
            if value not in _PROPERTY_TYPES:
                raise ValueError("unknown Onbid property type code")
        elif key == "prptDivCd":
            codes = value.split(",")
            if len(set(codes)) != len(codes) or not 1 <= len(codes) <= 10 or any(c not in _PROPERTY_CATEGORIES for c in codes):
                raise ValueError("unknown/duplicate Onbid property category")
        elif key == "pbctStatCd":
            if value not in _RESULT_STATES:
                raise ValueError("unsupported Onbid result state")
        elif not _SINGLE_ID.fullmatch(value):
            raise ValueError("invalid Onbid identifier")
        clean[key] = value
    if kind == "result_list" and clean["opbdDtEnd"] < clean["opbdDtStart"]:
        raise ValueError("end before start")
    return {
        "source": "ONBID_OFFICIAL_METADATA_ONLY",
        "kind": kind,
        "dataset_id": spec["dataset_id"],
        "documentation": f'https://www.data.go.kr/data/{spec["dataset_id"]}/openapi.do',
        "verified_api_base": spec["base"],
        "parameters": dict(sorted({**clean,"pageNo":str(page),"numOfRows":str(rows),"resultType":"json"}.items())),
        "operation_path": None,
        "service_key": "CUSTOMER_APPLICATION_REQUIRED_NOT_COLLECTED",
        "network_ready": False,
        "no_network_call": True,
        "warning": "계정별 사용권, 최종 오퍼레이션 경로, 원본 응답항목을 승인/실데이터로 검증하기 전 호출 금지",
    }
