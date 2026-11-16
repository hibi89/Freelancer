"""Host-owned independent acceptance for an immutable candidate snapshot."""
from __future__ import annotations

import json
from pathlib import Path
import re
import shutil
import tempfile

from .windows_review_process import run_restricted

_NAME = re.compile(r"[A-Za-z][A-Za-z0-9_]{0,62}")
_UNITTEST = """
import sys, unittest
suite = unittest.defaultTestLoader.discover('tests')
if not suite.countTestCases():
    raise SystemExit(1)
result = unittest.TextTestRunner(verbosity=0).run(suite)
raise SystemExit(not result.wasSuccessful() or result.testsRun <= len(result.skipped))
"""
_PYTHON = "import sys; sys.path.append(sys.argv.pop(1)); "
_PROBE = """
import importlib, json, sys
module, name, args, kwargs = json.loads(sys.argv[1])
result = getattr(importlib.import_module(module), name)(*args, **kwargs)
print(json.dumps(result, ensure_ascii=True, allow_nan=False, separators=(',', ':')))
"""


def _encode(value) -> str:
    return json.dumps(value, ensure_ascii=True, allow_nan=False, sort_keys=True,
                      separators=(",", ":"))


def validate_acceptance(probes) -> None:
    from .core import ContractError

    if not isinstance(probes, list) or not 1 <= len(probes) <= 12:
        raise ContractError("independent acceptance requires 1..12 callable probes")
    for probe in probes:
        if not isinstance(probe, dict) or set(probe) != {"module", "function", "args", "kwargs", "expected"}:
            raise ContractError("invalid independent acceptance probe fields")
        module, function = probe["module"], probe["function"]
        if (not isinstance(module, str) or len(module) > 160
                or not all(_NAME.fullmatch(p) for p in module.split("."))
                or not isinstance(function, str) or not _NAME.fullmatch(function)
                or not isinstance(probe["args"], list) or not isinstance(probe["kwargs"], dict)):
            raise ContractError("invalid independent acceptance callable or arguments")
        try:
            size = len(_encode(probe))
        except (ValueError, TypeError, RecursionError) as exc:
            raise ContractError("independent acceptance requires finite JSON") from exc
        if size > 4096:
            raise ContractError("independent acceptance probe exceeds its size limit")


def _python(runtime: Path, project: Path, code: str, *args: str) -> list[str]:
    return [str(runtime / "python" / "python.exe"), "-I", "-S", "-B", "-X", "utf8",
            "-c", _PYTHON + code, str(project), *args]


def _check_command(command: list[str], runtime: Path, project: Path) -> list[str]:
    if command[0] == "ruff":
        return [str(runtime / "ruff" / "ruff.exe"), *command[1:]]
    if command[2] == "unittest":
        return _python(runtime, project, _UNITTEST)
    # compileall writes bytecode; compile into memory in the read-only snapshot.
    return _python(runtime, project, "\nfrom pathlib import Path\n"
                   "root = Path(sys.argv[1])\n"
                   "if not root.is_dir(): raise SystemExit(1)\n"
                   "for file in root.rglob('*.py'): compile(file.read_bytes(), str(file), 'exec')\n",
                   command[-1])


def verify_candidate(task: dict, archive: Path, bundle: Path, parent: Path) -> dict:
    """Project checks and callable probes get distinct OS identities and no expected values."""
    from .sandbox_payload import extract_snapshot

    probes = task.get("acceptance")
    validate_acceptance(probes)
    with tempfile.TemporaryDirectory(prefix="review-", dir=parent) as directory:
        root = Path(directory)
        runtime, project = root / "runtime", root / "source"
        shutil.copytree(bundle / "python", runtime / "python")
        if any(cmd[0] == "ruff" for cmd in task["checks"]):
            shutil.copytree(bundle / "ruff", runtime / "ruff")
        extract_snapshot(archive, project)
        for command in task["checks"]:
            status, _ = run_restricted(_check_command(command, runtime, project), root, project, 240)
            if status:
                return {"ok": False, "reason": "PROJECT_CHECK_FAILED"}
        for probe in probes:
            module, function, args, kwargs, expected = (probe[key] for key in
                ("module", "function", "args", "kwargs", "expected"))
            if not any(path.is_file() for path in (
                    project.joinpath(*module.split(".")).with_suffix(".py"),
                    project.joinpath(*module.split("."), "__init__.py"))):
                return {"ok": False, "reason": "INDEPENDENT_PROBE_MODULE_MISSING"}
            argv = _python(runtime, project, _PROBE, _encode([module, function, args, kwargs]))
            status, output = run_restricted(argv, root, project, 45)
            try:
                observed = _encode(json.loads(output)) if status == 0 else None
            except (ValueError, RecursionError):
                observed = None
            if observed != _encode(expected):
                return {"ok": False, "reason": "INDEPENDENT_PROBE_FAILED"}
    return {"ok": True, "project_checks": len(task["checks"]), "independent_probes": len(probes)}
