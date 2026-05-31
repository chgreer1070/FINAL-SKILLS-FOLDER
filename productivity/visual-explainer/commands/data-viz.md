---
description: Generate a visual HTML dashboard from data files (CSV, JSON, TSV) — auto-detect data shape, produce Chart.js charts, and render a sortable/filterable data table
---
Load the visual-explainer skill, then generate a visual data dashboard as a self-contained HTML page.

Follow the visual-explainer skill workflow. Read the reference template, CSS patterns, and mermaid theming references before generating. Choose an aesthetic that fits the data's character: Data-dense for operational metrics, Editorial for reports intended to be read, Blueprint for technical measurements.

**Input:** `$1` — path to a data file (CSV, JSON, TSV, NDJSON) or a directory containing data files. If no argument, look for data files in the current directory.

**Data gathering phase:**

1. **Read the data file(s):**
   - Detect format from extension and file content
   - For CSV/TSV: read the header row + first 30 rows to understand schema
   - For JSON arrays: sample first 30 items; note total array length
   - For JSON objects: inspect the key structure
   - Note: row count, column count, data types per column (string, number, date, boolean)

2. **Analyze the data shape:**
   - Identify numeric columns (candidates for aggregation and charts)
   - Identify categorical columns (candidates for grouping — count unique values)
   - Identify date/time columns (candidates for time-series axis)
   - Compute basic stats for each numeric column: min, max, mean, count of null/empty values
   - Identify any obvious patterns: monotonically increasing values, skewed distributions, outliers

3. **Choose visualizations** based on data shape:
   - Single high-value number → KPI card with label and context
   - Numeric over ordered time → Line chart (Chart.js)
   - Numeric by category (≤10 categories) → Vertical bar chart (Chart.js)
   - Numeric by category (>10 categories) → Horizontal bar chart or sortable table
   - Part-of-whole with ≤6 slices → Doughnut chart (Chart.js)
   - Two numeric columns → Scatter chart (Chart.js)
   - Many numeric columns per row → Data table with inline SVG sparklines
   - Nested JSON hierarchy → Collapsible tree or Mermaid mindmap
   - If data doesn't clearly fit any chart: always fall back to a sortable/filterable data table

4. **Generate summary statistics** to display as KPIs: row count, date range (if applicable), key aggregate figures (sum, average, max for the most meaningful numeric column)

**HTML generation guidelines:**

- Embed the actual data inline as a JavaScript `const DATA = [...]` array so the page is fully self-contained (no external data fetching)
- For large datasets (>500 rows): embed only the first 500 rows and note the truncation in the UI. Use the full dataset for summary statistics.
- Use **Chart.js** for all charts (see `./references/libraries.md`). Always initialize with `isDark` check for correct colors.
- For data tables: use the full data-table pattern from `./references/css-patterns.md` with client-side sorting and a search/filter input
- Each chart gets a title and a 1-2 sentence interpretation below it: "X peaks in Y" or "Category A is 3× larger than category B"

**Interactive features to include:**
- Click column header → sort table ascending/descending (see sortable table pattern in `./references/css-patterns.md`)
- Search input above the table → filter rows by substring match across all columns
- Chart tooltips → show exact values on hover (Chart.js built-in)
- Print button or note → users can Ctrl+P to save as PDF (print styles in `./references/css-patterns.md` handle the rest)

**Diagram structure:**

1. **Data summary** — source file name, format, row count, column count. KPI cards for the most meaningful aggregate figures (total, average, max, date range). *Visual treatment: hero depth.*

2. **Column schema** — compact table: column name, detected type, sample values (3 examples), null count, unique value count (for categorical) or min/max (for numeric). Useful for understanding data quality before reading the charts.

3. **Visualizations** — one or more charts chosen based on data shape. Each chart in a card with a title, subtitle (what the axes represent), and a brief interpretation. Mix chart types if data supports multiple views (e.g., a bar chart of totals by category + a line chart of the same metric over time).

4. **Data table** — full (or truncated) sortable, filterable data table with sticky header, alternating rows, and row count display. *Visual treatment: flat, compact, full-width.*

**Write to `~/.agent/diagrams/` and open in browser.**

Ultrathink.

$@
