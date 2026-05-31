# Interactive Patterns

Client-side interactivity patterns for copy-to-clipboard, sortable tables, search/filter, print support, and Mermaid error handling. No build step, no external JS libraries beyond what's already in use.

## Copy-to-Clipboard Buttons

Add to code blocks in API docs, code tours, and implementation plans. Uses the Clipboard API with a brief success-state transition.

```css
.code-file {
  position: relative;
}

.copy-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  background: var(--surface-elevated, var(--surface));
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 4px 10px;
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 500;
  color: var(--text-dim);
  cursor: pointer;
  z-index: 5;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
}

.copy-btn:hover {
  background: var(--border);
  color: var(--text);
}

.copy-btn.copied {
  color: var(--green, #059669);
  border-color: var(--green, #059669);
}
```

```html
<div class="code-file">
  <div class="code-file__header">
    <span>curl example</span>
    <button class="copy-btn" data-copy>Copy</button>
  </div>
  <pre class="code-file__body"><code>curl -X POST https://api.example.com/v1/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "hello world"}'</code></pre>
</div>
```

```javascript
// Wire all copy buttons at page load — works for any number of blocks
document.querySelectorAll('[data-copy]').forEach(btn => {
  btn.addEventListener('click', async () => {
    const block = btn.closest('.code-file, .code-block-wrap');
    const text = block?.querySelector('code, pre')?.textContent ?? '';
    try {
      await navigator.clipboard.writeText(text.trim());
      btn.textContent = 'Copied!';
      btn.classList.add('copied');
    } catch {
      btn.textContent = 'Failed';
    }
    setTimeout(() => {
      btn.textContent = 'Copy';
      btn.classList.remove('copied');
    }, 2000);
  });
});
```

**Placement:** Position `copy-btn` inside the `.code-file` header (alongside the filename label) rather than floating over the code body — avoids obscuring the first line of code.

**Fallback:** If `navigator.clipboard` is unavailable (HTTP, old browser), the catch block shows "Failed" briefly. No silent errors.

---

## Sortable Tables

Click column headers to sort ascending/descending. Works on any `.data-table`. No library required.

```css
/* Mark sortable columns */
.data-table th[data-sort] {
  cursor: pointer;
  user-select: none;
  padding-right: 28px;  /* room for the arrow indicator */
  position: relative;
}

/* Default: unsorted indicator */
.data-table th[data-sort]::after {
  content: '\21D5';  /* ⇕ up-down arrow */
  position: absolute;
  right: 10px;
  color: var(--border-bright);
  font-size: 11px;
}

/* Active sort state */
.data-table th[data-sort="asc"]::after  { content: '\2191'; color: var(--accent); }  /* ↑ */
.data-table th[data-sort="desc"]::after { content: '\2193'; color: var(--accent); }  /* ↓ */
```

```html
<!-- Add data-sort and data-col to any th you want sortable -->
<thead>
  <tr>
    <th data-sort data-col="0">Name</th>
    <th data-sort data-col="1" class="num">Requests</th>
    <th data-sort data-col="2" class="num">Latency</th>
    <th>Status</th>  <!-- no data-sort = not sortable -->
  </tr>
</thead>
```

```javascript
function initSortableTable(table) {
  const headers = table.querySelectorAll('th[data-sort]');
  let lastCol = -1;
  let ascending = true;

  headers.forEach(th => {
    th.addEventListener('click', () => {
      const col = parseInt(th.dataset.col, 10);
      ascending = (col === lastCol) ? !ascending : true;
      lastCol = col;

      // Update header indicators
      headers.forEach(h => delete h.dataset.sort);
      th.dataset.sort = ascending ? 'asc' : 'desc';

      // Sort rows
      const tbody = table.querySelector('tbody');
      const rows = Array.from(tbody.querySelectorAll('tr'));
      rows.sort((a, b) => {
        const av = a.cells[col]?.textContent.trim() ?? '';
        const bv = b.cells[col]?.textContent.trim() ?? '';
        const an = parseFloat(av.replace(/[^0-9.-]/g, ''));
        const bn = parseFloat(bv.replace(/[^0-9.-]/g, ''));
        const cmp = (!isNaN(an) && !isNaN(bn))
          ? an - bn
          : av.localeCompare(bv, undefined, { sensitivity: 'base' });
        return ascending ? cmp : -cmp;
      });
      rows.forEach(r => tbody.appendChild(r));
    });
  });
}

document.querySelectorAll('.data-table').forEach(initSortableTable);
```

