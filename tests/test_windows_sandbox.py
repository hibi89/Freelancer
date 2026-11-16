"""Candidate forgery, host acceptance, and Windows AppContainer regressions."""
from __future__ import annotations

import json
import os
from contextlib import nullcontext
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
import xml.etree.ElementTree as ET
import zipfile

from axdev.core import ContractError, Factory, git, plan_hash
from axdev.sandbox_payload import BINARIES, encode_files, extract_snapshot, read_json, write_json
from axdev.sandbox_review import verify_candidate
from axdev.windows_review_process import run_restricted, single_sandbox_slot
from axdev.windows_sandbox_runtime import (
    BACKEND, _read_bundle, _read_receipt, _wsb, run_sandbox_one, run_sandbox_queue, validate_history,
)
from scripts.prepare_offline_bundle import build_manifest
from scripts.sandbox_guest import _safe_payload, _start_local_ollama

MOD = "axdev.windows_sandbox_runtime"
SOURCE = "src/example.py"
CHECK = ["python", "-m", "unittest", "discover", "-s", "tests", "-q"]


def copy_python(runtime: Path):
    origin = Path(sys.executable).parent
    runtime.mkdir(parents=True)
    for pattern in ("python.exe", "python*.dll", "vcruntime*.dll"):
        for path in origin.glob(pattern):
            shutil.copy2(path, runtime / path.name)
    for name in ("Lib", "DLLs"):
        shutil.copytree(origin / name, runtime / name,
                        ignore=shutil.ignore_patterns("site-packages", "__pycache__", "test"))


class SandboxGuestStartupTests(unittest.TestCase):
    def test_local_ollama_pins_one_model_and_one_request(self):
        bundle, workroot = Path("offline-bundle"), Path("sandbox-guest")
        inherited = {"OLLAMA_MAX_LOADED_MODELS": "3", "OLLAMA_NUM_PARALLEL": "4"}
        with (
            patch.dict(os.environ, inherited),
            patch("scripts.sandbox_guest.subprocess.Popen") as start,
        ):
            self.assertIs(_start_local_ollama(bundle, workroot), start.return_value)
            self.assertEqual({name: os.environ[name] for name in inherited}, inherited)
        args, options = start.call_args
        self.assertEqual(args[0], [str(bundle / "ollama" / "ollama.exe"), "serve"])
        expected = {
            "OLLAMA_HOST": "127.0.0.1:11434",
            "OLLAMA_MODELS": str(bundle / "models"),
            "OLLAMA_NO_CLOUD": "1",
            "OLLAMA_MAX_LOADED_MODELS": "1",
            "OLLAMA_NUM_PARALLEL": "1",
        }
        self.assertEqual({name: options["env"][name] for name in expected}, expected)


class SandboxContractTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.state, self.repo, self.bundle = (self.root / n for n in ("state", "repo", "bundle"))
        for path in (self.repo, self.bundle):
            path.mkdir()
        git(self.repo, "init", "-q")
        git(self.repo, "config", "user.name", "AXDEV Fixtures")
        git(self.repo, "config", "user.email", "axdev@example.invalid")
        git(self.repo, "config", "core.autocrlf", "false")
        (self.repo / "tests").mkdir()
        (self.repo / "tests/test_protected.py").write_text(
            "import unittest\nfrom src.example import greet\n"
            "class TestProtected(unittest.TestCase):\n"
            " def test_empty(self): self.assertEqual(greet(''), 'Hello, ')\n", encoding="utf-8")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-qm", "fixture")
        self.base = git(self.repo, "rev-parse", "HEAD")
        self.task = {"id": "AAA-001", "goal": "Approved greeting behavior", "files": [SOURCE],
                     "depends_on": [], "checks": [CHECK],
                     "acceptance": [{"module": "src.example", "function": "greet",
                                     "args": ["secret-probe"], "kwargs": {}, "expected": "Hello, secret-probe"}]}
        self.plan = self.root / "plan.json"
        self.plan_sha = write_json(self.plan, {"version": 1, "tasks": [self.task]})
        self.factory = Factory(self.repo, self.plan, self.state)
        self.addCleanup(self.factory.close)

    def _response(self, run, files=None):
        return {"version": 2, "run_id": run["run_id"], "base_sha": run["base_sha"],
                "task_id": self.task["id"], "task_sha256": plan_hash(self.task),
                "status": "CANDIDATE", "files": encode_files(
                    files if files is not None else {SOURCE: b"def greet(name): return 'Hello, ' + name\n"})}

    def _start(self, _, root):
        request, _ = read_json(root / "input/request.json", 65536)
        self.assertEqual(set(request["task"]), {"id", "goal", "files"})
        self.assertNotIn("secret-probe", (root / "input/request.json").read_text())
        write_json(root / "outbox/receipt.json", self._response(request))
        return Mock(**{"poll.return_value": 0})

    def _run(self):
        return run_sandbox_one(self.factory, self.task, self.bundle, "0" * 64, True,
                               executable=self.root / "WindowsSandbox.exe")

    def _pinned(self):
        return git(self.repo, "rev-parse", self.factory.integration_ref)

    def test_wsb_disables_redirection_and_only_gives_the_guest_a_disposable_outbox(self):
        input_dir, outbox = self.root / "input", self.root / "outbox"
        root = ET.fromstring(_wsb(input_dir, self.bundle, outbox))
        for name in ("Networking", "VGpu", "ClipboardRedirection", "PrinterRedirection",
                     "AudioInput", "VideoInput"):
            self.assertEqual(root.findtext(name), "Disable")
        folders = root.findall("MappedFolders/MappedFolder")
        self.assertEqual([f.findtext("ReadOnly") for f in folders], ["true", "true", "false"])
        self.assertEqual([f.findtext("HostFolder") for f in folders],
                         [str(input_dir), str(self.bundle), str(outbox)])

    def test_reject_verified_claim_out_of_scope_bytes_and_replay(self):
        run = {"run_id": "a" * 32, "base_sha": self.base}
        outbox = self.root / "outbox"
        outbox.mkdir()
        path = outbox / "receipt.json"
        for obj in (
            dict(self._response(run), status="VERIFIED"),
            self._response(run, {"tests/test_protected.py": b"tampered"}),
            dict(self._response(run), run_id="b" * 32),
            dict(self._response(run), task_sha256="0" * 64),
        ):
            write_json(path, obj)
            with self.assertRaises(ContractError):
                _read_receipt(self.root, run["run_id"], self.task, self.base)
        data = self._response(run)
        data["files"][0]["sha256"] = "0" * 64
        write_json(path, data)
        with self.assertRaisesRegex(ContractError, "hash differs"):
            _read_receipt(self.root, run["run_id"], self.task, self.base)

    def test_rejects_legacy_prepared_without_independent_proof(self):
        self.factory._set(self.task["id"], "PREPARED", "guest claim", self.base)
        self.assertEqual(self._run()["status"], "HOLD")
        self.assertEqual(self._pinned(), self.base)

    def test_candidate_is_reviewed_before_exact_tree_promotion_and_recovers_prepared(self):
        def review(task, archive, _bundle, root):
            with zipfile.ZipFile(archive) as contents:
                self.assertEqual(contents.read(SOURCE), b"def greet(name): return 'Hello, ' + name\n")
                self.assertEqual(contents.read("tests/test_protected.py"),
                                 (self.repo / "tests/test_protected.py").read_bytes())
            write_json(root / "outbox/receipt.json", {"status": "VERIFIED", "forged": True})
            return {"ok": True, "project_checks": 1, "independent_probes": 1}

        with patch(MOD + "._sandbox_running", return_value=False), \
                patch(MOD + "._start_guest", side_effect=self._start) as start, \
                patch(MOD + ".verify_candidate", side_effect=review) as verified:
            with patch.object(self.factory, "_promote_prepared", side_effect=SystemExit):
                with self.assertRaises(SystemExit):
                    self._run()
            self.assertEqual(self.factory.status()[self.task["id"]], "PREPARED")
            self.assertEqual(self._pinned(), self.base)
            set_status = self.factory._set

            def stop_after_ref_update(tid, status, evidence="", commit=""):
                if status == "VERIFIED":
                    raise SystemExit
                set_status(tid, status, evidence, commit)

            with patch.object(self.factory, "_set", side_effect=stop_after_ref_update):
                with self.assertRaises(SystemExit):
                    self._run()
            self.assertNotEqual(self._pinned(), self.base)
            self.assertEqual(self.factory.status()[self.task["id"]], "PREPARED")
            validate_history(self.repo, self.state, self.factory.db, [self.task],
                             self.factory.integration_ref, allow_prepared=True)
            outcome = self._run()
        self.assertEqual(outcome["status"], "VERIFIED")
        self.assertEqual(self._pinned(), outcome["commit"])
        self.assertEqual(git(self.repo, "rev-parse", "HEAD"), self.base)
        self.assertEqual(git(self.repo, "status", "--porcelain"), "")
        start.assert_called_once()
        verified.assert_called_once()
        validate_history(self.repo, self.state, self.factory.db, [self.task],
                         self.factory.integration_ref, allow_prepared=False)
        git(self.repo, "update-ref", self.factory.integration_ref, self.base, outcome["commit"])
        with self.assertRaisesRegex(ContractError, "history differ"):
            validate_history(self.repo, self.state, self.factory.db, [self.task],
                             self.factory.integration_ref, allow_prepared=False)

    def test_one_fix_then_hold_after_independent_check_fails(self):
        with patch(MOD + "._sandbox_running", return_value=False), \
                patch(MOD + "._start_guest", side_effect=self._start) as start, \
                patch(MOD + ".verify_candidate",
                      return_value={"ok": False, "reason": "INDEPENDENT_PROBE_FAILED"}) as review:
            self.assertEqual(self._run()["status"], "HOLD")
        self.assertEqual(start.call_count, 2)
        self.assertEqual(review.call_count, 2)
        self.assertEqual(self._pinned(), self.base)
        self.assertEqual(self.factory.db.execute("SELECT attempts FROM runs").fetchone()[0], 1)
        self.assertTrue(list(self.state.glob("sandbox-runs/*/input/initial.json")))

    def test_git_error_after_ref_update_keeps_prepared_proof_for_retry(self):
        def lose_update_reply(repo, *args):
            result = git(repo, *args)
            if args[:2] == ("update-ref", self.factory.integration_ref):
                raise RuntimeError("Git reply lost after updating ref")
            return result

        with patch(MOD + "._sandbox_running", return_value=False), \
                patch(MOD + "._start_guest", side_effect=self._start) as start, \
                patch(MOD + ".verify_candidate",
                      return_value={"ok": True, "project_checks": 1, "independent_probes": 1}):
            with patch("axdev.core.git", side_effect=lose_update_reply):
                with self.assertRaisesRegex(RuntimeError, "Git reply lost"):
                    self._run()
            pending = self._pinned()
            self.assertNotEqual(pending, self.base)
            self.assertEqual(self.factory.status()[self.task["id"]], "PREPARED")
            with patch(MOD + "._host_proof", side_effect=ContractError("proof unavailable")):
                with self.assertRaisesRegex(ContractError, "proof unavailable"):
                    self._run()
            self.assertEqual(self.factory.status()[self.task["id"]], "PREPARED")
            validate_history(self.repo, self.state, self.factory.db, [self.task],
                             self.factory.integration_ref, allow_prepared=True)
            result = self._run()
        self.assertEqual((result["status"], result["commit"]), ("VERIFIED", pending))
        start.assert_called_once()

    def test_sandbox_queue_keeps_independent_work_after_hold(self):
        plan = self.root / "queue.json"
        independent = dict(self.task, id="BBB-001", files=["src/independent.py"])
        blocked = dict(self.task, id="CCC-001", depends_on=[self.task["id"]])
        digest = write_json(plan, {"version": 1, "tasks": [self.task, independent, blocked]})

        def start_guest(_, root):
            request, _ = read_json(root / "input/request.json", 65536)
            task = request["task"]
            candidate = self._response(request, {task["files"][0]: b"fixture = 1\n"})
            candidate.update(task_id=task["id"], task_sha256=request["task_sha256"])
            write_json(root / "outbox/receipt.json", candidate)
            return Mock(**{"poll.return_value": 0})

        with patch(MOD + "._sandbox_binary", return_value=self.root / "WindowsSandbox.exe"), \
                patch(MOD + "._read_bundle"), patch(MOD + ".single_sandbox_slot", nullcontext), \
                patch(MOD + "._sandbox_running", return_value=False), \
                patch(MOD + "._start_guest", side_effect=start_guest) as start, \
                patch(MOD + ".verify_candidate", side_effect=[
                    {"ok": False, "reason": "INDEPENDENT_PROBE_FAILED"},
                    {"ok": False, "reason": "INDEPENDENT_PROBE_FAILED"},
                    {"ok": True, "project_checks": 1, "independent_probes": 1}]):
            results, states = run_sandbox_queue(self.repo, plan, self.state, self.bundle, "0" * 64,
                                                self.factory.model, 3, True, plan_sha256=digest)
        self.assertEqual([row["status"] for row in results], ["HOLD", "VERIFIED"])
        self.assertEqual(states, {"AAA-001": "HOLD", "BBB-001": "VERIFIED", "CCC-001": "QUEUED"})
        self.assertEqual(start.call_count, 3)

    def test_interrupted_coder_is_not_started_twice(self):
        with patch(MOD + "._sandbox_running", return_value=False), \
                patch(MOD + "._start_guest", side_effect=SystemExit) as start:
            with self.assertRaises(SystemExit):
                self._run()
            self.assertEqual(self._run()["status"], "HOLD")
        start.assert_called_once()
        self.assertEqual(self._pinned(), self.base)

    def test_tampered_acceptance_proof_cannot_resume_promotion(self):
        with patch(MOD + "._sandbox_running", return_value=False), \
                patch(MOD + "._start_guest", side_effect=self._start), \
                patch(MOD + ".verify_candidate",
                      return_value={"ok": True, "project_checks": 1, "independent_probes": 1}), \
                patch.object(self.factory, "_promote_prepared", side_effect=SystemExit):
            with self.assertRaises(SystemExit):
                self._run()
        proof = next(self.state.glob("sandbox-runs/*/acceptance.json"))
        write_json(proof, {"fake": True})
        self.assertEqual(self._run()["status"], "HOLD")
        self.assertEqual(self._pinned(), self.base)

    def test_manifest_commits_to_libraries_and_model_bytes(self):
        for name in (*BINARIES, "python/python311.dll", "models/blobs/sha256-test"):
            path = self.bundle / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(name.encode())
        path = self.bundle / "manifest.json"
        digest = write_json(path, build_manifest(self.bundle))
        with self.assertRaisesRegex(ContractError, "hash mismatched"):
            _read_bundle(self.bundle, "0" * 64)
        _read_bundle(self.bundle, digest)
        (self.bundle / "python/python311.dll").write_bytes(b"changed")
        with self.assertRaisesRegex(ContractError, "files differ"):
            _read_bundle(self.bundle, digest)

    def test_unpinned_plan_and_legacy_direct_execution_fail_before_model(self):
        with self.assertRaisesRegex(ContractError, "plan SHA256 differs"):
            run_sandbox_queue(self.repo, self.plan, self.state, self.bundle, "0" * 64,
                              self.factory.model, 1, True, plan_sha256="1" * 64)
        with self.assertRaisesRegex(ContractError, "isolated Windows queue"):
            self.factory.run_one(True)
        self.factory.require_isolated_state(BACKEND, self.plan_sha)
        self.assertEqual(self._pinned(), self.base)

    def test_guest_rejects_remote_provider_and_path_traversal(self):
        payload = {"version": 2, "run_id": "a" * 32, "base_sha": self.base,
                   "task": {k: self.task[k] for k in ("id", "goal", "files")},
                   "task_sha256": "0" * 64, "model": "openai/paid", "archive_sha256": "0" * 64,
                   "bundle_sha256": "0" * 64, "initial_sha256": None}
        with self.assertRaises(ContractError):
            _safe_payload(payload)
        for unsafe in ("../escape.txt", "con.txt", "test/.git/config", "a~1/value"):
            archive = self.root / "source.zip"
            with zipfile.ZipFile(archive, "w") as output:
                output.writestr(unsafe, "untrusted")
            with self.assertRaises(ContractError):
                extract_snapshot(archive, self.root / ("guest" + str(len(unsafe))))
        self.assertFalse((self.root / "escape.txt").exists())

    def test_test_success_cannot_supply_the_independent_expected_value(self):
        archive = self.root / "source.zip"
        with zipfile.ZipFile(archive, "w") as synthetic:
            synthetic.writestr(SOURCE, "def greet(name): return None")
        (self.bundle / "python").mkdir()
        with patch("axdev.sandbox_review.run_restricted", side_effect=[(0, b"verified"), (0, b"null")]) as run:
            result = verify_candidate(self.task, archive, self.bundle, self.root)
        self.assertEqual(result["reason"], "INDEPENDENT_PROBE_FAILED")
        self.assertEqual(run.call_count, 2)
        self.assertNotIn(self.task["acceptance"][0]["expected"], " ".join(run.call_args.args[0]))


