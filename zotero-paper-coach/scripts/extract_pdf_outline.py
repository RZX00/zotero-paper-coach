#!/usr/bin/env python3
import argparse
import fitz
import json


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pdf')
    args = ap.parse_args()

    doc = fitz.open(args.pdf)
    out = []
    for i, page in enumerate(doc):
        text = page.get_text('text')
        out.append({
            'page': i + 1,
            'text': text[:12000]
        })
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
