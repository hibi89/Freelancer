"""Optional AES-GCM backup, not encrypted live SQLite. Passphrases stay local."""
from __future__ import annotations

import hashlib
import os
import sqlite3
from contextlib import closing
from pathlib import Path

from .core import Desk, DeskError

_MAGIC = b"WORKNOVA-AES256GCM-v1\0"
_AAD = b"WORKNOVA Desk offline SQLite encrypted backup v1"
_MAX_DB_BYTES = 128 * 1024 * 1024
_MAX_BACKUP_BYTES = _MAX_DB_BYTES + 4096


def _aead():
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        from cryptography.exceptions import InvalidTag
    except ImportError as exc:
        raise DeskError("optional cryptography package is required for encrypted backup") from exc
    return AESGCM, InvalidTag


def _password(value: str) -> bytes:
    if not isinstance(value, str) or len(value) < 12 or len(value) > 256 or "\x00" in value:
        raise DeskError("backup passphrase must contain 12..256 characters")
    return value.encode("utf-8")


def _key(passphrase: str, salt: bytes) -> bytes:
    return hashlib.scrypt(_password(passphrase), salt=salt, n=2**14, r=8, p=1, dklen=32)


def _safe_new_path(path: str | Path) -> Path:
    dst = Path(path)
    if not dst.parent.is_dir() or dst.parent.is_symlink() or dst.exists() or dst.is_symlink():
        raise DeskError("encrypted backup/restore needs a NEW file in an existing plain directory")
    return dst


def _write_exclusive(path: Path, data: bytes) -> None:
    fd = None
    created = False
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        created = True
        with os.fdopen(fd, 'wb') as stream:
            fd = None
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError:
        raise DeskError("backup/restore destination already exists") from None
    except Exception:
        if fd is not None:
            os.close(fd)
        if created:
            path.unlink(missing_ok=True)
        raise


def encrypted_backup(desk: Desk, destination: str | Path, passphrase: str) -> dict:
    """Take consistent in-memory SQLite backup, encrypt, write new private blob."""
    AESGCM, _ = _aead()
    dst = _safe_new_path(destination)
    if dst.resolve() == desk.path.resolve():
        raise DeskError("cannot replace active ledger")
    _password(passphrase)
    desk.verify_audit()
    with closing(sqlite3.connect(':memory:')) as snapshot:
        desk.db.backup(snapshot)
        if snapshot.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
            raise DeskError("source snapshot failed integrity check")
        data = snapshot.serialize()
    if len(data) > _MAX_DB_BYTES:
        raise DeskError("encrypted backup exceeds 128 MiB in-memory safety limit")
    salt = os.urandom(16)
    nonce = os.urandom(12)
    encrypted = AESGCM(_key(passphrase, salt)).encrypt(nonce, data, _AAD)
    blob = _MAGIC + salt + nonce + encrypted
    _write_exclusive(dst, blob)
    return {"encrypted": True, "algorithm": "AES-256-GCM", "kdf": "scrypt-16384-8-1",
            "sha256": hashlib.sha256(blob).hexdigest(), "bytes": len(blob),
            "note": "Encrypted backup only; the source SQLite ledger remains unencrypted"}


def encrypted_restore_new(source: str | Path, destination: str | Path, passphrase: str,
                          *, expected_sha256: str | None = None) -> dict:
    """Authenticate backup in RAM; restore to a NEW path only, never overwrite."""
    AESGCM, InvalidTag = _aead()
    src = Path(source)
    dst = _safe_new_path(destination)
    if not src.is_file() or src.is_symlink() or src.stat().st_size > _MAX_BACKUP_BYTES:
        raise DeskError("encrypted source must be a regular file <= 128 MiB")
    if src.resolve() == dst.resolve():
        raise DeskError("source and destination cannot be the same")
    blob = src.read_bytes()
    sha = hashlib.sha256(blob).hexdigest()
    if expected_sha256 is not None:
        if (not isinstance(expected_sha256, str) or len(expected_sha256) != 64 or
                not all(c in '0123456789abcdef' for c in expected_sha256.lower()) or
                sha != expected_sha256.lower()):
            raise DeskError("encrypted source SHA256 differs from separately retained pin")
    header = len(_MAGIC)
    if not blob.startswith(_MAGIC) or len(blob) < header + 16 + 12 + 16 + 100:
        raise DeskError("not a valid WORKNOVA encrypted backup")
    salt, nonce, payload = blob[header:header+16], blob[header+16:header+28], blob[header+28:]
    try:
        raw = AESGCM(_key(passphrase, salt)).decrypt(nonce, payload, _AAD)
    except InvalidTag as exc:
        raise DeskError("wrong passphrase or encrypted backup was modified") from exc
    if len(raw) > _MAX_DB_BYTES or not raw.startswith(b'SQLite format 3\x00'):
        raise DeskError("encrypted payload is not a supported SQLite database")
    try:
        with closing(sqlite3.connect(':memory:')) as check:
            check.deserialize(raw)
            if check.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                raise DeskError("encrypted backup contains damaged SQLite data")
            version = check.execute('PRAGMA user_version').fetchone()[0]
            if version not in (1, 2):
                raise DeskError("encrypted backup has unsupported WORKNOVA schema")
    except sqlite3.DatabaseError as exc:
        raise DeskError("encrypted backup SQLite validation failed") from exc
    _write_exclusive(dst, raw)
    try:
        ledger = Desk(dst, allow_create=False)
        try:
            events = ledger.verify_audit()
            if ledger.schema_version != version:
                raise DeskError("restored schema version mismatch")
        finally:
            ledger.close()
    except Exception:
        dst.unlink(missing_ok=True)
        raise
    return {"restored": True, "schema_version": version, "verified_events": events,
            "encrypted_source_sha256": sha,
            "note": "New plaintext SQLite created; apply OS file protection immediately"}
