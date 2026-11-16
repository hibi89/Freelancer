"""Effective Git trust policy regression tests; no model or remote calls."""
import subprocess
import tempfile
import unittest
from pathlib import Path
from axdev.core import ContractError
from axdev.repo_trust import assert_safe_git_checkout


class GitRepositoryTrustTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        self.git("init")
        self.git("config", "user.name", "AXDev Test")
        self.git("config", "user.email", "axdev-test@example.invalid")
        (self.repo / "README.md").write_text("fixture\n", encoding="utf-8")
        self.git("add", "README.md")
        self.git("commit", "-m", "fixture")

    def tearDown(self):
        self.tmp.cleanup()

    def git(self, *args):
        subprocess.run(["git", *args], cwd=self.repo, check=True,
                       stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)

    def test_dormant_git_lfs_registration_allows_safe_repo(self):
        self.git("config", "filter.lfs.clean", "git-lfs clean -- %f")
        self.git("config", "filter.lfs.smudge", "git-lfs smudge -- %f")
        self.git("config", "filter.lfs.process", "git-lfs filter-process")
        assert_safe_git_checkout(self.repo, ("src/new.bin",))

    def test_global_attribute_active_on_future_path_is_rejected(self):
        self.git("config", "filter.lfs.clean", "git-lfs clean -- %f")
        attr = Path(self.tmp.name) / "global-attributes"
        attr.write_text("*.bin filter=lfs\n", encoding="utf-8")
        self.git("config", "core.attributesFile", str(attr))
        with self.assertRaisesRegex(ContractError, "active Git content filter"):
            assert_safe_git_checkout(self.repo, ("src/new.bin",))

    def test_custom_executable_filter_remains_blocked(self):
        self.git("config", "filter.custom.clean", "echo unsafe")
        with self.assertRaisesRegex(ContractError, "Git executable hooks/filters"):
            assert_safe_git_checkout(self.repo)

    def test_active_hooks_path_remains_blocked(self):
        self.git("config", "core.hooksPath", "../hooks")
        with self.assertRaisesRegex(ContractError, "Git executable hooks/filters"):
            assert_safe_git_checkout(self.repo)

    def test_tracked_git_attributes_activate_block(self):
        (self.repo / ".gitattributes").write_text("*.bin filter=lfs\n", encoding="utf-8")
        self.git("add", ".gitattributes")
        self.git("commit", "-m", "attributes")
        with self.assertRaisesRegex(ContractError, "Git content filter attribute"):
            assert_safe_git_checkout(self.repo, ("src/new.bin",))


if __name__ == "__main__":
    unittest.main()
