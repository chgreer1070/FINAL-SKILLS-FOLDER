---
description: Recap what happened in a session — files touched, decisions made, outcomes
---
Generate a session recap for $1. If $1 is omitted or "last", recap the most recent session.

1. Determine the session_id:
   - If $1 looks like a session ID (`sess-YYYY-MM-DD-NNN`), use it directly.
   - If $1 is "last" or omitted: run `python3 <skill_dir>/scripts/session_journal.py latest --root <project_root>`
   - If $1 is a date (YYYY-MM-DD): run `list` and filter by that date, let the user pick if multiple.
2. Run:
   ```
   python3 <skill_dir>/scripts/session_journal.py show --session-id <id> --root <project_root>
   ```
3. Present the recap:

   **Session Recap — <goal>**
   `<session_id>` | Started: <time> | Ended: <time or "ongoing"> | Duration: <Xm Ys>

   **Files touched** (<N>):
   - <action> — <path>

   **Decisions made** (<M>):
   1. <decision>: <rationale>

   **Outcomes**:
   - <outcome>

   (Omit any section that has no entries.)

$@
