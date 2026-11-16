"""Create-only SHA256 manifest for a user-provided offline Sandbox bundle.

This does not download/install anything, execute a model, or modify OS policy.
An owner separately vets the portable binaries and their supply-chain origin.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from axdev.core import ContractError
from axdev.windows_sandbox_runtime import BINARIES, _no_reparse


def build_manifest(bundle: Path) -> dict:
    root = _no_reparse(bundle)
    if not root.is_dir():
        raise ContractError("offline bundle root is absent")
    results = {}
    for name in BINARIES:
        file = _no_reparse(root / Path(name))
        if not file.is_file():
            raise ContractError("required portable offline binary missing")
        hasher = hashlib.sha256()
        with file.open("rb") as stream:
            while True:
                data = stream.read(1024 * 1024)
                if not data:
                    break
                hasher.update(data)
        results[name] = hasher.hexdigest()
    if not _no_reparse(root / "models").is_dir():
        raise ContractError("offline Ollama model cache absent")
    return {"version": 1, "executables": results,
            "models_pinned_by_this_manifest": False,
            "source_trust": "OWNER_MUST_CONFIRM"}


def main(argv=None):
    p = argparse.ArgumentParser(description="Create-only local offline toolchain manifest")
    p.add_argument("--offline-bundle", type=Path, required=True)
    a = p.parse_args(argv)
    bundle = _no_reparse(a.offline_bundle)
    manifest = _no_reparse(bundle / "manifest.json")
    if manifest.exists():
        raise ContractError("manifest exists; refusing overwrite")
    data = (json.dumps(build_manifest(bundle), ensure_ascii=False,
                       indent=2, sort_keys=True) + "\n").encode("utf-8")
    with manifest.open("xb") as output:
        output.write(data)
    digest = hashlib.sha256(data).hexdigest()
    print(json.dumps({"manifest_sha256": digest, "bundle": str(bundle),
                      "models_pinned": False,
                      "external_downloads": False, "executed": False},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, ContractError) as exc:
        print("AXDEV_OFFLINE_BUNDLE_ERROR:", type(exc).__name__)
        raise SystemExit(2)
