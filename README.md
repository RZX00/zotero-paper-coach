# Zotero Paper Coach

A reading-coach skill for OpenClaw that annotates academic papers and Zotero-managed PDFs with structured highlights, mentor-style notes, reading guides, and confidence-aware write-back workflows.

## What it does

`zotero-paper-coach` is **not** a blind auto-highlighter.
It is designed as a **paper reading coach + PDF write-back annotator**.

Core ideas:

- choose annotations based on the reader's goal
- use stable color semantics
- control density intentionally
- generate sidecar reading guides and annotation plans
- work well with Zotero-managed local PDF attachments
- be honest about backend mode and extraction confidence

## Key features

- **Goal-aware annotation modes**
  - beginner-learning
  - quick-read
  - exam-prep
  - literature-review
  - replication
  - citation-harvest

- **Style overlays**
  - mentor
  - top-student
  - critical-researcher
  - executive-brief

- **Density control**
  - light
  - medium
  - heavy
  - teaching

- **Dynamic density calculation**
  - scales by body pages
  - scales by body word count
  - adjusts for paragraph density and paper type
  - judges density by **highlight anchors**, not inflated note counts

- **Sidecar outputs**
  - `paper.reading-guide.md`
  - `paper.annotation-plan.md`
  - `paper.annotation-plan.json`

- **Zotero-friendly workflow**
  - supports local PDF attachment write-back
  - includes a stable Zotero desktop import helper
  - avoids the broken `open -a Zotero file.pdf` pattern on macOS

## Skill layout

```text
zotero-paper-coach/
├── SKILL.md
├── references/
│   ├── annotation-plan-schema.md
│   ├── annotation-styles.md
│   ├── backend-modes.md
│   ├── density-profiles.md
│   ├── failure-and-fallbacks.md
│   ├── reading-goals.md
│   ├── user-modes.md
│   └── zotero-import-workflow.md
└── scripts/
    ├── annotate_pdf.py
    ├── extract_pdf_outline.py
    ├── import_pdf_to_zotero.py
    └── remove_openclaw_annots.py
```

## Install with a prompt

After this repo is published to GitHub, a user can ask their agent:

```text
帮我安装 Zotero Paper Coach：https://raw.githubusercontent.com/RZX00/zotero-paper-coach/main/docs/install.md
```

This repo is published at `RZX00/zotero-paper-coach` on the `main` branch.

## Install manually

Copy the `zotero-paper-coach/` folder into one of these locations:

- `<workspace>/skills/zotero-paper-coach`
- `~/.openclaw/skills/zotero-paper-coach`

Then start a **new OpenClaw session** so the skill is picked up.

## Runtime expectations

The skill files themselves can be installed without system changes.
Some workflows may later rely on:

- Python 3
- PyMuPDF / `fitz`
- Zotero desktop (for Zotero-specific review flows)

## Design stance

This skill is opinionated:

- more highlights is **not** always better
- notes must add reading value, not noise
- density should be calculated dynamically from the paper itself
- "dense" should reflect actual passage coverage, not annotation-object inflation
- product honesty beats fake magic

## Repository contents

This repo is structured so it can be shared directly on GitHub and installed through a prompt-driven `docs/install.md` workflow.

- `zotero-paper-coach/` — installable AgentSkill folder
- `docs/install.md` — AI-agent installation instructions
- `PROMPT_TEMPLATE.txt` — copy/paste install prompt template

## Status

Current state: working prototype with validated packaging and real-paper workflow testing on:

- Transformer-style technical paper
- dense philosophy/hermeneutics paper

## License

Add your preferred license before broad public release if needed.
