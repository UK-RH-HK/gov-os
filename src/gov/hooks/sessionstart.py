#!/usr/bin/env python3
"""SessionStart hook (W1-29, CAP-15.g, CAP-37.b, DEC-208).

On startup/resume/clear/compact: injects gov context --brief, tk ready output,
and the checkpoint resume brief (for compact/clear/resume) within the 2,500-token
(10,000 character) cap.  On fork: does nothing.

Always exits 0: a failure injects nothing and never stops a session from starting.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

CAP_CHARS = 10_000


def main() -> None:
    data = json.loads(sys.stdin.read())
    source = data.get("source", "")
    if source == "fork":
        sys.stdout.write(json.dumps({"hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": "",
        }}))
        return

    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    ticket = os.environ.get("GOV_TICKET", "")
    parts: list[str] = []

    if ticket:
        try:
            from gov.context import context
            result = context(root, ticket, brief=True)
            summary = result.get("summary", "")
            if summary:
                parts.append(summary)
        except Exception:
            pass

    try:
        done = subprocess.run(
            ["tk", "ready"], cwd=str(root),
            capture_output=True, text=True, timeout=10,
        )
        if done.returncode == 0 and done.stdout.strip():
            parts.append(done.stdout.strip())
    except Exception:
        pass

    if source in ("compact", "clear", "resume") and ticket:
        try:
            from gov.checkpoint.record import brief
            b = brief(root, ticket)
            parts.append(
                f"Checkpoint resume: ticket={b['ticket']}, "
                f"next_action={b['next_action']}, "
                f"path={b.get('path', '')}"
            )
        except Exception:
            pass

    text = "\n\n".join(parts)
    if len(text) > CAP_CHARS:
        text = text[:CAP_CHARS]

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
