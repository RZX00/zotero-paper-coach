#!/usr/bin/env python3
"""Remove annotations written by this skill from a PDF.

By default only annotations whose author name starts with one of DEFAULT_PREFIXES
are removed, so the user's own annotations stay. --all removes every annotation
(the `wipe-all` rewrite mode) and should only run after the user confirms.
"""
import argparse
import os
import shutil
import sys

import fitz

# 'OpenClaw' is the author name used by versions before 2026-10; keep it so old runs
# can still be cleaned up.
DEFAULT_PREFIXES = ['Zotero Paper Coach', 'OpenClaw']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pdf')
    ap.add_argument('--title-prefix', action='append',
                    help='Author-name prefix to remove; repeatable. Defaults to this skill and its legacy name.')
    ap.add_argument('--all', action='store_true', help='Remove every annotation, including the user\'s own')
    ap.add_argument('--backup', action='store_true',
                    help='Copy the original to <pdf>.bak-paper-coach first (only if that backup does not exist yet)')
    args = ap.parse_args()

    prefixes = tuple(args.title_prefix or DEFAULT_PREFIXES)
    # An empty prefix would match every author and silently become --all.
    if not args.all and any(not p for p in prefixes):
        sys.exit('[error] empty --title-prefix would remove every annotation; use --all if that is intended')

    if args.backup:
        bak = args.pdf + '.bak-paper-coach'
        if not os.path.exists(bak):
            shutil.copy2(args.pdf, bak)

    doc = fitz.open(args.pdf)
    removed = 0
    for page in doc:
        for a in list(page.annots()):
            title = (a.info or {}).get('title') or ''
            if args.all or title.startswith(prefixes):
                page.delete_annot(a)
                removed += 1
    try:
        doc.save(args.pdf, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
        doc.close()
    except Exception:
        tmp = args.pdf + '.tmp.pdf'
        doc.save(tmp)
        doc.close()
        try:
            os.replace(tmp, args.pdf)
        except PermissionError:
            # Windows readers often lock the open PDF; leave the original untouched.
            os.remove(tmp)
            sys.exit(f'[error] {args.pdf} is locked by another program. Close it in your PDF reader or Zotero, then run again.')
    print(removed)


if __name__ == '__main__':
    main()
