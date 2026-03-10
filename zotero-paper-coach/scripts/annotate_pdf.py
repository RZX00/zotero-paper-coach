#!/usr/bin/env python3
"""Minimal starter for writing structured highlights and notes to a PDF.

Input spec (JSON file):
[
  {
    "page": 1,
    "phrase": "exact text to search",
    "color": "yellow|blue|pink|green|orange",
    "note": "[主张] ...",
    "limit": 1
  }
]
"""
import argparse
import json
import os
import shutil
import fitz

COLORS = {
    'yellow': (1.0, 0.92, 0.23),
    'blue': (0.45, 0.72, 0.98),
    'pink': (0.97, 0.58, 0.76),
    'green': (0.67, 0.90, 0.60),
    'orange': (1.0, 0.75, 0.33),
}


def save(doc, path):
    try:
        doc.save(path, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
    except Exception:
        tmp = path + '.tmp.pdf'
        doc.save(tmp)
        doc.close()
        os.replace(tmp, path)
        return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pdf')
    ap.add_argument('plan_json')
    ap.add_argument('--backup', action='store_true')
    args = ap.parse_args()

    if args.backup:
        bak = args.pdf + '.bak-openclaw'
        if not os.path.exists(bak):
            shutil.copy2(args.pdf, bak)

    with open(args.plan_json, 'r', encoding='utf-8') as f:
        plan = json.load(f)

    doc = fitz.open(args.pdf)
    added = 0
    for item in plan:
        page = doc[item['page'] - 1]
        phrase = item['phrase']
        color = COLORS.get(item.get('color', 'yellow'), COLORS['yellow'])
        note = item.get('note', '')
        limit = int(item.get('limit', 1))
        rects = page.search_for(phrase)
        count = 0
        for r in rects:
            a = page.add_highlight_annot(r)
            a.set_colors(stroke=color)
            a.set_info(title='OpenClaw Annotator', content=note)
            a.update()
            added += 1
            count += 1
            if note:
                t = page.add_text_annot((r.x1 + 8, r.y0), note)
                t.set_info(title='OpenClaw Annotator', content=note)
                t.update()
                added += 1
            if count >= limit:
                break
    save(doc, args.pdf)
    try:
        doc.close()
    except Exception:
        pass
    print(added)


if __name__ == '__main__':
    main()
