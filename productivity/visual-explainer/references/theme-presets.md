# Theme Presets

Six named CSS custom-property blocks that codify the skill's recommended aesthetics. Each preset is a complete `:root` declaration plus a `prefers-color-scheme` override plus the Google Fonts `<link>` line plus a matched Mermaid `themeVariables` block. Copy a preset wholesale rather than re-deriving colors from scratch.

The variable surface is identical across all presets — every preset declares the same names in the same order. That makes swapping presets a single block replacement, and downstream CSS that uses `var(--accent)` or `var(--text-dim)` works against any preset.

## Variable Surface (every preset declares these)

| Variable | Purpose |
|---|---|
| `--font-display` | Display headings (h1, hero) |
| `--font-body` | Body text and section headings |
| `--font-mono` | Code, labels, eyebrows |
| `--bg` | Page background |
| `--surface` | Card background |
| `--surface-elevated` | Elevated card background (hero) |
| `--surface-recessed` | Recessed area (code, secondary) |
| `--border` | Subtle borders, low-opacity |
| `--border-bright` | Visible borders, dividers |
| `--text` | Primary text |
| `--text-dim` | Secondary text |
| `--text-faint` | Tertiary text, captions |
| `--accent` | Primary accent |
| `--accent-dim` | Primary accent at low opacity |
| `--accent-bright` | Primary accent at higher saturation |
| `--secondary` | Secondary accent |
| `--secondary-dim` | Secondary accent at low opacity |
| `--tertiary` | Tertiary accent (warnings, highlights) |
| `--tertiary-dim` | Tertiary accent at low opacity |
| `--danger` / `--danger-dim` | Errors, destructive actions |

Pages that use other tokens (e.g. `--phase-past`, `--kpi-color`) layer them on top of this base — keep the names consistent.

---

## `paper-ink` — Warm, Editorial, Informal

Cream + terracotta + sage. Italic serif display, sans body, monospace labels. Default choice for project recaps, plan reviews, and prose-leaning visual pages.

**Fonts:**
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=IBM+Plex+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
```

**Variables:**
```css
:root {
  --font-display: 'Instrument Serif', Georgia, serif;
  --font-body: 'IBM Plex Sans', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', 'SF Mono', Consolas, monospace;

  --bg: #faf7f5;
  --surface: #ffffff;
  --surface-elevated: #fffdfb;
  --surface-recessed: #f5efe8;
  --border: rgba(26, 24, 21, 0.09);
  --border-bright: rgba(26, 24, 21, 0.16);
  --text: #1a1815;
  --text-dim: #6e655c;
  --text-faint: #9a9082;

  --accent: #c2410c;          /* terracotta */
  --accent-dim: rgba(194, 65, 12, 0.09);
  --accent-bright: #ea580c;
  --secondary: #65a30d;       /* sage */
  --secondary-dim: rgba(101, 163, 13, 0.10);
  --tertiary: #d97706;        /* amber */
  --tertiary-dim: rgba(217, 119, 6, 0.12);
  --danger: #be123c;
  --danger-dim: rgba(190, 18, 60, 0.10);
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg: #100e0c;
    --surface: #1a1714;
    --surface-elevated: #221e1a;
    --surface-recessed: #141210;
    --border: rgba(245, 240, 232, 0.08);
    --border-bright: rgba(245, 240, 232, 0.16);
    --text: #f5f0e8;
    --text-dim: #a39687;
    --text-faint: #6e6357;

    --accent: #fb923c;
    --accent-dim: rgba(251, 146, 60, 0.12);
    --accent-bright: #fdba74;
    --secondary: #84cc16;
    --secondary-dim: rgba(132, 204, 22, 0.12);
    --tertiary: #fbbf24;
    --tertiary-dim: rgba(251, 191, 36, 0.12);
    --danger: #f87171;
    --danger-dim: rgba(248, 113, 113, 0.14);
  }
}
```

**Mermaid themeVariables:**
```javascript
const isDark = matchMedia('(prefers-color-scheme: dark)').matches;
mermaid.initialize({
  theme: 'base',
  themeVariables: {
    fontFamily: "'IBM Plex Sans', system-ui, sans-serif",
    primaryColor:        isDark ? '#2a1a14' : '#fff3ec',
    primaryBorderColor:  isDark ? '#fb923c' : '#c2410c',
    primaryTextColor:    isDark ? '#f5f0e8' : '#1a1815',
    secondaryColor:      isDark ? '#1a2614' : '#f1f8e1',
    secondaryBorderColor: isDark ? '#84cc16' : '#65a30d',
    secondaryTextColor:  isDark ? '#f5f0e8' : '#1a1815',
    tertiaryColor:       isDark ? '#221d10' : '#fef5e0',
    tertiaryBorderColor: isDark ? '#fbbf24' : '#d97706',
    lineColor:           isDark ? '#a39687' : '#6e655c',
  }
});
```

---

## `blueprint` — Technical, Precise, Dark Header

IBM Plex Sans + Mono throughout. Teal + slate palette. Subtle grid background. Dark header bar (`--surface-header`) for visual hierarchy. Default for system diagrams, architecture overviews, implementation plans.

**Fonts:**
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
```

