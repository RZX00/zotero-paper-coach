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
- If PyMuPDF's own search finds nothing, a second matcher compares NFKC-folded
  text on both sides, so 'fi' matches a typeset 'ﬁ' ligature, and treats a hyphen
  as optional, so 'prompt-based' matches 'prompt-' + line break + 'based'.
- Multi-line matches are grouped and written as a single highlight annotation
  where possible, instead of one annotation per line fragment.
"""
import argparse
import json
import os
import re
import shutil
import sys
import unicodedata
import fitz

# Author name stamped on every annotation; remove_coach_annots.py uses it to clean up
# only what this skill wrote.
AUTHOR = 'Zotero Paper Coach'

COLORS = {
    'yellow': (1.0, 0.92, 0.23),
    'blue': (0.45, 0.72, 0.98),
    'pink': (0.97, 0.58, 0.76),
    'green': (0.67, 0.90, 0.60),
    'orange': (1.0, 0.75, 0.33),
}


def normalize_phrase(text):
    return ' '.join((text or '').split())


def dehyphenate(text):
    # Extracted text keeps end-of-line hyphenation ('gener-\nalization'), while
    # PyMuPDF's search matches the joined word ('generalization').
    return re.sub(r'(\w)-\s+(\w)', r'\1\2', text)


def fold(text):
    # NFKC turns ligature characters (ﬁ ﬂ ﬀ ﬃ ﬄ) and no-break spaces into plain
    # letters and spaces; the soft hyphen and U+2010/2011 are not letters, so map
    # them to '-' by hand.
    return re.sub('[\u00ad\u2010\u2011]', '-', unicodedata.normalize('NFKC', text))


def page_lines(page):
    """Text lines of the page as lists of (char, rect), in reading order."""
    lines = []
    for block in page.get_text('rawdict')['blocks']:
        if block['type'] != 0:
            continue
        for line in block['lines']:
            chars = [(c['c'], fitz.Rect(c['bbox'])) for span in line['spans'] for c in span['chars']]
            if chars:
                lines.append(chars)
    return lines


def folded_stream(lines):
    """Fold the page text into one string, remembering which glyph each character came from.

    A hyphen that ends a line and sits between two alphanumerics is dropped, like
    PyMuPDF's own dehyphenation, so 'prompt-' + 'based' reads 'promptbased'.
    owner[i] is the (line, char) index of the glyph behind text[i], or None for the
    space inserted between lines.
    """
    text, owner = [], []
    for n, chars in enumerate(lines):
        last = max((i for i, (c, _) in enumerate(chars) if c.strip()), default=-1)
        following = next((c for c, _ in lines[n + 1] if c.strip()), '') if n + 1 < len(lines) else ''
        joins = (last > 0 and fold(chars[last][0]) == '-' and chars[last - 1][0].isalnum()
                 and following.isalnum())
        for i, (c, _) in enumerate(chars):
            if joins and i >= last:
                break
            for ch in fold(c):
                text.append(ch)
                owner.append((n, i))
        if not joins:
            text.append(' ')
            owner.append(None)
    return ''.join(text), owner


def phrase_regex(phrase):
    """Regex for a phrase against the folded page text: a hyphen is optional, and the
    whitespace after it too (a line-end hyphen leaves no space behind)."""
    parts, after_hyphen = [], False
    for ch in ' '.join(fold(phrase).split()):
        if ch == ' ':
            parts.append(r'\s*' if after_hyphen else r'\s+')
        elif ch == '-':
            parts.append('-?')
        else:
            parts.append(re.escape(ch))
        after_hyphen = ch == '-'
    return ''.join(parts)


def find_folded_matches(page, phrase):
    """Occurrences of phrase in the page text ignoring ligatures and line-end hyphenation.

    Returns the same shape as group_wrapped_hits: one list of rects per occurrence,
    one rect per line it spans.
    """
    pattern = phrase_regex(phrase)
    if not pattern:
        return []
    lines = page_lines(page)
    text, owner = folded_stream(lines)
    groups = []
    for m in re.finditer(pattern, text, re.IGNORECASE):
        glyphs = [owner[i] for i in range(m.start(), m.end()) if owner[i]]
        if not glyphs:
            continue
        (first_line, first_char), (last_line, last_char) = glyphs[0], glyphs[-1]
        rects = []
        for n in range(first_line, last_line + 1):
            start = first_char if n == first_line else 0
            end = last_char if n == last_line else len(lines[n]) - 1
            boxes = [r for c, r in lines[n][start:end + 1] if c.strip()]
            if boxes:
                rects.append(union_rect(boxes))
        groups.append(rects)
    return groups


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
        try:
            os.replace(tmp, path)
        except PermissionError:
            # Windows readers often lock the open PDF; leave the original untouched.
            os.remove(tmp)
            sys.exit(f'[error] {path} is locked by another program. Close it in your PDF reader or Zotero, then run again.')
        return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pdf')
    ap.add_argument('plan_json')
    ap.add_argument('--backup', action='store_true')
    args = ap.parse_args()

    if args.backup:
        # Shared with remove_coach_annots.py: only the first run creates it, so it
        # always holds the PDF as it was before this skill touched it.
        bak = args.pdf + '.bak-paper-coach'
        if not os.path.exists(bak):
            shutil.copy2(args.pdf, bak)

    # utf-8-sig: PowerShell 5.1 writes a BOM with -Encoding utf8
    with open(args.plan_json, 'r', encoding='utf-8-sig') as f:
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
        if not groups and dehyphenate(phrase) != phrase:
            hits = page.search_for(dehyphenate(phrase), quads=True)
            groups = group_wrapped_hits(hits)
        if not groups:
            groups = find_folded_matches(page, phrase)
        if not groups:
            print(f"[warn] no match on page {item['page']} for phrase: {raw_phrase[:80]!r}", file=sys.stderr)
            continue

        count = 0
        for group in groups:
            annot_target = group[0] if len(group) == 1 else group
            a = page.add_highlight_annot(annot_target)
            a.set_colors(stroke=color)
            a.set_info(title=AUTHOR, content=note)
            a.update()
            added += 1
            count += 1
            if note:
                anchor = union_rect(group)
                t = page.add_text_annot((anchor.x1 + 8, anchor.y0), note)
                t.set_info(title=AUTHOR, content=note)
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
