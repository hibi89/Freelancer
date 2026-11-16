"""Create-only Windows Sandbox template; never auto-launch or alter policies.

Windows Sandbox is edition-dependent; a generated .wsb is a proposal,
not proof of a sandbox or network isolation on the owner Windows10 device.
The chosen workspace is mounted READ-ONLY, clipboard/network/vGPU denied.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
from xml.etree import ElementTree as ET

from axdev.core import ContractError


def build_wsb(disposable_checkout: Path) -> bytes:
    root = disposable_checkout.expanduser().absolute()
    if root.is_symlink() or any(p.is_symlink() for p in root.parents):
        raise ContractError("sandbox checkout cannot have symlink parents")
    if not (root / ".git").exists():
        raise ContractError("sandbox source must be a disposable Git checkout")
    sandbox = ET.Element("Configuration")
    for name in ("Networking", "ClipboardRedirection", "PrinterRedirection",
                 "AudioInput", "VideoInput", "VGpu"):
        ET.SubElement(sandbox, name).text = "Disable"
    folders = ET.SubElement(sandbox, "MappedFolders")
    folder = ET.SubElement(folders, "MappedFolder")
    ET.SubElement(folder, "HostFolder").text = str(root.resolve())
    ET.SubElement(folder, "SandboxFolder").text = "C:\\AXDEV_READ_ONLY"
    ET.SubElement(folder, "ReadOnly").text = "true"
    return ET.tostring(sandbox, encoding="utf-8", xml_declaration=True)


def main(argv=None):
    p = argparse.ArgumentParser(description="Prepare a no-network Windows Sandbox .wsb")
    p.add_argument("--disposable-checkout", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args(argv)
    if os.name != "nt":
        raise ContractError("Windows Sandbox template must be prepared on Windows")
    output = a.output.expanduser().absolute()
    if output.is_symlink() or any(p.is_symlink() for p in output.parents):
        raise ContractError("output path symlink forbidden")
    if output.exists():
        raise ContractError("sandbox configuration exists: refuse overwrite")
    data = build_wsb(a.disposable_checkout)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as out:
        out.write(data)
    print("Windows Sandbox template created (NOT launched, OS policy unchanged)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ContractError) as exc:
        print("AXDEV_SANDBOX_PREP_ERROR:", type(exc).__name__)
        raise SystemExit(2)
