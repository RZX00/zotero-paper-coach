---
name: zotero-paper-coach
description: Annotate academic papers and Zotero-managed PDF attachments with structured, high-value highlights and mentor-style notes. Use when a user wants paper pre-highlighting, reading guidance, layered annotation styles, note density control, color-coded importance, Zotero/PDF write-back, or a reusable workflow for studying, literature review, exam prep, or paper comprehension.
---

# Zotero Paper Coach

Provide paper annotation as a reading-coach workflow, not as raw highlighting.

## Quick start

When invoked, do this in order:

1. Identify the target document and whether the write target is:
   - a Zotero local PDF attachment, or
   - a standalone PDF.
2. Ask for the minimum annotation configuration if the user did not specify it.
3. Produce an internal annotation plan before writing anything.
4. Back up the PDF.
5. Remove only prior annotations created by this skill unless the user explicitly asks to wipe all annotations.
6. Write highlights and notes back to the PDF.
7. Optionally generate a sidecar reading guide markdown file.

## Minimum configuration to collect

Ask only for missing items. Default aggressively when the user is vague.

Collect these knobs:

- **goal**: `beginner-learning` | `quick-read` | `exam-prep` | `literature-review` | `replication` | `citation-harvest`
- **style**: `mentor` | `top-student` | `critical-researcher` | `executive-brief`
- **density**: `light` | `medium` | `heavy` | `teaching`
- **note depth**: `brief` | `explain` | `teach`
- **color scheme**: `standard` | `minimal` | `research`
- **rewrite mode**: `clean-openclaw-only` | `append` | `wipe-all`

Recommended defaults:

- goal: `beginner-learning`
- style: `mentor`
- density: `medium`
- note depth: `explain`
- color scheme: `standard`
- rewrite mode: `clean-openclaw-only`

## Annotation semantics

Use stable color meaning. Do not improvise colors per run.

Read `/Users/apple/.openclaw/workspace/skills/zotero-paper-coach/references/annotation-styles.md` when deciding style, density, and color policy.
Read `/Users/apple/.openclaw/workspace/skills/zotero-paper-coach/references/user-modes.md` when mapping the user's actual job to annotation behavior.

### Standard color scheme

- **Yellow**: core claim, must-read result, takeaway sentence
- **Blue**: evidence, method, metric, experimental setup
- **Pink**: limitation, caveat, failure mode, uncertainty
- **Green**: definition, orientation sentence, beginner-friendly framing
- **Orange**: quotable sentence, reusable summary, literature-review worthy line

## Workflow

### Step 1: Locate the source

For Zotero use cases:

- Prefer local attachment write-back to the Zotero-managed PDF file.
- Confirm the exact paper before editing if multiple candidates exist.
- If direct Zotero UI automation is unavailable, edit the underlying PDF attachment.
- When a generated or modified PDF needs to be inspected inside Zotero desktop, read `/Users/apple/.openclaw/workspace/skills/zotero-paper-coach/references/zotero-import-workflow.md` and prefer the helper script instead of `open -a Zotero file.pdf`.

For standalone PDFs:

- Work directly on the file path the user provided.

### Step 2: Inspect the document

Extract enough text to identify:

- title and abstract
- research question / gap
- contribution or key points
- methods and dataset choices
- central results
- limitations / caveats
- conclusion

When the PDF is scanned or text extraction is poor, say so and switch to a reduced-confidence workflow.
Read `/Users/apple/.openclaw/workspace/skills/zotero-paper-coach/references/backend-modes.md` and `/Users/apple/.openclaw/workspace/skills/zotero-paper-coach/references/failure-and-fallbacks.md` when choosing whether to write back or downgrade.

### Step 3: Build an annotation plan

Do not highlight as you read blindly.

Create an internal plan with:

- target pages
- target sentences or paragraph anchors
- highlight color
- note label
- note content
- rationale for inclusion
- item confidence
- whether the item should be promoted into the reading guide

Read `/Users/apple/.openclaw/workspace/skills/zotero-paper-coach/references/annotation-plan-schema.md` for the recommended plan shape.

The plan should optimize for learning value, not raw coverage.

### Step 4: Map the plan to the user goal

#### beginner-learning
Prioritize:
- research question
- why the paper matters
- main findings
- limitations
- plain-language explanations
- suggested reading order

#### quick-read
Prioritize:
- abstract core lines
- contribution list
- 3 to 8 strongest result sentences
- main caveat
- conclusion

