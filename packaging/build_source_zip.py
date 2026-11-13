"""Create an auditable source snapshot ZIP, not a Windows executable.

Only explicitly listed source/test/docs are included. Local DBs, credentials,
customer input and Git metadata are never traversed or packed.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ALLOW = [".gitignore", "README.md", "REQUIREMENTS.md", "AGENTS.md", "STATUS.md",
         "HANDOFF.md", "run_bidax.py", "packaging/README.md",
         "packaging/build_windows.ps1", "packaging/build_source_zip.py"]
ALLOW += sorted(str(p.relative_to(ROOT)) for sub in ("bidax", "tests", "docs", "examples")
                for p in (ROOT / sub).glob("**/*") if p.is_file() and p.suffix in (".py", ".md", ".json"))


def build(target: Path) -> dict:
    target = Path(target)
    if target.exists():
        raise FileExistsError("never replace an existing snapshot")
    records={}
    data=[]
    for name in ALLOW:
        p=ROOT/name
        if p.is_symlink() or not p.is_file() or not p.resolve().is_relative_to(ROOT.resolve()):
            raise ValueError("unsafe or missing source file: "+name)
        raw=p.read_bytes()
        data.append((name,raw))
        records[name] = {"sha256":hashlib.sha256(raw).hexdigest(),"bytes":len(raw)}
    manifest={"product":"BID AX", "scope":"SOURCE_ONLY_UNRELEASED", "files":records}
    try:
        with target.open("xb") as out:
            with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED) as z:
                for name,raw in data: z.writestr("BID_AX/"+name,raw)
                z.writestr("BID_AX/MANIFEST.json",json.dumps(manifest,ensure_ascii=False,sort_keys=True,indent=2))
    except Exception:
        target.unlink(missing_ok=True)
        raise
    return {"target":str(target),"files":len(records),"scope":manifest["scope"]}


if __name__ == "__main__":
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("output")
    args=parser.parse_args()
    print(json.dumps(build(Path(args.output)),ensure_ascii=False))