**Variables:**
```css
:root {
  --font-display: 'IBM Plex Sans', system-ui, sans-serif;
  --font-body: 'IBM Plex Sans', system-ui, sans-serif;
  --font-mono: 'IBM Plex Mono', 'SF Mono', Consolas, monospace;

  --bg: #f1f5f9;
  --surface: #ffffff;
  --surface-elevated: #ffffff;
  --surface-recessed: #e2e8f0;
  --surface-header: #0f172a;   /* dark header bar */
  --border: rgba(15, 23, 42, 0.10);
  --border-bright: rgba(15, 23, 42, 0.20);
  --text: #0f172a;
  --text-dim: #475569;
  --text-faint: #94a3b8;

  --accent: #0891b2;           /* teal */
  --accent-dim: rgba(8, 145, 178, 0.10);
  --accent-bright: #0e7490;
  --secondary: #0369a1;        /* slate-blue */
  --secondary-dim: rgba(3, 105, 161, 0.10);
  --tertiary: #d97706;
  --tertiary-dim: rgba(217, 119, 6, 0.12);
  --danger: #dc2626;
  --danger-dim: rgba(220, 38, 38, 0.10);
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0f172a;
    --surface: #1e293b;
    --surface-elevated: #243049;
    --surface-recessed: #0b1220;
    --surface-header: #020617;
    --border: rgba(226, 232, 240, 0.08);
    --border-bright: rgba(226, 232, 240, 0.16);
    --text: #f1f5f9;
    --text-dim: #94a3b8;
    --text-faint: #64748b;

    --accent: #22d3ee;
    --accent-dim: rgba(34, 211, 238, 0.12);
    --accent-bright: #67e8f9;
    --secondary: #38bdf8;
    --secondary-dim: rgba(56, 189, 248, 0.12);
    --tertiary: #fbbf24;
    --tertiary-dim: rgba(251, 191, 36, 0.12);
    --danger: #f87171;
    --danger-dim: rgba(248, 113, 113, 0.14);
  }
}

body {
  background-image: linear-gradient(var(--border) 1px, transparent 1px),
                    linear-gradient(90deg, var(--border) 1px, transparent 1px);
  background-size: 32px 32px;
}
```

**Mermaid themeVariables:**
```javascript
const isDark = matchMedia('(prefers-color-scheme: dark)').matches;
mermaid.initialize({
  theme: 'base',
  themeVariables: {
    fontFamily: "'IBM Plex Sans', system-ui, sans-serif",
    primaryColor:        isDark ? '#0c4a6e' : '#cffafe',
    primaryBorderColor:  isDark ? '#22d3ee' : '#0891b2',
    primaryTextColor:    isDark ? '#f1f5f9' : '#0f172a',
    secondaryColor:      isDark ? '#1e3a5f' : '#e0f2fe',
    secondaryBorderColor: isDark ? '#38bdf8' : '#0369a1',
    lineColor:           isDark ? '#94a3b8' : '#475569',
  }
});
```

