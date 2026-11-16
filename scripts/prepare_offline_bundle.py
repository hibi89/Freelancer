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
from axdev.sandbox_payload import no_reparse
from axdev.windows_sandbox_runtime import MAX_MANIFEST, bundle_inventory


def build_manifest(bundle: Path) -> dict:
    return {"version": 2, "files": bundle_inventory(bundle)}


def main(argv=None):
    p = argparse.ArgumentParser(description="Create-only local offline toolchain manifest")
    p.add_argument("--offline-bundle", type=Path, required=True)
    a = p.parse_args(argv)
    bundle = no_reparse(a.offline_bundle)
    manifest = no_reparse(bundle / "manifest.json")
    if manifest.exists():
        raise ContractError("manifest exists; refusing overwrite")
    data = (json.dumps(build_manifest(bundle), ensure_ascii=False,
                       indent=2, sort_keys=True) + "\n").encode("utf-8")
    if len(data) > MAX_MANIFEST:
        raise ContractError("offline bundle manifest exceeds size limit")
    with manifest.open("xb") as output:
        output.write(data)
    digest = hashlib.sha256(data).hexdigest()
    print(json.dumps({"manifest_sha256": digest, "bundle": str(bundle),
                      "models_pinned": True,
                      "external_downloads": False, "executed": False},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, ContractError) as exc:
        print("AXDEV_OFFLINE_BUNDLE_ERROR:", type(exc).__name__)
        raise SystemExit(2)
