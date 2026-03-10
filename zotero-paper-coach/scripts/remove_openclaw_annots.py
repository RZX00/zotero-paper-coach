#!/usr/bin/env python3
import argparse
import fitz
import os


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pdf')
    ap.add_argument('--title-prefix', default='OpenClaw')
    args = ap.parse_args()

    doc = fitz.open(args.pdf)
    removed = 0
    for page in doc:
        annots = []
        a = page.first_annot
        while a:
            annots.append(a)
            a = a.next
        for a in annots:
            info = a.info or {}
            title = (info.get('title') or '')
            if title.startswith(args.title_prefix):
                page.delete_annot(a)
                removed += 1
    try:
        doc.save(args.pdf, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
    except Exception:
        tmp = args.pdf + '.tmp.pdf'
        doc.save(tmp)
        doc.close()
        os.replace(tmp, args.pdf)
        print(removed)
        return
    doc.close()
    print(removed)


if __name__ == '__main__':
    main()
