#!/usr/bin/env python3
"""Stop hook (W1-29, CAP-37.b).

Writes a checkpoint via gov.checkpoint.record.write with trigger "stop".
When stop_hook_active is present and truthy, exits 0 immediately with no
side effects to prevent re-entrancy loops.

Always exits 0.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def main() -> None:
    data = json.loads(sys.stdin.read())

    if data.get("stop_hook_active"):
        return

    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    ticket = os.environ.get("GOV_TICKET", "")
    if not ticket:
        return

    try:
        from gov.checkpoint.record import write
        write(root, ticket, "stop", "Resume after stop", [], dest="automatic")
    except Exception:
        pass


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
