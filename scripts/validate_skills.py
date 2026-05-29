#!/usr/bin/env python3
"""Validate the .skill packages in this repository.

A `.skill` file is a zip archive that must contain a single top-level directory
named after the skill, with a `SKILL.md` at its root. `SKILL.md` must have YAML
frontmatter providing a `name` (lowercase, hyphenated) and a `description`.

This script checks every `*.skill` file under the repo root and reports problems.
It exits non-zero if any package fails, so it can gate CI.

Usage:
    python scripts/validate_skills.py [root_dir]

Requires PyYAML if available (for exact frontmatter parsing); otherwise falls
back to a small built-in parser sufficient for these packages.
"""
from __future__ import annotations

import os
import re
import sys
import zipfile

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_NAME_LEN = 64
MAX_DESC_LEN = 1024
STRAY_MARKERS = ("__pycache__", ".pyc", ".DS_Store", "/.ipynb_checkpoints/")

try:
    import yaml  # type: ignore

    def parse_frontmatter(text: str):
        if not text.startswith("---"):
            return None, "no YAML frontmatter"
        end = text.find("\n---", 3)
        if end == -1:
            return None, "unterminated frontmatter"
        try:
            data = yaml.safe_load(text[3:end]) or {}
        except yaml.YAMLError as exc:  # pragma: no cover - defensive
            return None, f"invalid YAML frontmatter: {exc}"
        if not isinstance(data, dict):
            return None, "frontmatter is not a mapping"
        return data, None

except ImportError:  # pragma: no cover - fallback path

    def parse_frontmatter(text: str):
        if not text.startswith("---"):
            return None, "no YAML frontmatter"
        end = text.find("\n---", 3)
        if end == -1:
            return None, "unterminated frontmatter"
        fm = text[3:end]
        data = {}
        m = re.search(r"^name:\s*(.+)$", fm, re.MULTILINE)
        if m:
            data["name"] = m.group(1).strip().strip('"').strip("'")
        dm = re.search(
            r"^description:(.*?)(?=^\w[\w-]*:|\Z)", fm, re.MULTILINE | re.DOTALL
        )
        if dm:
            desc = re.sub(r"^\s*[>|]\s*", "", dm.group(1)).strip().strip('"').strip("'")
            data["description"] = re.sub(r"\s+", " ", desc)
        return data, None


def find_skills(root: str):
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        if ".git" in dirpath.split(os.sep):
            continue
        for fn in filenames:
            if fn.endswith(".skill"):
                out.append(os.path.join(dirpath, fn))
    return sorted(out)


def validate(path: str, root: str):
    rel = os.path.relpath(path, root).replace(os.sep, "/")
    issues = []
    try:
        zf = zipfile.ZipFile(path)
    except zipfile.BadZipFile:
        return rel, ["not a valid zip archive"]

    with zf as z:
        names = [n for n in z.namelist() if n.strip()]
        skillmds = [n for n in names if n.endswith("SKILL.md")]
        text = (
            z.open(skillmds[0]).read().decode("utf-8", "replace") if skillmds else None
        )

    tops = sorted({n.split("/")[0] for n in names})
    strays = [n for n in names if any(m in n for m in STRAY_MARKERS)]

    if "SKILL.md" in names:
        issues.append("SKILL.md at archive root (no top-level skill directory)")
    if len(tops) > 1:
        issues.append(f"multiple top-level entries: {tops}")
    if strays:
        issues.append(f"stray build artifacts: {strays}")

    base = os.path.basename(path)[: -len(".skill")]
    if " " in base or "(" in base or ")" in base:
        issues.append(f"filename not clean (spaces/parens): {base!r}")

    if not skillmds:
        issues.append("no SKILL.md found")
        return rel, issues

    data, err = parse_frontmatter(text)
    if err:
        issues.append(err)
        return rel, issues

    name = data.get("name")
    desc = data.get("description")
    dirname = skillmds[0].split("/")[0] if "/" in skillmds[0] else "(root)"

    if not name:
        issues.append("missing 'name' in frontmatter")
    else:
        name = str(name)
        if not NAME_RE.match(name):
            issues.append(f"name fails ^[a-z0-9]+(-[a-z0-9]+)*$: {name!r}")
        if len(name) > MAX_NAME_LEN:
            issues.append(f"name exceeds {MAX_NAME_LEN} chars")
        if dirname != name:
            issues.append(f"top-level dir {dirname!r} != name {name!r}")
        if base != name:
            issues.append(f".skill filename {base!r} != name {name!r}")

    if not desc:
        issues.append("missing 'description' in frontmatter")
    elif len(str(desc)) > MAX_DESC_LEN:
        issues.append(f"description exceeds {MAX_DESC_LEN} chars ({len(str(desc))})")

    return rel, issues


def main(argv):
    root = argv[1] if len(argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    skills = find_skills(root)
    if not skills:
        print(f"No .skill files found under {root}")
        return 1

    failures = 0
    for path in skills:
        rel, issues = validate(path, root)
        if issues:
            failures += 1
            print(f"FAIL  {rel}")
            for i in issues:
                print(f"        - {i}")
        else:
            print(f"OK    {rel}")

    print()
    print(f"{len(skills) - failures}/{len(skills)} packages valid.")
    if failures:
        print(f"{failures} package(s) FAILED validation.")
        return 1
    print("All skill packages are valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
