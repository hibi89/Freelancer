"""Publication boundaries with disposable Git history and GitHub responses."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from axdev.core import ContractError, git
from scripts.publish_pr import _verify_remote_base, publish_draft
from scripts.publish_queue_status import REMOTE_PATH, publish


class PublicExportTests(unittest.TestCase):
    def test_local_private_baseline_is_not_already_on_remote_branch(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo, remote = root / "source", root / "bare remote"
            repo.mkdir()
            remote.mkdir()
            git(repo, "init", "-q", "-b", "approved")
            git(remote, "init", "--bare", "-q")
            git(repo, "config", "user.name", "Fixture")
            git(repo, "config", "user.email", "fixture@example.invalid")
            git(repo, "commit", "--allow-empty", "-qm", "reviewed public base")
            base = git(repo, "rev-parse", "HEAD")
            git(repo, "commit", "--allow-empty", "-qm", "newer public base")
            public = git(repo, "rev-parse", "HEAD")
            git(repo, "remote", "add", "origin", str(remote))
            git(repo, "push", "origin", "approved")
            git(repo, "commit", "--allow-empty", "-qm", "local-only ancestor")
            self.assertEqual(_verify_remote_base(repo, "approved", base), public)
            self.assertEqual(_verify_remote_base(repo, "approved", public), public)
            with self.assertRaisesRegex(ContractError, "already be on the approved remote base"):
                _verify_remote_base(repo, "approved", git(repo, "rev-parse", "HEAD"))
            with self.assertRaisesRegex(ContractError, "missing or ambiguous"):
                _verify_remote_base(repo, "absent", base)

    def test_draft_export_verifies_receipt_and_refuses_unapproved_head(self):
        inspection = {"repository": "hibi89/Freelancer", "base_branch": "approved",
                      "head_branch": "axdev/review-fixture", "reviewed_commit": "a" * 40,
                      "source_baseline": "b" * 40, "verified_task_ids": ["FIXTURE"],
                      "changed_files": ["example.py"]}
        url = "https://github.com/hibi89/Freelancer/pull/3"
        expected = {"isDraft": True, "headRefOid": "a" * 40, "baseRefName": "approved",
                    "headRefName": "axdev/review-fixture", "url": url}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            settings = root / "settings.json"
            settings.write_text(json.dumps({"repo": str(root)}), encoding="utf-8")
            for head, ok in (("a" * 40, True), ("c" * 40, False)):
                responses = ["hibi89\n", "", url + "\n", json.dumps(dict(expected, headRefOid=head))]
                with patch("scripts.publish_pr.shutil.which", return_value="gh"), \
                        patch("scripts.publish_pr.preview", return_value=inspection), \
                        patch("scripts.publish_pr._verify_remote_base", return_value="b" * 40), \
                        patch("scripts.publish_pr._git", return_value=""), \
                        patch("scripts.publish_pr.subprocess.run", side_effect=[
                            subprocess.CompletedProcess([], 0, stdout=out) for out in responses]) as run:
                    if ok:
                        self.assertEqual(publish_draft(settings, inspection)["pr_url"], url)
                    else:
                        with self.assertRaisesRegex(ContractError, "differs from the approved base or reviewed head"):
                            publish_draft(settings, inspection)
                push = run.call_args_list[1].args[0]
                self.assertIn("--no-follow-tags", push)
                self.assertIn("remote.origin.mirror=false", push)
                self.assertEqual(push[-1], "a" * 40 + ":refs/heads/axdev/review-fixture")
                self.assertIn("github.com/hibi89/Freelancer", run.call_args_list[2].args[0])

    def test_status_receipt_identifies_the_exact_public_payload(self):
        view = {"target_repo": "hibi89/Freelancer", "target_branch": "approved-status",
                "target_path": REMOTE_PATH, "payload": {"task_state_counts": {"QUEUED": 1}}}
        for valid in (True, False):
            observed = []

            def remote(argv, **_):
                self.assertEqual(argv[:4], ["gh", "api", "--hostname", "github.com"])
                if "user" in argv:
                    return subprocess.CompletedProcess(argv, 0, stdout="hibi89\n")
                self.assertIn("PUT", argv)
                self.assertIn("branch=approved-status", argv)
                self.assertIn("sha=" + "b" * 40, argv)
                encoded = next(arg.removeprefix("content=") for arg in argv if arg.startswith("content="))
                data = base64.b64decode(encoded)
                self.assertEqual(json.loads(data), view["payload"])
                sha = hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()
                observed.append(sha)
                receipt = {"commit": {"sha": "a" * 40},
                           "content": {"path": REMOTE_PATH, "sha": sha if valid else "c" * 40}}
                return subprocess.CompletedProcess(argv, 0, stdout=json.dumps(receipt))

            with patch("scripts.publish_queue_status.shutil.which", return_value="gh"), \
                    patch("scripts.publish_queue_status.subprocess.run", side_effect=remote):
                if valid:
                    self.assertEqual(publish(view, "b" * 40)["blob_sha"], observed[0])
                else:
                    with self.assertRaisesRegex(ContractError, "does not match the approved status bytes"):
                        publish(view, "b" * 40)
            self.assertEqual(len(observed), 1)
