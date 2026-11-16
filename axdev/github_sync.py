"""Import an approved PUBLIC GitHub task plan without running or pushing anything."""
from __future__ import annotations
import base64
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from urllib.parse import quote
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener
from .core import ContractError, load_plan, safe_path

REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
BRANCH = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,149}$")
SHA = re.compile(r"^[0-9a-f]{40}$")
LIMIT = 512 * 1024

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ContractError("GitHub redirect refused")

def github_get(url):
    if not url.startswith("https://api.github.com/repos/"):
        raise ContractError("only GitHub API GET allowed")
    opener = build_opener(ProxyHandler({}), NoRedirect())
    request = Request(url, headers={"User-Agent": "axdev-plan-import/1",
                                    "Accept": "application/vnd.github+json"})
    with opener.open(request, timeout=12) as response:
        body = response.read(1500001)
    if len(body) > 1500000:
        raise ContractError("GitHub API response too large")
    data = json.loads(body)
    if not isinstance(data, dict):
        raise ContractError("unexpected response")
    return data

def branch_sha(repo, branch):
    url = "https://api.github.com/repos/{}/git/ref/heads/{}".format(
        repo, quote(branch, safe="/"))
    sha = github_get(url).get("object", {}).get("sha")
    if not isinstance(sha, str) or not SHA.fullmatch(sha):
        raise ContractError("invalid branch SHA")
    return sha

def sync_public_plan(repo, branch, path, expected_sha, output):
    if (not isinstance(repo, str) or not REPO.fullmatch(repo)
            or any(part in (".", "..") for part in repo.split("/"))):
        raise ContractError("invalid owner/repo")
    if (not isinstance(branch, str) or not BRANCH.fullmatch(branch)
            or ".." in branch or "//" in branch or branch.endswith(("/", ".lock"))):
        raise ContractError("invalid branch")
    if not isinstance(path, str):
        raise ContractError("invalid plan path")
    safe_path(path)
    if not path.endswith(".json"):
        raise ContractError("plan must be JSON")
    if not isinstance(expected_sha, str) or not SHA.fullmatch(expected_sha):
        raise ContractError("previously reviewed commit SHA required")
    first = branch_sha(repo, branch)
    if first != expected_sha:
        raise ContractError("branch changed since approval")
    url = "https://api.github.com/repos/{}/contents/{}?ref={}".format(
        repo, quote(path, safe="/"), first)
    data = github_get(url)
    if data.get("type") != "file" or data.get("encoding") != "base64":
        raise ContractError("expected inline base64 file")
    encoded = data.get("content")
    if not isinstance(encoded, str) or len(encoded) > 1500000:
        raise ContractError("bad remote file")
    try:
        raw = base64.b64decode("".join(encoded.split()), validate=True)
    except (ValueError, base64.binascii.Error) as exc:
        raise ContractError("invalid base64") from exc
    if not raw or len(raw) > LIMIT:
        raise ContractError("plan size exceeds limit")
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if blob != data.get("sha"):
        raise ContractError("GitHub blob mismatch")
    try:
        decoded = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ContractError("plan must be UTF-8") from exc
    with tempfile.TemporaryDirectory(prefix="axdev-plan-") as root:
        candidate = Path(root) / "plan.json"
        candidate.write_text(decoded, encoding="utf-8")
        try:
            tasks = load_plan(candidate)
        except (ValueError, TypeError, AttributeError, KeyError) as exc:
            raise ContractError("remote plan contract rejected") from exc
    if branch_sha(repo, branch) != first:
        raise ContractError("branch advanced during import")
    output = Path(output).expanduser().absolute()
    if output.is_symlink() or any(parent.is_symlink() for parent in output.parents):
        raise ContractError("symlink output or parent refused")
    if output.exists():
        if not output.is_file() or output.read_bytes() != raw:
            raise ContractError("existing plan differs: no overwrite")
        created = False
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        try:
            fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError as exc:
            raise ContractError("output appeared during import") from exc
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(raw)
        except BaseException:
            output.unlink(missing_ok=True)
            raise
        created = True
    return {"repo": repo, "branch": branch, "source_sha": first,
            "blob_sha": blob, "sha256": hashlib.sha256(raw).hexdigest(),
            "tasks": len(tasks), "output": str(output),
            "created": created, "executed": False}
