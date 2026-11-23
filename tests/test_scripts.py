#!/usr/bin/env python3
"""Tests for the three PDF scripts beyond phrase matching: plan validation,
occurrence grouping, backups, clean-up and text extraction.

Run from the repo root (no test framework needed; pytest also collects it):

    uv run --with pymupdf python tests/test_scripts.py

Fixture PDFs are generated at run time, except the README demo, which uses the
files under docs/demo/ so the numbers quoted in the README stay true.
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import pymupdf as fitz
except ImportError:
    import fitz

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / 'zotero-paper-coach' / 'scripts'
DEMO = ROOT / 'docs' / 'demo'


def run(script, *args):
    return subprocess.run([sys.executable, '-I', str(SCRIPTS / script), *map(str, args)],
                          capture_output=True, text=True, encoding='utf-8')


def make_pdf(path, pages):
    """pages: one list of (y, text) per page."""
    doc = fitz.open()
    for lines in pages:
        page = doc.new_page()
        for y, text in lines:
            page.insert_text((72, y), text, fontsize=11)
    doc.save(path)
    doc.close()


def annots(path):
    """[(page number, type name, author, vertex count)] for every annotation."""
    doc = fitz.open(path)
    try:
        out = []
        for page in doc:
            for a in page.annots():
                out.append((page.number + 1, a.type[1], a.info.get('title', ''), len(a.vertices or [])))
        return out
    finally:
        doc.close()


def annotate(tmp, pages, plan, *flags):
    pdf, plan_path = Path(tmp) / 'paper.pdf', Path(tmp) / 'plan.json'
    make_pdf(pdf, pages)
    plan_path.write_text(json.dumps(plan), encoding='utf-8')
    return pdf, run('annotate_pdf.py', pdf, plan_path, *flags)


TWO_PAGES = [[(100, 'The first page states the claim.')], [(100, 'The last page states the claim.')]]


def test_page_zero_is_skipped_not_written_to_the_last_page():
    with tempfile.TemporaryDirectory() as tmp:
        pdf, r = annotate(tmp, TWO_PAGES, [{'page': 0, 'phrase': 'states the claim', 'note': 'n'}])
        assert r.returncode == 0, r.stderr
        assert r.stdout.strip() == '0', r.stdout
        assert '[warn] page 0 is not in this PDF (1-2)' in r.stderr, r.stderr
        assert annots(pdf) == []


def test_page_past_the_end_is_skipped_and_the_rest_is_still_written():
    plan = [{'page': 99, 'phrase': 'states the claim'},
            {'page': 2, 'phrase': 'states the claim'}]
    with tempfile.TemporaryDirectory() as tmp:
        pdf, r = annotate(tmp, TWO_PAGES, plan)
        assert r.returncode == 0, r.stderr
        assert r.stdout.strip() == '1', r.stdout
        assert '[warn] page 99 is not in this PDF (1-2)' in r.stderr, r.stderr
        assert 'Traceback' not in r.stderr, r.stderr
        assert [a[0] for a in annots(pdf)] == [2]


def test_plan_object_instead_of_flat_list_is_rejected_before_touching_the_pdf():
    with tempfile.TemporaryDirectory() as tmp:
        pdf, r = annotate(tmp, TWO_PAGES, {'version': '2.0', 'items': []}, '--backup')
        assert r.returncode != 0
        assert '[error] the plan file must be a JSON list' in r.stderr, r.stderr
        assert 'Traceback' not in r.stderr, r.stderr
        assert annots(pdf) == []


# The same word on three consecutive lines: three occurrences, not one wrapped match.
def adjacent(leading):
    return [[(100, 'An anchor is a sentence worth returning to.'),
             (100 + leading, 'Each anchor carries one note.'),
             (100 + 2 * leading, 'No anchor is decorative.')]]


ADJACENT = adjacent(18)


def test_occurrences_on_adjacent_lines_are_separate_highlights():
    # 14 pt leading makes the search rects of neighbouring lines overlap; 18 pt leaves a gap.
    for leading in (14, 18):
        with tempfile.TemporaryDirectory() as tmp:
            pdf, r = annotate(tmp, adjacent(leading), [{'page': 1, 'phrase': 'anchor', 'limit': 3}])
            assert r.returncode == 0, r.stderr
            found = annots(pdf)
            assert r.stdout.strip() == '3' and len(found) == 3, (leading, r.stdout, found)
            assert all(vertices == 4 for *_, vertices in found), (leading, found)  # one line each


def test_limit_one_highlights_only_the_first_of_adjacent_occurrences():
    with tempfile.TemporaryDirectory() as tmp:
        pdf, r = annotate(tmp, ADJACENT, [{'page': 1, 'phrase': 'anchor'}])
        assert r.returncode == 0, r.stderr
        assert [vertices for *_, vertices in annots(pdf)] == [4], annots(pdf)


def test_wrapped_sentence_is_one_highlight_at_any_leading():
    phrase = 'a reading coach should mark only the sentences that carry'
    for leading in (14, 18):
        pages = [[(100, 'We show that a reading coach should mark'),
                  (100 + leading, 'only the sentences that carry the argument.')]]
        with tempfile.TemporaryDirectory() as tmp:
            pdf, r = annotate(tmp, pages, [{'page': 1, 'phrase': phrase}])
            assert r.returncode == 0, r.stderr
            # two lines, one annotation
            assert [vertices for *_, vertices in annots(pdf)] == [8], (leading, annots(pdf))


def test_readme_demo_writes_twelve_annotations_and_keeps_a_backup():
    with tempfile.TemporaryDirectory() as tmp:
        pdf = Path(tmp) / 'demo.pdf'
        shutil.copy(DEMO / 'sample-paper.pdf', pdf)
        r = run('annotate_pdf.py', pdf, DEMO / 'sample-highlights.json', '--backup')
        assert r.returncode == 0, r.stderr
        assert r.stdout.strip() == '12', r.stdout
        assert r.stderr == '', r.stderr  # no unmatched phrase, no import warning
        kinds = [kind for _, kind, _, _ in annots(pdf)]
        assert (kinds.count('Highlight'), kinds.count('Text')) == (6, 6), kinds
        backup = Path(str(pdf) + '.bak-paper-coach')
        assert backup.read_bytes() == (DEMO / 'sample-paper.pdf').read_bytes()


def test_backup_keeps_the_state_before_the_first_run():
    with tempfile.TemporaryDirectory() as tmp:
        pdf, r = annotate(tmp, TWO_PAGES, [{'page': 1, 'phrase': 'states the claim'}], '--backup')
        assert r.returncode == 0, r.stderr
        backup = Path(str(pdf) + '.bak-paper-coach')
        original = backup.read_bytes()
        assert annots(backup) == []
        r = run('annotate_pdf.py', pdf, Path(tmp) / 'plan.json', '--backup')
        assert r.returncode == 0, r.stderr
        assert backup.read_bytes() == original


def make_mixed_pdf(path):
    """One page with a highlight from this skill, one from the pre-2026-10 name, one from the reader."""
    make_pdf(path, [[(100, 'alpha sentence'), (140, 'beta sentence'), (180, 'gamma sentence')]])
    doc = fitz.open(path)
    page = doc[0]
    for word, author in (('alpha', 'Zotero Paper Coach'), ('beta', 'OpenClaw Paper Coach'), ('gamma', 'Reader')):
        a = page.add_highlight_annot(page.search_for(word)[0])
        a.set_info(title=author)
        a.update()
    doc.saveIncr()
    doc.close()


def test_remove_keeps_annotations_made_by_the_reader():
    with tempfile.TemporaryDirectory() as tmp:
        pdf = Path(tmp) / 'paper.pdf'
        make_mixed_pdf(pdf)
        r = run('remove_coach_annots.py', pdf, '--backup')
        assert r.returncode == 0, r.stderr
        assert r.stdout.strip() == '2', r.stdout
        assert [author for _, _, author, _ in annots(pdf)] == ['Reader']
        assert len(annots(str(pdf) + '.bak-paper-coach')) == 3


def test_remove_all_removes_everything():
    with tempfile.TemporaryDirectory() as tmp:
        pdf = Path(tmp) / 'paper.pdf'
        make_mixed_pdf(pdf)
        r = run('remove_coach_annots.py', pdf, '--all')
        assert r.returncode == 0, r.stderr
        assert r.stdout.strip() == '3' and annots(pdf) == []


def test_remove_rejects_an_empty_prefix():
    with tempfile.TemporaryDirectory() as tmp:
        pdf = Path(tmp) / 'paper.pdf'
        make_mixed_pdf(pdf)
        r = run('remove_coach_annots.py', pdf, '--title-prefix', '')
        assert r.returncode != 0 and '[error] empty --title-prefix' in r.stderr, r.stderr
        assert len(annots(pdf)) == 3


def test_extract_writes_one_utf8_entry_per_page():
    with tempfile.TemporaryDirectory() as tmp:
        pdf, out = Path(tmp) / 'paper.pdf', Path(tmp) / 'outline.json'
        make_pdf(pdf, TWO_PAGES)
        r = run('extract_pdf_outline.py', pdf, '-o', out)
        assert r.returncode == 0, r.stderr
        pages = json.loads(out.read_text(encoding='utf-8'))
        assert [p['page'] for p in pages] == [1, 2]
        assert 'first page' in pages[0]['text'] and 'last page' in pages[1]['text']


def test_scripts_import_without_a_deprecation_warning():
    with tempfile.TemporaryDirectory() as tmp:
        pdf = Path(tmp) / 'paper.pdf'
        make_pdf(pdf, TWO_PAGES)
        for script, args in (('extract_pdf_outline.py', [pdf, '-o', Path(tmp) / 'o.json']),
                             ('remove_coach_annots.py', [pdf])):
            r = run(script, *args)
            assert r.returncode == 0 and r.stderr == '', (script, r.stderr)


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
