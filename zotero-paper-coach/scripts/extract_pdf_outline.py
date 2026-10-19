#!/usr/bin/env python3
import argparse
import fitz
import json
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pdf')
    ap.add_argument('-o', '--output', help='Write JSON to this file (UTF-8) instead of stdout')
    args = ap.parse_args()

    doc = fitz.open(args.pdf)
    out = []
    for i, page in enumerate(doc):
        text = page.get_text('text')
        out.append({
            'page': i + 1,
            'text': text[:12000]
        })
    text = json.dumps(out, ensure_ascii=False, indent=2)
    if args.output:
        # Writing the file ourselves avoids shell redirection re-encoding the text
        # (Windows PowerShell 5.1 turns `>` output into UTF-16 and mangles CJK).
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(text + '\n')
    else:
        sys.stdout.reconfigure(encoding='utf-8')
        print(text)


if __name__ == '__main__':
    main()
