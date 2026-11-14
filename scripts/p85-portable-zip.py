"""Strict standard-library ZIP round-trip for self-contained SYNTHETIC Windows QA.
No network, published release, external credentials or customer content.
"""
import hashlib
import json
import pathlib
import sys
import zipfile


def checksum(file_path):
    digest = hashlib.sha256()
    with open(file_path, 'rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def main():
    if len(sys.argv) != 4:
        raise ValueError('USAGE: source-directory target.zip new-output-directory')
    root = pathlib.Path(sys.argv[1]).resolve(strict=True)
    archive = pathlib.Path(sys.argv[2]).resolve(strict=False)
    output = pathlib.Path(sys.argv[3]).resolve(strict=False)
    if not root.is_dir() or archive.exists() or output.exists() or not archive.parent.is_dir():
        raise ValueError('INVALID_TARGET')
    items = []
    for item in sorted(root.rglob('*')):
        if item.is_symlink():
            raise ValueError('SYMLINK_REJECTED')
        if item.is_dir():
            continue
        if not item.is_file():
            raise ValueError('UNEXPECTED_SOURCE_TYPE')
        name = item.relative_to(root).as_posix()
        if not name or '..' in pathlib.PurePosixPath(name).parts or name.startswith('/'):
            raise ValueError('PATH_INVALID')
        items.append((name, item, checksum(item)))
    if not items or len(items) > 64:
        raise ValueError('FILE_COUNT_INVALID')
    names = [n for n, _, _ in items]
    if len(set(n.lower() for n in names)) != len(names):
        raise ValueError('DUPLICATE_CASE_NAME')
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as z:
        for name, item, _ in items:
            z.write(item, arcname=name)
    with zipfile.ZipFile(archive, 'r') as z:
        if z.testzip() is not None:
            raise ValueError('ZIP_CRC_FAILED')
        if z.namelist() != names:
            raise ValueError('ZIP_MEMBER_MISMATCH')
        # Extract only exact allowlisted build members, never arbitrary uploaded archives.
        output.mkdir(parents=False)
        for name, _, _ in items:
            z.extract(name, path=output)
    for name, _, before in items:
        after = output.joinpath(*name.split('/'))
        if checksum(after) != before:
            raise ValueError('ROUNDTRIP_DIGEST_MISMATCH')
    print(json.dumps({'status': 'PORTABLE_ZIP_ROUNDTRIP_PASS', 'files': len(items),
                      'network_calls': 0, 'archive_bytes': archive.stat().st_size}))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        print(json.dumps({'status': 'FAIL', 'error': str(error)[:180]}), file=sys.stderr)
        sys.exit(1)
