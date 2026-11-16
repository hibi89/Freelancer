"""Explicit Windows startup task XML preparation. No silent OS registration."""
from __future__ import annotations

import argparse
import csv
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from axdev.core import ContractError
from axdev.windows_review_process import system_directory

NS = "http://schemas.microsoft.com/windows/2004/02/mit/task"
SID = re.compile(r"S-1-[0-9]+(?:-[0-9]+)+")


def _element(parent, tag: str, text: str | None = None):
    item = ET.SubElement(parent, "{" + NS + "}" + tag)
    if text is not None:
        item.text = text
    return item


def _current_user_sid() -> str:
    result = subprocess.run([str(system_directory() / "whoami.exe"), "/user", "/fo", "csv", "/nh"],
                            stdin=subprocess.DEVNULL, capture_output=True, timeout=10, check=False)
    rows = list(csv.reader(result.stdout.decode("utf-8", errors="replace").splitlines()))
    if result.returncode or len(rows) != 1 or len(rows[0]) != 2 or not SID.fullmatch(rows[0][1]):
        raise ContractError("could not identify the current Windows account for the startup trigger")
    return rows[0][1]


def build_startup_task(repo: Path, settings: Path, max_tasks: int = 30) -> bytes:
    if not 1 <= max_tasks <= 100:
        raise ContractError("startup maximum must be 1..100")
    repo, settings = repo.expanduser().absolute(), settings.expanduser().absolute()
    if (repo.is_symlink() or settings.is_symlink() or
            any(p.is_symlink() for p in settings.parents)):
        raise ContractError("startup paths must not contain symlinks")
    if not (repo / "axdev" / "core.py").is_file() or not settings.is_file():
        raise ContractError("approved local project and settings must exist")
    owner = _current_user_sid()
    ET.register_namespace("", NS)
    task = ET.Element("{" + NS + "}Task", version="1.4")
    reg = _element(task, "RegistrationInfo")
    _element(reg, "Description", "AX Dev Factory owner-only approved local queue")
    triggers = _element(task, "Triggers")
    logon = _element(triggers, "LogonTrigger")
    _element(logon, "Enabled", "true")
    _element(logon, "UserId", owner)
    principals = _element(task, "Principals")
    principal = _element(principals, "Principal")
    principal.set("id", "Owner")
    _element(principal, "UserId", owner)
    _element(principal, "LogonType", "InteractiveToken")
    _element(principal, "RunLevel", "LeastPrivilege")
    options = _element(task, "Settings")
    _element(options, "MultipleInstancesPolicy", "IgnoreNew")
    _element(options, "DisallowStartIfOnBatteries", "true")
    _element(options, "StopIfGoingOnBatteries", "true")
    _element(options, "ExecutionTimeLimit", "PT3H")
    _element(options, "Enabled", "true")
    _element(options, "StartWhenAvailable", "false")
    actions = _element(task, "Actions")
    actions.set("Context", "Owner")
    action = _element(actions, "Exec")
    _element(action, "Command", str(Path(sys.executable).resolve()))
    _element(action, "Arguments", "-m scripts.run_configured_queue --settings "
             + subprocess.list2cmdline([str(settings)]) +
             " --max-tasks " + str(max_tasks) + " --execute")
    _element(action, "WorkingDirectory", str(repo.resolve()))
    return ET.tostring(task, encoding="utf-16", xml_declaration=True)


def main(argv=None):
    p = argparse.ArgumentParser(description="Create an opt-in Windows Task Scheduler XML")
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--settings", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--max-tasks", type=int, default=30)
    p.add_argument("--register", action="store_true")
    p.add_argument("--confirm-autorun", action="store_true")
    a = p.parse_args(argv)
    if a.register != a.confirm_autorun:
        raise ContractError("OS registration requires BOTH flags")
    output = a.output.expanduser().absolute()
    if output.is_symlink() or any(p.is_symlink() for p in output.parents):
        raise ContractError("scheduler output path symlink forbidden")
    if output.exists():
        raise ContractError("scheduler XML already exists: no overwrite")
    if os.name != "nt":
        raise ContractError("Windows startup task is only supported on Windows")
    data = build_startup_task(a.repo, a.settings, a.max_tasks)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as file:
        file.write(data)
    if a.register:
        # Never replace an existing OS task; no /F, elevation or hidden launch.
        result = subprocess.run(
            [str(system_directory() / "schtasks.exe"), "/Create", "/TN", "AXDevFactoryOwnerLocal",
             "/XML", str(output)], shell=False, stdin=subprocess.DEVNULL, capture_output=True,
            timeout=30, check=False)
        if result.returncode != 0:
            raise ContractError("OS scheduler registration failed; inspect manually")
    print("OS task registered" if a.register else "XML prepared ONLY; OS unchanged")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, ContractError) as exc:
        print("AXDEV_SCHEDULER_ERROR:", type(exc).__name__)
        raise SystemExit(2)
