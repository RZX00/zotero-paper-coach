# Zotero Paper Coach — Installation Guide

## For Humans

Copy this to your AI agent (Claude Code, Codex, or any agent that loads Agent Skills):

```text
帮我安装 Zotero Paper Coach：https://raw.githubusercontent.com/RZX00/zotero-paper-coach/main/docs/install.md
```

---

## For AI Agents

### Goal

Install the `zotero-paper-coach` skill folder from the GitHub repo that hosts this file into the skills directory of the agent you are running in.

The repository contains:

- `zotero-paper-coach/` — the skill folder to install (`SKILL.md`, `DESIGN.md`, `references/`, `scripts/`)
- `docs/install.md` — this guide

### Boundaries

- Do not use `sudo` or administrator rights unless the user explicitly approves.
- Do not modify files outside the install target and a temporary directory.
- Do not install Python packages during skill installation; the skill asks before its first PDF write.
- Do not unpack the repo into the user's current project unless they ask.

### Step 1: Pick the install target

Use the directory your own agent loads skills from:

| Agent | Personal install (all projects) | Project install (current repo only) |
|---|---|---|
| Claude Code | `~/.claude/skills/zotero-paper-coach/` | `<project>/.claude/skills/zotero-paper-coach/` |
| Codex and other agents that read `~/.agents/skills` | `~/.agents/skills/zotero-paper-coach/` | `<project>/.agents/skills/zotero-paper-coach/` |

If your agent is not listed, use the skills directory documented by that agent. If you cannot determine it, ask the user. Default to the personal install unless the user asks for a project install.

On Windows, `~` is the user's home folder, for example `C:\Users\<name>`.

### Step 2: Download the repo to a temporary directory

Derive the archive URL from the raw URL of this file:

- `https://raw.githubusercontent.com/<owner>/<repo>/<branch>/docs/install.md`
- → `https://github.com/<owner>/<repo>/archive/refs/heads/<branch>.zip`

Download and extract it into the system temporary directory (`/tmp` on macOS and Linux, `$env:TEMP` in PowerShell). `git clone --depth 1 https://github.com/<owner>/<repo>.git` works too.

The repository and the skill folder share the same name, so the folder to copy is one level down:

- source: `<extracted repo root>/zotero-paper-coach/` — it contains `SKILL.md` directly
- target: `<skills directory>/zotero-paper-coach/SKILL.md`

The zip extracts to `zotero-paper-coach-<branch>/zotero-paper-coach/`; a clone gives `zotero-paper-coach/zotero-paper-coach/`.

### Step 3: Validate and copy

1. Confirm the source folder contains `SKILL.md`. If it does not, stop and tell the user the download is not a valid skill bundle.
2. If the target folder already exists, ask the user before replacing it. After they confirm, delete the old folder first, then copy, so files from the old version do not linger.
3. Copy the whole source folder to the target.
4. Delete the temporary directory.

macOS / Linux example (personal install for Claude Code):

```bash
tmp=$(mktemp -d)
git clone --depth 1 https://github.com/RZX00/zotero-paper-coach.git "$tmp/repo"
mkdir -p ~/.claude/skills
cp -R "$tmp/repo/zotero-paper-coach" ~/.claude/skills/
rm -rf "$tmp"
```

Windows PowerShell example (personal install for Codex):

```powershell
$tmp = Join-Path $env:TEMP "zpc-install"
Invoke-WebRequest https://github.com/RZX00/zotero-paper-coach/archive/refs/heads/main.zip -OutFile "$tmp.zip"
Expand-Archive "$tmp.zip" -DestinationPath $tmp -Force
New-Item -ItemType Directory -Force "$HOME\.agents\skills" | Out-Null
Copy-Item "$tmp\zotero-paper-coach-main\zotero-paper-coach" "$HOME\.agents\skills\" -Recurse
Remove-Item "$tmp.zip"; Remove-Item $tmp -Recurse
```

### Step 4: Tell the user how to load it

- Claude Code watches its skills directories, so the skill is usually available right away. If this is the user's first skill (the skills directory did not exist when the session started), tell them to run `/reload-skills` or restart Claude Code.
- Codex detects new skills automatically; if the skill does not appear, tell the user to restart Codex.

### Runtime dependencies

The skill writes PDFs with Python 3 and PyMuPDF. Install with the interpreter that will run the scripts: `python3 -m pip install pymupdf` on macOS and Linux, `python -m pip install pymupdf` on Windows. Do not install them now; it is fine to offer:

> Skill files are installed. If you want, I can check whether Python 3 and PyMuPDF are available.

### Success message

> Installed `zotero-paper-coach` into `<target>`. Start a new session, then ask me to annotate a paper, for example: 用 quick-read 模式标注这篇论文：<PDF 路径>
