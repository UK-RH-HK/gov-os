#!/usr/bin/env python3
"""
PreCompact hook (W1-49, light form of CAP-37; W1-29 replaces it).

Checks that the checkpoint is current before a compaction (DEC-258):
the orchestrator's in the main tree, the lead's in a linked worktree.
Current means the file exists and is at most 30 minutes old. Acts only
when GOV_ROLE is exactly "orchestrator" (DEC-259).

Exit codes:
- 0 with no stdout       -> the compaction proceeds
- 0 with JSON on stdout  -> automatic compaction over a checkpoint
  that is not current: it proceeds, systemMessage tells the user
- 2 with stderr          -> manual compaction over a checkpoint that
  is not current: blocked, stderr is the reason

The hook's own failure never blocks: it ends with 0.
"""

from __future__ import annotations

import json
import os
import sys
import time

MAX_AGE_S = 30 * 60
NOT_CURRENT = "CHECKPOINT NOT CURRENT"


def checkpoint_rel(project_root: str) -> str:
    """The lead's checkpoint in a linked worktree (.git is a file
    there), the orchestrator's in the main tree."""
    linked = os.path.isfile(os.path.join(project_root, ".git"))
    return f".gov-runtime/scratch/{'lead' if linked else 'orchestrator'}/CHECKPOINT.md"


def is_current(project_root: str, rel: str) -> bool:
    try:
        age = time.time() - os.path.getmtime(os.path.join(project_root, rel))
    except OSError:
        return False
    return age <= MAX_AGE_S


def main() -> int:
    if os.environ.get("GOV_ROLE") != "orchestrator":
        return 0
    trigger = json.load(sys.stdin).get("trigger")
    project_root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    rel = checkpoint_rel(project_root)
    if is_current(project_root, rel):
        return 0
    message = f"{NOT_CURRENT}: {rel} is missing or older than 30 minutes."
    if trigger == "manual":
        sys.stderr.write(f"{message} Update it, then compact again.\n")
        return 2
    sys.stdout.write(json.dumps({"systemMessage": f"{message} The compaction proceeds."}))
    return 0


if __name__ == "__main__":
    try:
        code = main()
    except Exception:
        code = 0
    sys.exit(code)
