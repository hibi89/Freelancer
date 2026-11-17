"""Safety tests for private EXE command inbox and standalone UI helpers."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from axdev.core import ContractError
from scripts import desktop_commands as commands
from scripts.axdev_desktop import _model_label, _safe_events, _safe_status


class DesktopCommandTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.repo = root / "owned-repo"
        self.repo.mkdir()
        (self.repo / ".git").mkdir()
        self.home = root / "private-drafts"
        self.settings = root / "owner-settings.json"
        self.settings.write_text(json.dumps({
            "version": 1, "repo": str(self.repo),
            "plan": str(root / "owner-immutable-plan.json"),
            "state": str(root / "owner-state"),
            "model": "ollama/qwen3:4b-instruct", "max_tasks": 30,
            "sandbox": {
                "bundle": str(root / "offline-bundle"),
                "manifest_sha256": "a" * 64,
            },
            "daily_model_call_budget": 5,
        }), encoding="utf-8")
        self.acceptance = [{
            "module": "src.hello", "function": "greet", "args": ["AX"],
            "kwargs": {}, "expected": "Hello, AX",
        }]

    def test_free_text_creates_inert_private_draft(self):
        item = commands.save_draft("기능을 개선해줘", self.repo, home=self.home)
        self.assertEqual(item["state"], "DRAFT")
        self.assertFalse(item["model_called"])
        self.assertFalse(item["execution_started"])
        self.assertFalse((self.repo / "src").exists())
        self.assertEqual(len(commands.recent_drafts(home=self.home)), 1)
        self.assertTrue((self.home / (item["id"] + ".json")).is_file())

    def test_bad_goal_or_checkout_rejected(self):
        for value in ("", "A" * 4001, "x\x00y"):
            with self.subTest(value=value[:10]), self.assertRaises(ContractError):
                commands.save_draft(value, self.repo, home=self.home)
        with self.assertRaises(ContractError):
            commands.save_draft("좋아요", self.home / "missing", home=self.home)

    def test_contract_pinned_and_requires_independent_oracle(self):
        draft = commands.save_draft("src/hello.py 함수 구현", self.repo, home=self.home)
        with self.assertRaises(ContractError):
            commands.approve_draft(draft["id"], ["src/hello.py"], [],
                                   source_settings=self.settings, home=self.home)
        self.assertFalse((self.home / ("run-" + draft["id"])).exists())
        result = commands.approve_draft(
            draft["id"], ["src/hello.py"], self.acceptance,
            source_settings=self.settings, home=self.home)
        self.assertTrue(result["approved"])
        self.assertFalse(result["execution_started"])
        proof = commands.inspect_approval(Path(result["settings"]))
        self.assertEqual(proof["probe_count"], 1)
        self.assertEqual(proof["files"], ["src/hello.py"])
        self.assertEqual(proof["plan_sha256"], result["plan_sha256"])
        plan = Path(result["settings"]).with_name("plan.json")
        self.assertEqual(hashlib.sha256(plan.read_bytes()).hexdigest(), result["plan_sha256"])
        plan.write_text(plan.read_text(encoding="utf-8") + " ", encoding="utf-8")
        with self.assertRaises(ContractError):
            commands.inspect_approval(Path(result["settings"]))

    def test_plan_rejects_unsafe_paths_and_preserves_original_settings(self):
        original = self.settings.read_bytes()
        draft = commands.save_draft("파일 범위 제한", self.repo, home=self.home)
        for files in (["../secrets.txt"], ["tests/.env"], ["A.py", "a.py"]):
            with self.subTest(files=files), self.assertRaises(ContractError):
                commands.approve_draft(draft["id"], files, self.acceptance,
                                       source_settings=self.settings, home=self.home)
        self.assertEqual(self.settings.read_bytes(), original)

    def test_launch_requires_pinned_contract_and_one_explicit_process(self):
        draft = commands.save_draft("src/hello.py 작업", self.repo, home=self.home)
        approved = commands.approve_draft(
            draft["id"], ["src/hello.py"], self.acceptance,
            source_settings=self.settings, home=self.home)
        class DummyProcess:
            pid = 12345
        with patch("scripts.desktop_commands.subprocess.Popen", return_value=DummyProcess()) as start:
            result = commands.launch_approved(Path(approved["settings"]), app_root=self.repo)
        args = start.call_args.args[0]
        self.assertIn("--execute", args)
        self.assertEqual(args[-3:], ["--max-tasks", "1", "--execute"])
        self.assertFalse(start.call_args.kwargs["shell"] if "shell" in start.call_args.kwargs else False)
        self.assertTrue(result["execution_started"])
        self.assertEqual(result["result"], "STARTED_NOT_VERIFIED")
        self.assertEqual(self.settings.read_text(encoding="utf-8").count('"max_tasks": 30'), 1)

    def test_untrusted_approval_model_cannot_switch_to_paid_provider(self):
        source = json.loads(self.settings.read_text(encoding="utf-8"))
        source["model"] = "openai/gpt-paid"
        self.settings.write_text(json.dumps(source), encoding="utf-8")
        draft = commands.save_draft("모델 허용목록", self.repo, home=self.home)
        with self.assertRaises(ContractError):
            commands.approve_draft(draft["id"], ["src/hello.py"], self.acceptance,
                                   source_settings=self.settings, home=self.home)

    def test_events_whitelist_never_displays_token_or_model_output(self):
        state = Path(self.tmp.name) / "owner-state"
        state.mkdir()
        (state / "run-events.jsonl").write_text(
            json.dumps({"task_id": "TASK-001", "status": "VERIFIED",
                        "timestamp_utc": "2026-11-17T01:00:00Z",
                        "model_output": "TOKEN-NEVER-EXPOSE"}) + "\n"
            + json.dumps({"task_id": "TASK-002", "status": "HOLD",
                          "secret": "TOKEN-NEVER-EXPOSE"}) + "\n",
            encoding="utf-8")
        messages = _safe_events(self.settings)
        self.assertEqual(len(messages), 2)
        self.assertNotIn("TOKEN-NEVER-EXPOSE", "".join(messages))
        self.assertIn("VERIFIED", messages[0])

    def test_status_unavailable_is_not_claimed_pass(self):
        (self.repo / ".git").rmdir()
        state, error = _safe_status(Path(self.tmp.name) / "missing-settings.json")
        self.assertIsNotNone(error)
        self.assertEqual(state["counts"]["VERIFIED"], 0)
        self.assertEqual(_model_label(Path(self.tmp.name) / "missing"), "미설정")


if __name__ == "__main__":
    unittest.main()
