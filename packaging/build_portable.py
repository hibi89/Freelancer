"""Build a deterministic Python 3.11+ zipapp, not a Windows EXE or installer.

No network, third-party dependencies, customer files, or credentials.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MAIN = b'from bidax.cli import main\n\nif __name__ == "__main__":\n    main()\n'
STAMP = (2020, 1, 1, 0, 0, 0)


def build(destination: Path) -> dict:
    destination = Path(destination)
    if destination.exists():
        raise FileExistsError("portable package exists; not overwritten")
    paths = sorted((ROOT / "bidax").glob("*.py"))
    files = {}
    for path in paths:
        if path.is_symlink() or not path.resolve().is_relative_to(ROOT.resolve()):
            raise ValueError("unsafe source file")
        files[f"bidax/{path.name}"] = path.read_bytes()
    files["__main__.py"] = MAIN
    hashes = {path: hashlib.sha256(blob).hexdigest() for path, blob in sorted(files.items())}
    manifest = {"product": "BID AX", "format": "PYTHON_ZIPAPP_NOT_EXE",
                "status": "UNRELEASED", "files": hashes}
    files["BIDAX_MANIFEST.json"] = json.dumps(manifest, ensure_ascii=False, sort_keys=True,
                                                separators=(",", ":")).encode("utf-8")
    try:
        with destination.open("xb") as stream:
            with zipfile.ZipFile(stream,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
                for path, blob in sorted(files.items()):
                    entry = zipfile.ZipInfo(path, date_time=STAMP)
                    entry.compress_type = zipfile.ZIP_DEFLATED
                    entry.external_attr = (0o644 << 16)
                    archive.writestr(entry, blob, compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    return {"path": str(destination), "files":len(files), "sha256":hashlib.sha256(destination.read_bytes()).hexdigest(),
            "status": "UNRELEASED_PYTHON_REQUIRED"}


if __name__ == "__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("output")
    options=ap.parse_args()
    print(json.dumps(build(Path(options.output))))
