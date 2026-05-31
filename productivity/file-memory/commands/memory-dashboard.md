---
description: Generate a visual HTML dashboard of all remembered files and sessions
---
Generate the file memory dashboard for this project.

1. Run:
   ```
   python3 <skill_dir>/scripts/dashboard_builder.py \
     --root <project_root> \
     --out .ai-memory/dashboard.html \
     --open
   ```
2. Tell the user: "Dashboard generated at `.ai-memory/dashboard.html` — opening in browser."
3. If --open fails (headless environment): show the file path and say "Open this file in your browser to view the dashboard."

The dashboard shows:
- KPI header: files remembered, sessions logged, most active file
- Sortable file table with expandable rows (full notes and change history on click)
- Session history (most recent 10, collapsible with decisions and outcomes)
- Tag cloud sized by frequency
- Activity sparkline (files touched per session over last 10 sessions)

$@
