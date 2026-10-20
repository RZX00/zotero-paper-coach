#!/usr/bin/env python3
"""Regression tests for phrase matching in scripts/annotate_pdf.py.

Run from the repo root (no test framework needed; pytest also collects it):

    uv run --with pymupdf python tests/test_annotate_matching.py

The fixture PDF is generated at run time. PyMuPDF's bundled 'cjk' font has the
U+FB01/U+FB02 glyphs, so the page text really contains single ligature
characters, like a LaTeX-typeset paper does, and a phrase spelled 'fi'
cannot be found by a plain search. Lines are placed by hand, so the
'prompt-' / 'based' break is a real end-of-line hyphenation.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import fitz

SCRIPT = Path(__file__).resolve().parent.parent / 'zotero-paper-coach' / 'scripts' / 'annotate_pdf.py'

# Page text as typeset: ligature glyphs as single characters, a real
# end-of-line hyphen, and (last two lines) both problems in one sentence.
LINES = [
    'Our method uses task-speci\ufb01c actions in an interleaved manner.',
    'We introduce ReAct, a novel prompt-',
    'based paradigm to synergize reasoning and acting.',
    'It was a signi\ufb01cantly different prompt-',
    'based approach that was \ufb01rst tested in the \ufb02ow.',
]
LINE_Y = [100, 130, 145, 175, 190]


def new_page():
    doc = fitz.open()
    page = doc.new_page()
    page.insert_font(fontname='F0', fontbuffer=fitz.Font('cjk').buffer)
    for text, y in zip(LINES, LINE_Y):
        page.insert_text((72, y), text, fontname='F0', fontsize=11)
    return doc, page


def make_pdf(path):
    doc, _ = new_page()
    doc.save(path)
    doc.close()


def run_plan(phrase, limit=1):
    """Annotate a fresh copy of the fixture; return (count printed, stderr, annots)."""
    with tempfile.TemporaryDirectory() as tmp:
        pdf = Path(tmp) / 'paper.pdf'
        plan = Path(tmp) / 'plan.json'
        make_pdf(pdf)
        plan.write_text(json.dumps([{'page': 1, 'phrase': phrase, 'note': 'n', 'limit': limit}]),
                        encoding='utf-8')
        r = subprocess.run([sys.executable, '-I', str(SCRIPT), str(pdf), str(plan)],
                           capture_output=True, text=True, encoding='utf-8')
        assert r.returncode == 0, r.stderr
        doc = fitz.open(pdf)
        try:
            page = doc[0]  # annotations are only valid while their page object is alive
            highlights = [a for a in page.annots() if a.type[0] == fitz.PDF_ANNOT_HIGHLIGHT]
            quads = [fitz.Quad(a.vertices[i:i + 4]).rect for a in highlights
                     for i in range(0, len(a.vertices), 4)]
        finally:
            doc.close()  # Windows cannot delete the temp dir while the file is open
        return int(r.stdout.strip()), r.stderr, len(highlights), quads


def literal_rects(fragment):
    """Where a fragment sits on the fixture page, found without any of the script's logic."""
    doc, page = new_page()
    flags = fitz.TEXT_PRESERVE_LIGATURES | fitz.TEXT_PRESERVE_WHITESPACE
    rects = page.search_for(fragment, flags=flags)
    doc.close()
    assert rects, f'fixture does not contain {fragment!r}'
    return rects


def assert_quads_match(quads, expected):
    assert len(quads) == len(expected), f'{len(quads)} quads, expected {len(expected)}'
    for got, want in zip(quads, expected):
        for g, w in zip(tuple(got), tuple(want)):
            assert abs(g - w) <= 1.0, f'highlight {tuple(got)} is off the text {tuple(want)}'


def test_plain_phrase_still_matches():
    count, err, n_highlights, quads = run_plan('We introduce ReAct')
    assert (count, n_highlights) == (2, 1), (count, n_highlights, err)  # highlight + note
    assert_quads_match(quads, literal_rects('We introduce ReAct'))


def test_ligature_phrase_written_as_plain_letters():
    count, err, _, quads = run_plan('uses task-specific actions in an interleaved manner')
    assert count == 2, err
    assert_quads_match(quads, literal_rects('uses task-speci\ufb01c actions in an interleaved manner'))


def test_ligature_phrase_written_as_ligature_character():
    count, err, _, _ = run_plan('uses task-speci\ufb01c actions')
    assert count == 2, err


def test_hyphenated_compound_across_line_break():
    # 'prompt-based' as a writer spells it; the page shows 'prompt-' / 'based'.
    count, err, n_highlights, quads = run_plan('a novel prompt-based paradigm to synergize')
    assert (count, n_highlights) == (2, 1), (count, n_highlights, err)
    assert_quads_match(quads, [
        *literal_rects('a novel prompt-'),
        *literal_rects('based paradigm to synergize'),
    ])


def test_other_spellings_of_the_line_break_still_match():
    for phrase in ('a novel prompt- based paradigm',   # whitespace kept after the hyphen
                   'a novel prompt-\nbased paradigm',  # copied straight from extracted text
                   'a novel promptbased paradigm'):    # hyphen dropped
        count, err, _, _ = run_plan(phrase)
        assert count == 2, (phrase, err)


def test_ligature_and_line_break_in_one_phrase():
    count, err, _, quads = run_plan('a significantly different prompt-based approach that was first tested in the flow')
    assert count == 2, err
    assert_quads_match(quads, [
        *literal_rects('a signi\ufb01cantly different prompt-'),
        *literal_rects('based approach that was \ufb01rst tested in the \ufb02ow'),
    ])


def test_text_not_on_page_is_still_reported():
    count, err, n_highlights, _ = run_plan('this sentence is nowhere on the page')
    assert (count, n_highlights) == (0, 0)
    assert '[warn] no match on page 1' in err


if __name__ == '__main__':
    tests = [(name, fn) for name, fn in sorted(globals().items()) if name.startswith('test_')]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f'PASS {name}')
        except AssertionError as e:
            failed += 1
            print(f'FAIL {name}: {e}')
    print(f'{len(tests) - failed}/{len(tests)} passed')
    sys.exit(1 if failed else 0)
