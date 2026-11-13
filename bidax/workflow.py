"""Offline BID AX customer workflow, safe report serialization and file exports.

No network operation, commercial eligibility conclusion, or automatic submission.
"""
from __future__ import annotations

import csv
from datetime import datetime, timedelta
from html import escape
from io import StringIO
import json
import os
from pathlib import Path
from typing import Any

from .core import BidLedger, DISCLAIMER, KST, _when, evaluate, validate_profile

MAX_LOCAL_JSON_BYTES = 10 * 1024 * 1024


def read_local_json(path: str | Path) -> object:
    """Bound untrusted local JSON before parsing; no server or external AI upload."""
    path = Path(path)
    if path.stat().st_size > MAX_LOCAL_JSON_BYTES:
        raise ValueError("local JSON exceeds 10 MiB safety limit")
    with path.open("rb") as file:
        blob = file.read(MAX_LOCAL_JSON_BYTES + 1)
    if len(blob) > MAX_LOCAL_JSON_BYTES:
        raise ValueError("local JSON exceeds 10 MiB safety limit")
    return json.loads(blob.decode("utf-8-sig"))


def build_report(ledger: BidLedger, profile: object, now: datetime | None = None) -> dict[str, Any]:
    """Build a source-linked, offline preliminary report from current local notices."""
    checked_profile = validate_profile(profile)
    current = now or datetime.now(KST)
    if current.tzinfo is None or current.utcoffset() is None:
        raise ValueError("now must be timezone-aware")
    reports = [evaluate(notice, checked_profile, current) for notice in ledger.current()]
    summary = {"적합": 0, "부적합": 0, "추가 확인 필요": 0}
    for report in reports:
        summary[report["status"]] += 1
    return {
        "scope": "OFFLINE_PRELIMINARY_ONLY",
        "generated_at": current.astimezone(KST).isoformat(),
        "company": checked_profile["company"],
        "count": len(reports),
        "summary": summary,
        "results": reports,
        "disclaimer": DISCLAIMER,
        "source_freshness": "실시간 공고 또는 첨부문서와 동기화되지 않음. 이용자 직접 원문 재확인 필요",
    }


def due_alerts(ledger: BidLedger, *, now: datetime | None = None, within_hours: int = 72) -> list[dict]:
    """On-demand reminders only; never claims to monitor while PC is off."""
    if type(within_hours) is not int or not 1 <= within_hours <= 24 * 30:
        raise ValueError("within_hours must be between 1 and 720")
    current = now or datetime.now(KST)
    if current.tzinfo is None or current.utcoffset() is None:
        raise ValueError("now must have offset")
    limit = current + timedelta(hours=within_hours)
    alerts = []
    for notice in ledger.current():
        deadline = _when(notice["deadline"], "deadline")
        if deadline < current:
            state = "마감 경과"
        elif deadline <= limit:
            state = "마감 임박"
        else:
            continue
        alerts.append({
            "notice_no": notice["notice_no"],
            "title": notice["title"],
            "deadline": notice["deadline"],
            "state": state,
            "source_url": notice["source_url"],
            "fingerprint": notice["fingerprint"],
        })
    return sorted(alerts, key=lambda item: (item["deadline"], item["notice_no"]))


def _csv_safe(value: object) -> str:
    """Neutralize formula injection on Excel/LibreOffice CSV opening."""
    text = str(value if value is not None else "").replace("\x00", "")
    if text.lstrip().startswith(("=", "+", "-", "@", "\t", "\r", "\n")) or text.startswith(("\t", "\r", "\n")):
        return "'" + text
    return text


def report_csv(report: dict) -> str:
    buf = StringIO(newline="")
    writer = csv.writer(buf, lineterminator="\r\n")
    writer.writerow(["공고번호", "기업", "공고명", "판정", "마감", "부적합사유", "수동확인사항", "원문", "SHA256"])
    for row in report["results"]:
        writer.writerow([_csv_safe(row.get(key, "")) for key in ("notice_no", "company", "title", "status", "deadline")]
                        + [_csv_safe(" | ".join(row["deterministic_mismatch"])),
                           _csv_safe(" | ".join(row["needs_review"])),
                           _csv_safe(row["source_url"]),
                           _csv_safe(row.get("source_fingerprint"))])
    return buf.getvalue()


def report_html(report: dict) -> str:
    esc = lambda value: escape(str(value if value is not None else ""), quote=True)
    body = []
    for row in report["results"]:
        issues = row["deterministic_mismatch"] + row["needs_review"]
        items = "".join("<li>" + esc(issue) + "</li>" for issue in issues) or "<li>추가 검사 없음 (원문 대조 별도 필요)</li>"
        body.append("<section><h2>" + esc(row["notice_no"]) + " — " + esc(row.get("title", "")) + "</h2>"
                    + "<p><b>잠정 판정:</b> " + esc(row["status"]) + "</p>"
                    + "<p><b>마감:</b> " + esc(row["deadline"]) + "</p>"
                    + "<p><b>원문:</b> <a rel=\"noopener noreferrer\" href=\"" + esc(row["source_url"]) + "\">원문 열기</a></p>"
                    + "<p><b>원본 지문:</b> " + esc(row.get("source_fingerprint")) + "</p><ul>" + items + "</ul></section>")
    return ("<!doctype html><html lang=\"ko\"><head><meta charset=\"utf-8\">"
            "<meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'\">"
            "<title>BID AX 로컬 사전검토</title>"
            "<style>body{font-family:system-ui,sans-serif;max-width:900px;margin:3rem auto;padding:0 1rem;color:#202936}"
            "section{border:1px solid #ddd;border-radius:12px;margin:1rem 0;padding:1rem}h1{font-size:1.5rem}h2{font-size:1.2rem}"
            "p,li{line-height:1.5}a{color:#1448aa}</style></head><body>"
            "<h1>BID AX — 로컬 입찰 준비 사전검토</h1>"
            "<p>기업: " + esc(report["company"]) + " · 작성: " + esc(report["generated_at"]) + "</p>"
            "<p><strong>" + esc(report["disclaimer"]) + "</strong></p>"
            "<p>" + esc(report["source_freshness"]) + "</p>"
            + "".join(body) + "</body></html>")


def write_new_report(path: str | Path, report: dict, fmt: str) -> None:
    """Export to a new path, never replace an existing customer report."""
    path = Path(path)
    if fmt == "json":
        content = json.dumps(report, ensure_ascii=False, indent=2).encode("utf-8")
    elif fmt == "csv":
        content = ("\ufeff" + report_csv(report)).encode("utf-8")
    elif fmt == "html":
        content = report_html(report).encode("utf-8")
    else:
        raise ValueError("unknown export format")
    with path.open("xb") as file:
        try:
            file.write(content)
            file.flush()
            os.fsync(file.fileno())
        except Exception:
            file.close()
            path.unlink(missing_ok=True)  # only our freshly created path
            raise
