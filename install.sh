#!/usr/bin/env bash
# One-time setup: installs file-memory skill globally so every Claude Code
# session in every repo automatically has persistent file memory.
# Run once: bash install.sh

set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_ZIP="$REPO_DIR/productivity/file-memory.skill"
SKILLS_DIR="$HOME/.claude/skills"
SKILL_DST="$SKILLS_DIR/file-memory"
CLAUDE_MD="$HOME/.claude/CLAUDE.md"

echo "Installing file-memory skill..."

# The skill ships as a .skill zip package (the repo convention); extract it
# rather than copying a loose source tree.
if [ ! -f "$SKILL_ZIP" ]; then
  echo "  ✗ Could not find $SKILL_ZIP" >&2
  echo "    Run this script from inside the FINAL-SKILLS-FOLDER checkout." >&2
  exit 1
fi

# The skill's scripts run on Python 3, which is also used to unpack the package.
if ! command -v python3 >/dev/null 2>&1; then
  echo "  ✗ python3 is required (the file-memory scripts run on Python 3)." >&2
  exit 1
fi

# Extract <zip>/file-memory/... into ~/.claude/skills/file-memory/ (clean refresh).
mkdir -p "$SKILLS_DIR"
rm -rf "$SKILL_DST"
python3 - "$SKILL_ZIP" "$SKILLS_DIR" <<'PY'
import sys, zipfile
zip_path, dest = sys.argv[1], sys.argv[2]
with zipfile.ZipFile(zip_path) as z:
    z.extractall(dest)
PY
echo "  ✓ Skill installed to $SKILL_DST"

# Write global CLAUDE.md (or append if one already exists with different content)
if [ -f "$CLAUDE_MD" ] && grep -q "File Memory" "$CLAUDE_MD" 2>/dev/null; then
  echo "  ✓ Global CLAUDE.md already contains file-memory instructions — skipping"
else
  mkdir -p "$(dirname "$CLAUDE_MD")"
  cat >> "$CLAUDE_MD" << 'GLOBALMD'

## File Memory — Always Active

Every session in every project automatically uses file memory.

### On every session start

1. Check if `.ai-memory/` exists in the current project directory.
2. If it exists:
   - Run: `python3 ~/.claude/skills/file-memory/scripts/session_journal.py start --goal "New session" --root .`
   - Save the printed session ID as `<current_session_id>` for this session.
   - Run: `python3 ~/.claude/skills/file-memory/scripts/memory_manager.py list --root .`
   - Load the file list silently — do not print it.
   - Tell the user: "File memory loaded — I remember N files and M sessions for this project."
3. If `.ai-memory/` does not exist:
   - Say nothing about memory unless the user asks.
   - When the user opens or edits the first file, silently create `.ai-memory/` and start tracking.

### During every session

- Whenever you read, modify, or create any file: silently run `memory_manager.py log-change` for that file.
- If the file has no memory entry yet: silently run `memory_manager.py remember` to create one.
- Silently run `session_journal.py add-file` to record the file was touched.
- When the user makes a notable decision: silently run `session_journal.py add-decision`.
- Never narrate these background actions.

### On every session end

When the user says goodbye, "done", "that's all", or ends the conversation:
1. Run: `python3 ~/.claude/skills/file-memory/scripts/session_journal.py end --session-id <current_session_id> --root .`
2. Tell the user: "Session saved — memory updated."

### Commands you can say to Claude any time

- "What do you know about [file]?" — recalls full memory for that file
- "Search my memory for [topic]" — searches across all remembered files
- "Show me the memory dashboard" — generates a visual HTML summary
- "Session recap" — summarizes what happened this session
- "Remember this file" — explicitly saves the current file with notes
GLOBALMD
  echo "  ✓ Global CLAUDE.md updated at $CLAUDE_MD"
fi

echo ""
echo "Done. File memory is now active in every Claude Code session."
echo "No further setup needed — open any project and it just works."
