# Zotero Paper Coach v2 Design

## Positioning

This skill should behave like a paper reading coach with PDF write-back, not like a blind auto-highlighter.

The product promise is:

- help the reader understand the paper faster
- preserve a stable annotation language
- write useful highlights and notes back into the PDF when confidence is high enough
- generate sidecar guidance when PDF write-back alone cannot carry enough value

## Product thesis

The unit of intelligence is not the highlight. It is the annotation plan.

A good run should answer:

1. what this reader is trying to do
2. what parts of the paper matter for that goal
3. what should be highlighted
4. why each highlight exists
5. whether a note is needed
6. whether the document is reliable enough for precise write-back

## Scope

### In scope

- annotate standalone PDFs
- annotate Zotero-managed local PDF attachments
- remove only prior OpenClaw-created annotations by default
- generate a reading guide markdown sidecar
- generate an annotation plan markdown or JSON sidecar
- expose confidence and fallback mode clearly to the user

### Out of scope for v2

- pretending to write Zotero-native database annotations when only PDF attachment write-back exists
- perfect annotation on poor OCR scans
- full bibliography graph analysis
- autonomous paper selection from a Zotero library without a clearly identified target paper

## Users and jobs

The skill should optimize for user jobs, not one universal annotation style.

Primary jobs:

- beginner-learning
- quick-read
- exam-prep
- literature-review
- replication
- citation-harvest

Cross-cutting style overlays:

- mentor
- top-student
- critical-researcher
- executive-brief

These are not cosmetic presets. They change section priority, note density, and note voice.

## Core workflow

### 1. Resolve target

Determine whether the input is:

- a standalone PDF path
- a Zotero local attachment PDF
- a document with uncertain or unresolved attachment location

If multiple candidate files exist, ask before writing.

### 2. Inspect document

Extract enough structure to identify:

- title
- abstract
- section outline
- research question or gap
- method anchors
- result anchors
- limitation anchors
- conclusion anchors

Also classify extraction confidence:

- high
- medium
- low

### 3. Build annotation plan

The plan is the internal source of truth. Writing to the PDF is a downstream rendering step.

Minimum plan fields:

- document metadata
- user profile
- extraction confidence
- section priorities
- passage anchors
- target pages
- annotation type
- color
- note label
- note content
- rationale
- confidence
- inclusion in reading guide or not

### 4. Render outputs

Possible outputs:

- annotated PDF
- `paper.annotation-plan.md`
- `paper.annotation-plan.json`
- `paper.reading-guide.md`

### 5. Report result honestly

Every run should say which backend was used, how confident extraction was, and whether any downgrade happened.

## Design principles

### 1. Goal first, marking second

Do not start highlighting before the paper has been converted into a goal-aware plan.

### 2. Stable semantics beat colorful chaos

Color should encode stable semantic roles. Importance should be expressed mostly by selection pressure, note strength, and reading-guide promotion.

### 3. Density is a product control, not a vague adjective

Each density mode should have hard behavioral rules.

### 4. Every paper needs boundary information

At minimum, a complete useful run should try to preserve:

- one core claim
- one key evidence anchor
- one limitation or caveat
- one reusable conclusion-level sentence

### 5. Sidecars are first-class outputs

A reading guide is not a debug artifact. It is part of the teaching product.

## Semantic system

### Color = semantic category

Default standard scheme:

- yellow: claim or takeaway
- blue: evidence, method, metric, setup
- pink: limitation, risk, uncertainty, failure mode
- green: definition, orientation, beginner-friendly framing
- orange: quotable or reusable synthesis line

### Importance = rendered intensity

Importance should be reflected through:

- whether a passage is selected at all
- whether a note is attached
- how deep the note is: brief, explain, teach
- whether it appears in the reading guide

Avoid multiplying colors just to simulate importance.

## User interaction model

Keep the questioning short.

### Step A: ask one main intent question when missing

What are you trying to do with this paper?

Suggested intent options:

- 入门理解
- 快速抓重点
- 考试/课程
- 文献综述
- 复现实验
- 提取可引用观点

