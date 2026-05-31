# .ai-memory/ Schema Reference

## Directory Layout

```
<project_root>/
└── .ai-memory/
    ├── index.json                    # Master registry of all remembered files
    ├── files/
    │   └── <slug>.json              # One file per remembered file
    ├── sessions/
    │   └── sess-YYYY-MM-DD-NNN.json # One file per session journal
    └── .embeddings_cache.pkl        # Optional: TF-IDF/semantic search cache
```

Add `.ai-memory/` to `.gitignore` to keep memory private, or commit it to share team context.

---

## index.json

```json
{
  "version": "1.0",
  "last_updated": "2026-05-31T14:22:00Z",
  "project_root": "/home/user/myproject",
  "file_count": 12,
  "session_count": 7,
  "files": [
    {
      "slug": "src-app-py",
      "path": "src/app.py",
      "label": "Main application entry point",
      "last_seen": "2026-05-31T14:20:00Z",
      "first_seen": "2026-05-28T09:00:00Z",
      "session_count": 3,
      "tag_summary": ["fastapi", "auth", "routing"]
    }
  ]
}
```

The `files` array is a lightweight index — use `files/<slug>.json` for the full entry.

---

## files/\<slug\>.json

Slug derivation: lowercase the relative path, replace `/` and `.` with `-`, strip leading separators. Examples:
- `src/app.py` → `src-app-py`
- `tests/utils.py` → `tests-utils-py`
- `README.md` → `readme-md`

```json
{
  "version": "1.0",
  "slug": "src-app-py",
  "path": "src/app.py",
  "label": "Main application entry point",
  "first_seen": "2026-05-28T09:00:00Z",
  "last_seen": "2026-05-31T14:20:00Z",
  "summary": "FastAPI app with JWT auth, 3 routers (users, items, admin). Entry point calls create_app() factory. Uses lifespan context manager for DB connection pooling.",
  "notes": [
    {
      "timestamp": "2026-05-28T09:05:00Z",
      "session_id": "sess-2026-05-28-001",
      "note": "Added rate limiting via slowapi. Chose slowapi over custom for Redis compatibility."
    }
  ],
  "change_history": [
    {
      "timestamp": "2026-05-28T09:05:00Z",
      "session_id": "sess-2026-05-28-001",
      "change_type": "modified",
      "description": "Added slowapi rate limiting middleware",
      "lines_added": 14,
      "lines_removed": 2
    }
  ],
  "tags": ["fastapi", "auth", "routing", "middleware"],
  "related_files": ["src/auth.py", "src/routers/users.py"],
  "language": "python",
  "importance": "high"
}
```

**Field reference:**

| Field | Type | Description |
|---|---|---|
| `slug` | string | Unique ID derived from path (see above) |
| `path` | string | Relative path from project root, forward slashes |
| `label` | string | First 80 chars of summary — used in index and dashboard |
| `summary` | string | 2–4 sentence description of the file's purpose |
| `notes` | array | Timestamped notes added manually or by Claude |
| `change_history` | array | History of edits logged during sessions |
| `tags` | array | 3–8 keyword tags |
| `related_files` | array | Relative paths of related files |
| `language` | string | Detected language from extension |
| `importance` | string | `high`, `normal`, or `low` |

---

## sessions/sess-YYYY-MM-DD-NNN.json

Session ID format: `sess-2026-05-31-001` (date + zero-padded counter for same-day sessions).

```json
{
  "version": "1.0",
  "session_id": "sess-2026-05-31-001",
  "started_at": "2026-05-31T13:45:00Z",
  "ended_at": "2026-05-31T14:22:00Z",
  "goal": "Refactor app startup to use FastAPI lifespan context manager",
  "files_touched": [
    { "path": "src/app.py", "slug": "src-app-py", "action": "modified" }
  ],
  "decisions": [
    {
      "timestamp": "2026-05-31T13:55:00Z",
      "decision": "Use lifespan instead of @app.on_event",
      "rationale": "FastAPI deprecated on_event in 0.93; lifespan is the idiomatic replacement."
    }
  ],
  "outcomes": [
    "Removed 2 deprecated @app.on_event handlers",
    "All 24 tests passing"
  ],
  "tags": ["refactor", "fastapi", "startup"]
}
```

**Field reference:**

| Field | Type | Description |
|---|---|---|
| `session_id` | string | Unique ID in `sess-YYYY-MM-DD-NNN` format |
| `started_at` | ISO 8601 UTC | When the session started |
| `ended_at` | ISO 8601 UTC or null | When the session ended (null = ongoing) |
| `goal` | string | What the session was trying to accomplish |
| `files_touched` | array | Files read, modified, or created during the session |
| `decisions` | array | Notable decisions with rationale |
| `outcomes` | array | What was accomplished (string list) |
| `tags` | array | Keywords for the session |

---

## Manual Editing

All files are plain JSON — you can edit them directly in any text editor. The scripts perform atomic writes (write-to-temp, rename) so manual edits between script calls are safe as long as you don't write while a script is running.
