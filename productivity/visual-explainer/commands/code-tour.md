---
description: Generate a visual HTML codebase tour — file structure, entry points, module relationships, data models, and onboarding checklist for developer orientation
---
Load the visual-explainer skill, then generate a comprehensive visual codebase tour as a self-contained HTML page.

Follow the visual-explainer skill workflow. Read the reference template, CSS patterns, and mermaid theming references before generating. Use a Blueprint aesthetic (technical, precise, deep slate/blue palette, monospace labels) — ideal for developer-facing documentation.

**Scope:** `$1` if provided (path to directory or file); otherwise the current working directory.

**Data gathering phase** — run these before generating:

1. **File structure scan:**
   - `find . -type f | grep -v node_modules | grep -v .git | grep -v dist | grep -v __pycache__ | sort` — full file tree
   - Identify the language and framework (look for `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `pom.xml`, etc.)
   - Identify entry points: `main.*`, `index.*`, `app.*`, `server.*`, `cli.*`
   - Read `README.md` if present for stated purpose and install instructions
   - Read the first 40 lines of each entry point to understand how the program starts

2. **Module and dependency mapping:**
   - For each directory with code files, read its main file(s) to understand the module's purpose
   - Map import/require relationships between modules (grep for import patterns in the project's language)
   - Identify "core" modules (imported by many others) vs "leaf" modules (import from core, not imported elsewhere)
   - Note any circular dependencies

3. **Data model discovery:**
   - Find type definitions, interfaces, schemas, models
   - Identify the primary data entities the codebase works with and their relationships

4. **Configuration and environment:**
   - List env vars used in code
   - Read config files (`.env.example`, `config.*`, `settings.*`)

5. **Test coverage:**
   - Count test files and test cases
   - Identify which modules have corresponding test files vs which are untested

**Verification checkpoint** — before generating HTML, confirm:
- You've read each entry point in full
- You understand the primary data flow (what comes in, what happens to it, what goes out)
- You've mapped the module dependency graph from actual imports (not guessed from file names)
- All module descriptions are based on code you read

**Diagram structure** — the page should include:

1. **Project overview** — one-paragraph elevator pitch synthesized from README + code: what problem it solves, how it works at a high level, target users. Then: language/framework badge, entry point list, scale (file count, approximate line count). *Visual treatment: hero depth — large type 20-24px, accent-tinted background zone. This is the first thing a new developer reads.*

2. **Codebase map** — visual file tree using the `.dir-tree` CSS pattern. Color-code by role: entry points (accent), core modules (primary text), utilities (dimmed), tests (muted green), config (amber). Annotate each directory with a one-line purpose description.

3. **Module dependency graph** — Mermaid `graph TD` showing how modules import from each other. Nodes are directories/modules (not individual files). Color-code by role: core (bright accent border), leaf (default), entry point (hero accent). Circular dependencies get a red dashed edge with a `⚠ circular` label. Use the full `diagram-shell` pattern with zoom/pan controls and click-to-expand.

4. **Entry point flows** — for each entry point file, a Mermaid sequence diagram or flowchart showing the top-level execution path from program start to first meaningful action. Keep to 8-10 steps — don't trace every branch, only the happy path. Use the full `diagram-shell` pattern.

5. **Primary data models** — for each major data entity: a card showing name, key fields with types, and which modules read/write it. If there are 3+ entities with relationships, add a Mermaid `erDiagram` or `classDiagram`.

6. **Configuration reference** — table of all env vars and config options: name, type, required/optional, default value, purpose. Mark security-sensitive values (tokens, keys, secrets) with an amber `SECRET` badge. *Visual treatment: compact data table with sticky header.*

7. **Test coverage map** — table or card grid: module name → has tests (green dot) / no tests (red dot) / partial (amber dot). Add a coverage KPI at the top showing % of modules with at least one test file.

8. **Onboarding checklist** — what a new developer needs to do to get running locally: clone, install dependencies, configure env vars, run tests, start dev server. Synthesize from README + package.json scripts + config files. *Visual treatment: numbered flow cards, not a flat list. Each step should be actionable — include the actual command.*

9. **Key invariants and gotchas** — collapsible `<details>` section with: implicit assumptions the codebase relies on, non-obvious coupling between modules, things that would surprise a developer modifying this code. Be specific — reference actual files and function names. *Visual treatment: `<details>` collapsed by default.*

**Visual hierarchy**: Sections 1-4 dominate (hero depth for overview, elevated for graphs). Sections 5-7 are content-density medium (elevated cards, compact tables). Sections 8-9 are reference material (flat/collapsible).

Include responsive section navigation (sticky sidebar on desktop, horizontal bar on mobile — see `./references/responsive-nav.md`). Write to `~/.agent/diagrams/` and open in browser.

Ultrathink.

$@
