"""P2 synthetic contracts for F14 (EAI), F15 (AXNODE), F19 (semantic review).

No network, external EAI executable, or real local model is invoked.
"""
import hashlib
import json
import sqlite3
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from axdev.core import ContractError, plan_hash
from axdev.eai_adapter import load_eai_policy, run_eai_goal
from axdev.axnode_adapter import typed_checkpoint, export_checkpoint, verify_checkpoint
from axdev.semantic_review import review_semantics


class AdapterContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.task = {
            "id": "AAA-001", "goal": "Implement the approved feature safely",
            "files": ["src/feature.py"], "depends_on": [],
            "checks": [["python", "-m", "unittest", "discover", "-s", "tests", "-q"]],
        }
        self.plan = self.root / "plan.json"
        self.plan.write_text(json.dumps({"version": 1, "tasks": [self.task]}),
                             encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_eai_policy_is_sha_pinned_and_rejects_unknown_task(self):
        policy = self.root / "eai-policy.json"
        rule = {
            "eai_repo": str(self.root / "eai"),
            "expected_sha": "a" * 40,
            "goal": str(self.root / "goals" / "one.json"),
            "approved_directory": str(self.root / "goals"),
        }
        payload = {"version": 1, "tasks": {"AAA-001": rule}}
        policy.write_text(json.dumps(payload), encoding="utf-8")
        records, digest = load_eai_policy(policy, {"AAA-001"})
        self.assertEqual(records["AAA-001"]["expected_sha"], "a" * 40)
        self.assertEqual(digest, hashlib.sha256(policy.read_bytes()).hexdigest())
        with self.assertRaisesRegex(ContractError, "unapproved task IDs"):
            load_eai_policy(policy, {"BBB-002"})
        payload["tasks"]["AAA-001"]["expected_sha"] = "unapproved"
        policy.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaisesRegex(ContractError, "incomplete or unpinned"):
            load_eai_policy(policy, {"AAA-001"})

    def test_eai_receipt_is_advisory_not_automatic_task_verification(self):
        repo = self.root / "eai"
        (repo / "eai").mkdir(parents=True)
        (repo / "eai" / "__main__.py").write_text("# stub\n", encoding="utf-8")
        approved = self.root / "private-goals"
        approved.mkdir()
        goal = approved / "approved.json"
        goal.write_text('{"request":"synthetic"}\n', encoding="utf-8")
        sha = "a" * 40

        def git_check(path, *cmd):
            self.assertEqual(path, repo)
            if cmd == ("rev-parse", "--show-toplevel"):
                return str(repo.resolve())
            if cmd == ("rev-parse", "HEAD"):
                return sha
            if cmd == ("status", "--porcelain", "--untracked-files=all"):
                return ""
            raise AssertionError("unexpected Git command")

        for status, rc, accepted in (("AGREE", 0, True), ("CONFLICT", 2, False)):
            payload = json.dumps({"status": status}).encode("utf-8")
            result = subprocess.CompletedProcess([], rc, stdout=payload, stderr=b"")
            with patch("axdev.eai_adapter.git", side_effect=git_check), \
                 patch("axdev.eai_adapter.subprocess.run", return_value=result) as runner:
                record = run_eai_goal(repo, sha, goal, approved)
            self.assertEqual(record["independent_receipt_accepted"], accepted)
            self.assertEqual(record["task_verification"], "NOT_VERIFIED")
            self.assertEqual(record["goal_sha256"], hashlib.sha256(goal.read_bytes()).hexdigest())
            self.assertNotIn("request", str(record))
            self.assertNotIn("GITHUB_TOKEN", runner.call_args.kwargs["env"])
            self.assertFalse(runner.call_args.kwargs["shell"])

    def _sqlite_checkpoint(self, spec=None, status="VERIFIED", commit=None):
        db_path = self.root / "factory.sqlite3"
        connection = sqlite3.connect(db_path)
        try:
            connection.execute("CREATE TABLE meta(key TEXT PRIMARY KEY,value TEXT NOT NULL)")
            connection.execute(
                "CREATE TABLE runs(id TEXT PRIMARY KEY,spec TEXT,status TEXT,commit_sha TEXT)")
            connection.execute("INSERT INTO meta VALUES(?,?)", ("base_sha", "a" * 40))
            connection.execute("INSERT INTO runs VALUES(?,?,?,?)",
                               ("AAA-001", spec or plan_hash(self.task), status,
                                commit if commit is not None else "b" * 40))
            connection.commit()
        finally:
            connection.close()
        return db_path

    def test_axnode_export_and_verify_are_metadata_only(self):
        db = self._sqlite_checkpoint()
        graph = typed_checkpoint(self.plan, db)
        self.assertEqual(graph["format"], "axdev.axnode-typed-bridge.v1")
        self.assertFalse(graph["native_axnode_binary"])
        self.assertEqual(graph["nodes"][0]["verified_commit"], "b" * 40)
        out = self.root / "private" / "checkpoint.json"
        result = export_checkpoint(self.plan, db, out)
        self.assertEqual(result["nodes"], 1)
        self.assertTrue(verify_checkpoint(self.plan, db, out)["bridge_verified_against_source"])
        with self.assertRaisesRegex(ContractError, "exists"):
            export_checkpoint(self.plan, db, out)
        forged = json.loads(out.read_text(encoding="utf-8"))
        forged["nodes"][0]["status"] = "HOLD"
        out.write_text(json.dumps(forged), encoding="utf-8")
        with self.assertRaisesRegex(ContractError, "differs"):
            verify_checkpoint(self.plan, db, out)

    def test_axnode_rejects_mismatched_source_contract(self):
        db = self._sqlite_checkpoint(spec="0" * 64)
        with self.assertRaisesRegex(ContractError, "contract or status"):
            typed_checkpoint(self.plan, db)

    def test_semantic_review_local_only_verdict_contract(self):
        source = self.root / "src"
        source.mkdir()
        (source / "feature.py").write_text("answer = 42\n", encoding="utf-8")
        files = {"src/feature.py"}
        model = "ollama/qwen3:4b"
        for verdict, issue, expected in (
            ("PASS", "NONE", True), ("HOLD", "UNSAFE_CHANGE", False),
            ("PASS", "UNSAFE_CHANGE", False),
        ):
            answer = {"response": json.dumps({
                "verdict": verdict, "issue": issue, "reason": "synthetic"})}
            with patch("axdev.semantic_review._local_generate", return_value=answer) as local:
                ok, reason = review_semantics(self.task, self.root, files, model)
            self.assertEqual(ok, expected)
            self.assertTrue(reason.startswith("SEMANTIC_"))
            request = local.call_args.args[0]
            self.assertEqual(request["stream"], False)
            self.assertEqual(request["model"], "qwen3:4b")
            self.assertIn("answer = 42", request["prompt"])

    def test_semantic_review_rejects_wrong_provider_and_malformed_verdict(self):
        source = self.root / "src"
        source.mkdir()
        (source / "feature.py").write_text("answer = 42\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "local Ollama"):
            review_semantics(self.task, self.root, {"src/feature.py"}, "openai/remote")
        bad = {"response": json.dumps({
            "verdict": "PASS", "issue": "NONE", "reason": "too long" * 100})}
        with patch("axdev.semantic_review._local_generate", return_value=bad):
            with self.assertRaisesRegex(ValueError, "malformed or unbounded"):
                review_semantics(self.task, self.root, {"src/feature.py"}, "ollama/qwen3:4b")


if __name__ == "__main__":
    unittest.main()