**Note:** The `data-sort` attribute on `<th>` serves double duty — it marks the column as sortable AND carries the current sort state (`asc`/`desc`/unset). Starting with no value means unsorted (shows ⇕). Clicking once sets it to `asc`, clicking again flips to `desc`.

---

## Table Search / Filter

A search input that hides rows not matching the query. Substring match across all visible cell text.

```css
.table-filter {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.table-filter__input {
  padding: 7px 12px;
  max-width: 280px;
  width: 100%;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--text);
  outline: none;
  transition: border-color 0.15s;
}

.table-filter__input:focus {
  border-color: var(--accent);
}

.table-filter__count {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--text-dim);
  white-space: nowrap;
}
```

```html
<div class="table-filter">
  <input
    class="table-filter__input"
    type="search"
    placeholder="Filter rows…"
    aria-label="Filter table rows"
    data-filter-target="endpoints-table"
  >
  <span class="table-filter__count" id="endpoints-count"></span>
</div>

<table id="endpoints-table" class="data-table">...</table>
```

```javascript
function initTableFilter(input) {
  const tableId = input.dataset.filterTarget;
  const table = document.getElementById(tableId);
  if (!table) return;

  const rows = Array.from(table.querySelectorAll('tbody tr'));
  const countEl = document.querySelector(
    `[aria-label="Filter table rows"] ~ .table-filter__count, #${tableId}-count`
  );

  function updateCount(visible) {
    if (!countEl) return;
    const q = input.value.trim();
    countEl.textContent = q ? `${visible} of ${rows.length}` : `${rows.length} rows`;
  }

  input.addEventListener('input', () => {
    const q = input.value.toLowerCase().trim();
    let visible = 0;
    rows.forEach(row => {
      const match = !q || row.textContent.toLowerCase().includes(q);
      row.style.display = match ? '' : 'none';
      if (match) visible++;
    });
    updateCount(visible);
  });

  updateCount(rows.length);
}

