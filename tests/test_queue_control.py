import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts.queue_control import control, main
from axdev.core import ContractError

class QueueControlTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.state = self.root / "runtime"
        self.settings = self.root / "settings.json"
        self.settings.write_text(json.dumps({
            "version": 1,
            "repo": str(self.root / "project"),
            "state": str(self.state),
            "plan": str(self.root / "plan.json"),
            "model": "ollama/qwen3:4b-instruct"}), encoding="utf-8")

    def test_readonly_status_without_database(self):
        result = control("status", self.settings)
        self.assertEqual(result["counts"]["QUEUED"], 0)
        self.assertFalse(result["stop_requested"])
        self.assertFalse(self.state.exists())

    def test_stop_is_idempotent_and_resume_needs_confirmation(self):
        self.assertTrue(control("stop", self.settings)["stop_requested"])
        self.assertTrue(control("stop", self.settings)["stop_requested"])
        self.assertTrue((self.state / "STOP.REQUESTED").exists())
        with self.assertRaisesRegex(ContractError, "--confirm"):
            control("resume", self.settings)
        self.assertTrue(control("resume", self.settings, True)["execution_started"] is False)
        self.assertFalse((self.state / "STOP.REQUESTED").exists())

    def test_status_reports_stop_request(self):
        control("stop", self.settings)
        with patch("builtins.print"):
            self.assertEqual(main(["status", "--settings", str(self.settings)]), 0)
        self.assertTrue(control("status", self.settings)["stop_requested"])

    def test_refuse_state_inside_checkout(self):
        settings = json.loads(self.settings.read_text(encoding="utf-8"))
        settings["state"] = str(self.root / "project" / "state")
        self.settings.write_text(json.dumps(settings))
        with self.assertRaises(ContractError):
            control("stop", self.settings)
        self.assertFalse((self.root / "project").exists())


if __name__ == "__main__":
    unittest.main()
