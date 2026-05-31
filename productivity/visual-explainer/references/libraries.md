# External Libraries (CDN)

Optional CDN libraries for cases where pure CSS/HTML isn't enough. Only include what the diagram actually needs — most diagrams need zero external JS.

## Mermaid.js — Diagramming Engine

Use for flowcharts, sequence diagrams, ER diagrams, state machines, mind maps, class diagrams, and any diagram where automatic node positioning and edge routing saves effort. Mermaid handles layout — you handle theming.

Do NOT use for dashboards — CSS Grid card layouts with Chart.js look better for those. Data tables use `<table>` elements.

**CDN:**
```html
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';

  mermaid.initialize({ startOnLoad: true, /* ... */ });
</script>
```

**With ELK layout** (required for `layout: 'elk'` — it's a separate package, not bundled in core):
```html
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
  import elkLayouts from 'https://cdn.jsdelivr.net/npm/@mermaid-js/layout-elk/dist/mermaid-layout-elk.esm.min.mjs';

  mermaid.registerLayoutLoaders(elkLayouts);
  mermaid.initialize({ startOnLoad: true, layout: 'elk', /* ... */ });
</script>
```

Without the ELK import and registration, `layout: 'elk'` silently falls back to dagre. Only import ELK when you actually need it — it adds significant bundle weight. Most simple diagrams render fine with dagre.

### Deep Theming

Always use `theme: 'base'` — it's the only theme where all `themeVariables` are fully customizable. The built-in themes (`default`, `dark`, `forest`, `neutral`) ignore most variable overrides.

```html
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';

  const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  mermaid.initialize({
    startOnLoad: true,
    theme: 'base',
    look: 'classic',
    themeVariables: {
      // Background and surfaces — teal/slate palette (not violet/indigo!)
      primaryColor: isDark ? '#134e4a' : '#ccfbf1',
      primaryBorderColor: isDark ? '#14b8a6' : '#0d9488',
      primaryTextColor: isDark ? '#f0fdfa' : '#134e4a',
      secondaryColor: isDark ? '#1e293b' : '#f0fdf4',
      secondaryBorderColor: isDark ? '#059669' : '#16a34a',
      secondaryTextColor: isDark ? '#f1f5f9' : '#1e293b',
      tertiaryColor: isDark ? '#27201a' : '#fef3c7',
      tertiaryBorderColor: isDark ? '#d97706' : '#f59e0b',
      tertiaryTextColor: isDark ? '#fef3c7' : '#27201a',
      // Lines and edges
      lineColor: isDark ? '#64748b' : '#94a3b8',
      // Text
      fontSize: '16px',
      fontFamily: 'var(--font-body)',
      // Notes and labels
      noteBkgColor: isDark ? '#1e293b' : '#fefce8',
      noteTextColor: isDark ? '#f1f5f9' : '#1e293b',
      noteBorderColor: isDark ? '#fbbf24' : '#d97706',
    }
  });
</script>
```

**FORBIDDEN in Mermaid themeVariables:** `#8b5cf6`, `#7c3aed`, `#a78bfa` (indigo/violet), `#d946ef` (fuchsia). Use teal, slate, amber, emerald, or colors from your page's palette.

### CSS Overrides on Mermaid SVG

Mermaid renders SVG. Override its classes for pixel-perfect control that `themeVariables` can't reach:

```css
/* Container — see css-patterns.md "Mermaid Zoom Controls" for the full zoom pattern */
.mermaid-wrap {
  position: relative;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 24px;
  overflow: auto;
}

/* CRITICAL: Force node/edge text to follow the page's color scheme.
   Without this, themeVariables.primaryTextColor works for DEFAULT nodes,
   but any classDef that sets color: will hardcode a single value that
   breaks in the opposite color scheme. Fix: never set color: in classDef,
   and always include these CSS overrides. */
.mermaid .nodeLabel { color: var(--text) !important; }
.mermaid .edgeLabel { color: var(--text-dim) !important; background-color: var(--bg) !important; }
.mermaid .edgeLabel rect { fill: var(--bg) !important; }

/* Node shapes */
.mermaid .node rect,
.mermaid .node circle,
.mermaid .node polygon {
  stroke-width: 1.5px;
}

/* Edge paths */
.mermaid .edge-pattern-solid {
  stroke-width: 1.5px;
}

/* Edge labels — smaller than node labels for visual hierarchy */
.mermaid .edgeLabel {
  font-family: var(--font-mono) !important;
  font-size: 13px !important;
}

/* Node labels — 16px default; drop to 14px for complex diagrams (20+ nodes) */
.mermaid .nodeLabel {
  font-family: var(--font-body) !important;
  font-size: 16px !important;
}

/* Sequence diagram actors */
.mermaid .actor {
  stroke-width: 1.5px;
}

/* Sequence diagram messages */
.mermaid .messageText {
  font-family: var(--font-mono) !important;
  font-size: 12px !important;
}

/* ER diagram entities */
.mermaid .er.entityBox {
  stroke-width: 1.5px;
}

/* Mind map nodes */
.mermaid .mindmap-node rect {
  stroke-width: 1.5px;
}
```

### classDef and style Gotchas

`classDef` values and per-node `style` directives are static text inside `<pre>` — they can't use CSS variables or JS ternaries. Two rules:

1. **Never set `color:` in classDef or per-node `style` directives.** It hardcodes a text color that breaks in the opposite color scheme. This applies to both `classDef highlight fill:...,color:#2c2a25` and `style I fill:...,color:#2c2a25`. Let the CSS overrides above handle text color via `var(--text)`.

2. **Use semi-transparent fills (8-digit hex) for node backgrounds.** They layer over whatever Mermaid's base theme background is, producing a tint that works in both light and dark modes. Use `20`–`44` alpha for subtle, `55`–`77` for prominent:

```
classDef highlight fill:#b5761433,stroke:#b57614,stroke-width:2px
classDef muted fill:#7c6f6411,stroke:#7c6f6444,stroke-width:1px
```

### Node Label Special Characters

Mermaid uses certain characters for shape syntax. Node labels containing these characters cause syntax errors unless quoted.

**Shape characters to watch:**
- `[/text/]` — parallelogram
- `[\text\]` — trapezoid (alt)
- `[/text\]` — trapezoid
- `[\text/]` — trapezoid (alt)
- `[(text)]` — cylindrical
- `[[text]]` — subroutine
- `((text))` — circle
- `{{text}}` — hexagon

**If your node label starts with `/`, `\`, `(`, or `{`, wrap it in quotes:**

```
%% WRONG — syntax error (/ starts parallelogram shape)
CMD[/gallery command] --> SRV[server]

%% RIGHT — quotes escape the special character
CMD["/gallery command"] --> SRV[server]
```

**Edge labels with special characters also need quotes:**

```
%% WRONG — quotes inside edge label
UI -->|"Use as Reference"| RET

%% RIGHT — use single quotes or escape
UI -->|'Use as Reference'| RET
UI -->|Use as Reference| RET
```

Avoid opaque light fills like `fill:#fefce8` — they render as bright boxes in dark mode.

### stateDiagram-v2 Label Limitations

State diagram transition labels have a strict parser. Avoid:
- `<br/>` — only works in flowcharts; causes a parse error in state diagrams
- Parentheses in labels — `cancel()` can confuse the parser
- Multiple colons — the first `:` is the label delimiter; extra colons in the label text may break parsing

If you need multi-line labels or special characters, use a `flowchart` instead of `stateDiagram-v2`. Flowcharts support quoted labels (`|"label with: special chars"|`) and `<br/>` for line breaks.

### Writing Valid Mermaid

Most Mermaid failures come from a few recurring issues. Follow these rules to avoid invalid diagrams:

**For multi-line flowchart node labels, use `<br/>` (not `\n`).** Mermaid flowcharts interpret `<br/>` as a line break, but escaped `\n` in labels often renders as literal text:

```
%% WRONG — renders literal "\n" in node text
A["Copilot Backend\n/api + /api/voicebot"] --> B["Redis"]

%% RIGHT — renders on two lines
A["Copilot Backend<br/>/api + /api/voicebot"] --> B["Redis"]
```

**Quote labels with special characters.** Parentheses, colons, commas, brackets, and ampersands break the parser when unquoted. Wrap any label containing special characters in double quotes:

```
A["handleRequest(ctx)"] --> B["DB: query users"]
A[handleRequest] --> B[query users]
```

**Keep IDs simple.** Node IDs should be alphanumeric with no spaces or punctuation. Put the readable name in the label, not the ID:

```
userSvc["User Service"] --> authSvc["Auth Service"]
```

**Max 10-12 nodes per Mermaid diagram.** Beyond that, readability collapses even with zoom controls and increased fontSize. For complex architectures (15+ elements), use the **hybrid pattern**: a simple 5-8 node Mermaid overview showing module relationships, followed by CSS Grid cards with detailed function lists. Never cram everything into one diagram. Use `subgraph` blocks to group related nodes when under the limit:

```
subgraph Auth
  login --> validate --> token
end
subgraph API
  gateway --> router --> handler
end
Auth --> API
```

**Arrow styles for semantic meaning:**

| Arrow | Meaning | Use for |
|-------|---------|--------|
| `-->` | Solid | Primary flow |
| `-.->` | Dotted | Optional, async, or fallback paths |
| `==>` | Thick | Critical or highlighted path |
| `--x` | Cross | Rejected or blocked |
| `-->\|label\|` | Labeled | Decision branches, data descriptions |

**Escape pipes in labels.** If a label contains a literal `|`, use `#124;` (HTML entity) or rephrase to avoid it — pipes delimit edge labels in flowcharts.

**Sequence diagram messages must be plain text.** Unlike flowchart labels, sequence diagram messages (the text after `:`) cannot be quoted or escaped. Curly braces `{}`, square brackets `[]`, angle brackets `<>`, and `&` will silently break the parser and the entire diagram renders as raw text. Write human-readable descriptions, not code:

```
%% WRONG — parser chokes on braces, brackets, ampersand
A->>B: web_search({ queries: [...] })
B->>B: User removes query 2, keeps 1 & 3
B->>S: POST /submit { selected: [0, 2] }

%% RIGHT — plain English, no special characters
A->>B: Call web_search with queries
B->>B: User removes query 2, keeps 1 and 3
B->>S: POST /submit with selected indices
```

**Don't mix diagram syntax.** Each diagram type has its own syntax. `-->` works in flowcharts but not in sequence diagrams (`->>` instead). `:::className` works in flowcharts but not in ER diagrams. When in doubt, check the examples below for correct syntax per type.

### Layout Direction: TD vs LR

`flowchart LR` (left-to-right) spreads horizontally. With many nodes, Mermaid scales everything down to fit the width, making text unreadable. `flowchart TD` (top-down) is almost always better.

**When to use each:**

| Direction | Use when | Avoid when |
|-----------|----------|------------|
| `TD` (top-down) | Complex diagrams, 5+ nodes, hierarchies, architecture | Simple A→B→C linear flows |
| `LR` (left-to-right) | Simple linear flows, 3-4 nodes, pipelines | Complex graphs, many branches |

**Rule of thumb:** If the diagram has more than one row of nodes or any branching, use `TD`. The extra vertical space makes labels readable.

```
%% WRONG — LR with many nodes produces wide, short, unreadable diagram
flowchart LR
  A --> B --> C --> D --> E
  A --> F --> G --> H
  
%% RIGHT — TD uses vertical space, labels stay readable
flowchart TD
  A --> B --> C --> D --> E
  A --> F --> G --> H
```

### Diagram Type Examples

**Flowchart with decisions:**
```html
<pre class="mermaid">
graph TD
  A[Request] --> B{Authenticated?}
  B -->|Yes| C[Load Dashboard]
  B -->|No| D[Login Page]
  D --> E[Submit Credentials]
  E --> B
  C --> F{Role?}
  F -->|Admin| G[Admin Panel]
  F -->|User| H[User Dashboard]
</pre>
```

**Sequence diagram:**
```html
<pre class="mermaid">
sequenceDiagram
  participant C as Client
  participant G as Gateway
  participant S as Service
  participant D as Database
  C->>G: POST /api/data
  G->>G: Validate JWT
  G->>S: Forward request
  S->>D: Query
  D-->>S: Results
  S-->>G: Response
  G-->>C: 200 OK
</pre>
```

**ER diagram:**
```html
<pre class="mermaid">
erDiagram
  USERS ||--o{ ORDERS : places
  ORDERS ||--|{ LINE_ITEMS : contains
  LINE_ITEMS }o--|| PRODUCTS : references
  USERS { string email PK }
  ORDERS { int id PK }
  LINE_ITEMS { int quantity }
  PRODUCTS { string name }
</pre>
```

**State diagram:**
```html
<pre class="mermaid">
stateDiagram-v2
  [*] --> Draft
  Draft --> Review : submit
  Review --> Approved : approve
  Review --> Draft : request_changes
  Approved --> Published : publish
  Published --> Archived : archive
  Archived --> [*]
</pre>
```

**Mind map:**
```html
<pre class="mermaid">
mindmap
  root((Project))
    Frontend
      React
      Next.js
      Tailwind
    Backend
      Node.js
      PostgreSQL
      Redis
    Infrastructure
      AWS
      Docker
      Terraform
</pre>
```

**Class diagram:**
```html
<pre class="mermaid">
classDiagram
  class User {
    +string email
    +string name
    +login()
    +logout()
  }
  class Order {
    +int id
    +decimal total
    +submit()
  }
  class Product {
    +string name
    +decimal price
  }
  User "1" --> "*" Order : places
  Order "*" --> "*" Product : contains
</pre>
```

**C4 architecture (flowchart-as-C4):**
```html
<pre class="mermaid">
graph TD
  user(("👤 User<br/><small>Browser client</small>"))
  subgraph boundary["Web Platform"]
    app["Web App<br/><small>Node.js</small>"]
    db[("Database<br/><small>PostgreSQL</small>")]
  end
  email["📧 Email Service"]:::ext
  payment["💳 Payment Gateway"]:::ext
  user -->|"HTTPS"| app
  app -->|"SQL"| db
  app -->|"SMTP"| email
  app -->|"API"| payment
  classDef ext fill:none,stroke-dasharray:5 5
</pre>
```

Do NOT use native `C4Context` / `C4Container` syntax — it hardcodes sharp corners, its own font, and inline colors that ignore `themeVariables`. Use `graph TD` + `subgraph` for C4 boundaries instead; it inherits all theme settings automatically.

### Which Mermaid Diagram Type?

Quick-reference for choosing the right Mermaid syntax:

| You want to show... | Use | Syntax keyword |
|---|---|---|
| Process flow, decisions, pipelines | Flowchart | `graph TD` / `graph LR` |
| Request/response, API calls, temporal interactions | Sequence diagram | `sequenceDiagram` |
| Database tables and relationships | ER diagram | `erDiagram` |
| OOP classes, domain models with methods | Class diagram | `classDiagram` |
| System architecture at multiple zoom levels | C4 diagram | `graph TD` + `subgraph` (not native `C4Context`) |
| State transitions, lifecycles | State diagram | `stateDiagram-v2` |
| Hierarchical breakdowns, brainstorms | Mind map | `mindmap` |

### Dark Mode Handling

Mermaid initializes once — it can't reactively switch themes. Read the preference at load time inside your `<script type="module">`:

```javascript
const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
// Use isDark to pick light or dark values in themeVariables
```

The CSS overrides on the container (`.mermaid-wrap`) and page will still respond to `prefers-color-scheme` normally — only the Mermaid SVG internals are static.

## Chart.js — Data Visualizations

Use for bar charts, line charts, pie/doughnut charts, radar charts, and other data-driven visualizations in dashboard-type diagrams. Overkill for static numbers — use pure SVG/CSS for simple progress bars and sparklines.

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"></script>

<canvas id="myChart" width="600" height="300"></canvas>

<script>
  const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const textColor = isDark ? '#8b949e' : '#6b7280';
  const gridColor = isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)';
  const fontFamily = getComputedStyle(document.documentElement)
    .getPropertyValue('--font-body').trim() || 'system-ui, sans-serif';

  new Chart(document.getElementById('myChart'), {
    type: 'bar',
    data: {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
      datasets: [{
        label: 'Feedback Items',
        data: [45, 62, 78, 91, 120],
        backgroundColor: isDark ? 'rgba(129, 140, 248, 0.6)' : 'rgba(79, 70, 229, 0.6)',
        borderColor: isDark ? '#818cf8' : '#4f46e5',
        borderWidth: 1,
        borderRadius: 4,
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { labels: { color: textColor, font: { family: fontFamily } } },
      },
      scales: {
        x: { ticks: { color: textColor, font: { family: fontFamily } }, grid: { color: gridColor } },
        y: { ticks: { color: textColor, font: { family: fontFamily } }, grid: { color: gridColor } },
      }
    }
  });
</script>
```

Wrap the canvas in a styled container:
```css
.chart-container {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 20px;
  position: relative;
}

.chart-container canvas {
  max-height: 300px;
}
```

## anime.js — Orchestrated Animations

Use when a diagram has 10+ elements and you want a choreographed entrance sequence (staggered reveals, path drawing, count-up numbers). For simpler diagrams, CSS `animation-delay` staggering is sufficient.

```html
<script src="https://cdn.jsdelivr.net/npm/animejs@3.2.2/lib/anime.min.js"></script>

<script>
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (!prefersReduced) {
    anime({
      targets: '.ve-card',
      opacity: [0, 1],
      translateY: [20, 0],
      delay: anime.stagger(80, { start: 200 }),
      easing: 'easeOutCubic',
      duration: 500,
    });

    anime({
      targets: '.connector path',
      strokeDashoffset: [anime.setDashoffset, 0],
      easing: 'easeInOutCubic',
      duration: 800,
      delay: anime.stagger(150, { start: 600 }),
    });

    document.querySelectorAll('[data-count]').forEach(el => {
      anime({
        targets: { val: 0 },
        val: parseInt(el.dataset.count),
        round: 1,
        duration: 1200,
        delay: 400,
        easing: 'easeOutExpo',
        update: (anim) => { el.textContent = anim.animations[0].currentValue; }
      });
    });
  }
</script>
```

When using anime.js, set initial opacity to 0 in CSS so elements don't flash before the animation:
```css
.ve-card { opacity: 0; }

@media (prefers-reduced-motion: reduce) {
  .ve-card { opacity: 1 !important; }
}
```

## D3.js — Network and Custom Visualizations

Use for force-directed network graphs, tree/hierarchy visualizations, and custom SVG diagrams that need dynamic data-driven layout. D3 is overkill for simple charts (use Chart.js) and unnecessary for flowcharts (use Mermaid). Reserve it for interactive network visualizations and complex data encodings that neither handles.

**Decision guide:**

| Need | Tool |
|------|------|
| Bar / line / pie charts | Chart.js |
| Flowcharts, sequence, ER, state | Mermaid |
| Dependency graphs, module maps, link+node networks | **D3.js** |
| Tree with size/color encoding | **D3.js** |
| Custom SVG driven by data arrays | **D3.js** |

```html
<script src="https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js"></script>
```

### Force-Directed Network Graph

For dependency graphs, module relationship maps, and any link-and-node visualization where position should emerge from relationship strength. Nodes repel each other; links pull connected nodes together.

```html
<div id="network-graph"
  style="width:100%;height:480px;border:1px solid var(--border);border-radius:12px;overflow:hidden;background:var(--surface);"
></div>

<script>
const nodes = [
  { id: 'core',  label: 'Core',    group: 'core'    },
  { id: 'auth',  label: 'Auth',    group: 'service' },
  { id: 'api',   label: 'API',     group: 'service' },
  { id: 'db',    label: 'Database',group: 'data'    },
  { id: 'cache', label: 'Cache',   group: 'data'    },
];

const links = [
  { source: 'core',  target: 'auth'  },
  { source: 'core',  target: 'api'   },
  { source: 'api',   target: 'db'    },
  { source: 'api',   target: 'cache' },
  { source: 'auth',  target: 'db'    },
];

const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
const groupColor = {
  core:    isDark ? '#22d3ee' : '#0891b2',
  service: isDark ? '#34d399' : '#059669',
  data:    isDark ? '#fbbf24' : '#d97706',
};
const labelColor  = isDark ? '#e2e8f0' : '#1e293b';
const linkColor   = isDark ? 'rgba(255,255,255,0.12)' : 'rgba(0,0,0,0.10)';

const container = document.getElementById('network-graph');
const width = container.clientWidth;
const height = 480;

const svg = d3.select(container)
  .append('svg')
  .attr('width', width)
  .attr('height', height);

const g = svg.append('g');
svg.call(
  d3.zoom().scaleExtent([0.3, 4]).on('zoom', e => g.attr('transform', e.transform))
);

const sim = d3.forceSimulation(nodes)
  .force('link',   d3.forceLink(links).id(d => d.id).distance(110))
  .force('charge', d3.forceManyBody().strength(-320))
  .force('center', d3.forceCenter(width / 2, height / 2))
  .force('collide', d3.forceCollide(36));

const link = g.append('g')
  .selectAll('line')
  .data(links)
  .join('line')
  .attr('stroke', linkColor)
  .attr('stroke-width', 1.5);

const node = g.append('g')
  .selectAll('circle')
  .data(nodes)
  .join('circle')
  .attr('r', 20)
  .attr('fill',   d => groupColor[d.group] + '28')
  .attr('stroke', d => groupColor[d.group])
  .attr('stroke-width', 2)
  .style('cursor', 'grab')
  .call(
    d3.drag()
      .on('start', (e, d) => { if (!e.active) sim.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
      .on('drag',  (e, d) => { d.fx = e.x; d.fy = e.y; })
      .on('end',   (e, d) => { if (!e.active) sim.alphaTarget(0); d.fx = null; d.fy = null; })
  );

const label = g.append('g')
  .selectAll('text')
  .data(nodes)
  .join('text')
  .text(d => d.label)
  .attr('text-anchor', 'middle')
  .attr('dy', '0.35em')
  .attr('font-family', 'var(--font-mono, monospace)')
  .attr('font-size', 11)
  .attr('fill', labelColor)
  .attr('pointer-events', 'none');

sim.on('tick', () => {
  link
    .attr('x1', d => d.source.x).attr('y1', d => d.source.y)
    .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
  node .attr('cx', d => d.x).attr('cy', d => d.y);
  label.attr('x',  d => d.x).attr('y',  d => d.y + 34);
});
</script>
```

**Interaction:** Drag nodes to reposition them (force simulation responds in real time). Scroll to zoom the whole graph. Drag the background to pan.

**Customization tips:**
- `d3.forceManyBody().strength(-320)` — more negative = stronger repulsion = more spread out
- `d3.forceLink().distance(110)` — controls preferred link length
- Change `r` on circles for node size; vary by `d.group` or add a `size` field to data
- Add arrowheads: `svg.append('defs').append('marker')` with `markerEnd` on link paths
- Color circular dependencies red: filter links where `source === target` chain exists

---

## Prism.js — Syntax Highlighting

Use for code blocks that display source code snippets with token-level syntax coloring. Useful in code tours, API docs, and implementation plans where the language is known.

**When to use:** Named language code blocks (TypeScript, Python, SQL, YAML, etc.) where readers are expected to read and understand the code.

**When to skip:** Terminal output, log lines, single-expression snippets, or any code block where language detection would guess wrong.

**CDN — core + autoloader (handles 200+ languages, no per-language imports):**

```html
<!-- Load theme first so code isn't unstyled for a frame -->
<link id="prism-theme" rel="stylesheet" href="">

<script src="https://cdn.jsdelivr.net/npm/prismjs@1/components/prism-core.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/prismjs@1/plugins/autoloader/prism-autoloader.min.js"></script>

<script>
  const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  document.getElementById('prism-theme').href = isDark
    ? 'https://cdn.jsdelivr.net/npm/prismjs@1/themes/prism-tomorrow.css'
    : 'https://cdn.jsdelivr.net/npm/prismjs@1/themes/prism-solarizedlight.css';

  Prism.plugins.autoloader.languages_path =
    'https://cdn.jsdelivr.net/npm/prismjs@1/components/';
</script>
```

**Usage** — add a `language-*` class to any `<code>` element:

```html
<div class="code-file">
  <div class="code-file__header">
    <span>src/server.ts</span>
    <button class="copy-btn" data-copy>Copy</button>
  </div>
  <pre class="code-file__body"><code class="language-typescript">export async function startServer(port: number) {
  const app = express();
  app.listen(port, () => console.log(`Listening on ${port}`));
}</code></pre>
</div>
```

Prism scans the page automatically after load and highlights all `code[class*="language-"]` elements. No manual call required.

**Theme palette overview:**

| Theme file | Best for |
|---|---|
| `prism-tomorrow.css` | Dark pages — gray-on-near-black, neutral |
| `prism-vsc-dark-plus.css` | Dark pages — VS Code Dark+ feel |
| `prism-solarizedlight.css` | Light pages — warm, low-contrast |
| `prism.css` (default) | Light pages — classic white background |
| `prism-nord.css` | Either — matches Nord IDE theme |

**Removing Prism's default background:** Prism's themes set `code[class*="language-"]` background to a fixed color. Override it to inherit from your card:

```css
/* Let your .code-file__body background win */
pre[class*="language-"],
code[class*="language-"] {
  background: transparent !important;
  text-shadow: none !important;
}
```

**Supported language classes** (autoloader fetches on demand): `language-typescript`, `language-javascript`, `language-python`, `language-go`, `language-rust`, `language-java`, `language-sql`, `language-bash`, `language-yaml`, `language-json`, `language-css`, `language-html`, `language-markdown`, and 200+ more.

---

## Google Fonts — Typography

Always load with `display=swap` for fast rendering. Pick a distinctive pairing — body + mono at minimum, optionally a display font for the title.

**FORBIDDEN as `--font-body` (AI slop signals):**
- Inter — the single most overused AI default font
- Roboto — generic Android/Google default
- Arial, Helvetica — system defaults with no character
- system-ui alone without a named font — signals zero design intent

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">
```

Define as CSS variables for easy reference:
```css
:root {
  --font-body: 'Outfit', system-ui, sans-serif;
  --font-mono: 'Space Mono', 'SF Mono', Consolas, monospace;
}
```

**Font pairings** (rotate — never use the same pairing twice in a row):

| Body / Headings | Mono / Labels | Feel | Use for |
|---|---|---|---|
| DM Sans | Fira Code | Friendly, developer | Blueprint, technical docs |
| Instrument Serif | JetBrains Mono | Editorial, refined | Plan reviews, decision logs |
| IBM Plex Sans | IBM Plex Mono | Reliable, readable | Architecture diagrams |
| Bricolage Grotesque | Fragment Mono | Bold, characterful | Data tables, dashboards |
| Plus Jakarta Sans | Azeret Mono | Rounded, approachable | Status reports, audits |
| Outfit | Space Mono | Clean geometric, modern | Flowcharts, pipelines |
| Sora | IBM Plex Mono | Technical, precise | ER diagrams, schemas |
| Crimson Pro | Noto Sans Mono | Scholarly, serious | RFC reviews, specs |
| Fraunces | Source Code Pro | Warm, distinctive | Project recaps |
| Geist | Geist Mono | Vercel-inspired, sharp | Modern API docs |
| Red Hat Display | Red Hat Mono | Cohesive family | System overviews |
| Libre Franklin | Inconsolata | Classic, reliable | Data-dense tables |
| Playfair Display | Roboto Mono | Elegant contrast | Executive summaries |

The first 5 pairings are recommended for most use cases. Vary across consecutive diagrams.

### Typography by Content Voice

For prose-heavy pages (documentation, articles, essays), match typography to the content's voice:

| Voice | Fonts | Best For |
|-------|-------|----------|
| **Literary / Thoughtful** | Literata, Lora, Newsreader, Merriweather | Essays, personal posts, long-form articles |
| **Technical / Precise** | IBM Plex Sans + Mono, Geist + Geist Mono, Source family | Documentation, READMEs, API references |
| **Bold / Contemporary** | Bricolage Grotesque, Space Grotesk, DM Sans | Product pages, feature announcements |
| **Minimal / Focused** | Source Serif 4 + Source Sans 3, Karla + Inconsolata | Tutorials, how-tos, focused reading |

**Literata** deserves special mention — it has optical sizing designed specifically for screen reading. Google's answer to Georgia, but modernized.

---

## Chart.js Plugins

Three plugin packages that extend Chart.js with data shapes the core library doesn't handle: time/value grids (heatmap), flow allocations (Sankey), and hierarchical proportions (treemap). All ship via jsDelivr — no build step required.

**Decision guide before reaching for a plugin:**

| Data shape | Use | Instead of |
|---|---|---|
| Correlation matrix, time-of-day grid, activity heatmap | `chartjs-chart-matrix` | A bar-per-row (loses the 2D structure) |
| Fund flows, traffic funnels, user-journey transitions | `chartjs-plugin-sankey` | A stacked bar (loses the flow connection) |
| Codebase size by directory, market share breakdown | `chartjs-chart-treemap` | A pie chart (loses the hierarchy) |

If your data fits a bar/line/pie/doughnut, use Chart.js core directly — plugins add complexity.

---

### Heatmap — `chartjs-chart-matrix`

For 2D grids where both axes are categories and cell color encodes a value: activity calendars, time-of-week grids, correlation matrices, severity heatmaps.

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-chart-matrix@2/dist/chartjs-chart-matrix.min.js"></script>

<div class="chart-container">
  <canvas id="heatmap" width="640" height="280"></canvas>
</div>

<script>
const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
const fontFamily = getComputedStyle(document.documentElement)
  .getPropertyValue('--font-mono').trim() || 'monospace';
const textColor = isDark ? '#94a3b8' : '#475569';

const days  = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`);

const rawData = days.flatMap((day) =>
  hours.map((hour) => ({ x: hour, y: day, v: Math.round(Math.random() * 100) }))
);

// Color scale built around page accent (teal) — swap to match your preset
function cellColor(value) {
  const t = value / 100;
  const r = Math.round(isDark ? 8  + t * 14  : 8  + t * 21);
  const g = Math.round(isDark ? 20 + t * 181 : 185 - t * 110);
  const b = Math.round(isDark ? 42 + t * 156 : 230 - t * 86);
  return `rgba(${r},${g},${b},${0.25 + t * 0.75})`;
}

new Chart(document.getElementById('heatmap'), {
  type: 'matrix',
  data: {
    datasets: [{
      label: 'Activity',
      data: rawData,
      backgroundColor: ctx => cellColor(ctx.dataset.data[ctx.dataIndex]?.v ?? 0),
      borderColor: 'transparent',
      width:  ({ chart }) => (chart.chartArea?.width  / hours.length) - 2,
      height: ({ chart }) => (chart.chartArea?.height / days.length)  - 2,
    }]
  },
  options: {
    responsive: true,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          title: () => '',
          label: ctx => {
            const d = ctx.dataset.data[ctx.dataIndex];
            return `${d.y} ${d.x} — ${d.v} events`;
          },
        }
      }
    },
    scales: {
      x: {
        type: 'category',
        labels: hours,
        ticks: { color: textColor, font: { family: fontFamily, size: 10 }, maxRotation: 0 },
        grid: { display: false },
      },
      y: {
        type: 'category',
        labels: days,
        ticks: { color: textColor, font: { family: fontFamily, size: 11 } },
        grid: { display: false },
        offset: true,
      }
    }
  }
});
</script>
```

**Color scale:** Build around your page's `--accent` token. Zero cells should use the surface color — so the grid reads as "no data" rather than "maximum absence." Replace the inline color math with an interpolation between `var(--surface)` and `var(--accent)` for exact palette fidelity.

---

### Sankey Diagram — `chartjs-plugin-sankey`

For flow diagrams: budget allocations, user funnel drop-offs, traffic source breakdowns, energy flows. Nodes are columns; links are colored bands showing how much flows from source to destination.

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-sankey@0/dist/chartjs-plugin-sankey.min.js"></script>

<div class="chart-container" style="min-height: 320px;">
  <canvas id="sankey" height="320"></canvas>
</div>

<script>
const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
const fontFamily = getComputedStyle(document.documentElement)
  .getPropertyValue('--font-body').trim() || 'system-ui, sans-serif';

const nodeColors = {
  'Direct':    isDark ? '#2c7a7b' : '#0891b2',
  'Search':    isDark ? '#276749' : '#059669',
  'Social':    isDark ? '#975a16' : '#d97706',
  'Landing':   isDark ? '#1e4e7a' : '#0369a1',
  'Pricing':   isDark ? '#4a4e69' : '#6b7280',
  'Sign Up':   isDark ? '#7c3d12' : '#c2410c',
  'Abandoned': isDark ? '#4c1d1d' : '#9f1239',
  'Converted': isDark ? '#14532d' : '#166534',
};

function nodeColor(node) {
  return nodeColors[node.id] ?? (isDark ? '#334155' : '#cbd5e1');
}

new Chart(document.getElementById('sankey'), {
  type: 'sankey',
  data: {
    datasets: [{
      label: 'Traffic Funnel',
      data: [
        { from: 'Direct',  to: 'Landing',   flow: 1200 },
        { from: 'Search',  to: 'Landing',   flow: 1800 },
        { from: 'Social',  to: 'Landing',   flow: 600  },
        { from: 'Landing', to: 'Pricing',   flow: 1400 },
        { from: 'Landing', to: 'Abandoned', flow: 2200 },
        { from: 'Pricing', to: 'Sign Up',   flow: 980  },
        { from: 'Pricing', to: 'Abandoned', flow: 420  },
        { from: 'Sign Up', to: 'Converted', flow: 740  },
        { from: 'Sign Up', to: 'Abandoned', flow: 240  },
      ],
      colorFrom: c => nodeColor(c.dataset.data[c.dataIndex].from),
      colorTo:   c => nodeColor(c.dataset.data[c.dataIndex].to),
      colorMode: 'gradient',
      borderWidth: 0,
      nodePadding: 16,
      nodeWidth:   14,
    }]
  },
  options: {
    responsive: true,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: ctx => {
            const d = ctx.dataset.data[ctx.dataIndex];
            return `${d.from} → ${d.to}: ${d.flow} visitors`;
          },
        }
      }
    }
  }
});
</script>
```

**`colorMode: 'gradient'`** — each link fades from source color to destination color, reinforcing flow direction visually.

**Data shape:** `{ from: string, to: string, flow: number }`. Nodes are inferred automatically — you don't declare them separately. The plugin calculates column positions from the DAG structure.

**Limit:** Fewer than ~20 nodes and ~30 links. Beyond that, overlapping labels make it unreadable — aggregate into broader categories.

---

### Treemap — `chartjs-chart-treemap`

For hierarchical proportions: codebase size by directory, budget by department, market share by segment. Nested rectangles where area encodes magnitude and color encodes group.

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-chart-treemap@3/dist/chartjs-chart-treemap.min.js"></script>

<div class="chart-container" style="min-height: 340px;">
  <canvas id="treemap" height="340"></canvas>
</div>

<script>
const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
const fontFamily = getComputedStyle(document.documentElement)
  .getPropertyValue('--font-body').trim() || 'system-ui, sans-serif';

const groupColors = {
  'frontend': isDark ? '#1e4e7a' : '#bae6fd',
  'backend':  isDark ? '#276749' : '#bbf7d0',
  'infra':    isDark ? '#975a16' : '#fde68a',
  'tests':    isDark ? '#4a1d7a' : '#e9d5ff',
};

const rawData = [
  { group: 'frontend', label: 'components',  value: 42000 },
  { group: 'frontend', label: 'pages',       value: 18000 },
  { group: 'frontend', label: 'hooks',       value: 9000  },
  { group: 'backend',  label: 'api',         value: 31000 },
  { group: 'backend',  label: 'db',          value: 14000 },
  { group: 'backend',  label: 'services',    value: 22000 },
  { group: 'infra',    label: 'terraform',   value: 8000  },
  { group: 'infra',    label: 'docker',      value: 5000  },
  { group: 'tests',    label: 'unit',        value: 27000 },
  { group: 'tests',    label: 'integration', value: 12000 },
];

new Chart(document.getElementById('treemap'), {
  type: 'treemap',
  data: {
    datasets: [{
      label: 'Codebase Size',
      tree: rawData,
      key: 'value',
      groups: ['group', 'label'],
      spacing: 1,
      backgroundColor: ctx => {
        const item = ctx.dataset.data[ctx.dataIndex];
        if (!item) return 'transparent';
        return groupColors[item.g] ?? (isDark ? '#334155' : '#e2e8f0');
      },
      borderColor: isDark ? 'rgba(255,255,255,0.12)' : 'rgba(0,0,0,0.08)',
      borderWidth: 1,
      labels: {
        display: true,
        formatter: ctx => {
          const item = ctx.dataset.data[ctx.dataIndex];
          if (!item) return '';
          return item.l ? [item.l, `${Math.round(item.v / 1000)}K`] : item.g;
        },
        color: isDark ? '#f1f5f9' : '#1e293b',
        font: { family: fontFamily, size: 12 },
        overflow: 'hidden',
      }
    }]
  },
  options: {
    responsive: true,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          title: ctx => {
            const d = ctx[0]?.dataset.data[ctx[0]?.dataIndex];
            return d ? `${d.g}${d.l ? ' / ' + d.l : ''}` : '';
          },
          label: ctx => {
            const d = ctx.dataset.data[ctx.dataIndex];
            return d ? `${(d.v / 1000).toFixed(1)}K lines` : '';
          },
        }
      }
    }
  }
});
</script>
```

**`groups: ['group', 'label']`** — first entry is the parent grouping, second is the leaf label. Cells of the same group are placed adjacent and share a color family. The squarified treemap layout is computed automatically.

**Label overflow:** Small cells have labels clipped automatically with `overflow: 'hidden'`. Micro-cells are still hoverable via tooltip.

**When to prefer over a pie chart:** More than ~6 segments, or when the data has a natural two-level hierarchy (group → item). A pie chart can't show both levels simultaneously.