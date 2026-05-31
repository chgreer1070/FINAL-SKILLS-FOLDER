# CLAUDE.md — File Memory Activation Template

Copy this file to the **root of any project** where you want Claude to have persistent file memory. Update the skill path if your installation location differs.

---

## File Memory Skill

This project uses the `file-memory` skill for persistent cross-session context.

### Skill Path

The skill is installed at: `~/.claude/skills/file-memory/`

Use `<skill_dir>` as an alias for this path in all script invocations below.

### Auto-Activation

**On session start:**
1. Check if `.ai-memory/` exists in this directory.
2. If it exists:
   - Run: `python3 <skill_dir>/scripts/session_journal.py start --goal "New session" --root .`
   - Capture the printed `session_id` as `<current_session_id>` for this session.
   - Run: `python3 <skill_dir>/scripts/memory_manager.py list --root .`
   - Note the remembered files silently (do not print the list to the user).
   - Greet the user: "File memory loaded — I remember N files and M sessions for this project."
3. If it does not exist: say nothing unless the user asks about memory.

**During a session:**
- Whenever you read, modify, or create a file: silently call `memory_manager.py log-change` for that file.
- If a file has no memory entry yet: silently call `memory_manager.py remember` to create one.
- When the user makes a notable decision: silently call `session_journal.py add-decision`.
- Do not narrate these actions — they happen in the background.

**On session end** (when the user says goodbye, "we're done", "that's all", or closes the session):
1. Run: `python3 <skill_dir>/scripts/session_journal.py end --session-id <current_session_id> --root .`
2. Ensure all files touched this session have been recorded via `session_journal.py add-file`.
3. Confirm: "Session journaled — N files remembered across M total sessions."

### Available Commands

| Command | What it does |
|---|---|
| `/file-memory:remember-file <path>` | Save a file's summary and context to memory |
| `/file-memory:recall-file <path>` | Retrieve everything remembered about a file |
| `/file-memory:session-recap [id\|last]` | Recap a session's files, decisions, and outcomes |
| `/file-memory:search-memory <query>` | Search remembered context by keyword or meaning |
| `/file-memory:memory-dashboard` | Generate a visual HTML dashboard of all memory |

### Gitignore Recommendation

Add `.ai-memory/` to your `.gitignore` to keep memory private:
```
.ai-memory/
```

Or commit it to share memory with teammates — both approaches are valid.
