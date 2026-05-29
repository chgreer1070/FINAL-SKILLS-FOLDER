# FINAL-SKILLS-FOLDER

A curated collection of **16 Agent Skills** (`.skill` packages) for legal/contract
analysis, finance, forecasting, data science, and productivity. Each `.skill` file is
a zip archive containing a top-level skill directory with a `SKILL.md` (YAML
frontmatter + instructions) plus any supporting `scripts/`, `references/`, and
`assets/`.

The skills are grouped into four categories:

| Category | Skills | What they cover |
|---|---|---|
| [`legal-contracts/`](#legal-contracts) | 8 | EMS / Flex contract review, risk scoring, intake, organization, litigation, and pipeline building |
| [`finance-forecasting/`](#finance-forecasting) | 2 | P&L intelligence reporting and zero-shot time-series forecasting |
| [`data-science/`](#data-science) | 4 | Statistics, modeling, explainability, and economic data access |
| [`productivity/`](#productivity) | 2 | Branded PowerPoint generation and Cowork session visualization |

## Using a skill

Each `.skill` is a self-contained package. To inspect or install one:

```bash
unzip -l legal-contracts/ems-contract-analyzer.skill   # list contents
unzip legal-contracts/ems-contract-analyzer.skill -d ./   # extract the skill dir
```

When extracted, every package produces a single directory matching its skill name
(e.g. `ems-contract-analyzer/`) containing `SKILL.md` at its root.

---

## legal-contracts

EMS (Electronics Manufacturing Services) and Flex-focused contract and legal tooling.

### `5d-engine.skill`
Quantitative EMS contract risk scoring across five weighted dimensions (Cash Flow 30%,
Inventory Exposure 25%, Cost Recovery 20%, Operational Risk 13%, Legal Architecture
12%) with cascade interaction mapping. Scores contracts 0–10 from a CFO perspective and
generates tiered, color-coded DOCX reports.
*Contents:* `SKILL.md`, `scripts/report_builder.md`, `references/scoring_criteria.md`,
`references/flex_standard_provisions.md`.

### `contract-intake-pipeline.skill`
Automated 8-step intake pipeline for new EMS manufacturing agreements: extracts key
terms, scores clause-by-clause risk against Flex standard positions, quantifies
exposure, and outputs a prioritized issues list with redline-ready fallbacks. Has FULL
(~15–20 min) and QUICK (~5 min triage) modes.
*Contents:* `SKILL.md`, `scripts/extract_contract_text.py`,
`scripts/generate_intake_report.py`, `references/flex_positions_summary.md`,
`references/pipelines/new-contract-intake.json`.

### `contract-portfolio-organizer.skill`
Organizes batches of contract PDFs into customer-grouped folder hierarchies with
parent/child relationship mapping and four visualizations per customer (interactive HTML
tree, SVG, markdown outline, temporal timeline). Resolves entities to corporate families
via fuzzy matching. Documented as validated to a 99% pass rate over 73 contracts.
*Contents:* `SKILL.md`, `references/visualization-templates.md`.

### `contract-twin-3d.skill`
Transforms manufacturing contracts into interactive 3D digital twins — a force-directed
graph where clauses are nodes and dependencies are edges, navigable from executive
overview down to clause language. Built on a 25-family EMS clause ontology across 6
operational zones.
*Contents:* `SKILL.md`.

### `ems-contract-analyzer.skill`
Analyzes EMS manufacturing agreements against company standard terms, identifies
deviations, assesses financial/legal risk, and generates redlined recommendation
reports. Covers 41 critical clause areas with Preferred/Fallback/Red Line positions and
cross-clause dependency analysis.
*Contents:* `SKILL.md`, `scripts/redline_helper.py`,
`references/standard_terms.md`, `references/key_terms_checklist.md`,
`references/standard_contract.docx`.

### `ems-insurance-coverage-analyzer.skill`
Maps contract risks, liabilities, and obligations against an insurance program to
identify covered vs. uninsured exposures, quantify deductibles/limits, and produce a
coverage-gap narrative (Word report) plus a coverage matrix (Excel). Defaults to Flex's
manufacturer perspective.
*Contents:* `SKILL.md`, `references/flex-insurance-program.md`,
`references/risk-pattern-taxonomy.md`.

### `legal-pipeline-factory.skill`
A tool factory for building, storing, running, and curating chained LLM instruction
pipelines for legal/EMS contract analysis — sequences of analytical steps where each
step's output feeds the next.
*Contents:* `SKILL.md`, `references/pipeline-library.md`.

### `litigation-history-analyzer.skill`
Connects Flex litigation claims to EMS contract clauses. Three modes: classify new
matters against a 41-section clause taxonomy, analyze a contract against claim history
for clause gaps/financial risk, and generate/refresh the 4-deliverable report set.
*Contents:* `SKILL.md`, `references/classification_engine.py`,
`references/ems_clause_taxonomy.md`, `references/report_generation_workflow.md`,
`references/schema_reference.md`.

---

## finance-forecasting

### `pl-intelligence-report.skill`
Generates an executive-ready HTML P&L Intelligence Report dashboard from a Flex P&L
"Trended Actuals vs Forecast" Excel export. Handles data extraction, fiscal-year
detection, forecast-vintage selection, KPI calculation, and a rules-based risk-flag
engine. (v3.1, validated end-to-end against 4 live Flex P&L exports.)
*Contents:* `SKILL.md`, `run.py`, `scripts/extract_pl.py`,
`scripts/generate_report.py`, `references/flex_pl_definitions.md`,
`references/flex_bs_definitions.md`, `references/risk_flag_rules.md`.

### `timesfm-forecasting.skill`
Zero-shot univariate time-series forecasting with Google's TimesFM 2.5 foundation model
— point forecasts plus calibrated 10/50/90 quantile intervals, no training required.
Includes an auto-installer, an MCP server, an interactive dashboard, and finance-aware
triggers.
*Contents:* `SKILL.md`, `scripts/install.sh`, `scripts/check_system.py`,
`scripts/forecast_csv.py`, `assets/timesfm-dashboard.html`, `mcp-server/` (TS server),
`examples/minimal/`, `references/`.

---

## data-science

General-purpose statistical and ML tooling (authored by K-Dense Inc., except as noted).

### `fred-economic-data.skill`
Query the FRED (Federal Reserve Economic Data) API for 800,000+ economic time series
(GDP, unemployment, inflation, rates, housing, regional data) for macroeconomic
analysis and forecasting. **Requires a FRED API key** (`FRED_API_KEY`).
*Contents:* `SKILL.md`, `scripts/fred_query.py`, `scripts/fred_examples.py`, plus seven
`references/` topic guides (api_basics, categories, geofred, releases, series, sources,
tags).

### `shap.skill`
Model interpretability/explainability with SHAP (SHapley Additive exPlanations): feature
importance, SHAP plots (waterfall, beeswarm, bar, scatter, force, heatmap), bias/fairness
analysis, and model debugging across tree, deep-learning, linear, and black-box models.
License: MIT.
*Contents:* `SKILL.md`, `references/` (theory, explainers, plots, workflows).

### `statistical-analysis.skill`
Guided statistical analysis with test selection, assumption checking, power analysis, and
APA-formatted reporting — geared toward academic research. License: MIT.
*Contents:* `SKILL.md`, `scripts/assumption_checks.py`, `references/`
(test_selection_guide, assumptions_and_diagnostics, effect_sizes_and_power,
bayesian_statistics, reporting_standards).

### `statsmodels.skill`
The statsmodels Python library: OLS, GLM, mixed models, ARIMA, and other model classes
with detailed diagnostics, residuals, and inference — for econometrics, time series, and
rigorous coefficient-table reporting. License: BSD-3-Clause.
*Contents:* `SKILL.md`, `references/` (linear_models, glm, discrete_choice, time_series,
stats_diagnostics).

---

## productivity

### `flex-pptx-creator.skill`
Builds PowerPoint decks that strictly adhere to Flex's official brand template (Century
Gothic, Flex palette, approved layouts, confidentiality marks, logo placement). Produces
visually rich, branded slides and can convert HTML artifact decks to PPTX (image or
native shapes).
*Contents:* `SKILL.md`, `assets/PowerPoint_Template__Light.pptx`,
`scripts/html_to_pptx_image.py`, `scripts/html_to_pptx_shapes.py`, `references/`
(flex-brand, visual-patterns, charts-and-tables, layout-catalog, qa-and-pitfalls,
html-to-pptx).

### `cowork-visualizer.skill`
Analyzes Claude Cowork sessions and produces a self-contained 8-panel HTML dashboard
(workflow trace, file outputs, filesystem diff, decision graph, cost/perf, skill
invocation map, error/retry heatmap, cross-run comparison). Supports Mode A (OTel NDJSON
export) and Mode B (zipped Cowork workspace). Writes a run summary back to Notion.
*Contents:* `SKILL.md`, `assets/dashboard_template.html`, several `scripts/` (mode
detection/parsing, dashboard builder, skill signatures, Notion writeback),
`references/` (component_specs, otel_event_schema, skill_signatures).

---

## Prerequisites & external dependencies

Most skills run on Python 3 with common document/scientific libraries. A few need
external services, credentials, or model downloads — summarized here:

| Skill | External requirement |
|---|---|
| `fred-economic-data` | A free FRED API key in the `FRED_API_KEY` env var (from https://fredaccount.stlouisfed.org). Python: `requests`. |
| `cowork-visualizer` | The Notion MCP tool (`notion-create-pages`) for run-summary write-back. Optional: set `KNOWLEDGE_ARTIFACTS_DATA_SOURCE_ID` to target a different Notion database (defaults to the bundled KnowledgeArtifacts DB). |
| `timesfm-forecasting` | Downloads Google's TimesFM 2.5 model via `scripts/install.sh`. Optional Node.js MCP server under `mcp-server/`. Python: `numpy`, `pandas`, `matplotlib`. |
| `flex-pptx-creator` | Python: `python-pptx`, `lxml`; `playwright` (with a browser installed) for the HTML→PPTX image path. |
| `pl-intelligence-report` | Python: `openpyxl` (reads the Flex P&L `.xlsx`). |
| `ems-contract-analyzer` | Python: `python-docx` (reads/writes DOCX contracts). |
| `statistical-analysis` | Python: `numpy`, `pandas`, `scipy`, `matplotlib`, `seaborn`. |
| `shap`, `statsmodels` | The corresponding library (`shap` / `statsmodels`) plus the usual model/data stack — these skills are usage guides for those libraries. |

The remaining skills (`5d-engine`, `contract-intake-pipeline`,
`contract-portfolio-organizer`, `contract-twin-3d`, `ems-insurance-coverage-analyzer`,
`legal-pipeline-factory`, `litigation-history-analyzer`) require no external service or
credential; they use Python 3 with common document libraries (e.g. `python-docx` and a
PDF reader) for input/output.

---

## Package conventions & validation

All packages follow the Agent Skill format:

- A `.skill` file is a zip whose **single top-level directory** matches the skill `name`.
- That directory contains `SKILL.md` with YAML frontmatter providing `name` (lowercase,
  hyphenated) and `description`, plus the skill body.
- Supporting material lives under `scripts/`, `references/`, and `assets/`.

All 16 packages in this folder pass a structural check: each contains a single
correctly-named top-level directory with a `SKILL.md`, the frontmatter `name` matches both
the directory and the `.skill` filename, descriptions are within the 1024-character
guideline, and there are no stray build artifacts (`__pycache__`, `.pyc`, etc.).

Run the validator locally:

```bash
pip install pyyaml          # optional; falls back to a built-in parser if absent
python scripts/validate_skills.py
```

A companion smoke test extracts every package and byte-compiles the bundled scripts:

```bash
python scripts/smoke_test_skills.py
```

Both run in CI on every push and pull request via
[`.github/workflows/validate-skills.yml`](.github/workflows/validate-skills.yml), so
packaging and script-syntax regressions are caught automatically. See
[CONTRIBUTING.md](CONTRIBUTING.md) for the full conventions when adding or updating a
skill.
