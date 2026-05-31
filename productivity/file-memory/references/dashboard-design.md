# Dashboard Design Reference

## Overview

`dashboard_builder.py` reads `.ai-memory/` data, injects it into `assets/dashboard_template.html` as inline JSON, and writes a self-contained HTML file. All CSS and JS are already embedded in the template — the builder only injects data and optionally updates the page title.

---

## How Data Is Injected

The template contains this placeholder line:
```js
const MEMORY_DATA = {"files":[],"sessions":[],"project_root":"","file_count":0,"session_count":0};
```

`dashboard_builder.py` replaces it with the real JSON payload:
```js
const MEMORY_DATA = { /* full data object */ };
```

The `MEMORY_DATA` shape:
```json
{
  "files": [ /* array of full file entry objects from files/*.json */ ],
  "sessions": [ /* array of session journal objects, most recent first */ ],
  "project_root": "/absolute/path/to/project",
  "file_count": 12,
  "session_count": 7,
  "last_updated": "2026-05-31T14:22:00Z"
}
```

---

## CSS Custom Properties

All colors and fonts are defined as CSS custom properties on `:root`. To retheme the dashboard, override these:

| Property | Default | Role |
|---|---|---|
| `--bg` | `#1a2332` | Page background (deep slate) |
| `--surface` | `#1e2d42` | Panel backgrounds |
| `--surface-2` | `#243550` | Hover states, table headers |
| `--border` | `rgba(255,255,255,0.08)` | Dividers |
| `--text` | `#e2e8f0` | Primary text |
| `--text-dim` | `#94a3b8` | Secondary text, labels |
| `--accent` | `#0891b2` | Teal highlight, links, badges |
| `--accent-dim` | `rgba(8,145,178,0.15)` | KPI chip backgrounds |
| `--green` | `#10b981` | Outcomes, success states |
| `--amber` | `#f59e0b` | Warnings |
| `--red` | `#ef4444` | Errors |
| `--mono` | JetBrains Mono → Fira Code | Monospace font (paths, IDs, timestamps) |
| `--body` | IBM Plex Sans → system-ui | Body text font |

---

## Dashboard Panels

### 1. Header + KPIs
- Project name from `MEMORY_DATA.project_root` (basename)
- Three KPI chips: Files Remembered, Sessions Logged, Most Active File
- Rendered by `renderKPIs()`

### 2. File Memory Table (`#files-table`)
- Columns: Path (monospace), Importance (badge), Last Seen (relative time), Tags, Summary
- Sortable by clicking column headers — calls `sortTable(key)`
- Click any row to expand/collapse inline detail panel showing full change history and notes
- Rendered by `renderFiles()` / `toggleRow(i)`

### 3. Session History (`#sessions-list`)
- Most recent 10 sessions as `<details>/<summary>` collapsible elements
- Each shows: session ID, goal, duration, file count in the collapsed header
- Expanded: files touched, decisions, outcomes
- Rendered by `renderSessions()`

### 4. Tag Cloud (`#tag-cloud`)
- All unique tags across all files, font-size proportional to frequency
- Top-5 most common tags styled in accent color
- Rendered by `renderTagCloud()`

### 5. Activity Sparkline
- Inline SVG `<polyline>` showing files-per-session over last 10 sessions
- Dots at each data point, no axes — just the shape of activity
- Rendered by `renderSparkline()`

---

## Adding a New Panel

1. Add a `<div class="panel">` block in the HTML body with a new `id`.
2. Add a `render<PanelName>()` function in the `<script>` block that reads from `MEMORY_DATA`.
3. Call it from `init()`.
4. If new data is needed, extend the `MEMORY_DATA` shape and update `_load_data()` in `dashboard_builder.py`.

---

## Self-Contained Guarantee

The only external resource is Google Fonts (loaded via `<link>` in `<head>`). If offline, the browser falls back to `system-ui` / monospace system fonts. All logic, styles, and data are inline — the file works permanently with no server.
