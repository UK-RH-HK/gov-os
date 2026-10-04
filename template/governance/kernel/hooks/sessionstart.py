#!/usr/bin/env python3
"""
SessionStart hook (W1-49, light form of CAP-37; W1-29 replaces it).

On compact, clear and resume, injects the paths to read now and the
checkpoint's RESUME HERE section, inside the 10,000-character cap of
additionalContext. In the main tree: the orchestrator prompt and the
orchestrator's checkpoint. In a linked worktree: the lead's checkpoint
only. After a compaction over a checkpoint that is not current it says
so (DEC-258). Acts only when GOV_ROLE is exactly "orchestrator"
(DEC-259).

Always exits 0: a failure of this hook injects nothing and never stops
a session from starting.
"""

from __future__ import annotations

import json
import os
import re
import sys

PROMPT_REL = "governance/project/prompts/w1-orchestrator.md"
CAP_CHARS = 10_000
SECTION_MAX_CHARS = 9_000


def resume_section(text: str) -> str:
    """The heading that begins with RESUME HERE and everything up to
    the next heading of the same or a higher level. A line inside a
    fenced code block (three backticks) is not a heading."""
    kept: list[str] = []
    level = 0
    fenced = False
    for line in text.splitlines():
        if line.startswith("```"):
            fenced = not fenced
        heading = None if fenced else re.match(r"(#{1,6})\s+(.*)", line)
        if level:
            if heading and len(heading.group(1)) <= level:
                break
            kept.append(line)
        elif heading and heading.group(2).startswith("RESUME HERE"):
            level = len(heading.group(1))
            kept.append(line)
    return "\n".join(kept).strip()


def main() -> None:
    if os.environ.get("GOV_ROLE") != "orchestrator":
        return
    source = json.load(sys.stdin).get("source")
    sys.dont_write_bytecode = True
    from precompact import NOT_CURRENT, checkpoint_rel, is_current

    project_root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    rel = checkpoint_rel(project_root)
    paths = [rel] if "/lead/" in rel else [PROMPT_REL, rel]
    parts = ["Read now, before anything else: " + " and ".join(paths) + "."]
    if source == "compact" and not is_current(project_root, rel):
        parts.append(f"{NOT_CURRENT}: {rel} was missing or older than 30 minutes at the compaction; "
                     "it may not hold the latest state.")
    try:
        with open(os.path.join(project_root, rel), encoding="utf-8", errors="replace") as f:
            section = resume_section(f.read())
    except OSError:
        section = ""
    if section:
        parts.append(f"The RESUME HERE section of {rel}:\n\n{section[:SECTION_MAX_CHARS]}")
        if len(section) > SECTION_MAX_CHARS:
            parts.append(f"[truncated: the first {SECTION_MAX_CHARS} of {len(section)} characters of the "
                         f"section are shown; the rest is in {rel}]")
    else:
        parts.append(f"{rel} is missing or has no RESUME HERE section.")
    sys.stdout.write(json.dumps({"hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": "\n\n".join(parts)[:CAP_CHARS],
    }}))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
