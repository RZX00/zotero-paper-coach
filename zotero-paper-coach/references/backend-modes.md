# Backend modes

Use this file to decide what kind of write target we truly have.

## Principle

Be product-honest.
Do not imply native Zotero annotation support when only the PDF file was edited.

## Modes

### pdf-writeback

Use when:

- a writable PDF file exists locally
- the file is either standalone or a Zotero-managed attachment PDF
- text extraction is good enough for reliable anchoring

Behavior:

- back up the PDF first
- optionally clean prior OpenClaw annotations
- write highlights and notes into the PDF
- optionally emit reading guide and annotation plan sidecars

User-facing wording:

- "我改的是本地 PDF 附件本体，不是假装写进 Zotero 原生注释数据库。"

### zotero-native

Use only when:

- an actual implemented local bridge or plugin exists
- the tool can prove it is writing native Zotero annotation entities

Behavior:

- integrate with the Zotero annotation ecosystem directly
- preserve accurate provenance

User-facing wording:

- only claim this mode when it is real

### guide-only

Use when:

- extraction confidence is too low for safe precise write-back
- the file is protected or not writable
- the attachment path cannot be resolved
- dependencies are missing and installation was not approved

Behavior:

- generate `paper.reading-guide.md`
- generate annotation plan sidecars
- explain why write-back was skipped or downgraded

## Confidence matrix

### high confidence

Recommended mode:

- pdf-writeback

Signals:

- clean text extraction
- stable phrase search
- sensible section structure

### medium confidence

Recommended mode:

- pdf-writeback with reduced precision

Signals:

- partial extraction issues
- line-wrap or ligature fragility
- some section ambiguity

Precautions:

- use fewer, broader anchors
- prefer paragraph-level selection
- reduce note count if anchoring is fragile

### low confidence

Recommended mode:

- guide-only by default

Signals:

- scanned pages
- OCR garbage
- repeated search misses
- broken text order

Precautions:

- warn clearly
- ask before any best-effort PDF mutation

## Zotero-specific note

For v2, the practical default should be:

- resolve the Zotero local attachment path
- edit that PDF file directly
- let Zotero surface the result by reopening the attachment

That is a good product path. It just is not the same thing as native DB annotation creation.
