#!/usr/bin/env python3
"""Session journal — start/end/track decisions and file touches across Claude sessions."""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def _memory_dir(root: str) -> Path:
    return Path(root) / ".ai-memory"


def _sessions_dir(root: str) -> Path:
    return _memory_dir(root) / "sessions"


def _session_path(root: str, session_id: str) -> Path:
    return _sessions_dir(root) / f"{session_id}.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _next_session_id(root: str) -> str:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    sessions_dir = _sessions_dir(root)
    if not sessions_dir.exists():
        return f"sess-{today}-001"
    existing = sorted(
        p.stem for p in sessions_dir.glob(f"sess-{today}-*.json")
    )
    if not existing:
        return f"sess-{today}-001"
    last_num = int(existing[-1].split("-")[-1])
    return f"sess-{today}-{last_num + 1:03d}"


def _read_session(root: str, session_id: str) -> dict:
    path = _session_path(root, session_id)
    if not path.exists():
        print(f"error: session '{session_id}' not found", file=sys.stderr)
        sys.exit(1)
    return json.loads(path.read_text())


def _write_session(root: str, session_id: str, data: dict) -> None:
    sessions_dir = _sessions_dir(root)
    sessions_dir.mkdir(parents=True, exist_ok=True)
    path = _session_path(root, session_id)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2))
    tmp.rename(path)


def _update_index(root: str) -> None:
    index_path = _memory_dir(root) / "index.json"
    if not index_path.exists():
        return
    index = json.loads(index_path.read_text())
    sessions_dir = _sessions_dir(root)
    count = len(list(sessions_dir.glob("sess-*.json"))) if sessions_dir.exists() else 0
    index["session_count"] = count
    index["last_updated"] = _now()
    tmp = index_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(index, indent=2))
    tmp.rename(index_path)


def cmd_start(args: argparse.Namespace) -> None:
    root = args.root
    session_id = args.session_id or _next_session_id(root)
    data = {
        "version": "1.0",
        "session_id": session_id,
        "started_at": _now(),
        "ended_at": None,
        "goal": args.goal,
        "files_touched": [],
        "decisions": [],
        "outcomes": [],
        "tags": [],
    }
    _write_session(root, session_id, data)
    _update_index(root)
    print(session_id)


def cmd_end(args: argparse.Namespace) -> None:
    data = _read_session(args.root, args.session_id)
    data["ended_at"] = _now()
    if args.outcomes:
        data["outcomes"].extend([o.strip() for o in args.outcomes.split(",") if o.strip()])
    _write_session(args.root, args.session_id, data)
    print(f"session {args.session_id} closed")


def cmd_add_decision(args: argparse.Namespace) -> None:
    data = _read_session(args.root, args.session_id)
    data["decisions"].append({
        "timestamp": _now(),
        "decision": args.decision,
        "rationale": args.rationale,
    })
    _write_session(args.root, args.session_id, data)
    print("decision recorded")


def cmd_add_file(args: argparse.Namespace) -> None:
    data = _read_session(args.root, args.session_id)
    already = {f["path"] for f in data["files_touched"]}
    if args.file not in already:
        slug = args.file.replace("/", "-").replace("\\", "-").replace(".", "-").lower().lstrip("-")
        data["files_touched"].append({
            "path": args.file,
            "slug": slug,
            "action": args.action,
        })
        _write_session(args.root, args.session_id, data)
    print(f"recorded: {args.file}")


def cmd_show(args: argparse.Namespace) -> None:
    data = _read_session(args.root, args.session_id)
    print(json.dumps(data, indent=2))


def cmd_list(args: argparse.Namespace) -> None:
    sessions_dir = _sessions_dir(args.root)
    if not sessions_dir.exists():
        print("no sessions found")
        return
    sessions = sorted(sessions_dir.glob("sess-*.json"), reverse=True)
    limit = args.limit or 20
    print(f"{'Session ID':<30} {'Goal':<45} {'Duration':>10} {'Files':>6}")
    print("-" * 95)
    for p in sessions[:limit]:
        s = json.loads(p.read_text())
        goal = (s.get("goal") or "")[:44]
        files = len(s.get("files_touched", []))
        started = s.get("started_at", "")
        ended = s.get("ended_at")
        if started and ended:
            from datetime import datetime
            try:
                s_dt = datetime.fromisoformat(started.replace("Z", "+00:00"))
                e_dt = datetime.fromisoformat(ended.replace("Z", "+00:00"))
                secs = int((e_dt - s_dt).total_seconds())
                dur = f"{secs // 60}m {secs % 60}s"
            except Exception:
                dur = "?"
        else:
            dur = "ongoing"
        print(f"{s['session_id']:<30} {goal:<45} {dur:>10} {files:>6}")


def cmd_latest(args: argparse.Namespace) -> None:
    sessions_dir = _sessions_dir(args.root)
    if not sessions_dir.exists():
        print("", end="")
        return
    sessions = sorted(sessions_dir.glob("sess-*.json"), reverse=True)
    if not sessions:
        print("", end="")
        return
    s = json.loads(sessions[0].read_text())
    print(s["session_id"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Session journal for file-memory skill")
    sub = parser.add_subparsers(dest="command", required=True)

    p_start = sub.add_parser("start")
    p_start.add_argument("--goal", required=True)
    p_start.add_argument("--session-id")
    p_start.add_argument("--root", default=".")

    p_end = sub.add_parser("end")
    p_end.add_argument("--session-id", required=True)
    p_end.add_argument("--outcomes")
    p_end.add_argument("--root", default=".")

    p_dec = sub.add_parser("add-decision")
    p_dec.add_argument("--session-id", required=True)
    p_dec.add_argument("--decision", required=True)
    p_dec.add_argument("--rationale", required=True)
    p_dec.add_argument("--root", default=".")

    p_af = sub.add_parser("add-file")
    p_af.add_argument("--session-id", required=True)
    p_af.add_argument("--file", required=True)
    p_af.add_argument("--action", default="modified", choices=["modified", "created", "deleted"])
    p_af.add_argument("--root", default=".")

    p_show = sub.add_parser("show")
    p_show.add_argument("--session-id", required=True)
    p_show.add_argument("--root", default=".")

    p_list = sub.add_parser("list")
    p_list.add_argument("--root", default=".")
    p_list.add_argument("--limit", type=int)

    p_latest = sub.add_parser("latest")
    p_latest.add_argument("--root", default=".")

    args = parser.parse_args()
    dispatch = {
        "start": cmd_start,
        "end": cmd_end,
        "add-decision": cmd_add_decision,
        "add-file": cmd_add_file,
        "show": cmd_show,
        "list": cmd_list,
        "latest": cmd_latest,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
