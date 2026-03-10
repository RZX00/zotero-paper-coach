# Zotero Paper Coach — Installation Guide

## For Humans

Copy this to your AI agent:

```text
帮我安装 Zotero Paper Coach：https://raw.githubusercontent.com/RZX00/zotero-paper-coach/main/docs/install.md
```

After you publish this repo to GitHub, replace `<RAW_INSTALL_MD_URL>` with the raw URL of **this file**, for example:

```text
帮我安装 Zotero Paper Coach：https://raw.githubusercontent.com/RZX00/zotero-paper-coach/main/docs/install.md
```

---

## For AI Agents

### Goal

Install the `zotero-paper-coach` skill from the same GitHub repo as this `install.md` file into the user's OpenClaw skills directory.

This repository contains:

- `zotero-paper-coach/` — the skill folder to install
- `docs/install.md` — this installation guide

### Boundaries

- Do **not** use `sudo` unless the user explicitly approved.
- Do **not** modify files outside the skill install target and temporary directories.
- Do **not** install extra system packages automatically just because the skill may use them later.
- Do **not** clone or unpack the repo into the user's active project workspace unless they explicitly ask.
- Use `/tmp/` or another temporary directory for download/extraction work.

### Install target

Preferred target:

- If the user's OpenClaw workspace is known, install into `<workspace>/skills/zotero-paper-coach`

Fallback target:

- `~/.openclaw/skills/zotero-paper-coach`

If both exist, prefer the workspace-local `skills/` folder unless the user asks for a global install.

### How to derive the repo URL

If the user invoked this guide using a raw GitHub URL like:

- `https://raw.githubusercontent.com/<owner>/<repo>/<branch>/docs/install.md`

then derive:

- repo page: `https://github.com/<owner>/<repo>`
- zip download: `https://github.com/<owner>/<repo>/archive/refs/heads/<branch>.zip`

If the source URL is not available, ask the user for the GitHub repo URL.

### Step 1: Download the repo to a temporary directory

Use a temp directory such as:

- `/tmp/zotero-paper-coach-install-<timestamp>/`

Download the branch zip from GitHub, extract it, and locate:

- `zotero-paper-coach/SKILL.md`

Do not install from a partial copy or guessed file list if the repo archive is available.

### Step 2: Validate the skill folder

Before copying, verify that the skill folder contains at least:

- `zotero-paper-coach/SKILL.md`

And preferably also:

- `zotero-paper-coach/scripts/`
- `zotero-paper-coach/references/`

If `SKILL.md` is missing, stop and tell the user the repo does not look like a valid skill bundle.

### Step 3: Copy the skill into the install target

Install the whole `zotero-paper-coach/` folder into the target skills directory.

Final result should be one of:

- `<workspace>/skills/zotero-paper-coach/SKILL.md`
- `~/.openclaw/skills/zotero-paper-coach/SKILL.md`

If a folder already exists:

- ask before overwriting
- if the user confirms, replace the existing folder cleanly

### Step 4: Tell the user how to load it

After installation, tell the user:

- start a **new OpenClaw session** so the skill is picked up
- or restart/reopen the session if their environment requires a fresh skills snapshot

### Optional dependency note

The skill itself can be installed without extra package changes.

However, some workflows may later rely on:

- Python 3
- `pymupdf` / `fitz`

Do **not** auto-install these during skill installation unless the user explicitly asks. It is fine to say:

> “Skill files are installed. If you want, I can next verify runtime dependencies like PyMuPDF.”

### Success message template

Use a short confirmation like:

> Installed `zotero-paper-coach` into `<target>`. Start a new OpenClaw session and then you can invoke it for Zotero/PDF paper annotation workflows.
