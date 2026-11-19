#!/usr/bin/env python3
"""Stop hook (W1-29, CAP-37.b; W2-205, RT-2).

Writes a checkpoint via gov.checkpoint.record.write with trigger "stop"
(only with a ticket, GOV_TICKET). Then it runs the Stop check
(gov.msg.stopcheck.check, the wake carrier) for the session's address
(GOV_MSG_ADDRESS), with or without a ticket, and prints the check's
block decision on stdout: a turn end is blocked only for an unread wake
message, once per message. With no decision it prints nothing.

When stop_hook_active is present and truthy, exits 0 immediately with no
side effects to prevent re-entrancy loops: no checkpoint, no check.

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


def _add_src(project_root: str) -> None:
    src_dir = os.path.join(project_root, "src")
    if _gov_os_source_tree(project_root) and src_dir not in sys.path:
        sys.path.insert(0, src_dir)


def _stop_check(project_root: str) -> None:
    """Print the Stop check's block decision, when it gives one (W2-205, RT-2). A check that cannot run lets the
    turn end."""
    try:
        _add_src(project_root)
        from gov.msg.stopcheck import check
        decision = check()
    except Exception as exc:
        _no_gov(exc, "the stop check was not run")
        return
    if decision:
        sys.stdout.write(json.dumps(decision))


def main() -> None:
    data = json.loads(sys.stdin.read())

    if data.get("stop_hook_active"):
        return

    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    ticket = os.environ.get("GOV_TICKET", "")
    if ticket:
        try:
            from gov.checkpoint.record import write
            write(root, ticket, "stop", "Resume after stop", [], dest="automatic")
        except Exception as exc:
            _no_gov(exc, "the checkpoint record was not written")

    _stop_check(str(root))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
