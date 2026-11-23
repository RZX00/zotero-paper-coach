#!/usr/bin/env python3
"""Build zotero-paper-coach.skill from the zotero-paper-coach/ folder, or check that it is current.

    python tools/pack_skill.py           rebuild the archive
    python tools/pack_skill.py --check   exit 1 if the archive and the folder differ

The archive is a zip of the skill folder. Entries are stored in sorted order with a
fixed timestamp, so the same sources always give the same bytes. Text files are
compared and packed with LF line endings, whatever the checkout uses.
"""
import argparse
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = 'zotero-paper-coach'
ARCHIVE = ROOT / f'{SKILL}.skill'
TEXT = {'.md', '.py', '.txt', '.json'}


def sources():
    out = {}
    for path in sorted((ROOT / SKILL).rglob('*')):
        if not path.is_file() or '__pycache__' in path.parts or path.suffix == '.pyc':
            continue
        data = path.read_bytes()
        if path.suffix in TEXT:
            data = data.replace(b'\r\n', b'\n')
        out[path.relative_to(ROOT).as_posix()] = data
    return out


def packed():
    if not ARCHIVE.exists():
        return {}
    with zipfile.ZipFile(ARCHIVE) as z:
        return {name: z.read(name) for name in z.namelist() if not name.endswith('/')}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()

    want = sources()
    if args.check:
        have = packed()
        stale = sorted(n for n in want.keys() | have.keys() if want.get(n) != have.get(n))
        if stale:
            print(f'{ARCHIVE.name} is out of date; run: python tools/pack_skill.py', file=sys.stderr)
            for name in stale:
                print(f'  {name}', file=sys.stderr)
            sys.exit(1)
        print(f'{ARCHIVE.name} matches {SKILL}/ ({len(want)} files)')
        return

    with zipfile.ZipFile(ARCHIVE, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, data in want.items():
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, data)
    print(f'wrote {ARCHIVE.name} ({len(want)} files)')


if __name__ == '__main__':
    main()