document.querySelectorAll('[data-filter-target]').forEach(initTableFilter);
```

**Combining sort + filter:** Both work independently on the same table. Sort reorders DOM rows; filter hides them. When the user clears the filter, hidden rows reappear in whatever sort order is currently active.

---

## Print Styles

Support Ctrl+P / browser print for saving diagrams as PDF. Include in any page that might be shared in document form.

```css
@media print {
  /* Hide interactive chrome */
  .zoom-controls,
  .copy-btn,
  .theme-toggle,
  nav,
  .nav-sidebar,
  .table-filter { display: none !important; }

  /* Expand all collapsible sections */
  details { display: block !important; }
  details > summary + * { display: block !important; }

  /* Page margins */
  @page { margin: 1.5cm; }

  /* Force white background for ink savings */
  body { background: white !important; color: black !important; font-size: 11pt; }

  /* Keep cards and table rows together */
  .ve-card, .timeline-entry, tr { break-inside: avoid; }

  /* Repeat table header on each page */
  thead { display: table-header-group; }

  /* Show link URLs inline */
  a[href]::after    { content: ' (' attr(href) ')'; font-size: 9pt; color: #555; }
  a[href^="#"]::after { content: none; }  /* skip internal anchors */
}
```

**Usage:** No JavaScript required. Users Ctrl+P → Save as PDF. The `@media print` block handles hiding controls and fixing backgrounds automatically.

**Mermaid diagrams in print:** The SVGs render as vectors and print cleanly. The zoom/pan controls are hidden by the rule above. If a diagram is very wide, it will scale to fit the page width via the browser's print engine.

---

## Mermaid Loading State and Error Fallback

Two problems to solve: (1) a brief blank flash while Mermaid initializes, (2) a broken diagram leaving a blank space with a console error the user never sees.

### Loading Skeleton

Show a shimmer placeholder while the async render runs. Hide it as soon as the SVG is ready.

```css
.diagram-skeleton {
  width: 100%;
  height: 300px;
  border-radius: 8px;
  background: linear-gradient(
    90deg,
    var(--border)          0%,
    var(--surface-elevated, var(--surface)) 40%,
    var(--border)          80%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s linear infinite;
}

@keyframes shimmer {
  from { background-position: 200% 0; }
  to   { background-position: -200% 0; }
}

@media (prefers-reduced-motion: reduce) {
  .diagram-skeleton { animation: none; }
}
```

```html
<section class="diagram-shell">
  <!-- Shown while rendering, removed on success -->
  <div class="diagram-skeleton"></div>

  <!-- Hidden until render succeeds -->
  <div class="mermaid-wrap" style="display:none;">
    <div class="zoom-controls"><!-- … --></div>
    <div class="mermaid-viewport">
      <div class="mermaid mermaid-canvas"></div>
    </div>
  </div>

  <script type="text/plain" class="diagram-source">
    graph TD
      A --> B
  </script>
</section>
```

In the `render()` function inside `initDiagram(shell)` (see `css-patterns.md` full pattern):

```javascript
async function render() {
  const skeleton = shell.querySelector('.diagram-skeleton');
  try {
    const { svg } = await mermaid.render(id, code);
    canvas.innerHTML = svg;
    skeleton?.remove();
    wrap.style.display = '';
    // … readSvgNaturalSize, fitDiagram, wire controls
  } catch (err) {
    showError(err);
  }
}
```

### Error Fallback

When Mermaid fails to parse, show the source code as a formatted code block. A syntax error in one diagram must not blank out the rest of the page.

```css
.diagram-error {
  border: 1px solid var(--red-dim, rgba(239,68,68,0.2));
  border-radius: 10px;
  overflow: hidden;
}

.diagram-error__header {
  padding: 9px 16px;
  background: var(--red-dim, rgba(239,68,68,0.08));
  border-bottom: 1px solid var(--red-dim, rgba(239,68,68,0.2));
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--red, #ef4444);
}

.diagram-error__source {
  font-family: var(--font-mono);
  font-size: 12px;
  line-height: 1.55;
  padding: 14px 16px;
  white-space: pre-wrap;
  color: var(--text-dim);
  max-height: 280px;
  overflow-y: auto;
}
```

```javascript
function showError(err) {
  const skeleton = shell.querySelector('.diagram-skeleton');
  skeleton?.remove();

  const fallback = document.createElement('div');
  fallback.className = 'diagram-error';
  fallback.innerHTML = `
    <div class="diagram-error__header">
      Diagram failed to render: ${(err.message ?? 'Syntax error').replace(/</g, '&lt;')}
    </div>
    <pre class="diagram-error__source">${code.replace(/</g, '&lt;')}</pre>
  `;
  // Insert before the (still-hidden) wrap so layout stays intact
  shell.insertBefore(fallback, wrap);
  // Don't rethrow — let the rest of the page render normally
}
```

**Why not throw?** If `initDiagram` lets the error propagate, an unhandled rejection in one diagram can silence the other `initDiagram` calls that haven't run yet. Catching and displaying locally keeps every other diagram functional.

---

## Export to PNG / SVG

Two export paths: (1) Mermaid SVG → download directly as `.svg` (pure DOM, no library); (2) general DOM screenshot via `html-to-image` CDN (optional fallback for non-SVG sections). Add export buttons to any diagram where the user might want to share or embed the output.

### SVG Export (Mermaid diagrams)

```css
.export-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 12px;
  background: var(--surface-elevated, var(--surface));
  border: 1px solid var(--border-bright);
  border-radius: 6px;
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 500;
  color: var(--text-dim);
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}

.export-btn:hover {
  background: var(--accent-dim);
  color: var(--accent);
  border-color: var(--accent);
}

.export-btn svg {
  width: 13px;
  height: 13px;
  stroke: currentColor;
  fill: none;
}
```

```html
<!-- Place inside .zoom-controls alongside the existing buttons -->
<button class="export-btn" data-export-svg aria-label="Export diagram as SVG">
  <svg viewBox="0 0 16 16" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M8 2v8m0 0l-3-3m3 3l3-3M2 12v1a1 1 0 001 1h10a1 1 0 001-1v-1"/>
  </svg>
  SVG
</button>
```

```javascript
// Wire inside initDiagram(shell), after SVG renders:
shell.querySelector('[data-export-svg]')?.addEventListener('click', () => {
  const svgEl = canvas.querySelector('svg');
  if (!svgEl) return;

  // Clone SVG, set explicit dimensions
  const clone = svgEl.cloneNode(true);
  const { width, height } = svgEl.getBoundingClientRect();
  clone.setAttribute('width', Math.ceil(width));
  clone.setAttribute('height', Math.ceil(height));

  // Inline @font-face rules so the downloaded SVG is self-contained
  const fontFace = Array.from(document.styleSheets)
    .flatMap(s => { try { return Array.from(s.cssRules); } catch { return []; } })
    .filter(r => r instanceof CSSFontFaceRule)
    .map(r => r.cssText)
    .join('\n');
  if (fontFace) {
    const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
    const style = document.createElementNS('http://www.w3.org/2000/svg', 'style');
    style.textContent = fontFace;
    defs.appendChild(style);
    clone.insertBefore(defs, clone.firstChild);
  }

  const blob = new Blob([clone.outerHTML], { type: 'image/svg+xml;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `diagram-${Date.now()}.svg`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
});
```

### PNG Export (general DOM sections)

For non-SVG sections (card grids, dashboards), use `html-to-image` as an optional CDN load — only fetched when the user clicks Export:

```javascript
async function exportSectionAsPng(section, filename = `export-${Date.now()}.png`) {
  if (!window.htmlToImage) {
    await loadLibrary('https://cdn.jsdelivr.net/npm/html-to-image@1/dist/html-to-image.min.js');
  }
  const dataUrl = await htmlToImage.toPng(section, { pixelRatio: 2 });
  const a = document.createElement('a');
  a.href = dataUrl;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
}

// Wire a button:
document.querySelector('[data-export-png]')?.addEventListener('click', () => {
  exportSectionAsPng(document.querySelector('.export-target'));
});
```

**Note on `loadLibrary`:** See the "Lazy-Load CDN Libraries" pattern below for the full implementation.

**When to use each path:**
- Mermaid diagrams → SVG export (pure DOM, no library, vectors stay crisp at any size)
- CSS Grid cards, tables, Chart.js canvases → PNG export via `html-to-image` (captures what SVG export can't)
- Never include `html-to-image` at page load — it's ~80 KB and only useful if the user clicks Export

---

## Voice Narration (Web Speech API)

Reads section content aloud using the browser's built-in `speechSynthesis`. No library required. Highlights the section being narrated with `.is-narrating`. Respects `prefers-reduced-motion` — skips the highlight animation but still narrates.

```css
.narration-controls {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
}

.narrate-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: var(--surface);
  border: 1px solid var(--border-bright);
  border-radius: 20px;
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--text-dim);
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s, color 0.15s;
}

.narrate-btn:hover  { background: var(--accent-dim); color: var(--accent); border-color: var(--accent); }
.narrate-btn.active { background: var(--accent); color: #fff; border-color: var(--accent); }

.is-narrating {
  outline: 2px solid var(--accent);
  outline-offset: 6px;
  border-radius: 4px;
  transition: outline-color 0.3s;
}

@media (prefers-reduced-motion: reduce) {
  .is-narrating { transition: none; }
}
```

```html
<div class="narration-controls">
  <button class="narrate-btn" id="narrate-play"  aria-label="Start narration">▶ Play</button>
  <button class="narrate-btn" id="narrate-pause" aria-label="Pause narration" disabled>⏸ Pause</button>
  <button class="narrate-btn" id="narrate-stop"  aria-label="Stop narration"  disabled>⏹ Stop</button>
</div>

<!-- Mark sections with explicit narration text or rely on textContent -->
<section data-narrate="Introduction: this system handles authentication...">
  <!-- card content -->
</section>
```

```javascript
(function () {
  if (!('speechSynthesis' in window)) return;

  const synth = window.speechSynthesis;
  const sections = Array.from(document.querySelectorAll('[data-narrate]'));
  const playBtn  = document.getElementById('narrate-play');
  const pauseBtn = document.getElementById('narrate-pause');
  const stopBtn  = document.getElementById('narrate-stop');

  if (!playBtn || sections.length === 0) return;

  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let currentSection = null;

  function highlight(section) {
    if (currentSection) currentSection.classList.remove('is-narrating');
    currentSection = section;
    if (section && !prefersReduced) section.classList.add('is-narrating');
  }

  function resetButtons() {
    playBtn.classList.remove('active');
    pauseBtn.disabled = true;
    stopBtn.disabled = true;
  }

  function narrateAll() {
    synth.cancel();
    let idx = 0;

    function speakNext() {
      if (idx >= sections.length) { highlight(null); resetButtons(); return; }
      const section = sections[idx++];
      const text = section.dataset.narrate || section.textContent.replace(/\s+/g, ' ').trim();
      highlight(section);
      const utt = new SpeechSynthesisUtterance(text);
      utt.rate = 0.95;
      utt.onend = speakNext;
      utt.onerror = speakNext;
      synth.speak(utt);
    }
    speakNext();
  }

  playBtn.addEventListener('click', () => {
    if (synth.paused) {
      synth.resume();
      playBtn.classList.remove('active');
      pauseBtn.disabled = false;
    } else {
      narrateAll();
      playBtn.classList.add('active');
      pauseBtn.disabled = false;
      stopBtn.disabled = false;
    }
  });

  pauseBtn.addEventListener('click', () => {
    synth.pause();
    playBtn.classList.remove('active');
    pauseBtn.disabled = true;
  });

  stopBtn.addEventListener('click', () => {
    synth.cancel();
    highlight(null);
    resetButtons();
  });
}());
```

**`data-narrate` attribute:** Provide the text to speak explicitly for precise narration, or omit it to fall back to `section.textContent` (which includes nested code — usually too noisy for code-heavy sections).

**Browser support:** Chrome, Edge, Safari 14+, Firefox 114+. The guard at the top silently skips unsupported browsers.

---

## Lazy-Load CDN Libraries

Load CDN scripts on demand rather than at page load. Use when a heavy library (Chart.js, D3, html-to-image) is only needed in sections that some users never scroll to, or when you want to reduce blank-page time.

```javascript
// Promise-based script loader with Map-based deduplication.
// Multiple calls with the same src share one Promise — no duplicate network requests.
const _libraryCache = new Map();

function loadLibrary(src) {
  if (_libraryCache.has(src)) return _libraryCache.get(src);
  const promise = new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = src;
    script.onload  = resolve;
    script.onerror = () => reject(new Error(`Failed to load: ${src}`));
    document.head.appendChild(script);
  });
  _libraryCache.set(src, promise);
  return promise;
}
```

### Trigger on Viewport Entry (IntersectionObserver)

Load and initialize a library only when a section scrolls into view:

```javascript
const lazyEls = document.querySelectorAll('[data-lazy-lib]');

