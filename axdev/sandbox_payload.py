"""Portable snapshot and data-only candidate format shared with the coding guest."""
from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import tempfile
import zipfile

from .core import ContractError, safe_path

SHA40 = re.compile(r"[0-9a-f]{40}")
SHA256 = re.compile(r"[0-9a-f]{64}")
RUN_ID = re.compile(r"[0-9a-f]{32}")
MAX_ARCHIVE = 64 * 1024 * 1024
MAX_CODE = 8 * 1024 * 1024
MAX_RECEIPT = 12 * 1024 * 1024
BINARIES = ("python/python.exe", "git/cmd/git.exe", "ollama/ollama.exe", "opencode/opencode.exe")


def hex_sha(path: Path) -> str:
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def json_bytes(value) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()


def write_json(path: Path, value) -> str:
    raw = json_bytes(value)
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".")
    try:
        with os.fdopen(descriptor, "wb") as out:
            out.write(raw)
            out.flush()
            os.fsync(out.fileno())
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)
    return hashlib.sha256(raw).hexdigest()


def no_reparse(path: Path) -> Path:
    absolute = path.expanduser().absolute()
    for item in (absolute, *absolute.parents):
        try:
            meta = item.lstat()
        except FileNotFoundError:
            continue
        if (stat.S_ISLNK(meta.st_mode) or getattr(meta, "st_file_attributes", 0) & 0x400):
            raise ContractError("sandbox path uses a symlink or reparse point")
    return absolute


def read_json(path: Path, limit: int) -> tuple[dict, str]:
    file = no_reparse(path)
    if not file.is_file() or file.stat().st_size > limit:
        raise ContractError("sandbox data file is absent, unsafe or oversized")
    with file.open("rb") as source:
        raw = source.read(limit + 1)
    if len(raw) > limit:
        raise ContractError("sandbox data exceeds size limit")
    try:
        data = json.loads(raw, object_pairs_hook=_unique_keys)
    except (ValueError, RecursionError) as exc:
        raise ContractError("invalid sandbox JSON") from exc
    if not isinstance(data, dict):
        raise ContractError("sandbox data must be an object")
    return data, hashlib.sha256(raw).hexdigest()


def _unique_keys(entries):
    value = dict(entries)
    if len(entries) != len(value):
        raise ValueError("duplicate JSON keys")
    return value


def portable_path(name: str) -> str:
    parts = name.split("/")
    # Reuse the Windows lexical rules while permitting tracked .gitignore,
    # .github and .opencode content in a read-only source snapshot.
    normalized = "/".join("_" + p if p.startswith(".") and p not in (".", "..") else p for p in parts)
    safe_path(normalized)
    if (len(name) > 240 or any(p.casefold() == ".git" or re.search(r"~[0-9]", p) for p in parts)
            or any(p.casefold() in {".ssh", ".aws", ".gnupg", "id_rsa", "id_ed25519", ".npmrc", ".netrc"}
                   or p.casefold().startswith(".env") and p.casefold() != ".env.example"
                   or p.casefold().endswith((".pfx", ".p12", ".key")) for p in parts)):
        raise ContractError("sandbox snapshot contains an unsafe or sensitive path")
    return name


def snapshot_entries(archive: zipfile.ZipFile):
    entries = archive.infolist()
    if not entries or len(entries) > 6000:
        raise ContractError("sandbox snapshot entry limit")
    names = {}
    budget = MAX_ARCHIVE
    for entry in entries:
        name = portable_path(entry.filename.rstrip("/"))
        path = name.split("/")
        for offset in range(1, len(path) + 1):
            parent = "/".join(path[:offset])
            if names.setdefault(parent.casefold(), parent) != parent:
                raise ContractError("sandbox snapshot path alias")
        if stat.S_ISLNK(entry.external_attr >> 16):
            raise ContractError("sandbox snapshot contains a symlink")
        if not entry.is_dir():
            budget -= entry.file_size
            if budget < 0:
                raise ContractError("sandbox snapshot decompression limit")
            yield name, entry


def extract_snapshot(source: Path, destination: Path) -> None:
    if not source.is_file() or source.stat().st_size > MAX_ARCHIVE:
        raise ContractError("sandbox snapshot is absent or oversized")
    destination.mkdir(parents=True, exist_ok=False)
    with zipfile.ZipFile(source) as archive:
        for name, entry in snapshot_entries(archive):
            target = destination / Path(name)
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as file:
                file.write(archive.read(entry))


def encode_files(files: dict[str, bytes | None]) -> list[dict]:
    return [{"path": name, "sha256": hashlib.sha256(data).hexdigest() if data is not None else None,
             "data_b64": base64.b64encode(data).decode() if data is not None else None}
            for name, data in sorted(files.items())]


def decode_files(items, approved: set[str]) -> dict[str, bytes | None]:
    if not isinstance(items, list) or not 1 <= len(items) <= 16:
        raise ContractError("sandbox candidate file count invalid")
    decoded = {}
    seen = set()
    remaining = MAX_CODE
    for item in items:
        if not isinstance(item, dict) or set(item) != {"path", "sha256", "data_b64"}:
            raise ContractError("sandbox candidate file fields invalid")
        name = item["path"]
        if safe_path(name) not in approved or name.casefold() in seen:
            raise ContractError("sandbox candidate file outside allowlist or repeated")
        portable_path(name)
        seen.add(name.casefold())
        value, digest = item["data_b64"], item["sha256"]
        if value is None and digest is None:
            decoded[name] = None
            continue
        if not isinstance(value, str) or not isinstance(digest, str) or not SHA256.fullmatch(digest):
            raise ContractError("sandbox candidate data fields invalid")
        try:
            data = base64.b64decode(value, validate=True)
        except ValueError as exc:
            raise ContractError("sandbox candidate base64 invalid") from exc
        remaining -= len(data)
        if remaining < 0 or hashlib.sha256(data).hexdigest() != digest:
            raise ContractError("sandbox candidate byte budget or hash differs")
        decoded[name] = data
    return decoded
