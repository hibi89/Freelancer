"""F20 dashboard loopback HTTP authority/CSRF tests; no model execution."""
import http.client
import threading
import unittest
from http.server import HTTPServer
from pathlib import Path
from unittest.mock import patch

from scripts.owner_dashboard import handler_factory


class DashboardHttpSecurityTests(unittest.TestCase):
    def setUp(self):
        self.token = "synthetic-csrf-only"
        self.settings = Path("no-real-settings.json")
        self.control = patch("scripts.owner_dashboard.control")
        self.stub = self.control.start()
        self.stub.return_value = {
            "counts": {"QUEUED": 2, "IMPLEMENTED": 1, "VERIFIED": 0, "HOLD": 1},
            "stop_requested": False,
        }
        self.addCleanup(self.control.stop)
        self.server = HTTPServer(
            ("127.0.0.1", 0), handler_factory(self.settings, 0, self.token))
        self.port = self.server.server_port
        self.server.RequestHandlerClass = handler_factory(
            self.settings, self.port, self.token)
        thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(thread.join, 5)
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)

    def request(self, method, path, *, host=None, data=None, origin=None, response_header=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        headers = {"Host": host or ("127.0.0.1:" + str(self.port))}
        if data is not None:
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        if origin is not None:
            headers["Origin"] = origin
        try:
            connection.request(method, path, body=data, headers=headers)
            response = connection.getresponse()
            if response_header:
                return response.status, response.getheader(response_header)
            return response.status, response.read().decode("utf-8")
        finally:
            connection.close()

    def test_rebound_domain_cannot_read_local_page_token(self):
        code, data = self.request(
            "GET", "/", host="attacker.example:" + str(self.port))
        self.assertEqual(code, 403)
        self.assertNotIn(self.token, data)
        self.stub.assert_not_called()

    def test_exact_loopback_host_can_read_status_without_source_data(self):
        code, data = self.request("GET", "/")
        self.assertEqual(code, 200)
        self.assertIn(self.token, data)
        self.assertIn("QUEUED", data)
        self.assertIn("VERIFIED", data)
        self.assertNotIn("GITHUB_TOKEN", data)

    def test_rebound_post_denied_despite_known_csrf(self):
        data = "csrf=" + self.token
        try:
            code, _ = self.request(
                "POST", "/stop", data=data,
                host="attacker.example:" + str(self.port))
        except (ConnectionAbortedError, ConnectionResetError):
            # On Windows, rejecting a POST before draining its untrusted
            # body can produce a TCP reset instead of an HTTP 403 response.
            # Both must be fail-closed; control() must still NOT be called.
            code = 403
        self.assertEqual(code, 403)
        self.stub.assert_not_called()

    def test_cross_origin_post_denied_and_same_origin_can_stop(self):
        data = "csrf=" + self.token
        code, _ = self.request(
            "POST", "/stop", data=data, origin="https://attacker.example")
        self.assertEqual(code, 403)
        self.stub.assert_not_called()
        code, _ = self.request(
            "POST", "/stop", data=data,
            origin="http://127.0.0.1:" + str(self.port))
        self.assertEqual(code, 303)
        self.stub.assert_called_once()

    def test_form_page_keeps_origin_for_loopback_but_refuses_opaque_origin(self):
        code, policy = self.request("GET", "/", response_header="Referrer-Policy")
        self.assertEqual((code, policy), (200, "same-origin"))
        self.stub.reset_mock()
        try:
            code, _ = self.request("POST", "/resume", data="csrf=" + self.token, origin="null")
        except (ConnectionAbortedError, ConnectionResetError):
            code = 403
        self.assertEqual(code, 403)
        self.stub.assert_not_called()


    def test_corrupt_private_status_is_503_without_owner_token(self):
        import sqlite3
        self.stub.side_effect = sqlite3.DatabaseError("synthetic-corrupt-sqlite")
        status, data = self.request("GET", "/")
        self.assertEqual(status, 503)
        self.assertNotIn(self.token, data)
        status, _ = self.request("POST", "/stop", data="csrf=" + self.token)
        self.assertEqual(status, 503)

if __name__ == "__main__":
    unittest.main()
