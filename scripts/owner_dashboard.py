"""Loopback-only owner status, stop and confirmed-resume dashboard.

No remote binding, no uploads, no task editing, no automatic model execution.
The ephemeral form token is kept only in this process, not in GitHub.
"""
from __future__ import annotations

import argparse
import html
import hmac
import json
import secrets
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs

from axdev.core import ContractError
from scripts.queue_control import control
from scripts.owner_dashboard_view import render_dashboard


def handler_factory(settings: Path, port: int, secret: str):
    local_origin = "http://127.0.0.1:" + str(port)

    class OwnerHandler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            # Never print CSRF tokens, request paths, project data or headers.
            pass

        def _headers(self, code, mime="text/html; charset=utf-8", length=0):
            self.send_response(code)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(length))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            # Browsers can send Origin: null for a form POST under no-referrer.
            # Keep the exact loopback origin while suppressing cross-site referrers.
            self.send_header("Referrer-Policy", "same-origin")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Content-Security-Policy",
                "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; "
                "base-uri 'none'; frame-ancestors 'none'")
            self.end_headers()

        def _send(self, code, body: str):
            data = body.encode("utf-8")
            self._headers(code, length=len(data))
            self.wfile.write(data)

        def _local_request(self):
            # DNS rebinding can make a remote domain resolve to loopback.
            # Binding to 127.0.0.1 alone is NOT an HTTP authority check.
            return (self.client_address[0] == "127.0.0.1" and
                    self.headers.get("Host") == "127.0.0.1:" + str(port))

        def do_GET(self):
            if not self._local_request():
                return self._send(403, "Forbidden")
            if self.path != "/":
                return self._send(404, "Not found")
            try:
                state = control("status", settings)
            except (OSError, ValueError) as exc:
                return self._send(503, "Queue status unavailable: " +
                                  html.escape(type(exc).__name__))
            self._send(200, render_dashboard(state, secret))

        def do_POST(self):
            if not self._local_request() or self.path not in ("/stop", "/resume"):
                return self._send(403, "Forbidden")
            # HTML form from exact same-origin loopback page only.
            origin = self.headers.get("Origin")
            if origin not in (None, local_origin):
                return self._send(403, "Origin forbidden")
            if self.headers.get("Content-Type", "").split(";", 1)[0] != "application/x-www-form-urlencoded":
                return self._send(415, "Unsupported form content type")
            try:
                size = int(self.headers.get("Content-Length", "-1"))
            except ValueError:
                return self._send(400, "Invalid length")
            if not 1 <= size <= 512:
                return self._send(400, "Invalid length")
            values = parse_qs(self.rfile.read(size).decode("utf-8"), keep_blank_values=True)
            presented = values.get("csrf", [])
            if len(presented) != 1 or not hmac.compare_digest(presented[0], secret):
                return self._send(403, "Owner token missing or invalid")
            try:
                control(self.path[1:], settings, confirm=self.path == "/resume")
            except (OSError, ValueError):
                return self._send(503, "Local control unavailable")
            self.send_response(303)
            self.send_header("Location", "/")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()

    return OwnerHandler


def main(argv=None):
    p = argparse.ArgumentParser(description="Loopback-only AXDEV owner controls")
    p.add_argument("--settings", type=Path, required=True)
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--confirm-local-dashboard", action="store_true")
    a = p.parse_args(argv)
    if not a.confirm_local_dashboard or not 1024 <= a.port <= 65535:
        raise ContractError("explicit loopback dashboard consent and high port required")
    # Preflight the read-only state before binding the local HTTP listener.
    control("status", a.settings)
    secret = secrets.token_urlsafe(32)
    with HTTPServer(("127.0.0.1", a.port),
                    handler_factory(a.settings, a.port, secret)) as server:
        print("Owner-only loopback dashboard: http://127.0.0.1:" + str(a.port))
        print("Stop with Ctrl+C; never forward this port.")
        server.serve_forever(poll_interval=0.5)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, ContractError, KeyboardInterrupt) as exc:
        print("AXDEV_DASHBOARD_EXIT:", type(exc).__name__)
        raise SystemExit(2)