@unittest.skipUnless(os.name == "nt", "requires Windows AppContainer kernel")
class NativeAppContainerTests(unittest.TestCase):
    def test_windows_coding_slot_recovers_after_abrupt_process_exit(self):
        child = [sys.executable, "-c", """
import os
from axdev.core import ContractError
from axdev.windows_review_process import single_sandbox_slot
try:
    with single_sandbox_slot():
        os._exit(17)
except ContractError:
    os._exit(23)
"""]
        with single_sandbox_slot():
            self.assertEqual(subprocess.run(child, timeout=10).returncode, 23)
        self.assertEqual(subprocess.run(child, timeout=10).returncode, 17)
        with single_sandbox_slot():
            self.assertEqual(subprocess.run(child, timeout=10).returncode, 23)

    def test_appcontainer_enforces_private_file_network_and_source_boundaries(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stage = root / "run"
            runtime = stage / "python"
            copy_python(runtime)
            outside = root / "host-private.txt"
            outside.write_text("private canary", encoding="utf-8")
            code = """
import pathlib, socket, sys
host, workspace, port = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), int(sys.argv[3])
for attempt in (host.read_text, lambda: host.write_text('mutated'),
                lambda: (workspace / 'fake-proof.json').write_text('forged'),
                lambda: socket.create_connection(('127.0.0.1', port), timeout=1)):
    try:
        attempt()
    except (PermissionError, TimeoutError):
        continue
    raise SystemExit('boundary unexpectedly accessible')
print('RESTRICTIONS_OK')
"""
            with socket.socket() as server:
                server.bind(("127.0.0.1", 0))
                server.listen(1)
                with socket.create_connection(server.getsockname(), timeout=1):
                    connection, _ = server.accept()
                    connection.close()
                args = [str(runtime / "python.exe"), "-I", "-S", "-B", "-c", code, str(outside),
                        str(stage), str(server.getsockname()[1])]
                status, output = run_restricted(args, stage, stage, 15)
            self.assertEqual(status, 0, output.decode(errors="replace"))
            self.assertEqual(output.strip(), b"RESTRICTIONS_OK")
            self.assertEqual(outside.read_text(encoding="utf-8"), "private canary")
            self.assertFalse((stage / "fake-proof.json").exists())
            parent = root / "review"
            parent.mkdir()
            archive = root / "candidate.zip"
            with zipfile.ZipFile(archive, "w") as candidate:
                candidate.writestr("tests/test_fake.py", "import os; os._exit(0)\n")
                candidate.writestr(SOURCE, "def greet(name): return 'wrong'\n")
            task = {"checks": [CHECK], "acceptance": [
                {"module": "src.example", "function": "greet", "args": ["outside"],
                 "kwargs": {}, "expected": "Hello, outside"}]}
            self.assertFalse(verify_candidate(task, archive, stage, parent)["ok"])
            with zipfile.ZipFile(archive, "w") as candidate:
                candidate.writestr("tests/test_fixed.py",
                                   "import unittest\nfrom src.example import greet\n"
                                   "class TestSimple(unittest.TestCase):\n"
                                   " def test_simple(self): self.assertEqual(greet(''), 'Hello, ')\n")
                candidate.writestr(SOURCE, "def greet(name): return 'Hello, ' + name\n")
            self.assertTrue(verify_candidate(task, archive, stage, parent)["ok"])


if __name__ == "__main__":
    unittest.main()
