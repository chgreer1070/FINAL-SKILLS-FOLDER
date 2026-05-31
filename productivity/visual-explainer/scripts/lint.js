#!/usr/bin/env node
/*
 * visual-explainer-lint
 * Codifies the 7-point Slop Test from plugins/visual-explainer/SKILL.md.
 * Audits a generated HTML file against the explicit anti-patterns the
 * skill forbids. Exits 0 on clean, 1 on any violation, 2 on usage error.
 *
 * Usage:
 *   node lint.js path/to/page.html
 *   node lint.js --json path/to/page.html
 */

'use strict';

const fs = require('fs');
const path = require('path');

const USAGE = `Usage: node lint.js [--json] <html-file>

Audits an HTML file against the visual-explainer Slop Test:
  1. Forbidden fonts as --font-body (Inter, Roboto, Arial, Helvetica, bare system-ui)
  2. Forbidden indigo/violet/fuchsia hex colors
  3. Cyan + magenta + pink combination
  4. Gradient text on headings (background-clip:text inside h1/h2/h3)
  5. Animated glowing box-shadows
  6. Emoji icons leading section headers
  7. Three-dot window chrome on code blocks

Exits 0 on clean, 1 on any violation, 2 on usage error.`;

// ---- Argument parsing ----
const args = process.argv.slice(2);
let jsonMode = false;
let filePath = null;

for (const a of args) {
  if (a === '--json') jsonMode = true;
  else if (a === '-h' || a === '--help') { console.log(USAGE); process.exit(0); }
  else if (a.startsWith('-')) { console.error(`Unknown flag: ${a}\n\n${USAGE}`); process.exit(2); }
  else filePath = a;
}

if (!filePath) { console.error(USAGE); process.exit(2); }
if (!fs.existsSync(filePath)) { console.error(`File not found: ${filePath}`); process.exit(2); }

const html = fs.readFileSync(filePath, 'utf8');
const styleBlocks = (html.match(/<style\b[^>]*>([\s\S]*?)<\/style>/gi) || [])
  .map(b => b.replace(/<\/?style\b[^>]*>/gi, '')).join('\n');
const inlineStyles = (html.match(/\sstyle\s*=\s*"([^"]*)"/gi) || []).join('\n');
// CSS zones: where a color/effect would actually take effect.
// Excludes document body text (e.g. <code>#8b5cf6</code> documenting a forbidden value).
const cssZones = styleBlocks + '\n' + inlineStyles;

// ---- Checks ----
// Each returns { ok, found:[], note, name }

