---
name: file-memory
description: >
  Persistent cross-session memory for files Claude has worked with. Stores per-file
  summaries, notes, and change history in a local .ai-memory/ directory. Journals what
  happened in each session (files touched, decisions made, key outcomes). Supports
  keyword and semantic search over remembered context. Generates a visual HTML dashboard
  of all remembered files. Use whenever the user says "remember this file", "what do you
  know about X", "search my memory", "session recap", "memory dashboard", or starts a new
  session in a project that has a .ai-memory/ directory. Also auto-activates on session
  start/end when CLAUDE.md includes the activation block for this skill.
license: MIT
---

# File Memory Skill

This skill gives Claude persistent, searchable memory of files across sessions. It stores per-file summaries, session journals, and supports meaning/keyword search. A visual HTML dashboard shows everything at a glance.

---

## Trigger Conditions

Activate this skill when:
- User says any of: "remember this file", "remember what we did", "recall file", "what do you know about", "search my memory", "memory dashboard", "session recap", "what happened last session", "file history", "note this", "log this decision"
- A `.ai-memory/` directory exists in the project root (auto-detected on session start when CLAUDE.md includes the activation block)
- User invokes any slash command from this skill: `/file-memory:remember-file`, `/file-memory:recall-file`, `/file-memory:session-recap`, `/file-memory:search-memory`, `/file-memory:memory-dashboard`

---

## Session Lifecycle

### On Session Start

1. Check for `.ai-memory/` in the project root.
2. If found:
   - Run: `python3 <skill_dir>/scripts/session_journal.py start --goal "New session" --root <project_root>`
   - Capture the printed `session_id` — store it as `<current_session_id>` for the rest of this session.
   - Run: `python3 <skill_dir>/scripts/memory_manager.py list --root <project_root>`
   - Note the remembered files silently (do not print the list to the user).
   - Greet the user: "File memory loaded — I remember N files and M sessions for this project."
3. If not found:
   - Say nothing unless the user asks about memory.

### During a Session

Whenever you read, modify, or create a file:
- If the file has no memory entry yet: silently call `memory_manager.py remember` to create one with an auto-generated summary.
- Call `memory_manager.py log-change` to append the action to that file's change history.
- Call `session_journal.py add-file` to record that the file was touched this session.
- Do all of this silently — do not narrate these actions unless the user asks for a recap.

When the user makes a notable decision (chooses one approach over another, explains a constraint, picks a library):
- Silently call `session_journal.py add-decision` to record it.

### On Session End

When the user says goodbye, closes the session, or says "we're done" / "that's all":
1. Call `session_journal.py end --session-id <current_session_id> --root <project_root>`
2. Add any remaining files not yet recorded via `session_journal.py add-file`.
3. Confirm: "Session journaled — N files remembered across M total sessions."

---

## Slash Commands

Each command template lives in `commands/`. Follow the instructions in the relevant file when a command is invoked.

| Command | File | What it does |
|---|---|---|
| `/file-memory:remember-file <path>` | `commands/remember-file.md` | Save a file's summary and context to memory |
| `/file-memory:recall-file <path>` | `commands/recall-file.md` | Retrieve everything remembered about a file |
| `/file-memory:session-recap [id\|last]` | `commands/session-recap.md` | Recap a session's files, decisions, outcomes |
| `/file-memory:search-memory <query>` | `commands/search-memory.md` | Search remembered context by keyword or meaning |
| `/file-memory:memory-dashboard` | `commands/memory-dashboard.md` | Generate a visual HTML dashboard |

---

## Script Reference

All scripts are in `<skill_dir>/scripts/`. They are plain Python 3, no external dependencies required for basic functionality (semantic search has optional deps with fallback).

- `memory_manager.py` — CRUD for per-file memory entries in `.ai-memory/files/`
- `session_journal.py` — Session lifecycle (start/end/decisions/file tracking)
- `search_memory.py` — Keyword + semantic search over `.ai-memory/files/`
- `dashboard_builder.py` — Generates self-contained HTML dashboard from `.ai-memory/`

Run any script with `--help` for usage details.

---

## Memory Directory

The skill writes to `.ai-memory/` in the **user's project root** — not inside the skill itself. Claude should suggest adding `.ai-memory/` to `.gitignore` unless the user wants to share memory with teammates (both are valid choices).

See `references/schema.md` for the full JSON schema documentation.
