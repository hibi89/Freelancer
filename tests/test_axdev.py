import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from axdev.core import ContractError, Factory, load_plan, single_worker_lock

class FactoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self._git("init")
        self._git("config", "user.name", "AXDev Test")
        self._git("config", "user.email", "axdev-test@example.invalid")
        (self.repo / "README.md").write_text("fixture\n", encoding="utf-8")
        (self.repo / "tests").mkdir()
        (self.repo / "tests" / "test_base.py").write_text(
            "import unittest\nclass T(unittest.TestCase):\n def test_base(self): self.assertTrue(True)\n",
            encoding="utf-8")
        self._git("add", ".")
        self._git("commit", "-m", "fixture")
        self.plan = self.root / "plan.json"
        self.state = self.root / "state"

    def tearDown(self):
        self.temp.cleanup()

    def _git(self, *args):
        subprocess.run(["git", *args], cwd=self.repo, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def write_plan(self, tasks):
        self.plan.write_text(json.dumps({"version": 1, "tasks": tasks}),
                             encoding="utf-8")

    def task(self, tid="AAA-001", deps=None):
        return {"id": tid, "goal": "Create a safe tested addition",
                "files": ["src/feature.py"],
                "depends_on": deps or [],
                "checks": [["python", "-m", "unittest", "discover", "-s", "tests", "-q"]]}

    def fake_coder(self, cwd, prompt):
        (cwd / "src").mkdir(exist_ok=True)
        (cwd / "src" / "feature.py").write_text("value = 42\n", encoding="utf-8")
        return 0, "ok"

    def test_invalid_path_and_cycle(self):
        bad = self.task()
        bad["files"] = ["../oops"]
        self.write_plan([bad])
        with self.assertRaises(ContractError):
            load_plan(self.plan)
        self.write_plan([self.task("AAA-001", ["BBB-002"]),
                         self.task("BBB-002", ["AAA-001"])])
        with self.assertRaises(ContractError):
            load_plan(self.plan)

    def test_dry_run_does_not_edit(self):
        self.write_plan([self.task()])
        f = Factory(self.repo, self.plan, self.state, coder=self.fake_coder)
        result = f.run_one(False)
        self.assertEqual(result["status"], "DRY_RUN")
        self.assertFalse((self.state / "worktrees" / "AAA-001").exists())
        f.close()

    def test_verified_worktree_preserves_original(self):
        self.write_plan([self.task()])
        f = Factory(self.repo, self.plan, self.state, coder=self.fake_coder)
        result = f.run_one(True)
        self.assertEqual(result["status"], "VERIFIED", result)
        self.assertFalse((self.repo / "src" / "feature.py").exists())
        self.assertTrue((self.state / "worktrees" / "AAA-001" / "src" / "feature.py").exists())
        self.assertEqual(f.status()["AAA-001"], "VERIFIED")
        f.close()

    def test_forbidden_file_causes_hold_and_one_fix(self):
        self.write_plan([self.task()])
        count = [0]
        def evil(cwd, prompt):
            count[0] += 1
            (cwd / "README.md").write_text("changed\n", encoding="utf-8")
            return 0, "ok"
        f = Factory(self.repo, self.plan, self.state, coder=evil)
        result = f.run_one(True)
        self.assertEqual(result["status"], "HOLD")
        self.assertEqual(count[0], 2)
        self.assertEqual(f.status()["AAA-001"], "HOLD")
        f.close()

    def test_dependency_blocks_until_reviewed(self):
        self.write_plan([self.task("AAA-001"),
                         self.task("BBB-002", ["AAA-001"])])
        f = Factory(self.repo, self.plan, self.state, coder=self.fake_coder)
        self.assertEqual(f.next_task()["id"], "AAA-001")
        self.assertEqual(f.run_one(True)["status"], "VERIFIED")
        self.assertEqual(f.next_task()["id"], "BBB-002")
        f.close()

    def test_single_worker_lock(self):
        with single_worker_lock(self.state):
            with self.assertRaises(ContractError):
                with single_worker_lock(self.state):
                    pass
        with single_worker_lock(self.state):
            pass

    def test_independent_job_proceeds_after_hold(self):
        self.write_plan([self.task("AAA-001"), self.task("BBB-002")])
        calls = [0]
        def fail_first(cwd, prompt):
            calls[0] += 1
            if "AAA-001" in prompt:
                return 1, "synthetic model failure"
            return self.fake_coder(cwd, prompt)
        f = Factory(self.repo, self.plan, self.state, coder=fail_first)
        self.assertEqual(f.run_one(True)["status"], "HOLD")
        self.assertEqual(f.next_task()["id"], "BBB-002")
        self.assertEqual(f.run_one(True)["status"], "VERIFIED")
        f.close()

    def test_resume_contract_changes_rejected(self):
        self.write_plan([self.task()])
        Factory(self.repo, self.plan, self.state, coder=self.fake_coder).close()
        t = self.task()
        t["goal"] = "modified"
        self.write_plan([t])
        with self.assertRaises(ContractError):
            Factory(self.repo, self.plan, self.state, coder=self.fake_coder)

if __name__ == "__main__":
    unittest.main()
