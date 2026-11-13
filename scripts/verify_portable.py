"""Offline local package integrity verifier, requires no dependencies.

Note: hashes in an unsigned manifest detect corruption, not malicious re-signing.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import stat
from pathlib import Path

EXPECTED = frozenset({
    "worknova_desk/__init__.py",
    "worknova_desk/__main__.py",
    "worknova_desk/core.py",
    "worknova_desk/gui.py",
    "worknova_desk/documents.py",
    "worknova_desk/evidence.py",
    "worknova_desk/delivery_evidence.py",
    "worknova_desk/lifecycle.py",
    "launch.cmd", "install_local.ps1", "README_OFFLINE.txt", "verify_portable.py",
})
FORMAT = "worknova-p85-portable-v2"
HEX = re.compile(r"^[0-9a-f]{64}$")

class PackageError(ValueError):
    pass


def _regular(path: Path) -> bool:
    if path.is_symlink():
        return False
    try:
        mode = path.lstat().st_mode
        return stat.S_ISREG(mode)
    except OSError:
        return False


def verify(root: str | Path) -> dict:
    root = Path(root)
    if not root.is_dir() or root.is_symlink():
        raise PackageError("unsafe package directory")
    manifest = root/"FILE_MANIFEST.json"
    if not _regular(manifest) or manifest.stat().st_size > 32768:
        raise PackageError("missing/oversized package manifest")
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except (UnicodeError, ValueError) as exc:
        raise PackageError("invalid package manifest") from exc
    if not isinstance(data, dict) or data.get("format") != FORMAT or not isinstance(data.get("files"), list):
        raise PackageError("unsupported manifest")
    entries = data["files"]
    if len(entries) != len(EXPECTED):
        raise PackageError("incomplete/extra manifest entries")
    seen = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise PackageError("invalid entry")
        name = entry.get("path")
        if not isinstance(name, str) or name not in EXPECTED or name.casefold() in seen:
            raise PackageError("unexpected/duplicate path")
        seen.add(name.casefold())
        size = entry.get("bytes")
        checksum = entry.get("sha256")
        if type(size) is not int or size < 0 or size > 1024 * 1024 or not isinstance(checksum,str) or not HEX.fullmatch(checksum):
            raise PackageError("invalid file size/hash")
        path = root.joinpath(*name.split("/"))
        if path.parent.is_symlink() or not _regular(path):
            raise PackageError("missing file or symbolic link")
        if path.stat().st_size != size:
            raise PackageError("file size mismatch")
        digest=hashlib.sha256()
        with path.open("rb") as stream:
            while block:=stream.read(65536):
                digest.update(block)
        if digest.hexdigest()!=checksum:
            raise PackageError("file digest mismatch")
    if seen != {n.casefold() for n in EXPECTED}:
        raise PackageError("missing required file")
    # Executable unlisted files could change import resolution; cache from Python is ignored.
    for candidate in root.rglob("*"):
        if candidate.is_symlink():
            raise PackageError("symlink in package tree")
        if "__pycache__" in candidate.parts:
            continue
        if candidate.is_file() and candidate.suffix.lower() in (".py", ".pth", ".pyd", ".dll", ".cmd", ".ps1"):
            rel = candidate.relative_to(root).as_posix()
            if rel not in EXPECTED:
                raise PackageError("unlisted executable code in package")
    return {"ok": True, "verified_files": len(EXPECTED),
            "manifest_sha256":hashlib.sha256(manifest.read_bytes()).hexdigest(),
            "note":"Unsigned hashes check accidental corruption, not authenticity; customer data untouched"}


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--root",required=True)
    args=p.parse_args()
    try:
        print(json.dumps(verify(args.root), sort_keys=True))
        return 0
    except (PackageError,OSError) as exc:
        print(json.dumps({"ok":False,"error":str(exc)}))
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
