#!/usr/bin/env python3
"""Per-file memory manager — CRUD for .ai-memory/files/ entries."""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def _memory_dir(root: str) -> Path:
    return Path(root) / ".ai-memory"


def _files_dir(root: str) -> Path:
    return _memory_dir(root) / "files"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _make_slug(filepath: str) -> str:
    norm = filepath.replace("\\", "/").lower().lstrip("./")
    slug = norm.replace("/", "-").replace(".", "-").strip("-")
    # Ensure uniqueness for edge cases with a short hash suffix only on collision
    return slug or hashlib.md5(filepath.encode()).hexdigest()[:8]


def _index_path(root: str) -> Path:
    return _memory_dir(root) / "index.json"


def _read_index(root: str) -> dict:
    p = _index_path(root)
    if p.exists():
        return json.loads(p.read_text())
    return {
        "version": "1.0",
        "last_updated": _now(),
        "project_root": str(Path(root).resolve()),
        "file_count": 0,
        "session_count": 0,
        "files": [],
    }


def _write_index(root: str, index: dict) -> None:
    _memory_dir(root).mkdir(parents=True, exist_ok=True)
    p = _index_path(root)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(index, indent=2))
    tmp.rename(p)


def _read_file_entry(root: str, slug: str) -> dict | None:
    p = _files_dir(root) / f"{slug}.json"
    if p.exists():
        return json.loads(p.read_text())
    return None


def _write_file_entry(root: str, slug: str, entry: dict) -> None:
    files_dir = _files_dir(root)
    files_dir.mkdir(parents=True, exist_ok=True)
    p = files_dir / f"{slug}.json"
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(entry, indent=2))
    tmp.rename(p)


def _update_index_entry(root: str, slug: str, filepath: str, label: str, tags: list) -> None:
    index = _read_index(root)
    now = _now()
    existing = next((f for f in index["files"] if f["slug"] == slug), None)
    if existing:
        existing["last_seen"] = now
        existing["label"] = label
        existing["tag_summary"] = tags[:3]
    else:
        index["files"].append({
            "slug": slug,
            "path": filepath,
            "label": label,
            "last_seen": now,
            "first_seen": now,
            "session_count": 1,
            "tag_summary": tags[:3],
        })
        index["file_count"] = len(index["files"])
    index["last_updated"] = now
    _write_index(root, index)


def cmd_remember(args: argparse.Namespace) -> None:
    filepath = args.file.replace("\\", "/")
    slug = _make_slug(filepath)
    now = _now()

    existing = _read_file_entry(args.root, slug)
    first_seen = existing["first_seen"] if existing else now

    tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []
    related = [r.strip() for r in args.related.split(",") if r.strip()] if args.related else []

    entry = {
        "version": "1.0",
        "slug": slug,
        "path": filepath,
        "label": args.summary[:80] if args.summary else filepath,
        "first_seen": first_seen,
        "last_seen": now,
        "summary": args.summary or "",
        "notes": existing.get("notes", []) if existing else [],
        "change_history": existing.get("change_history", []) if existing else [],
        "tags": tags,
        "related_files": related,
        "language": _detect_language(filepath),
        "importance": args.importance or "normal",
    }

    if args.note:
        entry["notes"].append({
            "timestamp": now,
            "session_id": args.session_id or "",
            "note": args.note,
        })

    _write_file_entry(args.root, slug, entry)
    _update_index_entry(args.root, slug, filepath, entry["label"], tags)
    print(slug)


def cmd_update(args: argparse.Namespace) -> None:
    filepath = args.file.replace("\\", "/")
    slug = _make_slug(filepath)
    existing = _read_file_entry(args.root, slug)
    if not existing:
        print(f"error: no memory entry for '{args.file}'. Use 'remember' first.", file=sys.stderr)
        sys.exit(1)
    existing["notes"].append({
        "timestamp": _now(),
        "session_id": args.session_id or "",
        "note": args.note,
    })
    existing["last_seen"] = _now()
    _write_file_entry(args.root, slug, existing)
    print("note added")


def cmd_log_change(args: argparse.Namespace) -> None:
    filepath = args.file.replace("\\", "/")
    slug = _make_slug(filepath)
    existing = _read_file_entry(args.root, slug)
    if not existing:
        # Auto-create a minimal entry
        now = _now()
        existing = {
            "version": "1.0",
            "slug": slug,
            "path": filepath,
            "label": filepath,
            "first_seen": now,
            "last_seen": now,
            "summary": "",
            "notes": [],
            "change_history": [],
            "tags": [],
            "related_files": [],
            "language": _detect_language(filepath),
            "importance": "normal",
        }
        _update_index_entry(args.root, slug, filepath, filepath, [])

    change = {
        "timestamp": _now(),
        "session_id": args.session_id or "",
        "change_type": args.change_type,
        "description": args.description,
    }
    if args.lines_added is not None:
        change["lines_added"] = args.lines_added
    if args.lines_removed is not None:
        change["lines_removed"] = args.lines_removed

    existing["change_history"].append(change)
    existing["last_seen"] = _now()
    _write_file_entry(args.root, slug, existing)
    print("change logged")


