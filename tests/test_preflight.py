"""No real Ollama or OpenCode needed for deterministic host-preflight tests."""
import unittest
from unittest.mock import patch

from scripts.preflight import inspect, main


class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.version = [
            (True, "git version 2.47.0"),
            (True, "ollama version 0.11.0"),
            (True, "2.2.3"),
            (True, "OpenCode 2 --standalone --help"),
        ]

    def _run(self, models=("qwen3:4b-instruct",), gpu=False):
        versions = self.version + ([(True, "GTX 1050 Ti, 4096")] if gpu else [])
        with patch("scripts.preflight._version", side_effect=versions) as ver, \
             patch("scripts.preflight._ollama_models", return_value=list(models)), \
             patch("scripts.preflight.shutil.which", return_value="nvidia-smi" if gpu else None):
            result = inspect("ollama/qwen3:4b-instruct")
        return result, ver

    def test_readonly_local_model_ready_and_gpu_optional(self):
        report, calls = self._run()
        self.assertTrue(report["ready_for_disposable_model_trial"])
        self.assertTrue(report["model_present"])
        self.assertFalse(report["approved_for_real_tasks"])
        self.assertFalse(report["gpu_detected"])
        self.assertEqual(report["blockers"], [])
        self.assertEqual(calls.call_count, 4)

    def test_gpu_detected_but_not_claimed_benchmarked(self):
        report, _ = self._run(gpu=True)
        self.assertTrue(report["gpu_detected"])
        self.assertFalse(report["gpu_performance_verified"])

    def test_missing_model_fails_closed(self):
        report, _ = self._run(models=())
        self.assertFalse(report["ready_for_disposable_model_trial"])
        self.assertIn("selected Ollama model not installed", report["blockers"])

    def test_missing_opencode_v2_stops_trial(self):
        version = self.version.copy()
        version[2] = (True, "1.9.9")
        with patch("scripts.preflight._version", side_effect=version), \
             patch("scripts.preflight._ollama_models", return_value=["qwen3:4b-instruct"]), \
             patch("scripts.preflight.shutil.which", return_value=None):
            report = inspect("ollama/qwen3:4b-instruct")
        self.assertFalse(report["ready_for_disposable_model_trial"])
        self.assertTrue(any("2+" in x for x in report["blockers"]))

    def test_missing_ollama_api_fails_closed(self):
        with patch("scripts.preflight._version", side_effect=self.version), \
             patch("scripts.preflight._ollama_models", side_effect=ConnectionRefusedError()), \
             patch("scripts.preflight.shutil.which", return_value=None):
            report = inspect("ollama/qwen3:4b-instruct")
        self.assertFalse(report["ready_for_disposable_model_trial"])
        self.assertFalse(report["model_present"])

    def test_no_remote_calls_are_initiated_from_preflight(self):
        # _ollama_models is the ONLY network call; standalone config is inspected, not executed.
        with patch("scripts.preflight._version", side_effect=self.version), \
             patch("scripts.preflight._ollama_models", return_value=["qwen3:4b-instruct"]) as tags, \
             patch("scripts.preflight.shutil.which", return_value=None):
            with patch("builtins.print"):
                self.assertEqual(main(["--model", "ollama/qwen3:4b-instruct"]), 0)
            tags.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
