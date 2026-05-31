---
description: Remember a file — save its summary, notes, and context to persistent memory
---
Remember the file $1 with persistent memory.

1. If $1 is not provided, ask the user which file to remember.
2. Read the file. Produce:
   - A 2–4 sentence `summary` describing what the file does, its role in the project, and any notable patterns.
   - A list of `tags` (3–8 keywords from: language, purpose, domain, framework, pattern).
   - An `importance` rating: `high` (entry point, core logic, frequently modified), `normal` (standard module), `low` (test fixture, config, generated file).
   - Any `related_files` the user mentioned or that are obvious from imports/references.
3. Run:
   ```
   python3 <skill_dir>/scripts/memory_manager.py remember \
     --file "$1" \
     --summary "<summary>" \
     --tags "<comma-separated tags>" \
     --importance <importance> \
     --related "<comma-separated related files or empty>" \
     --session-id <current_session_id> \
     --root <project_root>
   ```
4. Confirm: "Remembered $1: <first sentence of summary>. Tagged: <tags>."

If $2 is provided, treat it as an initial note and also run:
   ```
   python3 <skill_dir>/scripts/memory_manager.py update \
     --file "$1" --note "$2" --session-id <current_session_id> --root <project_root>
   ```

$@
