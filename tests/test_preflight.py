"""No real Ollama or OpenCode needed for deterministic host-preflight tests."""
import unittest
from unittest.mock import patch

from scripts.preflight import inspect, main


class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.version = [
            (True, "git version 2.47.0"),
            (True, "ollama version 0.11.0"),
            (True, "2.2.6"),
            (True, "OpenCode 2 --standalone --help"),
        ]

    def _run(self, models=("qwen3:4b-instruct",), gpu=False):
        versions = self.version + ([(True, "GTX 1050 Ti, 4096")] if gpu else [])
        with patch("scripts.preflight._version", side_effect=versions) as ver, \
             patch("scripts.preflight._ollama_models", return_value=list(models)), \
             patch("scripts.preflight._ollama_capabilities", return_value=["completion", "tools"]), \
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
        calls.assert_any_call("opencode", "run", "--help")

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
             patch("scripts.preflight._ollama_capabilities", return_value=["completion", "tools"]), \
             patch("scripts.preflight.shutil.which", return_value=None):
            report = inspect("ollama/qwen3:4b-instruct")
        self.assertFalse(report["ready_for_disposable_model_trial"])
        self.assertTrue(any("2.2.6+" in x for x in report["blockers"]))

    def test_old_v2_ignoring_websearch_policy_is_blocked(self):
        version = self.version.copy()
        version[2] = (True, "2.2.5")
        with patch("scripts.preflight._version", side_effect=version), \
             patch("scripts.preflight._ollama_models",
                   return_value=["qwen3:4b-instruct"]), \
             patch("scripts.preflight._ollama_capabilities",
                   return_value=["completion", "tools"]), \
             patch("scripts.preflight.shutil.which", return_value=None):
            value = inspect("ollama/qwen3:4b-instruct")
        self.assertFalse(value["ready_for_disposable_model_trial"])
        self.assertIn("OpenCode 2.2.6+ required for effective V2 hard policies",
                      value["blockers"])

    def test_missing_ollama_api_fails_closed(self):
        with patch("scripts.preflight._version", side_effect=self.version), \
             patch("scripts.preflight._ollama_models", side_effect=ConnectionRefusedError()), \
             patch("scripts.preflight.shutil.which", return_value=None):
            report = inspect("ollama/qwen3:4b-instruct")
        self.assertFalse(report["ready_for_disposable_model_trial"])
        self.assertFalse(report["model_present"])

    def test_installed_model_without_tools_is_blocked_before_worktree(self):
        with patch("scripts.preflight._version", side_effect=self.version), \
             patch("scripts.preflight._ollama_models", return_value=["qwen3:4b-instruct"]), \
             patch("scripts.preflight._ollama_capabilities", return_value=["completion"]), \
             patch("scripts.preflight.shutil.which", return_value=None):
            result = inspect("ollama/qwen3:4b-instruct")
        self.assertFalse(result["ready_for_disposable_model_trial"])
        self.assertFalse(result["model_tool_calls_supported"])
        self.assertIn("selected Ollama model does not support tool calling", result["blockers"])

    def test_show_metadata_unavailable_fails_closed(self):
        with patch("scripts.preflight._version", side_effect=self.version), \
             patch("scripts.preflight._ollama_models", return_value=["qwen3:4b-instruct"]), \
             patch("scripts.preflight._ollama_capabilities", side_effect=RuntimeError("metadata missing")), \
             patch("scripts.preflight.shutil.which", return_value=None):
            result = inspect("ollama/qwen3:4b-instruct")
        self.assertFalse(result["ready_for_disposable_model_trial"])
        self.assertTrue(any("capabilities unavailable" in b for b in result["blockers"]))

    def test_git_author_and_committer_checked_without_exposing_addresses(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as root:
            project = Path(root) / "trial"
            (project / ".git").mkdir(parents=True)
            calls = []
            def stub(argv, **kwargs):
                calls.append(argv[-1])
                return type("C", (), {"returncode": 0,
                         "stdout": "Example <private@example.invalid> 123 +0000"})()
            with patch("scripts.preflight.subprocess.run", side_effect=stub):
                self.assertTrue(__import__("scripts.preflight", fromlist=["_git_identity_ready"])
                                ._git_identity_ready(project))
            self.assertEqual(calls, ["GIT_AUTHOR_IDENT", "GIT_COMMITTER_IDENT"])

    def test_git_identity_missing_blocks_repo_trial(self):
        from pathlib import Path
        with patch("scripts.preflight._version", side_effect=self.version), \
             patch("scripts.preflight._ollama_models", return_value=["qwen3:4b-instruct"]), \
             patch("scripts.preflight._ollama_capabilities", return_value=["completion", "tools"]), \
             patch("scripts.preflight._git_identity_ready", return_value=False), \
             patch("scripts.preflight.shutil.which", return_value=None):
            result = inspect("ollama/qwen3:4b-instruct", Path("temporary"))
        self.assertFalse(result["ready_for_disposable_model_trial"])
        self.assertFalse(result["git_author_committer_ready"])
        self.assertFalse(result["git_identity_github_account_verified"])
        self.assertIn("local Git author/committer identity is missing or invalid", result["blockers"])

    def test_no_remote_calls_are_initiated_from_preflight(self):
        # _ollama_models is the ONLY network call; standalone config is inspected, not executed.
        with patch("scripts.preflight._version", side_effect=self.version), \
             patch("scripts.preflight._ollama_models", return_value=["qwen3:4b-instruct"]) as tags, \
             patch("scripts.preflight._ollama_capabilities", return_value=["completion", "tools"]) as show, \
             patch("scripts.preflight.shutil.which", return_value=None):
            with patch("builtins.print"):
                self.assertEqual(main(["--model", "ollama/qwen3:4b-instruct"]), 0)
            tags.assert_called_once_with()
            show.assert_called_once_with("qwen3:4b-instruct")


if __name__ == "__main__":
    unittest.main()
