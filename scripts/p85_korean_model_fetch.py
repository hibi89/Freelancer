"""Explicit, synthetic CI-only downloader for fixed public Xenova ONNX artifacts.
Never downloads private data and never writes to an existing destination.
"""
from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import shutil
import urllib.request

BASE = "https://huggingface.co/Xenova/multilingual-e5-small/resolve/main/"
FILES = {
    "config.json": 1_000_000,
    "tokenizer.json": 25_000_000,
    "tokenizer_config.json": 1_000_000,
    "special_tokens_map.json": 1_000_000,
    "onnx/model_int8.onnx": 128 * 1024 * 1024,
}
MODEL_SHA = "4d24e2bc01a447951524466ef533e52944bf48509e6552810bcee1a2711cb02c"


def fetch_public_model(dest: Path) -> dict:
    if not dest.is_absolute() or dest.exists():
        raise ValueError("NEW_ABSOLUTE_DESTINATION_REQUIRED")
    dest.mkdir(mode=0o700, parents=True, exist_ok=False)
    try:
        observed = {}
        for name, max_bytes in FILES.items():
            target = dest / name
            target.parent.mkdir(parents=True, exist_ok=True)
            sha = hashlib.sha256()
            total = 0
            request = urllib.request.Request(
                BASE + name, headers={"User-Agent": "CITEVAULT-synthetic-public-model-smoke/1.0"}
            )
            with urllib.request.urlopen(request, timeout=120) as src, target.open("xb") as out:
                while True:
                    chunk = src.read(1024 * 1024)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > max_bytes:
                        raise ValueError("PUBLIC_MODEL_FILE_TOO_LARGE")
                    sha.update(chunk)
                    out.write(chunk)
            if total < 2:
                raise ValueError("PUBLIC_MODEL_FILE_EMPTY")
            observed[name] = {"sha256": sha.hexdigest(), "bytes": total}
        if observed["onnx/model_int8.onnx"]["sha256"] != MODEL_SHA:
            raise ValueError("PUBLIC_MODEL_HASH_MISMATCH")
        return {"status": "PUBLIC_ASSET_HASH_VERIFIED", "onnx_sha256": MODEL_SHA}
    except Exception:
        shutil.rmtree(dest, ignore_errors=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dest", type=Path, required=True)
    args = parser.parse_args()
    result = fetch_public_model(args.dest)
    print(result["status"], result["onnx_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
