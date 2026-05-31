---
description: Search file memory by keyword or meaning
---
Search persistent file memory for: $@

1. Run:
   ```
   python3 <skill_dir>/scripts/search_memory.py "$@" --root <project_root> --format table
   ```
2. Present the results:
   - If 0 results: "No matches found for '$@'. Try broader terms or run /file-memory:memory-dashboard to see what's remembered."
   - If 1–3 results: show each match with full summary, tags, and last-seen date.
   - If 4+ results: show the ranked table, offer to expand any specific result.
3. After showing results, offer: "Want full details for any of these? Say 'recall <filename>'."

Semantic search is used by default (keyword fallback if sentence-transformers/sklearn unavailable).

$@