---

## `editorial` — Refined, Magazine, Deep Navy + Gold

Fraunces display, Source Sans body, Source Code mono. Deep navy + sophisticated gold. Use for executive summaries, premium-feeling reports, plan reviews where polish matters.

**Fonts:**
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Source+Sans+3:wght@400;500;600&family=Source+Code+Pro:wght@400;500;600&display=swap" rel="stylesheet">
```

**Variables:**
```css
:root {
  --font-display: 'Fraunces', Georgia, serif;
  --font-body: 'Source Sans 3', system-ui, sans-serif;
  --font-mono: 'Source Code Pro', 'SF Mono', Consolas, monospace;

  --bg: #fdfcfa;
  --surface: #ffffff;
  --surface-elevated: #fffdf8;
  --surface-recessed: #f4f0e8;
  --border: rgba(30, 58, 95, 0.10);
  --border-bright: rgba(30, 58, 95, 0.20);
  --text: #1e3a5f;
  --text-dim: #506480;
  --text-faint: #8c9bb0;

  --accent: #1e3a5f;           /* deep navy */
  --accent-dim: rgba(30, 58, 95, 0.10);
  --accent-bright: #2c4a72;
  --secondary: #b8860b;        /* gold */
  --secondary-dim: rgba(184, 134, 11, 0.10);
  --tertiary: #d4a73a;
  --tertiary-dim: rgba(212, 167, 58, 0.14);
  --danger: #9a3412;
  --danger-dim: rgba(154, 52, 18, 0.10);
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0c1726;
    --surface: #162538;
    --surface-elevated: #1b2c44;
    --surface-recessed: #091321;
    --border: rgba(212, 167, 58, 0.10);
    --border-bright: rgba(212, 167, 58, 0.22);
    --text: #f0e9d6;
    --text-dim: #c5b886;
    --text-faint: #8a7d56;

    --accent: #d4a73a;
    --accent-dim: rgba(212, 167, 58, 0.14);
    --accent-bright: #eac15a;
    --secondary: #b8860b;
    --secondary-dim: rgba(184, 134, 11, 0.14);
    --tertiary: #fbbf24;
    --tertiary-dim: rgba(251, 191, 36, 0.14);
    --danger: #f87171;
    --danger-dim: rgba(248, 113, 113, 0.14);
  }
}
```

---

## `terminal` — Monospace, CRT, Green/Amber on Near-Black

JetBrains Mono throughout. Green primary, amber secondary, near-black background. Optional CRT glow on text (subtle text-shadow, not animated). Use for log dumps, system status reports, ops dashboards.

**Fonts:**
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
```

**Variables:**
```css
:root {
  /* Terminal preset is dark-first */
  --font-display: 'JetBrains Mono', monospace;
  --font-body: 'JetBrains Mono', monospace;
  --font-mono: 'JetBrains Mono', monospace;

  --bg: #0a0e0a;
  --surface: #121712;
  --surface-elevated: #161c16;
  --surface-recessed: #060906;
  --border: rgba(80, 220, 100, 0.15);
  --border-bright: rgba(80, 220, 100, 0.30);
  --text: #d4f5d4;
  --text-dim: #7fb37f;
  --text-faint: #4a7a4a;

  --accent: #50dc64;            /* terminal green */
  --accent-dim: rgba(80, 220, 100, 0.14);
  --accent-bright: #7fe890;
  --secondary: #ffb454;         /* warm amber */
  --secondary-dim: rgba(255, 180, 84, 0.14);
  --tertiary: #ff9a3c;
  --tertiary-dim: rgba(255, 154, 60, 0.14);
  --danger: #ff6b6b;
  --danger-dim: rgba(255, 107, 107, 0.14);
}

@media (prefers-color-scheme: light) {
  :root {
    --bg: #f4f6f0;
    --surface: #ffffff;
    --surface-elevated: #fafcf6;
    --surface-recessed: #e8ecdc;
    --border: rgba(38, 89, 51, 0.14);
    --border-bright: rgba(38, 89, 51, 0.26);
    --text: #1a3320;
    --text-dim: #4a6651;
    --text-faint: #8b9c8f;

    --accent: #1f7a32;
    --accent-dim: rgba(31, 122, 50, 0.10);
    --accent-bright: #16602a;
    --secondary: #b86b2a;
    --secondary-dim: rgba(184, 107, 42, 0.10);
    --tertiary: #c87523;
    --tertiary-dim: rgba(200, 117, 35, 0.10);
    --danger: #a3221c;
    --danger-dim: rgba(163, 34, 28, 0.10);
  }
}
```

