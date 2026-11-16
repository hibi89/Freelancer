"""Real disposable fixture + independent acceptance; no Ollama required."""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from axdev.core import Factory, ContractError
from scripts.verify_trial import verify, main


class TrialVerificationTests(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.root = Path(self.t.name) / "trial"
        subprocess.run([sys.executable, "scripts/prepare_trial.py",
                        "--output", str(self.root)], check=True,
                       capture_output=True, text=True)
        self.repo = self.root / "trial-repo"
        self.plan = self.root / "trial-plan.json"
        self.state = self.root / "state"

    def _fake_coder(self, cwd, prompt):
        (cwd / "src").mkdir(exist_ok=True)
        (cwd / "src" / "hello.py").write_text(
            "def greet(name):\n    return 'Hello, ' + name\n", encoding="utf-8")
        return 0, "synthetic fake coder"

    def _successful_run(self):
        f = Factory(self.repo, self.plan, self.state, coder=self._fake_coder)
        try:
            result = f.run_many(1, execute=True)
        finally:
            f.close()
        self.assertEqual(result[0]["status"], "VERIFIED", result)
        return result[0]

    def test_fresh_fixture_ready_then_fake_coder_acceptance(self):
        self.assertTrue(verify(self.root, "ready")["ready"])
        done = self._successful_run()
        summary = verify(self.root, "completed")
        self.assertTrue(summary["verified"])
        self.assertEqual(summary["verified_commit"], done["commit"])
        self.assertFalse(summary["model_called_proven"])
        with self.assertRaisesRegex(ContractError, "already started or finished"):
            verify(self.root, "ready")

    def test_no_ready_tasks_must_not_report_success(self):
        self.assertTrue(verify(self.root, "ready")["ready"])
        with self.assertRaisesRegex(ContractError, "not independently VERIFIED"):
            verify(self.root, "completed")

    def test_false_verified_ref_is_rejected(self):
        self._successful_run()
        ref = ("refs/heads/axdev/integration-" +
               hashlib.sha256(str(self.state.resolve()).encode()).hexdigest()[:12])
        baseline = subprocess.check_output(
            ["git", "-C", str(self.repo), "rev-parse", "HEAD"], text=True).strip()
        subprocess.run(["git", "-C", str(self.repo), "update-ref", ref, baseline],
                       check=True)
        with self.assertRaisesRegex(ContractError, "integration ref differs"):
            verify(self.root, "completed")

    def test_protected_acceptance_test_modification_refused(self):
        (self.repo / "tests" / "test_hello.py").write_text("def bad(): pass\n")
        with self.assertRaises(ContractError):
            verify(self.root, "ready")

    def test_plan_modified_refused_before_model(self):
        data = json.loads(self.plan.read_text(encoding="utf-8"))
        data["tasks"][0]["files"] = ["src/other.py"]
        self.plan.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaisesRegex(ContractError, "differs from fixed"):
            verify(self.root, "ready")

    def test_cli_ready_exit_contract(self):
        self.assertEqual(main(["--trial", str(self.root), "--phase", "ready"]), 0)
        with self.assertRaises(ContractError):
            verify(self.root, "completed")


if __name__ == "__main__":
    unittest.main()