const obs = new IntersectionObserver((entries) => {
  entries.forEach(async entry => {
    if (!entry.isIntersecting) return;
    obs.unobserve(entry.target);  // initialize once

    const libSrc = entry.target.dataset.lazyLib;
    try {
      await loadLibrary(libSrc);
      const initFn = entry.target.dataset.lazyInit;
      if (initFn && typeof window[initFn] === 'function') {
        window[initFn](entry.target);
      }
    } catch (err) {
      console.warn('Lazy load failed for', libSrc, err);
    }
  });
}, { rootMargin: '200px' });  // start loading 200px before visible

lazyEls.forEach(el => obs.observe(el));
```

```html
<!-- Chart.js section — loads chart.js only when this section nears the viewport -->
<section
  data-lazy-lib="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"
  data-lazy-init="initMyChart"
>
  <canvas id="lazy-chart"></canvas>
</section>

<script>
function initMyChart(section) {
  const canvas = section.querySelector('canvas');
  new Chart(canvas, { type: 'bar', data: { /* ... */ } });
}
</script>
```

### ESM Libraries (Mermaid, D3)

The `loadLibrary` pattern works for UMD/CommonJS scripts that set a global. For ES module scripts, use `import()` instead:

```javascript
async function initMermaidSection(section) {
  const { default: mermaid } = await import(
    'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs'
  );
  mermaid.initialize({ startOnLoad: false, theme: 'base' });
  await mermaid.run({ nodes: section.querySelectorAll('.mermaid') });
}
```

**`rootMargin: '200px'`** loads 200px before the section enters the viewport, giving the script time to download before the user sees the placeholder. Adjust upward on slow connections.

**Limitation:** `loadLibrary` is for UMD/CJS globals only. Mermaid, D3, and any pure-ESM package require `import()`.

---

## In-Page Search Overlay

Triggered by Cmd/Ctrl+K (or `/` when not in an input). Does **not** conflict with the browser's native Ctrl+F. Highlights matches across `.ve-card`, table cells, and headings with arrow-key navigation.

```css
.search-overlay {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  z-index: 1000;
  align-items: flex-start;
  justify-content: center;
  padding-top: 10vh;
}

