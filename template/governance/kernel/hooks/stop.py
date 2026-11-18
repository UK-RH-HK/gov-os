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


def _gov_os_source_tree(project_root: str) -> bool:
    """The Gov OS source tree itself (copier.yml, template/ and src/gov/ at its root): the one project whose src/ a
    hook puts on the import path (W2-18); a product's own package named gov is never imported."""
    return (os.path.isfile(os.path.join(project_root, "copier.yml"))
            and os.path.isdir(os.path.join(project_root, "template"))
            and os.path.isdir(os.path.join(project_root, "src", "gov")))


def _no_gov(exc: BaseException, what: str) -> bool:
    """For an import of gov that failed: one line on stderr naming what was looked for, and True (W2-18)."""
    if not isinstance(exc, ImportError) or not (getattr(exc, "name", None) or "").split(".")[0] == "gov":
        return False
    sys.stderr.write(f"gov hook: no gov importable by {sys.executable} (looked on its import path for "
                     f"{exc.name}); {what}\n")
    return True


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
    except Exception as exc:
        _no_gov(exc, "the checkpoint record was not written")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
