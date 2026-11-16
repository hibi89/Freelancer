import base64
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from axdev.core import ContractError, load_plan
from axdev.github_sync import sync_public_plan

HEAD = "a" * 40
TASK = {"id": "AAA-001", "goal": "Create synthetic module",
        "files": ["src/feature.py"], "depends_on": [],
        "checks": [["python", "-m", "unittest", "discover", "-s", "tests", "-q"]]}
RAW = (json.dumps({"version": 1, "tasks": [TASK]}) + "\n").encode()
BLOB = hashlib.sha1(b"blob " + str(len(RAW)).encode() + b"\0" + RAW).hexdigest()

class ImportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name) / "private" / "plan.json"
        self.answers = [{"object": {"sha": HEAD}},
                        {"type": "file", "encoding": "base64", "sha": BLOB,
                         "content": base64.b64encode(RAW).decode()},
                        {"object": {"sha": HEAD}}]
    def sync(self, answers=None, **extra):
        params = dict(repo="hibi89/Freelancer", branch="tools/ax-dev-factory-local",
                      path="examples/sample-plan.json", expected_sha=HEAD,
                      output=self.output)
        params.update(extra)
        with patch("axdev.github_sync.github_get", side_effect=answers or self.answers) as get:
            result = sync_public_plan(**params)
        return result, get.call_count
    def test_safe_read_only_success(self):
        result, count = self.sync()
        self.assertEqual(count, 3)
        self.assertTrue(result["created"])
        self.assertFalse(result["executed"])
        self.assertEqual(len(load_plan(self.output)), 1)
    def test_repeat_same_plan_noop(self):
        self.sync()
        self.assertFalse(self.sync()[0]["created"])
    def test_no_overwrite(self):
        self.output.parent.mkdir()
        self.output.write_text("ORIGINAL")
        with self.assertRaisesRegex(ContractError, "no overwrite"):
            self.sync()
        self.assertEqual(self.output.read_text(), "ORIGINAL")
    def test_reject_different_sha(self):
        with self.assertRaisesRegex(ContractError, "changed"):
            self.sync(answers=[{"object": {"sha": "b" * 40}}])
        self.assertFalse(self.output.exists())
    def test_reject_race(self):
        answers = self.answers[:2] + [{"object": {"sha": "b" * 40}}]
        with self.assertRaisesRegex(ContractError, "advanced"):
            self.sync(answers=answers)
    def test_reject_blob_corruption(self):
        answers = self.answers.copy()
        answers[1] = dict(answers[1], sha="b" * 40)
        with self.assertRaisesRegex(ContractError, "blob mismatch"):
            self.sync(answers=answers)
    def test_reject_malicious_paths_and_unpinned_source(self):
        for value in ({"branch": "../main"}, {"path": ".github/private.json"},
                      {"path": "../plan.json"}, {"expected_sha": ""}):
            with self.subTest(value), self.assertRaises(ContractError):
                self.sync(**value)
    def test_bad_contract_fails_before_write(self):
        raw = b'{"version":1,"tasks":[{"id":"AAA-001"}]}'
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        answers = self.answers.copy()
        answers[1] = {"type": "file", "encoding": "base64", "sha": blob,
                      "content": base64.b64encode(raw).decode()}
        with self.assertRaises(ContractError):
            self.sync(answers=answers)
        self.assertFalse(self.output.exists())
    def test_reject_symlink_output(self):
        target = Path(self.temp.name) / "protected"
        target.write_text("SAFE")
        self.output.parent.mkdir()
        try:
            self.output.symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("symlink unavailable")
        with self.assertRaisesRegex(ContractError, "symlink"):
            self.sync()
        self.assertEqual(target.read_text(), "SAFE")

if __name__ == "__main__":
    unittest.main()
