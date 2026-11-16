import sqlite3
import tempfile
import unittest
from pathlib import Path

from axdev.core import ContractError
from scripts.first_use_evidence import report, main


class TrialReportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.trial = self.root / "trial"
        (self.trial / "trial-repo" / ".git").mkdir(parents=True)
        (self.trial / "trial-plan.json").write_text('{"version":1,"tasks":[]}')
        self.state = self.trial / "state"

    def test_readonly_without_runtime_state(self):
        data = report(self.trial)
        self.assertEqual(data["state_counts"]["VERIFIED"], 0)
        self.assertFalse(data["real_model_call_proven_by_this_report"])
        self.assertFalse(self.state.exists())

    def test_verified_metadata_never_claims_actual_model_proof(self):
        self.state.mkdir()
        with sqlite3.connect(self.state / "factory.sqlite3") as db:
            db.execute("CREATE TABLE runs (status TEXT, commit_sha TEXT)")
            db.execute("INSERT INTO runs VALUES (?,?)", ("VERIFIED", "b" * 40))
        (self.state / "run-events.jsonl").write_text('{"status":"VERIFIED"}\n')
        data = report(self.trial)
        self.assertEqual(data["verified_commit_count"], 1)
        self.assertEqual(data["task_events"], 1)
        self.assertFalse(data["effective_opencode_permissions_verified"])
        self.assertFalse(data["real_model_call_proven_by_this_report"])

    def test_private_output_file_is_exclusive(self):
        output = self.root / "private" / "evidence.json"
        self.assertEqual(main(["--trial", str(self.trial),
                               "--output", str(output)]), 0)
        self.assertTrue(output.is_file())
        with self.assertRaises(FileExistsError):
            main(["--trial", str(self.trial), "--output", str(output)])

    def test_missing_synthetic_repo_fails_closed(self):
        with self.assertRaisesRegex(ContractError, "fixture missing"):
            report(self.root / "missing")

    def test_symlinked_state_fails_closed(self):
        target = self.root / "other-state"
        target.mkdir()
        try:
            self.state.symlink_to(target, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        with self.assertRaisesRegex(ContractError, "symlink"):
            report(self.trial)

    def test_symlinked_trial_fails_closed(self):
        link = self.root / "other-trial"
        try:
            link.symlink_to(self.trial, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        with self.assertRaisesRegex(ContractError, "symlink"):
            report(link)


if __name__ == "__main__":
    unittest.main()
