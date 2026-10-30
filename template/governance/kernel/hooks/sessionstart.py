#!/usr/bin/env python3
"""
SessionStart hook (W1-49 resume injection + W1-29 context packet, CAP-37).

Combined injection, within the 10,000-character cap:

Critical parts (W1-49, W2-62, orchestrator only, never cut):
  - instruction to read the prompt the roster names and the checkpoint
  - staleness warning (DEC-264)
  - instruction to read the RESUME HERE section in full: the
    checkpoint's path, the section's line range and its size
  - the whole RESUME HERE section, only when it fits within the cap
    with the rest; a section is never cut (DEC-837)

Optional parts (W1-29, all roles, the ones trimmed):
  - gov context --brief output
  - tk ready output
  - checkpoint resume brief (on compact/clear/resume)

When the combined injection exceeds the cap, the optional parts are
trimmed (reviewer finding 3).

Acts for all roles when GOV_TICKET is set (W1-29 context injection).
The orchestrator injection (prompt path, RESUME HERE, staleness
warning) acts only when GOV_ROLE is exactly "orchestrator" (DEC-259).
The prompt is the one governance/project/roster.yaml names under
roles: orchestrator: prompt:; with none, no prompt is named (W2-M373).

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

ROSTER_REL = "governance/project/roster.yaml"
CAP_CHARS = 10_000  # Claude Code moves a longer additionalContext to a file (W2-62 CIT-P)


def resume_lines(text: str) -> tuple[int, int, str]:
    """(first, last, section): the heading that begins with RESUME HERE
    and everything up to the next heading of the same or a higher
    level, trailing empty lines excluded; first and last are 1-based
    line numbers of text. A line inside a fenced code block (three
    backticks) is not a heading. (0, 0, "") when there is none."""
    lines = text.split("\n")
    first = last = level = 0
    fenced = False
    for number, line in enumerate(lines, 1):
        if line.startswith("```"):
            fenced = not fenced
        heading = None if fenced else re.match(r"(#{1,6})\s+(.*)", line)
        if level:
            if heading and len(heading.group(1)) <= level:
                break
        elif heading and heading.group(2).startswith("RESUME HERE"):
            level, first = len(heading.group(1)), number
        if level and line.strip():
            last = number
    return first, last, "\n".join(lines[first - 1:last]) if first else ""


def resume_section(text: str) -> str:
    return resume_lines(text)[2]


def roster_prompt(project_root: str) -> str:
    """The orchestrator's prompt the project's roster names
    (roles: orchestrator: prompt:), or "" when it names none."""
    try:
        import yaml
        with open(os.path.join(project_root, ROSTER_REL), encoding="utf-8") as f:
            prompt = yaml.safe_load(f)["roles"]["orchestrator"]["prompt"]
    except Exception:
        return ""
    return prompt.strip() if isinstance(prompt, str) else ""


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
    source = data.get("source", "") if isinstance(data, dict) else ""

    project_root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    role = os.environ.get("GOV_ROLE", "")
    ticket = os.environ.get("GOV_TICKET", "")

    critical_parts: list[str] = []
    if role == "orchestrator":
        from precompact import STAMP, checkpoint_rel, split

        rel = checkpoint_rel(project_root)
        path = os.path.join(project_root, rel)
        prompt = roster_prompt(project_root)
        if "/lead/" in rel:
            lead_ticket = ticket or "this worktree's ticket (GOV_TICKET is not set)"
            appendix = f"appendix A5 of {prompt} and " if prompt else ""
            critical_parts.append(
                f"You are the ticket lead for {lead_ticket}; read {appendix}your checkpoint {rel} now.")
        else:
            critical_parts.append(f"Read now, before anything else: {f'{prompt} and ' if prompt else ''}{rel}.")
        first = last = 0
        section, older = "", False
        try:
            with open(path, "rb") as f:
                written, block = split(f.read())
            first, last, section = resume_lines(written.decode("utf-8", errors="replace"))
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
            critical_parts.append(
                f"Read the RESUME HERE section of {rel} in full before anything else: "
                f"lines {first}-{last}, {len(section):,} characters.")
            whole = f"The whole RESUME HERE section of {rel} (lines {first}-{last}):\n\n{section}"
            if len("\n\n".join(critical_parts + [whole])) <= CAP_CHARS:
                critical_parts.append(whole)
            else:
                critical_parts.append(
                    f"The section is longer than this injection can carry whole ({CAP_CHARS:,} characters), so "
                    f"none of it is shown here: read lines {first}-{last} of {rel} now, every line, in as many "
                    "reads as it takes.")
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
