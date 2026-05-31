# Guided Walkthrough Mode

Steps a viewer through sections one at a time — dims non-active sections, highlights the current one, and provides a fixed bottom control bar with Prev / Next / Close controls.

## When to use

- Long single-page explanations (architectures, deep-dives, onboarding flows) where you want to guide a first-time viewer through the material in a prescribed order
- Any page where combining voice narration (pattern 6 in this file) with step navigation adds value — the two integrate directly (see Notes)
- **Skip for** dashboards and data tables, which are meant to be scanned freely, not stepped through

The walkthrough attaches to elements marked with the `.ve-section` class (the standard section class from `./css-patterns.md`). Each section can optionally carry a `data-walkthrough-title` attribute; otherwise the pattern reads the first `<h2>` or `<h3>` text as the step label.

---

## CSS

Add to your page `<style>` block.

```css
/* ---- Walkthrough bar ---- */
.walkthrough-bar {
  position: fixed;
  bottom: 0; left: 0; right: 0;
  z-index: 200;
  background: var(--surface);
  border-top: 1px solid var(--border-bright);
  padding: 14px 24px;
  display: none;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
}
.walkthrough-bar.is-open { display: flex; }

.walkthrough-bar__title {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--text-dim);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
  min-width: 0;
}
.walkthrough-bar__title strong { color: var(--text); }

.walkthrough-bar__controls { display: flex; gap: 8px; flex-shrink: 0; }

.walkthrough-bar__btn {
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 500;
  border: 1px solid var(--border-bright);
  border-radius: 6px;
  padding: 6px 14px;
  background: var(--surface);
  color: var(--text);
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.15s;
}
.walkthrough-bar__btn:hover { background: var(--border); }
.walkthrough-bar__btn--primary {
  background: var(--accent);
  border-color: var(--accent);
  color: #fff;
}
.walkthrough-bar__btn--primary:hover { opacity: 0.88; }

/* ---- Section dim/highlight ---- */
.walkthrough-mode .ve-section {
  opacity: 0.18;
  filter: blur(1px);
  pointer-events: none;
  transition: opacity 0.35s ease, filter 0.35s ease;
}

.walkthrough-mode .ve-section.walkthrough-active {
  opacity: 1;
  filter: none;
  pointer-events: auto;
}

/* Respect prefers-reduced-motion: disable blur/fade, keep scroll + step counter */
@media (prefers-reduced-motion: reduce) {
  .walkthrough-mode .ve-section,
  .walkthrough-mode .ve-section.walkthrough-active {
    opacity: 1 !important;
    filter: none !important;
    transition: none !important;
  }
}
```

---

## HTML

Place the `<div class="walkthrough-bar">` once at the end of `<body>`. Place the start button wherever suits the page — hero section, nav bar, or a floating corner badge.

```html
<!-- Start button — place in nav, hero card, or a floating badge -->
<button class="walkthrough-start-btn" onclick="startWalkthrough()">
  Walk through
</button>

<!-- Fixed bottom bar — place once at end of <body> -->
<div class="walkthrough-bar" id="walkthrough-bar"
     role="navigation" aria-label="Guided walkthrough controls">
  <span class="walkthrough-bar__title" id="walkthrough-title">
    Step <strong id="walkthrough-step">1</strong>
    of <span id="walkthrough-total">&mdash;</span>
    &nbsp;&mdash;&nbsp;<span id="walkthrough-section-title"></span>
  </span>
  <div class="walkthrough-bar__controls">
    <button class="walkthrough-bar__btn"
            onclick="walkPrev()" id="walkthrough-prev"
            aria-label="Previous section">&larr; Prev</button>
    <button class="walkthrough-bar__btn walkthrough-bar__btn--primary"
            onclick="walkNext()" id="walkthrough-next"
            aria-label="Next section">Next &rarr;</button>
    <button class="walkthrough-bar__btn"
            onclick="stopWalkthrough()"
            aria-label="Exit walkthrough">Close</button>
  </div>
</div>

<!-- Mark each section: .ve-section + optional data-walkthrough-title -->
<section class="ve-section" id="overview" data-walkthrough-title="Overview">
  <h2>Overview</h2>
  <!-- ... -->
</section>

<section class="ve-section" id="architecture" data-walkthrough-title="Architecture">
  <h2>Architecture</h2>
  <!-- ... -->
</section>
```

