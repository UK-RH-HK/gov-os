#!/usr/bin/env python3
"""
SessionStart hook (W1-49, light form of CAP-37; W1-29 replaces it).

On compact, clear and resume, injects what to read now and the
checkpoint's RESUME HERE section, inside the 10,000-character cap of
additionalContext. The injection is role-specific (DEC-263): in the
main tree the orchestrator prompt and the orchestrator's checkpoint;
in a linked worktree the ticket-lead sentence with GOV_TICKET, appendix
A5 of the orchestrator prompt and the lead's checkpoint. It warns when
the checkpoint's written part is older than the generated state block
the PreCompact hook appended (DEC-264); nothing of the block is
injected. Acts only when GOV_ROLE is exactly "orchestrator" (DEC-259).

Always exits 0: a failure of this hook injects nothing and never stops
a session from starting.
"""

from __future__ import annotations

import calendar
import json
import os
import re
import sys
import time

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
    sys.dont_write_bytecode = True
    from precompact import STAMP, checkpoint_rel, split

    project_root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    rel = checkpoint_rel(project_root)
    path = os.path.join(project_root, rel)
    if "/lead/" in rel:
        ticket = os.environ.get("GOV_TICKET") or "this worktree's ticket (GOV_TICKET is not set)"
        parts = [f"You are the ticket lead for {ticket}; read appendix A5 of {PROMPT_REL} and your checkpoint "
                 f"{rel} now."]
    else:
        parts = [f"Read now, before anything else: {PROMPT_REL} and {rel}."]
    section, older = "", False
    try:
        with open(path, "rb") as f:
            written, block = split(f.read())
        section = resume_section(written.decode("utf-8", errors="replace"))
        stamp = re.search(rb"^generated: (\S+)", block, re.M)
        older = bool(stamp) and os.path.getmtime(path) < calendar.timegm(time.strptime(stamp.group(1).decode(), STAMP))
    except (OSError, ValueError):
        pass
    if older:
        parts.append(f"CHECKPOINT OLDER THAN STATE BLOCK: the written part of {rel} is older than the generated "
                     "state block at the end of that file. Re-derive state from git and the tickets before acting.")
    if section:
        parts.append(f"The RESUME HERE section of {rel}:\n\n{section[:SECTION_MAX_CHARS]}")
        if len(section) > SECTION_MAX_CHARS:
            parts.append(f"[truncated: the first {SECTION_MAX_CHARS} of {len(section)} characters of the "
                         f"section are shown; the rest is in {rel}]")
    else:
        parts.append(f"{rel} is missing, can't be read or has no RESUME HERE section.")
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
