'use strict';

const { spawnSync } = require('child_process');
const path = require('path');
const fs   = require('fs');

const scriptDir    = __dirname;
const lintScript   = path.join(scriptDir, 'lint.js');
const templatesDir = path.join(scriptDir, '..', 'templates');
const jsonMode     = process.argv.includes('--json');

const files = fs.readdirSync(templatesDir)
  .filter(f => f.endsWith('.html'))
  .sort()
  .map(f => path.join(templatesDir, f));

if (files.length === 0) {
  if (jsonMode) {
    process.stdout.write(JSON.stringify({ total: 0, passed: 0, failed: 0, results: [] }) + '\n');
  } else {
    process.stderr.write('No HTML templates found in ' + templatesDir + '\n');
  }
  process.exit(1);
}

const results = [];
let passed = 0;
let failed = 0;

for (const file of files) {
  const rel  = path.relative(process.cwd(), file);
  const proc = spawnSync('node', [lintScript, '--json', file], { encoding: 'utf8' });
  const ok   = proc.status === 0;

  if (ok) {
    passed++;
    results.push({ file: rel, pass: true });
    if (!jsonMode) process.stdout.write('PASS  ' + rel + '\n');
  } else {
    failed++;
    let parsed = { checks: {} };
    try { parsed = JSON.parse(proc.stdout); } catch (_) { /* treat as no details */ }
    const violations = Object.entries(parsed.checks || {})
      .filter(([, v]) => v === false)
      .map(([k]) => k);
    results.push({ file: rel, pass: false, violations });
    if (!jsonMode) {
      process.stdout.write('FAIL  ' + rel + '\n');
      for (const v of violations) process.stdout.write('      - ' + v + '\n');
    }
  }
}

if (jsonMode) {
  process.stdout.write(JSON.stringify({ total: files.length, passed, failed, results }, null, 2) + '\n');
} else {
  const sym = failed === 0 ? '✓' : '✗';
  process.stdout.write('\n' + sym + ' ' + passed + '/' + files.length + ' templates passed\n');
}

process.exit(failed > 0 ? 1 : 0);