---

## JS

Drop this `<script>` block near the end of `<body>`, after the walkthrough bar HTML.

```javascript
(function () {
  'use strict';

  let sections = [];
  let current  = 0;

  const bar      = document.getElementById('walkthrough-bar');
  const stepEl   = document.getElementById('walkthrough-step');
  const totalEl  = document.getElementById('walkthrough-total');
  const titleEl  = document.getElementById('walkthrough-section-title');
  const prevBtn  = document.getElementById('walkthrough-prev');
  const nextBtn  = document.getElementById('walkthrough-next');

  function getSectionTitle(section) {
    if (section.dataset.walkthroughTitle) return section.dataset.walkthroughTitle;
    const h = section.querySelector('h2, h3');
    return h ? h.textContent.trim() : '';
  }

  function showStep(index) {
    sections.forEach((s, i) => s.classList.toggle('walkthrough-active', i === index));
    current = index;

    stepEl.textContent  = index + 1;
    titleEl.textContent = getSectionTitle(sections[index]);
    prevBtn.disabled    = (index === 0);
    nextBtn.textContent = (index === sections.length - 1) ? 'Finish' : 'Next →';

    sections[index].scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function startWalkthrough() {
    sections = Array.from(document.querySelectorAll('.ve-section'));
    if (!sections.length) return;

    totalEl.textContent = sections.length;
    document.body.classList.add('walkthrough-mode');
    bar.classList.add('is-open');
    showStep(0);
  }

  function stopWalkthrough() {
    document.body.classList.remove('walkthrough-mode');
    bar.classList.remove('is-open');
    sections.forEach(s => s.classList.remove('walkthrough-active'));
  }

  function walkNext() {
    if (current < sections.length - 1) {
      showStep(current + 1);
    } else {
      stopWalkthrough();
    }
  }

  function walkPrev() {
    if (current > 0) showStep(current - 1);
  }

  document.addEventListener('keydown', function (e) {
    if (!bar.classList.contains('is-open')) return;
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown') { e.preventDefault(); walkNext(); }
    if (e.key === 'ArrowLeft'  || e.key === 'ArrowUp')   { e.preventDefault(); walkPrev(); }
    if (e.key === 'Escape')                               { stopWalkthrough(); }
  });

  // Expose to onclick attributes in HTML above
  window.startWalkthrough = startWalkthrough;
  window.stopWalkthrough  = stopWalkthrough;
  window.walkNext         = walkNext;
  window.walkPrev         = walkPrev;
}());
```

---

## Notes

**Combining with voice narration (auto-narrated walkthrough)**

The voice narration pattern (`startNarration` / `stopNarration`) from pattern 6 in this file integrates directly. Inside `showStep(index)`, after the `scrollIntoView` call, add:

```javascript
stopNarration();                    // stop current
startNarration(sections[index]);    // narrate new section
```

Also call `stopNarration()` inside `stopWalkthrough()`. This gives you a self-guided audio tour where each section is read aloud as you advance.

**Custom section selector**

`document.querySelectorAll('.ve-section')` is the default. To target a different element type or class, change the selector inside `startWalkthrough()`:

```javascript
sections = Array.from(document.querySelectorAll('article.content-block'));
```

**Finish behavior**

The last "Next →" button changes its label to "Finish" and calls `stopWalkthrough()`. To navigate to a different URL or show a completion modal instead, replace the `stopWalkthrough()` call in `walkNext()` with your own logic.

**Scroll offset for sticky navbars**

If the page has a sticky top nav, `scrollIntoView({ block: 'start' })` will position the section behind it. Add `scroll-margin-top: 64px` (or your nav height) to `.ve-section` in CSS, following the pattern in `./responsive-nav.md`.

**Accessibility**

The `.walkthrough-bar` has `role="navigation"` and `aria-label`. The Prev/Next/Close buttons have `aria-label` values. When `prefers-reduced-motion` is active, the blur/fade transitions are removed so the page is never visually degraded — only the step counter and scroll advance.
