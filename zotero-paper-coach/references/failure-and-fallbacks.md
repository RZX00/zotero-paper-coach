# Failure and fallbacks

This skill should fail honestly, not magically.

## Failure classes

### 1. Missing dependency

Examples:

- `pymupdf` not installed
- Python environment unavailable

Response:

- explain what is missing
- ask before installing anything
- offer `guide-only` if possible

### 2. Attachment not resolved

Examples:

- multiple Zotero candidates
- no confirmed local PDF path
- broken Zotero storage reference

Response:

- ask the user to confirm the exact paper or file
- do not guess and mutate the wrong PDF

### 3. Low extraction confidence

Examples:

- scanned PDF
- OCR text is broken
- phrase search fails repeatedly

Response:

- classify confidence as low
- prefer reading guide + annotation plan
- only run best-effort write-back if the user explicitly wants it

### 4. Partial anchor fragility

Examples:

- ligatures break exact text search
- line wrapping changes extraction
- tables and formulas are not text-search friendly

Response:

- downgrade from exact phrase matches to paragraph anchors
- reduce highlight count
- note the approximation in the result summary

### 5. Protected or corrupted PDF

Examples:

- save fails
- file permissions block mutation
- incremental save breaks

Response:

- preserve the original
- report the error clearly
- offer sidecar outputs

### 6. Cleanup ambiguity

Examples:

- user wants a fresh run but has existing personal annotations
- prior OpenClaw annotations are missing reliable metadata

Response:

- default to `clean-openclaw-only`
- never wipe user annotations unless explicitly told to `wipe-all`
- prefer conservative cleanup when metadata is incomplete

## Fallback ladder

Preferred downgrade path:

1. high-confidence PDF write-back
2. medium-confidence PDF write-back with broader anchors
3. guide-only with annotation plan
4. inspection-only dry run

Do not jump straight from perfect hopes to silent failure.

## Mandatory user-facing disclosures

When a downgrade happens, say:

- what failed or became uncertain
- what backend was actually used
- whether the PDF was modified
- what alternative artifact was produced

## Anti-bullshit rules

Do not say:

- "annotated successfully" when only a plan was created
- "Zotero-native" when only the PDF file changed
- "high precision" when anchors were approximate

## Good downgrade example

- "这篇 PDF 文本抽取置信度低，精确写回风险大。我先给你生成 reading guide 和 annotation plan；如果你愿意赌一个 best-effort 版本，我再往 PDF 里写。"
