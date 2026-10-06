#!/usr/bin/env python3
"""
SessionStart hook (W1-49 resume injection + W1-29 context packet, CAP-37).

Combined injection, within the 10,000-character cap:

Critical parts (W1-49, orchestrator only, last to be cut):
  - instruction to read the prompt and checkpoint
  - staleness warning (DEC-264)
  - RESUME HERE section

Optional parts (W1-29, all roles, first to be cut):
  - gov context --brief output
  - tk ready output
  - checkpoint resume brief (on compact/clear/resume)

When the combined injection exceeds the cap, the optional parts are
trimmed first; the instruction and the staleness warning are the last
things cut (reviewer finding 3).

Acts for all roles when GOV_TICKET is set (W1-29 context injection).
The W1-49 orchestrator injection (prompt path, RESUME HERE, staleness
warning) acts only when GOV_ROLE is exactly "orchestrator" (DEC-259).

Always exits 0.
"""

from __future__ import annotations

import calendar
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

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


def _add_src(project_root: str) -> None:
    src_dir = os.path.join(project_root, "src")
    if os.path.isdir(src_dir) and src_dir not in sys.path:
        sys.path.insert(0, src_dir)


def main() -> None:
    sys.dont_write_bytecode = True
    try:
        data = json.loads(sys.stdin.read())
    except Exception:
        data = {}
    source = data.get("source", "")

    project_root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    role = os.environ.get("GOV_ROLE", "")
    ticket = os.environ.get("GOV_TICKET", "")

    critical_parts: list[str] = []
    if role == "orchestrator":
        from precompact import STAMP, checkpoint_rel, split

        rel = checkpoint_rel(project_root)
        path = os.path.join(project_root, rel)
        if "/lead/" in rel:
            lead_ticket = ticket or "this worktree's ticket (GOV_TICKET is not set)"
            critical_parts.append(
                f"You are the ticket lead for {lead_ticket}; read appendix A5 of "
                f"{PROMPT_REL} and your checkpoint {rel} now.")
        else:
            critical_parts.append(f"Read now, before anything else: {PROMPT_REL} and {rel}.")
        section, older = "", False
        try:
            with open(path, "rb") as f:
                written, block = split(f.read())
            section = resume_section(written.decode("utf-8", errors="replace"))
            stamp = re.search(rb"^generated: (\S+)", block, re.M)
            older = bool(stamp) and os.path.getmtime(path) < calendar.timegm(
                time.strptime(stamp.group(1).decode(), STAMP))
        except (OSError, ValueError):
            pass
        if older:
            critical_parts.append(
                f"CHECKPOINT OLDER THAN STATE BLOCK: the written part of {rel} is older than the generated "
                "state block at the end of that file. Re-derive state from git and the tickets before acting.")
        if section:
            critical_parts.append(f"The RESUME HERE section of {rel}:\n\n{section[:SECTION_MAX_CHARS]}")
            if len(section) > SECTION_MAX_CHARS:
                critical_parts.append(
                    f"[truncated: the first {SECTION_MAX_CHARS} of {len(section)} characters of the "
                    f"section are shown; the rest is in {rel}]")
        else:
            critical_parts.append(f"{rel} is missing, can't be read or has no RESUME HERE section.")

    optional_parts: list[str] = []
    if ticket:
        try:
            _add_src(project_root)
            from gov.context import context
            result = context(Path(project_root), ticket, brief=True)
            summary = result.get("summary", "")
            if summary:
                optional_parts.append(summary)
        except Exception:
            pass

    try:
        done = subprocess.run(
            ["tk", "ready"], cwd=project_root,
            capture_output=True, text=True, timeout=10,
        )
        if done.returncode == 0 and done.stdout.strip():
            optional_parts.append(done.stdout.strip())
    except Exception:
        pass

    if source in ("compact", "clear", "resume") and ticket:
        try:
            _add_src(project_root)
            from gov.checkpoint.record import brief
            b = brief(Path(project_root), ticket)
            optional_parts.append(
                f"Checkpoint resume: ticket={b['ticket']}, "
                f"next_action={b['next_action']}, "
                f"path={b.get('path', '')}")
        except Exception:
            pass

    critical_text = "\n\n".join(critical_parts)
    optional_text = "\n\n".join(optional_parts)

    if not critical_text and not optional_text:
        return

    if critical_text and optional_text:
        combined = critical_text + "\n\n" + optional_text
        if len(combined) > CAP_CHARS:
            remaining = CAP_CHARS - len(critical_text) - 2
            if remaining > 0:
                text = critical_text + "\n\n" + optional_text[:remaining]
            else:
                text = critical_text[:CAP_CHARS]
        else:
            text = combined
    elif critical_text:
        text = critical_text[:CAP_CHARS]
    else:
        text = optional_text[:CAP_CHARS]

    sys.stdout.write(json.dumps({"hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": text,
    }}))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