function check_forbiddenFontBody() {
  const name = 'Forbidden fonts as --font-body';
  const found = [];
  const fontBodyMatch = styleBlocks.match(/--font-body\s*:\s*([^;}\n]+)/i);
  if (fontBodyMatch) {
    const value = fontBodyMatch[1].trim();
    const firstFont = (value.split(',')[0] || '').replace(/['"]/g, '').trim().toLowerCase();
    const forbidden = ['inter', 'roboto', 'arial', 'helvetica', 'helvetica neue'];
    if (forbidden.includes(firstFont)) {
      found.push(`primary --font-body is "${firstFont}" — forbidden as primary`);
    }
    if (firstFont === 'system-ui' && !value.includes(',')) {
      found.push(`--font-body is bare "system-ui" with no named font`);
    }
  }
  return {
    name,
    ok: found.length === 0,
    found,
    note: 'Pick a distinctive pairing from libraries.md (DM Sans, Instrument Serif, IBM Plex Sans, Bricolage Grotesque, Plus Jakarta Sans).',
  };
}

function check_forbiddenHexColors() {
  const name = 'Forbidden indigo/violet/fuchsia hexes';
  const banned = [
    '#8b5cf6', // violet-500
    '#7c3aed', // violet-600
    '#a78bfa', // violet-400
    '#d946ef', // fuchsia-500
  ];
  const found = [];
  for (const hex of banned) {
    const re = new RegExp(hex, 'gi');
    const matches = cssZones.match(re);
    if (matches && matches.length > 0) {
      found.push(`${hex} appears ${matches.length}× in CSS`);
    }
  }
  return {
    name,
    ok: found.length === 0,
    found,
    note: 'Use terracotta+sage, teal+slate, rose+cranberry, amber+emerald, or a real IDE theme (Nord, Dracula, Solarized).',
  };
}

function check_neonCombo() {
  const name = 'Cyan + magenta + pink combo';
  const neon = ['#06b6d4', '#22d3ee', '#d946ef', '#f472b6', '#ec4899'];
  const present = neon.filter(h => new RegExp(h, 'i').test(cssZones));
  const found = [];
  if (present.length >= 2) {
    found.push(`${present.length} neon hexes co-occur: ${present.join(', ')}`);
  }
  return {
    name,
    ok: found.length === 0,
    found,
    note: 'The cyan-magenta-pink palette is a Tailwind/AI-template default. Pick a constrained aesthetic instead.',
  };
}

function check_gradientHeadings() {
  const name = 'Gradient text on headings';
  const found = [];
  const re = /(h[123][^{]*)\{([^}]*)\}/gi;
  let m;
  while ((m = re.exec(styleBlocks)) !== null) {
    const selector = m[1].trim();
    const body = m[2];
    const hasClip = /background-clip\s*:\s*text|-webkit-background-clip\s*:\s*text/i.test(body);
    const hasGradient = /linear-gradient|radial-gradient/i.test(body);
    if (hasClip && hasGradient) {
      found.push(`${selector} uses background-clip:text + gradient`);
    }
  }
  return {
    name,
    ok: found.length === 0,
    found,
    note: 'Gradient-text headings are AI-template slop. Use a single accent color + good typography.',
  };
}

function check_glowingShadows() {
  const name = 'Animated glowing box-shadows';
  const found = [];
  const re = /@keyframes\s+([\w-]+)\s*\{([\s\S]*?)\n\s*\}/g;
  let m;
  while ((m = re.exec(styleBlocks)) !== null) {
    const keyframeName = m[1];
    const body = m[2];
    if (/^glow/i.test(keyframeName) || /glow/i.test(keyframeName)) {
      if (/box-shadow/i.test(body)) {
        found.push(`@keyframes ${keyframeName} animates box-shadow`);
        continue;
      }
    }
    if (/box-shadow\s*:[^;]*\b(?:[2-9]\d|\d{3,})px[^;]*(?:rgba?|#)/i.test(body)) {
      found.push(`@keyframes ${keyframeName} animates a large box-shadow (likely glow)`);
    }
  }
  return {
    name,
    ok: found.length === 0,
    found,
    note: 'Pulsing/breathing glows are forbidden. Use entrance fades + hover transitions only.',
  };
}

function check_emojiHeaders() {
  const name = 'Emoji icons leading section headers';
  const found = [];
  const headingRe = /<h([1-6])\b[^>]*>([\s\S]*?)<\/h\1>/gi;
  let m;
  while ((m = headingRe.exec(html)) !== null) {
    const innerText = m[2];
    const text = innerText.replace(/<[^>]+>/g, '').trim();
    const firstChar = Array.from(text)[0];
    if (firstChar && /[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}\u{1F000}-\u{1F2FF}]/u.test(firstChar)) {
      const snippet = text.slice(0, 40).replace(/\s+/g, ' ');
      found.push(`h${m[1]} starts with emoji: "${snippet}"`);
    }
  }
  return {
    name,
    ok: found.length === 0,
    found,
    note: 'Use monospace section labels + colored dots, numbered badges, or inline SVG. Never emoji.',
  };
}

function check_threeDotChrome() {
  const name = 'Three-dot window chrome on code blocks';
  const found = [];
  const macWindowColors = /#ff5f5[67]|#ffbd2e|#28c[649]40/gi;
  const macMatches = (html.match(macWindowColors) || []);
  if (macMatches.length >= 2) {
    found.push(`macOS traffic-light colors found ${macMatches.length}× (likely window chrome)`);
  }

  const classHints = /(?:window-controls?|traffic-lights?|window-chrome|window-dots?|os-chrome|code-window-dots?)\b/i;
  if (classHints.test(html)) {
    found.push(`class name hints at window-chrome dots`);
  }

  const trio = /background[^;}]*(?:red|#e0[1-7]|#f00)[^>]*>[\s\S]{0,300}background[^;}]*(?:yellow|#ffbd|#ffc|#fc0)[^>]*>[\s\S]{0,300}background[^;}]*(?:green|#0c0|#28c|#0f0)/i;
  if (trio.test(html)) {
    found.push(`three consecutive red/yellow/green colored elements detected`);
  }

  return {
    name,
    ok: found.length === 0,
    found,
    note: 'Code blocks should use a clean filename header, not macOS traffic-light dots.',
  };
}

// ---- Run all checks ----
const checks = [
  check_forbiddenFontBody,
  check_forbiddenHexColors,
  check_neonCombo,
  check_gradientHeadings,
  check_glowingShadows,
  check_emojiHeaders,
  check_threeDotChrome,
];

const results = checks.map(fn => fn());
const violations = results.filter(r => !r.ok);
const exitCode = violations.length === 0 ? 0 : 1;

// ---- Output ----
if (jsonMode) {
  const out = {
    file: path.resolve(filePath),
    pass: exitCode === 0,
    checks: results.map(r => ({ name: r.name, ok: r.ok, found: r.found, note: r.note })),
    summary: {
      total: results.length,
      passed: results.length - violations.length,
      violated: violations.length,
    },
  };
  console.log(JSON.stringify(out, null, 2));
  process.exit(exitCode);
}

// Human-readable
const useColor = process.stdout.isTTY;
const c = {
  reset:     useColor ? '\x1b[0m'        : '',
  bold:      useColor ? '\x1b[1m'        : '',
  dim:       useColor ? '\x1b[2m'        : '',
  red:       useColor ? '\x1b[31m'       : '',
  green:     useColor ? '\x1b[32m'       : '',
  yellow:    useColor ? '\x1b[33m'       : '',
  terracotta:useColor ? '\x1b[38;5;166m' : '',
  sage:      useColor ? '\x1b[38;5;106m' : '',
};

const header = `${c.terracotta}${c.bold}visual-explainer-lint${c.reset} ${c.dim}→${c.reset} ${path.basename(filePath)}`;
console.log('');
console.log(header);
console.log(c.dim + '─'.repeat(56) + c.reset);

for (const r of results) {
  const mark  = r.ok ? `${c.green}✓${c.reset}` : `${c.red}✗${c.reset}`;
  const label = r.ok ? `${c.sage}${r.name}${c.reset}` : `${c.bold}${r.name}${c.reset}`;
  console.log(`  ${mark} ${label}`);
  if (!r.ok) {
    for (const f of r.found) {
      console.log(`      ${c.red}·${c.reset} ${f}`);
    }
    console.log(`      ${c.dim}→ ${r.note}${c.reset}`);
  }
}

console.log(c.dim + '─'.repeat(56) + c.reset);

if (exitCode === 0) {
  console.log(`${c.green}✓ clean${c.reset} — ${results.length}/${results.length} checks passed.`);
} else {
  console.log(`${c.red}✗ ${violations.length} violation${violations.length === 1 ? '' : 's'}${c.reset} — ${results.length - violations.length}/${results.length} checks passed.`);
}
console.log('');

process.exit(exitCode);
