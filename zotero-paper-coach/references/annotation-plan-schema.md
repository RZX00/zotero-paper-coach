# Annotation plan schema

The annotation plan is the canonical intermediate representation.

Do not annotate the PDF before the plan exists.

## Why it exists

The plan gives us:

- explainability
- dry-run preview
- reproducibility
- safer retries
- future UI review
- sidecar generation without reparsing decisions

## Recommended files

- `paper.annotation-plan.md` for human review
- `paper.annotation-plan.json` for machine use

## JSON shape

```json
{
  "version": "2.0",
  "created_at": "2026-03-10T10:30:00+08:00",
  "backend_mode": "pdf-writeback",
  "document_profile": {
    "source_type": "zotero-attachment",
    "source_path": "/path/to/paper.pdf",
    "zotero_item_key": "OPTIONAL",
    "zotero_attachment_path": "/path/to/paper.pdf",
    "extraction_confidence": "high",
    "has_ocr": false,
    "page_count": 18,
    "paper_type": "empirical",
    "structure_map": [
      {"section": "Abstract", "pages": [1]},
      {"section": "Introduction", "pages": [1, 2, 3]},
      {"section": "Methods", "pages": [4, 5, 6]}
    ]
  },
  "user_profile": {
    "goal": "beginner-learning",
    "style": "mentor",
    "density": "medium",
    "note_depth": "explain",
    "color_scheme": "standard",
    "rewrite_mode": "clean-openclaw-only",
    "language": "zh-CN"
  },
  "section_priorities": [
    {"section": "Abstract", "priority": "high", "why": "fast framing"},
    {"section": "Results", "priority": "high", "why": "core evidence"},
    {"section": "Methods", "priority": "medium", "why": "only anchor essentials"}
  ],
  "items": [
    {
      "item_id": "a1",
      "page": 2,
      "section": "Introduction",
      "anchor_text": "We address the problem of...",
      "anchor_strategy": "exact-text",
      "color": "yellow",
      "note_label": "[主张]",
      "note_depth": "explain",
      "note_content": "这是全文要你接受的核心判断。",
      "rationale": "frames the paper's thesis",
      "confidence": "high",
      "include_in_reading_guide": true,
      "tags": ["claim", "must-read"]
    }
  ],
  "guide_promotions": [
    "a1"
  ],
  "fallback_notes": []
}
```

## Field guidance

### backend_mode

Allowed values:

- `pdf-writeback`
- `zotero-native`
- `guide-only`

### extraction_confidence

Allowed values:

- `high`
- `medium`
- `low`

### anchor_strategy

Allowed values:

- `exact-text`
- `normalized-text`
- `paragraph-anchor`
- `page-region`
- `manual-placeholder`

Prefer the weakest reliable strategy rather than pretending precision.

### confidence per item

An item may have lower confidence than the whole document.
This matters for fragile phrase matching.

## Human-readable markdown shape

Suggested sections:

1. Run summary
2. Document profile
3. User profile
4. Extraction confidence
5. Section priorities
6. Planned annotations table or bullets
7. Downgrades and warnings
8. Reading guide promotions

## Rendering rules

- only `items` should drive PDF mutation
- `guide_promotions` should drive reading-guide assembly
- if confidence is low, prefer generating the plan even when PDF write-back is skipped

## Non-goals

The schema does not need to represent every PDF geometry detail in v2.
Start with reliable anchorable text and evolve later.
