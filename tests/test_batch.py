"""Batch mode: independent staging, verified linear commits, crash and HOLD gates."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from axdev.core import Factory, git


class ImplementationBatchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.git("init")
        self.git("config", "user.name", "AXDev Test")
        self.git("config", "user.email", "axdev-test@example.invalid")
        (self.repo / "README.md").write_text("synthetic\n", encoding="utf-8")
        (self.repo / "tests").mkdir()
        (self.repo / "tests" / "test_base.py").write_text(
            "import unittest\nclass T(unittest.TestCase):\n"
            " def test_base(self): self.assertTrue(True)\n", encoding="utf-8")
        self.git("add", ".")
        self.git("commit", "-m", "fixture")
        self.plan = self.root / "plan.json"
        self.state = self.root / "state"

    def git(self, *args):
        subprocess.run(["git", *args], cwd=self.repo, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def task(self, tid="AAA-001", path="src/feature.py", deps=None):
        return {"id": tid, "goal": "Create a safe tested addition",
                "files": [path], "depends_on": deps or [],
                "checks": [["python", "-m", "unittest", "discover", "-s", "tests", "-q"]]}

    def setup_factory(self, tasks, coder):
        self.plan.write_text(json.dumps({"version": 1, "tasks": tasks}), encoding="utf-8")
        f = Factory(self.repo, self.plan, self.state, coder=coder)
        self.addCleanup(f.close)
        return f

    def coder(self, cwd, prompt):
        (cwd / "src").mkdir(exist_ok=True)
        path = "addon.py" if "BBB-002" in prompt else "feature.py"
        (cwd / "src" / path).write_text("value = 42\n", encoding="utf-8")
        return 0, "synthetic"

    def test_stages_multiple_independent_tasks_before_review_then_commits_linearly(self):
        order = []
        def coder(cwd, prompt):
            order.append("code_" + ("A" if "AAA-001" in prompt else "B"))
            return self.coder(cwd, prompt)
        a = self.task()
        b = self.task("BBB-002", "src/addon.py")
        f = self.setup_factory([a, b], coder)
        orig_review = f._review
        def review(task, work):
            order.append("review_" + task["id"][:3])
            return orig_review(task, work)
        f._review = review
        results = f.run_implementation_batch(2, True)
        self.assertEqual([r["status"] for r in results],
                         ["IMPLEMENTED", "IMPLEMENTED", "VERIFIED", "VERIFIED"], results)
        self.assertEqual(order, ["code_A", "code_B", "review_AAA", "review_BBB"])
        self.assertEqual(git(self.repo, "rev-parse", results[3]["commit"] + "^"),
                         results[2]["commit"])
        self.assertEqual(git(self.repo, "rev-parse", f.integration_ref),
                         results[3]["commit"])
        self.assertFalse((self.repo / "src").exists())
        self.assertEqual(f.status(), {"AAA-001": "VERIFIED", "BBB-002": "VERIFIED"})
        events = [json.loads(line) for line in
                  (self.state / "run-events.jsonl").read_text().splitlines()]
        self.assertEqual([e["status"] for e in events],
                         ["IMPLEMENTED", "IMPLEMENTED", "VERIFIED", "VERIFIED"])
        self.assertEqual(f.run_implementation_batch(2, True), [])

    def test_dependent_tasks_must_wait_for_verified_predecessor(self):
        def coder(cwd, prompt):
            (cwd / "src").mkdir(exist_ok=True)
            name = "addon.py" if "BBB-002" in prompt else "feature.py"
            (cwd / "src" / name).write_text("value = 7\n")
            return 0, "ok"
        f = self.setup_factory([self.task(),
                                self.task("BBB-002", "src/addon.py", ["AAA-001"])], coder)
        first = f.run_implementation_batch(2, True)
        self.assertEqual([r["status"] for r in first], ["IMPLEMENTED", "VERIFIED"])
        self.assertEqual(f.status()["BBB-002"], "QUEUED")
        second = f.run_implementation_batch(2, True)
        self.assertEqual([r["status"] for r in second], ["IMPLEMENTED", "VERIFIED"])
        self.assertEqual(f.status()["BBB-002"], "VERIFIED")

    def test_stop_and_resume_from_implemented_without_second_model_call(self):
        calls = []
        def coder(cwd, prompt):
            calls.append(prompt)
            result = self.coder(cwd, prompt)
            (self.state / "STOP.REQUESTED").write_text("pause")
            return result
        f = self.setup_factory([self.task()], coder)
        first = f.run_implementation_batch(2, True)
        self.assertEqual([r["status"] for r in first],
                         ["IMPLEMENTED", "STOP_REQUESTED"])
        self.assertEqual(f.status()["AAA-001"], "IMPLEMENTED")
        self.assertEqual(len(calls), 1)
        (self.state / "STOP.REQUESTED").unlink()
        f.close()
        resumed = Factory(self.repo, self.plan, self.state,
                          coder=lambda *args: self.fail("model cannot be rerun"))
        self.addCleanup(resumed.close)
        second = resumed.run_implementation_batch(2, True)
        self.assertEqual([r["status"] for r in second], ["VERIFIED"], second)
        self.assertEqual(len(calls), 1)

    def test_interrupted_coding_recovers_existing_edits_no_duplicate_model(self):
        f = self.setup_factory([self.task()],
                               coder=lambda *args: self.fail("never rerun model"))
        work = f._workspace("AAA-001")
        self.coder(work, "AAA-001")
        f._set("AAA-001", "CODING", "interrupted before model result")
        results = f.run_implementation_batch(2, True)
        self.assertEqual([r["status"] for r in results], ["VERIFIED"], results)

    def test_review_failure_allows_only_one_fix_then_verified(self):
        (self.repo / "tests" / "test_base.py").write_text(
            "import unittest\nfrom src.feature import value\n"
            "class T(unittest.TestCase):\n"
            " def test_value(self): self.assertEqual(value, 42)\n")
        self.git("add", ".")
        self.git("commit", "-m", "protected acceptance")
        calls = []
        def coder(work, prompt):
            calls.append("FIX_ONCE" if "FIX_ONCE" in prompt else "CODING")
            (work / "src").mkdir(exist_ok=True)
            (work / "src" / "feature.py").write_text(
                "value = " + ("42" if "FIX_ONCE" in prompt else "0") + "\n")
            return 0, "ok"
        f = self.setup_factory([self.task()], coder)
        result = f.run_implementation_batch(1, True)
        self.assertEqual([r["status"] for r in result], ["IMPLEMENTED", "VERIFIED"], result)
        self.assertEqual(calls, ["CODING", "FIX_ONCE"])
        self.assertEqual(f.db.execute("SELECT attempts FROM runs WHERE id='AAA-001'").fetchone()[0], 1)

    def test_review_repeated_failure_holds_and_never_promotes(self):
        (self.repo / "tests" / "test_base.py").write_text(
            "import unittest\nclass T(unittest.TestCase):\n"
            " def test_fail(self): self.assertEqual(1, 2)\n")
        self.git("add", ".")
        self.git("commit", "-m", "synthetic failing acceptance")
        calls = []
        def coder(cwd, prompt):
            calls.append(prompt)
            return self.coder(cwd, prompt)
        f = self.setup_factory([self.task()], coder)
        baseline = git(self.repo, "rev-parse", f.integration_ref)
        result = f.run_implementation_batch(1, True)
        self.assertEqual([r["status"] for r in result], ["IMPLEMENTED", "HOLD"], result)
        self.assertEqual(len(calls), 2)
        self.assertEqual(f.status()["AAA-001"], "HOLD")
        self.assertEqual(git(self.repo, "rev-parse", f.integration_ref), baseline)
        self.assertEqual(f.run_implementation_batch(1, True), [])

    def test_overlapping_files_are_not_coded_in_same_stage(self):
        a, b = self.task(), self.task("BBB-002")
        coded = []
        def coder(cwd, prompt):
            coded.append("B" if "BBB-002" in prompt else "A")
            (cwd / "src").mkdir(exist_ok=True)
            (cwd / "src" / "feature.py").write_text("value = 1\n")
            return 0, "ok"
        f = self.setup_factory([a, b], coder)
        first = f.run_implementation_batch(2, True)
        self.assertEqual([r["status"] for r in first], ["IMPLEMENTED", "VERIFIED"])
        self.assertEqual(coded, ["A"])
        second = f.run_implementation_batch(2, True)
        # B's modified bytes are identical to already verified A, so
        # there is no change. Reviewer cannot promote a no-op.
        self.assertEqual(second[0]["status"], "REVIEW")
        self.assertEqual(second[-1]["status"], "HOLD")
        self.assertEqual(coded, ["A", "B", "B"])

    def test_single_batch_invocation_chains_multiple_dependency_waves(self):
        tasks = [self.task(), self.task("BBB-002", "src/addon.py", ["AAA-001"])]
        seen = []
        def coder(work, prompt):
            seen.append("B" if "BBB-002" in prompt else "A")
            return self.coder(work, prompt)
        f = self.setup_factory(tasks, coder)
        result = f.run_implementation_batch(5, True)
        self.assertEqual([r["status"] for r in result],
                         ["IMPLEMENTED", "VERIFIED", "IMPLEMENTED", "VERIFIED"], result)
        self.assertEqual(seen, ["A", "B"])
        self.assertEqual(f.status()["BBB-002"], "VERIFIED")

    def test_restarted_staged_source_tampering_is_held_not_promoted(self):
        calls = []
        def coder(work, prompt):
            calls.append(prompt)
            result = self.coder(work, prompt)
            (self.state / "STOP.REQUESTED").write_text("stop")
            return result
        f = self.setup_factory([self.task()], coder)
        first = f.run_implementation_batch(1, True)
        self.assertEqual([r["status"] for r in first],
                         ["IMPLEMENTED", "STOP_REQUESTED"], first)
        (self.state / "worktrees" / "AAA-001" / "src" / "feature.py").write_text(
            "value = 999\n")
        (self.state / "STOP.REQUESTED").unlink()
        resumed = f.run_implementation_batch(1, True)
        self.assertEqual([r["status"] for r in resumed], ["HOLD"], resumed)
        self.assertIn("bytes changed", resumed[0]["reason"])
        self.assertEqual(len(calls), 1)
        self.assertEqual(git(self.repo, "rev-parse", f.integration_ref),
                         git(self.repo, "rev-parse", "HEAD"))

    def test_batch_dry_run_never_calls_model(self):
        f = self.setup_factory([self.task()],
                               coder=lambda *args: self.fail("model called"))
        self.assertEqual(f.run_implementation_batch(3, False)[0]["status"], "DRY_RUN")
        self.assertEqual(f.status()["AAA-001"], "QUEUED")


if __name__ == "__main__":
    unittest.main()