.search-overlay.is-open { display: flex; }

.search-box {
  width: min(560px, 90vw);
  background: var(--surface-elevated, var(--surface));
  border: 1px solid var(--border-bright);
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.35);
}

.search-box__input {
  display: block;
  width: 100%;
  padding: 14px 18px;
  border: none;
  background: transparent;
  font-family: var(--font-body);
  font-size: 15px;
  color: var(--text);
  outline: none;
  box-sizing: border-box;
}

.search-box__meta {
  padding: 6px 16px 10px;
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--text-faint);
  border-top: 1px solid var(--border);
}

mark.search-match {
  background: var(--tertiary-dim, rgba(217, 119, 6, 0.20));
  color: inherit;
  border-radius: 2px;
  padding: 0 1px;
}

mark.search-match.is-active {
  background: var(--tertiary, #d97706);
  color: #fff;
}
```

```html
<div class="search-overlay" id="search-overlay" role="dialog" aria-modal="true" aria-label="In-page search">
  <div class="search-box">
    <input
      class="search-box__input"
      type="search"
      id="search-input"
      placeholder="Search this page…"
      aria-label="Search"
      autocomplete="off"
      spellcheck="false"
    >
    <div class="search-box__meta" id="search-meta">⌘K or / to open · Esc to close · ↑↓ to navigate</div>
  </div>
</div>
```

```javascript
(function () {
  const overlay = document.getElementById('search-overlay');
  const input   = document.getElementById('search-input');
  const meta    = document.getElementById('search-meta');
  if (!overlay || !input) return;

  const SEARCH_SELECTORS = '.ve-card, td, th, h1, h2, h3, h4, p, li';
  let matches = [];
  let cursor  = -1;

  function open() {
    overlay.classList.add('is-open');
    input.value = '';
    input.focus();
    clearMarks();
    meta.textContent = '⌘K or / to open · Esc to close · ↑↓ to navigate';
  }

  function close() {
    overlay.classList.remove('is-open');
    clearMarks();
    input.blur();
  }

  function clearMarks() {
    document.querySelectorAll('mark.search-match').forEach(m => {
      const parent = m.parentNode;
      parent.replaceChild(document.createTextNode(m.textContent), m);
      parent.normalize();
    });
    matches = [];
    cursor = -1;
  }

  function highlightAll(query) {
    clearMarks();
    if (!query || query.length < 2) return;
    const q = query.toLowerCase();

    Array.from(document.querySelectorAll(SEARCH_SELECTORS)).forEach(el => {
      if (overlay.contains(el)) return;
      const tw = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
      const textNodes = [];
      let n;
      while ((n = tw.nextNode())) textNodes.push(n);

      textNodes.forEach(tn => {
        const idx = tn.textContent.toLowerCase().indexOf(q);
        if (idx === -1) return;

        const mark = document.createElement('mark');
        mark.className = 'search-match';
        mark.textContent = tn.textContent.slice(idx, idx + query.length);

        const frag = document.createDocumentFragment();
        if (idx > 0) frag.appendChild(document.createTextNode(tn.textContent.slice(0, idx)));
        frag.appendChild(mark);
        const after = tn.textContent.slice(idx + query.length);
        if (after) frag.appendChild(document.createTextNode(after));

        tn.parentNode.replaceChild(frag, tn);
        matches.push(mark);
      });
    });

    meta.textContent = matches.length
      ? `${matches.length} match${matches.length === 1 ? '' : 'es'} · ↑↓ to navigate`
      : 'No matches';
  }

  function navigate(dir) {
    if (matches.length === 0) return;
    if (cursor >= 0) matches[cursor].classList.remove('is-active');
    cursor = (cursor + dir + matches.length) % matches.length;
    matches[cursor].classList.add('is-active');
    matches[cursor].scrollIntoView({ behavior: 'smooth', block: 'center' });
    meta.textContent = `Match ${cursor + 1} of ${matches.length}`;
  }

  document.addEventListener('keydown', e => {
    const inInput = document.activeElement === input;
    const isOpen  = overlay.classList.contains('is-open');

    if ((e.key === 'k' && (e.metaKey || e.ctrlKey)) || (e.key === '/' && !inInput && !isOpen)) {
      e.preventDefault();
      open();
    } else if (e.key === 'Escape' && isOpen) {
      close();
    } else if (e.key === 'ArrowDown' && inInput) {
      e.preventDefault(); navigate(+1);
    } else if (e.key === 'ArrowUp' && inInput) {
      e.preventDefault(); navigate(-1);
    } else if (e.key === 'Enter' && inInput) {
      navigate(+1);
    }
  });

  overlay.addEventListener('click', e => { if (e.target === overlay) close(); });
  input.addEventListener('input', () => highlightAll(input.value.trim()));
}());
```

**Why Cmd+K, not Ctrl+F?** `Ctrl+F` / `Cmd+F` triggers the browser's native find bar — intercepting it is hostile to users who rely on it. `Cmd+K` is the common "quick open" shortcut. The `/` shortcut fires only when the user isn't in an input.

**Match limit:** This implementation marks the first occurrence of the query per text node. For pages with many repeated terms across distinct elements, all get marked. If you need multi-match highlighting within a single long text node, split the node iteratively before wrapping.

---

## Runtime Theme Toggle

Use on any page that ships with a dark-first (or light-first) default and should let the viewer override it. Especially useful for pages embedded in documentation sites where the surrounding context may be either theme.

### CSS

```css
:root[data-theme="light"] {
  --bg: #f8f9fb;
  --surface: #ffffff;
  --border: rgba(0, 0, 0, 0.08);
  --text: #1a1a2e;
  --text-dim: #5c6880;
}

.theme-toggle {
  position: fixed;
  top: 16px;
  right: 16px;
  width: 36px;
  height: 36px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  cursor: pointer;
  display: grid;
  place-items: center;
  transition: color 0.15s, background 0.15s, border-color 0.15s;
  z-index: 100;
}

.theme-toggle::before {
  content: '\2600';  /* ☀ sun */
  font-size: 16px;
}

:root[data-theme="light"] .theme-toggle::before {
  content: '\263E';  /* ☾ moon */
}
```

### HTML

```html
<button class="theme-toggle" id="theme-toggle" type="button" aria-label="Toggle theme"></button>
```

### JS (~25 lines, IIFE)

```javascript
(function () {
  const root = document.documentElement;
  const btn  = document.getElementById('theme-toggle');
  const STORE = 've-theme';

  function apply(theme) {
    root.dataset.theme = theme;
    btn.setAttribute('aria-label', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
  }

  const stored = localStorage.getItem(STORE);
  const osLight = window.matchMedia('(prefers-color-scheme: light)').matches;
  apply(stored ?? (osLight ? 'light' : 'dark'));

  btn.addEventListener('click', () => {
    const next = root.dataset.theme === 'dark' ? 'light' : 'dark';
    apply(next);
    localStorage.setItem(STORE, next);
  });
}());
```

### Notes

- **Light-first pages:** Use `:root[data-theme="dark"]` and flip the initial detection logic.
- **Smooth transitions:** Apply `transition` to individual component properties rather than `:root` — a root transition causes a full-page flash on toggle.
- **Mermaid caveat:** Mermaid SVGs are rendered once at load time and do not re-render on theme toggle. Accept the static SVG in its initial theme, or regenerate the page. See "Dark Mode Handling" in `libraries.md`.
- **Chart.js:** Use a `MutationObserver` on `document.documentElement` watching the `data-theme` attribute to re-render charts when the theme changes.