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

Implementation note:
- Phrase matching normalizes whitespace so extracted text containing newlines can
  still match wrapped PDF text.
- Multi-line matches are grouped and written as a single highlight annotation
  where possible, instead of one annotation per line fragment.
"""
import argparse
import json
import os
import shutil
import sys
import fitz

COLORS = {
    'yellow': (1.0, 0.92, 0.23),
    'blue': (0.45, 0.72, 0.98),
    'pink': (0.97, 0.58, 0.76),
    'green': (0.67, 0.90, 0.60),
    'orange': (1.0, 0.75, 0.33),
}


def normalize_phrase(text):
    return ' '.join((text or '').split())


def rect_of(hit):
    return hit.rect if hasattr(hit, 'rect') else hit


def union_rect(hits):
    rects = [rect_of(hit) for hit in hits]
    out = fitz.Rect(rects[0])
    for rect in rects[1:]:
        out.include_rect(rect)
    return out


def group_wrapped_hits(hits):
    """Group consecutive search hits that belong to one wrapped multi-line match.

    PyMuPDF returns one rect/quad per line fragment for wrapped matches. We merge
    nearby vertical fragments into a single logical occurrence so one highlight
    can span multiple lines.
    """
    if not hits:
        return []

    groups = [[hits[0]]]
    prev_rect = rect_of(hits[0])
    for hit in hits[1:]:
        rect = rect_of(hit)
        prev_h = max(prev_rect.height, 1)
        curr_h = max(rect.height, 1)
        same_line = abs(rect.y0 - prev_rect.y0) <= max(prev_h, curr_h) * 0.25
        vertical_gap = rect.y0 - prev_rect.y1
        wrapped_next_line = (not same_line) and 0 <= vertical_gap <= max(prev_h, curr_h) * 1.5

        if wrapped_next_line:
            groups[-1].append(hit)
        else:
            groups.append([hit])
        prev_rect = rect
    return groups


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
        raw_phrase = item['phrase']
        phrase = normalize_phrase(raw_phrase)
        color = COLORS.get(item.get('color', 'yellow'), COLORS['yellow'])
        note = item.get('note', '')
        limit = int(item.get('limit', 1))
        hits = page.search_for(phrase, quads=True)
        groups = group_wrapped_hits(hits)
        if not groups and raw_phrase != phrase:
            hits = page.search_for(raw_phrase, quads=True)
            groups = group_wrapped_hits(hits)
        if not groups:
            print(f"[warn] no match on page {item['page']} for phrase: {raw_phrase[:80]!r}", file=sys.stderr)
            continue

        count = 0
        for group in groups:
            annot_target = group[0] if len(group) == 1 else group
            a = page.add_highlight_annot(annot_target)
            a.set_colors(stroke=color)
            a.set_info(title='OpenClaw Annotator', content=note)
            a.update()
            added += 1
            count += 1
            if note:
                anchor = union_rect(group)
                t = page.add_text_annot((anchor.x1 + 8, anchor.y0), note)
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
