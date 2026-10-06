#!/usr/bin/env python3
"""PreCompact hook (W1-29, CAP-37.b, DEC-264).

Writes a checkpoint via gov.checkpoint.record.write with trigger "compaction".
Never blocks a compaction (always exits 0).
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def main() -> None:
    data = json.loads(sys.stdin.read())
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    ticket = os.environ.get("GOV_TICKET", "")
    if not ticket:
        return

    try:
        from gov.checkpoint.record import write
        write(root, ticket, "compaction", "Resume after compaction", [])
    except Exception as exc:
        sys.stdout.write(json.dumps({
            "systemMessage": f"PreCompact: checkpoint not written ({exc}). The compaction proceeds.",
        }))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
