import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from axdev.core import git

from axdev.core import ContractError, Factory, load_plan, single_worker_lock
from scripts.configure_queue import main as configure_queue
from scripts.run_configured_queue import main as run_configured_queue

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

    def test_stop_signal_prevents_first_model_call(self):
        self.write_plan([self.task()])
        f = Factory(self.repo, self.plan, self.state, coder=self.fake_coder)
        (self.state / "STOP.REQUESTED").write_text("stop", encoding="utf-8")
        result = f.run_many(2, True)
        self.assertEqual(result[0]["status"], "STOP_REQUESTED")
        self.assertEqual(f.status()["AAA-001"], "QUEUED")
        self.assertFalse((self.state / "worktrees" / "AAA-001").exists())
        f.close()

    def test_stop_between_jobs_resume_and_local_runtime_metrics(self):
        a, b = self.task("AAA-001"), self.task("BBB-002")
        b["files"] = ["src/addon.py"]
        self.write_plan([a, b])
        calls = []
        def coder(workspace, prompt):
            if "AAA-001" in prompt:
                calls.append("AAA-001")
                result = self.fake_coder(workspace, prompt)
                (self.state / "STOP.REQUESTED").write_text("pause")
                return result
            calls.append("BBB-002")
            (workspace / "src" / "addon.py").write_text("value = 43\n")
            return 0, "ok"
        f = Factory(self.repo, self.plan, self.state, coder=coder)
        result = f.run_many(3, True)
        self.assertEqual([x["status"] for x in result],
                         ["VERIFIED", "STOP_REQUESTED"])
        self.assertEqual(calls, ["AAA-001"])
        self.assertEqual(f.status()["BBB-002"], "QUEUED")
        (self.state / "STOP.REQUESTED").unlink()
        second = f.run_many(3, True)
        self.assertEqual(second[0]["status"], "VERIFIED")
        self.assertEqual(calls, ["AAA-001", "BBB-002"])
        events = [json.loads(x) for x in
                  (self.state / "run-events.jsonl").read_text().splitlines()]
        self.assertEqual(len(events), 2)
        self.assertEqual([x["task_id"] for x in events], ["AAA-001", "BBB-002"])
        self.assertTrue(all(x["duration_seconds"] >= 0 for x in events))
        self.assertTrue(all(x["commit"] for x in events))
        f.close()

    def test_review_subprocess_has_no_parent_credentials_or_real_home(self):
        from axdev import core as core_module
        self.write_plan([self.task()])
        f = Factory(self.repo, self.plan, self.state, coder=self.fake_coder)
        self.addCleanup(f.close)
        workspace = f._workspace("AAA-001")
        self.fake_coder(workspace, "synthetic")
        actual_call = core_module.call
        captured = []
        def wrapped(argv, cwd, timeout=60, env=None, output_limit=6000):
            if argv and argv[0] == sys.executable and "-m" in argv:
                captured.append(env.copy())
            return actual_call(argv, cwd, timeout=timeout, env=env,
                               output_limit=output_limit)
        with patch.dict(os.environ, {
                 "AXDEV_SYNTHETIC_API_KEY": "never_send",
                 "GITHUB_TOKEN": "synthetic_token",
                 "OPENAI_API_KEY": "synthetic_key"}):
            with patch("axdev.core.call", side_effect=wrapped):
                ok, details = f._review(self.task(), workspace)
        self.assertTrue(ok, details)
        self.assertTrue(captured)
        for env in captured:
            self.assertNotIn("GITHUB_TOKEN", env)
            self.assertNotIn("OPENAI_API_KEY", env)
            self.assertNotIn("AXDEV_SYNTHETIC_API_KEY", env)
            self.assertEqual(env["HOME"], str((self.state / "review-home").resolve()))
            self.assertEqual(env["PYTHONNOUSERSITE"], "1")
        f.close()

    def test_python_test_bytecode_never_enters_reviewed_git_commit(self):
        self.write_plan([self.task()])
        f = Factory(self.repo, self.plan, self.state, coder=self.fake_coder)
        result = f.run_one(True)
        self.assertEqual(result["status"], "VERIFIED", result)
        names = git(self.repo, "diff-tree", "--no-commit-id", "--name-only",
                    "-r", result["commit"])
        self.assertEqual(names.splitlines(), ["src/feature.py"])
        work = self.state / "worktrees" / "AAA-001"
        self.assertFalse((work / "tests" / "__pycache__").exists())
        f.close()

    def test_acceptance_script_new_unapproved_file_causes_hold(self):
        (self.repo / "tests" / "test_base.py").write_text(
            "import unittest\nfrom pathlib import Path\n"
            "class T(unittest.TestCase):\n"
            " def test_side_effect(self):\n"
            "  Path('tests/generated.txt').write_text('unapproved')\n")
        self._git("add", "tests/test_base.py")
        self._git("commit", "-m", "synthetic side-effect fixture")
        self.write_plan([self.task()])
        f = Factory(self.repo, self.plan, self.state, coder=self.fake_coder)
        base = git(self.repo, "rev-parse", "HEAD")
        result = f.run_one(True)
        self.assertEqual(result["status"], "HOLD", result)
        self.assertTrue(
            "POST_CHECK_CHANGED_PATHS" in result["reason"]
            or "FORBIDDEN_PATHS" in result["reason"], result)
        self.assertEqual(git(self.repo, "rev-parse", f.integration_ref), base)
        f.close()

    def test_acceptance_script_mutating_allowed_source_causes_hold(self):
        (self.repo / "tests" / "test_base.py").write_text(
            "import unittest\nfrom pathlib import Path\n"
            "class T(unittest.TestCase):\n"
            " def test_side_effect(self):\n"
            "  Path('src/feature.py').write_text('modified by test')\n")
        self._git("add", "tests/test_base.py")
        self._git("commit", "-m", "synthetic mutation fixture")
        self.write_plan([self.task()])
        f = Factory(self.repo, self.plan, self.state, coder=self.fake_coder)
        result = f.run_one(True)
        self.assertEqual(result["status"], "HOLD", result)
        self.assertIn("POST_CHECK_SOURCE_MUTATION", result["reason"])
        f.close()

    def test_windows_reserved_and_alias_paths_are_rejected_portably(self):
        for name in ("src/CON.txt", "src/prn.py", "src/LPT9", "src/AUX",
                     "src/file.", "src/file ", "src/foo?bar.py",
                     "src/p|q.py", "src/nul", "src/COM1.py"):
            task = self.task()
            task["files"] = [name]
            self.write_plan([task])
            with self.subTest(name=name), self.assertRaises(ContractError):
                load_plan(self.plan)

    def test_case_colliding_paths_rejected_for_windows(self):
        t = self.task()
        t["files"] = ["src/Main.py", "src/main.py"]
        self.write_plan([t])
        with self.assertRaisesRegex(ContractError, "Windows"):
            load_plan(self.plan)

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

    def test_resume_review_does_not_reinvoke_model(self):
        self.write_plan([self.task()])
        f = Factory(self.repo, self.plan, self.state, coder=self.fake_coder)
        workspace = f._workspace("AAA-001")
        self.fake_coder(workspace, "fixture")
        f._set("AAA-001", "REVIEW")
        def forbidden_call(cwd, prompt):
            raise AssertionError("model must not be rerun at REVIEW checkpoint")
        f.coder = forbidden_call
        self.assertEqual(f.run_one(True)["status"], "VERIFIED")
        f.close()

    def test_fix_budget_survives_restart(self):
        self.write_plan([self.task()])
        f = Factory(self.repo, self.plan, self.state, coder=self.fake_coder)
        f._workspace("AAA-001")
        f._set("AAA-001", "REVIEW")
        f.db.execute("UPDATE runs SET attempts=1 WHERE id='AAA-001'")
        f.db.commit()
        def forbidden_call(cwd, prompt):
            raise AssertionError("second fix is forbidden")
        f.coder = forbidden_call
        self.assertEqual(f.run_one(True)["status"], "HOLD")
        f.close()

    def test_verified_changes_flow_to_next_worktree(self):
        a = self.task("AAA-001")
        b = self.task("BBB-002", ["AAA-001"])
        b["files"] = ["src/addon.py"]
        self.write_plan([a, b])
        def coder(cwd, prompt):
            if "AAA-001" in prompt:
                return self.fake_coder(cwd, prompt)
            self.assertTrue((cwd / "src" / "feature.py").exists(),
                            "next task must receive preceding verified code")
            (cwd / "src" / "addon.py").write_text(
                "from src.feature import value\nother = value + 1\n", encoding="utf-8")
            return 0, "ok"
        f = Factory(self.repo, self.plan, self.state, coder=coder)
        results = f.run_many(2, True)
        self.assertEqual([x["status"] for x in results],
                         ["VERIFIED", "VERIFIED"], results)
        integration = git(self.repo, "rev-parse", f.integration_ref)
        self.assertEqual(integration, results[-1]["commit"])
        self.assertTrue((self.state / "worktrees" / "BBB-002" / "src" / "feature.py").exists())
        self.assertFalse((self.repo / "src").exists(),
                         "original checkout must not be written")
        f.close()

    def test_prepared_commit_recovers_without_model_call(self):
        self.write_plan([self.task()])
        f = Factory(self.repo, self.plan, self.state, coder=self.fake_coder)
        workspace = f._workspace("AAA-001")
        self.fake_coder(workspace, "prepare")
        self.assertTrue(f._review(self.task(), workspace)[0])
        git(workspace, "add", "--", "src/feature.py")
        git(workspace, "commit", "-m", "prepared")
        commit = git(workspace, "rev-parse", "HEAD")
        f._set("AAA-001", "PREPARED", "pending", commit)
        def forbidden_call(cwd, prompt):
            raise AssertionError("must not recode prepared commit")
        f.coder = forbidden_call
        self.assertEqual(f.run_one(True)["status"], "VERIFIED")
        self.assertEqual(git(self.repo, "rev-parse", f.integration_ref), commit)
        self.assertEqual(f.run_one(True)["status"], "NO_READY_TASK")
        f.close()

    def test_opencode_policy_pins_provider_and_only_task_edit(self):
        self.write_plan([self.task()])
        f = Factory(self.repo, self.plan, self.state, coder=self.fake_coder)
        f._active_allowed_files = ("src/feature.py",)
        intercepted = {}
        def capture(argv, cwd, timeout=60, env=None, output_limit=6000):
            intercepted.update({"argv": argv, "cwd": cwd, "env": env})
            if argv == ["opencode", "debug", "config"]:
                return 0, env["OPENCODE_CONFIG_CONTENT"]
            return 0, "synthetic"
        with patch("axdev.core.shutil.which", return_value="/fake/opencode"), \
             patch("axdev.core.call", side_effect=capture):
            rc, out = f._opencode(self.repo, "synthetic only")
        self.assertEqual(rc, 0)
        settings = json.loads(intercepted["env"]["OPENCODE_CONFIG_CONTENT"])
        self.assertNotIn("enabled_providers", settings)
        self.assertNotIn("package", settings["providers"]["ollama"])
        self.assertIn({"action": "plugin.use", "resource": "opencode.provider.ollama",
                       "effect": "allow"}, settings["policies"])
        self.assertEqual(settings["policies"][:2], [
            {"action": "provider.use", "resource": "*", "effect": "deny"},
            {"action": "provider.use", "resource": "ollama", "effect": "allow"}])
        self.assertIn({"action": "tool.use", "resource": "shell:*", "effect": "deny"},
                      settings["policies"])
        edits = [rule for rule in settings["permissions"] if rule["action"] == "edit"]
        self.assertEqual(edits[-1],
                         {"action": "edit", "resource": "src/feature.py", "effect": "allow"})
        self.assertEqual(intercepted["env"]["OPENCODE_AUTO_SHARE"], "false")
        self.assertIn("--model", intercepted["argv"])
        self.assertIn("--standalone", intercepted["argv"])
        self.assertEqual(settings["permissions"][0],
                         {"action": "*", "resource": "*", "effect": "deny"})
        f.close()

    def test_opencode_effective_config_mismatch_blocks_model_execution(self):
        self.write_plan([self.task()])
        f = Factory(self.repo, self.plan, self.state, coder=self.fake_coder)
        f._active_allowed_files = ("src/feature.py",)
        invoked = []
        def tampered(argv, cwd, timeout=60, env=None, output_limit=6000):
            invoked.append(argv)
            if argv == ["opencode", "debug", "config"]:
                config = json.loads(env["OPENCODE_CONFIG_CONTENT"])
                config["policies"].append(
                    {"action": "provider.use", "resource": "openai", "effect": "allow"})
                return 0, json.dumps(config)
            raise AssertionError("model run must be blocked")
        with (patch("axdev.core.shutil.which", return_value="/fake/opencode"),
              patch("axdev.core.call", side_effect=tampered)):
            rc, message = f._opencode(self.repo, "test only")
        self.assertEqual(rc, 125)
        self.assertEqual(invoked, [["opencode", "debug", "config"]])
        self.assertIn("could not be verified", message)
        f.close()

    def test_interrupted_coding_reviews_existing_diff_without_model(self):
        self.write_plan([self.task()])
        f = Factory(self.repo, self.plan, self.state, coder=self.fake_coder)
        workspace = f._workspace("AAA-001")
        self.fake_coder(workspace, "partial")
        f._set("AAA-001", "CODING")
        def must_not_call(cwd, prompt):
            raise AssertionError("interrupted coder must not be repeated")
        f.coder = must_not_call
        self.assertEqual(f.run_one(True)["status"], "VERIFIED")
        f.close()

    def test_nested_sensitive_file_is_rejected(self):
        for path in ["src/.env", "src/.git/config", ".github/workflows/job.yml"]:
            task = self.task()
            task["files"] = [path]
            self.write_plan([task])
            with self.assertRaises(ContractError):
                load_plan(self.plan)

    def test_ruff_is_optional_approved_check(self):
        task = self.task()
        task["checks"].append(["ruff", "check", "--no-cache", "src"])
        self.write_plan([task])
        self.assertEqual(len(load_plan(self.plan)[0]["checks"]), 2)

    @unittest.skipIf(os.name == "nt", "symlink privileges vary on Windows")
    def test_parent_symlink_blocks_before_coder(self):
        self.write_plan([self.task()])
        f = Factory(self.repo, self.plan, self.state, coder=self.fake_coder)
        work = f._workspace("AAA-001")
        (work / "src").symlink_to(self.root, target_is_directory=True)
        def forbidden(cwd, prompt):
            raise AssertionError("symlink must be rejected before coder starts")
        f.coder = forbidden
        self.assertEqual(f.run_one(True)["status"], "HOLD")
        f.close()

    def test_one_time_local_queue_configuration_and_dry_run(self):
        self.write_plan([self.task()])
        settings = self.root / "private" / "settings.json"
        with patch("builtins.print"):
            configure_queue(["--repo", str(self.repo),
                             "--plan", str(self.plan), "--settings", str(settings)])
        self.assertTrue(settings.exists())
        value = json.loads(settings.read_text(encoding="utf-8"))
        self.assertEqual(value["model"], "ollama/qwen3:4b-instruct")
        self.assertTrue(Path(value["state"]).is_relative_to(settings.parent))
        with patch("builtins.print"):
            self.assertEqual(run_configured_queue(["--settings", str(settings)]), 0)
        state = Path(value["state"])
        self.assertFalse((state / "worktrees" / "AAA-001").exists())
        with self.assertRaises(SystemExit):
            configure_queue(["--repo", str(self.repo),
                             "--plan", str(self.plan), "--settings", str(settings)])

    def test_pinned_remote_queue_idempotent_offline_fallback(self):
        from urllib.error import URLError
        self.write_plan([self.task()])
        settings = self.root / "private" / "settings.json"
        flags = ["--repo", str(self.repo), "--plan", str(self.plan),
                 "--settings", str(settings),
                 "--github-source", "hibi89/Freelancer",
                 "--github-branch", "tools/ax-dev-factory-local",
                 "--github-path", "examples/sample-plan.json",
                 "--github-sha", "a" * 40]
        with patch("builtins.print"):
            configure_queue(flags)
        saved = json.loads(settings.read_text(encoding="utf-8"))
        self.assertEqual(saved["github"]["sha"], "a" * 40)
        self.assertEqual(len(saved["plan_sha256"]), 64)
        with patch("scripts.run_configured_queue.sync_public_plan") as importer:
            with patch("builtins.print"):
                self.assertEqual(run_configured_queue(["--settings", str(settings)]), 0)
        importer.assert_called_once()
        with patch("scripts.run_configured_queue.sync_public_plan",
                   side_effect=URLError("synthetic offline")):
            with patch("builtins.print"):
                self.assertEqual(run_configured_queue(["--settings", str(settings)]), 0)
        self.assertFalse((self.state / "worktrees" / "AAA-001").exists())

    def test_pinned_remote_queue_rejects_local_tampering_before_network(self):
        self.write_plan([self.task()])
        settings = self.root / "private" / "settings.json"
        with patch("builtins.print"):
            configure_queue(["--repo", str(self.repo), "--plan", str(self.plan),
                             "--settings", str(settings),
                             "--github-source", "hibi89/Freelancer",
                             "--github-branch", "tools/ax-dev-factory-local",
                             "--github-path", "examples/sample-plan.json",
                             "--github-sha", "a" * 40])
        self.plan.write_text('{"version":1,"tasks":[]}', encoding="utf-8")
        with patch("scripts.run_configured_queue.sync_public_plan") as importer:
            with self.assertRaisesRegex(ContractError, "SHA256 differs"):
                run_configured_queue(["--settings", str(settings), "--execute"])
        importer.assert_not_called()
        self.assertFalse((self.state / "worktrees" / "AAA-001").exists())

    def test_remote_source_change_fails_closed_before_coder(self):
        self.write_plan([self.task()])
        settings = self.root / "private" / "settings.json"
        with patch("builtins.print"):
            configure_queue(["--repo", str(self.repo), "--plan", str(self.plan),
                             "--settings", str(settings),
                             "--github-source", "hibi89/Freelancer",
                             "--github-branch", "tools/ax-dev-factory-local",
                             "--github-path", "examples/sample-plan.json",
                             "--github-sha", "a" * 40])
        with patch("scripts.run_configured_queue.sync_public_plan",
                   side_effect=ContractError("branch changed since approval")):
            with self.assertRaisesRegex(ContractError, "branch changed"):
                run_configured_queue(["--settings", str(settings), "--execute"])
        self.assertFalse((self.state / "worktrees" / "AAA-001").exists())

    def test_rate_limit_403_uses_approved_cache_only(self):
        from urllib.error import HTTPError
        self.write_plan([self.task()])
        settings = self.root / "private" / "settings.json"
        with patch("builtins.print"):
            configure_queue(["--repo", str(self.repo), "--plan", str(self.plan),
                             "--settings", str(settings),
                             "--github-source", "hibi89/Freelancer",
                             "--github-branch", "tools/ax-dev-factory-local",
                             "--github-path", "examples/sample-plan.json",
                             "--github-sha", "a" * 40])
        error = HTTPError("https://api.github.com", 403, "rate limit",
                          {"X-RateLimit-Remaining": "0"}, None)
        with patch("scripts.run_configured_queue.sync_public_plan", side_effect=error):
            with patch("builtins.print"):
                self.assertEqual(run_configured_queue(["--settings", str(settings)]), 0)

    def test_unrelated_403_fails_closed(self):
        from urllib.error import HTTPError
        self.write_plan([self.task()])
        settings = self.root / "private" / "settings.json"
        with patch("builtins.print"):
            configure_queue(["--repo", str(self.repo), "--plan", str(self.plan),
                             "--settings", str(settings),
                             "--github-source", "hibi89/Freelancer",
                             "--github-branch", "tools/ax-dev-factory-local",
                             "--github-path", "examples/sample-plan.json",
                             "--github-sha", "a" * 40])
        forbidden = HTTPError("https://api.github.com", 403, "forbidden", {}, None)
        with patch("scripts.run_configured_queue.sync_public_plan", side_effect=forbidden):
            with self.assertRaises(HTTPError):
                run_configured_queue(["--settings", str(settings)])

    def test_configure_queue_rejects_partial_github_coordinates(self):
        self.write_plan([self.task()])
        settings = self.root / "private" / "settings.json"
        with self.assertRaises(SystemExit):
            configure_queue(["--repo", str(self.repo), "--plan", str(self.plan),
                             "--settings", str(settings),
                             "--github-source", "hibi89/Freelancer"])
        self.assertFalse(settings.exists())

    def test_failed_prerequisites_do_not_consume_or_hold_any_task(self):
        self.write_plan([self.task()])
        settings = self.root / "private" / "settings.json"
        with patch("builtins.print"):
            configure_queue(["--repo", str(self.repo), "--plan", str(self.plan),
                             "--settings", str(settings)])
        configured = json.loads(settings.read_text(encoding="utf-8"))
        state = Path(configured["state"])
        with patch("scripts.preflight.inspect",
                   return_value={"ready_for_disposable_model_trial": False,
                                 "blockers": ["synthetic local model missing"]}):
            with self.assertRaisesRegex(ContractError, "prerequisites missing"):
                run_configured_queue(["--settings", str(settings), "--execute"])
        self.assertFalse((state / "factory.sqlite3").exists())
        self.assertFalse((state / "worktrees").exists())

    def test_configure_queue_exclusive_create_preserves_original(self):
        self.write_plan([self.task()])
        settings = self.root / "private" / "settings.json"
        settings.parent.mkdir()
        settings.write_text("ORIGINAL")
        with self.assertRaises(SystemExit):
            configure_queue(["--repo", str(self.repo), "--plan", str(self.plan),
                             "--settings", str(settings)])
        self.assertEqual(settings.read_text(), "ORIGINAL")

    def test_configure_queue_rejects_symlinked_settings(self):
        self.write_plan([self.task()])
        existing = self.root / "existing"
        existing.write_text("SAFE")
        target = self.root / "path"
        try:
            target.symlink_to(existing)
        except (OSError, NotImplementedError):
            self.skipTest("symlink unavailable")
        with self.assertRaises(SystemExit):
            configure_queue(["--repo", str(self.repo), "--plan", str(self.plan),
                             "--settings", str(target)])
        self.assertEqual(existing.read_text(), "SAFE")

    def test_configure_queue_rejects_invalid_ollama_id(self):
        self.write_plan([self.task()])
        settings = self.root / "private" / "settings.json"
        with self.assertRaises(SystemExit):
            configure_queue(["--repo", str(self.repo), "--plan", str(self.plan),
                             "--model", "ollama/", "--settings", str(settings)])
        self.assertFalse(settings.exists())

    def test_configure_queue_refuses_non_git_target(self):
        self.write_plan([self.task()])
        with self.assertRaises(SystemExit):
            configure_queue(["--repo", str(self.root),
                             "--plan", str(self.plan),
                             "--settings", str(self.root / "missing.json")])

    def test_preview_pr_checks_verified_commit_and_origin_without_remote_write(self):
        from scripts.publish_pr import preview
        self.write_plan([self.task()])
        self._git("remote", "add", "origin", "https://github.com/hibi89/Freelancer.git")
        settings = self.root / "private" / "settings.json"
        with patch("builtins.print"):
            configure_queue(["--repo", str(self.repo), "--plan", str(self.plan),
                             "--settings", str(settings)])
        configured_state = Path(json.loads(settings.read_text(encoding="utf-8"))["state"])
        factory = Factory(self.repo, self.plan, configured_state, coder=self.fake_coder)
        record = factory.run_one(True)
        self.assertEqual(record["status"], "VERIFIED")
        factory.close()
        with patch("scripts.publish_pr.publish_draft", side_effect=AssertionError("unexpected remote write")):
            preview_result = preview(settings, "hibi89/Freelancer", "main",
                                     record["commit"], "axdev/review-aaa-001")
        self.assertEqual(preview_result["verified_task_ids"], ["AAA-001"])
        self.assertEqual(preview_result["changed_files"], ["src/feature.py"])
        self.assertFalse(preview_result["remote_write_executed"])
        self.assertFalse(preview_result["pr_created"])
        with self.assertRaisesRegex(ContractError, "moved or does not match"):
            preview(settings, "hibi89/Freelancer", "main", "a" * 40,
                    "axdev/review-aaa-001")
        with self.assertRaisesRegex(ContractError, "origin URL"):
            preview(settings, "someoneelse/Freelancer", "main",
                    record["commit"], "axdev/review-aaa-001")

    def test_pr_publish_requires_both_explicit_flags(self):
        from scripts.publish_pr import main
        with self.assertRaisesRegex(ContractError, "BOTH"):
            main(["--approved-repo", "hibi89/Freelancer", "--base", "main",
                  "--expected-commit", "a" * 40, "--head", "axdev/review-aaa-001",
                  "--publish"])

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
