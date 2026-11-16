"""P2-only regression scenarios for F18; authoring is not validation.

Do not run this test module during the pre-CI implementation phase.
These tests check serialization/receipt guards, NOT real Windows isolation.
"""
from __future__ import annotations

import base64
import hashlib
import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch, MagicMock

from axdev.core import ContractError, plan_hash
from axdev.windows_sandbox_runtime import (
    _wsb, _read_receipt, _read_bundle, _reconcile, run_sandbox_one,
)
from scripts.sandbox_guest import _safe_payload, _extract

BASE = "a" * 40
RUN = "1" * 32


class SandboxContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.input = self.root / "input"
        self.bundle = self.root / "bundle"
        self.outbox = self.root / "outbox"
        for d in (self.input, self.bundle, self.outbox):
            d.mkdir()
        self.task = {
            "id": "AAA-001", "goal": "Approved only",
            "files": ["src/example.py"], "depends_on": [],
            "checks": [["python", "-m", "unittest", "discover", "-s", "tests", "-q"]],
        }

    def _receipt(self, paths=None):
        paths = paths or [{"path": "src/example.py",
                           "sha256": hashlib.sha256(b"safe").hexdigest(),
                           "data_b64": base64.b64encode(b"safe").decode()}]
        return {
            "version": 1, "run_id": RUN, "base_sha": BASE,
            "task_id": self.task["id"],
            "task_sha256": plan_hash(self.task), "status": "VERIFIED",
            "guest_commit": "b" * 40, "files": paths,
        }

    def _write(self, obj):
        (self.outbox / "receipt.json").write_text(json.dumps(obj), encoding="utf-8")

    def test_wsb_disables_network_and_gpu_and_only_one_host_writable_mapping(self):
        text = _wsb(self.input, self.bundle, self.outbox)
        root = ET.fromstring(text)
        self.assertEqual(root.findtext("Networking"), "Disable")
        self.assertEqual(root.findtext("VGpu"), "Disable")
        self.assertEqual(root.findtext("ClipboardRedirection"), "Disable")
        folders = root.findall("MappedFolders/MappedFolder")
        self.assertEqual([f.findtext("ReadOnly") for f in folders],
                         ["true", "true", "false"])
        self.assertEqual([f.findtext("HostFolder") for f in folders],
                         [str(self.input), str(self.bundle), str(self.outbox)])
        self.assertIn("sandbox_guest.py",
                      Path("scripts/sandbox_guest.py").as_posix())

    def test_receipt_import_accepts_only_approved_digest(self):
        self._write(self._receipt())
        result = _read_receipt(self.root, RUN, self.task, BASE)
        self.assertEqual(result["decoded_files"], {"src/example.py": b"safe"})

    def test_unapproved_receipt_file_rejected(self):
        wrong = [{"path": "keys/config.txt", "sha256": hashlib.sha256(b"x").hexdigest(),
                  "data_b64": base64.b64encode(b"x").decode()}]
        self._write(self._receipt(wrong))
        with self.assertRaisesRegex(ContractError, "allowlist"):
            _read_receipt(self.root, RUN, self.task, BASE)

    def test_modified_receipt_bytes_rejected(self):
        data = self._receipt()
        data["files"][0]["sha256"] = "0" * 64
        self._write(data)
        with self.assertRaisesRegex(ContractError, "hash differs"):
            _read_receipt(self.root, RUN, self.task, BASE)

    def test_wrong_run_id_rejected(self):
        data = self._receipt()
        data["run_id"] = "2" * 32
        self._write(data)
        with self.assertRaisesRegex(ContractError, "not bound"):
            _read_receipt(self.root, RUN, self.task, BASE)

    def test_guest_can_forge_passing_receipt_but_cannot_promote(self):
        # Simulate an untrusted guest that knows every task/request identifier
        # and can write a self-consistent digest plus a fake Git SHA.
        self._write(self._receipt())
        advisory = _read_receipt(self.root, RUN, self.task, BASE)
        self.assertEqual(advisory["status"], "VERIFIED")
        host_factory = MagicMock()
        with self.assertRaisesRegex(ContractError, "UNATTESTED"):
            _reconcile(host_factory, self.task, advisory, BASE)
        host_factory._workspace.assert_not_called()
        host_factory._promote_prepared.assert_not_called()

    def test_prepared_sandbox_task_cannot_promote_legacy_guest_receipt(self):
        host_factory = MagicMock()
        host_factory.status.return_value = {self.task["id"]: "PREPARED"}
        with patch("axdev.windows_sandbox_runtime._sandbox_binary"), \
             patch("axdev.windows_sandbox_runtime._read_bundle"):
            result = run_sandbox_one(
                host_factory, self.task, self.bundle, "0" * 64, True)
        self.assertEqual(result["status"], "HOLD")
        self.assertFalse(result["verified"])
        self.assertEqual(result["reason"], "SANDBOX_UNATTESTED_PREPARED")
        host_factory._promote_prepared.assert_not_called()

    def test_guest_refuses_unpinned_model(self):
        request = {"version": 1, "run_id": RUN, "base_sha": BASE,
                   "task": self.task, "task_sha256": plan_hash(self.task),
                   "model": "openai/paid", "archive_sha256": "0" * 64,
                   "bundle_sha256": "0" * 64}
        with self.assertRaises(ValueError):
            _safe_payload(json.dumps(request).encode())

    def test_guest_archive_rejects_zip_path_traversal(self):
        import zipfile
        archive = self.root / "archive.zip"
        with zipfile.ZipFile(archive, "w") as zipout:
            zipout.writestr("../escape.txt", "payload")
        with self.assertRaisesRegex(ValueError, "UNSAFE_PATH"):
            _extract(archive, self.root / "guest-project")
        self.assertFalse((self.root / "escape.txt").exists())

    def test_toolchain_requires_exact_owner_manifest_hash(self):
        (self.bundle / "manifest.json").write_text(
            json.dumps({"version": 1, "executables": {}}), encoding="utf-8")
        with self.assertRaisesRegex(ContractError, "hash mismatched"):
            _read_bundle(self.bundle, "0" * 64)

    def test_guest_hold_is_not_verification(self):
        data = self._receipt()
        data.pop("guest_commit")
        data.pop("files")
        data.update(status="HOLD", error_code="RuntimeError")
        self._write(data)
        result = _read_receipt(self.root, RUN, self.task, BASE)
        self.assertEqual(result["status"], "HOLD")


if __name__ == "__main__":
    unittest.main()
