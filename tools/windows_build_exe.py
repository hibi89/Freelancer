"""Optional local-only Windows PyInstaller build for WORKNOVA Desk.

No package installation, downloads, signing, cloud runner or charge. Requires a
pre-installed copy of PyInstaller on a real Windows machine. The resulting
unsigned onedir executable is NOT certified safe for release or real customers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENTRY = ROOT / 'tools' / 'windows_gui_entry.py'
APP_NAME = 'WORKNOVA-Desk'


class BuildError(ValueError):
    pass


def _assert_no_links(path: Path) -> None:
    for ancestor in (path, *path.parents):
        if ancestor.is_symlink():
            raise BuildError('Build path has a symbolic link')
        if ancestor.exists():
            attrs = getattr(ancestor.stat(follow_symlinks=False), 'st_file_attributes', 0)
            if attrs & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0):
                raise BuildError('Build path has a junction/reparse point')


def plan(output: Path) -> dict:
    """Validate a new, disposable destination without writing anything."""
    output = Path(output).absolute()
    _assert_no_links(output)
    if output.exists():
        raise BuildError('Output path already exists; existing data is never replaced')
    if not output.parent.is_dir():
        raise BuildError('Output parent folder must already exist')
    if output == ROOT or ROOT in output.parents or output in ROOT.parents:
        raise BuildError('Build must be outside the source repository')
    appdata = os.environ.get('LOCALAPPDATA', '')
    if appdata:
        protected = Path(appdata).absolute() / 'WORKNOVA Desk' / 'Data'
        if output == protected or protected in output.parents or output in protected.parents:
            raise BuildError('Build destination overlaps customer data')
    if not ENTRY.is_file() or ENTRY.is_symlink():
        raise BuildError('Original GUI entrypoint is missing or unsafe')
    command = [sys.executable, '-m', 'PyInstaller', '--onedir', '--windowed',
               '--noupx', '--clean', '--noconfirm', '--name', APP_NAME,
               '--paths', str(ROOT),
               '--distpath', str(output / 'dist'), '--workpath', str(output / 'build'),
               '--specpath', str(output / 'spec'), str(ENTRY)]
    return {'output': str(output), 'argv': command, 'requires': 'native Windows with locally installed PyInstaller',
            'network': False, 'signed': False, 'production_ready': False}


def build(output: Path) -> dict:
    if sys.platform != 'win32':
        raise BuildError('Windows EXE requires native Windows; Linux builds cannot certify it')
    spec = plan(output)
    destination = Path(spec['output'])
    # Exclusive create: never remove or overwrite a previous build or user data.
    destination.mkdir(mode=0o700)
    env = os.environ.copy()
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    env['PYTHONNOUSERSITE'] = '1'
    try:
        with (destination / 'build.log').open('x', encoding='utf-8') as log:
            proc = subprocess.run(spec['argv'], cwd=str(ROOT), env=env,
                                  stdout=log, stderr=subprocess.STDOUT,
                                  timeout=1200, check=False)
        if proc.returncode != 0:
            raise BuildError('PyInstaller failed; inspect private local build.log')
        exe = destination / 'dist' / APP_NAME / (APP_NAME + '.exe')
        if not exe.is_file() or exe.is_symlink():
            raise BuildError('Expected standalone Windows EXE is missing')
        with exe.open('rb') as stream:
            if stream.read(2) != b'MZ':
                raise BuildError('Output is not a Windows executable')
            stream.seek(0)
            digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        return {'ok': True, 'path': str(exe), 'bytes': exe.stat().st_size,
                'sha256': digest, 'mode': 'onedir (Python not required on target)',
                'signed': False, 'native_gui_test': 'NOT_RUN', 'defender_test': 'NOT_RUN',
                'release': 'HOLD'}
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise BuildError('Offline build failed; inspect private local build.log') from exc


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description='Offline native-Windows EXE candidate build (unsigned)')
    parser.add_argument('--out', required=True, help='NEW output directory outside the repository and customer data')
    parser.add_argument('--plan', action='store_true', help='Validate inputs without creating files or executing tools')
    args = parser.parse_args(argv)
    try:
        report = plan(Path(args.out)) if args.plan else build(Path(args.out))
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
        return 0
    except BuildError as exc:
        print(json.dumps({'ok': False, 'error': str(exc), 'release': 'HOLD'}, ensure_ascii=False))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