### Step B: ask the two most valuable modifiers when missing

- density: 轻 / 中 / 重 / 教学模式
- style: 导师 / 学霸 / 批判型研究员 / 极简摘要官

### Step C: default the rest

Use defaults unless the user asks for precision control:

- note depth: explain
- color scheme: standard
- rewrite mode: clean-openclaw-only

## Output design

### Annotated PDF

This is the primary artifact when write-back confidence is high enough.

### Reading guide

The reading guide should contain:

- one-sentence summary
- three-sentence summary
- research question
- why the paper matters
- core findings
- evidence chain
- limitations
- recommended reading order
- likely beginner confusions
- suggested oral explanation prompt

### Annotation plan

The plan should exist in both human-readable and machine-readable forms when possible.

Human-readable version is for trust and review.
Machine-readable version is for reproducibility and future UI.

## Data model

### UserProfile

- goal
- style
- density
- note_depth
- color_scheme
- rewrite_mode
- language

### DocumentProfile

- source_type
- source_path
- zotero_item_key optional
- zotero_attachment_path optional
- extraction_confidence
- structure_map
- paper_type optional
- has_ocr
- page_count

### AnnotationPlan

- version
- created_at
- backend_mode
- document_profile
- user_profile
- section_priorities
- items
- guide_promotions
- fallback_notes

### AnnotationPlanItem

- item_id
- page
- section
- anchor_text
- anchor_strategy
- color
- note_label
- note_depth
- note_content
- rationale
- confidence
- include_in_reading_guide
- tags

## Backend modes

### Backend A: pdf-writeback

Use when a writable PDF file is available.

Strengths:

- immediate visible result in the attachment
- aligns with Zotero PDF reading workflow
- easiest stable v2 path

Weaknesses:

- not the same as native Zotero DB annotations
- depends on extractable text and page anchoring quality

### Backend B: zotero-native

Future-facing only unless a local bridge or plugin exists.

Strengths:

- closer to Zotero's native annotation ecosystem
- could integrate more directly with notes and library metadata

Weaknesses:

- should not be claimed without real implementation

## Confidence and downgrade policy

### High confidence

- text extraction is reliable
- anchor search is precise
- write annotated PDF
- generate sidecars if requested or teaching mode is active

### Medium confidence

- extraction is partially reliable
- prefer paragraph anchors over fragile micro-targets
- reduce highlight count
- explicitly warn that some anchors may be approximate

### Low confidence

- scan or OCR quality is poor
- do not promise precise write-back
- prefer reading guide and plan outputs
- only write back if the user explicitly accepts a best-effort run

## Rewrite policy

Support these modes:

- append
- clean-openclaw-only
- wipe-all

Default must remain `clean-openclaw-only`.

OpenClaw-authored annotations should be identifiable by metadata, not only title text.

Recommended metadata fields:

- producer: openclaw.zotero-paper-coach
- skill_version
- run_id
- rewrite_mode
- goal
- style
- density

## Failure modes

Must handle and explain:

- missing PDF dependency
- unresolved Zotero attachment path
- scanned PDF with low extraction confidence
- phrase search misses because of ligatures or line wrapping
- protected or corrupted PDF
- backup failure
- partial write success

## v2 implementation priorities

1. formalize annotation plan schema
2. generate reading guide as a first-class output
3. strengthen OpenClaw annotation metadata for safe cleanup
4. add Zotero attachment locator workflow
5. add confidence-aware degradation behavior

## UX standard

Do not oversell automation.

Good message:

- says whether we edited the PDF attachment directly
- says whether confidence was high, medium, or low
- says whether a sidecar guide was generated
- says what defaults were assumed

Bad message:

- implies native Zotero integration when we only edited the PDF file
- hides low-confidence extraction
- acts like more highlights always means better support

## Future hooks

This design should support later additions without redesign:

- dry-run plan preview
- UI review and approval of plan items
- note-language switching
- Zotero local SQLite lookup
- OCR assist for scans
- export of notes into Zotero notes or external study systems
