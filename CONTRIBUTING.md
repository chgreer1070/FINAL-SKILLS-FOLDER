# Contributing

This repository hosts Agent Skill packages (`.skill` files). Each is a zip
archive with a single top-level directory named after the skill, containing a
`SKILL.md` plus optional `scripts/`, `references/`, and `assets/`.

## Adding or updating a skill

1. Place the `.skill` file in the category folder that best fits it:
   `legal-contracts/`, `finance-forecasting/`, `data-science/`, or
   `productivity/`. (See the [README](README.md) for what each category holds.)
2. Make sure the package follows the conventions below, then add a row to the
   README's skill list and, if it needs external setup, the
   **Prerequisites & external dependencies** table.
3. Run the checks locally (see below) before opening a PR.

## Packaging conventions

A `.skill` file must satisfy all of the following — these are enforced in CI:

- The archive contains exactly **one top-level directory**, and its name equals
  the skill `name`.
- `SKILL.md` lives at the **root of that directory** (`<name>/SKILL.md`), not
  nested deeper.
- `SKILL.md` starts with YAML frontmatter providing:
  - `name` — lowercase, hyphenated, matching `^[a-z0-9]+(-[a-z0-9]+)*$`, and
    equal to both the top-level directory and the `.skill` filename.
  - `description` — at most 1024 characters.
- The `.skill` filename has no spaces or `(1)`-style duplicate-download suffixes.
- No stray build artifacts are bundled (`__pycache__/`, `*.pyc`, `.DS_Store`,
  `.ipynb_checkpoints/`).
- Reference paths inside `SKILL.md` should be **relative** to the skill
  directory (e.g. `references/foo.md`), not absolute install paths.

## Running the checks locally

```bash
pip install pyyaml                  # optional; a built-in parser is used if absent
python scripts/validate_skills.py   # structural / frontmatter checks
python scripts/smoke_test_skills.py # extracts each package, byte-compiles scripts
```

Both scripts exit non-zero on failure and run automatically on every push and
pull request via
[`.github/workflows/validate-skills.yml`](.github/workflows/validate-skills.yml).

The smoke test verifies that bundled Python scripts compile and shell scripts
pass `bash -n`; it does **not** install third-party dependencies, so it checks
syntax only, not runtime behavior.

## Repackaging a skill

If you edit files inside a skill, rebuild the `.skill` zip so the single
top-level `<name>/` directory is preserved and no `__pycache__`/`.pyc` artifacts
are included. For example:

```bash
cd <name>/..            # directory that contains the <name>/ folder
zip -r ../<name>.skill <name> -x '*__pycache__*' '*.pyc'
```