def cmd_show(args: argparse.Namespace) -> None:
    filepath = args.file.replace("\\", "/")
    slug = _make_slug(filepath)
    entry = _read_file_entry(args.root, slug)
    if not entry:
        print(f"error: no memory entry for '{args.file}'", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(entry, indent=2))


def cmd_list(args: argparse.Namespace) -> None:
    index = _read_index(args.root)
    files = index.get("files", [])
    if args.importance:
        files_dir = _files_dir(args.root)
        filtered = []
        for f in files:
            entry_path = files_dir / f"{f['slug']}.json"
            if entry_path.exists():
                e = json.loads(entry_path.read_text())
                if e.get("importance") == args.importance:
                    filtered.append(f)
        files = filtered
    if args.tag:
        files_dir = _files_dir(args.root)
        tagged = []
        for f in files:
            entry_path = files_dir / f"{f['slug']}.json"
            if entry_path.exists():
                e = json.loads(entry_path.read_text())
                if args.tag in e.get("tags", []):
                    tagged.append(f)
        files = tagged
    limit = args.limit or len(files)
    files = files[:limit]
    if not files:
        print("no files in memory")
        return
    print(f"{'Slug':<30} {'Path':<45} {'Last Seen':<25} {'Importance'}")
    print("-" * 110)
    for f in files:
        print(f"{f['slug']:<30} {f['path']:<45} {f.get('last_seen',''):<25} {f.get('importance','normal')}")


def cmd_forget(args: argparse.Namespace) -> None:
    filepath = args.file.replace("\\", "/")
    slug = _make_slug(filepath)
    p = _files_dir(args.root) / f"{slug}.json"
    if not p.exists():
        print(f"error: no memory entry for '{args.file}'", file=sys.stderr)
        sys.exit(1)
    p.unlink()
    index = _read_index(args.root)
    index["files"] = [f for f in index["files"] if f["slug"] != slug]
    index["file_count"] = len(index["files"])
    index["last_updated"] = _now()
    _write_index(args.root, index)
    print(f"forgot: {filepath}")


def _detect_language(filepath: str) -> str:
    ext_map = {
        ".py": "python", ".js": "javascript", ".ts": "typescript",
        ".tsx": "typescript", ".jsx": "javascript", ".go": "go",
        ".rs": "rust", ".java": "java", ".rb": "ruby", ".php": "php",
        ".cs": "csharp", ".cpp": "cpp", ".c": "c", ".h": "c",
        ".sh": "bash", ".md": "markdown", ".json": "json",
        ".yaml": "yaml", ".yml": "yaml", ".toml": "toml",
        ".html": "html", ".css": "css", ".sql": "sql",
    }
    ext = Path(filepath).suffix.lower()
    return ext_map.get(ext, "text")


def main() -> None:
    parser = argparse.ArgumentParser(description="File memory manager for file-memory skill")
    sub = parser.add_subparsers(dest="command", required=True)

    p_rem = sub.add_parser("remember")
    p_rem.add_argument("--file", required=True)
    p_rem.add_argument("--summary", required=True)
    p_rem.add_argument("--note")
    p_rem.add_argument("--tags")
    p_rem.add_argument("--importance", choices=["high", "normal", "low"], default="normal")
    p_rem.add_argument("--related")
    p_rem.add_argument("--session-id")
    p_rem.add_argument("--root", default=".")

    p_upd = sub.add_parser("update")
    p_upd.add_argument("--file", required=True)
    p_upd.add_argument("--note", required=True)
    p_upd.add_argument("--session-id")
    p_upd.add_argument("--root", default=".")

    p_lc = sub.add_parser("log-change")
    p_lc.add_argument("--file", required=True)
    p_lc.add_argument("--change-type", required=True, choices=["modified", "created", "deleted"])
    p_lc.add_argument("--description", required=True)
    p_lc.add_argument("--lines-added", type=int)
    p_lc.add_argument("--lines-removed", type=int)
    p_lc.add_argument("--session-id")
    p_lc.add_argument("--root", default=".")

    p_show = sub.add_parser("show")
    p_show.add_argument("--file", required=True)
    p_show.add_argument("--root", default=".")

    p_list = sub.add_parser("list")
    p_list.add_argument("--root", default=".")
    p_list.add_argument("--tag")
    p_list.add_argument("--importance", choices=["high", "normal", "low"])
    p_list.add_argument("--limit", type=int)

    p_forget = sub.add_parser("forget")
    p_forget.add_argument("--file", required=True)
    p_forget.add_argument("--root", default=".")

    args = parser.parse_args()
    dispatch = {
        "remember": cmd_remember,
        "update": cmd_update,
        "log-change": cmd_log_change,
        "show": cmd_show,
        "list": cmd_list,
        "forget": cmd_forget,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