#### exam-prep
Prioritize:
- definitions
- framework and variables
- key findings
- compare/contrast points
- memorable sentences suitable for recall

#### literature-review
Prioritize:
- gap statement
- novelty claim
- strongest evidence sentences
- explicit limitations
- quotable synthesis lines
- relation to prior work

#### replication
Prioritize:
- data sources
- model/config choices
- metrics
- evaluation protocol
- implementation caveats
- anything likely to cause reproduction errors

#### citation-harvest
Prioritize:
- precise claims
- scoped findings
- definitions worth quoting
- limitation statements that prevent overclaiming

### Step 5: Write mentor-style notes

Notes must add value. Avoid empty comments like “important”.

Use short labels like:

- `[先看]`
- `[主张]`
- `[证据]`
- `[限制]`
- `[人话]`
- `[复述]`
- `[方法]`
- `[为什么重要]`

Write notes in one of these patterns:

- **segment function**: explain what role the passage plays in the paper
- **plain-language translation**: rewrite dense academic prose into simple language
- **reading instruction**: tell the user whether to skim, study, compare, or memorize
- **critical warning**: point out a limitation, assumption, or overclaim risk
- **reuse hint**: say whether the line is good for review writing or oral explanation

## Density policy

Read `/Users/apple/.openclaw/workspace/skills/zotero-paper-coach/references/density-profiles.md` when choosing how much to mark. Compute density dynamically from body pages, body words, and paragraph density rather than relying on a fixed total count.

Rules:

- `light`: mark only backbone sentences; minimal notes
- `medium`: mark backbone + key evidence + 1-2 limitations per section
- `heavy`: include method anchors, evidence chain, caveats, and reuse lines
- `teaching`: include reading prompts, plain-language notes, and section-level guidance

Avoid the “yellow wallpaper” failure mode. If many adjacent sentences are important, prefer one anchor highlight plus a note explaining the paragraph’s role.

## Output options

Primary output is the annotated PDF.

Optional sidecar outputs:

- `paper.reading-guide.md`
- `paper.annotation-plan.md`
- `paper.annotation-plan.json`

Treat the reading guide as a first-class teaching artifact, not a debug byproduct.

If the user asks for teaching support, generate a reading guide using `/Users/apple/.openclaw/workspace/skills/zotero-paper-coach/references/reading-goals.md`.

## Dependency policy

This skill may rely on local PDF tooling.

Preferred stack:

- Python 3
- `pymupdf` for annotation creation, update, and deletion

Optional helpers when needed:

- OCR/text extraction tooling for scanned PDFs
- SQLite inspection for local Zotero attachment lookup

Before first write on a machine, mention missing required dependencies and ask before installing them.
Do not claim Zotero-native support unless it is actually implemented.

## Safety and write discipline

Always:

- create a backup before mutation
- preserve user annotations unless explicitly told otherwise
- support dry-run planning when asked
- say when extraction confidence is low
- avoid claiming Zotero-native annotation support if only PDF attachment write-back is available

## Bundled resources

Use these references as needed:

- `/Users/apple/.openclaw/workspace/skills/zotero-paper-coach/DESIGN.md`
- `/Users/apple/.openclaw/workspace/skills/zotero-paper-coach/references/annotation-styles.md`
- `/Users/apple/.openclaw/workspace/skills/zotero-paper-coach/references/density-profiles.md`
- `/Users/apple/.openclaw/workspace/skills/zotero-paper-coach/references/reading-goals.md`
- `/Users/apple/.openclaw/workspace/skills/zotero-paper-coach/references/user-modes.md`
- `/Users/apple/.openclaw/workspace/skills/zotero-paper-coach/references/annotation-plan-schema.md`
- `/Users/apple/.openclaw/workspace/skills/zotero-paper-coach/references/backend-modes.md`
- `/Users/apple/.openclaw/workspace/skills/zotero-paper-coach/references/failure-and-fallbacks.md`
- `/Users/apple/.openclaw/workspace/skills/zotero-paper-coach/references/zotero-import-workflow.md`

Use scripts from:

- `/Users/apple/.openclaw/workspace/skills/zotero-paper-coach/scripts/annotate_pdf.py`
- `/Users/apple/.openclaw/workspace/skills/zotero-paper-coach/scripts/remove_openclaw_annots.py`
- `/Users/apple/.openclaw/workspace/skills/zotero-paper-coach/scripts/extract_pdf_outline.py`
- `/Users/apple/.openclaw/workspace/skills/zotero-paper-coach/scripts/import_pdf_to_zotero.py`
