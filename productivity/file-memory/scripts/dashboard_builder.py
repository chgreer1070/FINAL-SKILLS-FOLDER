#!/usr/bin/env python3
"""Generate a self-contained HTML dashboard from .ai-memory/ data."""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def _memory_dir(root: str) -> Path:
    return Path(root) / ".ai-memory"


def _load_data(root: str, limit_files: int, limit_sessions: int) -> dict:
    mem_dir = _memory_dir(root)
    index_path = mem_dir / "index.json"

    index: dict = {}
    if index_path.exists():
        index = json.loads(index_path.read_text())

    # Load full file entries (richer than index stubs)
    files_dir = mem_dir / "files"
    full_files = []
    if files_dir.exists():
        for p in sorted(files_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
            try:
                full_files.append(json.loads(p.read_text()))
            except Exception:
                pass
    full_files = full_files[:limit_files]

    # Load sessions (most recent first)
    sessions_dir = mem_dir / "sessions"
    sessions = []
    if sessions_dir.exists():
        for p in sorted(sessions_dir.glob("sess-*.json"), reverse=True):
            try:
                sessions.append(json.loads(p.read_text()))
            except Exception:
                pass
    sessions = sessions[:limit_sessions]

    return {
        "files": full_files,
        "sessions": sessions,
        "project_root": str(Path(root).resolve()),
        "file_count": index.get("file_count", len(full_files)),
        "session_count": index.get("session_count", len(sessions)),
        "last_updated": index.get("last_updated", ""),
    }


def build_dashboard(root: str, out: str, title: str | None, limit_files: int, limit_sessions: int) -> Path:
    template_path = Path(__file__).parent.parent / "assets" / "dashboard_template.html"
    if not template_path.exists():
        print(f"error: dashboard template not found at {template_path}", file=sys.stderr)
        sys.exit(1)

    data = _load_data(root, limit_files, limit_sessions)
    project_name = Path(root).resolve().name
    dash_title = title or f"AI File Memory — {project_name}"

    html = template_path.read_text(encoding="utf-8")

    # Inject title
    html = html.replace("<title>AI File Memory Dashboard</title>", f"<title>{dash_title}</title>")

    # Inject data by replacing the placeholder line
    data_script = f"const MEMORY_DATA = {json.dumps(data, indent=2)};"
    html = html.replace(
        'const MEMORY_DATA = {"files":[],"sessions":[],"project_root":"","file_count":0,"session_count":0};',
        data_script,
    )

    out_path = Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    return out_path


def open_browser(path: Path) -> None:
    import platform
    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.run(["open", str(path)], check=True)
        elif system == "Linux":
            subprocess.run(["xdg-open", str(path)], check=False)
        elif system == "Windows":
            os.startfile(str(path))
    except Exception:
        pass


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate file memory HTML dashboard")
    parser.add_argument("--root", default=".")
    parser.add_argument("--out", default=".ai-memory/dashboard.html")
    parser.add_argument("--title")
    parser.add_argument("--limit-files", type=int, default=50)
    parser.add_argument("--limit-sessions", type=int, default=10)
    parser.add_argument("--open", action="store_true")
    args = parser.parse_args()

    out_path = build_dashboard(args.root, args.out, args.title, args.limit_files, args.limit_sessions)
    print(f"dashboard written: {out_path}")

    if args.open:
        open_browser(out_path)
        print("opening in browser…")


if __name__ == "__main__":
    main()
