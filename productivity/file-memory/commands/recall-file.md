---
description: Recall everything Claude remembers about a file
---
Recall the memory for the file $1.

1. Run:
   ```
   python3 <skill_dir>/scripts/memory_manager.py show --file "$1" --root <project_root>
   ```
2. Parse the JSON and present in a structured, readable format:

   **$1**
   Summary: <summary field>
   First seen: <human-readable date> | Last seen: <human-readable date>
   Importance: <importance> | Language: <language>
   Tags: <tags joined by ", ">
   Related: <related_files joined by ", "> (omit if empty)

   **Change history** (most recent 5):
   - YYYY-MM-DD — <change_type>: <description>

   **Notes** (most recent 5):
   - YYYY-MM-DD — <note>

3. If no memory exists for $1: "No memory found for $1. Use /file-memory:remember-file to remember it."

$@
