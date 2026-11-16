import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from axdev.core import ContractError
from scripts.fleet import create_manifest, load_manifest, fleet_run, fleet_status, fleet_signal


class FleetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.settings = []
        self.manifest = self.root / "private" / "fleet.json"
        for n in range(2):
            repo = self.root / ("project" + str(n))
            (repo / ".git").mkdir(parents=True)
            plan = self.root / ("plan" + str(n) + ".json")
            plan.write_text('{"version":1,"tasks":[]}', encoding="utf-8")
            settings = self.root / ("settings" + str(n) + ".json")
            settings.write_text(json.dumps({
                "version": 1,
                "repo": str(repo),
                "plan": str(plan),
                "state": str(self.root / ("state" + str(n))),
                "model": "ollama/qwen3:4b-instruct",
                "max_tasks": 100,
                "plan_sha256": hashlib.sha256(plan.read_bytes()).hexdigest()
            }), encoding="utf-8")
            self.settings.append(settings)

    def configure(self):
        return create_manifest(self.settings, self.manifest)

    def test_configure_and_preview_never_execute_model(self):
        created = self.configure()
        self.assertTrue(created["created"])
        self.assertEqual(created["projects"], 2)
        with self.assertRaisesRegex(ContractError, "no overwrite"):
            self.configure()
        manifest, jobs = load_manifest(self.manifest)
        self.assertEqual(manifest, self.manifest)
        self.assertEqual(len(jobs), 2)
        stub = Mock(side_effect=AssertionError("no subprocess allowed"))
        self.assertEqual(fleet_run(self.manifest, runner=stub)["status"], "DRY_RUN")
        self.assertEqual(stub.call_count, 0)
        self.assertFalse((self.manifest.parent / ".axdev-fleet-state").exists())

    def test_execute_requires_two_explicit_flags(self):
        self.configure()
        with self.assertRaisesRegex(ContractError, "BOTH"):
            fleet_run(self.manifest, execute=True, confirm=False)
        with self.assertRaisesRegex(ContractError, "BOTH"):
            fleet_run(self.manifest, execute=False, confirm=True)

    def test_independent_projects_sequential_and_per_project_task_cap(self):
        self.configure()
        invocations = []
        def runner(argv, **kwargs):
            invocations.append(argv)
            return subprocess.CompletedProcess(argv, [2, 0][len(invocations)-1])
        result = fleet_run(self.manifest, execute=True, confirm=True,
                           max_projects=2, max_tasks=3, runner=runner)
        self.assertEqual(result["status"], "FINISHED_WITH_HOLDS")
        self.assertEqual([x["exit_code"] for x in result["projects"]], [2, 0])
        self.assertEqual(len(invocations), 2)
        self.assertTrue(all("--execute" in x and x[-2:] == ["--max-tasks", "3", "--execute"][-2:]
                            for x in invocations))
        self.assertEqual(len((self.manifest.parent / ".axdev-fleet-state" /
                              "fleet-events.jsonl").read_text().splitlines()), 2)

    def test_one_project_cap(self):
        self.configure()
        runner = Mock(return_value=subprocess.CompletedProcess([], 0))
        result = fleet_run(self.manifest, execute=True, confirm=True,
                           max_projects=1, runner=runner)
        self.assertEqual(len(result["projects"]), 1)
        runner.assert_called_once()

    def test_stop_prevents_spawning_and_resume_requires_confirmation(self):
        self.configure()
        fleet_signal(self.manifest, "stop")
        self.assertTrue(fleet_status(self.manifest)["stop_requested"])
        runner = Mock(side_effect=AssertionError("do not spawn model"))
        result = fleet_run(self.manifest, execute=True, confirm=True, runner=runner)
        self.assertEqual(result["projects"][0]["status"], "STOP_REQUESTED")
        runner.assert_not_called()
        with self.assertRaisesRegex(ContractError, "--confirm"):
            fleet_signal(self.manifest, "resume")
        self.assertFalse(fleet_signal(self.manifest, "resume", True)["stop_requested"])

    def test_settings_tampering_fails_before_any_project(self):
        self.configure()
        obj = json.loads(self.settings[1].read_text())
        obj["model"] = "openai/notlocal"
        self.settings[1].write_text(json.dumps(obj))
        with self.assertRaises(ContractError):
            fleet_run(self.manifest, execute=True, confirm=True,
                      runner=Mock(side_effect=AssertionError("not spawned")))

    def test_plan_tampering_fails_before_any_project(self):
        self.configure()
        plan = self.root / "plan1.json"
        plan.write_text('{"version":1,"tasks":[1]}')
        with self.assertRaises(ContractError):
            fleet_run(self.manifest, execute=True, confirm=True,
                      runner=Mock(side_effect=AssertionError("not spawned")))

    def test_emergency_cooperative_stop_still_works_after_plan_corruption(self):
        self.configure()
        (self.root / "plan1.json").write_text("corrupted")
        stopped = fleet_signal(self.manifest, "stop")
        self.assertTrue(stopped["stop_requested"])
        with self.assertRaises(ContractError):
            fleet_signal(self.manifest, "resume", True)

    def test_duplicate_project_rejected(self):
        with self.assertRaisesRegex(ContractError, "duplicate"):
            create_manifest([self.settings[0], self.settings[0]], self.manifest)
        self.assertFalse(self.manifest.exists())

    def test_negative_project_limits_refused(self):
        self.configure()
        for max_projects, max_tasks in ((0, 10), (1, 101), (11, 1)):
            with self.assertRaises(ContractError):
                fleet_run(self.manifest, execute=True, confirm=True,
                          max_projects=max_projects, max_tasks=max_tasks)


if __name__ == "__main__":
    unittest.main()
