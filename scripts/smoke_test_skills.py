#!/usr/bin/env python3
"""Smoke-test the .skill packages in this repository.

For every `*.skill` archive this script:
  1. verifies the zip is intact (CRC check),
  2. extracts it to a temporary directory,
  3. byte-compiles every bundled `*.py` file, and
  4. runs a `bash -n` syntax check on every bundled `*.sh` file (if `bash` is
     available on PATH).

This catches script-level breakage (syntax errors, truncated files) that the
structural validator in `validate_skills.py` does not. It exits non-zero if any
package fails, so it can gate CI.

Usage:
    python scripts/smoke_test_skills.py [root_dir]

Note: this does NOT install third-party dependencies, so it verifies syntax
only, not runtime behavior.
"""
from __future__ import annotations

import os
import py_compile
import shutil
import subprocess
import sys
import tempfile
import zipfile


def find_skills(root: str):
    out = []
    for dirpath, _, filenames in os.walk(root):
        if ".git" in dirpath.split(os.sep):
            continue
        for fn in filenames:
            if fn.endswith(".skill"):
                out.append(os.path.join(dirpath, fn))
    return sorted(out)


def main(argv):
    root = (
        argv[1]
        if len(argv) > 1
        else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    skills = find_skills(root)
    if not skills:
        print(f"No .skill files found under {root}")
        return 1

    bash_exe = shutil.which("bash")
    if bash_exe is None:
        print("note: 'bash' not found on PATH; skipping .sh syntax checks")

    failures = 0
    total_py = total_sh = 0
    work = tempfile.mkdtemp(prefix="skill-smoke-")
    try:
        for path in skills:
            rel = os.path.relpath(path, root).replace(os.sep, "/")
            issues = []
            try:
                with zipfile.ZipFile(path) as z:
                    bad = z.testzip()
                    if bad is not None:
                        issues.append(f"corrupt entry (CRC): {bad}")
                    dest = os.path.join(work, os.path.basename(path)[:-6])
                    z.extractall(dest)
            except zipfile.BadZipFile:
                issues.append("not a valid zip archive")
                dest = None

            if dest and os.path.isdir(dest):
                for dp, _, fns in os.walk(dest):
                    for fn in fns:
                        full = os.path.join(dp, fn)
                        if fn.endswith(".py"):
                            total_py += 1
                            try:
                                py_compile.compile(full, doraise=True)
                            except py_compile.PyCompileError as exc:
                                issues.append(
                                    f"py_compile failed: {fn}: "
                                    f"{str(exc).splitlines()[-1][:160]}"
                                )
                        elif fn.endswith(".sh") and bash_exe:
                            total_sh += 1
                            proc = subprocess.run(
                                [bash_exe, "-n", full],
                                capture_output=True,
                                text=True,
                            )
                            if proc.returncode != 0:
                                issues.append(
                                    f"bash -n failed: {fn}: "
                                    f"{proc.stderr.strip()[:160]}"
                                )

            if issues:
                failures += 1
                print(f"FAIL  {rel}")
                for i in issues:
                    print(f"        - {i}")
            else:
                print(f"OK    {rel}")
    finally:
        shutil.rmtree(work, ignore_errors=True)

    print()
    print(
        f"{len(skills) - failures}/{len(skills)} packages OK "
        f"(compiled {total_py} .py, checked {total_sh} .sh)."
    )
    if failures:
        print(f"{failures} package(s) FAILED smoke test.")
        return 1
    print("All skill packages passed the smoke test.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
