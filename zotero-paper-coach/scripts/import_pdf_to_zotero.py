#!/usr/bin/env python3
"""Import a local PDF into the running Zotero desktop app via the connector API.

Why this exists:
- `open -a Zotero file.pdf` is not a reliable import path on macOS
- Zotero's local connector on 127.0.0.1:23119 is the stable desktop import route
- Local API may be disabled and zotero.sqlite may be locked, so we resolve the imported
  attachment by inspecting the newest matching file under ~/Zotero/storage

Usage:
  python3 import_pdf_to_zotero.py /path/to/file.pdf --title "My Test PDF" --open
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from typing import Optional

CONNECTOR_BASE = "http://127.0.0.1:23119"


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def ping_connector(timeout: float = 2.0) -> None:
    req = urllib.request.Request(CONNECTOR_BASE + '/connector/ping', method='GET')
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode('utf-8', 'replace')
        if resp.status != 200 or 'Zotero is running' not in body:
            raise RuntimeError('Zotero connector ping failed')


def get_selected_collection(timeout: float = 3.0) -> dict:
    req = urllib.request.Request(
        CONNECTOR_BASE + '/connector/getSelectedCollection',
        method='POST',
        data=b'{}',
        headers={'Content-Type': 'application/json'},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode('utf-8', 'replace'))


def import_pdf(pdf_path: pathlib.Path, title: str, timeout: float = 120.0) -> dict:
    session_id = 'openclaw-' + uuid.uuid4().hex
    meta = {
        'sessionID': session_id,
        'url': pdf_path.as_uri(),
        'title': title,
    }
    data = pdf_path.read_bytes()
    req = urllib.request.Request(
        CONNECTOR_BASE + '/connector/saveStandaloneAttachment',
        method='POST',
        data=data,
        headers={
            'Content-Type': 'application/pdf',
            'X-Zotero-Connector-API-Version': '3',
            'X-Metadata': json.dumps(meta, ensure_ascii=False),
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode('utf-8', 'replace')
        parsed = json.loads(body or '{}')
        return {
            'status': resp.status,
            'sessionID': session_id,
            'response': parsed,
        }


def find_imported_attachment_key(source_pdf: pathlib.Path, since_ts: float, window_seconds: float = 180.0) -> Optional[str]:
    storage_root = pathlib.Path.home() / 'Zotero' / 'storage'
    if not storage_root.exists():
        return None

    source_size = source_pdf.stat().st_size
    source_hash = sha256_file(source_pdf)
    candidates = []
    cutoff = since_ts - 5
    now = time.time()

    for pdf in storage_root.glob('*/*.pdf'):
        try:
            st = pdf.stat()
        except FileNotFoundError:
            continue
        if st.st_mtime < cutoff or (now - st.st_mtime) > window_seconds:
            continue
        if st.st_size != source_size:
            continue
        candidates.append((st.st_mtime, pdf))

    candidates.sort(reverse=True)

    for _, pdf in candidates:
        try:
            if sha256_file(pdf) == source_hash:
                return pdf.parent.name
        except Exception:
            continue

    if candidates:
        return candidates[0][1].parent.name
    return None


def open_in_zotero(item_key: str) -> None:
    uri = f'zotero://open-pdf/library/items/{item_key}'
    subprocess.run(['open', uri], check=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('pdf')
    ap.add_argument('--title', help='Attachment title to show in Zotero')
    ap.add_argument('--open', action='store_true', help='Open the imported PDF in Zotero after import')
    ap.add_argument('--json', action='store_true', help='Print machine-readable JSON result')
    args = ap.parse_args()

    pdf_path = pathlib.Path(args.pdf).expanduser().resolve()
    if not pdf_path.exists():
        print(f'PDF not found: {pdf_path}', file=sys.stderr)
        return 2
    if pdf_path.suffix.lower() != '.pdf':
        print(f'Not a PDF: {pdf_path}', file=sys.stderr)
        return 2

    title = args.title or pdf_path.stem
    started = time.time()

    try:
        ping_connector()
        target = get_selected_collection()
        imported = import_pdf(pdf_path, title)
        time.sleep(1.2)
        item_key = find_imported_attachment_key(pdf_path, started)
        result = {
            'ok': True,
            'pdf': str(pdf_path),
            'title': title,
            'libraryName': target.get('libraryName'),
            'targetName': target.get('name'),
            'import': imported,
            'attachmentKey': item_key,
        }
        if args.open and item_key:
            open_in_zotero(item_key)
            result['opened'] = True
        elif args.open:
            result['opened'] = False
            result['warning'] = 'Imported, but failed to resolve attachment key for immediate open'
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', 'replace')
        result = {
            'ok': False,
            'status': e.code,
            'error': body,
        }
    except Exception as e:
        result = {
            'ok': False,
            'error': str(e),
        }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if result.get('ok'):
            print(f"Imported into Zotero: {result.get('title')}")
            print(f"Library/Target: {result.get('libraryName')} / {result.get('targetName')}")
            if result.get('attachmentKey'):
                print(f"Attachment key: {result['attachmentKey']}")
                print(f"Open URI: zotero://open-pdf/library/items/{result['attachmentKey']}")
            if result.get('warning'):
                print(f"Warning: {result['warning']}")
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2), file=sys.stderr)
            return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