**Optional CRT glow (text only, not animated):**
```css
body { text-shadow: 0 0 1.5px rgba(80, 220, 100, 0.4); }
```

Skip the CRT glow for body text below 14px — it reduces readability. Reserve it for hero titles only.

---

## `nord` — Real IDE Theme

Authentic Nord palette. Geist + Geist Mono. Pick this when you want a real, recognizable color scheme rather than an approximation.

**Fonts:**
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500&display=swap" rel="stylesheet">
```

**Variables:**
```css
:root {
  --font-display: 'Geist', system-ui, sans-serif;
  --font-body: 'Geist', system-ui, sans-serif;
  --font-mono: 'Geist Mono', 'SF Mono', Consolas, monospace;

  /* Nord light: Snow Storm base + Polar Night text */
  --bg: #eceff4;              /* nord6 */
  --surface: #e5e9f0;         /* nord5 */
  --surface-elevated: #ffffff;
  --surface-recessed: #d8dee9; /* nord4 */
  --border: rgba(46, 52, 64, 0.10);
  --border-bright: rgba(46, 52, 64, 0.20);
  --text: #2e3440;             /* nord0 */
  --text-dim: #4c566a;         /* nord3 */
  --text-faint: #7b88a1;

  --accent: #5e81ac;           /* nord10 frost-blue */
  --accent-dim: rgba(94, 129, 172, 0.14);
  --accent-bright: #81a1c1;
  --secondary: #88c0d0;        /* nord8 frost-cyan */
  --secondary-dim: rgba(136, 192, 208, 0.14);
  --tertiary: #d08770;         /* nord12 aurora-orange */
  --tertiary-dim: rgba(208, 135, 112, 0.14);
  --danger: #bf616a;           /* nord11 aurora-red */
  --danger-dim: rgba(191, 97, 106, 0.14);
}

@media (prefers-color-scheme: dark) {
  :root {
    /* Nord dark: Polar Night base + Snow Storm text */
    --bg: #2e3440;             /* nord0 */
    --surface: #3b4252;        /* nord1 */
    --surface-elevated: #434c5e; /* nord2 */
    --surface-recessed: #2a2f3a;
    --border: rgba(236, 239, 244, 0.08);
    --border-bright: rgba(236, 239, 244, 0.16);
    --text: #eceff4;           /* nord6 */
    --text-dim: #d8dee9;       /* nord4 */
    --text-faint: #7b88a1;

    --accent: #88c0d0;         /* nord8 frost-cyan */
    --accent-dim: rgba(136, 192, 208, 0.14);
    --accent-bright: #8fbcbb;
    --secondary: #81a1c1;      /* nord9 frost */
    --secondary-dim: rgba(129, 161, 193, 0.14);
    --tertiary: #ebcb8b;       /* nord13 aurora-yellow */
    --tertiary-dim: rgba(235, 203, 139, 0.14);
    --danger: #bf616a;
    --danger-dim: rgba(191, 97, 106, 0.14);
  }
}
```

---

## `dracula` — Real IDE Theme

Authentic Dracula palette. DM Sans + Fira Code. Dark-first; high contrast; the pink/purple here is authentic Dracula, not Tailwind slop.

**Fonts:**
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
```

