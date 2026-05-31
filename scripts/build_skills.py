#!/usr/bin/env python3
"""Build .skill zip archives from source directories.

For every ``<category>/<skill-name>/`` directory under the repo root that
contains a ``SKILL.md``, this script produces a ``<category>/<skill-name>.skill``
zip archive in the same category directory.  Stray build artifacts
(``__pycache__``, ``*.pyc``, ``.DS_Store``, ``.ipynb_checkpoints``) are excluded
so the produced archives pass ``validate_skills.py`` without complaint.

Existing ``.skill`` files that have *no* matching source directory are left
untouched — this script is additive, not a full rebuild of every archive in
the repo.

Usage::

    python scripts/build_skills.py [root_dir]

``root_dir`` defaults to the repository root (parent of the ``scripts/``
directory).
"""
from __future__ import annotations

import os
import pathlib
import sys
import zipfile

CATEGORY_DIRS = {"productivity", "data-science", "finance-forecasting", "legal-contracts"}
STRAY_PATTERNS = ("__pycache__", ".pyc", ".DS_Store", ".ipynb_checkpoints")


def find_skill_dirs(root: pathlib.Path):
    """Yield ``Path`` objects for every ``<category>/<name>/`` dir with a SKILL.md."""
    for cat in sorted(root.iterdir()):
        if not cat.is_dir() or cat.name not in CATEGORY_DIRS:
            continue
        for skill_dir in sorted(cat.iterdir()):
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                yield skill_dir


def is_stray(path: pathlib.Path) -> bool:
    return any(pat in str(path) for pat in STRAY_PATTERNS)


def build_skill(skill_dir: pathlib.Path) -> pathlib.Path:
    """Zip *skill_dir* into ``<parent>/<name>.skill``; return the archive path."""
    skill_name = skill_dir.name
    out_path = skill_dir.parent / f"{skill_name}.skill"
    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for filepath in sorted(skill_dir.rglob("*")):
            if not filepath.is_file():
                continue
            if is_stray(filepath):
                continue
            arcname = f"{skill_name}/{filepath.relative_to(skill_dir)}"
            zf.write(filepath, arcname)
    return out_path


def main(argv: list[str]) -> int:
    root = (
        pathlib.Path(argv[1])
        if len(argv) > 1
        else pathlib.Path(__file__).resolve().parent.parent
    )
    built = 0
    for skill_dir in find_skill_dirs(root):
        out = build_skill(skill_dir)
        rel = out.relative_to(root)
        print(f"Built  {rel}")
        built += 1
    if built == 0:
        print("No skill source directories found.")
    else:
        print(f"\n{built} .skill archive(s) built.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
