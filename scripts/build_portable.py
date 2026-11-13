"""Build deterministic, strictly allowlisted, offline Python Windows portable ZIP.

This is not a standalone EXE, a signed installer or proof of native Windows QA.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import zipfile
from pathlib import Path

# Make the documented ``python scripts/build_portable.py`` command work from
# a clean source checkout, not only when PYTHONPATH was exported beforehand.
if __name__ == "__main__" and not __package__:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from worknova_desk.core import DeskError

SOURCE_FILES = ['worknova_desk/__init__.py', 'worknova_desk/__main__.py',
                'worknova_desk/core.py', 'worknova_desk/gui.py', 'worknova_desk/documents.py',
                'worknova_desk/evidence.py','worknova_desk/delivery_evidence.py','worknova_desk/lifecycle.py','worknova_desk/recovery.py', 'worknova_desk/privacy.py']
SCRIPTS = [('scripts/launch.cmd','launch.cmd'),
           ('scripts/install_local.ps1','install_local.ps1'),
           ('scripts/verify_portable.py','verify_portable.py'),
           ('scripts/README_OFFLINE.txt','README_OFFLINE.txt')]


def bundle(root: Path, output: Path) -> dict:
    root = Path(root)
    output = Path(output)
    if output.suffix.lower() != '.zip' or not output.parent.is_dir() or output.exists() or output.is_symlink():
        raise DeskError('portable ZIP must be a NEW .zip in existing directory')
    content = {}
    for source, name in [(p,p) for p in SOURCE_FILES] + SCRIPTS:
        path = root / source
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 1024*1024:
            raise DeskError(f'invalid package source: {source}')
        content[name] = path.read_bytes()
    manifest={'format':'worknova-p85-portable-v3',
              'kind':'Python source + per-user PowerShell installer; requires local Python; unsigned; RELEASE HOLD',
              'files':[{'path':name,'bytes':len(payload),'sha256':hashlib.sha256(payload).hexdigest()}
                       for name,payload in sorted(content.items())]}
    content['FILE_MANIFEST.json'] = (json.dumps(manifest,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf-8')
    buffer=io.BytesIO()
    with zipfile.ZipFile(buffer,'w') as archive:
        for name,payload in sorted(content.items()):
            info=zipfile.ZipInfo(name, date_time=(2020,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o600<<16
            archive.writestr(info,payload)
    data=buffer.getvalue()
    # read-back verifies every member; deterministic bytes + no duplicates/hidden payloads.
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        assert set(archive.namelist()) == set(content)
        assert archive.testzip() is None
        for name, payload in content.items():
            if archive.read(name) != payload:
                raise DeskError(f'archive content mismatch: {name}')
    created=False
    try:
        with output.open('xb') as stream:
            created=True
            stream.write(data)
    except Exception:
        if created and output.exists():
            output.unlink()
        raise
    return {'file_count': len(content), 'bytes':len(data), 'sha256':hashlib.sha256(data).hexdigest()}


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--out',required=True)
    args=p.parse_args()
    print(json.dumps(bundle(Path(__file__).resolve().parents[1], Path(args.out)),sort_keys=True))