**Variables:**
```css
:root {
  /* Dracula is dark-first */
  --font-display: 'DM Sans', system-ui, sans-serif;
  --font-body: 'DM Sans', system-ui, sans-serif;
  --font-mono: 'Fira Code', 'SF Mono', Consolas, monospace;

  --bg: #282a36;
  --surface: #343746;
  --surface-elevated: #44475a;
  --surface-recessed: #21222c;
  --border: rgba(248, 248, 242, 0.10);
  --border-bright: rgba(248, 248, 242, 0.20);
  --text: #f8f8f2;
  --text-dim: #bdbecf;
  --text-faint: #6272a4;        /* comment */

  --accent: #bd93f9;            /* purple */
  --accent-dim: rgba(189, 147, 249, 0.14);
  --accent-bright: #d6b3ff;
  --secondary: #50fa7b;         /* green */
  --secondary-dim: rgba(80, 250, 123, 0.14);
  --tertiary: #f1fa8c;          /* yellow */
  --tertiary-dim: rgba(241, 250, 140, 0.14);
  --danger: #ff5555;            /* red */
  --danger-dim: rgba(255, 85, 85, 0.14);
}

@media (prefers-color-scheme: light) {
  /* Dracula Light Theme (Alucard) */
  :root {
    --bg: #f8f8f2;
    --surface: #ffffff;
    --surface-elevated: #ffffff;
    --surface-recessed: #e9e9f4;
    --border: rgba(56, 58, 89, 0.10);
    --border-bright: rgba(56, 58, 89, 0.22);
    --text: #383a59;
    --text-dim: #4f526d;
    --text-faint: #7b7f9e;

    --accent: #644ac9;
    --accent-dim: rgba(100, 74, 201, 0.10);
    --accent-bright: #7b5fd6;
    --secondary: #14710a;
    --secondary-dim: rgba(20, 113, 10, 0.10);
    --tertiary: #846e15;
    --tertiary-dim: rgba(132, 110, 21, 0.10);
    --danger: #cb3a2a;
    --danger-dim: rgba(203, 58, 42, 0.10);
  }
}
```

**Authenticity note.** Dracula's `#bd93f9` purple is the real Dracula accent — it's not the forbidden Tailwind `#8b5cf6` indigo even though they look similar. The lint script doesn't flag Dracula because it scans for specific banned hex values. When you commit to Dracula, commit to the whole palette.

---

## Picking a Preset

Quick decision table:

| Content | Preset |
|---|---|
| Project recap, plan review, prose-heavy | `paper-ink` |
| Architecture diagram, implementation plan, system overview | `blueprint` |
| Executive summary, RFC, polished report | `editorial` |
| Log dump, system status, ops dashboard | `terminal` |
| Code-tour for a Rust/Go/system project | `nord` or `dracula` |
| API docs for a modern web framework | `nord` |

**Never:**
- Use two presets on the same page
- Edit a preset's colors mid-page (use a single source of truth in `:root`)
- Re-derive a palette from scratch when one of these fits — that's how generic AI templates happen

**To extend a preset** (e.g. add `--phase-past` for a timeline): add the new tokens after the preset block. Don't modify the preset itself.

---

## Verifying a Preset is Applied Correctly

Three checks before delivery:

1. **Lint clean:** `node {{skill_dir}}/scripts/lint.js <file>` — confirms no forbidden hex values leaked in.
2. **Both modes look intentional:** toggle the OS between light and dark. Both should look like a finished design, not "the dark version is a hack."
3. **Mermaid matches:** the Mermaid `themeVariables` block in each preset uses the same palette tokens as the CSS variables. If a diagram looks off-palette, cross-check the JS `isDark` branching against the CSS dark override.
